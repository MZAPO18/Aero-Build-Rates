#!/usr/bin/env python3
"""
Aero Build Rates Tool
=====================
Pulls the latest published build-rate / delivery data for:
  Airframers : Airbus, Boeing
  Aero Engines: GE Aerospace, Pratt & Whitney (RTX), Rolls Royce

Usage
-----
  python aero_build_rates.py                   # run scrapers + generate Excel
  python aero_build_rates.py --no-scrape       # skip live scraping, use embedded data only
  python aero_build_rates.py --output my.xlsx  # custom output path

Output
------
  output/aero_build_rates_YYYYMMDD.xlsx
"""

import argparse
import logging
import os
import sys
from copy import deepcopy
from datetime import datetime

import historical_data as HD
from scrapers import run_all_scrapers
from excel_writer import build_workbook

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Data assembly ─────────────────────────────────────────────────────────────

def _assemble_data(scrape_results: dict) -> dict:
    """
    Merge embedded historical data with any successfully scraped live values.
    Returns the unified data dict consumed by excel_writer.build_workbook().
    """

    # ── Airbus ────────────────────────────────────────────────────────────────
    airbus_rows = deepcopy(HD.AIRBUS_ANNUAL["rows"])

    # If the scraper returned delivery figures for a year, overwrite or append
    scraped_ab = scrape_results.get("airbus", {})
    if scraped_ab.get("status") == "ok" and scraped_ab.get("data"):
        for yr, cnt in scraped_ab["data"].items():
            existing_years = [r[0] for r in airbus_rows]
            if yr in existing_years:
                idx = existing_years.index(yr)
                # Only update total column (last col) if scrape total differs
                if airbus_rows[idx][-1] != cnt:
                    logger.info("Airbus %d: updating total %d → %d (from scrape)",
                                yr, airbus_rows[idx][-1], cnt)
                    airbus_rows[idx][-1] = cnt
            elif yr > max(existing_years):
                logger.info("Airbus: appending new year %d total=%d from scrape", yr, cnt)
                # Append with unknowns for per-family columns
                airbus_rows.append([yr, "—", "—", "—", "—", "—", cnt])

    # ── Boeing ────────────────────────────────────────────────────────────────
    boeing_rows = deepcopy(HD.BOEING_ANNUAL["rows"])

    scraped_bo = scrape_results.get("boeing", {})
    if scraped_bo.get("status") == "ok" and scraped_bo.get("data"):
        for yr, info in scraped_bo["data"].items():
            cnt = info.get("total", 0)
            if not cnt:
                continue
            existing_years = [r[0] for r in boeing_rows]
            if yr in existing_years:
                idx = existing_years.index(yr)
                if boeing_rows[idx][-1] != cnt:
                    logger.info("Boeing %d: updating total %d → %d (from scrape)",
                                yr, boeing_rows[idx][-1], cnt)
                    boeing_rows[idx][-1] = cnt
            elif yr > max(existing_years):
                logger.info("Boeing: appending new year %d total=%d from scrape", yr, cnt)
                boeing_rows.append([yr, "—", "—", "—", "—", cnt])

    # ── Engine OEMs ───────────────────────────────────────────────────────────
    # GE Aerospace
    ge_rows = deepcopy(HD.GE_ANNUAL["rows"])
    scraped_ge = scrape_results.get("ge_aerospace", {})
    if scraped_ge.get("status") == "ok" and scraped_ge.get("data"):
        latest = scraped_ge["data"].get("latest_engines")
        if latest:
            latest_yr = max(r[0] for r in ge_rows)
            for r in ge_rows:
                if r[0] == latest_yr:
                    old = r[-1]
                    r[-1] = latest
                    logger.info("GE Aerospace %d: total %d → %d (from scrape)", latest_yr, old, latest)

    # P&W
    pw_rows = deepcopy(HD.PW_ANNUAL["rows"])
    scraped_pw = scrape_results.get("pratt_whitney", {})
    if scraped_pw.get("status") == "ok" and scraped_pw.get("data"):
        latest = scraped_pw["data"].get("latest_engines")
        if latest:
            latest_yr = max(r[0] for r in pw_rows)
            for r in pw_rows:
                if r[0] == latest_yr:
                    old = r[-1]
                    r[-1] = latest
                    logger.info("P&W %d: total %d → %d (from scrape)", latest_yr, old, latest)

    # Rolls Royce
    rr_rows = deepcopy(HD.RR_ANNUAL["rows"])
    scraped_rr = scrape_results.get("rolls_royce", {})
    if scraped_rr.get("status") == "ok" and scraped_rr.get("data"):
        latest = scraped_rr["data"].get("latest_engines")
        if latest:
            latest_yr = max(r[0] for r in rr_rows)
            for r in rr_rows:
                if r[0] == latest_yr:
                    old = r[-1]
                    r[-1] = latest
                    logger.info("Rolls Royce %d: total %d → %d (from scrape)", latest_yr, old, latest)

    # ── Recalculate overview rows ─────────────────────────────────────────────
    overview_af_rows = []
    airbus_yr_map = {r[0]: r[-1] for r in airbus_rows}
    boeing_yr_map = {r[0]: r[-1] for r in boeing_rows}
    all_years = sorted(set(airbus_yr_map) | set(boeing_yr_map))
    for yr in all_years:
        ab = airbus_yr_map.get(yr, 0) or 0
        bo = boeing_yr_map.get(yr, 0) or 0
        overview_af_rows.append([yr, ab, bo, ab + bo])

    ge_yr_map  = {r[0]: r[-1] for r in ge_rows}
    pw_yr_map  = {r[0]: r[-1] for r in pw_rows}
    rr_yr_map  = {r[0]: r[-1] for r in rr_rows}
    all_eng_years = sorted(set(ge_yr_map) | set(pw_yr_map) | set(rr_yr_map))
    overview_eng_rows = []
    for yr in all_eng_years:
        ge  = ge_yr_map.get(yr, 0) or 0
        pw  = pw_yr_map.get(yr, 0) or 0
        rr  = rr_yr_map.get(yr, 0) or 0
        overview_eng_rows.append([yr, ge, pw, rr, ge + pw + rr])

    # ── Package it all up ─────────────────────────────────────────────────────
    return {
        "as_of": datetime.now().strftime("%B %Y"),
        "scrape_results": scrape_results,

        "overview": {
            "airframer_totals": {
                "headers": HD.OVERVIEW["airframer_totals"]["headers"],
                "rows": overview_af_rows,
            },
            "engine_totals": {
                "headers": HD.OVERVIEW["engine_totals"]["headers"],
                "rows": overview_eng_rows,
            },
        },

        "airbus": {
            "annual_deliveries": {
                "headers": HD.AIRBUS_ANNUAL["headers"],
                "rows": airbus_rows,
                "notes": HD.AIRBUS_ANNUAL["notes"],
            },
            "production_rates": HD.AIRBUS_RATES,
            "backlog": HD.AIRBUS_BACKLOG,
        },

        "boeing": {
            "annual_deliveries": {
                "headers": HD.BOEING_ANNUAL["headers"],
                "rows": boeing_rows,
                "notes": HD.BOEING_ANNUAL["notes"],
            },
            "production_rates": HD.BOEING_RATES,
            "backlog": HD.BOEING_BACKLOG,
        },

        "ge_aerospace": {
            "annual_deliveries": {
                "headers": HD.GE_ANNUAL["headers"],
                "rows": ge_rows,
                "notes": HD.GE_ANNUAL["notes"],
            },
            "by_engine_type": HD.GE_RATES,
        },

        "pratt_whitney": {
            "annual_deliveries": {
                "headers": HD.PW_ANNUAL["headers"],
                "rows": pw_rows,
                "notes": HD.PW_ANNUAL["notes"],
            },
            "by_engine_type": HD.PW_RATES,
        },

        "rolls_royce": {
            "annual_deliveries": {
                "headers": HD.RR_ANNUAL["headers"],
                "rows": rr_rows,
                "notes": HD.RR_ANNUAL["notes"],
            },
            "by_engine_type": HD.RR_RATES,
        },
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Aero Build Rates Tool — generates an Excel report of "
                    "aircraft and aeroengine build/delivery rates.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--no-scrape",
        action="store_true",
        default=False,
        help="Skip live web scraping; use only embedded historical data.",
    )
    p.add_argument(
        "--output",
        default=None,
        help="Output Excel file path (default: output/aero_build_rates_YYYYMMDD.xlsx).",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=False,
        help="Enable DEBUG-level logging.",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        stamp = datetime.now().strftime("%Y%m%d")
        output_path = os.path.join("output", f"aero_build_rates_{stamp}.xlsx")

    logger.info("=" * 60)
    logger.info("Aero Build Rates Tool")
    logger.info("=" * 60)

    # 1. Live scraping
    if args.no_scrape:
        logger.info("Skipping live scrape (--no-scrape flag set).")
        scrape_results = {
            mfr: {"source": "", "data": None, "status": "skipped",
                  "message": "--no-scrape flag set"}
            for mfr in ["airbus", "boeing", "ge_aerospace", "pratt_whitney", "rolls_royce"]
        }
    else:
        logger.info("Starting live scrape of manufacturer websites …")
        scrape_results = run_all_scrapers()
        ok = sum(1 for r in scrape_results.values() if r["status"] == "ok")
        logger.info("Scrape complete: %d/%d sources returned data.", ok, len(scrape_results))

    # 2. Assemble data
    logger.info("Assembling data …")
    merged = _assemble_data(scrape_results)

    # 3. Write workbook
    logger.info("Writing Excel workbook to: %s", output_path)
    saved = build_workbook(merged, output_path)

    logger.info("=" * 60)
    logger.info("Done! Workbook saved to: %s", saved)
    logger.info("=" * 60)
    print(f"\n✓  Report saved to: {saved}\n")


if __name__ == "__main__":
    main()
