from typing import Any, Optional
import os
import platform
import logging
from seleniumbase import SB
from sb_stealth_wrapper.strategies.base import DriverStrategy

logger = logging.getLogger(__name__)

class SeleniumBaseDriver(DriverStrategy):
    """Wrapper for SeleniumBase SB context."""
    
    def __init__(self):
        self._sb_context = None
        self.sb = None
        
    def initialize(self, headless: bool = False, proxy: Optional[str] = None) -> Any:
        is_linux = platform.system() == "Linux"
        xvfb = False
        
        if is_linux:
            # Smart headless handling for Linux
            logger.info("Linux/CI detected: using Xvfb with headed mode.")
            xvfb = True
            headless = False
            
        self._sb_context = SB(
            uc=True,
            headless=headless,
            xvfb=xvfb,
            proxy=proxy,
            test=False,
            rtf=False
        )
        self.sb = self._sb_context.__enter__()
        return self.sb
        
    def cleanup(self) -> None:
        if self._sb_context:
            self._sb_context.__exit__(None, None, None)
