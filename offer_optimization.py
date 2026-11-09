"""Synthetic multi-arm email incentive optimization with independent policy evaluation.

Training: randomized assignment among $0/$25/$50/$75 offer policies.
Policy: pre-treatment loyalty segment -> offer arm, learned from train sample only.
Evaluation: independent customers randomized to learned policy, blanket $50, or no offer.

All parameters are fictional, NOT inferred from actual casino customer data.
"""
import argparse
import csv
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

SEGMENTS = ('occasional', 'regular', 'frequent')
SEGMENT_WEIGHTS = (0.55, 0.32, 0.13)
OFFERS = (0, 25, 50, 75)
CONTACT_COST = 0.25
BASE_VISIT = (0.20, 0.42, 0.66)
# Absolute lift in visit probability by segment and offer; fictional simulation parameters.
VISIT_LIFT = (
    (0, 0.035, 0.09, 0.11),
    (0, 0.045, 0.08, 0.10),
    (0, 0.012, 0.035, 0.040),
)
REPEAT_RATE = (0.14, 0.32, 0.55)
MEDIAN_GROSS = (105, 180, 290)


def customer(rng, segment, offer):
    """One policy outcome. $0 = no email, no incentive, no contact cost."""
    tier = SEGMENTS.index(segment)
    offer_idx = OFFERS.index(offer)
    propensity = rng.random()
    visits = 0
    gross_cents = cost_cents = redeemed = 0
    if propensity < BASE_VISIT[tier] + VISIT_LIFT[tier][offer_idx]:
        visits = 1 + int(rng.random() < REPEAT_RATE[tier])
        # Never redeem in no-offer arm; treated: induced visitor more likely to redeem.
        if offer:
            probability = 0.74 if propensity >= BASE_VISIT[tier] else 0.53
            redeemed = int(rng.random() < probability)
        for _ in range(visits):
            gross_cents += round(rng.lognormvariate(math.log(MEDIAN_GROSS[tier]), 0.95) * 100)
            cost_cents += rng.randint(2400, 4100)
    net_cents = gross_cents - cost_cents - redeemed * offer * 100 - (25 if offer else 0)
    return visits, redeemed, net_cents / 100


def make_training(seed=20270110, n=160000):
    if n <= 0 or n % len(OFFERS):
        raise ValueError('Training size must be positive and a multiple of four')
    rng = random.Random(seed)
    assignments = list(OFFERS) * (n // len(OFFERS))
    rng.shuffle(assignments)
    out = []
    for i, offer in enumerate(assignments, 1):
        segment = rng.choices(SEGMENTS, SEGMENT_WEIGHTS)[0]
        visits, redeemed, net = customer(rng, segment, offer)
        out.append(dict(customer_id=i, segment=segment, offer=offer,
                        visits=visits, redeemed=redeemed, net_profit=net))
    return out


def mean_ci(vals):
    if len(vals)<2:
        raise ValueError('Need at least two observations')
    mean=statistics.mean(vals)
    se=statistics.stdev(vals)/math.sqrt(len(vals))
    return {'n':len(vals),'mean':mean,'lower_95':mean-1.9599639845*se,
            'upper_95':mean+1.9599639845*se,'se':se}


def learn_policy(training):
    """Select highest observed segment-arm mean. Never access the evaluation dataset."""
    grouped=defaultdict(list)
    for r in training:
        if r['segment'] not in SEGMENTS or r['offer'] not in OFFERS:
            raise ValueError('Unknown pretreatment segment or offer')
        grouped[(r['segment'], r['offer'])].append(r['net_profit'])
    estimates={}
    for seg in SEGMENTS:
        for offer in OFFERS:
            estimates[(seg,offer)]=mean_ci(grouped[(seg,offer)])
    policy={seg:max(OFFERS, key=lambda offer: estimates[(seg,offer)]['mean']) for seg in SEGMENTS}
    return policy, estimates


def evaluate(seed, n, policy):
    """Independent randomized policy A/B/C test. No post-assignment filtering."""
    if n<6 or n%3:
        raise ValueError('Evaluation size must be >=6 and a multiple of 3')
    if set(policy)!=set(SEGMENTS) or any(x not in OFFERS for x in policy.values()):
        raise ValueError('Invalid policy')
    rng=random.Random(seed)
    groups=['personalized','blanket_50','no_offer']*(n//3)
    rng.shuffle(groups)
    out=[]
    for customer_id, group in enumerate(groups,1):
        seg=rng.choices(SEGMENTS, SEGMENT_WEIGHTS)[0]
        offer=policy[seg] if group=='personalized' else (50 if group=='blanket_50' else 0)
        visits, redeemed, net=customer(rng, seg, offer)
        out.append(dict(customer_id=customer_id, segment=seg, assignment=group,
                        offer=offer, visits=visits, redeemed=redeemed, net_profit=net))
    return out


def compare(a,b):
    aa=mean_ci(a); bb=mean_ci(b)
    diff=aa['mean']-bb['mean']
    se=math.sqrt(aa['se']**2+bb['se']**2)
    z=diff/se if se else float('inf')
    return {'effect':diff,'se':se,'lower_95':diff-1.9599639845*se,
            'upper_95':diff+1.9599639845*se, 'p_two_sided':math.erfc(abs(z)/math.sqrt(2))}


def summarize(evaluation):
    groups={g:[r['net_profit'] for r in evaluation if r['assignment']==g]
            for g in ('personalized','blanket_50','no_offer')}
    if any(len(group)<2 for group in groups.values()):
        raise ValueError('Insufficient customers in evaluation')
    return {'groups':{name:mean_ci(vals) for name,vals in groups.items()},
            'personalized_vs_blanket50':compare(groups['personalized'],groups['blanket_50']),
            'personalized_vs_no_offer':compare(groups['personalized'],groups['no_offer'])}


def run(path, train_n=160000, eval_n=90000):
    output=Path(path)
    output.mkdir(parents=True,exist_ok=True)
    training=make_training(n=train_n)
    policy, estimates=learn_policy(training)
    # Freeze policy before evaluation. Existing policy file is overwritten only with same seeded process.
    frozen={'stage':'Training complete; policy frozen before holdout outcomes generated',
            'training_seed':20270110,'evaluation_seed':20270111,
            'train_size':train_n,'eval_size':eval_n,
            'offer_arms_dollars':list(OFFERS),'pre_treatment_segments':list(SEGMENTS),
            'policy':policy,'selection_method':'Maximize training mean net contribution within each segment',
            'primary_comparison':'personalized_vs_blanket50',
            'secondary_comparison':'personalized_vs_no_offer',
            'alpha_primary':0.05,'no_early_peeking':True,
            'independent_holdout':True,'fictional':True}
    (output/'frozen_policy.json').write_text(json.dumps(frozen,indent=2)+'\n')
    evaluation=evaluate(seed=20270111,n=eval_n,policy=policy)
    summary=summarize(evaluation)
    for name,rows,columns in [
        ('training.csv',training,('customer_id','segment','offer','visits','redeemed','net_profit')),
        ('evaluation.csv',evaluation,('customer_id','segment','assignment','offer','visits','redeemed','net_profit'))]:
        with (output/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(rows)
    summary['policy']=policy
    summary['training_segment_offer_means']={f'{seg}_${offer}':v for (seg,offer),v in estimates.items()}
    (output/'evaluation_report.json').write_text(json.dumps(summary,indent=2)+'\n')
    print('Learned policy:',policy)
    for name,g in summary['groups'].items(): print(f'{name}: n={g["n"]:,}, average profit=${g["mean"]:.2f}')
    for name in ('personalized_vs_blanket50','personalized_vs_no_offer'):
        r=summary[name]
        print(f'{name}: ITT=${r["effect"]:.2f}, CI=[${r["lower_95"]:.2f}, ${r["upper_95"]:.2f}], p={r["p_two_sided"]:.4g}')
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--output',default='results/offer_optimization')
    p.add_argument('--train-n',type=int,default=160000)
    p.add_argument('--eval-n',type=int,default=90000)
    a=p.parse_args()
    run(a.output,a.train_n,a.eval_n)