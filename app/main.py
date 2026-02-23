import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI

from app.routers.search import router as search_router
from app.services.product_service import load_products
from app.services.search_service import BM25Index


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    products_path_raw = os.getenv("PRODUCTS_PATH", "app/data/products.json")
    products_path = Path(products_path_raw)
    if not products_path.exists():
        raise RuntimeError(
            f"Products file not found: {products_path}. "
            "Set PRODUCTS_PATH environment variable to your dataset path."
        )

    products = load_products(products_path)
    app.state.search_index = BM25Index(products)

    yield


app = FastAPI(title="Product Search API", lifespan=lifespan)

app.include_router(search_router)
