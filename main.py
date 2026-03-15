from api.routes import route_request

def app(environ, start_response):
    return route_request(environ, start_response)