from core.utils.twilio_media import TWILIO_MEDIA_MAX_BYTES_AUDIO, TWILIO_MEDIA_MAX_BYTES_IMAGE, classify_media_content_type, is_allowed_media_content_type, is_stt_compatible_media_content_type, max_bytes_for_media_content_type, normalize_media_content_type, stt_filename_for_media_content_type


def test_normalize_strips_parameters_and_case():
    assert normalize_media_content_type("Image/JPEG; charset=binary") == "image/jpeg"
    assert normalize_media_content_type("  ") is None
    assert normalize_media_content_type(None) is None


def test_classify_and_allowlist():
    assert classify_media_content_type("image/png") == "image"
    assert classify_media_content_type("audio/ogg") == "audio"
    assert classify_media_content_type("application/pdf") is None
    assert is_allowed_media_content_type("image/jpeg") is True
    assert is_allowed_media_content_type("video/mp4") is False


def test_max_bytes_by_kind():
    assert max_bytes_for_media_content_type("image/jpeg") == TWILIO_MEDIA_MAX_BYTES_IMAGE
    assert max_bytes_for_media_content_type("audio/mpeg") == TWILIO_MEDIA_MAX_BYTES_AUDIO
    assert max_bytes_for_media_content_type("application/pdf") is None


def test_stt_compatible_subset_and_filenames():
    assert is_stt_compatible_media_content_type("audio/ogg") is True
    assert is_stt_compatible_media_content_type("audio/amr") is False
    assert is_stt_compatible_media_content_type("audio/3gpp") is False
    assert stt_filename_for_media_content_type("audio/opus") == "audio.ogg"
    assert stt_filename_for_media_content_type("audio/aac") == "audio.m4a"
    assert stt_filename_for_media_content_type("audio/amr") is None
