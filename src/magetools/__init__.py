from .adapters import MockEmbeddingProvider, get_default_provider
from .config import MageToolsConfig, get_config
from .grimorium import Grimorium
from .spell_registry import register_spell
from .spellsync import SpellSync

# Alias for nicer decorator usage
spell = register_spell

__version__ = "1.3.0"
__all__ = [
    "Grimorium",
    "SpellSync",
    "register_spell",
    "spell",
    "MageToolsConfig",
    "get_config",
    "MockEmbeddingProvider",
    "get_default_provider",
]
