from sb_stealth_wrapper import StealthBot

# Usage Example
if __name__ == "__main__":
    # 1. Initialize with context manager (auto-handles setup/teardown)
    # We pass 'NOWSECURE' as the specific success criteria for this demo site.
    with StealthBot(headless=False, success_criteria="NOWSECURE") as bot:
        # 2. Navigate safely to a protected site
        print("--- Testing Protected Site (nowsecure.nl) ---")
        bot.safe_get("https://nowsecure.nl")
        bot.save_screenshot("nowsecure_initial")

        # Verify we passed the challenge
        try:
            # Wait longer and print what we see
            # "OH YEAH, you passed!" is no longer present. We check for "NOWSECURE".
            bot.sb.wait_for_text("NOWSECURE", timeout=30)
            print("SUCCESS: Passed nowsecure.nl challenge (verified 'NOWSECURE' text)!")
        except Exception as e:
            raise RuntimeError("Manual smoke test did not prove the expected page state") from e

        bot.save_screenshot("nowsecure_final")

        # 3. Test Smart Click (on a page with buttons)
        print("\n--- Testing Smart Click ---")
        bot.success_criteria = None
        bot.safe_get("https://seleniumbase.io/demo_page")
        bot.smart_click("#myButton")  # Click the "Click Me" button (changes text to "Purple")

        # Verify the click worked
        if bot.sb.is_text_visible("Purple", "#myButton"):
            print("SUCCESS: Button clicked and text changed to 'Purple'")
        else:
            raise RuntimeError("Manual smoke test click did not produce the expected state")

        bot.save_screenshot("click_test")

        print("Done! Check debug_screenshots/")
