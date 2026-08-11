"""
Unit tests for the StealthBot class.

These tests focus on the initialization and configuration logic,
without requiring actual browser instances for most cases.
"""

import os
import platform
from unittest.mock import MagicMock, patch

import pytest

from sb_stealth_wrapper import (
    ChallengeNotSolvedError,
    StealthBot,
    StealthBotError,
    SuccessCriteriaNotMetError,
    __author__,
    __version__,
)
from sb_stealth_wrapper.strategies.evasion import CompositeEvasionStrategy


class TestModuleMetadata:
    """Tests for module-level attributes."""

    def test_version_is_string(self) -> None:
        """Version should be a string."""
        assert isinstance(__version__, str)

    def test_version_format(self) -> None:
        """Version should follow semantic versioning format."""
        parts = __version__.split(".")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)

    def test_author_is_set(self) -> None:
        """Author should be set correctly."""
        assert __author__ == "Dhiraj Das"


class TestExceptions:
    """Tests for custom exceptions."""

    def test_stealthbot_error_is_exception(self) -> None:
        """StealthBotError should be an Exception subclass."""
        assert issubclass(StealthBotError, Exception)

    def test_challenge_not_solved_error_is_stealthbot_error(self) -> None:
        """ChallengeNotSolvedError should be a StealthBotError subclass."""
        assert issubclass(ChallengeNotSolvedError, StealthBotError)

    def test_can_raise_stealthbot_error(self) -> None:
        """Should be able to raise and catch StealthBotError."""
        with pytest.raises(StealthBotError):
            raise StealthBotError("Test error")

    def test_can_raise_challenge_not_solved_error(self) -> None:
        """Should be able to raise and catch ChallengeNotSolvedError."""
        with pytest.raises(ChallengeNotSolvedError):
            raise ChallengeNotSolvedError("Challenge failed")


class TestStealthBotInit:
    """Tests for StealthBot initialization."""

    def test_default_values(self) -> None:
        """Test default initialization values."""
        bot = StealthBot()
        assert bot.proxy is None
        assert bot.screenshot_path == "debug_screenshots"
        assert bot.success_criteria is None
        assert bot.sb is None

    def test_custom_values(self) -> None:
        """Test custom initialization values."""
        bot = StealthBot(
            headless=True,
            proxy="user:pass@localhost:8080",
            screenshot_path="custom_screenshots",
            success_criteria="Welcome",
        )
        assert bot.proxy == "user:pass@localhost:8080"
        assert bot.screenshot_path == "custom_screenshots"
        assert bot.success_criteria == "Welcome"

    def test_screenshot_directory_creation(self, tmp_path: pytest.TempPathFactory) -> None:
        """Test that screenshot directory is created if it doesn't exist."""
        screenshot_dir = str(tmp_path / "new_screenshots")  # type: ignore[operator]
        assert not os.path.exists(screenshot_dir)

        StealthBot(screenshot_path=screenshot_dir)
        assert os.path.exists(screenshot_dir)

    @patch("sb_stealth_wrapper.driver.platform.system")
    @patch("sb_stealth_wrapper.driver.SB")
    def test_linux_detection_enables_xvfb(self, mock_sb: MagicMock, mock_system: MagicMock) -> None:
        """Test that Linux detection enables Xvfb and forces headed mode."""
        mock_system.return_value = "Linux"

        # We need to initialize the bot and enter the context to trigger driver.initialize()
        bot = StealthBot(headless=True)
        with bot:
            pass

        # Verify SB was initialized with correct arguments (xvfb=True, headless=False)
        mock_sb.assert_called_once()
        _, kwargs = mock_sb.call_args
        assert kwargs["xvfb"] is True
        assert kwargs["headless"] is False

    @patch("sb_stealth_wrapper.driver.platform.system")
    @patch("sb_stealth_wrapper.driver.SB")
    def test_windows_detection_no_xvfb(self, mock_sb: MagicMock, mock_system: MagicMock) -> None:
        """Test that Windows doesn't enable Xvfb."""
        mock_system.return_value = "Windows"

        bot = StealthBot(headless=False)
        with bot:
            pass

        mock_sb.assert_called_once()
        _, kwargs = mock_sb.call_args
        assert kwargs["xvfb"] is False


class TestStealthBotContextManager:
    """Tests for context manager behavior."""

    def test_ensure_initialized_raises_without_context(self) -> None:
        """Calling methods outside context manager should raise RuntimeError."""
        bot = StealthBot()
        with pytest.raises(RuntimeError, match="context manager"):
            bot.safe_get("https://example.com")

    def test_ensure_initialized_raises_for_smart_click(self) -> None:
        """smart_click should also raise RuntimeError outside context manager."""
        bot = StealthBot()
        with pytest.raises(RuntimeError, match="context manager"):
            bot.smart_click("#button")


class TestStealthBotClassConstants:
    """Tests for class-level constants."""

    def test_default_timeout(self) -> None:
        """DEFAULT_TIMEOUT should be a reasonable value."""
        assert StealthBot.DEFAULT_TIMEOUT == 15
        assert isinstance(StealthBot.DEFAULT_TIMEOUT, int)

    def test_max_challenge_retries(self) -> None:
        """MAX_CHALLENGE_RETRIES should be set."""
        assert StealthBot.MAX_CHALLENGE_RETRIES == 3
        assert isinstance(StealthBot.MAX_CHALLENGE_RETRIES, int)

    def test_challenge_indicators(self) -> None:
        """CHALLENGE_INDICATORS should contain expected keywords."""
        indicators = StealthBot.CHALLENGE_INDICATORS
        assert "challenge" in indicators
        assert "turnstile" in indicators
        assert "just a moment" in indicators
        assert "verify you are human" in indicators


class TestChallengeDetection:
    """Tests for challenge detection logic."""

    @pytest.mark.parametrize(
        "page_content,expected",
        [
            ("This page has a CHALLENGE to solve", True),
            ("Cloudflare Turnstile verification", True),
            ("Just a moment...", True),
            ("Please verify you are human", True),
            ("Welcome to our website!", False),
            ("Normal page content here", False),
        ],
    )
    def test_challenge_indicator_detection(self, page_content: str, expected: bool) -> None:
        """Test that challenge indicators are correctly detected."""
        src_lower = page_content.lower()
        is_challenge = any(indicator in src_lower for indicator in StealthBot.CHALLENGE_INDICATORS)
        assert is_challenge == expected

    @patch("sb_stealth_wrapper.time.sleep", return_value=None)
    def test_exhausted_challenge_raises_typed_error(self, _mock_sleep: MagicMock) -> None:
        bot = StealthBot()
        bot.sb = MagicMock()
        bot.sb.get_page_source.return_value = "Just a moment - verify you are human"
        bot.sb.is_element_visible.return_value = False

        with pytest.raises(ChallengeNotSolvedError, match="3 recovery attempts"):
            bot._handle_challenges()

        assert bot.sb.uc_gui_click_captcha.call_count == bot.MAX_CHALLENGE_RETRIES
        assert bot.sb.get_page_source.call_count == bot.MAX_CHALLENGE_RETRIES + 1

    @patch("sb_stealth_wrapper.time.sleep", return_value=None)
    def test_missing_success_criteria_raises_distinct_error(self, _mock_sleep: MagicMock) -> None:
        bot = StealthBot(success_criteria="Dashboard")
        bot.sb = MagicMock()
        bot.sb.get_page_source.return_value = "ordinary page"
        bot.sb.is_text_visible.return_value = False

        with pytest.raises(SuccessCriteriaNotMetError, match="Dashboard"):
            bot._handle_challenges()

        assert bot.sb.get_page_source.call_count == bot.MAX_CHALLENGE_RETRIES + 1

    @patch("sb_stealth_wrapper.time.sleep", return_value=None)
    def test_success_after_final_recovery_is_verified(self, _mock_sleep: MagicMock) -> None:
        bot = StealthBot()
        bot.sb = MagicMock()
        bot.sb.get_page_source.side_effect = [
            "Just a moment",
            "Just a moment",
            "Just a moment",
            "ordinary page",
        ]
        bot.sb.is_element_visible.return_value = False

        bot._handle_challenges()

        assert bot.sb.uc_gui_click_captcha.call_count == bot.MAX_CHALLENGE_RETRIES
        assert bot.sb.get_page_source.call_count == bot.MAX_CHALLENGE_RETRIES + 1

    @patch("sb_stealth_wrapper.time.sleep", return_value=None)
    def test_delayed_success_criteria_is_polled(self, _mock_sleep: MagicMock) -> None:
        bot = StealthBot(success_criteria="Dashboard")
        bot.sb = MagicMock()
        bot.sb.get_page_source.return_value = "ordinary page"
        bot.sb.is_text_visible.side_effect = [False, False, True]

        bot._handle_challenges()

        assert bot.sb.is_text_visible.call_count == 3

    def test_visible_success_criteria_returns_normally(self) -> None:
        bot = StealthBot(success_criteria="Dashboard")
        bot.sb = MagicMock()
        bot.sb.get_page_source.return_value = "ordinary page"
        bot.sb.is_text_visible.return_value = True

        bot._handle_challenges()


class TestExplicitClickFailures:
    def test_fallback_click_raises_when_every_attempt_fails(self) -> None:
        bot = StealthBot()
        bot.sb = MagicMock()
        bot.sb.get_page_source.return_value = "ordinary page"
        bot.sb.click.side_effect = RuntimeError("click failed")
        bot.sb.js_click.side_effect = RuntimeError("js click failed")

        with pytest.raises(StealthBotError, match="Could not click selector"):
            bot._fallback_click("#submit")

        assert bot.sb.click.call_count == 2

    def test_javascript_fallback_success_returns_normally(self) -> None:
        bot = StealthBot()
        bot.sb = MagicMock()
        bot.sb.click.side_effect = RuntimeError("click failed")

        bot._fallback_click("#submit")

        bot.sb.js_click.assert_called_once_with("#submit")

    def test_public_smart_click_propagates_typed_failure(self) -> None:
        bot = StealthBot()
        bot.sb = MagicMock()
        bot.sb.get_page_source.return_value = "ordinary page"
        bot.input_strategy = MagicMock()
        bot.input_strategy.click.side_effect = RuntimeError("strategy failed")
        bot.sb.click.side_effect = RuntimeError("click failed")
        bot.sb.js_click.side_effect = RuntimeError("js click failed")

        with pytest.raises(StealthBotError, match="Could not click selector"):
            bot.smart_click("#submit")


def test_navigation_log_destination_redacts_sensitive_url_components() -> None:
    safe = StealthBot._safe_destination_for_log(
        "https://user:password@example.com/private/path?token=secret#fragment"
    )
    assert safe == "https://example.com"


def test_fingerprint_mutation_is_disabled_by_default() -> None:
    assert CompositeEvasionStrategy().strategies == []
