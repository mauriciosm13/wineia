import os


PROJECT_ID = os.getenv("PROJECT_ID")
QUEUE_REGION = os.getenv("QUEUE_REGION", "southamerica-east1")


QUEUES = {
    "send_message": {
        "name": "wine-messages",
        "worker_path": "/workers/send-message",
        "rate_limit_per_second": 5
    },

    "send_campaign": {
        "name": "wine-campaigns",
        "worker_path": "/workers/send-campaign",
        "rate_limit_per_second": 2
    }
}