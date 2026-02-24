"""
AI Categorization Service.

Implements a rule-based keyword-to-category mapper.  This is intentionally
self-contained and requires no external API keys. The architecture makes it
trivial to swap in an LLM call later:

    1. Create a subclass / replace the `_apply_rules` method.
    2. Nothing else changes — routes, tests, and schemas are unaffected.

Design note: the rules are data (a plain dict), not code.  Adding a new
keyword mapping requires editing one dict, not touching any logic.
"""
import re
from typing import Optional

import structlog

log = structlog.get_logger()

# ---------------------------------------------------------------------------
# Rule table: keyword (lowercase, regex-safe) → canonical category name
# ---------------------------------------------------------------------------
_KEYWORD_RULES: list[tuple[str, str]] = [
    # Food & Drink
    (r"grocer|supermarket|walmart|whole\s*food|costco|aldi|trader\s*joe", "Groceries"),
    (r"restaurant|cafe|coffee|starbucks|mcdonald|pizza|sushi|lunch|dinner|breakfast|takeout|takeaway|uber\s*eat|doordash|zomato|swiggy", "Dining"),
    # Transport
    (r"uber|lyft|taxi|cab|fuel|petrol|gas\s*station|parking|toll|metro|subway|bus\s*pass|train|flight|airline|airbnb", "Transport"),
    # Utilities
    (r"electric|electricity|water\s*bill|gas\s*bill|internet|broadband|phone\s*bill|wifi|isp", "Utilities"),
    # Housing
    (r"rent|mortgage|landlord|lease|hoa", "Housing"),
    # Health
    (r"pharmacy|medicin|doctor|clinic|hospital|health|dental|gym|fitness|yoga", "Health"),
    # Entertainment
    (r"netflix|spotify|disney|hulu|prime\s*video|youtube|cinema|movie|concert|game|steam", "Entertainment"),
    # Shopping
    (r"amazon|ebay|shop|clothing|h&m|zara|nike|apple\s*store|best\s*buy|ikea", "Shopping"),
    # Income
    (r"salary|payroll|paycheck|freelance|invoice|dividend|interest|refund|transfer\s*in", "Income"),
    # Subscriptions
    (r"subscription|monthly\s*fee|annual\s*fee|membership", "Subscriptions"),
    # Education
    (r"tuition|course|udemy|coursera|book|textbook|school|university|college", "Education"),
    # Savings / Investments
    (r"invest|mutual\s*fund|stock|crypto|savings|deposit", "Savings"),
]


def suggest_category(description: str) -> dict:
    """
    Return the best-matching category name and a confidence score [0, 1].

    Confidence is 1.0 for a keyword match, 0.0 when no rule matches.
    """
    normalised = description.lower().strip()
    for pattern, category_name in _KEYWORD_RULES:
        if re.search(pattern, normalised):
            log.info(
                "ai_categorize_match",
                description=description,
                category=category_name,
                pattern=pattern,
            )
            return {"category": category_name, "confidence": 1.0}

    log.info("ai_categorize_no_match", description=description)
    return {"category": "Other", "confidence": 0.0}
