import os
import platform
import time
from seleniumbase import SB

class StealthBot:
    """
    A robust, 'plug-and-play' wrapper around SeleniumBase UC Mode for stealth web automation.
    Abstracts complexity into a single class.
    """

    def __init__(self, headless=False, proxy=None, screenshot_path="debug_screenshots", success_criteria=None):
        """
        Initialize the StealthBot.

        Args:
            headless (bool): Whether to run in headless mode. Defaults to False.
            proxy (str): Optional proxy string (e.g., "user:pass@host:port").
            screenshot_path (str): Path to save debug screenshots.
            success_criteria (str): Optional text to wait for to confirm success (e.g., "Welcome").
                                  If None, bot relies on challenge disappearance.
        """
        self.headless = headless
        self.proxy = proxy
        self.screenshot_path = screenshot_path
        self.success_criteria = success_criteria
        self.sb = None
        
        # Ensure screenshot directory exists
        if self.screenshot_path and not os.path.exists(self.screenshot_path):
            os.makedirs(self.screenshot_path)

        # Auto-detect Linux/CI environment
        self.is_linux = platform.system() == "Linux"
        self.xvfb = False
        
        if self.is_linux:
            # On Linux/CI, true headless is often detected. 
            # We use Xvfb (virtual display) with headed mode for better stealth.
            print("[StealthBot] Linux detected. Enabling Xvfb and disabling native headless mode for stealth.")
            self.xvfb = True
            self.headless = False # Force headed mode inside Xvfb

    def __enter__(self):
        """
        Context manager entry. Initializes the SeleniumBase SB instance.
        """
        # Initialize SB with UC mode enabled by default
        self.sb_context = SB(
            uc=True,
            headless=self.headless,
            xvfb=self.xvfb,
            proxy=self.proxy,
            test=False, # Disable test mode features that might reveal automation
            rtf=False,  # Disable "Rich Text Format" logs
        )
        self.sb = self.sb_context.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit. Cleans up the SeleniumBase SB instance.
        """
        if self.sb_context:
            self.sb_context.__exit__(exc_type, exc_val, exc_tb)

    def safe_get(self, url):
        """
        Safely navigates to a URL with built-in evasion and captcha handling.

        Args:
            url (str): The URL to navigate to.
        """
        if not self.sb:
            raise RuntimeError("StealthBot must be used within a context manager (with StealthBot() as bot:)")

        print(f"[StealthBot] Navigating to {url}...")
        self.sb.open(url) # Open URL using SeleniumBase's standard open which handles waiting
        
        # Smart wait for body to ensure page load (sb.open usually waits, but this is extra safety)
        print("[StealthBot] Waiting for page content...")
        self.sb.wait_for_element("body", timeout=15)
        
        # Check for common challenges (case-insensitive)
        self._handle_challenges()

    def smart_click(self, selector):
        """
        Clicks an element with auto-evasion logic. 
        If a captcha is detected, it attempts to solve it.
        Otherwise, uses human-like mouse movements.

        Args:
            selector (str): CSS selector of the element to click.
        """
        if not self.sb:
            raise RuntimeError("StealthBot must be used within a context manager")

        # Check for challenges before clicking
        self._handle_challenges()

        print(f"[StealthBot] Smart clicking '{selector}'...")
        try:
            # Ensure element is present and visible
            self.sb.wait_for_element_visible(selector, timeout=10)
            self.sb.scroll_to_element(selector)
            time.sleep(0.5) # Brief human-like pause
            
            # Attempt human-like click (UC mode's click is already enhanced)
            self.sb.uc_click(selector) 
        except Exception as e:
            print(f"[StealthBot] uc_click failed: {e}. Retrying with standard click...")
            # Fallback to standard click if UC click fails (sometimes UC click is flaky on some elements)
            try:
                self.sb.click(selector)
            except Exception as e2:
                print(f"[StealthBot] Standard click also failed: {e2}. Attempting JS Click (Last Resort)...")
                try:
                    self.sb.js_click(selector)
                except Exception as e3:
                    print(f"[StealthBot] All click methods failed: {e3}. Checking for captcha...")
                    self._handle_challenges()

    def _handle_challenges(self):
        """
        Internal method to detect and solve Cloudflare/Turnstile challenges.
        """
        max_retries = 3
        for attempt in range(max_retries):
            page_source = self.sb.get_page_source()
            src_lower = page_source.lower()
            
            # Common keywords for Cloudflare / Turnstile / Captchas
            challenge_indicators = ["challenge", "turnstile", "just a moment", "verify you are human"]
            is_challenge_present = any(indicator in src_lower for indicator in challenge_indicators)

            if is_challenge_present:
                print(f"[StealthBot] Challenge detected (Attempt {attempt+1}/{max_retries}). Engaging evasion protocols...")
                
                # Wait a bit for animations/loading/rendering
                time.sleep(2)
                
                try:
                    # Try SeleniumBase's specialized captcha clicker
                    self.sb.uc_gui_click_captcha()
                    print("[StealthBot] Captcha interaction attempted (uc_gui_click_captcha).")
                    time.sleep(4) # Wait for reaction
                except Exception as e:
                    print(f"[StealthBot] standard captcha click failed: {e}")
                
                # Fallback: Try clicking the container directly if specialized method failed
                try:
                    if self.sb.is_element_visible(".cf-turnstile"):
                        print("[StealthBot] Attempting fallback click on .cf-turnstile...")
                        self.sb.uc_click(".cf-turnstile")
                        time.sleep(4)
                except Exception:
                    pass

                # If we have run out of retries and still see challenge, we warn.
                # If we loop back, strict Mode will re-check criteria or challenge indicators.
            else:
                # No challenge detected. Now checks success criteria if defined.
                if self.success_criteria:
                    if self.sb.is_text_visible(self.success_criteria):
                        print(f"[StealthBot] Success criteria '{self.success_criteria}' met!")
                        return
                    else:
                        # No challenge seen, but success criteria NOT met.
                        # Could be loading? We'll wait a brief moment in the loop or just return if naive.
                        # Better: Continue to ensure we don't miss a late-loading challenge, 
                        # but we need a break condition so we don't loop forever if it's just a slow site.
                        pass 
                else:
                    # No criteria, no challenge -> Assume success.
                    print("[StealthBot] No challenge detected. Assuming access granted.")
                    return
        
        print("[StealthBot] Warning: Max retries reached for challenge solving.")

    def save_screenshot(self, name):
        """Helper to save screenshot to the configured path."""
        if self.screenshot_path:
            filename = os.path.join(self.screenshot_path, f"{name}.png")
            self.sb.save_screenshot(filename)
            print(f"[StealthBot] Screenshot saved to {filename}")
