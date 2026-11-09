from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
O=ROOT/'outputs'

def test_market_sample_and_weights():
    k=pd.read_csv(O/'market_metrics.csv').set_index('market')
    assert k.sample_n.to_dict()=={'Australia':2496,'China':714,'United States':575}
    assert (k.estimated_total_spend_nzd>0).all()
    assert (k.mean_daily_spend_per_visitor_nzd>0).all()

def test_purpose_and_visit_shares_sum_to_100():
    for name,col in [('purpose_metrics.csv','weighted_market_share_pct'),('first_repeat_mix.csv','weighted_visitor_share_pct')]:
        df=pd.read_csv(O/name)
        for m,grp in df.groupby('market'):
            assert np.isclose(grp[col].sum(),100,atol=1e-8),m

def test_spend_categories_reconcile():
    c=pd.read_csv(O/'spending_categories.csv')
    for _,grp in c.groupby(['market','cohort']):
        assert np.isclose(grp.share_of_spend_pct.sum(),100,atol=1e-8)

def test_published_total_rounded_reconciliation():
    r=pd.read_csv(O/'published_totals_reconciliation.csv')
    assert r.consistent_with_rounded_official.all()
    assert set(r.market)=={'All markets','Australia','United States'}

def test_key_integrity_and_no_unsupported_china_recovery():
    q=json.loads((O/'validation_summary.json').read_text())
    assert q['csv_table_count']==22
    assert q['full_main_header_rows']==36563
    assert q['orphan_keys_all_ivs_tables']==0
    assert not q['china_2019_recovery_exact_available']
    h=pd.read_csv(O/'historical_context_published.csv')
    assert pd.isna(h.query("market=='China'").recovery_pct_of_2019.iloc[0])