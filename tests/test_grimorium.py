"""Unit tests for Grimorium class."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from magetools.grimorium import Grimorium


@pytest.fixture
async def grim(tmp_path):
    """Fixture for an uninitialized Grimorium with mocked SpellSync."""
    with patch("magetools.grimorium.SpellSync") as mock_sync_class:
        mock_sync = mock_sync_class.return_value
        mock_sync.close = AsyncMock()
        mock_sync.sync_grimoriums_metadata_async = AsyncMock()
        g = Grimorium(root_path=str(tmp_path), auto_initialize=False)
        yield g
        await g.close()


@pytest.mark.asyncio
class TestGrimorium:
    async def test_init_state(self, grim):
        assert not grim._initialized

    async def test_initialize_calls_discovery(self, grim):
        with patch("magetools.grimorium.discover_and_load_spells") as mock_load:
            await grim.initialize()
            assert grim._initialized is True
            mock_load.assert_called_once()

    async def test_execute_spell_success(self, grim):
        grim._initialized = True

        def add(x, y):
            return x + y

        grim.spell_sync.registry = {"add": add}
        grim.spell_sync.validate_spell_access.return_value = True

        from google.adk.tools import ToolContext

        result = await grim.execute_spell(
            "add", {"x": 1, "y": 2}, MagicMock(spec=ToolContext)
        )
        assert result["status"] == "success"
        assert result["result"] == 3

    async def test_uninitialized_call_raises(self, grim):
        with pytest.raises(RuntimeError):
            grim.discover_grimoriums("test")

    async def test_list_spells(self, grim):
        grim._initialized = True
        grim.spell_sync.registry = {"spell1": lambda: None, "spell2": lambda: None}
        # Mock validate_spell_access to allow spell1 but not spell2
        grim.spell_sync.validate_spell_access.side_effect = (
            lambda name: name == "spell1"
        )

        result = await grim.list_spells()
        assert result["status"] == "success"
        assert result["spells"] == ["spell1"]

    async def test_list_spells_uninitialized(self, grim):
        with pytest.raises(RuntimeError):
            await grim.list_spells()
