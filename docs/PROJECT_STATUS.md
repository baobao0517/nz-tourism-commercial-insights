# Publication status — V1.0

**GitHub repository populated with source code, reproducibility instructions and a lightweight interactive dashboard.** The larger offline self-contained dashboard, full original chart exports, and all CSV-derived outputs are part of the separately delivered downloadable project package; they are not all committed to GitHub because of upload constraints. This online dashboard presents aggregated data only.

## Validated analysis

- 22 official IVS CSVs inspected; 36,563 main-header records; 3,785 target-market survey responses for YE June 2026.
- Respondent keys checked across survey tables; no orphan child references; included expenditure components reconciled to `treated_spend`.
- Three-country visitor purpose, repeat visitation and spending estimates computed with survey weights.
- Python and SQLite agree on five core weighted KPIs; five tests passed in the source local environment.
- Official rounded MBIE national, Australian and US spending figures reconcile to reporting precision.

## Transparent limitations

- Exact comparable China 2019 recovery rate and full monthly Stats NZ country arrivals series not verified.
- China market expenditure not independently reconciled to a standalone official top-line figure.
- No subgroup survey confidence intervals or operator conversion, margins, acquisition costs or measured ROI.
- No unsupported regional-spend estimates or visitor-income percentile inferences.

## Reproduction

Download the official IVS ZIP from MBIE; run the commands in README. The analysis generates aggregate `outputs/` and a complete offline dashboard on your machine.
