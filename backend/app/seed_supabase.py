import hashlib
from .engine import AXES,clip
from .assets import asset_url

CATS={
'한식':['제육볶음','김치찌개','순두부찌개','비빔밥','물냉면','불고기','된장찌개','삼겹살','육개장','설렁탕','부대찌개','오징어볶음','비빔냉면','해물파전'],
'중식':['짜장면','짬뽕','마파두부','탕수육','마라탕','양꼬치','볶음밥','유산슬'],
'일식':['돈코츠라멘','쇼유라멘','돈가스','초밥','규동','가라아게','우동','메밀소바'],
'치킨':['후라이드치킨','양념치킨','간장치킨','매운양념치킨','마늘치킨','허니치킨','파닭','숯불치킨'],
'피자':['페퍼로니피자','치즈피자','고구마피자','불고기피자','하와이안피자','포테이토피자','고르곤졸라피자','핫치킨피자'],
'분식':['떡볶이','라볶이','순대','튀김','김밥','쫄면','어묵','만두'],
'카페·디저트':['초콜릿케이크','치즈케이크','크로플','도넛','팥빙수','아이스크림','소금빵','베이글'],
'기타·글로벌':['쌀국수','팟타이','타코','햄버거','파스타','샐러드','커리','케밥']}
PRESETS={'김치찌개':(.25,.65,.55,.78,.62,.18),'제육볶음':(.48,.72,.18,.76,.70,.22),'순두부찌개':(.18,.60,.20,.75,.62,.14),'삼겹살':(.12,.50,.08,.67,.08,.75),'초밥':(.25,.48,.50,.72,.08,.12),'돈코츠라멘':(.12,.70,.07,.90,.16,.68),'떡볶이':(.70,.58,.10,.62,.82,.10),'마라탕':(.08,.72,.12,.82,.95,.42),'고구마피자':(.78,.42,.06,.50,.04,.46),'치즈케이크':(.82,.20,.28,.30,0,.58)}
COUNTS={'한식':10,'중식':5,'일식':5,'치킨':4,'피자':4,'분식':4,'카페·디저트':4,'기타·글로벌':5}
NAMES={'한식':['청춘찌개','서울밥상','한성국밥','불맛공방','냉면마을','온기백반','맛나한상','정담식당','담소키친','한결식탁'],'중식':['홍콩반점 1998','상하이웍','마라공방','용문각','만리향'],'일식':['멘야하루','스시도리','카츠연구소','우동정원','도쿄식탁'],'치킨':['바삭연구소','치킨살롱','불꽃치킨','골든윙'],'피자':['오븐클럽','피자스튜디오','도우하우스','치즈팩토리'],'분식':['오늘분식','떡볶이공방','골목김밥','분식대장'],'카페·디저트':['스윗테이블','버터룸','카페모먼트','베이크온'],'기타·글로벌':['월드키친','사이공테이블','타코스팟','커리하우스','버거랩']}
# 112 menu assets = Korean 14*4 + all other foods*1; add 8 second variants = exactly 120.
EXTRA_MENU_VARIANTS={'마라탕','돈코츠라멘','초밥','양념치킨','고구마피자','떡볶이','치즈케이크','햄버거'}

def h(s):return int(hashlib.sha256(s.encode()).hexdigest()[:12],16)
def slug_id(prefix,n):return f'{prefix}-{n:03d}'
def vector(name):
    if name in PRESETS:return dict(zip(AXES,PRESETS[name]))
    x=h(name);return {k:round(.08+(((x>>(i*7))&255)/255)*.78,3) for i,k in enumerate(AXES)}

def menu_variant_count(food):
    if food['category']=='한식': return 4
    return 2 if food['name'] in EXTRA_MENU_VARIANTS else 1

def make():
    foods=[];fi=0
    for cat,names in CATS.items():
      for name in names:
        fi+=1;v=vector(name);fid=slug_id('food',fi)
        foods.append({'food_id':fid,'name':name,'category':cat,'food_image_url':asset_url(f'foods/{fid}.webp'),**v,'vector_version':1,'source':'seed','rationale':'MVP recommendation prior calibrated for relative rank consistency'})
    bycat={c:[f for f in foods if f['category']==c] for c in CATS}
    restaurants=[];rid=0;assign={}
    for cat,count in COUNTS.items():
      cf=bycat[cat]
      for i in range(count):
        rid+=1;rest_id=slug_id('rest',rid); pc=6 if cat=='한식' else 5
        ids=[cf[(i*2+j)%len(cf)]['food_id'] for j in range(pc)]
        assign[rest_id]=list(dict.fromkeys(ids))
        restaurants.append({'restaurant_id':rest_id,'name':NAMES[cat][i],'category':cat,'restaurant_type':('찌개·백반' if i<3 else '고기·볶음' if i<6 else '종합한식') if cat=='한식' else f'{cat} 전문','restaurant_image_url':asset_url(f'restaurants/{rest_id}.webp'),'rating':round(4.5+(rid%5)*.08,1),'review_count':120+(rid*47)%1800,'delivery_minutes':f'{20+(rid%4)*5}~{30+(rid%4)*5}분','delivery_fee':0 if rid%4==0 else 1000+(rid%3)*500,'minimum_order':12000+(rid%3)*2000})
    # All foods >=3 restaurants; Korean foods >=4 (conservative interpretation of core Korean constraint).
    for f in foods:
      rs=[r for r in restaurants if r['category']==f['category']]; target=4 if f['category']=='한식' else 3
      carriers=[r for r in rs if f['food_id'] in assign[r['restaurant_id']]]
      for r in rs:
        if len(carriers)>=target:break
        if f['food_id'] not in assign[r['restaurant_id']]:assign[r['restaurant_id']].append(f['food_id']);carriers.append(r)
    fm={f['food_id']:f for f in foods};menus=[];mid=0;occurrence={}
    for r in restaurants:
      for j,fid in enumerate(assign[r['restaurant_id']]):
        mid+=1;f=fm[fid]; delta=((h(r['restaurant_id']+fid)%21)-10)/100
        v={k:round(clip(f[k]+delta*(-.45 if i%2 else 1)),3) for i,k in enumerate(AXES)}
        occurrence[fid]=occurrence.get(fid,0)+1
        variant=((occurrence[fid]-1)%menu_variant_count(f))+1
        asset_key=f'{fid}-v{variant:02d}'
        menus.append({'restaurant_menu_id':slug_id('menu',mid),'restaurant_id':r['restaurant_id'],'food_id':fid,'menu_name':f['name'],'menu_description':f"{r['name']}만의 {'깊고 균형 잡힌' if j%2 else '풍미를 살린'} {f['name']}",'menu_image_url':asset_url(f'menus/{asset_key}.webp'),'price':8000+((mid*1300)%9000),**v,'menu_section':'대표 메뉴' if j==0 else '메인' if j<4 else '사이드','is_representative':j==0,'is_popular':j<2,'is_available':True,'vector_version':1,'evidence_count':0,'source':'food_prior'})
    return foods,restaurants,menus

def seed():
    from .db import get_db
    db=get_db();foods,restaurants,menus=make()
    db.table('foods').upsert(foods).execute();db.table('restaurants').upsert(restaurants).execute();db.table('restaurant_menus').upsert(menus).execute()
    print({'foods':len(foods),'restaurants':len(restaurants),'menus':len(menus),'unique_food_images':len({f['food_image_url'] for f in foods}),'unique_restaurant_images':len({r['restaurant_image_url'] for r in restaurants}),'unique_menu_images':len({m['menu_image_url'] for m in menus})})
if __name__=='__main__':seed()
