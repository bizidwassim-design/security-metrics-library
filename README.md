# Security Metrics & KPI Library

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE) [![CI](https://github.com/bizidwassim-design/security-metrics-library/actions/workflows/ci.yml/badge.svg)](https://github.com/bizidwassim-design/security-metrics-library/actions/workflows/ci.yml) [![Fictional data](https://img.shields.io/badge/sample%20data-fictional-informational)](SECURITY.md)

A free, open-source catalogue of **47 security metrics** that a security team can measure tomorrow: each one with a
definition, a formula, the data source, the frequency, an example target, the audience it is for, the framework
identifiers it evidences (**NIST CSF 2.0**, **ISO/IEC 27001:2022**, **CIS Controls v8**) and the ways it gets gamed.
The catalogue is data (`YAML`); the documents, the CSV and the trend report are generated from it.

> 🇫🇷 Résumé en français en bas de page.

## Layout

```
data/metrics.yaml             the library: 47 metrics in 9 categories (source of truth)
data/metrics.csv              flat export for spreadsheets and GRC tools (generated)
docs/catalogue.md             every metric, grouped by category, with detail cards (generated)
docs/board-pack.md            the ten metrics for a board, with plain-language narrative (generated)
docs/designing-a-metric.md    SMART criteria, leading vs lagging, gaming risks, how to set a target
docs/dashboard-wireframes.md  board / CISO / operations wireframes (ASCII + Mermaid)
examples/sample-values.csv    12 months of fictional values for 8 metrics
examples/trend-report.md      Markdown trend report with sparklines and target status (generated)
scripts/build_catalogue.py    validates the YAML and writes catalogue.md, board-pack.md, metrics.csv
scripts/trend_report.py       turns a CSV of monthly values into the trend report
tests/test_library.py         unit tests for validation, rendering and the trend logic
```

## Quick start

```bash
pip install pyyaml
python scripts/build_catalogue.py          # validate the library, regenerate docs and CSV
python scripts/trend_report.py             # examples/sample-values.csv -> examples/trend-report.md
python -m unittest discover -s tests       # run the tests
```

To report on your own numbers, export a CSV with three columns (`metric_id,month,value`) from your tools and run:

```bash
python scripts/trend_report.py --values my-values.csv --out my-report.md
```

The report shows, per metric, a 12-month sparkline, first and latest value, change, target, status
(On / Near / Off target) and trend (Improving / Flat / Worsening), using the direction and target defined in the YAML.

## What's inside

| Category | Count | Examples |
|----------|------:|----------|
| Governance | 5 | Control coverage against framework, risk-treatment actions overdue, asset inventory completeness |
| Identity | 7 | MFA coverage, phishing-resistant MFA for admins, dormant accounts, leaver de-provisioning time |
| Vulnerability | 6 | Critical vulnerabilities in SLA, known-exploited vulnerabilities on external assets, scan coverage |
| Endpoint | 5 | EDR coverage, OS patch compliance, unsupported OS, disk encryption, hardening baseline |
| Detection & response | 8 | Time to detect, time to contain, triage SLA, log-source coverage, technique coverage, exercises |
| Awareness | 4 | Phishing click rate, phishing report rate, training completion, repeat clickers |
| Third-party | 4 | Tier 1 vendors assessed within cadence, overdue assessments, critical findings > 90 days, clauses |
| Cloud | 4 | High-severity misconfigurations, public storage, over-privileged identities, restore tests |
| AI | 4 | AI systems inventoried, impact assessments completed, unapproved AI apps, AI incidents |

36 leading indicators, 11 lagging. Ten are tagged for the board and ranked in [`docs/board-pack.md`](docs/board-pack.md).

### One entry, as an example

```yaml
- id: IDN-01
  name: MFA coverage (all users)
  category: identity
  type: leading
  definition: Share of enabled user accounts that must complete multi-factor authentication ...
  formula: enabled users with MFA enforced / enabled users x 100
  unit: "%"
  direction: higher
  data_source: Identity provider sign-in and authentication-method reports
  frequency: Monthly
  target_example: ">= 99 %"
  target_value: 99
  audience: [board, ciso, ops]
  frameworks:
    nist_csf: [PR.AA-03]
    iso27001: [A.5.17, A.8.5]
    cis_v8: ["6.3", "6.4"]
  pitfalls:
    - Registered is not enforced; count accounts where a policy requires MFA.
    - Legacy authentication protocols can bypass MFA; pair with a legacy-auth sign-in count.
  board:
    rank: 1
    narrative: The single control that most reduces account takeover ...
```

## Design choices

* **Metrics are data, documents are views.** Edit `data/metrics.yaml`; everything else is regenerated and CI fails
  if the committed copies drift.
* **Every metric carries its pitfalls.** The way a number gets gamed is part of its definition, not a footnote.
* **Denominators come from outside the tool.** The catalogue repeatedly points to the asset inventory or HR
  headcount, because a tool reporting its own coverage always says 100 %.
* **Audience is a field.** Filter on `board`, `ciso` or `ops` and you get a view that fits on one screen.
* **Targets are examples.** `target_value` makes the scripts work; it is not a benchmark. Calibrate after three months
  of baseline (see [`docs/designing-a-metric.md`](docs/designing-a-metric.md)).
* **Framework references are identifiers only**: NIST CSF 2.0 subcategories, ISO/IEC 27001:2022 Annex A controls,
  CIS Controls v8 safeguards. Standard text is never reproduced.

## Related repositories

| Repository | How it connects |
|------------|-----------------|
| [ciso-executive-dashboard](https://github.com/bizidwassim-design/ciso-executive-dashboard) | A rendered executive dashboard; the board-pack metrics here are the ones that belong on it |
| [vendor-risk-assessment-template](https://github.com/bizidwassim-design/vendor-risk-assessment-template) | Source of the third-party metrics (Tier 1 coverage, overdue reviews, clauses) |
| [application-risk-assessment-template](https://github.com/bizidwassim-design/application-risk-assessment-template) | Source of risk-treatment metrics (GOV-02) |
| [grc-control-crosswalk](https://github.com/bizidwassim-design/grc-control-crosswalk) | Cross-reference behind the NIST CSF / ISO 27001 / CIS v8 identifiers used here |
| [soc-detection-playbooks](https://github.com/bizidwassim-design/soc-detection-playbooks) | Detections and playbooks that feed the detection-and-response metrics |
| [iso27001-iso42001-toolkit](https://github.com/bizidwassim-design/iso27001-iso42001-toolkit) | Policies and AI impact assessment template behind the governance and AI metrics |
| [public-scripts](https://github.com/bizidwassim-design/public-scripts) | Scripts that can produce several of the raw numbers (MFA, dormant accounts, app registrations) |

## Contributing

New metrics, sharper pitfalls, corrected framework identifiers and translations are welcome — see
[CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md). Keep sample values fictional.

## Disclaimer

Targets and sample values are illustrative. A metric is only as good as its denominator and its owner; this library
gives you definitions, not assurance. It does not replace a risk assessment, an audit or professional judgement.

## License

[MIT](LICENSE) — free to use, copy, modify and redistribute.

---

## 🇫🇷 Résumé

Bibliothèque **open source** de 47 indicateurs de sécurité (KPI) en 9 catégories : gouvernance, identités,
vulnérabilités, postes de travail, détection et réponse, sensibilisation, fournisseurs, cloud et IA. Chaque indicateur
précise sa définition, sa formule, la source de données, la fréquence, une cible d'exemple, le public (conseil
d'administration, RSSI, opérations), les références **NIST CSF 2.0**, **ISO/IEC 27001:2022** et **CIS v8**, et les
façons dont il peut être détourné. Le catalogue, le pack conseil d'administration (10 indicateurs commentés), le CSV et
le rapport de tendance avec sparklines sont générés par les scripts Python à partir de `data/metrics.yaml`.
Toutes les valeurs d'exemple sont fictives.
