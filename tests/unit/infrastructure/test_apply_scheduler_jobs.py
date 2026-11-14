import io
import subprocess
from types import SimpleNamespace
from infrastructure.scheduler import apply_scheduler_jobs

SECRET = "s3cr3t-value"
SERVICE_URL = "https://wine-concierge-abc.a.run.app"
ENV = {
    "PROJECT_ID": "wineia-490200",
    "REGION": "southamerica-east1",
    "SERVICE": "wine-concierge",
    "JOB_INTERNAL_SECRET_ID": "wine-concierge-job-internal-secret",
}

RETRY_FLAGS = [
    "--max-retry-attempts=3",
    "--min-backoff=60s",
    "--max-backoff=600s",
    "--attempt-deadline=300s",
]


def _expected_job_argv(action, name, schedule, path):
    headers_flag = "--update-headers" if action == "update" else "--headers"
    return [
        "gcloud", "scheduler", "jobs", action, "http", name,
        "--location=southamerica-east1",
        "--project=wineia-490200",
        f"--schedule={schedule}",
        "--time-zone=America/Sao_Paulo",
        f"--uri={SERVICE_URL}{path}",
        "--http-method=POST",
        f"{headers_flag}=X-Job-Internal-Secret={SECRET},Content-Type=application/json",
        *RETRY_FLAGS,
    ]


def _expected_jobs_argv(action):
    return [
        _expected_job_argv(action, "wine-send-recommendations", "0 10 * * 4,6", "/jobs/send-recommendations"),
        _expected_job_argv(action, "wine-send-weekly-education", "0 15 * * 1", "/jobs/send-weekly-education"),
    ]


class FakeRunner:
    def __init__(self, secret=SECRET, url=SERVICE_URL + "\n", existing=(), apply_failures=0):
        self.secret = secret
        self.url = url
        self.existing = set(existing)
        self.apply_failures = apply_failures
        self.calls = []

    def __call__(self, argv):
        self.calls.append(list(argv))
        if argv[:4] == ["gcloud", "secrets", "versions", "access"]:
            return SimpleNamespace(returncode=0, stdout=self.secret)
        if argv[:4] == ["gcloud", "run", "services", "describe"]:
            return SimpleNamespace(returncode=0, stdout=self.url)
        if argv[:4] == ["gcloud", "scheduler", "jobs", "describe"]:
            found = argv[4] in self.existing
            return SimpleNamespace(returncode=0 if found else 1, stdout="")
        if argv[:3] == ["gcloud", "scheduler", "jobs"] and argv[3] in ("create", "update"):
            if self.apply_failures > 0:
                self.apply_failures -= 1
                return SimpleNamespace(returncode=1, stdout="")
            return SimpleNamespace(returncode=0, stdout="")
        raise AssertionError(f"unexpected gcloud call: {argv[:4]}")

    def job_writes(self):
        return [c for c in self.calls if c[:3] == ["gcloud", "scheduler", "jobs"] and c[3] in ("create", "update")]

    def secret_reads(self):
        return [c for c in self.calls if c[:4] == ["gcloud", "secrets", "versions", "access"]]


def _run(runner, environ=None):
    out = io.StringIO()
    err = io.StringIO()
    sleeps = []
    code = apply_scheduler_jobs.main(
        environ=ENV if environ is None else environ,
        runner=runner,
        sleep=sleeps.append,
        out=out,
        err=err,
    )
    return code, out.getvalue(), err.getvalue(), sleeps


def test_creates_both_jobs_when_describe_fails():
    runner = FakeRunner(existing=())

    code, _, _, sleeps = _run(runner)

    assert code == 0
    assert runner.job_writes() == _expected_jobs_argv("create")
    assert sleeps == []


def test_updates_both_jobs_when_describe_succeeds():
    runner = FakeRunner(existing=("wine-send-recommendations", "wine-send-weekly-education"))

    code, _, _, _ = _run(runner)

    assert code == 0
    assert runner.job_writes() == _expected_jobs_argv("update")


def test_creates_missing_job_and_updates_existing_one():
    runner = FakeRunner(existing=("wine-send-weekly-education",))

    code, _, _, _ = _run(runner)

    assert code == 0
    assert runner.job_writes() == [_expected_jobs_argv("create")[0], _expected_jobs_argv("update")[1]]


def test_describes_each_job_in_region_and_project():
    runner = FakeRunner()

    _run(runner)

    describes = [c for c in runner.calls if c[:4] == ["gcloud", "scheduler", "jobs", "describe"]]
    assert [c[4] for c in describes] == ["wine-send-recommendations", "wine-send-weekly-education"]
    for argv in describes:
        assert "--location=southamerica-east1" in argv
        assert "--project=wineia-490200" in argv


def test_reads_secret_and_service_url_through_runner():
    runner = FakeRunner()

    _run(runner)

    assert runner.calls[0][:6] == [
        "gcloud", "secrets", "versions", "access", "latest", "--secret=wine-concierge-job-internal-secret",
    ]
    assert runner.calls[1] == [
        "gcloud", "run", "services", "describe", "wine-concierge",
        "--project=wineia-490200",
        "--region=southamerica-east1",
        "--format=value(status.url)",
    ]


def test_first_stdout_line_masks_secret_and_no_other_line_contains_it():
    runner = FakeRunner()

    code, out, err, _ = _run(runner)

    assert code == 0
    lines = out.splitlines()
    assert lines[0] == f"::add-mask::{SECRET}"
    assert all(SECRET not in line for line in lines[1:])
    assert SECRET not in err


def test_secret_never_printed_when_attempts_fail():
    runner = FakeRunner(apply_failures=10)

    code, out, err, _ = _run(runner)

    assert code != 0
    lines = out.splitlines()
    assert lines[0] == f"::add-mask::{SECRET}"
    assert all(SECRET not in line for line in lines[1:])
    assert SECRET not in err


def test_empty_secret_fails_attempt():
    runner = FakeRunner(secret="")

    code, out, _, sleeps = _run(runner)

    assert code != 0
    assert runner.job_writes() == []
    assert len(runner.secret_reads()) == 3
    assert sleeps == [10, 20]
    assert "::add-mask::" not in out


def test_empty_service_url_fails_attempt():
    runner = FakeRunner(url="\n")

    code, out, err, sleeps = _run(runner)

    assert code != 0
    assert runner.job_writes() == []
    assert len(runner.secret_reads()) == 3
    assert sleeps == [10, 20]
    assert SECRET not in err


def test_fails_twice_then_succeeds_exits_zero_after_three_attempts():
    runner = FakeRunner(apply_failures=2)

    code, out, _, sleeps = _run(runner)

    assert code == 0
    assert len(runner.secret_reads()) == 3
    assert sleeps == [10, 20]
    assert out.splitlines().count(f"::add-mask::{SECRET}") == 1


def test_fails_three_times_exits_non_zero_without_fourth_attempt():
    runner = FakeRunner(apply_failures=10)

    code, _, _, sleeps = _run(runner)

    assert code != 0
    assert len(runner.secret_reads()) == 3
    assert sleeps == [10, 20]


def test_missing_env_fails_without_calling_gcloud():
    runner = FakeRunner()
    environ = {k: v for k, v in ENV.items() if k != "JOB_INTERNAL_SECRET_ID"}

    code, _, err, sleeps = _run(runner, environ=environ)

    assert code != 0
    assert runner.calls == []
    assert sleeps == []
    assert "JOB_INTERNAL_SECRET_ID" in err


def test_default_runner_reports_missing_gcloud_as_failure(monkeypatch):
    def raise_not_found(*args, **kwargs):
        raise FileNotFoundError("gcloud")

    monkeypatch.setattr(subprocess, "run", raise_not_found)

    result = apply_scheduler_jobs.run_gcloud(["gcloud", "version"])

    assert result.returncode != 0
