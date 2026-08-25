import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wine-concierge")


def log_request(method, path, status=None):
    message = f"request method={method} path={path}"
    if status is not None:
        message += f" status={status}"
    logger.info(message)
