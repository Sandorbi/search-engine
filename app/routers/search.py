from fastapi import APIRouter, HTTPException, Query, Request

from app.models.responses import SearchResponse, SearchResultItem


router = APIRouter(tags=["search"])


@router.get("/search", response_model=SearchResponse)
def search_products(
    request: Request,
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="How many results to return"),
) -> SearchResponse:
    if not q.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty.")

    ranked_results = request.app.state.search_index.search(q, limit=limit)

    results = [
        SearchResultItem(score=round(score, 4), product=product) 
        for score, product in ranked_results
    ]

    return SearchResponse(
        query=q,
        limit=limit,
        count=len(results),
        results=results,
    )
