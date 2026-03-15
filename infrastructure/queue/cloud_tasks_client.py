import os
import json
from google.cloud import tasks_v2
from core.queues import QUEUES, PROJECT_ID, QUEUE_REGION


class CloudTasksClient:

    def __init__(self):

        self.client = tasks_v2.CloudTasksClient()

    def enqueue(self, queue_key, payload):

        queue_config = QUEUES[queue_key]

        parent = self.client.queue_path(
            PROJECT_ID,
            QUEUE_REGION,
            queue_config["name"]
        )

        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": os.getenv("SERVICE_URL") + queue_config["worker_path"],
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(payload).encode(),
            }
        }

        self.client.create_task(parent=parent, task=task)
        