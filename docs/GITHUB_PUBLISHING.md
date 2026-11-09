# GitHub Publication Checklist

## Publish the deliverables

1. Create a public repository, suggested name `nz-tourism-commercial-insights`.
2. Upload the **contents** of this portfolio folder (not the wrapper ZIP) to the repository's root.
3. Confirm GitHub displays `README.md`, the embedded charts and the links under `docs/` and `outputs/`.
4. **Do not add the original microdata ZIP or a database of individual survey records.** The `.gitignore` excludes `data/raw/`.
5. Optionally enable **Settings → Pages → Deploy from a branch**, choose `main` and `/docs` (the dashboard is already copied to `docs/index.html`). You can also open `dashboard/index.html` locally without hosting it.
6. Check the hosted page on mobile and desktop; the interactive bubble chart uses an embedded JavaScript library, so no third-party service is needed at runtime.
7. Make sure `docs/DATA_VALIDATION.md` remains visible: the market-specific 2019 arrivals series and China published-value check are disclosed as incomplete.

## Reproduction

```bash
python -m venv .venv
# Activate .venv appropriate to your operating system
pip install -r requirements.txt
python src/build_portfolio.py /path/to/international-visitor-survey-data-quarter-2-2026.zip
python src/verify_sql.py /path/to/international-visitor-survey-data-quarter-2-2026.zip
python src/build_dashboard.py
pytest -q
```

## Interview story

> I used MBIE's public International Visitor Survey to evaluate three priority New Zealand tourism source markets. Rather than ranking markets by average spend alone, I segmented their travel purposes and first-time versus repeat visits, examined how expenditure categories differed, and translated these findings into testable product and marketing recommendations. I also independently reconciled the weighted figures with published MBIE totals and validated Python calculations against SQL.

**Claim only what is reproducible.** This is an independent public-data portfolio analysis, not an employer-sponsored project with measured campaign ROI.