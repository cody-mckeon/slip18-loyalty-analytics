"""Reproducible fictional email loyalty campaign: independent preperiod -> plan -> test.

No real customer information. The historical generator is deliberately independent
of randomized treatment results and uses a different RNG seed. The synthetic
world's parameters are illustrative, not calibrated against a real business.
"""
import argparse
import csv
import json
import math
import random
import statistics
from pathlib import Path

from baseline import SEGMENTS, generate, score, estimate, OFFER_CENTS, CONTACT_CENTS
from experiment_validation import validate
from power_analysis import plan

HISTORICAL_SEED = 20250401
EXPERIMENT_SEED = 20261201
HISTORICAL_N = 20000
ELIGIBLE_POPULATION = 100000
# Hypothetical commercial agreement: $100k fixed rollout/analytics cost,
# require at least $900k additional contribution above that -> $1m / 100k.
FIXED_ROLLOUT_COST = 100000
MINIMUM_NET_UPSIDE = 900000
MDE = (FIXED_ROLLOUT_COST + MINIMUM_NET_UPSIDE) / ELIGIBLE_POPULATION
POWER = 0.80
ALPHA = 0.05


def historical_customers(seed=HISTORICAL_SEED, count=HISTORICAL_N):
    """Independent 30-day preperiod outcomes, when no one gets this offer.

    Kept as an independent no-offer process rather than filtering the original
    completed treatment/control experiment. Output is (id, tier, visits, profit).
    """
    if count < 2:
        raise ValueError('Need >=2 preperiod observations')
    rng = random.Random(seed)
    for customer_id in range(1, count + 1):
        tier = rng.choices(range(3), (0.55, 0.32, 0.13))[0]
        visits = 0
        gross_cents = cost_cents = 0
        if rng.random() < (0.20, 0.42, 0.66)[tier]:
            visits = 1 + int(rng.random() < (0.14, 0.32, 0.55)[tier])
            for _ in range(visits):
                gross_cents += round(rng.lognormvariate(math.log((105, 180, 290)[tier]), 0.95) * 100)
                cost_cents += rng.randint(2400, 4100)
        yield customer_id, SEGMENTS[tier], visits, (gross_cents - cost_cents) / 100


def create_plan(history):
    """Must be called before inspecting prospectively simulated outcomes."""
    history = list(history)
    sd = statistics.stdev(row[3] for row in history)
    planned = plan(mde=MDE, sd=sd, power=POWER, alpha=ALPHA)
    if planned['total'] > ELIGIBLE_POPULATION:
        return {'feasible': False, 'preperiod_sd': sd, 'preperiod_n': len(history),
                'plan': planned, 'eligible_population': ELIGIBLE_POPULATION}
    return {'feasible': True, 'preperiod_sd': sd, 'preperiod_n': len(history),
            'plan': planned, 'eligible_population': ELIGIBLE_POPULATION}


def conduct(plan_record):
    if not plan_record['feasible']:
        raise ValueError('Planned test exceeds available eligible population; renegotiate design before simulation')
    if plan_record['plan']['control'] != plan_record['plan']['treatment']:
        raise ValueError('This demonstration generator requires 1:1 allocation')
    rows = list(generate(seed=EXPERIMENT_SEED, size=plan_record['plan']['total']))
    checks = validate(rows, expected_count=len(rows))
    if not checks['passed']:
        raise ValueError('Data validation failed: ' + '; '.join(checks['errors']))
    scored = score(rows)
    effect, lower, upper, p = estimate(scored)
    by_arm = {}
    for arm in (0, 1):
        group = [r for r in scored if r['treatment'] == arm]
        by_arm[str(arm)] = {
            'assigned': len(group),
            'visits_rate': statistics.mean(r['visits'] > 0 for r in group),
            'redemption_rate': statistics.mean(r['redeemed'] for r in group),
            'net_profit_per_customer': statistics.mean(r['net_cents'] for r in group)/100,
        }
    reached_stat_threshold = lower > 0
    reached_economic_point_target = effect >= MDE
    return {'experiment_seed': EXPERIMENT_SEED, 'checks': checks,
            'groups': by_arm, 'effect': effect, 'lower_95': lower,
            'upper_95': upper, 'p_value': p,
            'statistical_criterion_met': reached_stat_threshold,
            'economic_point_target_met': reached_economic_point_target,
            'scenario_rollout_contribution_at_100k': effect * ELIGIBLE_POPULATION,
            'scenario_rollout_net_after_fixed_cost': effect * ELIGIBLE_POPULATION - FIXED_ROLLOUT_COST,
            'decision': ('Advance for further controlled evaluation' if reached_stat_threshold and reached_economic_point_target
                         else 'Do not expand on these criteria; reassess economics and uncertainty'),
            'scored_rows': scored}


def run(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    history = list(historical_customers())
    with (output/'independent_preperiod.csv').open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(('customer_id', 'segment', 'visits', 'net_contribution_dollars'))
        writer.writerows(history)
    design = create_plan(history)
    with (output/'frozen_design.json').open('w') as f:
        json.dump({'stage': 'specified before experiment outcome simulation',
                   'historical_seed': HISTORICAL_SEED, 'historical_n': len(history),
                   'preperiod_sd': design['preperiod_sd'], 'eligible_population': ELIGIBLE_POPULATION,
                   'channel': 'email only', 'offer_face_value': OFFER_CENTS/100,
                   'treatment_contact_cost': CONTACT_CENTS/100,
                   'fixed_rollout_cost': FIXED_ROLLOUT_COST,
                   'minimum_net_upside_after_fixed_cost': MINIMUM_NET_UPSIDE,
                   'business_mde': MDE, 'power': POWER, 'alpha': ALPHA,
                   'test_counts': design['plan'], 'feasible': design['feasible'],
                   'prespecified_decision': 'require positive lower 95% CI AND point estimate >= MDE'},f,indent=2)
    if not design['feasible']:
        raise RuntimeError('Sample exceeds eligible pool; saved design but did not run test')
    result = conduct(design)
    with (output/'experiment_customers.csv').open('w',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(('customer_id','segment','treatment','visits','pre_offer_cents','redeemed','net_cents'))
        writer.writerows(tuple(r) for r in result.pop('scored_rows'))
    with (output/'experiment_report.json').open('w') as f:
        json.dump(result,f,indent=2)
    print(f'Historical: {len(history):,} independent no-campaign preperiod observations; SD=${design["preperiod_sd"]:.2f}')
    print(f'Planning: ${MDE:.2f} minimum worthwhile ITT; {design["plan"]["total"]:,} customers ({design["plan"]["treatment"]:,} offer / {design["plan"]["control"]:,} holdout)')
    print(f'Experiment: ITT=${result["effect"]:.2f}, 95% CI [${result["lower_95"]:.2f}, ${result["upper_95"]:.2f}], p={result["p_value"]:.3g}')
    print('Decision:', result['decision'])
    return design, result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',default='results/prospective_email')
    args = parser.parse_args()
    run(args.output)