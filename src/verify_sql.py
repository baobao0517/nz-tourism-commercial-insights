"""Independently validate weighted Python KPI estimates against real SQL queries.

Example:
  python src/verify_sql.py path/to/official-ivs.zip
No visitor-level records are saved to the GitHub repository.
"""
from pathlib import Path
import sqlite3
import zipfile
import sys
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ZIP = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT/'data'/'raw'/'international-visitor-survey-data-quarter-2-2026.zip'
if not ZIP.is_file():
    raise SystemExit(f'Cannot find MBIE microdata: {ZIP}')
with zipfile.ZipFile(ZIP) as z:
    h = pd.read_csv(z.open('views/survey_main_header.csv'), low_memory=False,
       usecols=['year','qtr','country_of_residence','purpose_of_visit_main',
                'first_nz_trip','population_weight','treated_spend','no_days_in_nz'])

# Process in memory so individual survey records are never distributed.
with sqlite3.connect(':memory:') as db:
    h.to_sql('ivs_visitors', db, index=False)
    sql = (ROOT/'sql'/'market_analytics.sql').read_text(encoding='utf-8')
    out = pd.read_sql_query(sql, db)

out_path = ROOT/'outputs'/'sql_crosscheck.csv'
out.to_csv(out_path, index=False)
py = pd.read_csv(ROOT/'outputs'/'market_metrics.csv').set_index('market')
for _, r in out.iterrows():
    m=r['market']
    assert int(r.sample_n)==int(py.loc[m,'sample_n'])
    for col in ('ivs_weighted_estimated_visitors','estimated_total_spend_nzd',
        'mean_total_spend_per_visit_nzd','mean_daily_spend_per_visitor_nzd',
        'mean_length_of_stay_days'):
        sql_col='estimated_ivs_visitors' if col=='ivs_weighted_estimated_visitors' else col
        assert np.isclose(float(r[sql_col]),float(py.loc[m,col]),rtol=1e-10,atol=0.1),(m,col,r[sql_col],py.loc[m,col])
print('PASS: SQLite and Python independently agree on five weighted market KPIs for all 3 markets.')
print(out[['market','sample_n','estimated_total_spend_nzd','repeat_visitor_share_pct']].round(1).to_string(index=False))