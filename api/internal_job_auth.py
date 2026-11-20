import json
import secrets
from core.config import JOB_INTERNAL_SECRET

INTERNAL_JOB_SECRET_HEADER = "HTTP_X_JOB_INTERNAL_SECRET"


def path_requires_internal_job_auth(path: str, method: str = "") -> bool:
    if path.startswith("/jobs/") or path.startswith("/workers/"):
        return True
    if path == "/ia/suggestions" or path == "/recommendation-contents":
        return True
    if path == "/customers" or path.startswith("/customers/"):
        return True
    # Public POST /waitlist; operator GET /waitlist requires job secret (T087/T088).
    if path == "/waitlist" and method.upper() == "GET":
        return True
    return False


def internal_job_request_is_authorized(environ) -> bool:
    if not JOB_INTERNAL_SECRET:
        return False
    provided = environ.get(INTERNAL_JOB_SECRET_HEADER, "")
    if not provided:
        return False
    return secrets.compare_digest(provided, JOB_INTERNAL_SECRET)


def reject_unauthorized_internal_job(start_response):
    start_response("401 Unauthorized", [("Content-Type", "application/json")])
    return [json.dumps({"error": "unauthorized"}).encode()]
