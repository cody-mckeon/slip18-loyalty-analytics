"""Pre-analysis integrity checks for synthetic loyalty experiment rows.

Checks data quality and allocation; does not prove randomization was fair or
that a causal effect exists. Warnings about chance balance are diagnostic.
"""
import argparse
import csv
import math
from collections import Counter
from statistics import NormalDist
from pathlib import Path

from baseline import CONTACT_CENTS, OFFER_CENTS, generate, score

FIELDS = ('customer_id','segment','treatment','visits','gross_cents','variable_cost_cents','redeemed')
NORMAL = NormalDist()


def validate(rows, expected_count=None, treatment_share=0.5, expected_segments=('occasional','regular','frequent')):
    if not 0 < treatment_share < 1:
        raise ValueError('treatment_share must be between 0 and 1')
    rows=list(rows)
    errors=[]
    warnings=[]
    if expected_count is not None and len(rows) != expected_count:
        errors.append(f'Expected {expected_count} rows; found {len(rows)}')
    ids=set()
    groups=Counter()
    segment_counts={0:Counter(),1:Counter()}
    for index,row in enumerate(rows,1):
        if len(row)!=len(FIELDS):
            errors.append(f'Row {index}: wrong field count')
            continue
        cid,segment,arm,visits,gross,cost,redeemed=row
        if cid in ids:
            errors.append(f'Row {index}: duplicate customer_id {cid}')
        ids.add(cid)
        if not all(type(x) is int for x in (cid,arm,visits,gross,cost,redeemed)):
            errors.append(f'Row {index}: numeric columns must be integers')
            continue
        if cid<=0 or arm not in (0,1) or visits<0 or gross<0 or cost<0 or redeemed not in (0,1):
            errors.append(f'Row {index}: invalid numeric value')
            continue
        if segment not in expected_segments:
            errors.append(f'Row {index}: unknown segment {segment}')
        if redeemed>arm or (visits==0 and (gross!=0 or cost!=0 or redeemed!=0)) or (redeemed and visits==0):
            errors.append(f'Row {index}: inconsistent outcome or redemption')
        groups[arm]+=1
        segment_counts[arm][segment]+=1
    if groups[0]==0 or groups[1]==0:
        errors.append('Both assignment groups must have customers')
    # Sample ratio mismatch is a diagnostic, not a hard error: allocation
    # counts may be deliberately fixed rather than Bernoulli randomized.
    n=groups[0]+groups[1]
    if n:
        z=(groups[1]-n*treatment_share)/math.sqrt(n*treatment_share*(1-treatment_share))
        srm_p=2*(1-NORMAL.cdf(abs(z)))
        if srm_p<0.001:
            warnings.append(f'Assignment ratio unexpected: treatment {groups[1]}/{n} (SRM p={srm_p:.3g}); check design')
    else:
        srm_p=None
    # Standardized differences for baseline categories, using binary indicators.
    # Imbalance can occur by chance; never silently exclude observed customers.
    if groups[0] and groups[1]:
        for seg in expected_segments:
            p0=segment_counts[0][seg]/groups[0]
            p1=segment_counts[1][seg]/groups[1]
            pooled=(p0*(1-p0)+p1*(1-p1))/2
            smd=(p1-p0)/math.sqrt(pooled) if pooled>0 else 0.0
            if abs(smd)>0.1:
                warnings.append(f'Pre-treatment segment {seg}: standardized difference={smd:+.3f}; investigate')
    # Independently recompute accounting from every valid row; SQL scoring
    # is checked only if structural validation succeeded.
    if not errors:
        scored=score(rows)
        by_id={record['customer_id']:record for record in scored}
        for cid,seg,arm,visits,gross,cost,redeemed in rows:
            expected=gross-cost-redeemed*OFFER_CENTS-arm*CONTACT_CENTS
            if by_id[cid]['net_cents']!=expected:
                errors.append(f'Customer {cid}: net accounting mismatch')
    return {'passed':not errors, 'errors':errors, 'warnings':warnings,
            'total':len(rows), 'control':groups[0], 'treatment':groups[1], 'srm_p':srm_p}


def main():
    parser=argparse.ArgumentParser(description='Validate assignment, data integrity and financial accounting')
    parser.add_argument('--csv',type=Path,help='Input generated customers.csv; omit to generate the default synthetic cohort')
    parser.add_argument('--expected-count',type=int,default=24000)
    args=parser.parse_args()
    if args.csv:
        with args.csv.open(newline='') as handle:
            reader=csv.DictReader(handle)
            if reader.fieldnames!=list(FIELDS):
                parser.error('CSV column names/order do not match original baseline')
            rows=[tuple(int(r[f]) if f not in ('segment',) else r[f] for f in FIELDS) for r in reader]
    else:
        rows=list(generate())
    report=validate(rows,expected_count=args.expected_count)
    print(f"Integrity {'PASS' if report['passed'] else 'FAIL'} | n={report['total']:,} | treatment={report['treatment']:,} | control={report['control']:,}")
    for issue in report['errors']:
        print('ERROR:',issue)
    for warning in report['warnings']:
        print('WARNING:',warning)
    if not report['passed']:
        raise SystemExit(1)

if __name__=='__main__':
    main()