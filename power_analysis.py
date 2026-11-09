"""Approximate prospective two-sample difference-in-means sample-size planner.

Only use SD from independent pre-campaign/pilot data. This is not post-hoc power.
Standard library only. Equal SD assumed for treatment and control outcomes.
"""
import argparse
import math
from statistics import NormalDist

NORMAL = NormalDist()


def plan(mde, sd, power=0.80, alpha=0.05, treatment_to_control=1.0):
    """Return conservative (rounded-up) arm counts for a two-sided normal test.

    Formula: n_control = ((z_(1-alpha/2)+z_power)^2 * sd^2
                          * (1+1/r)) / mde^2
    where r = n_treatment / n_control.
    """
    args = [mde, sd, power, alpha, treatment_to_control]
    if not all(math.isfinite(x) for x in args):
        raise ValueError('Inputs must be finite numbers')
    if mde <= 0 or sd <= 0 or not 0 < power < 1 or not 0 < alpha < 1 or treatment_to_control <= 0:
        raise ValueError('mde, sd, and allocation ratio must be positive; alpha and power must be between 0 and 1')
    zcrit = NORMAL.inv_cdf(1 - alpha / 2)
    zpower = NORMAL.inv_cdf(power)
    n_control = math.ceil((zcrit + zpower)**2 * sd**2 * (1 + 1/treatment_to_control) / mde**2)
    n_treatment = math.ceil(n_control * treatment_to_control)
    return {'control':n_control, 'treatment':n_treatment, 'total':n_control+n_treatment,
            'mde':mde, 'sd':sd, 'power':power, 'alpha':alpha, 'ratio':treatment_to_control}


def main():
    parser=argparse.ArgumentParser(description='Pre-campaign two-sided two-arm sample-size planner')
    parser.add_argument('--mde',type=float,required=True,help='Minimum worthwhile profit difference ($/assigned customer)')
    parser.add_argument('--sd',type=float,required=True,help='Independent pre-campaign estimate of customer net contribution SD ($)')
    parser.add_argument('--power',type=float,default=0.80)
    parser.add_argument('--alpha',type=float,default=0.05)
    parser.add_argument('--ratio',type=float,default=1.0,help='Treatment size divided by control size')
    args=parser.parse_args()
    result=plan(args.mde,args.sd,args.power,args.alpha,args.ratio)
    print(f"Plan: {result['treatment']:,} treatment + {result['control']:,} control = {result['total']:,} total")
    print(f"Assumptions: MDE=${args.mde:.2f}/assigned customer, independent SD=${args.sd:.2f}, "
          f"power={args.power:.0%}, two-sided alpha={args.alpha:.1%}, treatment/control ratio={args.ratio:g}")
    print('Approximation only; validate SD, operational feasibility and sensitivity before committing to a live campaign.')

if __name__=='__main__':
    main()