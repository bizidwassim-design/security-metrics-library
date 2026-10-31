# Designing a security metric

A metric is a decision aid. If nobody would act differently because the number moved, it is a statistic, not a
metric. This guide is the checklist used for every entry in [`data/metrics.yaml`](../data/metrics.yaml); use it before
adding your own.

## 1. Start from the decision, not the data

Write the sentence first: *"If this number is below X, we will ..."*. If you cannot finish the sentence with a
concrete action (reallocate budget, block a release, escalate to a vendor, accept a risk), the metric is not ready.

| Audience | Decision they make | Metrics that fit |
|----------|--------------------|------------------|
| Board | Funding, risk appetite, accountability | Coverage of the critical few controls, incident outcomes, recovery proof, obligations met |
| CISO | Priorities, programme health, where to intervene | Leading hygiene metrics by domain, SLA attainment, backlog ages, exceptions |
| Operations | What to do this week | Queues, overdue items, failing agents, noisy rules, open findings by owner |

Same data, three altitudes. The board sees MFA coverage as one number; operations sees the list of accounts.

## 2. SMART, applied to security

| Letter | Test | Example that passes | Example that fails |
|--------|------|---------------------|--------------------|
| **S**pecific | One control, one population, one definition | "Enabled user accounts with an MFA-enforcing policy" | "MFA adoption" |
| **M**easurable | Comes from a system of record, reproducibly | Identity-provider report joined with HR headcount | Team lead's estimate |
| **A**ctionable | A named owner can move it | Patch SLA attainment per platform team | "Threat level" |
| **R**elevant | Linked to a risk you actually carry | Known-exploited vulnerabilities on internet-facing assets | Total vulnerability count |
| **T**ime-bound | Has a period and a target date | ">= 99 % by end of Q2; measured monthly" | "Improve over time" |

Two more that matter in security:

* **Honest denominator.** The denominator must come from a source *outside* the tool being measured. An EDR console
  reporting its own coverage always says 100 %. Use the asset inventory, HR headcount or network discovery.
* **Stable definition.** Freeze the definition for at least a year. Note any change in the metric's record and show
  a break in the trend line; a redefined metric is a new metric.

## 3. Leading versus lagging

| | Leading | Lagging |
|-|---------|---------|
| Measures | Conditions that make incidents more or less likely | Outcomes that already happened |
| Examples | MFA coverage, patch SLA, log-source coverage, access-review completion, vendor assessments current | Incidents by severity, time to contain, audit findings, losses |
| Moves | Quickly, under your control | Slowly, partly outside your control |
| Risk of misreading | Green hygiene does not guarantee no incidents | Zero incidents may mean zero detection |

A balanced set pairs them: *log-source coverage* (leading) next to *mean time to detect* (lagging); *phishing report
rate* (leading) next to *business-email-compromise incidents* (lagging). When a leading metric improves and the
matching lagging one does not, the leading metric is probably measuring the wrong thing.

## 4. Anatomy of an entry

Every metric in the library records the same fields. The table explains why each exists.

| Field | Why it is there |
|-------|-----------------|
| `definition` | Removes ambiguity; the sentence a new analyst can compute from |
| `formula` | Numerator and denominator spelled out; "x 100" makes the unit explicit |
| `unit`, `direction` | Lets scripts and dashboards colour the metric without a human |
| `data_source` | Generic tool classes, so the metric survives a product change |
| `frequency` | How often the number is meaningful (weekly for exposure, quarterly for culture) |
| `target_example`, `target_value` | A starting point to calibrate, never a benchmark |
| `audience` | Prevents the 47-metric board deck |
| `frameworks` | Identifiers only, so an auditor can see which requirement the metric evidences |
| `pitfalls` | How the number is misread or gamed; the most valuable field |

## 5. Gaming risks and how to design them out

Every target creates an incentive. Anticipate it.

| Gaming pattern | Example | Design response |
|----------------|---------|-----------------|
| Shrink the denominator | Exclude "unmanaged" devices from patch compliance | Denominator from an independent inventory; report the excluded count |
| Re-rate the item | Downgrade Critical vulnerabilities to High to meet the SLA | Audit severity changes; include exploit availability in the rating rule |
| Move the date | Push the treatment target date instead of closing | Count date changes; show original versus current due date |
| Close without evidence | Mark the finding fixed on a promise | Require a verification scan or evidence link to close |
| Make the test easier | Lower phishing-template difficulty to lower the click rate | Record difficulty per campaign; compare like with like |
| Silence the signal | Disable noisy detection rules to lower false positives | Track detection coverage alongside the false-positive rate |
| Permanent exceptions | Exclude the same cloud finding for ever | Exceptions expire automatically and need an owner |
| Approve everything | Access reviews completed in seconds | Report the revocation rate with the completion rate |

Publish the pitfalls with the metric. People game numbers they think nobody understands.

## 6. Targets: how to set one

1. **Measure first.** Three months of baseline before any target.
2. **Set the target from the risk, not the baseline.** Phishing-resistant MFA for administrators is 100 % because
   the alternative is an account takeover, not because the baseline was 80 %.
3. **Two thresholds.** A *target* (green) and a *floor* (red). Between them is amber: on the way, needs watching.
4. **Date it.** "99 % by Q2" is a commitment; "99 %" is a wish.
5. **Review once a year.** When a metric sits at 100 % for four quarters, retire it to a control check and promote
   something that still moves.

## 7. Presenting a metric

* Current value, previous period, target, 12-month sparkline, one sentence of commentary. Always in that order.
* Colour against the target, not against last period. Improving and still red is a valid state.
* Show the count behind every rate. "95 %" of 20 devices and of 20,000 devices are different stories.
* Never show a metric without an owner. The owner's name is the real accountability mechanism.
* Retire metrics in public. Explain what replaced them and why.

## 8. Worked example: from a bad metric to a good one

**Before:** "Number of vulnerabilities" — 14,382. Nobody knows if that is good, who owns it or what to do.

**After:**

| Field | Value |
|-------|-------|
| Name | Critical vulnerabilities remediated within SLA (VUL-01) |
| Definition | Share of critical-severity vulnerabilities fixed or compensated within 14 days of first detection |
| Formula | critical vulnerabilities closed within SLA / critical vulnerabilities due in the period x 100 |
| Denominator | Scanner findings on assets present in the inventory (GOV-05) |
| Owner | Head of Infrastructure (servers), Head of Workplace (endpoints) |
| Target | >= 90 % by Q2; floor 75 % |
| Decision | Below floor two months in a row: release freeze on the owning platform until the backlog is cleared |
| Pitfalls | Severity re-rating; risk-accepted items hidden as closed |

Now the number means something, someone owns it, and it changes what happens next.
