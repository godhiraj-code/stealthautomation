# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-08-11

### Fixed
- Verify page state after the final challenge-recovery action before deciding failure.
- Raise `ChallengeNotSolvedError` when a challenge remains and `SuccessCriteriaNotMetError` when requested text remains absent.
- Raise `StealthBotError` when all click and recovery attempts fail.
- Make manual browser examples exit non-zero when expected outcomes are not proven.

### Changed
- Replace overstated stealth, Bezier-movement, and fingerprint-consistency claims with bounded behavior contracts.
- Disable experimental canvas/audio mutation by default; custom strategies remain opt-in.
- Replace third-party anti-bot pages as required CI gates with deterministic tests and package validation.
- Require Python 3.9 or newer and modernize package metadata. This compatibility change is why the release is 0.5.0 rather than a patch.

### Removed
- Remove captured `debug_page_source.html` from the tracked source tree.

## [0.4.0] - 2026-01-10

### Added
- **Modular Architecture**: Refactored monolithic class into a Strategy Pattern (`strategies/` package).
- `HumanInputStrategy` with variable click/typing timing and corrected typos. The original Bezier claim was inaccurate and is corrected in 0.5.0.
- Experimental `CanvasPoisoningStrategy` and `AudioContextNoiseStrategy`; stable fingerprinting was not proven and these become opt-in in 0.5.0.
- `stealth_showcase.py` example to demonstrate new capabilities.

### Changed
- Refactored `sb_stealth_wrapper` into a package.
- `StealthBot` now accepts `input_strategy` and `evasion_strategy` arguments.

## [0.3.0] - 2025-12-25

### Added
- Modern `pyproject.toml` packaging (PEP 517/518 compliant)
- Type hints throughout the codebase
- Logging support via Python's `logging` module (replaces print statements)
- Custom exceptions: `StealthBotError` and `ChallengeNotSolvedError`
- `py.typed` marker for PEP 561 typed package support
- Class constants for configuration (`DEFAULT_TIMEOUT`, `MAX_CHALLENGE_RETRIES`, `CHALLENGE_INDICATORS`)
- Optional dev dependencies (`pytest`, `black`, `isort`, `mypy`)
- Comprehensive test suite with pytest
- `__version__` and `__author__` module attributes

### Changed
- Migrated from legacy `setup.py` to `pyproject.toml`
- Updated Python version requirement to `>=3.8`
- Improved docstrings with usage examples
- Refactored click fallback logic into `_fallback_click()` method
- Updated author homepage to [www.dhirajdas.dev](https://www.dhirajdas.dev)

### Removed
- Removed legacy `setup.py` file

## [0.2.0] - 2025-12-24

### Added
- Initial public release
- `StealthBot` class with context manager support
- `safe_get()` method for navigating with challenge detection
- `smart_click()` method with human-like interactions
- Automatic Xvfb configuration for Linux/CI environments
- Cloudflare Turnstile challenge detection and solving
- Screenshot saving functionality
- Benchmark comparison script

## [0.1.0] - 2025-12-23

### Added
- Initial development version
- Basic SeleniumBase UC Mode wrapper
