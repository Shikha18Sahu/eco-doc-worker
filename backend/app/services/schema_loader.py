import json
import os
from typing import Optional


SCHEMAS_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")
SCHEMAS_DIR = os.path.abspath(SCHEMAS_DIR)


class SchemaLoader:
    """Loads document-type schemas from the schemas/ directory.
    This is what makes the system extensible: adding a new document
    type only requires adding a new JSON file here — no code changes
    to agents or the graph."""

    _cache: dict[str, dict] = {}

    @classmethod
    def _load_all(cls) -> dict[str, dict]:
        if cls._cache:
            return cls._cache

        if not os.path.isdir(SCHEMAS_DIR):
            return {}

        for filename in os.listdir(SCHEMAS_DIR):
            if not filename.endswith(".json"):
                continue
            path = os.path.join(SCHEMAS_DIR, filename)
            with open(path, "r", encoding="utf-8") as f:
                schema = json.load(f)
                doc_type = schema.get("document_type")
                if doc_type:
                    cls._cache[doc_type] = schema

        return cls._cache

    @classmethod
    def get_schema(cls, document_type: str) -> Optional[dict]:
        """Returns the schema dict for a document_type, or None if
        no matching schema exists (caller must handle this as a
        graceful 'unknown document type' case, not an error)."""
        schemas = cls._load_all()
        return schemas.get(document_type)

    @classmethod
    def list_known_types(cls) -> list[str]:
        """Used by the ClassificationAgent to know which types it's
        allowed to classify into."""
        schemas = cls._load_all()
        return list(schemas.keys())

    @classmethod
    def reload(cls) -> None:
        """Clears cache — useful if schemas are edited while server runs."""
        cls._cache = {}