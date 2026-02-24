# Product Search Engine

REST API for searching products in an online shop dataset

## What I Built

A search API with:
- Hybrid search (BM25 + semantic embeddings)
- Text search across product name, description, and brand
- Returns top 10 results by default (configurable via `limit` parameter)
- Handles messy input (extra spaces, different casing, punctuation)

## How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set dataset path
(This is already set to this path by default. skip this or set your required path)

```bash
$env:PRODUCTS_PATH="app/data/products.json"
```

### 3. Start server
(First startup takes a little time)
```bash
uvicorn app.main:app --reload
```

### 4. Test the API

Open browser: `http://127.0.0.1:8000/docs`

**Note:** First startup takes 2-3 minutes (downloads semantic model and generates embeddings). Subsequent startups are ~10 seconds (loads from cache).

## Example Queries

- `smart bulb`
- `   SMArt BulB!!   `
- `athletic wear`
- `runing` (still returns results for "running")
- `hfghfdgh` (doesn't return anything for unrelated query)
## How Search Works (High Level)

The search engine uses a **hybrid approach** combining two methods:

### 1. Lexical Search (BM25) - 70% weight
- Tokenizes text into words
- Scores products using BM25 algorithm
- Applies field-level boosting:
  - Product name: 3.0x weight (most important)
  - Description: 1.0x weight (baseline)
  - Brand: 0.5x weight (minor signal)

### 2. Semantic Search (Embeddings) - 30% weight
- Converts text into 384-dimensional vectors using pre-trained AI model
- Measures similarity using cosine distance
- Understands meaning beyond exact words
- Good at: synonyms, related concepts, vague queries

### 3. Combining & Filtering
- Combines both scores: `0.7 × BM25 + 0.3 × Semantic`
- Filters out low-quality matches (score < 0.20 threshold)
- Sorts by relevance
- Returns top results

## What I Built vs What I Reused

### Built from scratch:
- Hybrid scoring strategy (combining BM25 + semantic)
- Field-level weight configuration
- Text normalization pipeline
- Cache system for embeddings (validates product changes, model changes)
- API endpoint design and response formatting
- Quality threshold filtering

### Reused libraries:
- **rank-bm25** - BM25 algorithm implementation
  - Why: It's widely used library for BM25 algorithm
- **sentence-transformers** - Semantic embeddings (AI model)
  - Why: Pre-trained model understands language meaning
- **FastAPI** - Web framework
  - Why: Fast, modern
- **scikit-learn** - Cosine similarity calculation
  - Why: Optimized vector operations
- **Pydantic** - Data validation
  - Why: Type-safe request/response schemas

## Strengths and Weaknesses

### Works well:
- Handles exact keyword matches
- Understands semantic similarity
- Fast startup after first run because of caching
- Field boosting ensures product names rank higher than descriptions

### Weak / Unfinished:
- typo tolerance is enforced by semantic search. Could be possibly improved.
- First startup is slow
- Could possibly add re-ranking for more efficiency, but for current dataset and requirements I didn't consider it necessary.
