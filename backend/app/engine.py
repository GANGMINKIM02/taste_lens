import math
AXES=['sweet','salty','sour','umami','spicy','nutty']
NEUTRAL={k:.5 for k in AXES}

def clip(x,lo=0.,hi=1.): return max(lo,min(hi,float(x)))
def vclip(v): return {k:clip(v[k]) for k in AXES}
def dist(a,b): return math.sqrt(sum((float(a[k])-float(b[k]))**2 for k in AXES)/len(AXES))
def match(a,b): return clip(1-dist(a,b))
def blend(a,b,eta): return vclip({k:(1-eta)*a[k]+eta*b[k] for k in AXES})
def row_vec(row): return {k:float(row[k]) for k in AXES}

def pair_loss(u,pairs,beta=8.,lam=.05):
    loss=0.
    for p in pairs:
        s,r=p['selected'],p['rejected']
        z=beta*(dist(u,r)-dist(u,s))
        prob=1/(1+math.exp(-max(-40,min(40,z))))
        loss-=math.log(max(prob,1e-9))
    loss+=lam*sum((u[k]-.5)**2 for k in AXES)
    return loss

def optimize_pairwise(pairs):
    u=dict(NEUTRAL)
    for step in [.20,.10,.05,.02,.01,.005,.001]:
        improved=True; guard=0
        while improved and guard<100:
            guard+=1; improved=False
            base=pair_loss(u,pairs)
            for k in AXES:
                best=u; best_l=base
                for d in (1,-1):
                    c=dict(u); c[k]=clip(c[k]+d*step); l=pair_loss(c,pairs)
                    if l+1e-10<best_l: best,best_l=c,l
                if best is not u: u=best; base=best_l; improved=True
    return vclip(u)

def top_tags(v,n=3):
    labels={'sweet':'달콤','salty':'짭짤','sour':'새콤','umami':'감칠맛','spicy':'매콤','nutty':'고소'}
    return [labels[k] for k in sorted(AXES,key=lambda x:v[x],reverse=True)[:n]]
