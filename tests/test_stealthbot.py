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
    __author__,
    __version__,
)


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

    @patch("sb_stealth_wrapper.platform.system")
    def test_linux_detection_enables_xvfb(self, mock_system: MagicMock) -> None:
        """Test that Linux detection enables Xvfb and forces headed mode."""
        mock_system.return_value = "Linux"
        bot = StealthBot(headless=True)

        assert bot.is_linux is True
        assert bot.xvfb is True
        assert bot.headless is False  # Should be forced to False

    @patch("sb_stealth_wrapper.platform.system")
    def test_windows_detection_no_xvfb(self, mock_system: MagicMock) -> None:
        """Test that Windows doesn't enable Xvfb."""
        mock_system.return_value = "Windows"
        bot = StealthBot(headless=False)

        assert bot.is_linux is False
        assert bot.xvfb is False


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
        is_challenge = any(
            indicator in src_lower for indicator in StealthBot.CHALLENGE_INDICATORS
        )
        assert is_challenge == expected
