from datetime import datetime
from .engine import AXES,clip,row_vec,vclip

def time_segment(dt=None):
    h=(dt or datetime.now()).hour
    if 5<=h<=10:return 'morning'
    if 11<=h<=13:return 'lunch'
    if 14<=h<=16:return 'afternoon'
    if 17<=h<=21:return 'dinner'
    return 'late_night'

def mean_vec(rows):
    if not rows:return None
    return {k:sum(r[k] for r in rows)/len(rows) for k in AXES}
def raw_delta(a,b): return {k:clip(a[k]-b[k],-.15,.15) for k in AXES}
def scale(v,s): return {k:v[k]*s for k in AXES}
def add(*vs): return {k:sum(v.get(k,0) for v in vs) for k in AXES}
def zeros(): return {k:0. for k in AXES}
def global_time(t):
    z=zeros()
    if t=='late_night': z['salty']=.02;z['spicy']=.02
    return z
def global_weather(w):
    z=zeros()
    if w=='rain':z['spicy']=.03;z['umami']=.03
    elif w=='hot':z['sour']=.03;z['spicy']=-.02
    elif w=='cold':z['umami']=.03;z['spicy']=.02
    return z

def compute(base, orders, menu_by_id, place, tseg, weather):
    vectors=[]; by_place=[]; by_time=[]; by_weather=[]
    for o in orders:
        m=menu_by_id.get(o.get('restaurant_menu_id'))
        if not m: continue
        v=row_vec(m); vectors.append(v)
        if o.get('place_type')==place:by_place.append(v)
        if o.get('time_segment')==tseg:by_time.append(v)
        if o.get('weather_type')==weather:by_weather.append(v)
    mall=mean_vec(vectors)
    dp=zeros();dt=global_time(tseg);dw=global_weather(weather)
    if mall and by_place:
        n=len(by_place); r=n/(n+10); dp=scale(raw_delta(mean_vec(by_place),mall),r*.40)
    if mall and by_time:
        n=len(by_time); r=n/(n+12); personal=scale(raw_delta(mean_vec(by_time),mall),r*.30); dt=add(scale(global_time(tseg),1-r),personal)
    if mall and by_weather:
        n=len(by_weather); r=n/(n+20); personal=scale(raw_delta(mean_vec(by_weather),mall),r*.20); dw=add(scale(global_weather(weather),1-r),personal)
    current=vclip(add(base,dp,dt,dw))
    return current,{'place':dp,'time':dt,'weather':dw}
