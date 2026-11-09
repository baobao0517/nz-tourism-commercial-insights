# NZ Tourism Commercial Insights

### Visitor composition, spending behaviour and market opportunity | Year ended June 2026

**Python · SQL (SQLite) · Data validation · Survey weighting · Commercial analytics · Interactive dashboard**

> **Business question:** How should New Zealand tourism businesses tailor their products and marketing for visitors from **Australia, China and the United States**, based on market size, travel purposes, repeat visitation and spending patterns?

**Analysis period:** 1 July 2025 to 30 June 2026. **Historical context:** equivalent year ended June 2019, used as background rather than a second detailed analysis period.

[**Explore the interactive dashboard**](dashboard/index.html) · [**Executive brief**](docs/EXECUTIVE_SUMMARY.md) · [**Methods**](docs/METHODOLOGY.md) · [**Validation**](docs/DATA_VALIDATION.md) · [**Data sources**](docs/SOURCES.md)

If GitHub Pages is enabled from `/docs`, the hosted dashboard uses `docs/index.html`. Otherwise, download/open `dashboard/index.html` locally; all interactive JavaScript and charts are embedded.

---

## Executive snapshot

| Market | Survey respondents | Total estimated spend | Mean total spend / visit | Mean daily spend / visitor | Repeat visitors |
|---|---:|---:|---:|---:|---:|
| **Australia** | 2,496 | **NZ$4.35bn** | NZ$3,146 | NZ$405 | **76.1%** |
| **China** | 714 | NZ$1.54bn | NZ$5,449 | **NZ$635** | 19.6% |
| **United States** | 575 | NZ$2.18bn | **NZ$6,618** | NZ$584 | 32.8% |

*Source: MBIE International Visitor Survey Q2 2026 microdata. All metrics above are survey-weighted estimates for YE June 2026. "Mean daily" is the weighted mean of each respondent's spend divided by days in NZ; figures are nominal and exclude international airfares. Sample sizes are **unweighted respondents**, not population counts.*

### Three evidence-led insights

**1. Australia — a large market with different visitor segments.** Australia's tourism is not holiday-only: 42.6% holiday and 37.7% VFR (weighted). **76.1%** are repeat visitors, and 93.6% of Australian VFR visitors have visited New Zealand before. Australian holiday visitors spend more per visit (NZ$4,469) than the broad Australian market (NZ$3,146); treating the two as one target risks ineffective product positioning.

**2. China — first-time visitors and package/shopping spending.** **80.4%** are first-time visitors and **74.5%** are on holiday. Shopping comprises **16.4%** and tour packages **15.2%** of estimated total spending. This suggests an opportunity to test convenience-oriented bundles, shopping-linked experiences and distribution partnerships. These percentages are spending shares, not traveller participation rates.

**3. United States — greater visit spend, longer stays.** The US leads in estimated mean total spend per visit (NZ$6,618), but its mean daily spend (NZ$584) is below China's (NZ$635). US visitors spend more on average per person on accommodation and food than the other two markets; this supports testing long-stay products and experience combinations, **not** claiming US visitors have a proven higher willingness to pay.

### Visitor mix: why averages can mislead

![100 percent stacked purpose comparison](outputs/purpose_mix_100pct_stacked.png)

### Repeat visitors: market familiarity as a further segment

![First-time and repeat visit comparison](outputs/first_repeat_100pct_stacked.png)

### Spending patterns: composition is not the same as dollars per visitor

![Spending category mix across three markets, all visitors and holiday segment](outputs/spend_category_mix_100pct_stacked.png)

### Bubble chart: market size × purpose × spending

![Bubble area represents IVS weighted estimated visitor population](outputs/bubble_market_size_spend.png)

[Open interactive bubble chart with hover-level n, length of stay and spending](outputs/bubble_market_size_spend_interactive.html).

---

## Commercial recommendations to test

| Market | Suggested operator action | What to measure in a real business |
|---|---|---|
| **Australia — Volume & convenience** | Make core accommodation, dining and flexible tourism experiences easy to book; tailor by holiday/VFR and first/repeat visits | Conversion, repeat bookings, margin per trip, attach rate |
| **China — Bundles & shopping** | Test packaged experiences, suitable distribution channels and shopping-linked itineraries | Bundle conversion, activity uptake, commission-adjusted margin |
| **USA — Accommodation & experiences** | Test multi-night accommodation and experience offers, without assuming an unobserved price premium | Length of stay, extra activity bookings, contribution margin |

These are **testable commercial hypotheses**, not outcomes backed by company pricing, cost-of-acquisition or profit data. Full commentary: [`docs/EXECUTIVE_SUMMARY.md`](docs/EXECUTIVE_SUMMARY.md).

---

## Historical context (one concise reference)

The September 2026 MBIE release reports **3.67 million overseas visitor arrivals in YE June 2026**, compared with **3.89 million in YE June 2019**, a **94%** national recovery. Australia and the US were each approximately **105% of YE June 2019**. **China's exact same-window 2019 recovery percentage is not independently verified** here, so the project deliberately leaves it blank.

**Important:** These are published Stats NZ / MBIE border-arrival comparisons. They are not derived by summing IVS sample weights, which represent a different survey population. Source: [MBIE Q2 2026 top-line publication](https://teic.mbie.govt.nz/assets/ivs/2026Q2%20IVS%20Top-line%20results.pdf) and [MBIE release materials](https://www.mbie.govt.nz/immigration-and-tourism/tourism-research-and-data/tourism-data-releases/international-visitor-survey-ivs/international-visitor-survey-data-release-materials).

---

## Reproduce the analysis

### 1 · Download official public microdata

Use [MBIE's official data download page](https://www.mbie.govt.nz/immigration-and-tourism/tourism-research-and-data/tourism-data-releases/international-visitor-survey-ivs/international-visitor-survey-data-download) to obtain **International Visitor Survey — Quarter 2 2026** (Q3 2022–Q2 2026, ZIP). The original ZIP is deliberately **not committed to this repository**. The actual archive table is named `expenditure_by_industry.csv` even though the MBIE live webpage describes `expenditure_by_product.csv`.

### 2 · Install and run

```bash
pip install -r requirements.txt
python src/build_portfolio.py /path/to/international-visitor-survey-data-quarter-2-2026.zip
python src/verify_sql.py /path/to/international-visitor-survey-data-quarter-2-2026.zip
python src/build_dashboard.py
python -m pytest -q
```

Outputs are written to `outputs/`, and the self-contained interactive dashboard to both `dashboard/index.html` and `docs/index.html` (for GitHub Pages). No visitor-level rows are embedded in either HTML report or the aggregated CSV outputs.

### 3 · Repository structure

```text
nz-tourism-commercial-insights/
├── README.md
├── dashboard/index.html         # Portable interactive dashboard
├── docs/
│   ├── index.html               # GitHub Pages-ready copy
│   ├── EXECUTIVE_SUMMARY.md
│   ├── METHODOLOGY.md
│   ├── DATA_VALIDATION.md
│   ├── SOURCES.md
│   └── GITHUB_PUBLISHING.md
├── src/
│   ├── build_portfolio.py       # Weighted Python analytics + QA
│   ├── verify_sql.py            # Independent SQL cross-check
│   └── build_dashboard.py       # Offline HTML dashboard
├── sql/market_analytics.sql
├── tests/test_outputs.py
├── data/README.md               # Source/data license guidance
├── outputs/                     # Aggregates, figures, QA evidence
├── .gitignore
└── requirements.txt
```

---

## Verification and important limitations

- **22** actual CSVs inspected; **36,563** source header rows; **9,071** year-ended June 2026 respondents (all origins); **3,785** respondents across three target markets.
- Main `response_id` is unique, all 22 CSV tables have no respondent keys outside the main header, and included expenditure components reconcile to `treated_spend`.
- **Published spending reconciliation:** project estimates NZ$14.315bn for all markets, NZ$4.352bn for Australia and NZ$2.183bn for the US; these agree with MBIE's **rounded** official figures of NZ$14.3bn, NZ$4.4bn and NZ$2.2bn.
- Independent SQLite query and Python agree on five weighted market KPIs; **five automated tests pass**.
- IVS survey expenditure RMEs for YE June 2026 (MBIE): Australia **6.9%**, China **11.4%**, USA **12.4%**. No custom survey-design confidence intervals were calculated for smaller groups. A bubble cell requires at least **30 unweighted respondents** to be plotted; this is a presentation convention rather than an official reliability threshold.
- International airfare is excluded. Tour packages are not assumed to be an additional spend on top of their underlying individual components. `Other` is not overinterpreted.
- No causal or profitability inference, no inferred visitor income percentiles and **no IVS regional spending estimate**.
- Further historical series work (in particular China's exact 2019 recovery percentage) remains documented as a transparent enhancement rather than fabricated in V1.0.

Read [`docs/DATA_VALIDATION.md`](docs/DATA_VALIDATION.md) and [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) for precise calculations, data-quality checks and caveats.

---

**Portfolio context:** An independent applied analytics case study designed to illustrate reproducible Python/SQL analysis, statistical judgement, stakeholder-oriented reporting and commercial recommendation framing using official New Zealand public datasets.