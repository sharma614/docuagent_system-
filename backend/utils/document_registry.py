import json
import os
from datetime import datetime, timezone
from pathlib import Path

# Registry lives alongside main.py so it survives restarts
_REGISTRY_PATH = Path(__file__).parent.parent / "document_registry.json"


def _load() -> dict:
    if _REGISTRY_PATH.exists():
        try:
            return json.loads(_REGISTRY_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save(data: dict) -> None:
    _REGISTRY_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def register_document(doc_id: str, doc_name: str, chunk_count: int) -> dict:
    """Add or update a document entry."""
    data = _load()
    entry = {
        "doc_id": doc_id,
        "doc_name": doc_name,
        "chunk_count": chunk_count,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }
    data[doc_id] = entry
    _save(data)
    return entry


def list_documents() -> list:
    """Return all registered documents sorted newest-first."""
    data = _load()
    return sorted(data.values(), key=lambda d: d.get("uploaded_at", ""), reverse=True)


def get_document(doc_id: str) -> dict | None:
    return _load().get(doc_id)


def delete_document(doc_id: str) -> bool:
    """Remove a document from the registry. Returns True if it existed."""
    data = _load()
    if doc_id in data:
        del data[doc_id]
        _save(data)
        return True
    return False
