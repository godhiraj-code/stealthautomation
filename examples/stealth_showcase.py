"""Manual, assertion-based smoke test for an explicitly authorized target.

This script is intentionally excluded from deterministic CI because third-party
anti-bot behavior is not a stable release gate.
"""

from sb_stealth_wrapper import StealthBot


def verify_authorized_target() -> None:
    with StealthBot(headless=False, success_criteria="NOWSECURE") as bot:
        bot.safe_get("https://nowsecure.nl")
        if bot.sb is None or not bot.sb.is_text_visible("NOWSECURE"):
            raise RuntimeError("Expected success text was not visible")

        bot.success_criteria = None
        bot.safe_get("https://seleniumbase.io/demo_page")
        bot.smart_click("#myButton")
        if not bot.sb.is_text_visible("Purple", "#myButton"):
            raise RuntimeError("Click did not change button state")


if __name__ == "__main__":
    verify_authorized_target()
    print("Manual authorized-target smoke test passed")
