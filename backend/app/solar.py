import os,json,httpx
from typing import Any,Dict

PROMPT_VERSION='prd-v4.3-review-v1'
SYSTEM_PROMPT='''You analyze Korean food reviews for Taste Lens. Return ONLY valid JSON with exactly two arrays: menu_taste_claims and user_preference_claims. Valid axes: sweet,salty,sour,umami,spicy,nutty. A menu claim has axis, level (-2,-1,0,1,2), comparative (boolean), confidence (0..1), evidence_text. A user preference claim has axis, direction (prefer_more|prefer_less), confidence (0..1), evidence_text. Never infer a user preference from a mere taste description. Ignore non-taste statements such as quantity, service, delivery speed, and generic '맛있어요'.'''

async def analyze_review(text:str)->Dict[str,Any]:
    key=os.getenv('UPSTAGE_API_KEY','').strip()
    if not key:
        raise RuntimeError('UPSTAGE_API_KEY is required for PRD-compliant review analysis')
    base=os.getenv('UPSTAGE_API_BASE_URL','https://api.upstage.ai/v1').rstrip('/')
    model=os.getenv('UPSTAGE_MODEL','solar-pro4')
    payload={'model':model,'messages':[{'role':'system','content':SYSTEM_PROMPT},{'role':'user','content':text}],'temperature':0.1,'response_format':{'type':'json_object'}}
    async with httpx.AsyncClient(timeout=45) as c:
        r=await c.post(f'{base}/chat/completions',headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'},json=payload)
        r.raise_for_status(); data=json.loads(r.json()['choices'][0]['message']['content'])
    menu=[]
    for x in data.get('menu_taste_claims',[]):
        if x.get('axis') in {'sweet','salty','sour','umami','spicy','nutty'} and int(x.get('level',0)) in {-2,-1,0,1,2}:
            menu.append({'axis':x['axis'],'level':int(x['level']),'comparative':bool(x.get('comparative',False)),'confidence':max(0,min(1,float(x.get('confidence',0)))),'evidence_text':str(x.get('evidence_text',''))[:300]})
    user=[]
    for x in data.get('user_preference_claims',[]):
        if x.get('axis') in {'sweet','salty','sour','umami','spicy','nutty'} and x.get('direction') in {'prefer_more','prefer_less'}:
            user.append({'axis':x['axis'],'direction':x['direction'],'confidence':max(0,min(1,float(x.get('confidence',0)))),'evidence_text':str(x.get('evidence_text',''))[:300]})
    return {'menu_taste_claims':menu,'user_preference_claims':user,'model':model,'prompt_version':PROMPT_VERSION}
