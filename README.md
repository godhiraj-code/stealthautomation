# SB Stealth Wrapper

[![CI](https://github.com/godhiraj-code/stealthautomation/actions/workflows/ci.yml/badge.svg)](https://github.com/godhiraj-code/stealthautomation/actions/workflows/ci.yml)

A robust, 'plug-and-play' wrapper around **SeleniumBase UC Mode** for stealth web automation.

## 🚀 Why Use This Package?

Modern web automation often requires complex configurations to bypass bot detection systems like Cloudflare Turnstile. **SB Stealth Wrapper** abstracts this complexity into a single, easy-to-use class.

It handles:
- **Auto-Evasion**: Automatically configures the environment for maximum stealth (e.g., using `xvfb` on Linux).
- **Smart Interactions**: Provides human-like clicking and navigation methods that automatically handle scrolling, waiting, and captcha detection.
- **Generic Challenge Management**: Detects common challenge screens and attempts to solve them, while allowing you to define custom success criteria for any site.

It allows you to focus on *what* your bot needs to do, rather than *how* to keep it undetected.

---

## 📦 Installation

### 1. Install via pip

```bash
pip install sb-stealth-wrapper
```

### 2. Prerequisites (Linux / Docker Only)

If you are running this on a Linux server or inside a Docker container (like GitHub Actions), you **MUST** install `xvfb`.

**Why?**
Stealth automation works best in "headed" mode (where the browser GUI is visible). Native "headless" mode is easily detected by anti-bots. `xvfb` creates a "virtual display" so the browser thinks it has a screen, allowing it to run in headed mode on a headless server.

```bash
# Debian / Ubuntu
sudo apt-get install xvfb
```

---

## ⚡ Quick Start

Here is the minimal code to get started. This example navigates to a site and clicks a button safely.

```python
from sb_stealth_wrapper import StealthBot

# Initialize the bot
# Use success_criteria to tell the bot what text confirms the page is fully loaded/unlocked.
with StealthBot(headless=False, success_criteria="Welcome") as bot:
    
    # 1. Navigate safely
    bot.safe_get("https://example.com/protected-page")
    
    # 2. Click elements with auto-evasion
    bot.smart_click("#login-button")
    
    # 3. Save a screenshot for debugging
    bot.save_screenshot("debug_step_1")
```

---

## 🛠️ Detailed Usage & API Reference

### `StealthBot` Class

The main entry point. Use it as a context manager (`with ...`) to ensure the browser closes properly.

```python
StealthBot(
    headless=False, 
    proxy=None, 
    screenshot_path="debug_screenshots",
    success_criteria=None
)
```

**Parameters:**
- `headless` (bool): Defaults to `False`. **Recommended**. True headless mode is risky for stealth. On Linux, this is automatically managed (see *Core Concepts*).
- `proxy` (str): Optional. Format: `user:pass@host:port`.
- `screenshot_path` (str): Directory where screenshots are saved. Created automatically.
- `success_criteria` (str): Optional. A specific string to wait for (e.g., "Dashboard", "Login Successful") which confirms that challenges are passed. If `None`, the bot relies on the *disappearance* of challenge words (like "Turnstile") to assume success.

### `bot.safe_get(url)`

Navigates to a URL and immediately checks for challenges.

- **What it does**: Opens the URL → Waits for `<body>` → Checks for "Challenge"/"Turnstile" → auto-solves if found.

### `bot.smart_click(selector)`

A stealthy alternative to standard clicks.

- **What it does**: 
    1. Checks for challenges *before* clicking.
    2. Scrolls the element into view.
    3. waits for it to be visible.
    4. Attempts a "Human" click (UC Mode).
    5. **Fallbacks**: If the human click fails, it tries a standard Selenium click, then a JavaScript click, ensuring high reliability.

---

## 🧠 Core Concepts & Best Practices

### The "Headed vs Headless" Dilemma
Anti-bot systems (Cloudflare, Akamai, etc.) aggressively target "Headless Chrome". 
- **Rule of Thumb**: ALWAYS run with `headless=False` for stealth.
- **On Servers**: Use `xvfb` (as explained in Installation) to run `headless=False` on a server without a monitor. `StealthBot` detects Linux automatically and configures this for you!

### Challenge Handling Logic
The bot uses a smart loop to handle challenges:
1. **Detection**: It scans the page source for keywords: "challenge", "turnstile", "verify you are human".
2. **Action**: If found, it uses SeleniumBase's `uc_gui_click_captcha` (simulating a real human mouse) to click the checkbox.
3. **Verification**: 
   - If `success_criteria="My Dashboard"` was passed, it waits until that text appears.
   - If not, it waits until "challenge" text disappears.

---

## ⚠️ Edge Cases & Troubleshooting

### 1. The Bot Gets Stuck in a Loop
If the bot keeps clicking the challenge but it never solves:
- **Solution**: The IP might be bad (if using a proxy), or the site needs a stronger interaction. Try increasing `time.sleep` in your own script or manually slowing down interactions.
- `StealthBot` will try 3 times and then warn you ("Max retries reached") to prevent infinite hangs.

### 2. "Element Not Found" Errors
`smart_click` is robust, but if the page is heavy with JavaScript:
- Ensure you used `success_criteria` in `__init__` so the bot *really* waits for the page to be ready before trying to click.

### 3. CI/GitHub Actions Fails
- **Did you install `xvfb`?** Check the prerequisites.
- **Screen Size**: Sometimes elements are off-screen. The bot uses `scroll_to_element` automatically, but you can also try setting a window size explicitly using the underlying `bot.sb.set_window_size(1920, 1080)`.

---

## Credits & Disclaimer

Built on top of the incredible [SeleniumBase](https://github.com/seleniumbase/SeleniumBase) by **Michael Mintz**.

**Ethical Use Only**: This tool is for testing your own infrastructure or sites you have permission to test. Do not use for unauthorized scraping or bypassing security controls on 3rd party services.
