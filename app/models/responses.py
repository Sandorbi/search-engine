from typing import Any

from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    product: dict[str, Any] = Field(..., description="Product data")


class SearchResponse(BaseModel):
    query: str = Field(..., description="Original query")
    limit: int = Field(..., description="Requested number of results")
    count: int = Field(..., description="Actual number of results returned")
    results: list[SearchResultItem] = Field(..., description="Ranked search results")
