# pytest configuration lives in pyproject.toml (pythonpath, testpaths).
# Stub Datastore client so domain modules that import infrastructure do not need GCP credentials.
from unittest.mock import MagicMock

import google.cloud.datastore as google_datastore

google_datastore.Client = MagicMock(return_value=MagicMock())
