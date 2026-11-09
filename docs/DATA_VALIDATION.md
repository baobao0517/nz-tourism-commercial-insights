# Technical Validation & Reconciliation

**Input:** Actual MBIE Q2 2026 public IVS ZIP, downloaded separately by the analyst and used locally. The ZIP is **not** redistributed.

| Check | Result |
|---|---|
| CSV tables in uploaded archive | **22** |
| Main header rows (2022 Q3 to 2026 Q2) | **36,563** |
| Respondents in YE June 2026 (all countries) | **9,071** |
| Three target-market respondents | **3,785** (Australia 2,496; China 714; US 575) |
| Main `response_id` uniqueness / nulls | Unique and complete |
| Foreign keys across all 22 CSV tables | **0 orphan references** against header IDs |
| Expenditure record match in three target markets | Exactly one matched category row per main respondent |
| Treatment of included category totals | Reconciles to `treated_spend`; maximum absolute observed difference **under NZ$0.01** |
| Weight and stay validation in target cohort | Positive `population_weight` and `no_days_in_nz`; nonnegative `treated_spend` |
| Purpose/repeat weighted proportions | 100% by market (rounding excepted) |
| Python versus independently executed SQLite | 5 weighted KPIs agree across all 3 markets |
| Automated tests | 5 passed |

## Reconciliation to MBIE's published YE June 2026 top-line figures

| Region | This project's weighted microdata spend | MBIE published (rounded) | Interpretation |
|---|---:|---:|---|
| All markets | **NZ$14.315bn** | NZ$14.3bn | Consistent to published precision |
| Australia | **NZ$4.352bn** | NZ$4.4bn | Consistent to published precision; close to the rounding boundary |
| United States | **NZ$2.183bn** | NZ$2.2bn | Consistent to published precision |
| China | **NZ$1.535bn** | Not separately quoted in the Q2 top-line PDF | **No independent official market value reconciliation claimed** |

A close match to figures **rounded to 0.1bn** is not the same as exact-value reconciliation. Published RME information still applies.

## Important schema issue

The actual ZIP contains `expenditure_by_industry.csv`, whereas the MBIE live webpage currently describes `expenditure_by_product.csv`. The code reads the exact archive table encountered. No column names are inferred from the website if the ZIP disagrees.

## Interpreting duplicates and missingness

- Duplicate `response_id` values in multi-response tables (activities, itinerary, etc.) are **expected** and must not be joined directly to one-row-per-visitor expenditure before aggregation.
- A full CSV inventory with physical column names, pandas dtypes, counts, missingness indicators, exact duplicate rows and foreign-key checks is provided in `outputs/source_csv_inventory_and_quality.csv`.
- `vem_pop_weight` missingness is expected for respondents outside the optional module, not evidence that weights should be filled with zero.
- Small subgroups in activity/transport categories can have high sampling uncertainty; data are not used to infer campervan spend.

## Outstanding external checks (transparent publication limits)

1. An **exact** same-window YE June 2019 / YE June 2026 arrival series for each of Australia, China and the US is **not imported**; only verified MBIE rounded national context and published Australia/US recovery percentages appear in the current release.
2. MBIE's Q2 2026 **top-line PDF** does not give a separate China spend figure; the microdata China result is clearly identified as a weighted estimate without separate published-market reconciliation.
3. No custom replicate-weight confidence intervals for first-time/returning or holiday subgroups.

These gaps do not invalidate the descriptive IVS analysis, but they limit historical conclusions and precision.