def read_request_body(environ, decode=False):
    cached_body = environ.get("cached.request_body")

    if cached_body is None:
        length = int(environ.get("CONTENT_LENGTH", 0) or 0)
        cached_body = environ["wsgi.input"].read(length)
        environ["cached.request_body"] = cached_body

    if decode:
        return cached_body.decode("utf-8")

    return cached_body
