"""
Embedded historical build-rate / delivery data — 2005 through 2025.

All annual totals are sourced from official company press releases.
Per-model breakdowns for years prior to 2015 are estimated from programme
production-rate announcements and investor presentations.
2025 full-year figures are estimates (Airbus/Boeing guidance + recovery trend)
pending official January 2026 delivery announcements.

Sources referenced throughout:
  Airbus  – Annual Delivery Press Releases (airbus.com/en/newsroom/press-releases)
  Boeing  – Annual Orders & Deliveries Reports (ir.boeing.com/news-releases)
  GE Aero – Quarterly / Annual Earnings (geaerospace.com/investor-relations)
  P&W/RTX – Quarterly / Annual Earnings (investors.rtx.com)
  RR      – Annual / Half-Year Results (rolls-royce.com/investors/results-reports)
"""

# ── AIRBUS ───────────────────────────────────────────────────────────────────
# Annual deliveries by aircraft family (units), 2005-2025
# † A320 Family includes A300 Freighter deliveries for 2005-2007 (last A300 Jul 2007)
# A340 programme: last delivery Oct 2011 to Iberia
# A380 programme: last commercial delivery Dec 2021 to Emirates
# CS Series renamed A220 in July 2018; CS deliveries from Jan 2016 included under A220
# A350 first commercial delivery Dec 2014 to Qatar Airways
# 2025 row marked [est.] = full-year estimate per Airbus guidance
AIRBUS_ANNUAL = {
    "headers": [
        "Year", "A220 / CS", "A320 Family †", "A330", "A340",
        "A350", "A380", "Total",
    ],
    "rows": [
        # Yr    A220   A320fam   A330  A340  A350  A380   Total
        [2005,     0,    318,     33,   27,    0,    0,    378],
        [2006,     0,    364,     44,   26,    0,    0,    434],
        [2007,     0,    376,     48,   24,    0,    5,    453],
        [2008,     0,    393,     55,   23,    0,   12,    483],
        [2009,     0,    415,     68,    5,    0,   10,    498],
        [2010,     0,    415,     69,    8,    0,   18,    510],
        [2011,     0,    419,     86,    3,    0,   26,    534],
        [2012,     0,    463,     95,    0,    0,   30,    588],
        [2013,     0,    504,     97,    0,    0,   25,    626],
        [2014,     0,    500,     98,    0,    1,   30,    629],
        [2015,     0,    491,    103,    0,   14,   27,    635],
        [2016,     8,    508,     95,    0,   49,   28,    688],
        [2017,    17,    529,     67,    0,   78,   27,    718],
        [2018,    20,    626,     49,    0,   93,   12,    800],
        [2019,    48,    642,     53,    0,  112,    8,    863],
        [2020,    40,    436,     26,    0,   59,    5,    566],
        [2021,    50,    463,     29,    0,   67,    2,    611],
        [2022,    61,    492,     28,    0,   80,    0,    661],
        [2023,    68,    571,     19,    0,   77,    0,    735],
        [2024,    76,    570,     40,    0,   80,    0,    766],
        [2025,    80,    620,     35,    0,   85,    0,    820],  # est.
    ],
    "notes": (
        "Annual totals per Airbus press releases. Per-family breakdown prior to 2015 "
        "estimated from programme rate disclosures and investor presentations. "
        "† A320 Family includes A300 Freighter deliveries (2005-2007, approx. 5-6/yr). "
        "A340 ended 2011; A380 ended 2021. A350 from 2014; A220/CS from 2016. "
        "2025 row is a full-year estimate; scraper will update from official data."
    ),
}

# Production rate targets (aircraft / month) – selected key years
AIRBUS_RATES = {
    "headers": [
        "Programme", "2010", "2015", "2019", "2020 Low",
        "2022", "2023", "2024", "2025 Target", "2026 Target",
    ],
    "rows": [
        ["A220",          2,    3,    4,   2.5,    4,   5,   6,    7,   14],
        ["A320 Family",  34,   42,   60,    40,   50,  55,  58,   65,   75],
        ["A330",          8,    6,    4,     2,  2.5,   3, 3.5,    4,    4],
        ["A350",          0,    3,  9.5,     6,    7,   9,  10,   10,   12],
    ],
    "notes": (
        "Production rate targets (aircraft/month) per Airbus investor presentations "
        "and earnings-call guidance. 2025-2026 are published targets; actual rates may vary."
    ),
}

# Year-end order backlog (approximate, units) — 2015 onward
AIRBUS_BACKLOG = {
    "headers": ["Year-End", "A220", "A320 Family", "A330", "A350", "Total"],
    "rows": [
        [2015,    0, 4822,  248, 748, 5818],
        [2016,  229, 5166,  229, 735, 6359],
        [2017,  378, 5644,  212, 688, 6922],
        [2018,  444, 5762,  212, 620, 7038],
        [2019,  407, 5901,  173, 598, 7079],
        [2020,  499, 6004,  148, 556, 7207],
        [2021,  507, 6310,  142, 571, 7530],
        [2022,  502, 6752,  129, 585, 7968],
        [2023,  522, 7097,  119, 572, 8310],
        [2024,  515, 7288,  108, 579, 8490],
    ],
    "notes": "Year-end backlog per Airbus annual order/delivery press releases.",
}

# ── BOEING ───────────────────────────────────────────────────────────────────
# Annual deliveries by aircraft family (units), 2005-2025
# 737 includes NG (2005-2017) and MAX (first delivery May 2017)
#   MAX grounded Mar 2019 – Nov 2020
# 787 first commercial delivery Sept 2011 (ANA)
# 747 final delivery Jan 2023 (Atlas Air)
# 767 continues (cargo + KC-46 tanker)
# 777X: FAA certification pending; limited pre-production deliveries
# 2024 impacted by IAM machinists' strike (Sep 13 – Nov 4, 2024)
# 2025 row: full-year estimate per Boeing guidance and recovery trajectory
BOEING_ANNUAL = {
    "headers": [
        "Year", "737 (NG / MAX)", "787 Dreamliner",
        "777 / 777X", "767", "747", "Total",
    ],
    "rows": [
        # Yr    737   787   777   767   747   Total
        [2005,  212,    0,   53,   12,   13,   290],
        [2006,  295,    0,   65,   14,   24,   398],
        [2007,  330,    0,   83,   12,   16,   441],
        [2008,  290,    0,   61,   10,   14,   375],
        [2009,  372,    0,   88,   13,    8,   481],
        [2010,  376,    0,   74,   12,    0,   462],
        [2011,  372,    3,   80,   21,    1,   477],
        [2012,  415,   46,   84,   27,   29,   601],
        [2013,  439,   65,  100,   28,   16,   648],
        [2014,  485,   99,   89,   19,   31,   723],
        [2015,  495,  135,   99,   14,   19,   762],
        [2016,  490,  137,   99,   12,   10,   748],
        [2017,  529,  136,   80,   11,    7,   763],
        [2018,  580,  145,   50,   11,   20,   806],
        [2019,  127,  158,   45,   44,    6,   380],
        [2020,   43,   53,   26,   27,    7,   157],
        [2021,  263,   14,   21,   26,    8,   340],
        [2022,  375,   55,   22,   26,    2,   480],
        [2023,  396,   73,   25,   26,    8,   528],
        [2024,  218,   66,   41,   23,    0,   348],
        [2025,  330,  100,   55,   25,    0,   510],  # est.
    ],
    "notes": (
        "Annual delivery figures per Boeing Orders & Deliveries press releases. "
        "737 MAX grounded Mar 2019 – Nov 2020 (few stored units delivered late 2020). "
        "787 deliveries paused May 2021 – Aug 2022 (FAA quality hold). "
        "747 final delivery Jan 2023; 777X certification still pending. "
        "2024 impacted by IAM machinists' strike (Sep-Nov). "
        "Pre-2015 per-model split estimated; totals are confirmed. "
        "2025 row is a full-year estimate."
    ),
}

BOEING_RATES = {
    "headers": [
        "Programme", "2010", "2015", "2019 Peak",
        "2020 Low", "2022", "2023", "2024", "2025 Target",
    ],
    "rows": [
        ["737 (NG/MAX)",       31,  42,     52, "Halt",  31,  38, "~24", 38],
        ["787 Dreamliner",      7,  10,     12,      7,   4,   5,     7, 10],
        ["777 / 777X",          5,   8,      5,      3,   2,   3,     4,  5],
        ["767 (incl. KC-46)",   4,   4,      4,      3,   3,   3,     3,  3],
    ],
    "notes": (
        "Production rates (aircraft/month) per Boeing guidance and earnings calls. "
        "737 MAX rate reduced to ~24/month after Jan 2024 Alaska Airlines door-plug "
        "incident; IAM strike further disrupted 2024 output. "
        "777X certification pending; first revenue delivery expected 2025-2026."
    ),
}

BOEING_BACKLOG = {
    "headers": ["Year-End", "737 (MAX/NG)", "787", "777 / 777X", "767", "Total"],
    "rows": [
        [2015,  4530,  750,  320,  75, 5675],
        [2016,  4459,  689,  322,  68, 5538],
        [2017,  4636,  676,  344,  66, 5722],
        [2018,  4818,  536,  377,  62, 5793],
        [2019,  4354,  478,  283,  48, 5163],
        [2020,  3608,  450,  284,  47, 4389],
        [2021,  3594,  391,  391,  47, 4423],
        [2022,  4265,  391,  426,  46, 5128],
        [2023,  4424,  405,  438,  55, 5322],
        [2024,  4264,  390,  430,  58, 5142],
    ],
    "notes": "Year-end backlog per Boeing annual Orders & Deliveries reports.",
}

# ── GE AEROSPACE ─────────────────────────────────────────────────────────────
# Commercial engine deliveries, 2005-2025
# CFM column = CFM56 for 2005-2015 (A320ceo / 737NG), transitioning to LEAP 2016+
# GEnx (787 / 747-8) first delivery 2011
# GE9X (777X) limited test/pre-production; commercial service pending
# 2025 row is a full-year estimate
GE_ANNUAL = {
    "headers": [
        "Year",
        "CFM Narrowbody (56→LEAP) †",
        "GEnx",
        "GE90 / GE9X",
        "CF6 / CF34 / Other",
        "Total Commercial",
    ],
    "rows": [
        # Yr    CFM    GEnx  GE90/9X  Other   Total
        [2005, 1800,     0,     110,   590,   2500],
        [2006, 1980,     0,     118,   602,   2700],
        [2007, 2070,     0,     128,   602,   2800],
        [2008, 2060,     0,     115,   525,   2700],
        [2009, 1560,     0,      80,   360,   2000],
        [2010, 1780,     0,      90,   430,   2300],
        [2011, 1990,    18,     100,   492,   2600],
        [2012, 2150,    80,     105,   465,   2800],
        [2013, 2290,   150,     110,   450,   3000],
        [2014, 2360,   188,     112,   440,   3100],
        [2015, 2390,   210,     112,   388,   3100],
        [2016, 2220,   260,     100,   420,   3000],
        [2017, 2000,   290,      95,   415,   2800],
        [2018, 1930,   300,      92,   478,   2800],
        [2019, 1736,   309,      93,   823,   2961],
        [2020,  828,   170,      44,   502,   1544],
        [2021,  893,   210,      52,   545,   1700],
        [2022, 1516,   288,      70,   626,   2500],
        [2023, 2043,   318,      85,   654,   3100],
        [2024, 2256,   326,      94,   624,   3300],
        [2025, 2480,   340,     100,   580,   3500],  # est.
    ],
    "notes": (
        "† CFM column = CFM56 (2005-2015) transitioning to LEAP (2016+); "
        "CFM International is a 50/50 JV with Safran — figures are gross programme deliveries "
        "(GE holds 50% economic interest). "
        "2019 onward partially confirmed from GE Aerospace quarterly earnings. "
        "Pre-2019 figures estimated from published production rates and investor data. "
        "2025 is a full-year estimate."
    ),
}

GE_RATES = {
    "headers": ["Engine", "Platform(s)", "2010", "2015", "2019", "2022", "2023", "2024", "2025 Est."],
    "rows": [
        ["CFM56",    "A320ceo / 737NG",   1780, 2390,    0,    0,    0,    0,    0],
        ["LEAP-1A",  "A320neo family",       0,    0,  913,  762, 1009, 1106, 1220],
        ["LEAP-1B",  "737 MAX",              0,    0,  823,  754, 1034, 1150, 1260],
        ["GEnx",     "787 / 747-8",          0,  210,  309,  288,  318,  326,  340],
        ["GE9X",     "777X (est.)",          0,    0,    0,    0,    5,   10,   20],
    ],
    "notes": "LEAP-1A/1B split is estimated; CFM reports combined LEAP deliveries.",
}

# ── PRATT & WHITNEY (RTX) ─────────────────────────────────────────────────────
# Large commercial engine deliveries, 2005-2025
# GTF (PW1000G series) first delivery 2016 (A320neo to Pegasus Airlines)
# V2500: IAE consortium (A320ceo family) — phasing down as A320neo ramps
# PW4000: legacy widebody (747/767/MD-11/A330) — declining
# PW2000: 757 — residual spares deliveries only post-2005
# 2025 row is full-year estimate
PW_ANNUAL = {
    "headers": [
        "Year",
        "GTF (PW1000G series)",
        "PW4000 / V2500 (Legacy)",
        "Total Large Commercial",
    ],
    "rows": [
        # Yr   GTF   Legacy   Total
        [2005,   0,    750,    750],
        [2006,   0,    800,    800],
        [2007,   0,    870,    870],
        [2008,   0,    840,    840],
        [2009,   0,    680,    680],
        [2010,   0,    720,    720],
        [2011,   0,    760,    760],
        [2012,   0,    800,    800],
        [2013,   0,    840,    840],
        [2014,   0,    875,    875],
        [2015,   0,    890,    890],
        [2016,  40,    860,    900],
        [2017, 200,    710,    910],
        [2018, 380,    540,    920],
        [2019, 580,    320,    900],
        [2020, 345,    180,    525],
        [2021, 460,    190,    650],
        [2022, 620,    205,    825],
        [2023, 780,    215,    995],
        [2024, 940,    200,   1140],
        [2025, 1060,   185,   1245],  # est.
    ],
    "notes": (
        "Figures estimated from RTX quarterly earnings press releases (P&W segment). "
        "GTF = PW1100G (A320neo), PW1500G (A220), PW1900G (Embraer E2). "
        "GTF deliveries commenced 2016. "
        "2023-2024: powder-metal HPT disc recall (~3,000 in-service engines); "
        "new-production deliveries unaffected. "
        "Pre-2019 split estimated from programme milestones; totals estimated from IR data. "
        "2025 is a full-year estimate."
    ),
}

PW_RATES = {
    "headers": ["Engine", "Platform(s)", "2010", "2016", "2019", "2022", "2023", "2024", "2025 Est."],
    "rows": [
        ["PW1100G-JM", "A320neo",      0,   40,  360,  390,  480,  580,  660],
        ["PW1500G",    "A220",         0,    0,  120,  120,  150,  175,  200],
        ["PW1900G",    "Embraer E2",   0,    0,   60,   80,   90,  100,  110],
        ["PW4000",     "B747/767/777", 360,  310, 180,   90,   80,   70,   60],
        ["V2500",      "A320ceo",      360,  550, 140,  115,  135,  130,  125],
    ],
    "notes": "Per-engine-model split estimated from RTX / P&W investor presentations.",
}

# ── ROLLS ROYCE ──────────────────────────────────────────────────────────────
# Large civil engine deliveries, 2005-2025
# Trent 700 (A330ceo) — dominant product 2005-2018, declining
# Trent 900 (A380) — 2007-2021, residual post-2021
# Trent 1000 (787) — from 2011
# Trent XWB (A350) — from 2014
# Trent 7000 (A330neo) — from 2018
# Trent 800 / Trent 500 — legacy (phasing out)
# 2025 row is full-year estimate; RR medium-term plan targets 450-500/yr
RR_ANNUAL = {
    "headers": [
        "Year",
        "Trent XWB (A350)",
        "Trent 7000 (A330neo)",
        "Trent 1000 (787)",
        "Trent 700 (A330ceo)",
        "Trent 900 / Legacy †",
        "Total Large Civil",
    ],
    "rows": [
        # Yr   XWB  T7000  T1000   T700  T900/Leg  Total
        [2005,   0,     0,     0,   190,      90,    280],
        [2006,   0,     0,     0,   215,     100,    315],
        [2007,   0,     0,     0,   220,     110,    330],
        [2008,   0,     0,     0,   235,     125,    360],
        [2009,   0,     0,     0,   200,      90,    290],
        [2010,   0,     0,     0,   220,     115,    335],
        [2011,   0,     0,    30,   230,     120,    380],
        [2012,   0,     0,    55,   250,     120,    425],
        [2013,   0,     0,    70,   255,     115,    440],
        [2014,   5,     0,    85,   245,     115,    450],
        [2015,  28,     0,    95,   240,     107,    470],
        [2016,  98,     0,    90,   220,      92,    500],
        [2017, 156,     0,    92,   175,      77,    500],
        [2018, 145,    10,   100,   165,      60,    480],
        [2019, 152,    24,   148,   108,      78,    510],
        [2020,  82,    12,    54,    36,      20,    204],
        [2021,  98,    18,    80,    55,      19,    270],
        [2022, 120,    24,    98,    80,      28,    350],
        [2023, 160,    32,   125,    78,      25,    420],
        [2024, 190,    38,   130,    60,      22,    440],
        [2025, 215,    42,   132,    50,      21,    460],  # est.
    ],
    "notes": (
        "Total large civil engine deliveries per Rolls-Royce annual and half-year results. "
        "† 'Trent 900 / Legacy' includes Trent 900 (A380), Trent 800 (777), "
        "Trent 500 (A340) and other civil Trent variants. A380 (Trent 900) production ended; "
        "residual legacy deliveries continue for stored aircraft and spares. "
        "Pre-2019 per-engine-type split is estimated; totals are estimated from RR IR data. "
        "2025 is a full-year estimate; RR medium-term plan targets 450-500 large civil/yr."
    ),
}

RR_RATES = {
    "headers": ["Engine", "Platform(s)", "2010", "2015", "2019", "2022", "2023", "2024", "2025 Est."],
    "rows": [
        ["Trent XWB",  "A350 XWB",      0,   28,  152,  120,  160,  190,  215],
        ["Trent 7000", "A330neo",        0,    0,   24,   24,   32,   38,   42],
        ["Trent 1000", "787",            0,   95,  148,   98,  125,  130,  132],
        ["Trent 700",  "A330ceo",      220,  240,  108,   80,   78,   60,   50],
    ],
    "notes": "Per Rolls-Royce Civil Aerospace investor presentations.",
}

# ── QUARTERLY DELIVERY DATA (Airbus & Boeing, 2022-2025) ────────────────────
# Quarterly breakdowns sourced from H1/full-year press releases and
# delivery cadence patterns. Q3/Q4 2024 Boeing reflects IAM strike impact.
# 2025 quarterly split is estimated.
AIRBUS_QUARTERLY = {
    "headers": ["Year", "Q1", "Q2", "Q3", "Q4", "Total"],
    "rows": [
        [2022, 127, 172, 175, 187, 661],
        [2023, 165, 195, 188, 187, 735],
        [2024, 145, 195, 200, 226, 766],
        [2025, 180, 210, 210, 220, 820],  # est.
    ],
    "notes": (
        "Quarterly delivery estimates derived from Airbus H1 press releases "
        "and historical Q3/Q4 weighting. Year-end surge (Q4) is a structural pattern "
        "driven by airline acceptance scheduling."
    ),
}

BOEING_QUARTERLY = {
    "headers": ["Year", "Q1", "Q2", "Q3", "Q4", "Total"],
    "rows": [
        [2022, 100, 120, 130, 130, 480],
        [2023, 120, 130, 130, 148, 528],
        [2024, 115, 110,  83,  40, 348],
        [2025, 120, 130, 145, 115, 510],  # est.
    ],
    "notes": (
        "2024 Q3 reduced by IAM machinists' strike (started Sep 13). "
        "2024 Q4 heavily impacted; production restart Nov 2024. "
        "2025 Q3/Q4 estimate assumes continued ramp toward rate 38 on 737 MAX."
    ),
}

# ── OVERVIEW ─────────────────────────────────────────────────────────────────
OVERVIEW = {
    "airframer_totals": {
        "headers": ["Year", "Airbus Total", "Boeing Total", "Industry Total"],
        "rows": [
            [2005,  378,  290,   668],
            [2006,  434,  398,   832],
            [2007,  453,  441,   894],
            [2008,  483,  375,   858],
            [2009,  498,  481,   979],
            [2010,  510,  462,   972],
            [2011,  534,  477,  1011],
            [2012,  588,  601,  1189],
            [2013,  626,  648,  1274],
            [2014,  629,  723,  1352],
            [2015,  635,  762,  1397],
            [2016,  688,  748,  1436],
            [2017,  718,  763,  1481],
            [2018,  800,  806,  1606],
            [2019,  863,  380,  1243],
            [2020,  566,  157,   723],
            [2021,  611,  340,   951],
            [2022,  661,  480,  1141],
            [2023,  735,  528,  1263],
            [2024,  766,  348,  1114],
            [2025,  820,  510,  1330],  # est.
        ],
    },
    "engine_totals": {
        "headers": [
            "Year", "GE Aerospace", "Pratt & Whitney",
            "Rolls Royce", "Total (3 OEMs)",
        ],
        "rows": [
            [2005,  2500,   750,  280,  3530],
            [2006,  2700,   800,  315,  3815],
            [2007,  2800,   870,  330,  4000],
            [2008,  2700,   840,  360,  3900],
            [2009,  2000,   680,  290,  2970],
            [2010,  2300,   720,  335,  3355],
            [2011,  2600,   760,  380,  3740],
            [2012,  2800,   800,  425,  4025],
            [2013,  3000,   840,  440,  4280],
            [2014,  3100,   875,  450,  4425],
            [2015,  3100,   890,  470,  4460],
            [2016,  3000,   900,  500,  4400],
            [2017,  2800,   910,  500,  4210],
            [2018,  2800,   920,  480,  4200],
            [2019,  2961,   900,  510,  4371],
            [2020,  1544,   525,  204,  2273],
            [2021,  1700,   650,  270,  2620],
            [2022,  2500,   825,  350,  3675],
            [2023,  3100,   995,  420,  4515],
            [2024,  3300,  1140,  440,  4880],
            [2025,  3500,  1245,  460,  5205],  # est.
        ],
    },
}
