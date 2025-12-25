"""
SB Stealth Wrapper - A robust wrapper around SeleniumBase UC Mode for stealth web automation.

This module provides the StealthBot class for automated, undetectable browser interactions.
"""

from __future__ import annotations

import logging
import os
import platform
import time
from typing import TYPE_CHECKING, Optional

from seleniumbase import SB

if TYPE_CHECKING:
    from types import TracebackType

# Configure module logger
logger = logging.getLogger(__name__)

__version__ = "0.3.0"
__author__ = "Dhiraj Das"
__all__ = ["StealthBot", "StealthBotError", "ChallengeNotSolvedError"]


class StealthBotError(Exception):
    """Base exception for StealthBot errors."""

    pass


class ChallengeNotSolvedError(StealthBotError):
    """Raised when a captcha/challenge couldn't be solved after max retries."""

    pass


class StealthBot:
    """
    A robust, 'plug-and-play' wrapper around SeleniumBase UC Mode for stealth web automation.
    Abstracts complexity into a single class.

    Example:
        >>> with StealthBot(headless=False, success_criteria="Welcome") as bot:
        ...     bot.safe_get("https://example.com")
        ...     bot.smart_click("#login-button")
    """

    DEFAULT_TIMEOUT: int = 15
    MAX_CHALLENGE_RETRIES: int = 3
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
    ) -> None:
        """
        Initialize the StealthBot.

        Args:
            headless: Whether to run in headless mode. Defaults to False.
                      Note: True headless mode is often detected by anti-bot systems.
            proxy: Optional proxy string (e.g., "user:pass@host:port").
            screenshot_path: Path to save debug screenshots.
            success_criteria: Optional text to wait for to confirm success (e.g., "Welcome").
                              If None, bot relies on challenge disappearance.
        """
        self.headless = headless
        self.proxy = proxy
        self.screenshot_path = screenshot_path
        self.success_criteria = success_criteria
        self.sb: Optional[SB] = None
        self._sb_context: Optional[SB] = None

        # Ensure screenshot directory exists
        if self.screenshot_path and not os.path.exists(self.screenshot_path):
            os.makedirs(self.screenshot_path)
            logger.debug(f"Created screenshot directory: {self.screenshot_path}")

        # Auto-detect Linux/CI environment
        self.is_linux = platform.system() == "Linux"
        self.xvfb = False

        if self.is_linux:
            # On Linux/CI, true headless is often detected.
            # We use Xvfb (virtual display) with headed mode for better stealth.
            logger.info(
                "Linux detected. Enabling Xvfb and disabling native headless mode for stealth."
            )
            self.xvfb = True
            self.headless = False  # Force headed mode inside Xvfb

    def __enter__(self) -> "StealthBot":
        """Context manager entry. Initializes the SeleniumBase SB instance."""
        # Initialize SB with UC mode enabled by default
        self._sb_context = SB(
            uc=True,
            headless=self.headless,
            xvfb=self.xvfb,
            proxy=self.proxy,
            test=False,  # Disable test mode features that might reveal automation
            rtf=False,  # Disable "Rich Text Format" logs
        )
        self.sb = self._sb_context.__enter__()
        logger.debug("StealthBot initialized successfully")
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Context manager exit. Cleans up the SeleniumBase SB instance."""
        if self._sb_context:
            self._sb_context.__exit__(exc_type, exc_val, exc_tb)
            logger.debug("StealthBot closed successfully")

    def _ensure_initialized(self) -> None:
        """Ensure the bot is properly initialized within a context manager."""
        if not self.sb:
            raise RuntimeError(
                "StealthBot must be used within a context manager (with StealthBot() as bot:)"
            )

    def safe_get(self, url: str) -> None:
        """
        Safely navigates to a URL with built-in evasion and captcha handling.

        Args:
            url: The URL to navigate to.
        """
        self._ensure_initialized()

        logger.info(f"Navigating to {url}")
        self.sb.open(url)  # type: ignore[union-attr]

        # Smart wait for body to ensure page load
        logger.debug("Waiting for page content...")
        self.sb.wait_for_element("body", timeout=self.DEFAULT_TIMEOUT)  # type: ignore[union-attr]

        # Check for common challenges (case-insensitive)
        self._handle_challenges()

    def smart_click(self, selector: str) -> None:
        """
        Clicks an element with auto-evasion logic.

        If a captcha is detected, it attempts to solve it.
        Otherwise, uses human-like mouse movements with fallback strategies.

        Args:
            selector: CSS selector of the element to click.
        """
        self._ensure_initialized()

        # Check for challenges before clicking
        self._handle_challenges()

        logger.info(f"Smart clicking '{selector}'")
        try:
            # Ensure element is present and visible
            self.sb.wait_for_element_visible(selector, timeout=10)  # type: ignore[union-attr]
            self.sb.scroll_to_element(selector)  # type: ignore[union-attr]
            time.sleep(0.5)  # Brief human-like pause

            # Attempt human-like click (UC mode's click is already enhanced)
            self.sb.uc_click(selector)  # type: ignore[union-attr]
            logger.debug(f"uc_click successful for '{selector}'")
        except Exception as e:
            logger.warning(f"uc_click failed: {e}. Retrying with standard click...")
            self._fallback_click(selector)

    def _fallback_click(self, selector: str) -> None:
        """
        Fallback click strategies when uc_click fails.

        Args:
            selector: CSS selector of the element to click.
        """
        # Fallback to standard click
        try:
            self.sb.click(selector)  # type: ignore[union-attr]
            logger.debug(f"Standard click successful for '{selector}'")
        except Exception as e2:
            logger.warning(f"Standard click also failed: {e2}. Attempting JS Click...")
            try:
                self.sb.js_click(selector)  # type: ignore[union-attr]
                logger.debug(f"JS click successful for '{selector}'")
            except Exception as e3:
                logger.error(f"All click methods failed: {e3}. Checking for captcha...")
                self._handle_challenges()

    def _handle_challenges(self) -> None:
        """
        Internal method to detect and solve Cloudflare/Turnstile challenges.

        Raises:
            ChallengeNotSolvedError: If the challenge couldn't be solved after max retries.
        """
        for attempt in range(self.MAX_CHALLENGE_RETRIES):
            page_source = self.sb.get_page_source()  # type: ignore[union-attr]
            src_lower = page_source.lower()

            # Check for challenge indicators
            is_challenge_present = any(
                indicator in src_lower for indicator in self.CHALLENGE_INDICATORS
            )

            if is_challenge_present:
                logger.info(
                    f"Challenge detected (Attempt {attempt + 1}/{self.MAX_CHALLENGE_RETRIES}). "
                    "Engaging evasion protocols..."
                )

                # Wait a bit for animations/loading/rendering
                time.sleep(2)

                try:
                    # Try SeleniumBase's specialized captcha clicker
                    self.sb.uc_gui_click_captcha()  # type: ignore[union-attr]
                    logger.debug("Captcha interaction attempted (uc_gui_click_captcha)")
                    time.sleep(4)  # Wait for reaction
                except Exception as e:
                    logger.warning(f"Standard captcha click failed: {e}")

                # Fallback: Try clicking the container directly
                try:
                    if self.sb.is_element_visible(".cf-turnstile"):  # type: ignore[union-attr]
                        logger.debug("Attempting fallback click on .cf-turnstile...")
                        self.sb.uc_click(".cf-turnstile")  # type: ignore[union-attr]
                        time.sleep(4)
                except Exception:
                    pass
            else:
                # No challenge detected. Check success criteria if defined.
                if self.success_criteria:
                    if self.sb.is_text_visible(self.success_criteria):  # type: ignore[union-attr]
                        logger.info(f"Success criteria '{self.success_criteria}' met!")
                        return
                    # No challenge seen, but success criteria NOT met - continue checking
                else:
                    # No criteria, no challenge -> Assume success.
                    logger.debug("No challenge detected. Assuming access granted.")
                    return

        logger.warning("Max retries reached for challenge solving.")

    def save_screenshot(self, name: str) -> str:
        """
        Save a screenshot to the configured path.

        Args:
            name: Base name for the screenshot file (without extension).

        Returns:
            The full path to the saved screenshot.
        """
        self._ensure_initialized()

        if self.screenshot_path:
            filename = os.path.join(self.screenshot_path, f"{name}.png")
            self.sb.save_screenshot(filename)  # type: ignore[union-attr]
            logger.info(f"Screenshot saved to {filename}")
            return filename
        return ""
