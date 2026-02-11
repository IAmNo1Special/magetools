"""Ultimate final 100% coverage unit tests for SpellSync module."""

import hashlib
import logging
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from magetools.config import MageToolsConfig
from magetools.constants import COLLECTION_ATTR_NAME
from magetools.spellsync import (
    SpellSync,
    _is_spell_allowed,
    _load_manifest,
    discover_and_load_spells,
)


@pytest.fixture
def mock_config(tmp_path):
    config = MagicMock(spec=MageToolsConfig)
    config.root_path = tmp_path
    config.magetools_root = tmp_path / ".magetools"
    config.db_path = tmp_path / ".chroma_db"
    config.magetools_dir_name = ".magetools"
    config.db_folder_name = ".chroma_db"
    config.debug = True
    config.magetools_root.mkdir(parents=True, exist_ok=True)
    return config


class TestSpellSyncCore:
    def test_init_defaults(self, tmp_path):
        with (
            patch("magetools.spellsync.get_config") as mock_get_config,
            patch("magetools.spellsync.ChromaVectorStore"),
            patch("magetools.adapters.get_default_provider") as mock_gp,
        ):
            config = MagicMock()
            config.magetools_root = tmp_path
            config.db_path = tmp_path / "db"
            mock_get_config.return_value = config
            mock_gp.return_value.get_embedding_function.return_value = MagicMock()
            sync = SpellSync()
            assert sync.config == config

    def test_init_root_missing(self, tmp_path):
        config = MagicMock(spec=MageToolsConfig)
        config.root_path = tmp_path
        config.magetools_root = tmp_path / "ghost"
        config.db_path = tmp_path / "db"
        with (
            patch("magetools.spellsync.ChromaVectorStore"),
            patch("magetools.adapters.get_default_provider") as gp,
        ):
            gp.return_value.get_embedding_function.return_value = MagicMock()
            sync = SpellSync(config=config)
            assert not sync.MAGETOOLS_ROOT.exists()

    def test_pickling(self, mock_config):
        sync = SpellSync(
            config=mock_config, embedding_provider=MagicMock(), vector_store=MagicMock()
        )
        sync.client = MagicMock()
        sync.embedding_function = MagicMock()
        state = sync.__getstate__()
        assert "client" not in state
        new_sync = SpellSync.__new__(SpellSync)
        state["MAGETOOLS_ROOT"] = mock_config.magetools_root
        state["DB_FOLDER_NAME"] = ".chroma_db"
        with patch("magetools.spellsync.chromadb.PersistentClient"):
            new_sync.__setstate__(state)
            assert hasattr(new_sync, "client")

    @pytest.mark.asyncio
    async def test_close(self, mock_config):
        sync = SpellSync(
            vector_store=MagicMock(), embedding_provider=MagicMock(), config=mock_config
        )
        sync.vector_store.close = AsyncMock()
        sync.embedding_provider.close = AsyncMock()
        await sync.close()
        mock_min = MagicMock()
        mock_min.get_embedding_function.return_value = MagicMock()
        del mock_min.close
        sync2 = SpellSync(
            vector_store=object(), embedding_provider=mock_min, config=mock_config
        )
        await sync2.close()


class TestSpellSyncDiscovery:
    def test_find_matching_spells(self, mock_config):
        mock_vs = MagicMock()
        sync = SpellSync(vector_store=mock_vs, config=mock_config)
        assert sync.find_matching_spells(None) == []
        mock_vs.list_collections.side_effect = Exception()
        assert sync.find_matching_spells("q") == []
        mock_vs.list_collections.side_effect = None
        c1 = MagicMock()
        c1.name = "c1"
        mock_vs.list_collections.return_value = [c1]
        mock_vs.get_collection.return_value = c1
        c1.query.return_value = {"ids": [["s1", "s2"]], "distances": [[0.1, 0.5]]}
        sync.distance_threshold = 0.4
        assert sync.find_matching_spells("q") == ["s1"]
        c1.query.return_value = {"ids": [["s1", "s1"]], "distances": [[0.1, 0.05]]}
        assert sync.find_matching_spells("q") == ["s1"]
        sync.allowed_collections = ["other"]
        assert sync.find_matching_spells("q") == []
        sync.allowed_collections = None
        c1.query.side_effect = Exception()
        assert sync.find_matching_spells("q") == []

    def test_find_relevant_grimoriums(self, mock_config):
        mock_vs = MagicMock()
        master = MagicMock()
        mock_vs.get_or_create_collection.return_value = master
        sync = SpellSync(vector_store=mock_vs, config=mock_config)
        assert sync.find_relevant_grimoriums("") == []
        master.query.return_value = {
            "ids": [["g1", "g2"]],
            "distances": [[0.1, 0.2]],
            "documents": [["d1", "d2"]],
            "metadatas": [[{}, {}]],
        }
        assert len(sync.find_relevant_grimoriums("q")) == 2
        master.query.side_effect = Exception()
        assert sync.find_relevant_grimoriums("q") == []

    def test_find_spells_within_grimorium(self, mock_config):
        mock_vs = MagicMock()
        coll = MagicMock()
        mock_vs.get_collection.return_value = coll
        sync = SpellSync(vector_store=mock_vs, config=mock_config)
        sync.allowed_collections = ["only"]
        assert sync.find_spells_within_grimorium("other", "q") == []
        sync.allowed_collections = ["g1"]
        coll.query.return_value = {"ids": [["s1"]], "distances": [[0.1]]}
        assert len(sync.find_spells_within_grimorium("g1", "q")) == 1
        mock_vs.get_collection.side_effect = Exception()
        assert sync.find_spells_within_grimorium("g1", "q") == []

    def test_validate_spell_access(self, mock_config):
        sync = SpellSync(config=mock_config)
        assert sync.validate_spell_access("s") is True
        mock_vs = MagicMock()
        sync.vector_store = mock_vs
        sync.allowed_collections = ["c"]
        coll = MagicMock()
        mock_vs.get_collection.return_value = coll
        coll.get.return_value = {"ids": ["s"]}
        assert sync.validate_spell_access("s") is True
        coll.get.side_effect = Exception()
        assert sync.validate_spell_access("s") is False
        sync.allowed_collections = MagicMock()
        sync.allowed_collections.__iter__.side_effect = Exception("Iter fail")
        assert sync.validate_spell_access("s") is False


class TestSpellSyncSynchronization:
    def test_sync_grimoriums_metadata_mega(self, tmp_path, mock_config):
        mock_vs = MagicMock()
        master = MagicMock()
        mock_vs.get_or_create_collection.return_value = master
        sync = SpellSync(
            vector_store=mock_vs, config=mock_config, embedding_provider=MagicMock()
        )
        sync.MAGETOOLS_ROOT = tmp_path
        d = tmp_path / "c"
        d.mkdir()
        # Fallback 352: Triggered by empty spell_docs
        (d / "s.py").write_text("def f():pass")  # NO DOCSTRING
        master.get.return_value = {"metadatas": []}
        sync.sync_grimoriums_metadata()
        # Up-to-date (326)
        (d / "s.py").write_text('"""doc"""')
        h = sync._compute_grimorium_hash(d)
        master.get.return_value = {"metadatas": [{"hash": h}]}
        (d / "grimorium_summary.md").write_text("Sum")
        sync.sync_grimoriums_metadata()
        # Stale + Re-generation (331) + Write error 348-349
        master.get.return_value = {"metadatas": [{"hash": "stale"}]}
        with (
            patch.object(
                sync.embedding_provider, "generate_content", return_value="ASum"
            ),
            patch.object(Path, "write_text", side_effect=IOError()),
        ):
            sync.sync_grimoriums_metadata()

    @pytest.mark.asyncio
    async def test_sync_grimoriums_metadata_async_mega(self, tmp_path, mock_config):
        mock_vs = MagicMock()
        master = MagicMock()
        mock_vs.get_or_create_collection.return_value = master
        sync = SpellSync(
            vector_store=mock_vs, config=mock_config, embedding_provider=MagicMock()
        )
        sync.MAGETOOLS_ROOT = tmp_path
        d = tmp_path / "c"
        d.mkdir()
        # Fallback 419: Triggered by empty spell_docs
        (d / "s.py").write_text("def f():pass")  # NO DOCSTRING
        master.get.return_value = {"metadatas": []}
        await sync.sync_grimoriums_metadata_async()
        # Up-to-date (402)
        (d / "s.py").write_text('"""doc"""')
        h = sync._compute_grimorium_hash(d)
        master.get.return_value = {"metadatas": [{"hash": h}]}
        (d / "grimorium_summary.md").write_text("Sum")
        await sync.sync_grimoriums_metadata_async()
        # Stale + Re-generation (405) + Write error 413-414
        master.get.return_value = {"metadatas": [{"hash": "stale"}]}
        with (
            patch.object(
                sync.embedding_provider, "generate_content", return_value="ASum"
            ),
            patch.object(Path, "write_text", side_effect=IOError()),
        ):
            await sync.sync_grimoriums_metadata_async()

    def test_sync_spells(self, mock_config):
        mock_vs = MagicMock()
        coll = MagicMock()
        mock_vs.get_or_create_collection.return_value = coll
        sync = SpellSync(vector_store=mock_vs, config=mock_config)

        def s():
            pass

        setattr(s, COLLECTION_ATTR_NAME, "override")
        s.__module__ = "magetools.discovered_spells.arcane.spell"
        s.__doc__ = "doc"
        sync.registry = {"s": s}
        coll.get.return_value = {"ids": []}
        sync.sync_spells()
        coll.get.side_effect = Exception()
        sync.sync_spells()
        coll.get.side_effect = None
        coll.get.return_value = {
            "ids": ["s"],
            "metadatas": [{"hash": hashlib.md5(b"doc").hexdigest()}],
        }
        sync.sync_spells()
        mock_vs.get_or_create_collection.side_effect = Exception()
        sync.sync_spells()


class TestHelpers:
    def test_is_spell_allowed(self):
        assert _is_spell_allowed("s", None) is True
        assert _is_spell_allowed("s", {"whitelist": ["s"]}) is True
        assert _is_spell_allowed("s", {"whitelist": ["o"]}) is False
        assert _is_spell_allowed("s", {"blacklist": ["s"]}) is False
        assert _is_spell_allowed("s", {"blacklist": ["o"]}) is True
        assert _is_spell_allowed("s", {"whitelist": ["s"], "blacklist": ["s"]}) is False


class TestSpellDiscovery:
    def test_discover_and_load_spells_comprehensive(self, tmp_path, mock_config):
        d = tmp_path / "c"
        d.mkdir()
        (d / "s.py").write_text("def f():pass\nf._grimorium_spell=True\nf.__name__='f'")
        (d / "manifest.json").write_text('{"whitelist": ["f"]}')
        with patch("magetools.spellsync.get_config") as mc:
            mc.return_value.magetools_root = tmp_path
            discover_and_load_spells(root_path=None)
        discover_and_load_spells(root_path=tmp_path / "ghost")
        reg = {}
        logging.getLogger("magetools.spellsync").setLevel(logging.DEBUG)
        discover_and_load_spells(root_path=tmp_path, registry=reg, strict_mode=False)
        (d / "manifest.json").write_text('{"whitelist": ["other"]}')
        discover_and_load_spells(root_path=tmp_path, strict_mode=False)
        d2 = tmp_path / "d2"
        d2.mkdir()
        (d2 / "s.py").touch()
        discover_and_load_spells(root_path=tmp_path, strict_mode=True)
        (d / "manifest.json").write_text('{"enabled": false}')
        discover_and_load_spells(root_path=tmp_path, strict_mode=False)
        sync = SpellSync(config=mock_config)
        (d / ".h.py").touch()
        sync._extract_spell_docs(d)
        (d / "bad.py").write_text("def bad(")
        (d / "manifest.json").write_text('{"enabled": true}')
        discover_and_load_spells(root_path=tmp_path, strict_mode=False)
        with patch(
            "magetools.spellsync.importlib.util.spec_from_file_location",
            side_effect=Exception(),
        ):
            discover_and_load_spells(root_path=tmp_path, strict_mode=False)
        sync.embedding_provider = MagicMock()
        sync.embedding_provider.generate_content.side_effect = Exception()
        sync._generate_grimorium_summary("g", ["d"])
        sync._sanitize_docstring("")
        with patch.object(Path, "read_bytes", side_effect=IOError()):
            sync._compute_grimorium_hash(d)

    def test_load_manifest_mega_error(self, tmp_path):
        d = tmp_path / "m"
        d.mkdir()
        (d / "manifest.json").write_text("{")
        assert _load_manifest(d) is None
        with patch("builtins.open", side_effect=Exception()):
            assert _load_manifest(d) is None
