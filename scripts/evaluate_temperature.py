"""Reproduce held-out temperature metrics without retraining or changing model selection."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parents[1]
d=pd.read_csv(R/'data/processed/temperature.csv',index_col=0,parse_dates=True);t=d.iloc[:,0].asfreq('h');m=json.loads((R/'software/models_cpp/model.json').read_text())
a=pd.DataFrame({'now':t,'t3':t.shift(3),'t21':t.shift(21),'t24':t.shift(24),'truth':t.shift(-3)})
a=a[t.rolling(25).count().eq(25)].dropna()
train=a[a.index+pd.Timedelta(hours=3)<pd.Timestamp('2024-01-01',tz='UTC')]
fit,_,rank,_=np.linalg.lstsq(np.column_stack([train['now']-train.t24,train['now']-train.t3,np.ones(len(train))]),train.truth-train.t21,rcond=None)
if rank!=3 or not np.allclose(fit,[m['a'],m['b'],m['c']],rtol=0,atol=1e-9):raise ValueError('Saved model does not match training data')
print('Saved coefficient / training-data audit PASS; training rows:',len(train))
def q(x,s):return np.copysign(np.floor(abs(x)*s+.5),x).astype(np.int64)
w=q(np.array([m['a'],m['b'],m['c']]),np.array([16384,16384,256]));rows=[];numerical=[]
for split,start,end in [('validation','2024-01-01','2025-01-01'),('test','2025-01-01','2026-01-01')]:
 x=a[(a.index>=pd.Timestamp(start,tz='UTC'))&(a.index+pd.Timedelta(hours=3)<pd.Timestamp(end,tz='UTC'))]
 n,v3,v21,v24=[x[k].to_numpy() for k in ['now','t3','t21','t24']];truth=x.truth.to_numpy()
 p=v21+m['a']*(n-v24)+m['b']*(n-v3)+m['c'];qn,q3,q21,q24=[q(v,256) for v in [n,v3,v21,v24]]
 sums=w[0]*(qn-q24)+w[1]*(qn-q3)+((q21+w[2])<<14)
 unbounded=sums//16384
 fixed=np.clip(unbounded,-32768,32767)/256
 input_quantized=q21/256+m['a']*(qn-q24)/256+m['b']*(qn-q3)/256+m['c']
 continuous_quantized=sums.astype(np.float64)/(16384*256)
 floored=unbounded/256
 saturation_count=int(np.count_nonzero((unbounded< -32768)|(unbounded>32767)))
 for stage,error in [('input_quantization',input_quantized-p),('coefficient_quantization_given_quantized_inputs',continuous_quantized-input_quantized),('final_floor_shift',floored-continuous_quantized),('total_fixed_minus_float',fixed-p)]:
  numerical.append(dict(split=split,stage=stage,samples=len(x),MAE_C=float(abs(error).mean()),RMSE_C=float(np.sqrt((error*error).mean())),max_abs_C=float(abs(error).max()),bias_C=float(error.mean()),saturation_count=saturation_count))
 if np.any(floored-continuous_quantized < -1/256) or np.any(floored-continuous_quantized>0):raise AssertionError('Final floor error bound')
 for name,pred in [('OLS_float',p),('OLS_fixed',fixed),('persistence',n),('diurnal',v21)]:
  e=pred-truth;rows.append(dict(split=split,model=name,samples=len(x),MAE_C=float(abs(e).mean()),RMSE_C=float(np.sqrt((e*e).mean())),bias_C=float(e.mean())))
 rows.append(dict(split=split,model='fixed_minus_float',samples=len(x),MAE_C=float(abs(fixed-p).mean()),RMSE_C=float(np.sqrt(((fixed-p)**2).mean())),max_abs_C=float(abs(fixed-p).max())))
pd.DataFrame(rows).to_csv(R/'docs/reports/temperature_metrics.csv',index=False)
pd.DataFrame(numerical).to_csv(R/'docs/reports/temperature_numerical_error.csv',index=False)
(R/'docs/reports/temperature_evaluation_manifest.json').write_text(json.dumps({'model':m,'quantized_coefficients':w.tolist(),'data_sha256':hashlib.sha256((R/'data/processed/temperature.csv').read_bytes()).hexdigest(),'test_policy':'Saved model evaluated unchanged; no fitting in this script.'},indent=2))
print(pd.DataFrame(rows).to_string(index=False))
