"""
Web scrapers for each manufacturer's publicly available delivery / build-rate data.

Uses Playwright (headless Chromium) when installed for JS-rendered sites.
Falls back to plain requests for static pages or when Playwright is unavailable.

Run  python setup_browser.py  once to install the Chromium driver.
"""

import re
import time
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime

logger = logging.getLogger(__name__)

# ── Playwright availability check ────────────────────────────────────────────

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.debug("playwright not installed — using requests fallback.")

_PW_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# ── Shared requests session ───────────────────────────────────────────────────

_SESSION = None


def _get_session() -> requests.Session:
    global _SESSION
    if _SESSION is None:
        _SESSION = requests.Session()
        _SESSION.headers.update({
            "User-Agent": _PW_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })
    return _SESSION


def _fetch_requests(url: str, timeout: int = 20) -> tuple[int, str]:
    """Plain requests fetch. Returns (status_code, html)."""
    try:
        r = _get_session().get(url, timeout=timeout, allow_redirects=True)
        return r.status_code, r.text
    except Exception as exc:
        logger.debug("requests fetch failed for %s: %s", url, exc)
        return -1, ""


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


# ── Playwright shared browser context ────────────────────────────────────────

class _Browser:
    """
    Manages a single shared Playwright browser for an entire scraping run.
    Use as a context manager:

        with _Browser() as br:
            status, html = br.fetch(url)
    """

    def __init__(self):
        self._pw_cm   = None
        self._pw      = None
        self._browser = None
        self.ok       = False   # True when the browser launched successfully

    def __enter__(self):
        if not PLAYWRIGHT_AVAILABLE:
            logger.warning(
                "Playwright not installed. Run  python setup_browser.py  "
                "to enable JS-rendered scraping."
            )
            return self
        try:
            self._pw_cm  = sync_playwright()
            self._pw     = self._pw_cm.__enter__()
            self._browser = self._pw.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            self.ok = True
            logger.info("Playwright Chromium browser started (headless).")
        except Exception as exc:
            logger.warning(
                "Playwright browser failed to start: %s\n"
                "  → Run  python setup_browser.py  to install the Chromium driver.",
                exc,
            )
        return self

    def __exit__(self, *args):
        try:
            if self._browser:
                self._browser.close()
            if self._pw_cm:
                self._pw_cm.__exit__(*args)
        except Exception:
            pass

    def _new_page(self):
        ctx = self._browser.new_context(
            user_agent=_PW_USER_AGENT,
            viewport={"width": 1280, "height": 900},
            java_script_enabled=True,
        )
        page = ctx.new_page()
        page.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})
        return page

    def fetch(self, url: str, timeout_ms: int = 35_000,
              wait_until: str = "networkidle") -> tuple[int, str]:
        """
        Fetch URL with Playwright (full JS rendering) if the browser is
        available, otherwise fall back to plain requests.
        """
        if self.ok:
            page = None
            try:
                page = self._new_page()
                resp  = page.goto(url, wait_until=wait_until, timeout=timeout_ms)
                html  = page.content()
                code  = resp.status if resp else 200
                page.context.close()
                if len(html) > 800:
                    return code, html
            except PlaywrightTimeout:
                logger.debug("Playwright timeout on %s; falling back to requests.", url)
                if page:
                    try:
                        page.context.close()
                    except Exception:
                        pass
            except Exception as exc:
                logger.debug("Playwright fetch error (%s): %s", url, exc)
                if page:
                    try:
                        page.context.close()
                    except Exception:
                        pass

        # Fall back to requests
        return _fetch_requests(url)

    def fetch_follow_link(
        self,
        listing_url: str,
        link_patterns: list[str],
        base_url: str = "",
        listing_wait: str = "networkidle",
        article_wait: str = "networkidle",
        timeout_ms: int = 35_000,
    ) -> tuple[str, str]:
        """
        Load listing_url, find the first <a> whose text matches any of
        link_patterns (regex), follow it, and return (article_text, final_url).
        """
        status, html = self.fetch(listing_url, timeout_ms=timeout_ms,
                                  wait_until=listing_wait)
        if not html:
            return "", listing_url

        href = _find_first_link(html, link_patterns, base_url)
        if not href:
            # Return listing page text if we can't find a deeper link
            return _soup(html).get_text(" ", strip=True), listing_url

        # Navigate to the target article
        _, article_html = self.fetch(href, timeout_ms=timeout_ms,
                                     wait_until=article_wait)
        text = _soup(article_html).get_text(" ", strip=True) if article_html else ""
        return text, href


# ── HTML helpers ─────────────────────────────────────────────────────────────

def _find_first_link(html: str, patterns: list[str], base_url: str = "") -> str:
    """Return the href of the first <a> whose text matches any pattern."""
    soup = _soup(html)
    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True)
        href = a["href"]
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                if href.startswith("http"):
                    return href
                if href.startswith("/") and base_url:
                    return base_url.rstrip("/") + href
    return ""


def _find_year_deliveries(text: str) -> dict[int, int]:
    """
    Heuristic: scan text for "YYYY: NNN aircraft" or "delivered NNN in YYYY"
    style patterns. Returns {year: count}.
    """
    results: dict[int, int] = {}
    patterns = [
        r"(\b20\d{2}\b)[^0-9]{1,40}?(\b\d{3,4}\b)\s*(?:aircraft|airplane|deliveries|delivered)",
        r"delivered\s+(\b\d{3,4}\b)\s*(?:aircraft|airplane)[^0-9]{1,40}?(\b20\d{2}\b)",
        r"full[- ]year\s+(\b20\d{2}\b)[^0-9]{1,40}?(\b\d{3,4}\b)\s*(?:aircraft|deliveries)",
    ]
    for pat in patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            g1, g2 = m.group(1), m.group(2)
            try:
                a, b = int(g1), int(g2)
            except ValueError:
                continue
            # Normalise: which is year, which is count?
            if 2015 <= a <= 2030 and 50 <= b <= 2000:
                results[a] = b
            elif 2015 <= b <= 2030 and 50 <= a <= 2000:
                results[b] = a
    return results


def _find_engine_count(text: str, patterns: list[str]) -> int | None:
    """Return the first integer that looks like an engine delivery count."""
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            try:
                val = int(m.group(1).replace(",", "").replace(" ", ""))
                if 100 <= val <= 6000:
                    return val
            except (ValueError, IndexError):
                pass
    return None


# ── Per-manufacturer scrapers ─────────────────────────────────────────────────

# ── Airbus ────────────────────────────────────────────────────────────────────

AIRBUS_BASE      = "https://www.airbus.com"
AIRBUS_PR_URL    = "https://www.airbus.com/en/newsroom/press-releases"

# Patterns that identify the annual delivery press release link
AIRBUS_LINK_PATS = [
    r"airbus\s+delivered\s+\d+",
    r"full[- ]year\s+20\d{2}\s+deliveries",
    r"20\d{2}\s+full[- ]year\s+deliveries",
    r"delivered\s+\d+\s+aircraft\s+in\s+20\d{2}",
    r"annual\s+deliveries?\s+20\d{2}",
]


def scrape_airbus(br: _Browser) -> dict:
    result = {"source": AIRBUS_PR_URL, "data": None, "status": "failed", "message": ""}

    text, url = br.fetch_follow_link(
        AIRBUS_PR_URL,
        link_patterns=AIRBUS_LINK_PATS,
        base_url=AIRBUS_BASE,
    )
    result["source"] = url

    if len(text) < 300:
        result["message"] = "Page too short; likely JS-skeleton without Playwright."
        return result

    parsed = _find_year_deliveries(text)
    if parsed:
        result["data"]    = parsed
        result["status"]  = "ok"
        result["message"] = f"Parsed delivery data for year(s): {sorted(parsed.keys())}"
    else:
        result["status"]  = "partial"
        result["message"] = "Page loaded but no delivery figures matched regex patterns."
    return result


# ── Boeing ────────────────────────────────────────────────────────────────────

BOEING_BASE   = "https://ir.boeing.com"
BOEING_IR_URL = "https://ir.boeing.com/news-releases"

BOEING_JSON_FEEDS = [
    "https://www.boeing.com/resources/boeingdotcom/commercial/orders-deliveries/assets/data/orders-deliveries.json",
]

BOEING_LINK_PATS = [
    r"orders?\s+(?:and|&)\s+deliveries?",
    r"boeing\s+reports?\s+(?:december|november|october|full[- ]year|annual)\s+deliveries?",
    r"deliveries?\s+\d{4}",
    r"commercial\s+deliveries?",
]


def scrape_boeing(br: _Browser) -> dict:
    result = {"source": BOEING_IR_URL, "data": None, "status": "failed", "message": ""}

    # 1. Try JSON feed (fastest, most structured)
    import json as _json
    for feed in BOEING_JSON_FEEDS:
        _, raw = _fetch_requests(feed)
        if raw and raw.strip().startswith(("[", "{")):
            try:
                obj = _json.loads(raw)
                rows = obj if isinstance(obj, list) else obj.get("data", obj.get("deliveries", []))
                yearly: dict[int, dict] = {}
                for row in rows:
                    yr = row.get("year") or row.get("Year")
                    tot = row.get("total") or row.get("Total") or row.get("deliveries") or 0
                    if yr and tot:
                        yearly[int(yr)] = {"total": int(tot), "by_model": {}}
                if yearly:
                    result.update(source=feed, data=yearly, status="ok",
                                  message=f"Parsed {len(yearly)} year(s) from JSON feed.")
                    return result
            except Exception:
                pass

    # 2. Playwright: listing page → follow delivery link → parse text
    text, url = br.fetch_follow_link(
        BOEING_IR_URL,
        link_patterns=BOEING_LINK_PATS,
        base_url=BOEING_BASE,
    )
    result["source"] = url

    if len(text) < 300:
        result["message"] = "Boeing IR page too short; JS-skeleton without Playwright."
        return result

    parsed = _find_year_deliveries(text)
    if parsed:
        result["data"]   = {yr: {"total": cnt, "by_model": {}} for yr, cnt in parsed.items()}
        result["status"] = "ok"
        result["message"] = f"Parsed delivery data for year(s): {sorted(parsed.keys())}"
    else:
        result["status"]  = "partial"
        result["message"] = "Boeing page loaded but no delivery figures matched patterns."
    return result


# ── GE Aerospace ─────────────────────────────────────────────────────────────

GE_BASE    = "https://www.geaerospace.com"
GE_PR_URL  = "https://www.geaerospace.com/news/press-releases"

GE_LINK_PATS = [
    r"fourth[- ]quarter.*(?:results|earnings)",
    r"full[- ]year.*(?:results|earnings)",
    r"q4\s+20\d{2}",
    r"annual\s+(?:results|earnings)\s+20\d{2}",
]

GE_ENGINE_PATS = [
    r"(?:delivered|shipped)\s+([\d,]+)\s*(?:commercial\s+)?(?:new\s+)?engines?",
    r"([\d,]+)\s*(?:commercial\s+)?(?:new\s+)?engines?\s*(?:delivered|shipped)",
    r"LEAP[^0-9]{0,30}([\d,]+)\s*(?:engines?|units?|deliveries)",
    r"commercial\s+engines?\s+(?:delivered|shipments?)[^0-9]{0,30}([\d,]+)",
    r"([\d,]+)\s*commercial\s+engine\s+(?:deliveries|shipments?)",
]


def scrape_ge_aerospace(br: _Browser) -> dict:
    result = {"source": GE_PR_URL, "data": None, "status": "failed", "message": ""}

    text, url = br.fetch_follow_link(
        GE_PR_URL,
        link_patterns=GE_LINK_PATS,
        base_url=GE_BASE,
    )
    result["source"] = url

    if len(text) < 300:
        result["message"] = "GE Aerospace page too short."
        return result

    count = _find_engine_count(text, GE_ENGINE_PATS)
    if count:
        result["data"]    = {"latest_engines": count}
        result["status"]  = "ok"
        result["message"] = f"Engine delivery figure found: {count:,}"
    else:
        result["status"]  = "partial"
        result["message"] = "GE page loaded but no engine delivery count matched patterns."
    return result


# ── Pratt & Whitney / RTX ─────────────────────────────────────────────────────

RTX_BASE    = "https://investors.rtx.com"
RTX_PR_URL  = "https://investors.rtx.com/press-releases"
PW_NEWS_URL = "https://www.prattwhitney.com/en/newsroom/news"

RTX_LINK_PATS = [
    r"fourth[- ]quarter.*(?:results|earnings)",
    r"full[- ]year.*(?:results|earnings)",
    r"q4\s+20\d{2}",
    r"rtx\s+reports?\s+(?:fourth|fourth[- ]quarter|full[- ]year)",
    r"annual\s+(?:results|earnings)\s+20\d{2}",
]

PW_ENGINE_PATS = [
    r"(?:delivered|shipped)\s+([\d,]+)\s*(?:large\s+)?(?:commercial\s+)?engines?",
    r"([\d,]+)\s*(?:large\s+)?(?:commercial\s+)?engines?\s*(?:delivered|shipped)",
    r"GTF[^0-9]{0,30}([\d,]+)\s*(?:engines?|deliveries|units?)",
    r"PW1[0-9]{3}G[^0-9]{0,30}([\d,]+)",
    r"geared\s+turbofan[^0-9]{0,30}([\d,]+)",
    r"pratt\s+&\s+whitney[^0-9]{0,60}([\d,]+)\s*(?:engines?|deliveries)",
]


def scrape_pratt_whitney(br: _Browser) -> dict:
    result = {"source": RTX_PR_URL, "data": None, "status": "failed", "message": ""}

    text, url = br.fetch_follow_link(
        RTX_PR_URL,
        link_patterns=RTX_LINK_PATS,
        base_url=RTX_BASE,
    )
    result["source"] = url

    if len(text) < 300:
        result["message"] = "RTX IR page too short."
        return result

    count = _find_engine_count(text, PW_ENGINE_PATS)
    if count:
        result["data"]    = {"latest_engines": count}
        result["status"]  = "ok"
        result["message"] = f"P&W engine delivery figure found: {count:,}"
    else:
        result["status"]  = "partial"
        result["message"] = "RTX page loaded but no P&W engine count matched patterns."
    return result


# ── Rolls Royce ───────────────────────────────────────────────────────────────

RR_BASE       = "https://www.rolls-royce.com"
RR_RESULTS_URL = "https://www.rolls-royce.com/investors/results-reports-and-presentations/financial-results.aspx"
RR_PR_URL     = "https://www.rolls-royce.com/media/press-releases.aspx"

RR_LINK_PATS = [
    r"full[- ]year\s+results?\s+20\d{2}",
    r"annual\s+results?\s+20\d{2}",
    r"(?:fourth[- ]quarter|full[- ]year).*(?:results|earnings)\s+20\d{2}",
    r"20\d{2}\s+full[- ]year\s+results?",
    r"preliminary\s+results?\s+20\d{2}",
]

RR_ENGINE_PATS = [
    r"(?:delivered|shipments?|shipped)\s+([\d,]+)\s*(?:large\s+)?(?:civil\s+)?engines?",
    r"([\d,]+)\s*(?:large\s+)?(?:civil\s+)?engines?\s*(?:delivered|shipments?)",
    r"large\s+(?:civil\s+)?engine\s+(?:deliveries|shipments?)[^0-9]{0,30}([\d,]+)",
    r"Trent\s+XWB[^0-9]{0,30}([\d,]+)",
    r"civil\s+aerospace[^0-9]{0,60}([\d,]+)\s*(?:engines?|deliveries)",
]


def scrape_rolls_royce(br: _Browser) -> dict:
    result = {"source": RR_RESULTS_URL, "data": None, "status": "failed", "message": ""}

    # Try the financial results page first (most likely to have delivery numbers)
    text, url = br.fetch_follow_link(
        RR_RESULTS_URL,
        link_patterns=RR_LINK_PATS,
        base_url=RR_BASE,
    )
    result["source"] = url

    if len(text) < 300:
        # Fall back to press releases page
        text, url = br.fetch_follow_link(
            RR_PR_URL,
            link_patterns=RR_LINK_PATS,
            base_url=RR_BASE,
        )
        result["source"] = url

    if len(text) < 300:
        result["message"] = "Rolls Royce pages too short."
        return result

    count = _find_engine_count(text, RR_ENGINE_PATS)
    if count:
        result["data"]    = {"latest_engines": count}
        result["status"]  = "ok"
        result["message"] = f"RR engine delivery figure found: {count:,}"
    else:
        result["status"]  = "partial"
        result["message"] = "RR page loaded but no engine count matched patterns."
    return result


# ── Orchestrator ──────────────────────────────────────────────────────────────

def run_all_scrapers(delay: float = 2.0) -> dict:
    """
    Run all five scrapers, sharing a single Playwright browser session.
    Returns {manufacturer: result_dict}.
    """
    scrapers = [
        ("airbus",        scrape_airbus),
        ("boeing",        scrape_boeing),
        ("ge_aerospace",  scrape_ge_aerospace),
        ("pratt_whitney", scrape_pratt_whitney),
        ("rolls_royce",   scrape_rolls_royce),
    ]

    results = {}
    with _Browser() as br:
        for name, fn in scrapers:
            logger.info("Scraping %s …", name)
            results[name] = fn(br)
            logger.info(
                "  → %s: %s — %s",
                name, results[name]["status"], results[name]["message"],
            )
            time.sleep(delay)

    return results
