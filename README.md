# AI-First Loyalty Analytics
## Does a $50 loyalty incentive generate incremental profit?

A Slip 18 portfolio case study using a fictional casino and fully synthetic records. The baseline runs from customer generation through SQL cost accounting and statistical inference. The AI-assisted analyst is a separate phase.

### Executive recommendation

**Advance the $50 offer to a controlled pilot in the fictional scenario.** The simulation estimates **$11.58 in incremental 30-day contribution profit per eligible customer assigned the offer** (95% CI $2.95 to $20.22, two-sided p = 0.0086). The offer raised the visit rate from 32.56% to 41.02%. Pre-offer contribution increased by about $23.35 per assigned customer, and redemption and contact absorbed about $11.77 of that lift.

The result depends on redemption economics. At $65 per redemption, the point estimate falls to $8.13 and the interval crosses zero. Regular customers showed a positive effect after adjusting for the three segment tests. That result alone does not establish that regular customers respond better than other tiers. These figures describe one simulated experiment and provide no evidence of real casino performance.

### Reproduce

Use Python 3.9+ with its standard library, including SQLite. Run from this directory.

```sh
python3 -m unittest -v
python3 baseline.py
python3 baseline.py --seed 42 --output results/customers-seed42.csv
```

The default run writes 24,000 rows to `results/customers.csv` and prints the analysis. `analysis.sql` is the exact parameterized SQLite query that Python runs on those records. Dollar values in the source data use integer cents.

### Decision and experiment

- **Population and unit.** One eligible fictional loyalty member per row. The pre-offer frequency tiers are occasional, regular, and frequent. Assume eligibility, consent, and applicable exclusions have already been applied.
- **Assignment.** Randomly shuffle 12,000 offer and 12,000 holdout assignments. Treatment gets one $50 offer with a 30-day expiry. Control receives no campaign contact. Measure both groups over the same 30 days. Assume no crossover, household spillover, overlapping offers, or missing outcomes.
- **Outcome.** Gross gaming and ancillary contribution before modeled variable visit costs and the campaign incentive, less those variable costs, $50 per actual redemption, and $0.25 per treatment assignment. The gross field is modeled revenue retained by the venue before these costs, with gaming revenue conceptually net of payouts. Fixed overhead is excluded. A nonvisitor has zero operating contribution and incurs contact cost if assigned treatment.
- **Decision rule.** Use the lower bound of the primary two-sided 95% interval above $0 as the fictional evidence threshold for advancing to a pilot. The 24,000-member cohort is a demonstration design choice. A live sample-size calculation would need a minimum worthwhile profit lift and historical customer-level variance.

### Data-generating assumptions

| Pre-offer tier | Population mix | Control visit probability | Offer lift | Second-visit probability given a visit | Median gross per visit |
| --- | ---: | ---: | ---: | ---: | ---: |
| Occasional | 55% | 20% | +9 pp | 14% | $105 |
| Regular | 32% | 42% | +8 pp | 32% | $180 |
| Frequent | 13% | 66% | +3.5 pp | 55% | $290 |

A uniform draw determines whether a customer visits under the assigned policy. Among treated visitors, simulated redemption probability is 53% for customers who would visit anyway and 74% for customers induced to visit. This builds in subsidy to existing behavior. The analyst sees actual visits and redemption, while the latent visit propensity stays inside the generator. Per-visit gross revenue is right-skewed lognormal (log-scale standard deviation 0.95), and variable cost is drawn uniformly from $24 to $41. The tier assumptions are illustrative and uncalibrated.

### Statistical walkthrough

1. **Keep the randomized denominator.** Estimate intention-to-treat (ITT) as average net profit in treatment minus average net profit in control. Redemption and visits happen after assignment. Filtering to either group would change the comparison and can make a subsidy look like lift.
2. **Measure sampling noise.** Each arm contributes its sample variance divided by its sample size to the squared standard error. Take the square root, then form the interval as effect ± 1.96 standard errors. The two-sided p-value is the normal tail probability beyond the absolute observed z-score under zero effect. The large-sample approximation allows unequal arm variances and relies on independent customer outcomes with finite variance. Under complete randomization this variance estimator is conservative for the finite-cohort average effect because it omits the unobservable treatment-effect variance term. Heavy tails still make small slices noisy.
3. **Reprice the same experiment.** Recompute every customer's outcome at redemption costs of $35, $50, $65, and $80, holding behavior fixed. The point estimate breaks even at $100.30 per redemption. That is an accounting threshold with sampling uncertainty. The sensitivity intervals are pointwise, and changing the offer's face value could change behavior.
4. **Keep segmentation exploratory.** Compare assigned arms within each of the three predefined tiers. Bonferroni gives each tier an interval at 1 − 0.05/3 confidence and multiplies its raw p-value by three, capped at one. This controls the familywise error rate for the three within-tier tests. Tier-to-tier differences would require a direct interaction contrast.

### Practice the statistics

- Hand-calculate the four-customer ITT in `test_baseline.py`, including the treated customer who never visits. Then try the same calculation using visitors only and explain why the question changes.
- Run a second seed and compare the frequent-tier interval with the occasional-tier interval. Look at both sample size and variation in spend.
- Set the modeled visit lifts to zero in a local copy and rerun. Predict the sign first, using the contact cost and redemption by customers who would have visited anyway.

### Limits

The simulator assumes an offer increases visits and leaves spend per visit and repeat-visit probabilities unchanged conditional on tier. It simplifies casino economics, including zero simulated negative gross gaming revenue per visit. A 30-day window cannot measure later pull-forward, retention, or cannibalization. A live test would need verified assignment, complete outcome and cost capture, and an approved eligibility policy before launch.

### Milestone 2: prospective planning and integrity checks

The original 24,000-customer demonstration above remains **retrospective**. The new [`experiment_plan.md`](experiment_plan.md) is a **proposed design for a distinct future synthetic experiment**, not a document that existed before the original simulation.

- [`power_analysis.py`](power_analysis.py): compute arm sizes based on an independently sourced pre-experiment standard deviation, approved minimum economically meaningful effect, significance level, power and allocation. A larger customer-level SD increases sample size; detecting a smaller effect also increases the required sample. Formula is an approximate large-sample two-sided normal test for mean profit differences, using common SD in both arms.
- [`experiment_validation.py`](experiment_validation.py): check unique IDs, population completeness versus an expected count, assignment counts and an allocation-ratio diagnostic, valid redemption/outcomes, pretreatment tier balance warnings, and exact SQL net-profit accounting. These checks cannot guarantee fair randomization or prove causal validity. Segment imbalance warnings are not automatic evidence of a flawed experiment.
- [`test_milestone.py`](test_milestone.py): tests reference sample-size calculation, monotonicity, invalid parameters, malformed data, allocation warning and row-order independence.

Run from this directory:

```sh
python3 -m unittest -v
python3 power_analysis.py --mde 10 --sd 341 --power .8 --alpha .05
python3 experiment_validation.py
# After running baseline.py, optionally audit a saved output:
python3 experiment_validation.py --csv results/customers.csv --expected-count 24000
```

The `$341` SD in the example command is a **teaching assumption**, not an independently measured preperiod estimate. An actual prospective experiment requires such an estimate, approved business MDE and documented operational thresholds *before* any outcome analysis. These scripts are not production casino decision software and use only synthetic records. The AI-assisted analyst remains an unbuilt future phase.

### Milestone 3: independent historical data → email-only test → decision

Run `python3 campaign_study.py` for a **separate, fictional** end-to-end study. This does not revise or recharacterize the initial 24,000-member analysis. The script (1) generates an independent 20,000-customer no-offer *preperiod*, (2) estimates SD of 30-day net contribution from that data, (3) computes the sample size with `power_analysis.py` using an economically defined MDE, (4) checks feasibility against a 100,000-person fictional eligible email population, (5) runs a **fresh randomized** $50-email-offer experiment with a separate fixed seed, and (6) validates the observations, estimates ITT and applies the predeclared decision rules. Run `python3 -m unittest -q` for the whole test suite.

Outputs in `results/prospective_email/`:
- `independent_preperiod.csv`: synthetic historical net profit by customer, without an offer
- `frozen_design.json`: planning inputs written by the program *before* generating the experiment's outcomes
- `experiment_customers.csv`: separate randomized experiment with the exact scored SQL fields
- `experiment_report.json`: effect, interval, p-value, validation and conditional rollout projection

**Illustrative business assumptions:** 100,000 eligible email members, one $50 redeemed offer, no paid-media targeting, $0.25 allocated contact/operational cost per assignment, and a hypothetical $100,000 fixed cost for wider program administration/analysis/integration. The fictional marketing director and finance partner set an additional minimum net upside after that fixed cost of $900,000 for full-population deployment. Thus the smallest economically worthwhile ITT is **($100,000 + $900,000) / 100,000 = $10 net contribution per assigned member**, with campaign variable costs *already included* in ITT. No real company budget or infrastructure is claimed; even email has nonzero modeled operating costs. A lower actual email-delivery marginal cost would change the economics. The test uses 80% power and two-sided 5% alpha. The fixed rollout expense is **not** deducted in individual-customer ITT; it is applied once only when projecting full-rollout net upside.

**Independence and honesty:** preperiod records and experimental outcomes are drawn with independent RNG seeds, but both use a synthetic process with related assumed spending behavior. The variance estimate is independent of the new experiment's results, not independent empirical proof that assumptions represent real customers. The design file is serialized before experiment outcomes are generated within a single reproducible run; it is not an externally time-stamped registration. The expected 100,000 customer population is also an invented assumption, not a known property database size. Future real work would require independently measured historical outcomes, verified email consent/eligibility, leadership-approved economics, and an experiment registry.

**Future improvement hypothesis (not a verified RWLV capability gap):** assess whether consented paid-audience activation or clean-room/identity capabilities could incrementally outperform an email-only program, only after documenting current marketing infrastructure, integration costs, governance requirements, identity match rates, and incrementality. Do not assume that LiveRamp, mParticle or equivalent capabilities are absent or appropriate.

### Milestone 4: customer segmentation and personalized offer optimization

Read [`SEGMENTATION_CASE_STUDY.md`](SEGMENTATION_CASE_STUDY.md) for the business question, method, measured fictional results, confidence intervals, limitations and recommendation. Run `python3 offer_optimization.py` to generate a randomized four-arm training experiment, learn a policy using **pre-treatment frequency tiers only**, freeze that policy, and independently compare it with blanket $50 and no-offer baselines on 90,000 fresh fictional customers. The selected segment policy is not derived from observed post-treatment visits or redemptions.

Seeded results: learned policy `occasional: $50 / regular: $75 / frequent: $50`; evaluation ITT policy vs blanket $50 **+$5.77 per assigned customer** (95% CI **$0.19 to $11.35**, p **0.0427**). The unadjusted result is marginal and simulation-specific. Policy vs no offer is **+$5.87** (CI **−$0.18 to $11.92**, p **0.0570**). The evaluation sample size was chosen for the demonstration, not prospectively powered. The analyst must not infer that real customers would respond similarly.

Use [`GITHUB_SETUP.md`](GITHUB_SETUP.md) for repository publication steps. Generated customer-level CSVs are ignored by Git because they can be reproduced; summary JSON snapshots and code remain reviewable. No live GitHub publication or AI agent is claimed.