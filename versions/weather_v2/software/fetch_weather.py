"""Fetch immutable yearly NASA POWER hourly responses; retain metadata and gaps."""
from pathlib import Path
import json
import requests
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def main():
    raw=ROOT/'data/raw'; raw.mkdir(parents=True,exist_ok=True)
    frames=[]
    for year in range(2021,2026):
        path=raw/f'power_{year}.json'
        if not path.exists():
            params=dict(parameters='T2M,PS,RH2M,WS10M,WD10M',community='SB',latitude=10.8231,longitude=106.6297,start=f'{year}0101',end=f'{year}1231',format='JSON',**{'time-standard':'UTC'})
            response=requests.get('https://power.larc.nasa.gov/api/temporal/hourly/point',params=params,timeout=180)
            response.raise_for_status(); payload=response.json()
            if set(params['parameters'].split(','))-set(payload.get('properties',{}).get('parameter',{})): raise ValueError('Missing requested parameters')
            path.write_text(json.dumps(payload)); print('Fetched',year,flush=True)
        payload=json.loads(path.read_text())
        df=pd.DataFrame(payload['properties']['parameter'],dtype=float)
        df.index=pd.to_datetime(df.index,format='%Y%m%d%H',utc=True)
        df=df.mask(df==float(payload.get('header',{}).get('fill_value',-999)))
        frames.append(df)
    df=pd.concat(frames).sort_index()
    if df.index.has_duplicates: raise ValueError('Duplicate timestamps')
    df=df.reindex(pd.date_range('2021-01-01','2025-12-31 23:00',freq='h',tz='UTC')).replace([np.inf,-np.inf],np.nan)
    df.index.name='timestamp'; df.to_csv(ROOT/'data/weather.csv')
    print(df.describe().to_string(),flush=True)
if __name__=='__main__': main()
