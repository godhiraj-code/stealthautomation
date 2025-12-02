# SB Stealth Wrapper

[![CI](https://github.com/godhiraj-code/stealthautomation/actions/workflows/ci.yml/badge.svg)](https://github.com/godhiraj-code/stealthautomation/actions/workflows/ci.yml)

A robust, 'plug-and-play' wrapper around **SeleniumBase UC Mode** for stealth web automation.

## Why Use This Package?

Modern web automation often requires complex configurations to bypass bot detection systems like Cloudflare Turnstile. **SB Stealth Wrapper** abstracts this complexity into a single, easy-to-use class. It handles:
- **Auto-Evasion**: Automatically configures the environment for maximum stealth (e.g., using `xvfb` on Linux).
- **Smart Interactions**: Provides human-like clicking and navigation methods that automatically handle scrolling, waiting, and retries.
- **Challenge Management**: Detects and attempts to solve captchas without interrupting your script's flow.

It allows you to focus on *what* your bot needs to do, rather than *how* to keep it undetected.

## Features

- **Auto-Evasion**: Automatically enables `uc=True` and handles Linux/CI environments with `xvfb`.
- **Stealth Navigation**: `safe_get(url)` handles page loads reliably and checks for challenges.
- **Smart Clicking**: `smart_click(selector)` attempts human-like clicks, with fallbacks to standard and JS clicks.
- **Challenge Solving**: Automatically detects and attempts to solve Cloudflare Turnstile and other challenges.

## Benchmark Comparison (Linux CI Environment)

We compared **StealthBot** against standard **Selenium** and **Playwright** in a GitHub Actions (Linux) environment targeting a protected site (`nowsecure.nl`).

| Tool | Status | Time | Notes |
|------|--------|------|-------|
| **Selenium** | FAIL | 0.50s | Crashed (No display for headed mode) |
| **Playwright** | FAIL | 0.36s | Crashed (No display for headed mode) |
| **StealthBot** | **PASS** | **3.65s** | **Auto-configured Xvfb & Passed Challenge** |

*Note: Standard drivers fail in CI because they must run in "Headed" mode to avoid detection, but Linux servers have no display. StealthBot automatically handles this by creating a virtual display (Xvfb).*

## Installation

```bash
pip install sb-stealth-wrapper
```

## Prerequisites

### Linux / Docker
If running on Linux or inside a Docker container, you must install `xvfb` to allow the bot to run in "headed" mode (which is required for stealth).

```bash
sudo apt-get install xvfb
```

## Usage

```python
from sb_stealth_wrapper import StealthBot

# Initialize the bot (headless=False recommended for debugging)
with StealthBot(headless=False) as bot:
    
    # Navigate safely to a URL
    bot.safe_get("https://example.com")
    
    # Click an element with auto-evasion and fallbacks
    bot.smart_click("#some-button")
    
    # Take a screenshot
    bot.save_screenshot("debug_image")
```

## Credits & Special Thanks

This project is a wrapper built upon the incredible work of the **[SeleniumBase](https://github.com/seleniumbase/SeleniumBase)** team. 

Special thanks to **Michael Mintz** and all SeleniumBase contributors for doing the heavy lifting in creating the underlying Undetected ChromeDriver (UC Mode) integration. Their work makes our work as automation testers so so easy. Many Thanks 

## Disclaimer

**Ethical Use Only**: This package is intended for educational purposes and for testing environments that **you own or have explicit permission to test**. 

- Do not use this tool for unauthorized scraping, spamming, or bypassing security controls on websites you do not own.
- The authors of this package are not responsible for any misuse or legal consequences resulting from the use of this software.
- Always adhere to the target website's `robots.txt` and Terms of Service.
