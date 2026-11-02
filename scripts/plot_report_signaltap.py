"""Plot control waveforms directly from the saved physical SignalTap CSVs."""
from pathlib import Path
import csv,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];D=R/'docs/reports/defense_session';out=R/'docs/reports/final_report/figures';out.mkdir(exist_ok=True)
checks=json.loads((D/'SIGNALTAP_CAPTURE_CHECK.json').read_text())
for c in checks['captures']:
 v=c['variant'];rows=list(csv.DictReader((R/c['decoded_csv']).open()));a=c['accepted_index']-c['trigger_index'];lo=a-5;hi=6
 sel=[r for r in rows if lo<=int(r['relative_to_trigger'])<=hi];xs=[int(r['relative_to_trigger']) for r in sel]
 fig,ax=plt.subplots(figsize=(8.8,2.8));fig.subplots_adjust(left=.18,right=.97,top=.84,bottom=.25)
 for i,key in enumerate(['sample_valid','sample_ready','forecast_valid']):
  base=(2-i)*1.6;ys=[base+int(r[key])*.8 for r in sel];ax.step(xs,ys,where='post',color='#1d5676',linewidth=1.5)
 ax.set_yticks([3.6,2,.4],['sample_valid','sample_ready','forecast_valid']);ax.set_ylim(-.2,4.8);ax.set_xlim(lo,hi)
 ax.set_xlabel('Sample relative to trigger (20 ns per sample)',fontsize=10);ax.tick_params(labelsize=10);ax.grid(axis='x',alpha=.2);ax.spines[['top','right','left']].set_visible(False)
 ax.axvline(a,color='.45',linestyle=':',linewidth=.9);ax.axvline(0,color='.45',linestyle=':',linewidth=.9)
 ax.annotate('',xy=(0,4.45),xytext=(a,4.45),arrowprops=dict(arrowstyle='<->',color='.25'))
 ax.text(a/2,4.6,f'{-a} sampled intervals',ha='center',va='bottom',fontsize=10)
 title={'temperature_speed':'Temperature speed','temperature_resource':'Temperature shared','weather_speed':'Weather parallel','weather_resource':'Weather shared'}[v]
 ax.set_title(title+'   Physical SignalTap capture',loc='left',fontsize=12,pad=18)
 fig.savefig(out/(v+'.png'),dpi=220);plt.close(fig)
