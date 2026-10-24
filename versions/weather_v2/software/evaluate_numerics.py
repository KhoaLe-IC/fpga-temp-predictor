"""Quantization/range diagnostics for the frozen weather model; no fitting/tuning."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parents[1];m=json.loads((R/'models/model.json').read_text());d=pd.read_csv(R/'data/weather.csv',index_col=0,parse_dates=True)
z=np.column_stack([d.T2M,d.PS,d.RH2M,d.WS10M,np.cos(np.deg2rad(d.WD10M)),np.sin(np.deg2rad(d.WD10M))]);X=np.concatenate([pd.DataFrame(z).shift(l).to_numpy() for l in m['lags_hours']],axis=1)
ok=np.isfinite(X).all(axis=1)&pd.DataFrame(z).notna().all(axis=1).rolling(25).sum().eq(25).to_numpy();t=d.index;target=t+pd.Timedelta(hours=3)
W=np.array(m['weights']);b=np.array(m['bias']);Wq=np.array(m['weights_q14'],dtype=np.int64);bq=np.array(m['bias_q8'],dtype=np.int64)
def clip(p):
 p=p.copy();p[:,2]=np.clip(p[:,2],0,100);p[:,3]=np.maximum(p[:,3],0);p[:,4:]=np.clip(p[:,4:],-1,1);return p
rows=[]
for split,start,end in [('validation','2024-01-01','2025-01-01'),('test','2025-01-01','2026-01-01')]:
 mask=ok&(t>=pd.Timestamp(start,tz='UTC'))&(target<pd.Timestamp(end,tz='UTC'));x=X[mask];truth_speed=pd.DataFrame(z).shift(-3).to_numpy()[mask,3]
 q=np.copysign(np.floor(abs(x)*256+.5),x).astype(np.int64);sums=q@Wq.T+(bq<<14)
 if np.any(abs(sums)>=2**47):raise ValueError('48-bit accumulator overflow')
 before=sums//16384;p=clip(x@W.T+b);fixed=clip(np.clip(before,-131072,131071)/256)
 for c,name in enumerate(m['channels']):
  e=fixed[:,c]-p[:,c];physical=before[:,c]/256
  if c==2:clipped=(physical<0)|(physical>100)
  elif c==3:clipped=physical<0
  elif c>=4:clipped=(physical< -1)|(physical>1)
  else:clipped=np.zeros(len(x),dtype=bool)
  rows.append(dict(split=split,target=name,samples=len(x),MAE=float(abs(e).mean()),RMSE=float(np.sqrt((e*e).mean())),max_abs=float(abs(e).max()),signed18_saturation_count=int(((before[:,c]< -131072)|(before[:,c]>131071)).sum()),physical_clip_count=int(clipped.sum())))
 valid=truth_speed>=.5;af=np.rad2deg(np.arctan2(fixed[:,5],fixed[:,4]));ap=np.rad2deg(np.arctan2(p[:,5],p[:,4]));e=((af-ap+180)%360-180)[valid]
 rows.append(dict(split=split,target='direction_deg_fixed_minus_float',samples=int(valid.sum()),MAE=float(abs(e).mean()),RMSE=float(np.sqrt((e*e).mean())),max_abs=float(abs(e).max()),undefined_predicted_vectors=int(((fixed[:,4]==0)&(fixed[:,5]==0)&valid).sum())))
pd.DataFrame(rows).to_csv(R/'reports/numerical_error.csv',index=False);print(pd.DataFrame(rows).to_string(index=False))
