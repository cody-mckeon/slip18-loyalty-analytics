# Pre-experiment design — next fictional loyalty offer pilot

**Status: proposed plan, not preregistered or executed.** This document was written after the original 24,000-customer demonstration was analyzed. It must not be described as a plan made before that historical simulation. For a fresh prospective simulation, freeze the values here, record a timestamp/commit hash, and do not change them after inspecting outcomes.

## Executive decision

Should a fictional casino expand a $50 loyalty incentive when the goal is incremental **30-day contribution profit**, after actual redemption and campaign contact costs? Offer assignment, not redemption, is the decision under evaluation. A positive visit rate alone is insufficient.

## Protocol for the next independent synthetic experiment

- **Eligible population:** one fictional loyalty customer per record, with consent and exclusions assumed checked. No actual resort or customer data.
- **Randomization unit:** individual customer, allocated 1:1 to offer and holdout using a new, recorded seed. The control group receives no offer or campaign contact. In a real deployment, evaluate households and cross-channel contamination before choosing the unit.
- **Observation window:** 30 days for both arms, starting at the same campaign launch date; all assigned customers remain in the analysis, including nonvisitors.
- **Primary outcome:** net contribution dollars per randomized customer: `gross_cents - variable_cost_cents - (redeemed × 5000) - (treatment × 25)`, divided by 100. A nonvisitor's net is −$0.25 in treatment and $0 in control.
- **Primary estimand:** treatment mean net contribution minus control mean net contribution (ITT). Report estimate, two-sided 95% confidence interval, and two-sided p-value using an unequal-variance large-sample standard error.
- **Hypotheses:** H0: ITT = $0; H1: ITT differs from $0. Use two-sided alpha = 0.05. A positive lower confidence bound is the evidence criterion; do not substitute a one-sided test after seeing results.
- **Business MDE:** **$10 incremental net contribution per assigned customer**, an illustrative business target to be approved *before* new experiment outcomes are viewed. Statistical detectability and economic attractiveness are distinct.
- **Power target:** 80%; treatment/control allocation: 1:1. Use independent *pre-period/pilot* records to estimate SD of the primary outcome, with uncertainty/sensitivity checks for skewed spending. **Do not plug the original experiment's observed treatment effect or observed standard error into the prospective design and claim the design was prespecified.**
- **Sample-size calculation:** `python3 power_analysis.py --mde 10 --sd <independently estimated SD>`; record the independent SD source, date, assumptions, planned counts, and sensitivity at larger SD before generating new outcomes. If independent SD is unavailable, the plan is **incomplete** and should not launch. A fictional SD of $341 is useful *only as an illustrative example*, not as validated pilot evidence.
- **Guardrails:** verify assigned counts, duplicate IDs, missing or impossible outcomes, redemption only among treatment visitors, segment distribution, and finance reconciliation. Track visit rates, total redemption expense, and cost assumptions as secondary/operational metrics, not additional primary success tests. Guardrail thresholds would need agreement before a real launch.
- **Sequential monitoring:** do not repeatedly inspect p-values and stop when significant. If interim looks are needed, preregister an appropriate sequential testing approach and stopping boundaries.
- **Segments:** occasional, regular, frequent are exploratory. Adjust three within-tier tests (Bonferroni as in baseline); directly test interaction before claiming one segment is more responsive than another. Do not optimize targeting on the same dataset used for confirmatory inference.
- **A/A validation:** on separate synthetic data with no modeled treatment lift, verify null calibration over many independent seeds; a single nonsignificant A/A result is not sufficient proof. Optional later milestone.

## Decision and escalation

Advance to a controlled follow-on pilot only if (a) the primary 95% interval's lower bound is above $0, (b) the *economic* estimate is sufficiently attractive relative to preapproved operational thresholds, and (c) data/assignment integrity checks and guardrails pass. Otherwise investigate and redesign; avoid claiming a null effect when a confidence interval is wide. The simulator's simplified 30-day economics cannot establish real-world causality or long-term profit.

## Frozen-versus-observed separation

The original seed `20261106` and its 24,000-customer output are an existing demonstration with an **observed** ITT of $11.58, CI [$2.95, $20.22]. This planned next experiment has **no observed results**. Only once the plan is frozen and an independent variance estimate is sourced should a new seed/sample be generated and analyzed.