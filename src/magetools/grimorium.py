"""Core Grimorium toolset for managing magical spells and their discovery."""

from __future__ import annotations

import asyncio
import inspect
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools import BaseTool, FunctionTool, ToolContext
from google.adk.tools.base_toolset import BaseToolset

if TYPE_CHECKING:
    from google.adk.tools.tool_configs import ToolArgsConfig

from .config import MageToolsConfig, get_config
from .prompts import grimorium_usage_guide
from .spellsync import SpellSync, discover_and_load_spells

logger = logging.getLogger(__name__)


class Grimorium(BaseToolset):
    """A magical grimoire toolset for discovering and managing spells.

    This toolset provides three main tools:
    1. magetools_discover_grimoriums: To find relevant collections (Grimoriums).
    2. magetools_discover_spells: To find spells within a Grimorium.
    3. magetools_execute_spell: To run a specific spell.

    Usage:
        grimorium = Grimorium(root_path="/path/to/project")
        await grimorium.initialize()  # Required before use
    """

    def __init__(
        self,
        root_path: str | None = None,
        allowed_collections: list[str] | None = None,
        embedding_provider: Any = None,
        vector_store: Any = None,
        config: MageToolsConfig | None = None,
        strict_mode: bool = True,
        auto_initialize: bool = True,
    ):
        """Initialize the Grimorium toolset.

        Args:
            root_path: Optional path string to the project root.
            allowed_collections: Optional list of collection names.
            embedding_provider: Optional EmbeddingProviderProtocol implementation.
            vector_store: Optional VectorStoreProtocol implementation.
            config: Optional MageToolsConfig object.
            strict_mode: If True, only load spells from folders with manifest.json.
            auto_initialize: If True (default), run sync initialization in constructor
                           for backwards compatibility. Set to False for async usage.
        """
        # Initialize the base toolset with a prefix to avoid naming collisions
        super().__init__(tool_name_prefix="magetools")

        self.config = config or get_config(
            root_path=Path(root_path) if root_path else None
        )
        path_obj = self.config.root_path

        # If root_path specifically provided, we trust it over auto-detection
        # but if neither provided, we use the auto-detection from previous version as fallback for compatibility
        if not root_path and not config:
            # Magic: Auto-detect the caller's frame to find where Grimorium is instantiated
            try:
                # Stack[0] is here, Stack[1] is the caller
                frame = inspect.stack()[1]
                caller_file = frame.filename
                if caller_file:
                    path_obj = Path(caller_file).parent.resolve()
                    logger.debug(
                        f"Auto-detected Grimorium root from caller: {path_obj}"
                    )
            except Exception as e:
                logger.warning(f"Could not auto-detect caller path: {e}")

            # Fallback to CWD if magic failed and no path provided
            if not path_obj:
                path_obj = Path.cwd()

            # Update config with the auto-detected path
            self.config.root_path = path_obj

        self.spell_sync = SpellSync(
            root_path=self.config.root_path,
            allowed_collections=allowed_collections,
            embedding_provider=embedding_provider,
            vector_store=vector_store,
            config=self.config,
        )

        self._strict_mode = strict_mode
        self._initialized = False
        self._allowed_collections = allowed_collections
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store

        # Create the tools that will be exposed to the agent
        self._discover_grimoriums_tool = FunctionTool(func=self.discover_grimoriums)
        self._discover_spells_tool = FunctionTool(func=self.discover_spells)
        self._execute_spell_tool = FunctionTool(func=self.execute_spell)

        # Auto-initialize for backwards compatibility
        if auto_initialize:
            try:
                self._sync_initialize()
            except Exception as e:
                logger.error(f"AUTO-INIT FAILED: {e}")
                logger.warning(
                    "Grimorium is in an uninitialized state. "
                    "Call 'await grimorium.initialize()' manually or check your configuration."
                )
                # Don't re-raise - allow object to exist in degraded state

        logger.debug("Grimorium constructor completed.")

    def _sync_initialize(self) -> None:
        """Synchronous initialization (for backwards compatibility)."""
        if self._initialized:
            return

        logger.debug(
            f"Initializing Grimorium with root: {self.spell_sync.MAGETOOLS_ROOT}"
        )
        discover_and_load_spells(
            self.spell_sync.MAGETOOLS_ROOT,
            registry=self.spell_sync.registry,
            strict_mode=self._strict_mode,
        )
        self.spell_sync.sync_spells()
        self._initialized = True
        logger.debug("Grimorium initialized successfully (sync).")

    @property
    def registry(self) -> dict[str, Any]:
        """Get the registry of discovered spells."""
        return self.spell_sync.registry

    async def initialize(self) -> None:
        """Async initialization for non-blocking setup.

        Call this after construction when using auto_initialize=False:

            grimorium = Grimorium(auto_initialize=False)
            await grimorium.initialize()

        This method handles:
        - Spell discovery from filesystem
        - Database synchronization
        - LLM-generated metadata (async)
        """
        if self._initialized:
            return

        logger.debug(
            f"Initializing Grimorium (async) with root: {self.spell_sync.MAGETOOLS_ROOT}"
        )
        discover_and_load_spells(
            self.spell_sync.MAGETOOLS_ROOT,
            registry=self.spell_sync.registry,
            strict_mode=self._strict_mode,
        )
        self.spell_sync.sync_spells()
        await self.spell_sync.sync_grimoriums_metadata_async()
        self._initialized = True
        logger.debug("Grimorium initialized successfully (async).")

    def _check_initialized(self) -> None:
        """Raise error if not initialized."""
        if not self._initialized:
            raise RuntimeError(
                "Grimorium not initialized. Call 'await grimorium.initialize()' first, "
                "or use auto_initialize=True (default) in constructor."
            )

    @property
    def usage_guide(self) -> str:
        """Returns the usage guide instructions for using this toolset."""
        return grimorium_usage_guide

    def discover_grimoriums(self, query: str) -> dict[str, Any]:
        """Find relevant Grimoriums (Collections) based on a high-level goal.

        Args:
            query: High-level description of what you want to achieve.
                   Example: "process data", "manage files", "handle audio"
        """
        self._check_initialized()
        results = self.spell_sync.find_relevant_grimoriums(query)
        if not results:
            return {"status": "not_found", "message": "No relevant Grimoriums found."}

        # Simplify output for the agent
        simple_results = []
        for r in results:
            simple_results.append(
                {
                    "id": r["grimorium_id"],
                    "description": r["description"][:200] + "...",  # Truncate
                }
            )

        return {
            "status": "success",
            "grimoriums": simple_results,
            "next_step": "Use 'magetools_discover_spells(grimorium_id, query)' to find specific tools.",
        }

    def discover_spells(self, grimorium_id: str, query: str) -> dict[str, Any]:
        """Find specific spells (tools) within a selected Grimorium.

        Args:
            grimorium_id: The ID of the Grimorium to search (found via discover_grimoriums).
            query: Specific action you want to perform.
        """
        self._check_initialized()
        spell_ids = self.spell_sync.find_spells_within_grimorium(grimorium_id, query)

        if not spell_ids:
            return {
                "status": "not_found",
                "message": f"No spells found in '{grimorium_id}' matching '{query}'.",
            }

        detailed_spells = {}
        for name in spell_ids:
            try:
                func = self.spell_sync.registry[name]
                sig = str(inspect.signature(func))
                doc = inspect.getdoc(func) or "No description."
                detailed_spells[name] = {"signature": sig, "description": doc}
            except Exception:
                continue

        return {
            "status": "success",
            "grimorium": grimorium_id,
            "spells": detailed_spells,
        }

    async def execute_spell(
        self, spell_name: str, arguments: dict[str, Any], tool_context: ToolContext
    ) -> dict[str, Any]:
        """Execute a specific spell by name.
        Args:
            spell_name: The exact name of the spell to find and execute.
            arguments: A dictionary of arguments to pass to the spell function.
        Returns:
            The result of the spell execution.
        """
        self._check_initialized()
        logger.info(
            f"Grimorium executing spell: {spell_name} with args: {arguments}..."
        )

        try:
            # SECURITY CHECK: Verify spell is allowed for this instance
            if not self.spell_sync.validate_spell_access(spell_name):
                return {
                    "status": "error",
                    "message": f"Permission denied: Spell '{spell_name}' is not in your allowed collections.",
                }

            spell_func = self.spell_sync.registry[spell_name]
        except KeyError:
            return {
                "status": "error",
                "message": f"Spell '{spell_name}' not found. Did you search for it first?",
            }
        try:
            # Check if the target spell function expects 'tool_context'
            sig = inspect.signature(spell_func)

            # Use a copy to avoid mutating the original arguments
            call_args = arguments.copy()

            # Robust injection of context by Type and Name
            for name, param in sig.parameters.items():
                if (
                    param.annotation == ToolContext
                    or name == "tool_context"
                    and name not in call_args
                ):
                    call_args[name] = tool_context

            # Execute the spell with the prepared arguments
            if inspect.iscoroutinefunction(spell_func):
                result = await spell_func(**call_args)
            else:
                # Run sync functions in a separate thread to keep the loop alive
                result = await asyncio.to_thread(spell_func, **call_args)

            return {"status": "success", "result": result}

        except TypeError as te:
            logger.error(f"Argument mismatch for spell {spell_name}: {te}")
            return {
                "status": "error",
                "message": f"Failed to call spell. Please check arguments. details: {str(te)}",
            }
        except Exception as e:
            # Catch Exception to protect the agent from misbehaving tools
            logger.error(
                f"Critical error executing spell {spell_name}: {type(e).__name__}: {e}"
            )
            return {
                "status": "error",
                "message": f"Execution failed: {type(e).__name__}: {str(e)}",
            }

    async def get_tools(
        self, readonly_context: ReadonlyContext | None = None
    ) -> list[BaseTool]:
        """Return the list of tools provided by this toolset."""
        return [
            self._discover_grimoriums_tool,
            self._discover_spells_tool,
            self._execute_spell_tool,
        ]

    @classmethod
    def from_config(cls, config: ToolArgsConfig, config_abs_path: str) -> "Grimorium":
        """Creates a toolset instance from a config.

        This method is required for full ADK integration when loading toolsets
        declaratively via YAML.
        """
        # For now, we return a default instance using MageTools individual discovery logic.
        # Future enhancement: Map config values to SpellSync root paths.
        return cls()

    def get_auth_config(self) -> Any:
        """Standard ADK Hook for providing tool authentication.

        Returning None as Magetools handles credentials via .env or explicitly
        configured providers.
        """
        return None

    async def close(self) -> None:
        """Cleanup resources."""
        logger.info("Closing Grimorium toolset...")
        await self.spell_sync.close()
        await super().close()
