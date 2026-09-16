from datetime import datetime
from app.engine import dist,match,blend
from app.context import compute,time_segment

def v(x=.5): return {k:x for k in ['sweet','salty','sour','umami','spicy','nutty']}

def test_identity():
    assert dist(v(),v())==0
    assert match(v(),v())==1

def test_order_blend():
    assert abs(blend(v(.5),v(1),.05)['sweet']-.525)<1e-12

def test_rain_cold_start_prior():
    current,deltas=compute(v(.5),[],{},'home','dinner','rain')
    assert abs(current['spicy']-.53)<1e-12
    assert abs(current['umami']-.53)<1e-12
    assert deltas['place']['sweet']==0

def test_time_segments():
    assert time_segment(datetime(2026,1,1,6,0))=='morning'
    assert time_segment(datetime(2026,1,1,12,0))=='lunch'
    assert time_segment(datetime(2026,1,1,15,0))=='afternoon'
    assert time_segment(datetime(2026,1,1,19,0))=='dinner'
    assert time_segment(datetime(2026,1,1,23,0))=='late_night'
