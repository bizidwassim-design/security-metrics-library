# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.0] — 2026-10-31

### Added
- Initial public release.
- `data/metrics.yaml`: 47 metrics in 9 categories (governance, identity, vulnerability, endpoint,
  detection-response, awareness, third-party, cloud, AI) with definition, formula, data source, frequency,
  target example, audience, NIST CSF 2.0 / ISO/IEC 27001:2022 / CIS v8 identifiers and pitfalls.
- `scripts/build_catalogue.py`: validation plus generated `docs/catalogue.md`, `docs/board-pack.md` (ten board
  metrics with narrative) and `data/metrics.csv`.
- `scripts/trend_report.py`: Markdown trend report with Unicode sparklines, target status and trend from a CSV of
  monthly values; `examples/sample-values.csv` with 12 fictional months for 8 metrics.
- `docs/designing-a-metric.md` (SMART, leading vs lagging, gaming risks) and `docs/dashboard-wireframes.md`
  (board, CISO and operations views in ASCII and Mermaid).
- Unit tests, CI that regenerates and diffs every generated file, Dependabot, security policy.
