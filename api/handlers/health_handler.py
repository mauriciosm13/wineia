def handle_health(environ, start_response):
    start_response("200 OK", [("Content-Type", "application/json")])
    return [b'{"status": "ok"}']