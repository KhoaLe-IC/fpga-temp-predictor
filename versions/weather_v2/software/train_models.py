"""Validation-selected linear forecasting candidates; fixed chronological test holdout."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
LAGS=[0,1,3,6,12,21,24]; CHANNELS=['temperature_C','pressure_kPa','humidity_pct','wind_speed_mps','direction_cos','direction_sin']
def quant(x,scale):return np.copysign(np.floor(np.abs(x)*scale+.5),x).astype(np.int64)
def main():
 d=pd.read_csv(ROOT/'data/weather.csv',index_col=0,parse_dates=True)
 z=np.column_stack([d.T2M,d.PS,d.RH2M,d.WS10M,np.cos(np.deg2rad(d.WD10M)),np.sin(np.deg2rad(d.WD10M))])
 X=np.concatenate([pd.DataFrame(z).shift(l).to_numpy() for l in LAGS],axis=1);Y=pd.DataFrame(z).shift(-3).to_numpy()
 ok=np.isfinite(X).all(1)&np.isfinite(Y).all(1)&pd.DataFrame(z).notna().all(1).rolling(25).sum().eq(25).to_numpy()
 t=d.index; target=t+pd.Timedelta(hours=3)
 masks={'train':ok&(target<pd.Timestamp('2024-01-01',tz='UTC')),'validation':ok&(t>=pd.Timestamp('2024-01-01',tz='UTC'))&(target<pd.Timestamp('2025-01-01',tz='UTC')),'test':ok&(t>=pd.Timestamp('2025-01-01',tz='UTC'))}
 if any(not m.any() for m in masks.values()):raise ValueError('Empty split')
 tr=masks['train']; va=masks['validation']; nf=X.shape[1]
 candidates=[]
 def add(name,W,b):
  if np.max(np.abs(quant(W,16384)))>131071:return
  candidates.append((name,W,b))
 W=np.zeros((6,nf));W[np.arange(6),np.arange(6)]=1;add('persistence',W.copy(),np.zeros(6))
 W=np.zeros((6,nf));W[np.arange(6),LAGS.index(21)*6+np.arange(6)]=1;add('diurnal',W.copy(),np.zeros(6))
 W=np.zeros((6,nf));b=np.zeros(6)
 for c in range(6):
  a0=X[:,c];a3=X[:,LAGS.index(3)*6+c];a21=X[:,LAGS.index(21)*6+c];a24=X[:,LAGS.index(24)*6+c]
  A=np.column_stack([a0-a24,a0-a3,np.ones(len(X))]); w=np.linalg.lstsq(A[tr],Y[tr,c]-a21[tr],rcond=None)[0]
  W[c,c]=w[0]+w[1];W[c,LAGS.index(24)*6+c]=-w[0];W[c,LAGS.index(3)*6+c]=-w[1];W[c,LAGS.index(21)*6+c]=1;b[c]=w[2]
 add('seasonal_OLS_3param',W.copy(),b.copy())
 for joint in [False,True]:
  for alpha in [0.,.001,.1,1.,10.,100.]:
   W=np.zeros((6,nf));b=np.zeros(6)
   for c in range(6):
    ids=np.arange(nf) if joint else np.arange(c,nf,6)
    xx=X[tr][:,ids];mu=xx.mean(0);sd=xx.std(0);sd[sd<1e-10]=1; A=(xx-mu)/sd;ym=Y[tr,c].mean()
    w=np.linalg.lstsq(np.vstack([A,np.sqrt(alpha)*np.eye(len(ids))]),np.r_[Y[tr,c]-ym,np.zeros(len(ids))],rcond=None)[0]/sd
    W[c,ids]=w;b[c]=ym-mu@w
   add(('multivariate' if joint else 'autoregressive')+f'_ridge_{alpha:g}',W,b)
 def clipped(p):
  p=p.copy();p[:,2]=np.clip(p[:,2],0,100);p[:,3]=np.maximum(p[:,3],0);p[:,4:]=np.clip(p[:,4:],-1,1);return p
 def angular(p,y):
  return np.abs((np.rad2deg(np.arctan2(p[:,5],p[:,4])-np.arctan2(y[:,5],y[:,4]))+180)%360-180)
 scores=[];preds=[]
 for name,W,b in candidates:
  p=clipped(X[va]@W.T+b);err=p-Y[va];row=[np.mean(np.abs(err[:,c])) for c in range(4)]
  row.append(float(angular(p,Y[va])[Y[va,3]>=.5].mean()));scores.append(row);preds.append(p)
 pd.DataFrame([{'candidate':c[0],**dict(zip(CHANNELS[:4]+['direction_deg'],s))} for c,s in zip(candidates,scores)]).to_csv(ROOT/'reports/validation_candidates.csv',index=False)
 selected=np.argmin(np.array(scores),axis=0);W=np.zeros((6,nf));b=np.zeros(6);names=[]
 for c in range(6):
  j=int(selected[c if c<4 else 4]);names.append(candidates[j][0]);W[c]=candidates[j][1][c];b[c]=candidates[j][2][c]
 Wq=quant(W,16384);bq=quant(b,256)
 if np.max(abs(bq))>=2**31:raise ValueError('Bias overflow')
 model={'horizon_hours':3,'lags_hours':LAGS,'channels':CHANNELS,'selected_candidates':names,'weights':W.tolist(),'bias':b.tolist(),'weights_q14':Wq.tolist(),'bias_q8':bq.tolist(),'input_width':18,'input_fraction':8,'coefficient_width':18,'coefficient_fraction':14,'split_counts':{k:int(v.sum()) for k,v in masks.items()},'data_sha256':hashlib.sha256((ROOT/'data/weather.csv').read_bytes()).hexdigest(),'direction_policy':'Predict cosine/sine jointly; circular evaluation for truth wind speed >=0.5 m/s; reconstruct atan2(sin,cos).'}
 (ROOT/'models/model.json').write_text(json.dumps(model,indent=2))
 (ROOT/'models/weights.hex').write_text(''.join(f'{int(q)&((1<<18)-1):05x}\n' for q in Wq.ravel()))
 (ROOT/'models/bias.hex').write_text(''.join(f'{int(q)&((1<<32)-1):08x}\n' for q in bq))
 rows=[]
 for split in ['validation','test']:
  mask=masks[split];xf=X[mask];y=Y[mask];p=clipped(xf@W.T+b)
  pq=clipped(((quant(xf,256)@Wq.T+(bq<<14))//16384)/256)
  for label,pred in [('selected_float',p),('selected_fixed',pq),('persistence',clipped(xf[:,:6])),('diurnal',clipped(xf[:,LAGS.index(21)*6:LAGS.index(21)*6+6]))]:
   for c in range(4):
    e=pred[:,c]-y[:,c];rows.append(dict(split=split,model=label,target=CHANNELS[c],MAE=float(abs(e).mean()),RMSE=float(np.sqrt((e*e).mean()))))
   e=angular(pred,y)[y[:,3]>=.5];rows.append(dict(split=split,model=label,target='direction_deg_wind_ge_0.5mps',MAE=float(e.mean()),RMSE=float(np.sqrt((e*e).mean()))))
 pd.DataFrame(rows).to_csv(ROOT/'reports/metrics.csv',index=False)
 print(json.dumps({'selected':names,'split_counts':model['split_counts']},indent=2),flush=True)
 print(pd.DataFrame(rows).to_string(index=False),flush=True)
if __name__=='__main__':main()
