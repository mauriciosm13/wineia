from gateway.middleware import enforce_gateway
from api.handlers.health_handler import handle_health
from api.handlers.worker_handler import handle_send_message
from api.handlers.ia_handler import handle_generate_suggestion
from api.handlers.customer_handler import handle_create_customer
from api.handlers.whatsapp_handler import handle_whatsapp_webhook
from api.handlers.jobs_handler import handle_send_recommendations
from api.handlers.recommendation_content_handler import handle_create_recommendation_content

ROUTES = {
    "/health": handle_health,
    "/customers": handle_create_customer,
    "/workers/send-message": handle_send_message,
    "/webhook/whatsapp": handle_whatsapp_webhook,
    "/ia/suggestions": handle_generate_suggestion,
    "/jobs/send-recommendations": handle_send_recommendations,
    "/recommendation-contents": handle_create_recommendation_content,
}

def route_request(environ, start_response):
    blocked_response = enforce_gateway(environ, start_response)
    if blocked_response is not None:
        return blocked_response

    path = environ.get("PATH_INFO")

    handler = ROUTES.get(path)

    if handler:
        return handler(environ, start_response)

    start_response("404 Not Found", [("Content-Type", "text/plain")])
    return [b"Not Found"]
    
