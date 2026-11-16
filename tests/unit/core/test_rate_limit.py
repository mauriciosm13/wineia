from unittest.mock import patch

from core.rate_limit import SlidingWindowRateLimiter


def test_allow_under_limit():
    limiter = SlidingWindowRateLimiter()
    with patch("core.rate_limit.time.monotonic", side_effect=[100.0, 100.1, 100.2]):
        assert limiter.allow("k", 3, 60.0) is True
        assert limiter.allow("k", 3, 60.0) is True


def test_allow_at_limit_then_reject():
    limiter = SlidingWindowRateLimiter()
    times = [10.0, 10.1, 10.2, 10.3]
    with patch("core.rate_limit.time.monotonic", side_effect=times):
        assert limiter.allow("k", 3, 60.0) is True
        assert limiter.allow("k", 3, 60.0) is True
        assert limiter.allow("k", 3, 60.0) is True
        assert limiter.allow("k", 3, 60.0) is False


def test_allow_after_window_slides():
    limiter = SlidingWindowRateLimiter()
    with patch("core.rate_limit.time.monotonic", side_effect=[0.0, 0.1, 0.2, 61.0]):
        assert limiter.allow("k", 2, 60.0) is True
        assert limiter.allow("k", 2, 60.0) is True
        assert limiter.allow("k", 2, 60.0) is False
        assert limiter.allow("k", 2, 60.0) is True


def test_max_zero_disables_limit():
    limiter = SlidingWindowRateLimiter()
    with patch("core.rate_limit.time.monotonic", return_value=1.0):
        for _ in range(5):
            assert limiter.allow("k", 0, 60.0) is True


def test_window_zero_disables_limit():
    limiter = SlidingWindowRateLimiter()
    with patch("core.rate_limit.time.monotonic", return_value=1.0):
        for _ in range(5):
            assert limiter.allow("k", 3, 0.0) is True


def test_reset_clears_prior_events():
    limiter = SlidingWindowRateLimiter()
    with patch("core.rate_limit.time.monotonic", side_effect=[1.0, 1.1, 1.2, 1.3]):
        assert limiter.allow("k", 1, 60.0) is True
        assert limiter.allow("k", 1, 60.0) is False
        limiter.reset()
        assert limiter.allow("k", 1, 60.0) is True
