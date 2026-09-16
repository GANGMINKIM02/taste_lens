from collections import Counter,defaultdict
from app.seed_supabase import make

def test_seed_constraints():
    foods,restaurants,menus=make()
    assert len(foods)==70
    assert len(restaurants)==41
    assert 210<=len(menus)<=250
    by_food=Counter(m['food_id'] for m in menus)
    assert min(by_food.values())>=3
    assert min(by_food[f['food_id']] for f in foods if f['category']=='한식')>=4
    by_rest=Counter(m['restaurant_id'] for m in menus)
    assert min(by_rest.values())>=4
    assert len({f['food_image_url'] for f in foods})==70
    assert len({r['restaurant_image_url'] for r in restaurants})==41
    assert len({m['menu_image_url'] for m in menus})==120
    rest_images=defaultdict(list)
    for m in menus: rest_images[m['restaurant_id']].append(m['menu_image_url'])
    assert all(len(v)==len(set(v)) for v in rest_images.values())
    food_images=defaultdict(set)
    for m in menus: food_images[m['food_id']].add(m['menu_image_url'])
    assert min(len(food_images[f['food_id']]) for f in foods if f['category']=='한식')>=4
