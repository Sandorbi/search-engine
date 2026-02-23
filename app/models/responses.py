from typing import Any, Dict, List

from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    score: float = Field(..., description="Relevance score")
    product: Dict[str, Any] = Field(..., description="Product data")


class SearchResponse(BaseModel):
    query: str = Field(..., description="Original query")
    limit: int = Field(..., description="Requested number of results")
    count: int = Field(..., description="Actual number of results returned")
    results: List[SearchResultItem] = Field(..., description="Ranked search results")
