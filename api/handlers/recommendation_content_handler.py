import json
from domain.services.recommendation_content_service import RecommendationContentService
from infrastructure.repositories.datastore_recommendation_repository import DatastoreRecommendationRepository
from core.utils.request import read_request_body

repository = DatastoreRecommendationRepository()
service = RecommendationContentService(repository)


def _respond_error(start_response, status, message):
    start_response(status, [("Content-Type", "application/json")])
    return [json.dumps({"error": message}).encode()]


def handle_create_recommendation_content(environ, start_response):
    if environ.get("REQUEST_METHOD") != "POST":
        return _respond_error(start_response, "405 Method Not Allowed", "Method not allowed")

    body = read_request_body(environ)

    if not body:
        return _respond_error(start_response, "400 Bad Request", "Body is required")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return _respond_error(start_response, "400 Bad Request", "Invalid JSON")

    name = payload.get("name")
    if not name:
        return _respond_error(start_response, "400 Bad Request", "name is required")

    if not isinstance(name, str):
        return _respond_error(start_response, "400 Bad Request", "name must be a string")

    name = name.strip()
    if not name:
        return _respond_error(start_response, "400 Bad Request", "name cannot be empty")

    grape = payload.get("grape")
    country = payload.get("country")
    winery = payload.get("winery")
    price = payload.get("price")
    description = payload.get("description")

    if grape is not None and not isinstance(grape, str):
        return _respond_error(start_response, "400 Bad Request", "grape must be a string")
    if country is not None and not isinstance(country, str):
        return _respond_error(start_response, "400 Bad Request", "country must be a string")
    if description is not None and not isinstance(description, str):
        return _respond_error(start_response, "400 Bad Request", "description must be a string")

    if price is not None:
        try:
            price = float(price) if not isinstance(price, (int, float)) else price
        except (TypeError, ValueError):
            return _respond_error(start_response, "400 Bad Request", "price must be a number")
        if price < 0:
            return _respond_error(start_response, "400 Bad Request", "price must be greater than or equal to 0")

    content = service.create_content(
        name=name,
        grape=grape or None,
        country=country or None,
        winery=winery or None,
        price=price,
        description=description or None,
    )

    start_response("201 Created", [("Content-Type", "application/json")])
    return [json.dumps(content, default=str).encode()]
