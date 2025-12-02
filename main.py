from sb_stealth_wrapper import StealthBot

# Usage Example
if __name__ == "__main__":
    # 1. Initialize with context manager (auto-handles setup/teardown)
    with StealthBot(headless=False) as bot:
        # 2. Navigate safely to a protected site
        print("--- Testing Protected Site (nowsecure.nl) ---")
        bot.safe_get("https://nowsecure.nl")
        bot.save_screenshot("nowsecure_initial")
        
        # Verify we passed the challenge
        try:
            # Wait longer and print what we see
            bot.sb.wait_for_text("OH YEAH, you passed!", timeout=30)
            print("SUCCESS: Passed nowsecure.nl challenge!")
        except Exception as e:
            print(f"FAILURE: Did not see success message on nowsecure.nl. Error: {e}")
            print("Visible Text on Page:")
            print(bot.sb.get_text("body")[:500]) # Print first 500 chars
            with open("nowsecure_debug.html", "w", encoding="utf-8") as f:
                f.write(bot.sb.get_page_source())
            print("Saved nowsecure_debug.html")
            
        bot.save_screenshot("nowsecure_final")
        
        # 3. Test Smart Click (on a page with buttons)
        print("\n--- Testing Smart Click ---")
        bot.safe_get("https://seleniumbase.io/demo_page")
        bot.smart_click("#myButton") # Click the "Click Me" button (changes text to "Purple")
        
        # Verify the click worked
        if bot.sb.is_text_visible("Purple", "#myButton"):
            print("SUCCESS: Button clicked and text changed to 'Purple'")
        else:
            print("FAILURE: Button text did not change!")
            with open("debug_page_source.html", "w", encoding="utf-8") as f:
                f.write(bot.sb.get_page_source())
            print("Saved page source to debug_page_source.html")
            
        bot.save_screenshot("click_test")
        
        print("Done! Check debug_screenshots/")
