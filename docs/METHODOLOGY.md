# Methodology & Metric Definitions

## Primary analytical population

- **Survey:** MBIE International Visitor Survey (IVS) Q2 2026 downloadable microdata.
- **Main period:** 1 July 2025–30 June 2026 (2025 Q3–Q4 and 2026 Q1–Q2).
- **Source markets:** Australia; China, People's Republic of; United States of America.
- **Observed respondents:** 2,496; 714; 575, respectively.
- **Primary visitor key:** `response_id`; physically verified in original CSVs, unique and non-null in the header.
- **Main table:** `views/survey_main_header.csv` (36,563 rows across the archive).
- **Spend details:** `views/expenditure_by_industry.csv` in the **actual uploaded ZIP** (36,563 rows). The live MBIE web description calls this `expenditure_by_product.csv`; the pipeline follows the actual archive's filename.

## Principal metrics

Let respondent *i* have survey population weight \(w_i\), treated NZ expenditure \(s_i\), length of stay in days \(d_i\).

| Name | Formula | Interpretation |
|---|---|---|
| **Estimated total visitor spend** | \(\sum_i w_i s_i\) | Estimated total in-NZ tourist expenditure (nominal NZD) |
| **Mean total spend per visit** | \(\sum_i w_i s_i/\sum_i w_i\) | Weighted per-visitor visit expenditure |
| **Mean daily spend per visitor** | \(\sum_i w_i(s_i/d_i)/\sum_i w_i\) | Weighted mean of individual daily spending amounts |
| **Mean length of stay** | \(\sum_i w_i d_i/\sum_i w_i\) | Weighted mean days in NZ |
| **IVS estimated visitor population** | \(\sum_i w_i\) | Population estimate for IVS eligible respondents, **not Stats NZ border arrivals** |
| **Purpose mix** | \(\sum_{i\in purpose} w_i/\sum_{i\in market}w_i\) | Share by main travel purpose |
| **First-time vs repeat mix** | Weighted fraction with `first_nz_trip = Yes` / `No` | Estimates of first/returning proportions |
| **Spend-category share** | \(\sum_i w_i c_i/\sum_i w_i s_i\) | Category proportion of estimated spend |
| **Category spend per visitor** | \(\sum_i w_i c_i/\sum_i w_i\) | Average across **all visitors**, including category nonbuyers |

The previously explored **pooled spend per visitor-day** \(\sum_i w_i s_i / \sum_i w_i d_i\) is mathematically valid but a **different measure**, and is **not used in main charts**. Neither metric is an inflation adjustment.

## Expenditure categories used

| Label | Physical CSV fields |
|---|---|
| Accommodation | `cost_accomm` |
| Food & dining | `cost_food_drink`, `cost_eating_out` |
| Transport in NZ | `cost_dom_travel`, `cost_dom_flights`, `cost_car_rentals` |
| Activities & cruises | `cost_entertainment`, `cost_day_cruise` |
| Shopping | `cost_shopping` |
| Tour packages | `cost_tour_package` |
| Other | `cost_other` |

These non-overlapping fields reconcile with `treated_spend` at respondent level to floating-point precision. Columns with `exc_` prefixes and foreign/international-airfare costs are excluded. `cost_tour_package` is not assumed to represent a separate itinerary style, and its value is **not redistributed** across accommodation, food, domestic travel or activities. The `Other` category is not interpreted as a coherent product opportunity.

## VEM (Visitor Experience Module)

Multiple-response transport and accommodation *use* comes from VEM and requires `vem_pop_weight`, not `population_weight`. A respondent may report multiple transport/accommodation methods, so participation shares across methods need not sum to 100%. Small subgroups are not ranked as if precise.

## Statistical uncertainty and comparisons

- The IVS is a sampled survey; **population-weighted estimates do not eliminate sampling or nonresponse error**.
- MBIE's published expenditure RMEs for YE June 2026 are **Australia 6.9%, China 11.4%, US 12.4%**. These are not custom RMEs for our segmented estimates.
- The project suppresses purpose bubbles with **unweighted sample n < 30**. This is an *editorial display rule*, not an official MBIE reliability cutoff or a confidence interval.
- The portfolio does **not** compute survey-design replicate-weight bootstrap confidence intervals, and thus does not imply formal significance of close market differences.
- Purpose and repeat-visitor associations **do not imply causality**. For example, Australian return visitors' lower spending could reflect both visit purpose and other characteristics.
- Source-market and period comparisons must account for different survey weighting/calibration across previous releases, especially MBIE's 2024 China recalibration.
- **No market-level regional spending** is estimated from IVS; data only support travel behaviour and visitor nights by region (not developed in this release).
- **No individual income field** exists in the downloaded microdata; spend cannot be mapped to a home-country income percentile.

## Separate historical context

The historical panel uses **published Stats NZ / MBIE arrival indicators**, *not* IVS survey weights. The available confirmed comparison is all markets in YE June 2019/2026 and Australia/US published recovery percentages. An exact same-period China 2019 ratio and full market-level monthly arrival series remain an explicitly documented follow-up.