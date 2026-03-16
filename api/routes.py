from api.handlers.health_handler import handle_health
from api.handlers.worker_handler import handle_send_message
from api.handlers.customer_handler import handle_create_customer
from api.handlers.jobs_handler import handle_daily_recommendations
from api.handlers.whatsapp_handler import handle_whatsapp_webhook
from api.handlers.ia_handler import handle_generate_suggestion

ROUTES = {
    "/health": handle_health,
    "/customers": handle_create_customer,
    "/workers/send-message": handle_send_message,
    "/webhook/whatsapp": handle_whatsapp_webhook,
    "/jobs/daily-recommendations": handle_daily_recommendations,
    "/ia/suggestions": handle_generate_suggestion,
}

def route_request(environ, start_response):

    path = environ.get("PATH_INFO")

    handler = ROUTES.get(path)

    if handler:
        return handler(environ, start_response)

    start_response("404 Not Found", [("Content-Type", "text/plain")])
    return [b"Not Found"]
    