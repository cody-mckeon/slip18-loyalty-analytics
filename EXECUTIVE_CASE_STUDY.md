# Fictional loyalty email campaign | Executive decision brief

**Project:** Slip 18 AI-First Loyalty Analytics · **Data:** entirely synthetic, not Resorts World data · **Status:** completed teaching simulation, not a proposed real-world campaign

## Business decision

Should a fictional casino test and potentially expand a $50 email loyalty offer based on **incremental 30-day contribution profit** rather than open rate, visit rate or redeemed-customer spend? The business assumes 100,000 eligible, consented members. No paid ads are included.

The fictional Director of Database Marketing and Finance agree on an illustrative financial hurdle: $100,000 incremental fixed cost for full-scale administration, plus at least $900,000 in net incremental upside after that fixed cost. Dividing the combined $1,000,000 hurdle by 100,000 eligible customers gives a **$10 minimum worthwhile incremental contribution per assigned member**. It is a business assumption, not a statistically derived quantity or a real casino requirement.

## How the experiment was planned

An **independent 20,000-member no-offer synthetic preperiod** estimated customer-level 30-day contribution-profit SD at **$317.71**. With 80% power, two-sided alpha of 5%, a $10 minimum detectable difference and equal arms, the approximate calculated design required **31,690 customers**: 15,845 assigned the email offer and 15,845 held out. Sample sizing was generated from preperiod data before simulated experiment outcomes. This is feasible within the hypothetical 100,000-person pool.

All assigned customers count, whether they visited or redeemed. Each treated member incurs an assumed $0.25 contact/allocated operating cost; each actual redemption incurs $50. These are illustrative costs. Random assignment and a contemporaneous holdout reduce the risk of mistaking existing visit behavior for offer impact.

## New simulated experiment results

- Estimated ITT incremental 30-day contribution profit: **+$17.25 per assigned member**.
- Two-sided 95% confidence interval: **+$9.93 to +$24.57**.
- Statistical criterion: **met** (lower CI bound above zero).
- Illustrative economic point-estimate criterion: **met** ($17.25 above $10).
- Automated experiment integrity and cost-accounting checks: **passed**.

**Recommendation for this fictional scenario:** advance to further controlled evaluation rather than launch automatically. The cost and profit assumptions are artificial, and one 30-day test cannot establish sustained retention, long-term profitability, selection effects after rollout, or whether results generalize to all 100,000 members.

The point estimate would imply approximately **$1.725 million** in additional contribution if the same effect held across all 100,000 members, or **$1.625 million after the fictional $100,000 fixed rollout cost**. These are conditional scenario projections, **not observed total revenue or a forecast validated against reality**. The full rollout has uncertainty and could alter behavior.

## What we would say to leadership

> "We compared customers randomly offered the promotion against customers who received no offer. We counted everyone targeted, including people who never visited. The estimated incremental contribution was $17.25 per customer after modeled redemption and contact costs. The statistical interval remained positive, and the estimate exceeded our fictional $10 economic hurdle. I'd recommend a controlled next-stage evaluation and cost validation before wider deployment."

## Questions a director should ask

**Why 31,690?** Because before testing we used independent preperiod variability, an economically worthwhile $10 difference, 80% detection power and a 5% false-positive threshold. Smaller worthwhile improvements require larger samples.

**Why not report redeemed customers only?** Redemption is influenced by the treatment. Filtering after assignment breaks the original randomized comparison; the decision being evaluated is *sending* an offer to the eligible population.

**Why email rather than paid audiences?** Email is the assumed initial channel and avoids adding uncertain paid-media audience acquisition costs to the demonstration. A future paid-audience hypothesis is appropriate, but must begin with actual architecture discovery, consent/identity constraints and a separate incrementality design.

**What might reverse the recommendation?** Higher redemption or operating cost, adverse long-term pull-forward/cannibalization, data quality failures, different targeting population, or weaker effects in replication.

## Portfolio claims and limits

The project demonstrates synthetic experiment design, independent preperiod variance estimation, financial hurdle translation, sample-size planning, SQL scoring, Python statistical inference, validation and executive decision communication. It does **not** demonstrate real customer impact, approved infrastructure, actual marketing budgets, deployed production AI or confirmed company technology gaps.