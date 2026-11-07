import json
from domain.services.education_service import send_weekly_education
from domain.services.recommendation_service import send_recommendations

def handle_send_recommendations(environ, start_response):
    send_recommendations()

    start_response("200 OK", [("Content-Type", "application/json")])

    return [json.dumps({"status": "ok"}).encode()]


def handle_send_weekly_education(environ, start_response):
    send_weekly_education()

    start_response("200 OK", [("Content-Type", "application/json")])

    return [json.dumps({"status": "ok"}).encode()]
