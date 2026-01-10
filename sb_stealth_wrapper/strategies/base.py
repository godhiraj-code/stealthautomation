from abc import ABC, abstractmethod
from typing import Any, Optional

class DriverStrategy(ABC):
    """Abstract base for driver initialization strategies."""
    
    @abstractmethod
    def initialize(self, headless: bool = False, proxy: Optional[str] = None) -> Any:
        """Initialize and return the driver instance."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up driver resources."""
        pass

class InputStrategy(ABC):
    """Abstract base for human-like input simulation."""
    
    @abstractmethod
    def click(self, driver: Any, selector: str) -> None:
        """Perform a human-like click on the element."""
        pass
        
    @abstractmethod
    def type(self, driver: Any, selector: str, text: str) -> None:
        """Type text with human-like timing."""
        pass

class EvasionStrategy(ABC):
    """Abstract base for active fingerprint evasion."""
    
    @abstractmethod
    def apply(self, driver: Any) -> None:
        """Apply evasion techniques (JS injection, header modification) to the driver."""
        pass
