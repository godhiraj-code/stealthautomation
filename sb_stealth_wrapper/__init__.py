"""
SB Stealth Wrapper - A robust wrapper around SeleniumBase UC Mode for stealth web automation.

This module provides the StealthBot class for resilient, authorized browser testing.
"""

from __future__ import annotations

import logging
import os
import time
from typing import TYPE_CHECKING, Optional
from urllib.parse import urlsplit

from sb_stealth_wrapper.driver import SeleniumBaseDriver

# Import Strategies
from sb_stealth_wrapper.strategies.base import DriverStrategy, EvasionStrategy, InputStrategy
from sb_stealth_wrapper.strategies.evasion import CompositeEvasionStrategy
from sb_stealth_wrapper.strategies.input import HumanInputStrategy

if TYPE_CHECKING:
    from types import TracebackType

    from seleniumbase import SB

# Configure module logger
logger = logging.getLogger(__name__)

__version__ = "0.5.0"
__author__ = "Dhiraj Das"
__all__ = [
    "StealthBot",
    "StealthBotError",
    "ChallengeNotSolvedError",
    "SuccessCriteriaNotMetError",
]


class StealthBotError(Exception):
    """Base exception for StealthBot errors."""

    pass


class ChallengeNotSolvedError(StealthBotError):
    """Raised when a captcha/challenge couldn't be solved after max retries."""

    pass


class SuccessCriteriaNotMetError(StealthBotError):
    """Raised when requested page text is not visible within the bounded check."""

    pass


class StealthBot:
    """
    A bounded reliability wrapper around SeleniumBase UC Mode for authorized testing.

    Example:
        >>> with StealthBot(headless=False, success_criteria="Welcome") as bot:
        ...     bot.safe_get("https://example.com")
        ...     bot.smart_click("#login-button")
    """

    DEFAULT_TIMEOUT: int = 15
    MAX_CHALLENGE_RETRIES: int = 3
    CRITERIA_POLL_INTERVAL: float = 1.0
    CHALLENGE_INDICATORS: tuple[str, ...] = (
        "challenge",
        "turnstile",
        "just a moment",
        "verify you are human",
    )

    def __init__(
        self,
        headless: bool = False,
        proxy: Optional[str] = None,
        screenshot_path: str = "debug_screenshots",
        success_criteria: Optional[str] = None,
        # Strategy Injection
        driver_strategy: Optional[DriverStrategy] = None,
        input_strategy: Optional[InputStrategy] = None,
        evasion_strategy: Optional[EvasionStrategy] = None,
    ) -> None:
        """
        Initialize the StealthBot.

        Args:
            headless: Whether to run in headless mode.
            proxy: Optional proxy string.
            screenshot_path: Path to save debug screenshots.
            success_criteria: Optional text to wait for.
            driver_strategy: Custom driver strategy (default: SeleniumBaseDriver).
            input_strategy: Custom input strategy (default: HumanInputStrategy).
            evasion_strategy: Custom evasion strategy (default: CompositeEvasionStrategy).
        """
        self.headless = headless
        self.proxy = proxy
        self.screenshot_path = screenshot_path
        self.success_criteria = success_criteria

        # Initialize Strategies
        self.driver_strategy = driver_strategy or SeleniumBaseDriver()
        self.input_strategy = input_strategy or HumanInputStrategy()
        self.evasion_strategy = evasion_strategy or CompositeEvasionStrategy()

        self.sb: Optional[SB] = None

        # Ensure screenshot directory exists
        if self.screenshot_path and not os.path.exists(self.screenshot_path):
            os.makedirs(self.screenshot_path)

    def __enter__(self) -> "StealthBot":
        """Context manager entry."""
        self.sb = self.driver_strategy.initialize(headless=self.headless, proxy=self.proxy)

        # Apply Evasion Strategies immediately after launch
        if self.sb:
            self.evasion_strategy.apply(self.sb)

        logger.debug("StealthBot initialized successfully (Modular Mode)")
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Context manager exit."""
        self.driver_strategy.cleanup()
        logger.debug("StealthBot closed successfully")

    def _ensure_initialized(self) -> None:
        """Ensure the bot is properly initialized."""
        if not self.sb:
            raise RuntimeError(
                "StealthBot must be used within a context manager (with StealthBot() as bot:)"
            )

    def safe_get(self, url: str) -> None:
        """Navigate and require the configured page/challenge outcome."""
        self._ensure_initialized()

        logger.info("Navigating to %s", self._safe_destination_for_log(url))
        self.sb.open(url)  # type: ignore

        # Smart wait
        logger.debug("Waiting for page content...")
        self.sb.wait_for_element("body", timeout=self.DEFAULT_TIMEOUT)  # type: ignore

        self._handle_challenges()

    def smart_click(self, selector: str) -> None:
        """Click with variable timing, bounded fallbacks, and explicit failure."""
        self._ensure_initialized()
        self._handle_challenges()

        logger.info(f"Smart clicking '{selector}'")
        try:
            # Delegate to the configured input strategy.
            self.input_strategy.click(self.sb, selector)
        except Exception as e:
            logger.warning(f"Strategy click failed: {e}. Retrying with generic fallback...")
            self._fallback_click(selector)

    def smart_type(self, selector: str, text: str) -> None:
        """Types text with human-like delays and typos."""
        self._ensure_initialized()
        try:
            self.input_strategy.type(self.sb, selector, text)
        except Exception as e:
            logger.warning(f"Strategy type failed: {e}. Fallback to standard.")
            self.sb.type(selector, text)  # type: ignore

    def _fallback_click(self, selector: str) -> None:
        """Try bounded fallback clicks and fail explicitly when none succeeds."""
        try:
            self.sb.click(selector)  # type: ignore
            return
        except Exception:
            pass
        try:
            self.sb.js_click(selector)  # type: ignore
            return
        except Exception:
            pass

        self._handle_challenges()
        try:
            self.sb.click(selector)  # type: ignore
        except Exception as exc:
            raise StealthBotError(
                f"Could not click selector {selector!r} after standard, JavaScript, and challenge-recovery attempts."
            ) from exc

    def _handle_challenges(self) -> None:
        """Attempt bounded challenge recovery and raise when success is unproven."""
        challenge_seen = False

        # Read once before recovery and once after every recovery action. The
        # extra final read prevents a successful last attempt from being
        # reported as a failure.
        for attempt in range(self.MAX_CHALLENGE_RETRIES + 1):
            page_source = self.sb.get_page_source()  # type: ignore
            src_lower = page_source.lower()
            is_challenge = any(i in src_lower for i in self.CHALLENGE_INDICATORS)

            if is_challenge:
                challenge_seen = True
                if attempt == self.MAX_CHALLENGE_RETRIES:
                    break

                logger.info("Challenge detected (recovery attempt %s).", attempt + 1)
                time.sleep(2)

                try:
                    self.sb.uc_gui_click_captcha()  # type: ignore
                    time.sleep(4)
                except Exception:
                    pass

                if self.sb.is_element_visible(".cf-turnstile"):  # type: ignore
                    self.sb.uc_click(".cf-turnstile")  # type: ignore
                    time.sleep(4)
                continue

            if self.success_criteria:
                if self.sb.is_text_visible(self.success_criteria):  # type: ignore
                    return
                if attempt < self.MAX_CHALLENGE_RETRIES:
                    time.sleep(self.CRITERIA_POLL_INTERVAL)
                    continue
                raise SuccessCriteriaNotMetError(
                    f"Success criteria {self.success_criteria!r} was not visible after "
                    f"{self.MAX_CHALLENGE_RETRIES + 1} bounded checks."
                )

            return

        if challenge_seen:
            raise ChallengeNotSolvedError(
                f"Challenge remained after {self.MAX_CHALLENGE_RETRIES} recovery attempts."
            )

        raise StealthBotError("The requested page outcome could not be verified.")

    @staticmethod
    def _safe_destination_for_log(url: str) -> str:
        """Return a query-, fragment-, credential-, and path-free destination label."""
        try:
            parsed = urlsplit(url)
            if not parsed.scheme or not parsed.hostname:
                return "<unparseable destination>"
            port = f":{parsed.port}" if parsed.port is not None else ""
            return f"{parsed.scheme}://{parsed.hostname}{port}"
        except (TypeError, ValueError):
            return "<unparseable destination>"

    def save_screenshot(self, name: str) -> str:
        """Save a screenshot."""
        self._ensure_initialized()
        if self.screenshot_path:
            filename = os.path.join(self.screenshot_path, f"{name}.png")
            self.sb.save_screenshot(filename)  # type: ignore
            return filename
        return ""
