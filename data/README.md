# Data policy

This public repository contains only aggregate, non-respondent analysis outputs and reproducible code. The official MBIE International Visitor Survey Q2 2026 microdata ZIP is **not distributed** here.

Download the dataset from the [MBIE official IVS download page](https://www.mbie.govt.nz/immigration-and-tourism/tourism-research-and-data/tourism-data-releases/international-visitor-survey-ivs/international-visitor-survey-data-download) and run `python src/build_portfolio.py /path/to/zip`.

`data/raw/` is gitignored. Do not commit survey respondent-level rows or extracts.
