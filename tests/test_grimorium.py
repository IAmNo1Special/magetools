"""Unit tests for Grimorium class."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest

from magetools.grimorium import Grimorium, ToolContext


@pytest.fixture
async def grim(tmp_path):
    """Fixture for an uninitialized Grimorium with mocked SpellSync."""
    with patch("magetools.grimorium.SpellSync") as mock_sync_class:
        mock_sync = mock_sync_class.return_value
        mock_sync.close = AsyncMock()
        mock_sync.sync_grimoriums_metadata_async = AsyncMock()
        mock_sync.registry = {}
        mock_sync.allowed_collections = None
        mock_sync.embedding_function = MagicMock()
        mock_sync.vector_store = MagicMock()
        mock_sync.MAGETOOLS_ROOT = tmp_path / ".magetools"

        g = Grimorium(root_path=str(tmp_path), auto_initialize=False)
        yield g
        await g.close()


class TestGrimorium:
    @pytest.mark.asyncio
    async def test_init_state(self, grim):
        assert not grim._initialized

    @pytest.mark.asyncio
    async def test_initialize_calls_discovery(self, grim):
        with patch("magetools.grimorium.discover_and_load_spells") as mock_load:
            await grim.initialize()
            assert grim._initialized is True
            mock_load.assert_called_once()

    @pytest.mark.asyncio
    async def test_uninitialized_calls_raise(self, grim):
        """Verify all methods raise RuntimeError when uninitialized."""
        with pytest.raises(RuntimeError, match="not initialized"):
            await grim.list_spells()
        with pytest.raises(RuntimeError, match="not initialized"):
            await grim.execute_spell("test", {}, MagicMock())
        with pytest.raises(RuntimeError, match="not initialized"):
            grim.discover_grimoriums("query")
        with pytest.raises(RuntimeError, match="not initialized"):
            grim.discover_spells("coll_id", "query")

    @pytest.mark.asyncio
    async def test_execute_spell_success(self, grim):
        grim._initialized = True

        def add(x, y):
            return x + y

        grim.spell_sync.registry = {"add": add}
        grim.spell_sync.validate_spell_access.return_value = True

        result = await grim.execute_spell("add", {"x": 1, "y": 2}, MagicMock())
        assert result["status"] == "success"
        assert result["result"] == 3

    @pytest.mark.asyncio
    async def test_execute_async_spell_success(self, grim):
        grim._initialized = True

        async def add_async(x, y):
            return x + y

        grim.spell_sync.registry = {"add": add_async}
        grim.spell_sync.validate_spell_access.return_value = True

        result = await grim.execute_spell("add", {"x": 10, "y": 20}, MagicMock())
        assert result["status"] == "success"
        assert result["result"] == 30

    @pytest.mark.asyncio
    async def test_execute_spell_permission_denied(self, grim):
        grim._initialized = True
        grim.spell_sync.validate_spell_access.return_value = False
        result = await grim.execute_spell("any", {}, MagicMock())
        assert result["status"] == "error"
        assert "Permission denied" in result["message"]

    @pytest.mark.asyncio
    async def test_execute_spell_not_found(self, grim):
        grim._initialized = True
        grim.spell_sync.validate_spell_access.return_value = True
        grim.spell_sync.registry = {}
        result = await grim.execute_spell("missing", {}, MagicMock())
        assert result["status"] == "error"
        assert "not found" in result["message"]

    @pytest.mark.asyncio
    async def test_execute_spell_runtime_error(self, grim):
        grim._initialized = True

        def fail():
            raise ValueError("fail")

        grim.spell_sync.registry = {"fail": fail}
        grim.spell_sync.validate_spell_access.return_value = True
        result = await grim.execute_spell("fail", {}, MagicMock())
        assert result["status"] == "error"
        assert "Execution failed" in result["message"]

    @pytest.mark.asyncio
    async def test_execute_spell_argument_mismatch(self, grim):
        grim._initialized = True

        def take_x(x):
            return x

        grim.spell_sync.registry = {"take_x": take_x}
        grim.spell_sync.validate_spell_access.return_value = True
        # Calling with wrong args to trigger TypeError in thread
        result = await grim.execute_spell("take_x", {"wrong": 1}, MagicMock())
        assert result["status"] == "error"
        assert "check arguments" in result["message"]

    @pytest.mark.asyncio
    async def test_execute_spell_with_context_injection(self, grim):
        grim._initialized = True

        def context_aware(tool_context: ToolContext):
            return tool_context.user_id

        grim.spell_sync.registry = {"ctx": context_aware}
        grim.spell_sync.validate_spell_access.return_value = True

        mock_ctx = MagicMock(spec=ToolContext)
        mock_ctx.user_id = "merlin"

        result = await grim.execute_spell("ctx", {}, tool_context=mock_ctx)
        assert result["status"] == "success"
        assert result["result"] == "merlin"

    @pytest.mark.asyncio
    async def test_list_spells_filtered(self, grim):
        grim._initialized = True
        grim.spell_sync.registry = {"spell1": lambda: 1, "spell2": lambda: 2}
        grim.spell_sync.allowed_collections = ["coll1"]

        mock_coll = MagicMock()
        mock_coll.get.return_value = {"ids": ["spell1"]}
        grim.spell_sync.vector_store.get_collection.return_value = mock_coll

        result = await grim.list_spells()
        assert result["spells"] == ["spell1"]

    @pytest.mark.asyncio
    async def test_list_spells_error_handling(self, grim):
        grim._initialized = True
        grim.spell_sync.registry = {"spell1": lambda: 1}
        grim.spell_sync.allowed_collections = ["coll1"]
        grim.spell_sync.vector_store.get_collection.side_effect = Exception("db fail")

        result = await grim.list_spells()
        assert result["spells"] == []  # Graceful degradation

    @pytest.mark.asyncio
    async def test_get_tools(self, grim):
        tools = await grim.get_tools()
        assert len(tools) == 4
        from google.adk.tools import BaseTool

        assert all(isinstance(t, BaseTool) for t in tools)

    def test_adk_lifecycle_stubs(self):
        g = Grimorium()
        assert g.get_auth_config() is None
        with patch("magetools.grimorium.Grimorium.__init__", return_value=None):
            instance = Grimorium.from_config(MagicMock(), "path")
            assert isinstance(instance, Grimorium)

    def test_discovery_proxies(self, grim):
        grim._initialized = True
        # Mock what find_relevant_grimoriums returns (list of dicts)
        grim.spell_sync.find_relevant_grimoriums = MagicMock(
            return_value=[{"grimorium_id": "coll1", "description": "desc1"}]
        )
        # Mock what find_spells_within_grimorium returns (list of IDs)
        grim.spell_sync.find_spells_within_grimorium = MagicMock(
            return_value=["spell1"]
        )
        grim.spell_sync.registry = {"spell1": lambda: 1}

        res1 = grim.discover_grimoriums("q")
        assert res1["grimoriums"][0]["id"] == "coll1"

        res2 = grim.discover_spells("coll1", "q")
        assert "spell1" in res2["spells"]

    def test_discover_grimoriums_not_found(self, grim):
        grim._initialized = True
        grim.spell_sync.find_relevant_grimoriums = MagicMock(return_value=[])
        res = grim.discover_grimoriums("q")
        assert res["status"] == "not_found"

    def test_discover_spells_not_found(self, grim):
        grim._initialized = True
        grim.spell_sync.find_spells_within_grimorium = MagicMock(return_value=[])
        res = grim.discover_spells("coll1", "q")
        assert res["status"] == "not_found"

    def test_discover_spells_parsing_error(self, grim):
        grim._initialized = True
        grim.spell_sync.find_spells_within_grimorium = MagicMock(return_value=["bad"])
        # Mock registry access to fail
        type(grim.spell_sync).registry = PropertyMock(
            side_effect=Exception("parse fail")
        )
        res = grim.discover_spells("coll1", "q")
        assert res["spells"] == {}

    @pytest.mark.asyncio
    async def test_list_spells_no_filtering(self, grim):
        grim._initialized = True
        grim.spell_sync.registry = {"s1": lambda: 1}
        grim.spell_sync.allowed_collections = None
        res = await grim.list_spells()
        assert "s1" in res["spells"]

    def test_usage_guide(self, grim):
        assert "USAGE GUIDE" in grim.usage_guide.upper()

    def test_registry_property(self, grim):
        grim.spell_sync.registry = {"key": "val"}
        assert grim.registry == {"key": "val"}

    def test_sync_initialize_already_init(self, grim):
        grim._initialized = True
        grim._sync_initialize()  # Should return immediately

    @pytest.mark.asyncio
    async def test_initialize_already_init(self, grim):
        grim._initialized = True
        await grim.initialize()  # Hits line 161 return

    def test_auto_detect_path_fail(self):
        with (
            patch("inspect.stack", side_effect=Exception("stack error")),
            patch("magetools.grimorium.get_config") as mock_get_config,
            patch("magetools.grimorium.SpellSync"),  # PREVENT CHROMADB INIT
        ):
            mock_config = MagicMock()
            mock_config.root_path = None  # Trigger line 86
            mock_get_config.return_value = mock_config
            with patch("pathlib.Path.cwd", return_value=Path("/fake/cwd")):
                g = Grimorium(auto_initialize=False)
                assert g.config.root_path == Path("/fake/cwd")

    def test_auto_init_error(self):
        with patch(
            "magetools.grimorium.Grimorium._sync_initialize",
            side_effect=Exception("init error"),
        ):
            g = Grimorium(auto_initialize=True)
            assert not g._initialized
