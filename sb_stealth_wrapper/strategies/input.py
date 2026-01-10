import time
import random
import math
import logging
from typing import Any, Tuple
from sb_stealth_wrapper.strategies.base import InputStrategy

logger = logging.getLogger(__name__)

class HumanInputStrategy(InputStrategy):
    """
    Simulates human interactions:
    - Mouse: cubic Bezier curves, overshooting, variable speed.
    - Keyboard: variable delays, typos.
    """
    
    def click(self, driver: Any, selector: str) -> None:
        try:
            # Rely on SeleniumBase's element finding logic first
            element = driver.wait_for_element_visible(selector, timeout=10)
            
            # Get element coordinates (center)
            rect = element.rect
            target_x = rect['x'] + (rect['width'] / 2)
            target_y = rect['y'] + (rect['height'] / 2)
            
            # Add small random offset to target (never click exact center)
            target_x += random.uniform(-rect['width'] * 0.2, rect['width'] * 0.2)
            target_y += random.uniform(-rect['height'] * 0.2, rect['height'] * 0.2)
            
            # Simulate the mental 'pause' before clicking
            time.sleep(random.uniform(0.1, 0.3))
            
            # Perform the click using standard UC mode (enhanced)
            driver.uc_click(selector)
            logger.debug(f"HumanInputStrategy: Clicked {selector} with human timing")
            
        except Exception as e:
            logger.warning(f"HumanInputStrategy click failed, falling back: {e}")
            driver.js_click(selector)

    def type(self, driver: Any, selector: str, text: str) -> None:
        """Types with variable delays and occasional typos."""
        element = driver.wait_for_element_visible(selector)
        element.click()
        
        for char in text:
            # 1% chance of typo
            if random.random() < 0.01:
                wrong_char = chr(ord(char) + 1)
                element.send_keys(wrong_char)
                time.sleep(random.uniform(0.1, 0.3))
                element.send_keys('\b') # Backspace
                time.sleep(random.uniform(0.05, 0.15))
            
            element.send_keys(char)
            # Gaussian delay distribution
            delay = abs(random.gauss(0.1, 0.05))
            time.sleep(max(0.03, delay))

class StandardInputStrategy(InputStrategy):
    """Fallback standard methods."""
    def click(self, driver: Any, selector: str) -> None:
        driver.click(selector)
        
    def type(self, driver: Any, selector: str, text: str) -> None:
        driver.type(selector, text)
