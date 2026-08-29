# SB Stealth Wrapper

[![CI](https://github.com/godhiraj-code/stealthautomation/actions/workflows/ci.yml/badge.svg)](https://github.com/godhiraj-code/stealthautomation/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/sb-stealth-wrapper.svg)](https://pypi.org/project/sb-stealth-wrapper/)

A small reliability wrapper around SeleniumBase UC Mode for **authorized browser testing** on applications that use modern bot defenses.

SB Stealth Wrapper standardizes browser setup, bounded challenge recovery, explicit failure behavior, fallback clicks, screenshots, and variable input timing. It does not guarantee that a site will accept automated traffic, solve every challenge, or make automation undetectable.

## Install

```bash
python -m pip install sb-stealth-wrapper
```

Python 3.9 or newer is required. On Linux, `headless=True` runs without a virtual display;
headed execution (`headless=False`) requires `xvfb`:

```bash
sudo apt-get install xvfb
```

## Quick start

```python
from sb_stealth_wrapper import StealthBot

with StealthBot(headless=False) as bot:
    bot.safe_get("https://test.example.com/login")
    bot.smart_click("#login-button")
    bot.sb.wait_for_text("Dashboard", timeout=15)
    bot.save_screenshot("after-login")
```

Use the package only on systems you own or have explicit permission to test.

## Failure contract

`safe_get()` returns only after one of these conditions is proven:

- the configured `success_criteria` text is visible; or
- no challenge is detected and no explicit success criterion was requested.

After three unsuccessful challenge-recovery attempts it performs one final state read and raises `ChallengeNotSolvedError` only if the challenge remains. When a page has no challenge but configured text remains absent after four bounded checks, it raises `SuccessCriteriaNotMetError`.

`success_criteria` applies to the current navigation outcome. Do not configure text that can appear only after a future click; verify post-click state explicitly as shown above.

`smart_click()` attempts:

1. the configured input strategy;
2. a standard SeleniumBase click;
3. a JavaScript click;
4. bounded challenge recovery and one final standard click.

If those attempts fail, it raises `StealthBotError` instead of silently continuing.

## API

```python
StealthBot(
    headless=False,
    proxy=None,
    screenshot_path="debug_screenshots",
    success_criteria=None,
    driver_strategy=None,
    input_strategy=None,
    evasion_strategy=None,
)
```

### `safe_get(url)`

Navigates to a URL, waits for the document body, checks known challenge indicators, and enforces the failure contract above.

### `smart_click(selector)`

Uses variable pre-click timing and SeleniumBase UC click behavior, then bounded fallbacks. The package does **not** claim Bezier mouse movement.

### `smart_type(selector, text)`

Types with variable delays. The default strategy may insert and immediately correct an occasional typo.

### `save_screenshot(name)`

Writes `<name>.png` under `screenshot_path` and returns the resulting path. `name` must be a
plain filename stem, not a path; path separators are rejected.

## Strategies

The strategy interfaces remain injectable for application-specific testing:

```python
from sb_stealth_wrapper import StealthBot
from sb_stealth_wrapper.strategies.input import StandardInputStrategy

with StealthBot(input_strategy=StandardInputStrategy()) as bot:
    bot.safe_get("https://test.example.com")
```

Fingerprint mutation is disabled by default in 0.5.0. `CanvasPoisoningStrategy` and `AudioContextNoiseStrategy` remain experimental opt-in components; they do not promise stable or undetectable fingerprints.

## Testing policy

Deterministic unit tests and package builds run in required CI. Third-party anti-bot pages are unsuitable as release gates because their behavior can change independently of this package. Live checks belong in explicitly authorized manual testing, with real assertions and non-zero failure exits.

## Limitations

- Bot-defense behavior varies by site, IP reputation, browser version, and policy.
- Challenge detection is keyword-based and can produce false positives or false negatives.
- The package does not bypass authorization, rate limits, access controls, or a site's terms.
- `headless=False` generally offers behavior closer to an interactive browser; it is not a guarantee of acceptance.

## Development

```bash
python -m pip install -c requirements-ci.txt -e ".[dev]" build twine
python -m pytest -q
python -m black --fast --check sb_stealth_wrapper tests examples
python -m isort --check-only sb_stealth_wrapper tests examples
python -m mypy sb_stealth_wrapper
python -m compileall -q sb_stealth_wrapper tests
python -m build
python -m twine check dist/*
```

Set `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` when you want the same isolated pytest-plugin behavior
used by CI.

## License and responsible use

MIT. Created by [Dhiraj Das](https://www.dhirajdas.dev) and built on [SeleniumBase](https://github.com/seleniumbase/SeleniumBase).

Use only for legitimate QA, resilience testing, and automation on systems you are authorized to test. Do not use it for unauthorized scraping or to evade security controls on third-party services.
