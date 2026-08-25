import json
import sys
from unittest.mock import MagicMock

import pytest

from infrastructure.queue import cloud_tasks_client


def _mock_tasks_v2(monkeypatch):
    mock_client = MagicMock()
    mock_client.queue_path.return_value = (
        "projects/my-project/locations/southamerica-east1/queues/wine-messages"
    )
    mock_client_cls = MagicMock(return_value=mock_client)

    mock_tasks_v2 = MagicMock()
    mock_tasks_v2.CloudTasksClient = mock_client_cls
    mock_tasks_v2.HttpMethod.POST = "POST"

    monkeypatch.setitem(sys.modules, "google.cloud.tasks_v2", mock_tasks_v2)
    return mock_client, mock_client_cls


def test_enqueue_builds_service_url_and_creates_task(monkeypatch):
    mock_client, mock_client_cls = _mock_tasks_v2(monkeypatch)
    monkeypatch.setenv("SERVICE_URL", "https://api.example.com")
    monkeypatch.setattr(cloud_tasks_client, "PROJECT_ID", "my-project")

    cloud_tasks_client.CloudTasksClient().enqueue(
        "send_message",
        {"phone": "+5511999999999", "message": "hello"},
    )

    mock_client_cls.assert_called_once()
    mock_client.queue_path.assert_called_once_with(
        "my-project",
        cloud_tasks_client.QUEUE_REGION,
        "wine-messages",
    )
    mock_client.create_task.assert_called_once()
    task = mock_client.create_task.call_args.kwargs["task"]
    assert task["http_request"]["url"] == "https://api.example.com/workers/send-message"
    assert task["http_request"]["http_method"] == "POST"
    assert task["http_request"]["headers"] == {"Content-Type": "application/json"}
    assert json.loads(task["http_request"]["body"].decode()) == {
        "phone": "+5511999999999",
        "message": "hello",
    }


def test_enqueue_raises_when_service_url_missing(monkeypatch):
    monkeypatch.delenv("SERVICE_URL", raising=False)
    monkeypatch.setattr(cloud_tasks_client, "PROJECT_ID", "my-project")

    with pytest.raises(ValueError, match="SERVICE_URL"):
        cloud_tasks_client.CloudTasksClient().enqueue("send_message", {})


def test_enqueue_raises_when_project_id_missing(monkeypatch):
    monkeypatch.setenv("SERVICE_URL", "https://api.example.com")
    monkeypatch.setattr(cloud_tasks_client, "PROJECT_ID", None)

    with pytest.raises(ValueError, match="PROJECT_ID"):
        cloud_tasks_client.CloudTasksClient().enqueue("send_message", {})
