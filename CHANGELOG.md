# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
