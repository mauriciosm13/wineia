import json

from core.utils.load_config import load_config


def test_load_config_reads_json(tmp_path, monkeypatch):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"ANTHROPIC_API_KEY": "secret"}), encoding="utf-8")
    monkeypatch.setattr("core.utils.load_config.CONFIG_PATH", config_file)

    loaded = load_config()

    assert loaded["ANTHROPIC_API_KEY"] == "secret"


def test_load_config_missing_file_returns_empty_dict(tmp_path, monkeypatch):
    missing = tmp_path / "does-not-exist.json"
    monkeypatch.setattr("core.utils.load_config.CONFIG_PATH", missing)

    assert load_config() == {}


def test_load_config_invalid_json_returns_empty_dict(tmp_path, monkeypatch):
    config_file = tmp_path / "config.json"
    config_file.write_text("{not-json", encoding="utf-8")
    monkeypatch.setattr("core.utils.load_config.CONFIG_PATH", config_file)

    assert load_config() == {}
