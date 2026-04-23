#!/usr/bin/env python3
"""
One-time setup script to install the Playwright Chromium browser driver.

Run this ONCE before using the live-scraping features of aero_build_rates.py:

    python setup_browser.py

What it does:
  1. Installs / upgrades the 'playwright' Python package
  2. Downloads the Chromium browser binary used for JS-rendered scraping
     (~150 MB, stored in your local Playwright cache)

After running this, the main tool will automatically use headless Chromium
to fully render JavaScript-heavy manufacturer pages (Airbus, Boeing, GE,
P&W, Rolls Royce) before extracting delivery data.
"""

import subprocess
import sys
import os


def run(cmd: list[str], label: str) -> bool:
    print(f"\n{'─' * 60}")
    print(f"  {label}")
    print(f"  Command: {' '.join(cmd)}")
    print(f"{'─' * 60}")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"\n  ERROR: '{label}' failed (exit code {result.returncode}).")
        return False
    print(f"\n  ✓  {label} — done.")
    return True


def main():
    print("=" * 60)
    print("  Aero Build Rates — Browser Driver Setup")
    print("=" * 60)

    python = sys.executable

    # Step 1: install / upgrade the playwright Python package
    ok = run(
        [python, "-m", "pip", "install", "--upgrade", "playwright>=1.40.0"],
        "Installing / upgrading playwright Python package",
    )
    if not ok:
        print("\nFailed to install playwright. Check your internet connection.")
        sys.exit(1)

    # Step 2: download the Chromium browser binary
    ok = run(
        [python, "-m", "playwright", "install", "chromium"],
        "Downloading Chromium browser (~150 MB, one-time)",
    )
    if not ok:
        print(
            "\nFailed to install Chromium. You may need to run this script as "
            "Administrator (Windows) or with sudo (Linux/Mac)."
        )
        sys.exit(1)

    # Step 3: quick smoke-test
    print(f"\n{'─' * 60}")
    print("  Smoke-testing Playwright …")
    print(f"{'─' * 60}")
    test_code = (
        "from playwright.sync_api import sync_playwright; "
        "p = sync_playwright().__enter__(); "
        "b = p.chromium.launch(headless=True); "
        "pg = b.new_page(); "
        "pg.goto('about:blank'); "
        "b.close(); "
        "p.__exit__(None,None,None); "
        "print('  Playwright OK')"
    )
    result = subprocess.run([python, "-c", test_code], check=False)
    if result.returncode != 0:
        print("\n  WARNING: smoke-test failed — Playwright may not be fully functional.")
    else:
        print("\n  ✓  Playwright Chromium working correctly.")

    print("\n" + "=" * 60)
    print("  Setup complete!")
    print()
    print("  You can now run:")
    print()
    print("      python aero_build_rates.py")
    print()
    print("  The tool will use headless Chromium to fetch live delivery data")
    print("  from all five manufacturer websites.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
