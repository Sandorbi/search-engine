import json
from pathlib import Path
from typing import Any, Dict, List


def load_products(products_path: Path) -> List[Dict[str, Any]]:
    """Load products from JSON file."""
    with products_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Products JSON must contain a list of product objects.")
    return data
