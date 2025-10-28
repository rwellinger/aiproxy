"""
MUREKA API Clients

Modular client architecture for MUREKA API integration.
Provides backward compatibility with existing imports.
"""

# Import all public functions for backward compatibility
from .base_client import MurekaBaseClient
from .generation_client import (
    MurekaGenerationClient,
    check_mureka_status,
    start_mureka_generation,
    wait_for_mureka_completion,
)
from .instrumental_client import (
    MurekaInstrumentalClient,
    check_mureka_instrumental_status,
    start_mureka_instrumental_generation,
    wait_for_mureka_instrumental_completion,
)


# Preserve the original function imports from client.py
__all__ = [
    # Original client.py functions (backward compatibility)
    "start_mureka_generation",
    "check_mureka_status",
    "wait_for_mureka_completion",
    "start_mureka_instrumental_generation",
    "check_mureka_instrumental_status",
    "wait_for_mureka_instrumental_completion",
    # New client classes
    "MurekaBaseClient",
    "MurekaGenerationClient",
    "MurekaInstrumentalClient",
]
