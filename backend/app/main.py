import os,uuid
from datetime import datetime,timezone
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field
from typing import Optional
from .db import get_db,configured
from .engine import AXES,row_vec,match,blend,optimize_pairwise,top_tags,clip
from .context import compute,time_segment
from .onboarding import choose_next,to_pairs
from .solar import analyze_review
from .weather import weather_type as fetch_weather
from .assets import public_asset_base_url

app=FastAPI(title='Taste Lens API',version='4.3.0')
origins=[x.strip() for x in os.getenv('CORS_ORIGINS','http://localhost:3000').split(',') if x.strip()]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=True,allow_methods=['*'],allow_headers=['*'])

class OnboardChoice(BaseModel): left_food_id:str;right_food_id:str;selected_food_id:str
class RecommendReq(BaseModel): user_id:str;scope:str='auto';category:Optional[str]=None;place_type:str='home';time_segment:Optional[str]=None;weather_type:str='normal';temperature:Optional[float]=None
class OrderReq(BaseModel): user_id:str;restaurant_menu_id:str;place_type:str='home';time_segment:Optional[str]=None;weather_type:str='normal';temperature:Optional[float]=None
class ReviewReq(BaseModel): user_id:str;order_id:str;rating:int=Field(ge=1,le=5);review_text:str=Field(min_length=1,max_length=4000)
class RecommendationSelection(BaseModel): selected_food_id:Optional[str]=None;selected_restaurant_id:Optional[str]=None;selected_restaurant_menu_id:Optional[str]=None

def db():
    try:return get_db()
    except RuntimeError as e:raise HTTPException(503,str(e))
def profile(user_id):
    r=db().table('user_profiles').select('*').eq('user_id',user_id).single().execute().data
    if not r:raise HTTPException(404,'user profile not found')
    return r

def get_context(user_id,place,weather,tseg=None):
    p=profile(user_id);base=row_vec(p);tseg=tseg if tseg in {'morning','lunch','afternoon','dinner','late_night'} else time_segment()
    orders=db().table('orders').select('restaurant_menu_id,place_type,time_segment,weather_type').eq('user_id',user_id).eq('status','completed').execute().data or []
    mids=list({o['restaurant_menu_id'] for o in orders if o.get('restaurant_menu_id')})
    menu_by={}
    if mids:
        rows=db().table('restaurant_menus').select('restaurant_menu_id,sweet,salty,sour,umami,spicy,nutty').in_('restaurant_menu_id',mids).execute().data or []
        menu_by={r['restaurant_menu_id']:r for r in rows}
    u,deltas=compute(base,orders,menu_by,place,tseg,weather)
    return u,tseg,deltas,p

@app.get('/health')
def health():
    upstage=bool(os.getenv('UPSTAGE_API_KEY','').strip())
    return {'ok':True,'supabase_configured':configured(),'upstage_configured':upstage,'solar_configured':upstage,'asset_base_url':public_asset_base_url(),'runtime_image_generation':False,'architecture':'Vercel Next.js /api -> FastAPI -> Supabase PostgreSQL / Supabase Storage / Upstage Solar Pro 4 / Open-Meteo'}

@app.post('/v1/users')
def create_user():
    uid=str(uuid.uuid4()); d=db();d.table('users').insert({'user_id':uid}).execute();d.table('user_profiles').insert({'user_id':uid}).execute();return {'user_id':uid}

@app.get('/v1/users/{user_id}/profile')
def get_profile(user_id:str):
    p=profile(user_id);return {'user_id':user_id,'vector':row_vec(p),'vector_version':p['vector_version']}

@app.get('/v1/onboarding/{user_id}/next')
def onboarding_next(user_id:str):
    d=db();foods=d.table('foods').select('*').execute().data or []
    responses=d.table('onboarding_responses').select('*').eq('user_id',user_id).order('question_index').execute().data or []
    if len(responses)>=10:return {'completed':True,'profile':get_profile(user_id)}
    pair=choose_next(foods,responses)
    for side in ('left','right'):
        f=pair[side]; pair[side]={'food_id':f['food_id'],'name':f['name'],'category':f['category'],'image_url':f['food_image_url']}
    return {'completed':False,**pair}

@app.post('/v1/onboarding/{user_id}/choice')
def onboarding_choice(user_id:str,req:OnboardChoice):
    d=db(); prior=d.table('onboarding_responses').select('question_index').eq('user_id',user_id).execute().data or []
    q=len(prior)+1
    if q>10:raise HTTPException(409,'onboarding already completed')
    if req.selected_food_id not in {req.left_food_id,req.right_food_id}:raise HTTPException(400,'selected food must be one of the pair')
    d.table('onboarding_responses').insert({'user_id':user_id,'question_index':q,'left_food_id':req.left_food_id,'right_food_id':req.right_food_id,'selected_food_id':req.selected_food_id}).execute()
    responses=d.table('onboarding_responses').select('*').eq('user_id',user_id).order('question_index').execute().data or []
    if len(responses)==10:
        foods=d.table('foods').select('*').execute().data or []; u=optimize_pairwise(to_pairs(responses,foods));p=profile(user_id)
        d.table('user_profiles').update({**u,'vector_version':1,'baseline_at':datetime.now(timezone.utc).isoformat()}).eq('user_id',user_id).execute()
        return {'completed':True,'u_base':u,'vector_version':1}
    return {'completed':False,'answered':len(responses)}

@app.post('/v1/recommendations')
def recommend(req:RecommendReq):
    d=db();u,tseg,deltas,p=get_context(req.user_id,req.place_type,req.weather_type,req.time_segment)
    q=d.table('foods').select('*')
    if req.scope=='category' and req.category:q=q.eq('category',req.category)
    foods=q.execute().data or []
    ranked=sorted([{'food_id':f['food_id'],'name':f['name'],'category':f['category'],'image_url':f['food_image_url'],'match':match(u,row_vec(f)),'tags':top_tags(row_vec(f))} for f in foods],key=lambda x:x['match'],reverse=True)
    if req.scope=='auto':
        selected=[];counts={}
        for x in ranked:
            if counts.get(x['category'],0)>=2:continue
            selected.append(x);counts[x['category']]=counts.get(x['category'],0)+1
            if len(selected)==5:break
        ranked=selected
    else:ranked=ranked[:5]
    snap={'place_type':req.place_type,'time_segment':tseg,'weather_type':req.weather_type,'temperature':req.temperature,'deltas':deltas}
    rec_id=str(uuid.uuid4());d.table('recommendations').insert({'recommendation_id':rec_id,'user_id':req.user_id,'scope':req.scope,'category':req.category,'candidate_ids':[x['food_id'] for x in ranked],'scores':{x['food_id']:x['match'] for x in ranked},'context_snapshot':snap,'user_vector_snapshot':u,'vector_version':p['vector_version']}).execute()
    return {'recommendation_id':rec_id,'u_current':u,'context':snap,'foods':ranked}

@app.post('/v1/recommendations/{recommendation_id}/selection')
def log_recommendation_selection(recommendation_id:str,req:RecommendationSelection):
    payload={k:v for k,v in req.model_dump().items() if v is not None}
    if not payload: raise HTTPException(400,'at least one selection field is required')
    d=db(); row=d.table('recommendations').select('recommendation_id').eq('recommendation_id',recommendation_id).execute().data or []
    if not row: raise HTTPException(404,'recommendation not found')
    d.table('recommendations').update(payload).eq('recommendation_id',recommendation_id).execute()
    return {'ok':True,**payload}

@app.get('/v1/assets/status')
def asset_status():
    d=db();foods=d.table('foods').select('food_image_url').execute().data or [];restaurants=d.table('restaurants').select('restaurant_image_url').execute().data or [];menus=d.table('restaurant_menus').select('menu_image_url').execute().data or []
    return {'runtime_generation':False,'base_url':public_asset_base_url(),'food_rows':len(foods),'restaurant_rows':len(restaurants),'menu_rows':len(menus),'unique_food_urls':len({x.get('food_image_url') for x in foods}),'unique_restaurant_urls':len({x.get('restaurant_image_url') for x in restaurants}),'unique_menu_urls':len({x.get('menu_image_url') for x in menus})}

@app.get('/v1/foods/{food_id}/restaurants')
def food_restaurants(food_id:str,user_id:str,place_type:str='home',weather_type:str='normal',time_segment:Optional[str]=None):
    d=db();u,_,_,_=get_context(user_id,place_type,weather_type,time_segment)
    menus=d.table('restaurant_menus').select('*').eq('food_id',food_id).eq('is_available',True).execute().data or []
    rids=list({m['restaurant_id'] for m in menus});rs=d.table('restaurants').select('*').in_('restaurant_id',rids).execute().data if rids else []
    rm={r['restaurant_id']:r for r in rs or []};out=[]
    for m in menus:
        r=rm.get(m['restaurant_id']);
        if not r:continue
        out.append({'restaurant_id':r['restaurant_id'],'restaurant_name':r['name'],'restaurant_image_url':r['restaurant_image_url'],'restaurant_menu_id':m['restaurant_menu_id'],'menu_name':m['menu_name'],'taste_match':match(u,row_vec(m)),'rating':r['rating'],'review_count':r['review_count'],'delivery_minutes':r['delivery_minutes'],'delivery_fee':r['delivery_fee']})
    return {'restaurants':sorted(out,key=lambda x:x['taste_match'],reverse=True)}

@app.get('/v1/restaurants/{restaurant_id}')
def restaurant_detail(restaurant_id:str,user_id:str,place_type:str='home',weather_type:str='normal',time_segment:Optional[str]=None):
    d=db();u,_,_,_=get_context(user_id,place_type,weather_type,time_segment)
    r=d.table('restaurants').select('*').eq('restaurant_id',restaurant_id).single().execute().data
    if not r:raise HTTPException(404,'restaurant not found')
    menus=d.table('restaurant_menus').select('*').eq('restaurant_id',restaurant_id).eq('is_available',True).execute().data or []
    return {'restaurant':r,'menus':[{'restaurant_menu_id':m['restaurant_menu_id'],'food_id':m['food_id'],'name':m['menu_name'],'description':m['menu_description'],'image_url':m['menu_image_url'],'price':m['price'],'section':m['menu_section'],'representative':m['is_representative'],'popular':m['is_popular'],'taste_match':match(u,row_vec(m))} for m in menus]}

@app.post('/v1/orders')
def create_order(req:OrderReq):
    d=db();m=d.table('restaurant_menus').select('*').eq('restaurant_menu_id',req.restaurant_menu_id).single().execute().data
    if not m:raise HTTPException(404,'menu not found')
    p=profile(req.user_id);before=row_vec(p);prev=d.table('orders').select('order_id').eq('user_id',req.user_id).eq('restaurant_menu_id',req.restaurant_menu_id).eq('status','completed').limit(1).execute().data or []
    repeat=bool(prev);after=blend(before,row_vec(m),.08 if repeat else .05);vb=int(p['vector_version']);va=vb+1;tseg=req.time_segment if req.time_segment in {'morning','lunch','afternoon','dinner','late_night'} else time_segment();oid=str(uuid.uuid4())
    snap={'place_type':req.place_type,'time_segment':tseg,'weather_type':req.weather_type,'temperature':req.temperature}
    d.table('orders').insert({'order_id':oid,'user_id':req.user_id,'restaurant_menu_id':req.restaurant_menu_id,'place_type':req.place_type,'time_segment':tseg,'weather_type':req.weather_type,'context_snapshot':snap,'user_vector_before':before,'user_vector_after':after,'vector_version_before':vb,'vector_version_after':va,'repeat_order':repeat,'taste_update_applied':True,'status':'completed','completed_at':datetime.now(timezone.utc).isoformat()}).execute()
    d.table('user_profiles').update({**after,'vector_version':va}).eq('user_id',req.user_id).execute()
    return {'order_id':oid,'repeat_order':repeat,'user_vector_before':before,'user_vector_after':after,'vector_version':va}

@app.get('/v1/users/{user_id}/orders')
def order_history(user_id:str):
    d=db();orders=d.table('orders').select('*').eq('user_id',user_id).order('created_at',desc=True).execute().data or []
    mids=list({o['restaurant_menu_id'] for o in orders});menus=d.table('restaurant_menus').select('restaurant_menu_id,restaurant_id,menu_name,menu_image_url,price').in_('restaurant_menu_id',mids).execute().data if mids else []
    mm={m['restaurant_menu_id']:m for m in menus or []};rids=list({m['restaurant_id'] for m in menus or []});rs=d.table('restaurants').select('restaurant_id,name').in_('restaurant_id',rids).execute().data if rids else [];rm={r['restaurant_id']:r['name'] for r in rs or []}
    reviews=d.table('reviews').select('order_id').eq('user_id',user_id).execute().data or [];reviewed={r['order_id'] for r in reviews}
    return {'orders':[{'order_id':o['order_id'],'created_at':o['created_at'],'repeat_order':o['repeat_order'],'reviewed':o['order_id'] in reviewed,**(mm.get(o['restaurant_menu_id']) or {}),'restaurant_name':rm.get((mm.get(o['restaurant_menu_id']) or {}).get('restaurant_id'))} for o in orders]}

@app.post('/v1/reviews')
async def create_review(req:ReviewReq):
    d=db();order=d.table('orders').select('*').eq('order_id',req.order_id).eq('user_id',req.user_id).single().execute().data
    if not order or order.get('status')!='completed':raise HTTPException(400,'completed order required')
    existing=d.table('reviews').select('review_id,status').eq('order_id',req.order_id).execute().data or []
    menu=d.table('restaurant_menus').select('*').eq('restaurant_menu_id',order['restaurant_menu_id']).single().execute().data;p=profile(req.user_id);before=row_vec(p)
    if existing:
        current=existing[0]
        if current.get('status')!='failed':
            raise HTTPException(409,'review already exists')
        # PRD v4.3 retry rule: reuse the same review_id after a failed Solar analysis.
        rid=current['review_id']
        d.table('review_evidence').delete().eq('review_id',rid).execute()
        d.table('reviews').update({'rating':req.rating,'review_text':req.review_text,'status':'processing','user_vector_before':before,'user_vector_after':before,'user_update_applied':False,'restaurant_update_applied':False,'updated_at':datetime.now(timezone.utc).isoformat()}).eq('review_id',rid).execute()
    else:
        rid=str(uuid.uuid4())
        d.table('reviews').insert({'review_id':rid,'order_id':req.order_id,'user_id':req.user_id,'restaurant_id':menu['restaurant_id'],'restaurant_menu_id':menu['restaurant_menu_id'],'rating':req.rating,'review_text':req.review_text,'status':'processing','user_vector_before':before,'user_vector_after':before}).execute()
    try:analysis=await analyze_review(req.review_text)
    except Exception as e:
        d.table('reviews').update({'status':'failed'}).eq('review_id',rid).execute();raise HTTPException(502,f'Solar Pro 4 review analysis failed: {e}')
    evidence=[]
    for x in analysis['menu_taste_claims']:
        evidence.append({'review_id':rid,'claim_type':'menu_taste','axis':x['axis'],'level':x['level'],'comparative':x['comparative'],'confidence':x['confidence'],'evidence_text':x['evidence_text'],'model':analysis['model'],'prompt_version':analysis['prompt_version']})
    for x in analysis['user_preference_claims']:
        evidence.append({'review_id':rid,'claim_type':'user_preference','axis':x['axis'],'direction':x['direction'],'confidence':x['confidence'],'evidence_text':x['evidence_text'],'model':analysis['model'],'prompt_version':analysis['prompt_version']})
    if evidence:d.table('review_evidence').insert(evidence).execute()
    # RestaurantMenu learning: aggregate weighted evidence for this peer food, convert to percentile center, max ±.15 from Food prior.
    menu_applied=False
    claims=[x for x in analysis['menu_taste_claims'] if x['level']!=0]
    if claims:
        axis_scores={}
        for x in claims:axis_scores.setdefault(x['axis'],[]).append(x['level']*(1.2 if x['comparative'] else 1.0)*x['confidence'])
        peers=d.table('restaurant_menus').select('*').eq('food_id',menu['food_id']).execute().data or []
        food=d.table('foods').select('*').eq('food_id',menu['food_id']).single().execute().data
        update={};count=int(menu.get('evidence_count') or 0)+1;conf=count/(count+10)
        for axis,vals in axis_scores.items():
            q=sum(vals)/len(vals); peer_values=sorted([float(p[axis]) for p in peers]); rank=sum(v<=float(menu[axis])+q*.01 for v in peer_values);pct=rank/max(1,len(peer_values));center=2*pct-1;delta=.15*conf*center;update[axis]=clip(float(food[axis])+delta)
        update.update({'evidence_count':count,'vector_version':int(menu.get('vector_version') or 1)+1,'source':'review_evidence'});d.table('restaurant_menus').update(update).eq('restaurant_menu_id',menu['restaurant_menu_id']).execute();menu_applied=True
    # User learning only explicit preference confidence >= .75, eta=.02.
    after=dict(before);user_applied=False
    for x in analysis['user_preference_claims']:
        if x['confidence']<.75:continue
        axis=x['axis'];target=clip(after[axis]+(.10 if x['direction']=='prefer_more' else -.10));after[axis]=.98*after[axis]+.02*target;user_applied=True
    if user_applied:
        va=int(p['vector_version'])+1;d.table('user_profiles').update({**after,'vector_version':va}).eq('user_id',req.user_id).execute()
    d.table('reviews').update({'status':'completed','user_vector_after':after,'user_update_applied':user_applied,'restaurant_update_applied':menu_applied}).eq('review_id',rid).execute()
    return {'review_id':rid,'status':'completed','analysis':analysis,'user_vector_before':before,'user_vector_after':after,'user_update_applied':user_applied,'restaurant_update_applied':menu_applied}

@app.get('/v1/weather')
async def weather(latitude:float,longitude:float):
    enabled=os.getenv('OPEN_METEO_ENABLED','true').strip().lower() in {'1','true','yes','on'}
    if not enabled:
        raise HTTPException(503,'Open-Meteo integration is disabled by OPEN_METEO_ENABLED')
    return await fetch_weather(latitude,longitude)
