# T077 builder report

Branch: `feat/t077-inbound-audio-stt` (from `main`).

| ID | Result (`done` or `skipped`) | Files | What changed |
|----|-------------------------------|-------|----------------|
| EW-01 | done | `docs/adrs/0006-openai-whisper-stt.md` | ADR: Claude cannot STT; OpenAI transcriptions via `requests`; `whisper-1`; `language=pt`; no new pip dep. |
| EW-02 | done | `infrastructure/external/openai_stt_client.py` + tests | `transcribe_audio` multipart POST; typed `OpenAISTTError`; mocked HTTP unit tests. |
| EW-03 | done | `core/utils/twilio_media.py` | `is_stt_compatible_media_content_type` + filename helper; amr/3gpp excluded. |
| EW-04 | done | `domain/services/messaging_service.py` | Optional `audio_transcriber`; audio → STT → IA → increment; domain imports `core` only. |
| EW-05 | done | same + domain tests | STT fail / empty / missing transcriber / incompatible MIME → `MEDIA_STT_FAILED_MESSAGE`; no increment. |
| EW-06 | done | messaging_service + tests | Image after download still unavailable; text-only unchanged. |
| EW-07 | done | `api/handlers/whatsapp_handler.py` | Injects `transcribe_audio` as `audio_transcriber`; Claude budget via existing IA path. |
| EW-08 | done | domain / core / infra / webhook tests | Success, fail, empty, incompatible MIME, image unavailable, text regression, mocked OpenAI. |
| EW-09 | done | ROADMAP / INDEX / this SDD | T077 checked / `implemented` after EW-01–EW-08 and EW-10. |
| EW-10 | done | whole diff | No vision/payments/blob persistence. Coverage 96.57%; pytest / ruff / import style pass. |

## Files touched

- `CONTEXT.md`
- `api/handlers/whatsapp_handler.py`
- `config.example.json`
- `core/utils/twilio_media.py`
- `docs/adrs/0006-openai-whisper-stt.md`
- `docs/ROADMAP-TASKS.md`
- `docs/specs/sdd/INDEX.md`
- `docs/specs/sdd/T077-builder-report.md`
- `docs/specs/sdd/T077-inbound-audio-stt-sdd.md`
- `docs/specs/sdd/T077-reviewer-verdict.md`
- `domain/services/messaging_service.py`
- `infrastructure/external/openai_stt_client.py`
- `tests/unit/api/test_webhook_rate_limit.py`
- `tests/unit/api/test_whatsapp_webhook.py`
- `tests/unit/core/test_twilio_media.py`
- `tests/unit/domain/test_messaging_service.py`
- `tests/unit/infrastructure/test_openai_stt_client.py`

## Verification

- `PYTHONPATH=. python3 -m pytest --cov=domain --cov=core --cov-report=term-missing -q` — Total coverage 96.57% (≥95%)
- `python3 -m ruff check` on touched paths — All checks passed
- `python3 quality/check_import_style.py` — Import style OK
