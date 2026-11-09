"""Build a portable, offline-capable HTML dashboard from precomputed aggregates.

No survey respondent rows are embedded in the HTML; only market aggregates.
"""
from pathlib import Path
import base64
import html
import pandas as pd
import plotly.express as px

ROOT=Path(__file__).resolve().parents[1]
O=ROOT/'outputs'
D=ROOT/'dashboard'
D.mkdir(exist_ok=True)
markets=['Australia','China','United States']
market=pd.read_csv(O/'market_metrics.csv').set_index('market').loc[markets]
purpose=pd.read_csv(O/'purpose_metrics.csv')
visits=pd.read_csv(O/'first_repeat_mix.csv')
recon=pd.read_csv(O/'published_totals_reconciliation.csv')

def asset(filename,alt):
    encoded=base64.b64encode((O/filename).read_bytes()).decode('ascii')
    return f'<img loading="lazy" class="chart-image" src="data:image/png;base64,{encoded}" alt="{html.escape(alt,quote=True)}">'

def strip_market(name):
    v=market.loc[name]
    return f'''<article class="market-card">
       <div class="market-name">{html.escape(name)}</div>
       <div class="big">NZ${v.estimated_total_spend_nzd/1e9:.2f}<small>bn</small></div>
       <div class="meta">Weighted estimated total visitor spending</div>
       <div class="metric-pair"><span>Mean spend / visit</span><strong>NZ${v.mean_total_spend_per_visit_nzd:,.0f}</strong></div>
       <div class="metric-pair"><span>Mean daily / visitor</span><strong>NZ${v.mean_daily_spend_per_visitor_nzd:,.0f}</strong></div>
       <div class="metric-pair"><span>Survey sample</span><strong>n={int(v.sample_n):,}</strong></div>
    </article>'''

p=purpose.loc[purpose.display_bubble.astype(str).str.lower().eq('true')].copy()
p['purpose']=pd.Categorical(p.purpose,categories=['Holiday','VFR','Business','Conference'],ordered=True)
fig=px.scatter(p,x='purpose',y='mean_total_spend_per_visit_nzd',size='ivs_weighted_estimated_visitors',
    color='market',color_discrete_sequence=px.colors.qualitative.Safe[:3],size_max=88,opacity=.7,
    hover_name='market',
    hover_data={'purpose':True,'ivs_weighted_estimated_visitors':':,.0f','sample_n':':,',
      'weighted_market_share_pct':':.1f','mean_daily_spend_per_visitor_nzd':':,.0f',
      'mean_length_of_stay_days':':.1f','mean_total_spend_per_visit_nzd':':,.0f'},
    labels={'purpose':'Primary travel purpose', 'market':'Source market',
      'ivs_weighted_estimated_visitors':'IVS estimated visitors',
      'sample_n':'Sample n','weighted_market_share_pct':'Share of market (%)',
      'mean_daily_spend_per_visitor_nzd':'Mean daily spend (NZD)',
      'mean_total_spend_per_visit_nzd':'Mean total spend per visit (NZD)',
      'mean_length_of_stay_days':'Mean stay (days)'},
    category_orders={'purpose':['Holiday','VFR','Business','Conference'],'market':markets})
fig.update_layout(template='plotly_white',height=540,margin=dict(l=45,r=10,t=20,b=55),
    legend=dict(orientation='h',y=1.1,x=0),font=dict(family='Arial, sans-serif',size=13))
fig.update_traces(marker=dict(line=dict(width=.5,color='#ffffff')))
plot=fig.to_html(full_html=False,include_plotlyjs='inline',config={'displaylogo':False,'responsive':True})

cards=''.join(strip_market(m) for m in markets)
content=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NZ Tourism | Commercial Market Insights — YE June 2026</title>
<style>
:root{{--ink:#163247;--muted:#647485;--accent:#137d83;--border:#dfe7eb;--bg:#f5f8f8;--white:#fff}}
*{{box-sizing:border-box}} body{{margin:0;font-family:Arial,Helvetica,sans-serif;color:var(--ink);background:var(--bg);line-height:1.55}}
header{{background:#123044;color:#fff;padding:38px max(20px,calc((100% - 1180px)/2));}}
header .kicker{{letter-spacing:2px;color:#9fd0d2;text-transform:uppercase;font-size:12px;font-weight:800}}
header h1{{font-size:clamp(30px,4vw,48px);line-height:1.12;margin:12px 0 12px;max-width:820px}}
header p{{color:#d6e4e8;max-width:900px;margin:0}}
nav{{display:flex;flex-wrap:wrap;gap:22px;margin-top:24px}} nav a{{color:#c3eded;text-decoration:none;font-weight:700;font-size:13px}}nav a:hover{{text-decoration:underline}}
main{{max-width:1180px;margin:auto;padding:28px 20px 80px}}
.intro{{background:#fff;border:1px solid var(--border);border-radius:14px;padding:18px 22px;margin-bottom:25px}}
.intro strong{{color:var(--accent)}}
.cards{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:24px 0 38px}}
.market-card{{padding:22px;border-radius:14px;border:1px solid var(--border);background:var(--white);box-shadow:0 3px 12px #1433480a}}
.market-name{{font-size:14px;font-weight:800;letter-spacing:.4px;text-transform:uppercase;color:var(--accent)}}
.big{{font-size:39px;font-weight:800;letter-spacing:-1.5px;margin:4px 0}}.big small{{font-size:17px;margin-left:3px}}
.meta{{font-size:12px;color:var(--muted);margin-bottom:14px}}
.metric-pair{{display:flex;justify-content:space-between;gap:12px;border-top:1px solid #edf2f4;padding-top:9px;margin-top:9px;font-size:13px}}.metric-pair strong{{white-space:nowrap}}
h2{{font-size:26px;margin:42px 0 5px}}.deck{{color:var(--muted);max-width:1000px;margin:0 0 18px}}
.charts{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
figure{{background:#fff;border-radius:14px;border:1px solid var(--border);padding:16px;margin:0;overflow:hidden}}
figure.full{{grid-column:1/-1}}.chart-image{{width:100%;display:block;height:auto}} figcaption{{font-size:12px;color:var(--muted);margin-top:8px}}
.plot{{background:#fff;padding:12px;border:1px solid var(--border);border-radius:14px}}
.recs{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:18px}}
.rec{{padding:22px;background:#fff;border:1px solid var(--border);border-radius:14px}}
.rec h3{{margin:0 0 8px;color:var(--accent);font-size:19px}}.rec p{{font-size:14px}}
.context{{background:#eaf2f3;padding:20px;border-radius:13px;margin-top:15px}}
.context strong{{font-size:26px}}.context .stats{{display:flex;flex-wrap:wrap;gap:26px;margin:14px 0}}
.note{{border-left:3px solid #c49a50;padding:8px 15px;margin:26px 0;background:#fff8ed;color:#53452e;font-size:13px}}
footer{{margin-top:55px;border-top:1px solid var(--border);padding-top:23px;font-size:12px;color:var(--muted)}}
a{{color:var(--accent)}}
@media(max-width:850px){{.cards,.recs{{grid-template-columns:1fr}}.charts{{grid-template-columns:1fr}}figure.full{{grid-column:auto}}}}
</style></head><body>
<header><div class="kicker">Independent public-data portfolio · 2026</div>
<h1>NZ Tourism: Where Is the Commercial Opportunity?</h1>
<p>A three-market view of visitor demand context, purpose, spending, and repeat visitation. Main period: <strong>1 July 2025 – 30 June 2026</strong>. Markets: Australia, China, and the United States.</p>
<nav><a href="#markets">Market KPIs</a><a href="#segments">Visitor segmentation</a><a href="#spending">Spending patterns</a><a href="#recommendations">Commercial opportunities</a><a href="#methodology">Method and sources</a></nav></header>
<main><div class="intro"><strong>Decision lens.</strong> Visitor volume is not the same as spend per visit; spend per visit is not the same as spend per day. Compare visitor composition before selecting a product or marketing focus. These results support testable business hypotheses, not observed campaign ROI.</div>
<section id="markets"><h2>01 · Market performance</h2><p class="deck">All spend values are IVS population-weighted estimates (NZD, nominal). These estimated visitors are <strong>not</strong> Stats NZ observed border arrivals.</p><div class="cards">{cards}</div></section>
<section id="segments"><h2>02 · Who is travelling — and why?</h2><p class="deck">Whole-market averages combine very different trip purposes. The first-time / repeat split adds evidence about source-market familiarity with New Zealand.</p>
<div class="charts"><figure>{asset('purpose_mix_100pct_stacked.png','100 percent stacked bars of primary travel purpose across Australia, China and the United States')}<figcaption>Population-weighted primary travel purpose. More than one type of traveller exists in every market.</figcaption></figure>
<figure>{asset('first_repeat_100pct_stacked.png','100 percent stacked bars of first-time and repeat visitors by market')}<figcaption>Australian visitors are disproportionately returning visitors; this does not measure price sensitivity.</figcaption></figure></div>
<h3 style="margin-top:24px">Purpose × market size × spend per visit</h3><p class="deck">Interactive: hover over a bubble to see its weighted IVS visitor count, survey n and daily spend. Bubble area shows IVS population estimates; categories with n&lt;30 are omitted.</p><div class="plot">{plot}</div>
</section>
<section id="spending"><h2>03 · Where does the spending go?</h2><p class="deck">A spending share is different from the dollar amount spent per visitor. The 'Holiday only' comparison controls for one important source of composition differences.</p>
<div class="charts">
<figure class="full">{asset('spend_category_mix_100pct_stacked.png','100 percent stacked spending categories by market and all-purpose versus holiday-only cohorts')}<figcaption>Tour-package expense is a separately reported category; underlying accommodation, transport and food costs should not be double-counted.</figcaption></figure>
<figure>{asset('holiday_category_spend_per_visitor.png','Average holiday visitor expenditure in NZD across seven spending categories')}<figcaption>Mean product-category spend per holiday visitor (including zero spending).</figcaption></figure>
<figure>{asset('mean_daily_spend_only.png','Mean daily spend per visitor comparing all purposes and holiday-only visitors by market')}<figcaption>Mean daily spend per visitor is a survey-weighted average of each person's spend ÷ days in NZ, not a pooled aggregate and not inflation-adjusted.</figcaption></figure>
</div></section>
<section id="recommendations"><h2>04 · Commercial opportunities</h2><p class="deck">These are hypotheses for operators to validate using their own conversion, booking, pricing and gross-margin data.</p>
<div class="recs">
 <article class="rec"><h3>Australia · Core service & retention</h3><p><strong>Evidence:</strong> 76.1% repeat visitors; 42.6% holiday and 37.7% VFR; lower overall visit spend but large total market spend.</p><p><strong>Test:</strong> convenient accommodation, dining and flexible experiences; separately target VFR and holiday visitors, with optional upsell for first-timers.</p></article>
 <article class="rec"><h3>China · Packages & shopping</h3><p><strong>Evidence:</strong> 80.4% first-time visitors; 74.5% holiday; shopping and package expenditure contribute 16.4% and 15.2% of category spend.</p><p><strong>Test:</strong> bookable bundles and shopping-linked experiences with appropriate channels; measure margins after commissions.</p></article>
 <article class="rec"><h3>United States · Stay & experiences</h3><p><strong>Evidence:</strong> higher mean total spend per visit and more per-visitor accommodation/dining spending; longer average stays.</p><p><strong>Test:</strong> multi-night accommodation + activity products, measured through actual nights, attachment and profitability—not assumed willingness to pay.</p></article>
</div></section>
<section><h2>05 · Where is 2026 historically?</h2><div class="context">
 <div class="stats"><div><strong>3.89m</strong><br>YE June 2019 visitor arrivals</div><div><strong>3.67m</strong><br>YE June 2026 visitor arrivals</div><div><strong>94%</strong><br>Nationwide recovery to 2019</div></div>
 <p>Australia and US arrivals each reached approximately <strong>105% of YE June 2019 levels</strong>, per MBIE. China's exact comparable recovery figure is <strong>not independently verified</strong> in this version. Observed border arrivals are separate from IVS weighted visitors.</p></div></section>
<div class="note"><strong>Statistical caution:</strong> IVS is a sample survey. Published market expenditure RMEs (95% level) for YE June 2026: Australia 6.9%, China 11.4%, USA 12.4%. Segmented charts have not been assigned custom uncertainty intervals. Tour packages and the heterogeneous “Other” category require careful interpretation. No regional spending estimates were attempted.</div>
<footer id="methodology">Built from MBIE IVS Q2 2026 public microdata; visitor estimates and spend are population weighted. Historical visitor-arrival context from MBIE/Stats NZ release materials. See the repository's <a href="../docs/METHODOLOGY.md">methodology</a>, <a href="../docs/DATA_VALIDATION.md">validation report</a> and <a href="../docs/SOURCES.md">sources</a>.
<br><br>Official sources: <a href="https://www.mbie.govt.nz/immigration-and-tourism/tourism-research-and-data/tourism-data-releases/international-visitor-survey-ivs/international-visitor-survey-data-download">MBIE public IVS data</a> · <a href="https://teic.mbie.govt.nz/assets/ivs/2026Q2%20IVS%20Top-line%20results.pdf">MBIE Q2 2026 top-line PDF</a> · <a href="https://www.mbie.govt.nz/immigration-and-tourism/tourism-research-and-data/tourism-data-releases/international-visitor-survey-ivs/survey-quality">MBIE survey quality</a>.</footer>
</main></body></html>'''
(D/'index.html').write_text(content,encoding='utf-8')
(ROOT/'docs'/'index.html').write_text(content,encoding='utf-8')
print('Wrote',D/'index.html','bytes:',(D/'index.html').stat().st_size)