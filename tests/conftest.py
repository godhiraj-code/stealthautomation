"""
Pytest configuration and fixtures for SB Stealth Wrapper tests.
"""

import pytest


@pytest.fixture
def mock_page_source_with_challenge() -> str:
    """Return page source containing challenge indicators."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Checking your browser</title></head>
    <body>
        <div class="cf-turnstile">
            <p>Just a moment...</p>
            <p>Verify you are human</p>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def mock_page_source_clean() -> str:
    """Return clean page source without challenge indicators."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Welcome</title></head>
    <body>
        <h1>Welcome to the Dashboard</h1>
        <p>You have successfully logged in.</p>
    </body>
    </html>
    """
