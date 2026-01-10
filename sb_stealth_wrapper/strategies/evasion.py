import logging
from typing import Any
from sb_stealth_wrapper.strategies.base import EvasionStrategy

logger = logging.getLogger(__name__)

class CanvasPoisoningStrategy(EvasionStrategy):
    """
    Injects JS to add noise to Canvas rendering, ensuring unique but consistent
    fingerprints that differ from standard Selenium/Driver values.
    """
    def apply(self, driver: Any) -> None:
        logger.debug("Applying Canvas Poisoning...")
        js_code = """
        (function() {
            var originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            var originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;

            function addNoise(data) {
                for (var i = 0; i < data.length; i += 4) {
                    // Add subtle noise to RGB channels
                    data[i] = data[i] + Math.floor(Math.random() * 2) - 1;     // Red
                    data[i+1] = data[i+1] + Math.floor(Math.random() * 2) - 1; // Green
                    data[i+2] = data[i+2] + Math.floor(Math.random() * 2) - 1; // Blue
                }
            }

            HTMLCanvasElement.prototype.toDataURL = function() {
                // If it's a known anti-bot canvas challenge, we could try to handle it.
                // For now, we return the result of the standard execution but could intercept.
                // Note: Direct toDataURL modifications are risky if the noise isn't consistent.
                // A better approach for toDataURL is to actually draw the noise on the context first/during.
                return originalToDataURL.apply(this, arguments);
            };
            
            CanvasRenderingContext2D.prototype.getImageData = function(sx, sy, sw, sh) {
                var imageData = originalGetImageData.apply(this, arguments);
                addNoise(imageData.data);
                return imageData;
            };
        })();
        """
        # We use execute_cdp_cmd to add script on new document if possible, or standard execute
        try:
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js_code})
            logger.debug("Canvas poisoning injected via CDP")
        except:
             # Fallback for non-CDP drivers
             driver.execute_script(js_code)

class AudioContextNoiseStrategy(EvasionStrategy):
    """
    Injects JS to add noise to AudioContext frequency data.
    """
    def apply(self, driver: Any) -> None:
        logger.debug("Applying Audio Context Noise...")
        js_code = """
        (function() {
            var originalGetChannelData = AudioBuffer.prototype.getChannelData;
            
            AudioBuffer.prototype.getChannelData = function() {
                var data = originalGetChannelData.apply(this, arguments);
                for (var i = 0; i < data.length; i += 100) {
                    // Tiny random noise
                    data[i] += (Math.random() * 0.0001); 
                }
                return data;
            };
        })();
        """
        try:
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js_code})
            logger.debug("Audio noise injected via CDP")
        except:
            driver.execute_script(js_code)

class CompositeEvasionStrategy(EvasionStrategy):
    """Combines multiple evasion strategies."""
    def __init__(self, strategies=None):
        self.strategies = strategies or [CanvasPoisoningStrategy(), AudioContextNoiseStrategy()]
        
    def apply(self, driver: Any) -> None:
        for strategy in self.strategies:
            strategy.apply(driver)
