import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from playwright.sync_api import sync_playwright
from sb_stealth_wrapper import StealthBot

# Target URL
URL = "https://nowsecure.nl"
TIMEOUT = 15

def is_challenge_page(page_source):
    src = page_source.lower()
    return "just a moment" in src or "checking your browser" in src

def test_selenium():
    print("\n[Benchmark] Running Standard Selenium (Chrome)...")
    start_time = time.time()
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") 
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.get(URL)
        
        # Check for bot signal
        is_bot = driver.execute_script("return navigator.webdriver")
        print(f"   -> navigator.webdriver: {is_bot}")

        # Wait for "NOWSECURE" text
        WebDriverWait(driver, TIMEOUT).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "NOWSECURE")
        )
        
        # Strict Check: Ensure we are not on a challenge page
        if is_challenge_page(driver.page_source):
             print("[Result] Selenium: FAIL (Detected Challenge Page)")
             driver.quit()
             return "FAIL (Challenge)", time.time() - start_time

        duration = time.time() - start_time
        print(f"[Result] Selenium: PASS ({duration:.2f}s)")
        driver.quit()
        return f"PASS (Bot Detected: {is_bot})", duration
    except Exception as e:
        duration = time.time() - start_time
        print(f"[Result] Selenium: FAIL ({duration:.2f}s) - {str(e)[:100]}...")
        try:
            driver.quit()
        except:
            pass
        return "FAIL", duration

def test_playwright():
    print("\n[Benchmark] Running Playwright (Chromium)...")
    start_time = time.time()
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(URL)
            
            # Check for bot signal
            is_bot = page.evaluate("navigator.webdriver")
            print(f"   -> navigator.webdriver: {is_bot}")
            
            # Wait for "NOWSECURE" text
            page.wait_for_selector("text=NOWSECURE", timeout=TIMEOUT * 1000)
            
            # Strict Check
            content = page.content()
            if is_challenge_page(content):
                 print("[Result] Playwright: FAIL (Detected Challenge Page)")
                 browser.close()
                 return "FAIL (Challenge)", time.time() - start_time
            
            duration = time.time() - start_time
            print(f"[Result] Playwright: PASS ({duration:.2f}s)")
            browser.close()
            return f"PASS (Bot Detected: {is_bot})", duration
    except Exception as e:
        duration = time.time() - start_time
        print(f"[Result] Playwright: FAIL ({duration:.2f}s) - {str(e)[:100]}...")
        return "FAIL", duration

def test_stealthbot():
    print("\n[Benchmark] Running StealthBot...")
    start_time = time.time()
    
    try:
        with StealthBot(headless=False, success_criteria="NOWSECURE") as bot:
            bot.safe_get(URL)
            
            # Check for bot signal
            is_bot = bot.sb.execute_script("return navigator.webdriver")
            print(f"   -> navigator.webdriver: {is_bot}")
            
            # Wait for "NOWSECURE" text
            bot.sb.wait_for_text("NOWSECURE", timeout=TIMEOUT)
            
            # Strict Check
            if is_challenge_page(bot.sb.get_page_source()):
                 # StealthBot should have handled it, so if it's still here, it failed
                 print("[Result] StealthBot: FAIL (Detected Challenge Page)")
                 return "FAIL (Challenge)", time.time() - start_time

            duration = time.time() - start_time
            print(f"[Result] StealthBot: PASS ({duration:.2f}s)")
            return f"PASS (Bot Detected: {is_bot})", duration
    except Exception as e:
        duration = time.time() - start_time
        print(f"[Result] StealthBot: FAIL ({duration:.2f}s) - {str(e)[:100]}...")
        return "FAIL", duration

if __name__ == "__main__":
    print("=== Starting Benchmark Comparison ===")
    print(f"Target: {URL}")
    print(f"Timeout: {TIMEOUT}s")
    
    results = []
    
    # Run tests
    results.append(("Selenium", *test_selenium()))
    results.append(("Playwright", *test_playwright()))
    results.append(("StealthBot", *test_stealthbot()))
    
    # Print Summary
    print("\n" + "="*40)
    print(f"{'Tool':<15} | {'Status':<10} | {'Time':<10}")
    print("-" * 40)
    for tool, status, duration in results:
        print(f"{tool:<15} | {status:<10} | {duration:.2f}s")
    print("="*40)
