"""Create or update the Cloud Scheduler jobs that call the job endpoints (T031, ADR 0005).

Run from the deploy workflow: `python3 -m infrastructure.scheduler.apply_scheduler_jobs`.
Standard library only, because the deploy job does not install dependencies.
"""
import os
import subprocess
import sys
import time

REQUIRED_ENV = ("PROJECT_ID", "REGION", "SERVICE", "JOB_INTERNAL_SECRET_ID")

TIME_ZONE = "America/Sao_Paulo"
HTTP_METHOD = "POST"
SECRET_HEADER = "X-Job-Internal-Secret"
CONTENT_TYPE_HEADER = "Content-Type=application/json"
RETRY_FLAGS = (
    "--max-retry-attempts=3",
    "--min-backoff=60s",
    "--max-backoff=600s",
    "--attempt-deadline=300s",
)

JOBS = (
    {"name": "wine-send-recommendations", "schedule": "0 10 * * 4,6", "path": "/jobs/send-recommendations"},
    {"name": "wine-send-weekly-education", "schedule": "0 15 * * 1", "path": "/jobs/send-weekly-education"},
)

MAX_ATTEMPTS = 3
WAIT_SECONDS_AFTER_FAILURE = (10, 20)

GCLOUD_NOT_FOUND_EXIT_CODE = 127


class ApplyError(Exception):
    """An attempt failed. The message never contains the secret."""


def run_gcloud(argv):
    """Run a gcloud command and capture its output without echoing it."""
    try:
        return subprocess.run(argv, capture_output=True, text=True, check=False)
    except OSError:
        return subprocess.CompletedProcess(argv, GCLOUD_NOT_FOUND_EXIT_CODE, "", "")


def read_config(environ):
    missing = [name for name in REQUIRED_ENV if not environ.get(name)]
    if missing:
        raise ApplyError("missing required env: " + ", ".join(missing))
    return {name: environ[name] for name in REQUIRED_ENV}


def read_secret(config, runner):
    argv = [
        "gcloud", "secrets", "versions", "access", "latest",
        f"--secret={config['JOB_INTERNAL_SECRET_ID']}",
        f"--project={config['PROJECT_ID']}",
    ]
    result = runner(argv)
    if result.returncode != 0:
        raise ApplyError(f"could not read secret {config['JOB_INTERNAL_SECRET_ID']} (exit {result.returncode})")
    secret = result.stdout or ""
    if not secret.strip():
        raise ApplyError(f"secret {config['JOB_INTERNAL_SECRET_ID']} is empty")
    return secret


def read_service_url(config, runner):
    argv = [
        "gcloud", "run", "services", "describe", config["SERVICE"],
        f"--project={config['PROJECT_ID']}",
        f"--region={config['REGION']}",
        "--format=value(status.url)",
    ]
    result = runner(argv)
    if result.returncode != 0:
        raise ApplyError(f"could not read URL of service {config['SERVICE']} (exit {result.returncode})")
    url = (result.stdout or "").strip()
    if not url:
        raise ApplyError(f"service {config['SERVICE']} has no URL")
    return url


def job_exists(job, config, runner):
    argv = [
        "gcloud", "scheduler", "jobs", "describe", job["name"],
        f"--location={config['REGION']}",
        f"--project={config['PROJECT_ID']}",
        "--format=value(name)",
    ]
    return runner(argv).returncode == 0


def build_job_argv(action, job, config, service_url, secret):
    headers_flag = "--update-headers" if action == "update" else "--headers"
    return [
        "gcloud", "scheduler", "jobs", action, "http", job["name"],
        f"--location={config['REGION']}",
        f"--project={config['PROJECT_ID']}",
        f"--schedule={job['schedule']}",
        f"--time-zone={TIME_ZONE}",
        f"--uri={service_url}{job['path']}",
        f"--http-method={HTTP_METHOD}",
        f"{headers_flag}={SECRET_HEADER}={secret},{CONTENT_TYPE_HEADER}",
        *RETRY_FLAGS,
    ]


def apply_job(job, config, service_url, secret, runner, out):
    action = "update" if job_exists(job, config, runner) else "create"
    result = runner(build_job_argv(action, job, config, service_url, secret))
    if result.returncode != 0:
        raise ApplyError(f"{action} failed for job {job['name']} (exit {result.returncode})")
    out.write(f"{action}d scheduler job {job['name']}\n")
    out.flush()


def run_attempt(config, runner, out, masked_secrets):
    secret = read_secret(config, runner)
    if secret not in masked_secrets:
        out.write(f"::add-mask::{secret}\n")
        out.flush()
        masked_secrets.add(secret)
    service_url = read_service_url(config, runner)
    for job in JOBS:
        apply_job(job, config, service_url, secret, runner, out)


def apply_with_retries(config, runner, sleep, out, err):
    masked_secrets = set()
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            run_attempt(config, runner, out, masked_secrets)
            return 0
        except ApplyError as exc:
            err.write(f"attempt {attempt}/{MAX_ATTEMPTS} failed: {exc}\n")
            err.flush()
            if attempt < MAX_ATTEMPTS:
                sleep(WAIT_SECONDS_AFTER_FAILURE[attempt - 1])
    err.write(f"scheduler jobs not applied after {MAX_ATTEMPTS} attempts\n")
    err.flush()
    return 1


def main(environ=None, runner=run_gcloud, sleep=time.sleep, out=None, err=None):
    environ = os.environ if environ is None else environ
    out = sys.stdout if out is None else out
    err = sys.stderr if err is None else err
    try:
        config = read_config(environ)
    except ApplyError as exc:
        err.write(f"{exc}\n")
        err.flush()
        return 2
    return apply_with_retries(config, runner, sleep, out, err)


if __name__ == "__main__":
    sys.exit(main())
