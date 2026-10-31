# Contributing

Thanks for helping improve this library. Useful contributions include new metrics, sharper definitions and
formulas, additional pitfalls (the most valuable field), corrected framework identifiers, better wireframes and
translations.

## Ground rules

* **Fictional data only.** Sample values in `examples/` are invented. Never commit real figures, company names,
  people or system names.
* **Vendor-neutral.** Data sources are tool classes ("identity provider", "EDR console"), not products.
* **Standards by identifier only.** Reference NIST CSF 2.0 subcategories, ISO/IEC 27001:2022 Annex A controls and
  CIS Controls v8 safeguards by ID; never paste their text.
* Be kind — see the [Code of Conduct](CODE_OF_CONDUCT.md).

## How the files are built

`data/metrics.yaml` is the single source of truth. `scripts/build_catalogue.py` validates it and writes
`docs/catalogue.md`, `docs/board-pack.md` and `data/metrics.csv`. `scripts/trend_report.py` writes
`examples/trend-report.md` from `examples/sample-values.csv`.

**Edit the YAML, not the generated files.** CI regenerates them and fails if the committed copies differ.

```bash
pip install pyyaml
python scripts/build_catalogue.py
python scripts/trend_report.py
python -m unittest discover -s tests
```

## Adding a metric

1. Read [`docs/designing-a-metric.md`](docs/designing-a-metric.md). Write the decision sentence first.
2. Pick the category and the next free ID (`GOV`, `IDN`, `VUL`, `END`, `DR`, `AWR`, `TPR`, `CLD`, `AI`).
3. Fill every field. The validator rejects an entry without a formula, a numeric `target_value`, a direction, an
   audience, at least one framework reference and at least one pitfall.
4. Quote any YAML string that contains `: ` or starts with a quote character.
5. If you tag it for the board, give it a unique `board.rank` (1–10) and a plain-language `narrative`; the board pack
   holds exactly ten metrics, so you will need to demote one.
6. Rebuild, run the tests, commit the YAML **and** the regenerated files.

## Changing the trend logic

`scripts/trend_report.py` keeps the thresholds at the top (`NEAR_TOLERANCE`, `FLAT_TOLERANCE`). Add a test in
`tests/test_library.py` for any behaviour change and regenerate `examples/trend-report.md`.

## Style notes

* British English, short sentences, second person where it helps.
* Formulas spell out numerator and denominator and end with `x 100` for percentages.
* Pitfalls describe a concrete misreading or gaming pattern and the countermeasure, in one sentence each.

## Licensing of contributions

By contributing you agree that your work is released under the repository's [MIT License](LICENSE).
