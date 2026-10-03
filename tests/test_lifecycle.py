from unittest.mock import Mock

import pytest

from sb_stealth_wrapper import StealthBot
from sb_stealth_wrapper.driver import SeleniumBaseDriver


def test_failed_setup_releases_browser(tmp_path):
    driver = Mock()
    evasion = Mock()
    evasion.apply.side_effect = ValueError("setup failed")
    bot = StealthBot(
        driver_strategy=driver, evasion_strategy=evasion, screenshot_path=str(tmp_path)
    )
    with pytest.raises(ValueError, match="setup failed"):
        bot.__enter__()
    driver.cleanup.assert_called_once()
    assert bot.sb is None


def test_use_after_exit_is_rejected(tmp_path):
    bot = StealthBot(driver_strategy=Mock(), evasion_strategy=Mock(), screenshot_path=str(tmp_path))
    with bot:
        pass
    with pytest.raises(RuntimeError, match="context manager"):
        bot.safe_get("https://example.com")


def test_driver_cleanup_is_idempotent():
    driver = SeleniumBaseDriver()
    context = Mock()
    context.__exit__ = Mock()
    driver._sb_context = context
    driver.sb = Mock()
    driver.cleanup()
    driver.cleanup()
    context.__exit__.assert_called_once_with(None, None, None)
    assert driver.sb is None
