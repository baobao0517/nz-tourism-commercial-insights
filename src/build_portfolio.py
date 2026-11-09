#!/usr/bin/env python3
"""NZ tourism portfolio: weighted purpose/bubble, daily spend, product expenditure and travel behaviour.

Run:
    python reproduce.py /path/to/international-visitor-survey-data-quarter-2-2026.zip

Outputs are written next to this script. All estimated visitors are the IVS target population
(summed population_weight), NOT the Stats NZ immigration/border arrivals count.
"""
from pathlib import Path
import json
import sys
import zipfile
import hashlib

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs'
OUT.mkdir(parents=True, exist_ok=True)
ZIP = Path(sys.argv[1]) if len(sys.argv)>1 else ROOT / 'data' / 'raw' / 'international-visitor-survey-data-quarter-2-2026.zip'
if not ZIP.is_file():
    raise FileNotFoundError(f'Official IVS ZIP not found: {ZIP}. Download it from MBIE and supply its path.')
MARKETS = ['Australia','China','United States']
COUNTRY_MAP = {'Australia':'Australia',"China, People's Republic of":'China','United States of America':'United States'}
PURPOSES = ['Holiday','VFR','Business','Conference','Other / education']
CATEGORY_FIELDS = {
    'Accommodation': ['cost_accomm'],
    'Food & dining': ['cost_food_drink','cost_eating_out'],
    'Transport in NZ': ['cost_dom_travel','cost_dom_flights','cost_car_rentals'],
    'Activities & cruises': ['cost_entertainment','cost_day_cruise'],
    'Shopping': ['cost_shopping'],
    'Tour packages': ['cost_tour_package'],
    'Other': ['cost_other'],
}
CATEGORIES = list(CATEGORY_FIELDS)

with zipfile.ZipFile(ZIP) as z:
    h = pd.read_csv(z.open('views/survey_main_header.csv'),low_memory=False)
    e = pd.read_csv(z.open('views/expenditure_by_industry.csv'),low_memory=False)
    t = pd.read_csv(z.open('views/transport_methods.csv'),low_memory=False)
    a = pd.read_csv(z.open('views/accommodation.csv'),low_memory=False)

period = ((h.year.eq(2025)&h.qtr.isin([3,4]))|(h.year.eq(2026)&h.qtr.isin([1,2])))
d = h.loc[period & h.country_of_residence.isin(COUNTRY_MAP)].copy()
d['market'] = d.country_of_residence.map(COUNTRY_MAP)
d['purpose'] = d.purpose_of_visit_main.replace({
    'Holiday / vacation':'Holiday',
    'Visiting friends / relatives':'VFR',
    'Conference / convention':'Conference',
})
d['purpose'] = d.purpose.where(d.purpose.isin(PURPOSES[:-1]),'Other / education')
assert d.response_id.notna().all() and d.response_id.is_unique, 'Duplicate/null IVS respondent ID in core period'
assert (d.population_weight>0).all() and d.population_weight.notna().all(), 'Invalid population weight'
assert (d.no_days_in_nz>0).all() and d.no_days_in_nz.notna().all(), 'Invalid length of stay'
assert d.treated_spend.notna().all() and (d.treated_spend>=0).all(), 'Invalid treated spend'
assert e.response_id.is_unique, 'Multiple expenditure category rows per respondent'
d = d.merge(e,on='response_id',how='left',validate='one_to_one',indicator=True)
assert d['_merge'].eq('both').all(), 'Unmatched expenditure row'
d = d.drop(columns=['_merge'])
flat_fields = [col for fields in CATEGORY_FIELDS.values() for col in fields]
assert d[flat_fields].notna().all().all(), 'Null included expenditure category'
assert (d[flat_fields]>=0).all().all(), 'Negative included expenditure category'
for category, columns in CATEGORY_FIELDS.items():
    d[category] = d[columns].sum(axis=1)
reconciled = d[CATEGORIES].sum(axis=1)
max_delta = float(np.max(np.abs(reconciled-d.treated_spend)))
assert max_delta < .02, f'Expenditure components do not reconcile: max {max_delta}'

def summary(g):
    w = g.population_weight.to_numpy(float)
    spending = g.treated_spend.to_numpy(float)
    days = g.no_days_in_nz.to_numpy(float)
    return {
        'sample_n':int(len(g)),
        'ivs_weighted_estimated_visitors':float(w.sum()),
        'estimated_total_spend_nzd':float((w*spending).sum()),
        'mean_total_spend_per_visit_nzd':float(np.average(spending, weights=w)),
        'mean_daily_spend_per_visitor_nzd':float(np.average(spending/days,weights=w)),
        'mean_length_of_stay_days':float(np.average(days,weights=w)),
    }

market_rows=[]; purpose_rows=[]; category_rows=[]
for m in MARKETS:
    g=d.loc[d.market.eq(m)]
    market_rows.append({'market':m,**summary(g)})
    pop = float(g.population_weight.sum())
    for p in PURPOSES:
        gp=g.loc[g.purpose.eq(p)]
        if gp.empty:continue
        purpose_rows.append({
            'market':m,'purpose':p,**summary(gp),
            'unweighted_sample_share_pct':100*len(gp)/len(g),
            'weighted_market_share_pct':100*gp.population_weight.sum()/pop,
            'display_bubble':bool(len(gp)>=30 and p!='Other / education'),
        })
    for cohort, cg in [('All purposes',g),('Holiday only',g.loc[g.purpose.eq('Holiday')])]:
        total_spend=float((cg.treated_spend*cg.population_weight).sum())
        for c in CATEGORIES:
            spend=float((cg[c]*cg.population_weight).sum())
            category_rows.append({
                'market':m,'cohort':cohort,'spending_category':c,
                'sample_n':int(len(cg)),
                'estimated_spend_nzd':spend,
                'share_of_spend_pct':100*spend/total_spend,
                'mean_category_spend_per_visit_nzd':spend/cg.population_weight.sum(),
            })
market_df=pd.DataFrame(market_rows)
purpose_df=pd.DataFrame(purpose_rows)
category_df=pd.DataFrame(category_rows)
market_df.to_csv(OUT/'market_metrics.csv',index=False)
purpose_df.to_csv(OUT/'purpose_metrics.csv',index=False)
category_df.to_csv(OUT/'spending_categories.csv',index=False)
assert all(abs(purpose_df.loc[purpose_df.market.eq(m),'weighted_market_share_pct'].sum()-100)<1e-7 for m in MARKETS)
assert all(abs(category_df.loc[(category_df.market==m)&(category_df.cohort==c),'share_of_spend_pct'].sum()-100)<1e-7 for m in MARKETS for c in ['All purposes','Holiday only'])

# Return data for groups with reliable enough raw support for display.
plot=purpose_df.loc[purpose_df.display_bubble].copy()
purpose_pos={'Holiday':0,'VFR':1,'Business':2,'Conference':3}
shifts={'Australia':-.24,'China':0,'United States':.24}
fig,ax=plt.subplots(figsize=(13.2,7.4))
colors=plt.rcParams['axes.prop_cycle'].by_key()['color'][:3]
max_count=float(plot.ivs_weighted_estimated_visitors.max())
for m,c in zip(MARKETS,colors):
    g=plot.loc[plot.market.eq(m)]
    x=g.purpose.map(purpose_pos).to_numpy(float)+shifts[m]
    y=g.mean_total_spend_per_visit_nzd.to_numpy(float)
    s=g.ivs_weighted_estimated_visitors.to_numpy(float)/max_count*2600
    ax.scatter(x,y,s=s,alpha=.38,label=m,linewidth=1.4,edgecolors=c,zorder=4)
    for xi,yi,ni,est in zip(x,y,g.sample_n,g.ivs_weighted_estimated_visitors):
        ax.annotate(f'${yi/1000:.1f}k',(xi,yi),ha='center',va='center',fontweight='bold',fontsize=9.3,zorder=6)
        ax.annotate(f'{est/1000:,.0f}k visitors',(xi,yi),xytext=(0,-25),textcoords='offset points',ha='center',fontsize=8.3)
ax.set_xticks(range(4),['Holiday','Visiting friends\n& relatives','Business','Conference'])
ax.set_xlim(-.62,3.58)
ax.set_ylim(500,10500)
ax.set_xlabel('Primary travel purpose')
ax.set_ylabel('Mean total spend per visit (NZD)')
ax.set_title('Market Size × Travel Purpose × Spend per Visit',loc='left',fontweight='bold',fontsize=16,pad=23)
ax.text(0,1.025,'IVS population-weighted visitor estimates | Year ended June 2026',transform=ax.transAxes,fontsize=10)
ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
ax.spines[['top','right']].set_visible(False)
market_legend=ax.legend(loc='upper left',bbox_to_anchor=(0.02,.98),title='Market',frameon=True,markerscale=.45)
ax.add_artist(market_legend)
size_vals=[100000,300000,600000]
handles=[ax.scatter([],[],s=v/max_count*2600,alpha=.25,edgecolors='gray') for v in size_vals]
ax.legend(handles,['100k','300k','600k'],title='Bubble area = estimated IVS visitors',loc='upper right',scatterpoints=1,labelspacing=1.5)
fig.text(.09,.075,'Bubble size = sum of IVS population weights within market × purpose. NOT observed Stats NZ border arrivals.',fontsize=9)
fig.text(.09,.052,'Only n≥30 shown, excluding Other / education. Small groups omitted; estimates are descriptive (no custom confidence intervals).',fontsize=9)
fig.text(.09,.027,'Source: MBIE IVS Q2 2026 microdata, 1 Jul 2025–30 Jun 2026. International airfares excluded.',fontsize=8.6)
fig.subplots_adjust(bottom=.18,left=.09,right=.98,top=.85)
fig.savefig(OUT/'bubble_market_size_spend.png',dpi=200)
plt.close(fig)

# All market mix - 100% stack retained.
fig,ax=plt.subplots(figsize=(11.2,4.9))
piv=purpose_df.pivot(index='market',columns='purpose',values='weighted_market_share_pct').reindex(index=MARKETS,columns=PURPOSES).fillna(0)
left=np.zeros(3)
for c in PURPOSES:
    heights=piv[c].to_numpy(float)
    bars=ax.barh(MARKETS,heights,left=left,label=c)
    for j,(r,v) in enumerate(zip(bars,heights)):
        if v>=8:
            ax.text(left[j]+v/2,r.get_y()+r.get_height()/2,f'{v:.0f}%',ha='center',va='center',fontsize=9)
    left+=heights
ax.invert_yaxis();ax.set_xlim(0,100)
ax.set_xlabel('Estimated share of visitors (%) — population weighted')
ax.set_title('Why Market Averages Differ: Primary Purpose Mix',loc='left',fontsize=15,fontweight='bold')
ax.legend(ncol=5,loc='lower center',bbox_to_anchor=(.5,-.42),frameon=False)
ax.spines[['top','right']].set_visible(False)
fig.text(.11,.03,'MBIE IVS Q2 2026 microdata; year ended June 2026. Small purpose categories carry higher uncertainty.',fontsize=9)
fig.subplots_adjust(left=.12,right=.98,top=.85,bottom=.32)
fig.savefig(OUT/'purpose_mix_100pct_stacked.png',dpi=185);plt.close(fig)

# Show ONLY the selected mean daily spend measure (not pooled total spend / all visitor-days).
fig,ax=plt.subplots(figsize=(9.7,5.7))
x=np.arange(3); width=.33
whole=market_df.set_index('market').loc[MARKETS].mean_daily_spend_per_visitor_nzd.to_numpy(float)
holiday=purpose_df.loc[purpose_df.purpose.eq('Holiday')].set_index('market').loc[MARKETS].mean_daily_spend_per_visitor_nzd.to_numpy(float)
for xpos,values,name in [(x-width/2,whole,'All purposes'),(x+width/2,holiday,'Holiday only')]:
    bars=ax.bar(xpos,values,width,label=name)
    for b in bars:
        ax.annotate(f'${b.get_height():,.0f}',(b.get_x()+b.get_width()/2,b.get_height()),xytext=(0,5),textcoords='offset points',ha='center',fontsize=10)
ax.set_xticks(x,MARKETS)
ax.set_ylim(0,max(max(whole),max(holiday))*1.19)
ax.set_ylabel('Mean daily spend per visitor (NZD)')
ax.set_title('Daily Spend: All Visitors vs Holiday Visitors',loc='left',fontsize=15,fontweight='bold')
ax.legend(frameon=False);ax.spines[['top','right']].set_visible(False)
ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
fig.text(.11,.04,'Weighted mean of individual visitor (treated_spend / days); same annual period for all markets.',fontsize=9)
fig.subplots_adjust(left=.11,right=.98,top=.88,bottom=.18)
fig.savefig(OUT/'mean_daily_spend_only.png',dpi=185);plt.close(fig)

# 100% stacked spend categories, ALL vs HOLIDAY as separate groups within one chart.
fig,ax=plt.subplots(figsize=(12.8,6.3))
rows=[(m,c) for m in MARKETS for c in ['All purposes','Holiday only']]
y=np.arange(len(rows)); left=np.zeros(len(rows))
for cat in CATEGORIES:
    val=np.array([category_df.loc[(category_df.market==m)&(category_df.cohort==c)&(category_df.spending_category==cat),'share_of_spend_pct'].iloc[0] for m,c in rows])
    bars=ax.barh(y,val,left=left,height=.68,label=cat)
    for i,(b,v) in enumerate(zip(bars,val)):
        if v>=10:
            ax.text(left[i]+v/2,b.get_y()+b.get_height()/2,f'{v:.0f}%',ha='center',va='center',fontsize=8.8)
    left+=val
ax.set_yticks(y,[f'{m} · {"All" if c=="All purposes" else "Holiday"}' for m,c in rows])
ax.invert_yaxis();ax.set_xlim(0,100)
ax.set_xlabel('Share of estimated visitor spend (%)')
ax.set_title('Where the Money Goes: Spend Category Mix',loc='left',fontweight='bold',fontsize=15)
ax.legend(loc='lower center',bbox_to_anchor=(.5,-.38),frameon=False,ncol=4)
ax.spines[['top','right']].set_visible(False)
fig.text(.11,.056,'Categories are mutually exclusive in the supplied IVS expenditure table. Package spending is not allocated to underlying products.',fontsize=8.8)
fig.text(.11,.033,'Source: MBIE IVS Q2 2026 microdata, population weighted; NZD expenditure excluding international airfare.',fontsize=8.8)
fig.subplots_adjust(left=.22,right=.98,top=.89,bottom=.34)
fig.savefig(OUT/'spend_category_mix_100pct_stacked.png',dpi=185);plt.close(fig)

# Holiday market comparability: average spend on each component per holiday visitor.
fig,ax=plt.subplots(figsize=(12.6,6.1))
x=np.arange(len(CATEGORIES)); width=.25
for j,m in enumerate(MARKETS):
    v=[category_df.loc[(category_df.market==m)&(category_df.cohort=='Holiday only')&(category_df.spending_category==cat),'mean_category_spend_per_visit_nzd'].iloc[0] for cat in CATEGORIES]
    ax.bar(x+(j-1)*width,v,width,label=m)
ax.set_xticks(x,['Accommodation','Food &\ndining','Transport\nin NZ','Activities\n& cruises','Shopping','Tour\npackages','Other'])
ax.set_ylabel('Weighted mean spend per holiday visit (NZD)')
ax.set_title('Holiday Visitors: Expenditure by Category',loc='left',fontsize=15,fontweight='bold')
ax.legend(frameon=False);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
ax.spines[['top','right']].set_visible(False)
fig.text(.10,.025,'All values are per visitor, not only per purchaser. “Other” and tour package costs need cautious interpretation.',fontsize=9)
fig.subplots_adjust(bottom=.17,left=.1,right=.98,top=.87)
fig.savefig(OUT/'holiday_category_spend_per_visitor.png',dpi=185);plt.close(fig)

# VEM-based travel modes and accommodation, sample counts retained and no unsupported precise campervan spend inference.
transport_modes = {
    'Rental car':('transport', ['Rental car']),
    'Rental campervan / motor-home':('transport',['Rental campervan / motor-home']),
    'Hotel':('accommodation',['Hotel']),
    'With friends / family':('accommodation',['Staying with family or friends']),
    'Holiday park (paid)':('accommodation', ['Other (paid) camping ground / holiday park (where you can stay in a tent, cabin, caravan, or campervan / motorhome)']),
}
t=t.drop_duplicates(['response_id','transport_method'])
a=a.drop_duplicates(['response_id','accomm_type_used'])
behaviour_rows=[]
for m in MARKETS:
    for cohort in ['All purposes','Holiday only']:
        g = d.loc[d.market.eq(m)&(d.purpose.eq('Holiday') if cohort=='Holiday only' else True)&d.vem_pop_weight.notna()&(d.vem_pop_weight>0)]
        for label,(kind, vals) in transport_modes.items():
            if kind=='transport':
                yes=set(t.loc[t.transport_method.isin(vals),'response_id'])
            else:
                yes=set(a.loc[a.accomm_type_used.isin(vals),'response_id'])
            used = g.response_id.isin(yes)
            n=int(used.sum())
            behaviour_rows.append({
                'market':m,'cohort':cohort,'behaviour':label,'eligible_vem_respondents_n':int(len(g)),
                'users_unweighted_n':n,
                'weighted_participation_pct':100*g.loc[used,'vem_pop_weight'].sum()/g.vem_pop_weight.sum(),
                'small_cell_n_lt_30':n<30,
                'sample_population_note':'VEM respondents only; overlapping modes/accommodations; shares need not total 100%',
            })
behaviour_df=pd.DataFrame(behaviour_rows)
behaviour_df.to_csv(OUT/'travel_behaviour_vem.csv',index=False)

# Only rental-car use in sufficiently sampled holiday segment is graphed; do not visually rank tiny campervan groups.
subset=behaviour_df.loc[(behaviour_df.cohort=='Holiday only')&(behaviour_df.behaviour=='Rental car')].set_index('market').loc[MARKETS]
fig,ax=plt.subplots(figsize=(8.5,5.5))
bars=ax.bar(MARKETS,subset.weighted_participation_pct)
for b,n in zip(bars,subset.users_unweighted_n):
    ax.annotate(f'{b.get_height():.1f}%\n(n={n})',(b.get_x()+b.get_width()/2,b.get_height()),xytext=(0,5),textcoords='offset points',ha='center',fontsize=10)
ax.set_ylim(0,85);ax.set_ylabel('Estimated share using a rental car (%)')
ax.set_title('Holiday Visitors: Rental Car Use',loc='left',fontsize=15,fontweight='bold')
ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
fig.text(.105,.05,'VEM-weighted, multi-response. Uses a rental car at some point; this is not rental-car expenditure.',fontsize=9)
fig.subplots_adjust(bottom=.2,left=.105,right=.98,top=.86)
fig.savefig(OUT/'rental_car_holiday_vem.png',dpi=185);plt.close(fig)

# Interactive chart HTML for individual group details; size in estimated people, not within-market percentage.
try:
    import plotly.express as px
    p=plot.copy();p['purpose']=pd.Categorical(p.purpose,categories=PURPOSES,ordered=True)
    fig=px.scatter(p,x='purpose',y='mean_total_spend_per_visit_nzd',size='ivs_weighted_estimated_visitors',color='market',
        size_max=100,opacity=.62,category_orders={'market':MARKETS,'purpose':PURPOSES[:-1]},
        hover_name='market',hover_data={
            'purpose':True,'ivs_weighted_estimated_visitors':':,.0f','sample_n':':,',
            'weighted_market_share_pct':':.1f','mean_total_spend_per_visit_nzd':':,.0f',
            'mean_daily_spend_per_visitor_nzd':':,.0f','mean_length_of_stay_days':':.1f'},
        labels={'purpose':'Primary travel purpose','market':'Source market',
                'ivs_weighted_estimated_visitors':'IVS estimated visitors',
                'mean_total_spend_per_visit_nzd':'Mean total spend per visit (NZD)',
                'mean_daily_spend_per_visitor_nzd':'Mean daily spend per visitor (NZD)',
                'sample_n':'Survey n','weighted_market_share_pct':'Within-market visitor share (%)',
                'mean_length_of_stay_days':'Mean length of stay (days)'},
        title='Visitor Volume × Trip Purpose × Spend per Visit | Year ended June 2026')
    fig.update_layout(template='plotly_white',height=650,margin=dict(l=60,r=55,t=90,b=130),
        annotations=[dict(text='Bubble area = IVS weighted estimated visitors (NOT Stats NZ arrival counts); n≥30 only. Source: MBIE IVS Q2 2026.',
        xref='paper',yref='paper',x=0,y=-.18,showarrow=False,font=dict(size=11,color='gray'))])
    fig.write_html(OUT/'bubble_market_size_spend_interactive.html',full_html=True,include_plotlyjs=True)
except ImportError:
    print('plotly unavailable; static chart was generated')

qa={'period':'2025-07-01 to 2026-06-30',
    'source_zip':ZIP.name,'core_market_rows':int(len(d)),
    'by_market_raw_samples':{k:int(v) for k,v in d.market.value_counts().items()},
    'maximum_absolute_category_to_treated_spend_difference_nzd':max_delta,
    'core_expenditure_columns':flat_fields,
    'population_weight_used_for_spend_and_purpose':True,
    'vem_pop_weight_used_for_transport_and_accommodation':True,
    'ivs_vs_stats_arrivals_warning':'IVS weighted population estimates are NOT independently observed border arrivals',
    'custom_sampling_confidence_intervals_computed':False,
    'category_composition_all_purposes_rows':int(len(category_df.loc[category_df.cohort.eq('All purposes')])),
}
(OUT/'validation_summary.json').write_text(json.dumps(qa,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Market metrics:\n',market_df.round(1).to_string(index=False))
print('Bubble purpose breakdown:\n',plot[['market','purpose','sample_n','ivs_weighted_estimated_visitors','mean_total_spend_per_visit_nzd']].round().to_string(index=False))
print('Wrote outputs to',OUT)

# First-time vs repeat visit: separate, unambiguous primary-question field.
visit_rows=[]
au_detail=[]
for m in MARKETS:
    g=d.loc[d.market.eq(m)]
    valid=g.loc[g.first_nz_trip.isin(['Yes','No'])]
    assert len(valid)==len(g), f'Missing first_nz_trip in {m}'
    total=valid.population_weight.sum()
    for flag,label in [('No','Repeat visitor'),('Yes','First-time visitor')]:
        gg=valid.loc[valid.first_nz_trip.eq(flag)]
        visit_rows.append({'market':m,'visit_status':label,'sample_n':len(gg),
            'unweighted_sample_share_pct':100*len(gg)/len(valid),
            'weighted_visitor_share_pct':100*gg.population_weight.sum()/total,
            'ivs_estimated_visitors':gg.population_weight.sum(),
            'mean_total_spend_per_visit_nzd':np.average(gg.treated_spend,weights=gg.population_weight)})
    if m=='Australia':
        for p in PURPOSES:
            gp=g.loc[g.purpose.eq(p)]
            if not len(gp):continue
            re=gp.loc[gp.first_nz_trip.eq('No')]
            au_detail.append({'purpose':p,'sample_n':len(gp),'repeat_sample_n':len(re),
                'weighted_repeat_pct':100*re.population_weight.sum()/gp.population_weight.sum()})
visit_df=pd.DataFrame(visit_rows)
visit_df.to_csv(OUT/'first_repeat_mix.csv',index=False)
pd.DataFrame(au_detail).to_csv(OUT/'australia_repeat_by_purpose.csv',index=False)

fig,ax=plt.subplots(figsize=(11,5.2))
vals=visit_df.pivot(index='market',columns='visit_status',values='weighted_visitor_share_pct').reindex(MARKETS)
left=np.zeros(3)
for col in ['Repeat visitor','First-time visitor']:
    bars=ax.barh(MARKETS,vals[col].to_numpy(),left=left,label=col,height=.6)
    for i,b in enumerate(bars):
        v=float(vals[col].iloc[i]);ax.text(left[i]+v/2,i,f'{v:.1f}%',va='center',ha='center',fontsize=12,fontweight='bold')
    left+=vals[col].to_numpy()
ax.invert_yaxis();ax.set_xlim(0,100)
ax.set_xlabel('Share of estimated IVS visitors (%)')
ax.set_title('Repeat Visits Explain Market Maturity',loc='left',fontweight='bold',fontsize=16,pad=18)
ax.legend(loc='lower center',bbox_to_anchor=(.5,-.32),ncol=2,frameon=False)
ax.spines[['top','right']].set_visible(False)
fig.text(.10,.075,'First-time = first_nz_trip "Yes"; repeat = "No". Population-weighted within each market.',fontsize=9)
fig.text(.10,.045,'MBIE IVS Q2 2026 microdata | Year ended June 2026 | Estimates, not census counts.',fontsize=9)
fig.subplots_adjust(bottom=.26,top=.84,left=.11,right=.97)
fig.savefig(OUT/'first_repeat_100pct_stacked.png',dpi=190);plt.close(fig)

# Independent reconciliation with round-to-1-decimal $ billions in the official MBIE Q2 release.
full=h.loc[period].copy()
full_total=(full.population_weight*full.treated_spend).sum()
recon=[
    ('All markets',full_total,14.3,'MBIE Q2 2026 top-line: NZ$14.3b'),
    ('Australia',float(market_df.set_index('market').loc['Australia','estimated_total_spend_nzd']),4.4,'MBIE Q2 2026 top-line: NZ$4.4b'),
    ('United States',float(market_df.set_index('market').loc['United States','estimated_total_spend_nzd']),2.2,'MBIE Q2 2026 top-line: NZ$2.2b'),
]
recon_df=pd.DataFrame([{
    'market':name,'microdata_spend_nzd':amt,'microdata_spend_billions':amt/1e9,
    'official_published_billions_rounded':published,
    'difference_from_published_rounded_billions':amt/1e9-published,
    'consistent_with_rounded_official':bool(abs(amt/1e9-published)<=.05+1e-6),
    'source_label':label,
} for name,amt,published,label in recon])
assert recon_df.consistent_with_rounded_official.all()
recon_df.to_csv(OUT/'published_totals_reconciliation.csv',index=False)

# Separate border arrivals and pre-pandemic context. Never mix these with IVS weighted counts.
historical=pd.DataFrame([
    {'market':'All markets','period':'YE Jun 2019','actual_arrivals_approx':3890000,'recovery_pct_of_2019':100,'value_status':'MBIE/Stats NZ published rounded'},
    {'market':'All markets','period':'YE Jun 2026','actual_arrivals_approx':3670000,'recovery_pct_of_2019':94,'value_status':'MBIE/Stats NZ published rounded'},
    {'market':'Australia','period':'YE Jun 2026','actual_arrivals_approx':1590000,'recovery_pct_of_2019':105,'value_status':'Published approximately; MBIE 105% and Stats NZ ~1.59m'},
    {'market':'China','period':'YE Jun 2026','actual_arrivals_approx':315000,'recovery_pct_of_2019':np.nan,'value_status':'Published approx. 315k; 2019 recovery NOT independently verified'},
    {'market':'United States','period':'YE Jun 2026','actual_arrivals_approx':np.nan,'recovery_pct_of_2019':105,'value_status':'MBIE published 105%; exact arrivals count NOT independently verified'},
])
historical.to_csv(OUT/'historical_context_published.csv',index=False)

# ZIP-level data inventory. Full table key checks; duplicate rows are not automatically bad for multi-response tables.
with zipfile.ZipFile(ZIP) as zin:
    master_keys=set(h.response_id)
    inventory=[]
    for filename in sorted(x for x in zin.namelist() if x.endswith('.csv')):
        tbl=pd.read_csv(zin.open(filename),low_memory=False)
        has_key='response_id' in tbl.columns
        n_orphan=int((~tbl.response_id.isin(master_keys)).sum()) if has_key else None
        inventory.append({
            'file':filename.split('/')[-1], 'rows':len(tbl), 'columns':len(tbl.columns),
            'respondent_key_present':has_key,
            'null_respondent_keys':int(tbl.response_id.isna().sum()) if has_key else None,
            'orphan_respondent_keys':n_orphan,
            'duplicate_respondent_key_rows':int(tbl.response_id.duplicated().sum()) if has_key else None,
            'exact_duplicate_rows':int(tbl.duplicated().sum()),
            'column_names':' | '.join(tbl.columns),
            'dtypes':' | '.join(f'{c}:{t}' for c,t in tbl.dtypes.items()),
            'fields_with_any_missing':' | '.join(f'{k}:{v:.1f}%' for k,v in
                (tbl.isna().mean()*100).items() if v>0),
        })
inventory_df=pd.DataFrame(inventory)
inventory_df.to_csv(OUT/'source_csv_inventory_and_quality.csv',index=False)
assert inventory_df.orphan_respondent_keys.fillna(0).eq(0).all()
assert h.response_id.notna().all() and h.response_id.is_unique

qa.update({
    'ivs_archive_sha256':hashlib.sha256(ZIP.read_bytes()).hexdigest(),
    'csv_table_count':int(len(inventory_df)),
    'full_main_header_rows':int(len(h)),
    'all_market_year_ended_june_2026_n':int(len(full)),
    'all_market_weighted_expenditure_nzd':float(full_total),
    'orphan_keys_all_ivs_tables':int(inventory_df.orphan_respondent_keys.fillna(0).sum()),
    'first_repeat_share_check':bool(all(abs(visit_df.loc[visit_df.market==m,'weighted_visitor_share_pct'].sum()-100)<1e-8 for m in MARKETS)),
    'reconciliation_to_official_rounded_totals':bool(recon_df.consistent_with_rounded_official.all()),
    'china_2019_recovery_exact_available':False,
    'published_annual_china_spend_separately_reconciled':False,
    'published_arrival_series_full_market_monthly_available':False,
    'fully_published_statistical_uncertainty_for_custom_subgroups':False,
    'market_spend_official_rme_pct':{'Australia':6.9,'China':11.4,'United States':12.4},
})
(OUT/'validation_summary.json').write_text(json.dumps(qa,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('First-revisit comparison:\n',visit_df.round(2).to_string(index=False))
print('Published reconciliation:\n',recon_df.round(3).to_string(index=False))
print('CSV inventory: ',len(inventory_df),'tables; orphan references:',int(inventory_df.orphan_respondent_keys.fillna(0).sum()))

# Weighted tour-package purchase incidence; not a claim that respondents joined a group tour.
package_incidence=[]
for m in MARKETS:
    g=d.loc[d.market.eq(m)]
    used=g['Tour packages'].gt(0)
    package_incidence.append({
        'market':m,'sample_n':len(g),
        'purchaser_sample_n':int(used.sum()),
        'weighted_purchase_incidence_pct':100*g.loc[used,'population_weight'].sum()/g.population_weight.sum(),
        'tour_package_spend_share_pct':100*(g['Tour packages']*g.population_weight).sum()/(g.treated_spend*g.population_weight).sum(),
    })
pd.DataFrame(package_incidence).to_csv(OUT/'tour_package_incidence.csv',index=False)