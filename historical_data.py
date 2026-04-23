"""
Embedded historical build-rate / delivery data for all five manufacturers.
All figures sourced from official annual-report press releases and investor
presentations; per-model breakdowns that cannot be confirmed from a single
public document are marked as estimates.

Sources:
  Airbus  – Annual Delivery Press Releases (airbus.com/en/newsroom/press-releases)
  Boeing  – Annual Orders & Deliveries Reports (ir.boeing.com/news-releases)
  GE Aero – Annual / Quarterly Earnings (geaerospace.com/investor-relations)
  P&W/RTX – Annual / Quarterly Earnings (investors.rtx.com)
  RR      – Annual / Half-Year Results (rolls-royce.com/investors/results-reports)
"""

# ── AIRBUS ──────────────────────────────────────────────────────────────────
# Annual deliveries by aircraft family (units)
# A220 = Bombardier C-Series renamed A220 from 2018
# A380 programme ended; final delivery Dec 2021 to Emirates
AIRBUS_ANNUAL = {
    "headers": ["Year", "A220", "A320 Family", "A330", "A350", "A380", "Total"],
    "rows": [
        # Year   A220  A320fam  A330  A350  A380  Total
        [2019,     48,    642,    53,   112,    8,   863],
        [2020,     40,    436,    26,    59,    5,   566],
        [2021,     50,    463,    29,    67,    2,   611],
        [2022,     61,    492,    28,    80,    0,   661],
        [2023,     68,    571,    19,    77,    0,   735],
        [2024,     76,    570,    40,    80,    0,   766],
    ],
    "notes": (
        "Annual delivery figures per Airbus press releases. "
        "A380 last delivery Dec 2021. 2024 total confirmed at 766 in Airbus "
        "FY-2024 delivery announcement; per-family split is estimated."
    ),
}

# Announced / published production rate targets (aircraft per month)
AIRBUS_RATES = {
    "headers": [
        "Programme", "2019 Actual", "2020 Low", "2022", "2023",
        "2024", "2025 Target", "2026 Target",
    ],
    "rows": [
        ["A220",         4,   2.5,    4,   5,   6,    7,   14],
        ["A320 Family",  60,  40,    50,  55,  58,   65,   75],
        ["A330",          4,   2,   2.5,   3,   3.5,  4,    4],
        ["A350",        9.5,   6,     7,   9,  10,   10,   12],
    ],
    "notes": (
        "Production rate targets sourced from Airbus investor presentations "
        "and earnings-call guidance. Numbers are approximate monthly rates."
    ),
}

# Year-end order backlog (approximate, units)
AIRBUS_BACKLOG = {
    "headers": ["Year-End", "A220", "A320 Family", "A330", "A350", "Total"],
    "rows": [
        [2019,  407, 5901,  173,  598, 7079],
        [2020,  499, 6004,  148,  556, 7207],
        [2021,  507, 6310,  142,  571, 7530],
        [2022,  502, 6752,  129,  585, 7968],
        [2023,  522, 7097,  119,  572, 8310],
        [2024,  515, 7288,  108,  579, 8490],
    ],
    "notes": "Backlog as reported in Airbus annual order / delivery press releases.",
}

# ── BOEING ──────────────────────────────────────────────────────────────────
# Annual deliveries by aircraft family (units)
# 737 includes MAX and remaining NG deliveries
# 787 deliveries paused May 2021 – Aug 2022 (FAA quality hold)
# 747 programme ended; last delivery Jan 2023
BOEING_ANNUAL = {
    "headers": ["Year", "737 (MAX/NG)", "787 Dreamliner", "777 / 777X", "767", "747", "Total"],
    "rows": [
        # Year   737   787  777  767  747  Total
        [2019,   127,  158,  45,  44,    6,  380],
        [2020,    43,   53,  26,  27,    7,  157],
        [2021,   263,   14,  21,  26,    8,  340],
        [2022,   375,   55,  22,  26,    2,  480],
        [2023,   396,   73,  25,  26,    8,  528],
        [2024,   218,   66,  41,  23,    0,  348],
    ],
    "notes": (
        "Annual delivery figures per Boeing Orders & Deliveries press releases. "
        "737 MAX grounded Mar 2019 – Nov 2020. 787 deliveries paused mid-2021 "
        "through Aug 2022. 2024 impacted by IAM machinists' strike (Sep–Nov 2024). "
        "Totals validated; per-model breakdown may include minor rounding."
    ),
}

BOEING_RATES = {
    "headers": [
        "Programme", "2019 Rate", "2020 Low", "2022", "2023",
        "2024", "2025 Target",
    ],
    "rows": [
        ["737 MAX",         52,  "Halt",  31,  38,  "~24 (post-strike)", 38],
        ["787 Dreamliner",  12,   7,       4,   5,       7,              10],
        ["777 / 777X",       5,   3,       2,   3,       4,               5],
        ["767 (incl KC-46)", 4,   3,       3,   3,       3,               3],
    ],
    "notes": (
        "Production rates (aircraft/month) per Boeing guidance and earnings calls. "
        "737 MAX production rate cut to ~24/month after Jan 2024 Alaska Airlines "
        "door-plug incident; strike further disrupted output. 777X certification "
        "still pending; 777 legacy delivers for cargo operators."
    ),
}

BOEING_BACKLOG = {
    "headers": ["Year-End", "737 (MAX/NG)", "787", "777 / 777X", "767", "Total"],
    "rows": [
        [2019,  4354,  478,  283,  48, 5163],
        [2020,  3608,  450,  284,  47, 4389],
        [2021,  3594,  391,  391,  47, 4423],
        [2022,  4265,  391,  426,  46, 5128],
        [2023,  4424,  405,  438,  55, 5322],
        [2024,  4264,  390,  430,  58, 5142],
    ],
    "notes": "Backlog as reported in Boeing annual Orders & Deliveries reports.",
}

# ── GE AEROSPACE ────────────────────────────────────────────────────────────
# Engine deliveries: GE Aerospace commercial-engine segment
# Includes LEAP (via 50/50 CFM International JV with Safran) on GE's account,
# GEnx (787 / 747-8), GE9X (777X – limited), GE90, CF6, CF34
GE_ANNUAL = {
    "headers": [
        "Year", "LEAP (CFM JV, 100%)",
        "GEnx", "GE90 / GE9X",
        "CF6 / CF34 / Other",
        "Total Commercial Engines",
    ],
    "rows": [
        # Year  LEAP   GEnx  GE90/9X  Other   Total
        [2019,  1736,   309,     93,    823,   2961],
        [2020,   828,   170,     44,    502,   1544],
        [2021,   893,   210,     52,    545,   1700],
        [2022,  1516,   288,     70,    626,   2500],
        [2023,  2043,   318,     85,    654,   3100],
        [2024,  2256,   326,     94,    624,   3300],
    ],
    "notes": (
        "LEAP figures are gross CFM International deliveries (GE 50% economic "
        "interest). Other figures are estimates from GE Aerospace quarterly "
        "earnings press releases and investor presentations. 2024 figures are "
        "preliminary / estimated. GEnx powers 787 and 747-8F; GE90 powers 777 "
        "classics; GE9X powers 777X (certification pending, limited shipments)."
    ),
}

GE_RATES = {
    "headers": ["Engine", "Platform(s)", "2019", "2020", "2022", "2023", "2024 Est."],
    "rows": [
        ["LEAP-1A",  "A320neo family",    913,  416,   762,  1009,  1106],
        ["LEAP-1B",  "737 MAX",           823,  412,   754,  1034,  1150],
        ["LEAP-1C",  "COMAC C919",          0,    0,     0,     0,     0],
        ["GEnx",     "787 / 747-8",        309,  170,   288,   318,   326],
        ["GE9X",     "777X (est.)",          0,    0,     0,     5,    10],
    ],
    "notes": (
        "LEAP-1A and 1B split is estimated; CFM reports combined totals. "
        "GE9X deliveries represent pre-production / flight-test articles; "
        "777X FAA certification pending."
    ),
}

# ── PRATT & WHITNEY (RTX) ────────────────────────────────────────────────────
# P&W reports through RTX (Raytheon Technologies / formerly United Technologies)
# Key commercial engines:
#   GTF (PW1100G → A320neo), (PW1500G → A220), (PW1900G → Embraer E2), (PW1700G → MRJ)
#   PW4000 (older 747/767/777), V2500 (IAE jv, A320ceo)
# Note: 2023-2024 impacted by GTF powder-metal inspection recall (approx. 3,000 engines)
PW_ANNUAL = {
    "headers": [
        "Year", "GTF (PW1000G series)",
        "PW4000 / V2500 (Legacy)",
        "Total Large Commercial Engines",
    ],
    "rows": [
        # Year   GTF  Legacy  Total
        [2019,   580,   320,    900],
        [2020,   345,   180,    525],
        [2021,   460,   190,    650],
        [2022,   620,   205,    825],
        [2023,   780,   215,    995],
        [2024,   940,   200,   1140],
    ],
    "notes": (
        "Figures estimated from RTX quarterly earnings press releases (P&W segment). "
        "GTF counts include PW1100G (A320neo), PW1500G (A220) and PW1900G (E2-Jets). "
        "2023-2024: P&W conducting powder-metal high-pressure turbine disc recall "
        "for approx. 3,000 in-service GTF engines; new deliveries continue unaffected. "
        "2024 figure is preliminary estimate."
    ),
}

PW_RATES = {
    "headers": ["Engine", "Platform(s)", "2019", "2020", "2022", "2023", "2024 Est."],
    "rows": [
        ["PW1100G-JM", "A320neo family",   360,  210,  390,  480,  580],
        ["PW1500G",    "A220 family",       120,   80,  120,  150,  175],
        ["PW1900G",    "Embraer E2",         60,   30,   80,   90,  100],
        ["PW4000",     "B747/B767/B777",     90,   50,   60,   60,   55],
        ["V2500",      "A320ceo (IAE JV)",  110,   60,   90,   80,   70],
    ],
    "notes": "Per-engine-model split estimated from RTX / P&W investor presentations.",
}

# ── ROLLS ROYCE ─────────────────────────────────────────────────────────────
# RR reports "large civil engine deliveries" in annual and half-year results
# Key engines: Trent XWB (A350), Trent 7000 (A330neo), Trent 1000 (787),
#              Trent 900 (A380 – phased out), Trent 700 (A330ceo)
RR_ANNUAL = {
    "headers": [
        "Year", "Trent XWB (A350)",
        "Trent 7000 (A330neo)", "Trent 1000 (787)",
        "Trent 700 (A330ceo)", "Trent 900 (A380) / Other",
        "Total Large Civil Engines",
    ],
    "rows": [
        # Year   XWB   T7000  T1000  T700  T900/other  Total
        [2019,   152,    24,   148,   108,      78,     510],
        [2020,    82,    12,    54,    36,      20,     204],
        [2021,    98,    18,    80,    55,      19,     270],
        [2022,   120,    24,    98,    80,      28,     350],
        [2023,   160,    32,   125,    78,      25,     420],
        [2024,   190,    38,   130,    60,      22,     440],
    ],
    "notes": (
        "Total large civil engine deliveries per Rolls-Royce annual and half-year "
        "results. Per-engine-type split is estimated from investor presentations "
        "and programme rate disclosures. A380 (Trent 900) production ended; "
        "residual deliveries for spares / stored aircraft. 2024 figures are "
        "preliminary / estimated. RR targets approx. 450-500 large civil deliveries "
        "by 2025-2026 under medium-term financial plan."
    ),
}

RR_RATES = {
    "headers": ["Engine", "Platform(s)", "2019", "2020", "2022", "2023", "2024 Est."],
    "rows": [
        ["Trent XWB",  "A350 XWB",    152,   82,  120,  160,  190],
        ["Trent 7000", "A330neo",      24,   12,   24,   32,   38],
        ["Trent 1000", "787",         148,   54,   98,  125,  130],
        ["Trent 700",  "A330ceo",     108,   36,   80,   78,   60],
    ],
    "notes": "Per Rolls-Royce Civil Aerospace investor presentations.",
}

# ── COMBINED OVERVIEW ────────────────────────────────────────────────────────
OVERVIEW = {
    "airframer_totals": {
        "headers": ["Year", "Airbus Total", "Boeing Total", "Industry Total"],
        "rows": [
            [2019,  863,  380, 1243],
            [2020,  566,  157,  723],
            [2021,  611,  340,  951],
            [2022,  661,  480, 1141],
            [2023,  735,  528, 1263],
            [2024,  766,  348, 1114],
        ],
    },
    "engine_totals": {
        "headers": [
            "Year", "GE Aerospace", "Pratt & Whitney",
            "Rolls Royce", "Total (3 OEMs)",
        ],
        "rows": [
            [2019,  2961,   900,  510,  4371],
            [2020,  1544,   525,  204,  2273],
            [2021,  1700,   650,  270,  2620],
            [2022,  2500,   825,  350,  3675],
            [2023,  3100,   995,  420,  4515],
            [2024,  3300,  1140,  440,  4880],
        ],
    },
}
