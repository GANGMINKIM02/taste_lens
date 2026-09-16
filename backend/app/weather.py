from __future__ import annotations
import httpx
async def weather_type(latitude:float, longitude:float):
    url='https://api.open-meteo.com/v1/forecast'
    params={'latitude':latitude,'longitude':longitude,'current':'temperature_2m,precipitation,rain,weather_code'}
    async with httpx.AsyncClient(timeout=10) as c:
        r=await c.get(url,params=params); r.raise_for_status(); cur=r.json().get('current',{})
    t=float(cur.get('temperature_2m',20)); rain=float(cur.get('rain',0) or 0)+float(cur.get('precipitation',0) or 0)
    kind='rain' if rain>0 else 'hot' if t>=28 else 'cold' if t<=8 else 'normal'
    return {'weather_type':kind,'temperature':t,'raw':cur}
