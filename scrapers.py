"""
Web scrapers for each manufacturer's publicly available delivery / build-rate data.

Each scraper returns a dict with keys:
  'source'   – URL actually fetched
  'data'     – dict of parsed values (or None if parsing failed)
  'status'   – 'ok' | 'partial' | 'failed'
  'message'  – human-readable note

Scrapers are intentionally tolerant: if the page structure changes or the site
is JS-rendered (and therefore returns a skeleton shell), the functions return
status='failed' so the caller falls back to embedded historical_data.
"""

import re
import time
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime

logger = logging.getLogger(__name__)

# ── shared HTTP session ──────────────────────────────────────────────────────

_SESSION = None


def _get_session() -> requests.Session:
    global _SESSION
    if _SESSION is None:
        _SESSION = requests.Session()
        _SESSION.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            }
        )
    return _SESSION


def _fetch(url: str, timeout: int = 20) -> tuple[int, str]:
    """Return (status_code, html_text) or (-1, '') on error."""
    try:
        resp = _get_session().get(url, timeout=timeout, allow_redirects=True)
        return resp.status_code, resp.text
    except Exception as exc:
        logger.debug("Fetch failed for %s: %s", url, exc)
        return -1, ""


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def _find_integers(text: str) -> list[int]:
    """Extract all integers (including comma-formatted) from a text block."""
    nums = re.findall(r"\b(\d{1,3}(?:,\d{3})*|\d+)\b", text)
    return [int(n.replace(",", "")) for n in nums]


def _find_year_deliveries(text: str) -> dict[int, int]:
    """
    Heuristic: look for patterns like "delivered NNN aircraft in YYYY" or
    "YYYY: NNN deliveries" and return {year: count}.
    """
    results: dict[int, int] = {}
    patterns = [
        r"(\d{4})[^0-9]{1,30}?(\d{2,4})\s*(?:aircraft|airplane|deliveries|delivered)",
        r"delivered\s+(\d{2,4})\s*(?:aircraft|airplane)[^0-9]{1,30}?(\d{4})",
        r"full[- ]year\s+(\d{4})[^0-9]{1,30}?(\d{2,4})\s*(?:aircraft|deliveries)",
    ]
    for pattern in patterns:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            g1, g2 = int(m.group(1)), int(m.group(2))
            # whichever is a plausible year and the other a plausible count
            if 2015 <= g1 <= 2030 and 10 <= g2 <= 2000:
                results[g1] = g2
            elif 2015 <= g2 <= 2030 and 10 <= g1 <= 2000:
                results[g2] = g1
    return results


# ── AIRBUS ───────────────────────────────────────────────────────────────────

AIRBUS_PR_URL = "https://www.airbus.com/en/newsroom/press-releases"
AIRBUS_DELIVERY_KEYWORDS = ["deliveries", "delivered", "orders-and-deliveries"]


def scrape_airbus() -> dict:
    """
    Try to find the most recent Airbus full-year delivery press release and
    extract the headline delivery total.
    """
    result = {"source": AIRBUS_PR_URL, "data": None, "status": "failed", "message": ""}

    status, html = _fetch(AIRBUS_PR_URL)
    if status != 200 or not html.strip():
        result["message"] = f"HTTP {status}; page may be JS-rendered."
        return result

    soup = _soup(html)
    text = soup.get_text(" ", strip=True)

    # Too short → skeleton JS page
    if len(text) < 500:
        result["message"] = "Page appears JS-rendered (text too short)."
        return result

    parsed = _find_year_deliveries(text)
    if parsed:
        result["data"] = parsed
        result["status"] = "ok"
        result["message"] = f"Parsed {len(parsed)} year(s) of delivery data."
    else:
        result["status"] = "partial"
        result["message"] = "Page loaded but no delivery figures matched pattern."

    return result


# ── BOEING ───────────────────────────────────────────────────────────────────

BOEING_DELIVERY_URLS = [
    "https://ir.boeing.com/news-releases",
    "https://www.boeing.com/commercial/orders-and-deliveries",
]

# Boeing sometimes publishes a public orders/deliveries Excel; we can also
# try the static JSON feed that powers their interactive web table.
BOEING_JSON_FEEDS = [
    "https://www.boeing.com/resources/boeingdotcom/commercial/orders-deliveries/assets/data/orders-deliveries.json",
    "https://www.boeing.com/commercial/orders-and-deliveries/orderdelivery-data.json",
]


def _parse_boeing_json(data: list | dict) -> dict[int, dict]:
    """
    Best-effort parse of Boeing's delivery JSON (format can vary).
    Returns {year: {'total': N, 'by_model': {...}}}.
    """
    yearly: dict[int, dict] = {}
    try:
        rows = data if isinstance(data, list) else data.get("data", data.get("deliveries", []))
        for row in rows:
            year = row.get("year") or row.get("Year")
            if not year:
                continue
            year = int(year)
            total = row.get("total") or row.get("Total") or row.get("deliveries") or 0
            yearly[year] = {"total": int(total), "by_model": {}}
    except Exception:
        pass
    return yearly


def scrape_boeing() -> dict:
    result = {"source": BOEING_DELIVERY_URLS[0], "data": None, "status": "failed", "message": ""}

    # 1. Try JSON feed first (most structured)
    import json as _json
    for feed_url in BOEING_JSON_FEEDS:
        status, html = _fetch(feed_url)
        if status == 200 and html.strip().startswith(("[", "{")):
            try:
                parsed = _parse_boeing_json(_json.loads(html))
                if parsed:
                    result["source"] = feed_url
                    result["data"] = parsed
                    result["status"] = "ok"
                    result["message"] = f"Parsed {len(parsed)} year(s) from JSON feed."
                    return result
            except Exception:
                pass

    # 2. Fall back to HTML press-release page
    for url in BOEING_DELIVERY_URLS:
        status, html = _fetch(url)
        if status != 200 or not html.strip():
            continue
        soup = _soup(html)
        text = soup.get_text(" ", strip=True)
        if len(text) < 500:
            continue
        parsed = _find_year_deliveries(text)
        if parsed:
            result["source"] = url
            result["data"] = {yr: {"total": cnt, "by_model": {}} for yr, cnt in parsed.items()}
            result["status"] = "ok"
            result["message"] = f"Parsed {len(parsed)} year(s) from press-release page."
            return result

    result["message"] = "All Boeing URLs returned JS-skeleton or no delivery data."
    return result


# ── GE AEROSPACE ─────────────────────────────────────────────────────────────

GE_PR_URLS = [
    "https://www.geaerospace.com/news/press-releases",
    "https://www.geaerospace.com/investor-relations/ir-updates",
]

_GE_ENGINE_PATTERNS = [
    r"(?:delivered|shipped)\s+([\d,]+)\s*(?:commercial\s+)?(?:new\s+)?engines?",
    r"([\d,]+)\s*(?:commercial\s+)?(?:new\s+)?engines?\s*(?:delivered|shipped)",
    r"LEAP[^0-9]{0,20}?([\d,]+)\s*(?:engines?|units?|deliveries)",
]


def _parse_engine_count(text: str, patterns: list[str]) -> int | None:
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            val = int(m.group(1).replace(",", ""))
            if 100 <= val <= 5000:
                return val
    return None


def scrape_ge_aerospace() -> dict:
    result = {"source": GE_PR_URLS[0], "data": None, "status": "failed", "message": ""}

    for url in GE_PR_URLS:
        status, html = _fetch(url)
        if status != 200 or not html.strip():
            continue
        soup = _soup(html)
        text = soup.get_text(" ", strip=True)
        if len(text) < 500:
            continue
        count = _parse_engine_count(text, _GE_ENGINE_PATTERNS)
        if count:
            result["source"] = url
            result["data"] = {"latest_engines": count}
            result["status"] = "ok"
            result["message"] = f"Found engine delivery figure: {count:,}."
            return result

    result["message"] = "GE Aerospace pages returned JS-skeleton or no engine data."
    return result


# ── PRATT & WHITNEY / RTX ────────────────────────────────────────────────────

RTX_URLS = [
    "https://investors.rtx.com/financial-news",
    "https://investors.rtx.com/press-releases",
    "https://www.prattwhitney.com/en/newsroom/news",
]

_PW_ENGINE_PATTERNS = [
    r"(?:delivered|shipped)\s+([\d,]+)\s*(?:large\s+)?(?:commercial\s+)?engines?",
    r"([\d,]+)\s*(?:large\s+)?(?:commercial\s+)?engines?\s*(?:delivered|shipped)",
    r"GTF[^0-9]{0,20}?([\d,]+)\s*(?:engines?|deliveries|units?)",
    r"PW1\d{3}G[^0-9]{0,20}?([\d,]+)",
]


def scrape_pratt_whitney() -> dict:
    result = {"source": RTX_URLS[0], "data": None, "status": "failed", "message": ""}

    for url in RTX_URLS:
        status, html = _fetch(url)
        if status != 200 or not html.strip():
            continue
        soup = _soup(html)
        text = soup.get_text(" ", strip=True)
        if len(text) < 500:
            continue
        count = _parse_engine_count(text, _PW_ENGINE_PATTERNS)
        if count:
            result["source"] = url
            result["data"] = {"latest_engines": count}
            result["status"] = "ok"
            result["message"] = f"Found P&W engine delivery figure: {count:,}."
            return result

    result["message"] = "RTX / P&W pages returned JS-skeleton or no engine data."
    return result


# ── ROLLS ROYCE ──────────────────────────────────────────────────────────────

RR_URLS = [
    "https://www.rolls-royce.com/investors/results-reports-and-presentations/financial-results.aspx",
    "https://www.rolls-royce.com/media/press-releases.aspx",
    "https://www.rolls-royce.com/investors.aspx",
]

_RR_ENGINE_PATTERNS = [
    r"(?:delivered|shipments?)\s+([\d,]+)\s*(?:large\s+)?(?:civil\s+)?engines?",
    r"([\d,]+)\s*(?:large\s+)?(?:civil\s+)?engines?\s*(?:delivered|shipments?)",
    r"Trent\s+XWB[^0-9]{0,20}?([\d,]+)",
    r"large\s+engine\s+deliveries[^0-9]{0,20}?([\d,]+)",
]


def scrape_rolls_royce() -> dict:
    result = {"source": RR_URLS[0], "data": None, "status": "failed", "message": ""}

    for url in RR_URLS:
        status, html = _fetch(url)
        if status != 200 or not html.strip():
            continue
        soup = _soup(html)
        text = soup.get_text(" ", strip=True)
        if len(text) < 500:
            continue
        count = _parse_engine_count(text, _RR_ENGINE_PATTERNS)
        if count:
            result["source"] = url
            result["data"] = {"latest_engines": count}
            result["status"] = "ok"
            result["message"] = f"Found RR engine delivery figure: {count:,}."
            return result

    result["message"] = "Rolls Royce pages returned JS-skeleton or no engine data."
    return result


# ── RUN ALL ──────────────────────────────────────────────────────────────────

def run_all_scrapers(delay: float = 1.5) -> dict:
    """
    Execute every scraper with a short polite delay between requests.
    Returns a dict keyed by manufacturer with scraper result dicts.
    """
    scrapers = {
        "airbus": scrape_airbus,
        "boeing": scrape_boeing,
        "ge_aerospace": scrape_ge_aerospace,
        "pratt_whitney": scrape_pratt_whitney,
        "rolls_royce": scrape_rolls_royce,
    }

    results = {}
    for name, fn in scrapers.items():
        logger.info("Scraping %s …", name)
        results[name] = fn()
        logger.info(
            "  → %s: %s — %s", name, results[name]["status"], results[name]["message"]
        )
        time.sleep(delay)

    return results
