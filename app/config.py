"""Search engine configuration constants."""

# BM25 Field Weights
# Higher weight = more importance in ranking
NAME_FIELD_WEIGHT = 3.0  # Product name is most important
DESCRIPTION_FIELD_WEIGHT = 1.0  # Baseline weight
BRAND_FIELD_WEIGHT = 0.5  # Brand is a weak signal (tie-breaker)

# Search Result Limits
DEFAULT_RESULT_LIMIT = 10  # Default number of results to return
MIN_RESULT_LIMIT = 1  # Minimum allowed results
MAX_RESULT_LIMIT = 50  # Maximum allowed results
