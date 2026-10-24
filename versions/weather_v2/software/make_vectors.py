from pathlib import Path
import json, subprocess
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parents[1];b=R/'build/vectors';b.mkdir(parents=True,exist_ok=True)
m=json.loads((R/'models/model.json').read_text());coeff=''
for c in range(6):coeff+=' '.join(str(m['weights_q14'][c][k*6+c]) for k in range(7))+' '+str(m['bias_q8'][c])+'\n'
(b/'reference_coefficients.txt').write_text(coeff)
subprocess.run(['g++','-std=c++17','-O2','-DSTANDALONE',str(R/'tb/weather_reference.cpp'),'-o',str(b/'reference')],check=True)
d=pd.read_csv(R/'data/weather.csv');d=d[d.timestamp.str.startswith('2025')].iloc[:256]
a=np.column_stack([d.T2M,d.PS,d.RH2M,d.WS10M,np.cos(np.deg2rad(d.WD10M)),np.sin(np.deg2rad(d.WD10M))]);q=np.copysign(np.floor(abs(a)*256+.5),a).astype(int)
# Historical inputs followed by signed extrema exercise hardware ranges beyond the training distribution.
q=np.vstack([q,np.tile([[131071]*6,[-131072]*6],(16,1))])
(b/'inputs.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in q))
with (b/'inputs.txt').open() as f,(b/'vectors.txt').open('w') as g:subprocess.run([str(b/'reference')],cwd=b,stdin=f,stdout=g,check=True)
# Independent NumPy evaluation cross-checks all exported C++ forecast values.
v=np.loadtxt(b/'vectors.txt',dtype=np.int64);W=np.array(m['weights_q14']);bias=np.array(m['bias_q8'])
for i in range(24,len(q)):
 x=np.concatenate([q[i-l] for l in m['lags_hours']]);y=(W@x+(bias<<14))//16384
 y[2]=np.clip(y[2],0,25600);y[3]=max(y[3],0);y[4:]=np.clip(y[4:],-256,256);y=np.clip(y,-131072,131071)
 if not np.array_equal(v[i,7:13],y):raise AssertionError((i,v[i,7:13],y))
print(f'C++/NumPy cross-check PASS: {len(q)-24} forecasts')
