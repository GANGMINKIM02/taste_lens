from .engine import AXES,row_vec,optimize_pairwise,dist

def _foodmap(foods):return {f['food_id']:f for f in foods}
def to_pairs(responses, foods):
    fm=_foodmap(foods); out=[]
    for r in responses:
        a=fm[r['left_food_id']];b=fm[r['right_food_id']];s=fm[r['selected_food_id']];rej=b if s['food_id']==a['food_id'] else a
        out.append({'selected':row_vec(s),'rejected':row_vec(rej)})
    return out

def choose_next(foods,responses):
    used_pairs={tuple(sorted((r['left_food_id'],r['right_food_id']))) for r in responses}
    counts={f['food_id']:0 for f in foods}
    coverage={k:0. for k in AXES}; evidence={k:0. for k in AXES}
    fm=_foodmap(foods)
    for r in responses:
        a,b=fm[r['left_food_id']],fm[r['right_food_id']]
        counts[a['food_id']]+=1;counts[b['food_id']]+=1
        for k in AXES:coverage[k]+=abs(a[k]-b[k])
        s=fm[r['selected_food_id']];rej=b if s['food_id']==a['food_id'] else a
        for k in AXES:evidence[k]+=abs(s[k]-rej[k])
    q=len(responses)+1
    u=optimize_pairwise(to_pairs(responses,foods)) if responses else {k:.5 for k in AXES}
    best=None;best_score=-1e9
    target=min(AXES,key=lambda k:evidence[k]) if q>=7 else None
    for i,a in enumerate(foods):
        for b in foods[i+1:]:
            pair=tuple(sorted((a['food_id'],b['food_id'])))
            if pair in used_pairs:continue
            max_rep=1 if q<=6 else 2
            if counts[a['food_id']]>=max_rep or counts[b['food_id']]>=max_rep:continue
            if q<=6:
                score=sum((1/(.1+coverage[k]))*abs(a[k]-b[k]) for k in AXES)
            else:
                dA=dist(u,row_vec(a));dB=dist(u,row_vec(b));score=abs(a[target]-b[target])-.7*abs(dA-dB)
            if score>best_score:best_score=score;best=(a,b)
    if not best:
        raise RuntimeError('No valid onboarding pair remains')
    return {'question_index':q,'left':best[0],'right':best[1]}
