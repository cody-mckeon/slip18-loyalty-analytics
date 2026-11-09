# Milestone 4 — Loyalty segmentation and email-offer optimization

**Portfolio demonstration. Synthetic data only.** No Resorts World customers, systems, budgets, or campaign results were used. This is a deliberately simplified fictional model, not a live targeting recommendation.

## Business question

Instead of sending all eligible email subscribers a $50 offer, could a policy selecting **no offer, $25, $50, or $75**, based on *pre-existing* visit-frequency tiers, create more 30-day contribution profit per eligible customer?

## Method

1. **Learn** from a randomized 160,000-customer fictional four-arm experiment, with 40,000 assigned to each offer. All customers are included, even those who never visit or redeem.
2. Pre-treatment loyalty tiers are **occasional, regular, frequent**. For each segment, calculate average net contribution per randomized offer assignment. Pick the arm with the highest *training* mean. This decision is explicitly descriptive/model-based and can overfit sampling noise.
3. **Freeze** the resulting segment → offer mapping in `results/offer_optimization/frozen_policy.json` before the separate test data are generated.
4. **Evaluate** the fixed policy in an **independent 90,000-customer randomized evaluation**: one third gets the personalized policy; one third gets a blanket $50 offer; one third gets no offer. No post-treatment visitor/redemption filtering, and no policy revisions using the evaluation sample.
5. Compare average 30-day net contribution, inclusive of redeemed incentive and email contact costs. Treat policy versus blanket $50 as the *primary* comparison; policy versus no offer as *secondary*.

## Actual seeded simulation outputs

| Evaluation group | Assigned | Mean net contribution per assigned customer |
|---|---:|---:|
| Personalized segment policy | 30,000 | $125.99 |
| Blanket $50 offer | 30,000 | $120.22 |
| No offer | 30,000 | $120.12 |

The learned **training-only** policy was: **occasional → $50**, **regular → $75**, **frequent → $50**.

| Comparison | Difference in mean net contribution | Approximate two-sided 95% CI | p-value |
|---|---:|---:|---:|
| Personalized minus blanket $50 | **+$5.77/customer** | **$0.19 to $11.35** | **0.0427** |
| Personalized minus no offer (secondary) | +$5.87/customer | −$0.18 to $11.92 | 0.0570 |

**Interpretation:** In this one synthetic evaluation, the learned policy marginally clears the unadjusted 5% significance threshold versus a blanket $50 offer. The benefit is **not** securely established versus no offer by that same threshold. Because the two comparisons are presented, interpret the secondary comparison cautiously; if both were treated as co-primary, multiplicity adjustments would be needed and the first result would not clear a simple Bonferroni 2.5% cutoff. The $5.77 improvement is an estimate, not a guaranteed profit. The simulator's fictional response assumptions largely determine these outcomes.

## Limitations and next checks

- Segments are based on pre-treatment behavior, but higher spending in a tier doesn't itself demonstrate offer *uplift*. The chosen policies are **experimentally learned treatment choices** and **independently evaluated**, not merely customers ranked by predicted spending.
- The training selection is winner-take-all and may overfit; repeated fresh training/evaluation seeds, shrinkage, and a prespecified policy-value objective would improve reliability.
- All four offers share illustrative response rules, including redemption probability; changing offer values may change spending, duration, redemption, or customer sentiment in ways this simulator doesn't capture.
- The 90,000 evaluation size is a demonstration choice, **not prospectively powered from an independent historical variance and policy MDE**. The next version should plan the evaluation's sample size explicitly.
- The no-offer arm has no campaign email or contact cost; costs for paid-media activation and operational rollout are not modeled.
- Independent customer outcomes, stable treatment, no cross-customer interference, complete measurements, and opt-in eligibility are assumed. Real marketing campaigns require validation of these assumptions and privacy/legal review.
- No deployment, dynamic live experimentation, AI agent or external data integrations are claimed. This is a rigorous synthetic analytics case study and a foundation for such future work.

## Reproduce

```bash
python3 -m unittest -q
python3 offer_optimization.py
# For a quick smoke run:
python3 offer_optimization.py --train-n 1200 --eval-n 900 --output results/optimization_smoke
```

Read `offer_optimization.py` for the exact fictional data-generating assumptions. `frozen_policy.json` is serialized before the holdout generation within a reproducible run; it is **not** a third-party preregistration timestamp.