import json

from core.utils.load_config import load_config


def test_load_config_reads_json(tmp_path, monkeypatch):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"ANTHROPIC_API_KEY": "secret"}), encoding="utf-8")
    monkeypatch.setattr("core.utils.load_config.CONFIG_PATH", config_file)

    loaded = load_config()

    assert loaded["ANTHROPIC_API_KEY"] == "secret"
