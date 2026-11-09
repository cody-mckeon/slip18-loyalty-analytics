"""Generate fictional experiment data, score it in SQL, and estimate ITT effects."""
import argparse
import csv
import math
import random
import sqlite3
import statistics
from pathlib import Path

SEGMENTS = ("occasional", "regular", "frequent")
OFFER_CENTS = 5000
CONTACT_CENTS = 25
NORMAL = statistics.NormalDist()
SQL = Path(__file__).with_name("analysis.sql").read_text()
COLUMNS = ("customer_id", "segment", "treatment", "visits",
           "gross_cents", "variable_cost_cents", "redeemed")


def generate(seed=20261106, size=24000):
    if size < 2 or size % 2:
        raise ValueError("Size must be positive and even")
    rng = random.Random(seed)
    assignments = [0, 1] * (size // 2)
    rng.shuffle(assignments)
    for customer_id, treatment in enumerate(assignments, 1):
        tier = rng.choices(range(3), (0.55, 0.32, 0.13))[0]
        base_visit = (0.20, 0.42, 0.66)[tier]
        lift = (0.09, 0.08, 0.035)[tier]
        # Shared latent propensity creates both natural and offer-induced visits.
        propensity = rng.random()
        visits = 0
        gross = cost = redeemed = 0
        if propensity < base_visit + treatment * lift:
            visits = 1 + (rng.random() < (0.14, 0.32, 0.55)[tier])
            redeemed = int(treatment and rng.random() < (0.74 if propensity >= base_visit else 0.53))
            for _ in range(visits):
                gross += round(rng.lognormvariate(math.log((105, 180, 290)[tier]), 0.95) * 100)
                cost += rng.randint(2400, 4100)
        yield customer_id, SEGMENTS[tier], treatment, visits, gross, cost, redeemed


def score(rows):
    with sqlite3.connect(":memory:") as db:
        db.execute("""
            CREATE TABLE customers (
                customer_id INTEGER PRIMARY KEY,
                segment TEXT NOT NULL CHECK(segment IN ('occasional','regular','frequent')),
                treatment INTEGER NOT NULL CHECK(treatment IN (0,1)),
                visits INTEGER NOT NULL CHECK(visits >= 0),
                gross_cents INTEGER NOT NULL CHECK(gross_cents >= 0),
                variable_cost_cents INTEGER NOT NULL CHECK(variable_cost_cents >= 0),
                redeemed INTEGER NOT NULL CHECK(redeemed IN (0,1) AND redeemed <= treatment),
                CHECK(visits > 0 OR (gross_cents = 0 AND variable_cost_cents = 0 AND redeemed = 0))
            )
        """)
        db.executemany("INSERT INTO customers VALUES (?,?,?,?,?,?,?)", rows)
        db.row_factory = sqlite3.Row
        return db.execute(SQL, {"offer_cents": OFFER_CENTS, "contact_cents": CONTACT_CENTS}).fetchall()


def estimate(rows, redemption_cost=50, alpha=0.05):
    arms = [[], []]
    for row in rows:
        net = (row["net_cents"] / 100
               + row["redeemed"] * (OFFER_CENTS / 100 - redemption_cost))
        arms[row["treatment"]].append(net)
    control, treatment = arms
    if min(map(len, arms)) < 2:
        raise ValueError("Each arm needs at least two customers")
    effect = statistics.mean(treatment) - statistics.mean(control)
    se = math.sqrt(sum(statistics.variance(arm) / len(arm) for arm in arms))
    critical = NORMAL.inv_cdf(1 - alpha / 2)
    p_value = math.erfc(abs(effect / se) / math.sqrt(2)) if se else float(effect == 0)
    return effect, effect - critical * se, effect + critical * se, p_value


def summarize(result):
    effect, low, high, p_value = result
    return f"${effect:.2f} [${low:.2f}, ${high:.2f}], p={p_value:.4g}"


def report(rows):
    primary = estimate(rows)
    print("SYNTHETIC EXPERIMENT | profit per assigned customer")
    for arm in (0, 1):
        group = [r for r in rows if r["treatment"] == arm]
        print(f"Arm {arm} | n={len(group):,} | visit rate={statistics.mean(r['visits'] > 0 for r in group):.2%}"
              f" | redemption={statistics.mean(r['redeemed'] for r in group):.2%}"
              f" | pre-offer=${statistics.mean(r['pre_offer_cents'] for r in group)/100:.2f}"
              f" | net=${statistics.mean(r['net_cents'] for r in group)/100:.2f}")
    print("Primary ITT, 95% CI:", summarize(primary))
    print("Redemption cost sensitivity (pointwise 95% CIs)")
    for cost in (35, 50, 65, 80):
        print(f"  ${cost}: {summarize(estimate(rows, cost))}")
    treatment_redemption = statistics.mean(r["redeemed"] for r in rows if r["treatment"])
    if treatment_redemption:
        print(f"Point-estimate break-even cost per redemption: ${50 + primary[0] / treatment_redemption:.2f}")
    print("Exploratory segments (Bonferroni familywise 95% CIs, raw p-values)")
    for segment in SEGMENTS:
        group = [r for r in rows if r["segment"] == segment]
        result = estimate(group, alpha=0.05 / len(SEGMENTS))
        print(f"  {segment} (n={len(group):,}): {summarize(result)}"
              f" | adjusted p={min(1, result[3] * len(SEGMENTS)):.4g}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=20261106)
    parser.add_argument("--output", type=Path, default=Path("results/customers.csv"))
    args = parser.parse_args()
    rows = list(generate(args.seed))
    scored = score(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(COLUMNS)
        writer.writerows(rows)
    report(scored)


if __name__ == "__main__":
    main()