import json
import os

from core.queues import PROJECT_ID, QUEUE_REGION, QUEUES


class CloudTasksClient:

    def __init__(self):
        self._client = None

    def enqueue(self, queue_key, payload):
        service_url = os.getenv("SERVICE_URL")
        if not service_url:
            raise ValueError("SERVICE_URL environment variable is required")
        if not PROJECT_ID:
            raise ValueError("PROJECT_ID environment variable is required")

        from google.cloud import tasks_v2

        if self._client is None:
            self._client = tasks_v2.CloudTasksClient()

        queue_config = QUEUES[queue_key]

        parent = self._client.queue_path(
            PROJECT_ID,
            QUEUE_REGION,
            queue_config["name"],
        )

        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": service_url + queue_config["worker_path"],
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(payload).encode(),
            }
        }

        self._client.create_task(parent=parent, task=task)
