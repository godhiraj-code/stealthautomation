# SB Stealth Wrapper: reliability lessons from authorized browser testing

## Context

QA teams sometimes need to test applications they own that are protected by browser-integrity or anti-bot controls. Direct Selenium sessions can behave differently from interactive user sessions, especially in Linux CI environments.

SB Stealth Wrapper is a small adapter around SeleniumBase UC Mode. It standardizes driver startup, headed Linux execution through Xvfb, bounded challenge detection, explicit failure behavior, screenshots, and injectable interaction strategies.

It does **not** make Selenium undetectable, guarantee challenge completion, or prove that a site will accept automated traffic.

## The reliability problem

Earlier versions had three credibility defects:

1. challenge retries could end without raising even when success was never proven;
2. click fallbacks could fail and return normally;
3. documentation described Bezier mouse movement and stable fingerprint mutation that the implementation did not prove.

Those defects made successful logs and green automation runs weaker evidence than they appeared.

## The 0.5.0 correction

Version 0.5.0 makes the outcome contract explicit:

- `safe_get()` reads page state before recovery and after each recovery attempt;
- a challenge remaining after three recovery attempts raises `ChallengeNotSolvedError`;
- configured text remaining absent after four bounded checks raises `SuccessCriteriaNotMetError`;
- exhausted click fallbacks raise `StealthBotError`;
- experimental canvas/audio mutation is disabled by default;
- the package no longer claims Bezier movement, consistent fingerprints, undetectability, or measured bypass rates.

External anti-bot pages are not required CI gates because their behavior can change independently of the package. Required CI uses deterministic unit tests, static checks, compilation, package building, metadata validation, and built-wheel installation.

## Supported environment

The package metadata requires Python 3.9 or newer. The release candidate is tested across the Python versions and operating systems listed in its GitHub Actions workflow. Linux headed execution requires Xvfb.

These checks validate package behavior and installation. They do not certify acceptance by a specific third-party site.

## Minimal authorized example

```python
from sb_stealth_wrapper import StealthBot

with StealthBot(headless=False) as bot:
    bot.safe_get("https://test.example.com/login")
    bot.smart_click("#login-button")
    bot.sb.wait_for_text("Dashboard", timeout=15)
```

The target above represents an environment the tester owns or has explicit permission to test.

## Engineering lesson

For automation infrastructure, an explicit failure is more valuable than a sophisticated-looking false success. Release claims should describe verified behavior, not the intended mechanism or an uncontrolled third-party outcome.

## Responsible-use boundary

Use this package only for legitimate QA, resilience testing, and automation on systems you own or are authorized to test. It must not be used for unauthorized scraping, access-control evasion, or testing third-party systems without permission.
