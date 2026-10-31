#!/usr/bin/env python3
"""
Build the generated views of the Security Metrics & KPI Library from data/metrics.yaml:

    docs/catalogue.md     every metric, grouped by category (tables + detail cards)
    docs/board-pack.md    the ten board-level metrics with narrative
    data/metrics.csv      flat export for spreadsheets and GRC tools

Usage:
    pip install pyyaml
    python scripts/build_catalogue.py            # writes the three files above
    python scripts/build_catalogue.py --check    # validate the YAML only, write nothing

The script validates the library first and exits non-zero on any structural
problem, so CI catches a broken entry before it reaches the docs.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
YAML_PATH = ROOT / "data" / "metrics.yaml"

CATEGORIES = ["governance", "identity", "vulnerability", "endpoint", "detection-response",
              "awareness", "third-party", "cloud", "ai"]
CATEGORY_TITLES = {
    "governance": "Governance & risk",
    "identity": "Identity & access",
    "vulnerability": "Vulnerability management",
    "endpoint": "Endpoint & platform",
    "detection-response": "Detection & response",
    "awareness": "Awareness & behaviour",
    "third-party": "Third-party risk",
    "cloud": "Cloud & resilience",
    "ai": "AI governance",
}
TYPES = {"leading", "lagging"}
AUDIENCES = ["board", "ciso", "ops"]
UNITS = {"%", "days", "hours", "count", "ratio", "score"}
DIRECTIONS = {"higher", "lower"}
FRAMEWORK_KEYS = ["nist_csf", "iso27001", "cis_v8"]
REQUIRED = ["id", "name", "category", "type", "definition", "formula", "unit", "direction",
            "data_source", "frequency", "target_example", "target_value", "audience", "frameworks", "pitfalls"]
ID_RE = re.compile(r"^[A-Z]{2,3}-\d{2}$")
MIN_METRICS = 40
BOARD_COUNT = 10


# --------------------------------------------------------------------------- #
# Load and validate
# --------------------------------------------------------------------------- #
def load_metrics(path: Path = YAML_PATH) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    metrics = data.get("metrics") if isinstance(data, dict) else None
    if not isinstance(metrics, list):
        raise ValueError("metrics.yaml must contain a top-level 'metrics' list")
    return metrics


def validate(metrics: list[dict[str, Any]]) -> list[str]:
    """Return a list of problems (empty = valid)."""
    problems: list[str] = []
    seen_ids: set[str] = set()
    board_ranks: dict[int, str] = {}
    if len(metrics) < MIN_METRICS:
        problems.append(f"library holds {len(metrics)} metrics; at least {MIN_METRICS} expected")
    for m in metrics:
        mid = str(m.get("id", "?"))
        for key in REQUIRED:
            if key not in m or m[key] in (None, "", []):
                problems.append(f"{mid}: missing '{key}'")
        if not ID_RE.match(mid):
            problems.append(f"{mid}: id must look like ABC-01")
        if mid in seen_ids:
            problems.append(f"{mid}: duplicate id")
        seen_ids.add(mid)
        if m.get("category") not in CATEGORIES:
            problems.append(f"{mid}: category '{m.get('category')}' not in {CATEGORIES}")
        if m.get("type") not in TYPES:
            problems.append(f"{mid}: type must be leading or lagging")
        if m.get("unit") not in UNITS:
            problems.append(f"{mid}: unit '{m.get('unit')}' not in {sorted(UNITS)}")
        if m.get("direction") not in DIRECTIONS:
            problems.append(f"{mid}: direction must be higher or lower")
        if not isinstance(m.get("target_value"), (int, float)):
            problems.append(f"{mid}: target_value must be a number")
        aud = m.get("audience")
        if not isinstance(aud, list) or not aud or any(a not in AUDIENCES for a in aud):
            problems.append(f"{mid}: audience must be a non-empty subset of {AUDIENCES}")
        fw = m.get("frameworks")
        if not isinstance(fw, dict) or any(k not in fw for k in FRAMEWORK_KEYS):
            problems.append(f"{mid}: frameworks must hold {FRAMEWORK_KEYS}")
        else:
            for k in FRAMEWORK_KEYS:
                if not isinstance(fw[k], list):
                    problems.append(f"{mid}: frameworks.{k} must be a list")
            if not any(fw.get(k) for k in FRAMEWORK_KEYS):
                problems.append(f"{mid}: at least one framework reference required")
        if not isinstance(m.get("pitfalls"), list) or len(m.get("pitfalls") or []) < 1:
            problems.append(f"{mid}: pitfalls must be a non-empty list")
        board = m.get("board")
        if board is not None:
            rank = board.get("rank") if isinstance(board, dict) else None
            if not isinstance(rank, int) or not 1 <= rank <= BOARD_COUNT:
                problems.append(f"{mid}: board.rank must be an integer 1..{BOARD_COUNT}")
            elif rank in board_ranks:
                problems.append(f"{mid}: board.rank {rank} already used by {board_ranks[rank]}")
            else:
                board_ranks[rank] = mid
            if not isinstance(board, dict) or not board.get("narrative"):
                problems.append(f"{mid}: board.narrative required")
            if "board" not in (aud or []):
                problems.append(f"{mid}: board metrics must list 'board' in audience")
    if len(board_ranks) != BOARD_COUNT:
        problems.append(f"{len(board_ranks)} board metrics defined; exactly {BOARD_COUNT} expected")
    return problems


# --------------------------------------------------------------------------- #
# Rendering helpers
# --------------------------------------------------------------------------- #
def esc(text: Any) -> str:
    """Make a value safe inside a Markdown table cell."""
    return str(text).replace("|", "\\|").replace("\n", " ").strip()


def fw_text(m: dict[str, Any]) -> str:
    fw = m["frameworks"]
    parts = []
    if fw.get("nist_csf"):
        parts.append("NIST CSF 2.0: " + ", ".join(fw["nist_csf"]))
    if fw.get("iso27001"):
        parts.append("ISO 27001: " + ", ".join(fw["iso27001"]))
    if fw.get("cis_v8"):
        parts.append("CIS v8: " + ", ".join(str(x) for x in fw["cis_v8"]))
    return " · ".join(parts)


def audience_text(m: dict[str, Any]) -> str:
    return ", ".join(a.upper() if a == "ciso" else a.capitalize() for a in m["audience"])


def target_text(m: dict[str, Any]) -> str:
    return esc(m["target_example"])


def write_text(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote {path.relative_to(ROOT).as_posix()}")


# --------------------------------------------------------------------------- #
# docs/catalogue.md
# --------------------------------------------------------------------------- #
def render_catalogue(metrics: list[dict[str, Any]]) -> list[str]:
    by_cat: dict[str, list[dict[str, Any]]] = {c: [] for c in CATEGORIES}
    for m in metrics:
        by_cat[m["category"]].append(m)
    leading = sum(1 for m in metrics if m["type"] == "leading")
    lines = [
        "# Security metrics catalogue",
        "",
        "<!-- Generated by scripts/build_catalogue.py from data/metrics.yaml. Do not edit by hand. -->",
        "",
        f"{len(metrics)} metrics in {len(CATEGORIES)} categories: {leading} leading, {len(metrics) - leading} lagging. "
        "Targets are illustrative examples, not industry benchmarks; calibrate them to your own baseline "
        "(see [designing-a-metric.md](designing-a-metric.md)).",
        "",
        "## Contents",
        "",
    ]
    for c in CATEGORIES:
        lines.append(f"- [{CATEGORY_TITLES[c]}](#{c.replace('-', '')}) ({len(by_cat[c])})")
    lines += ["", "## At a glance", "", "| ID | Metric | Category | Type | Unit | Better | Frequency | Audience |",
              "|----|--------|----------|------|------|--------|-----------|----------|"]
    for m in metrics:
        lines.append(f"| {m['id']} | {esc(m['name'])} | {m['category']} | {m['type']} | {esc(m['unit'])} | "
                     f"{m['direction']} | {esc(m['frequency'])} | {audience_text(m)} |")
    lines.append("")

    for c in CATEGORIES:
        group = by_cat[c]
        lines += [f"<a id=\"{c.replace('-', '')}\"></a>", "", f"## {CATEGORY_TITLES[c]}", "",
                  "| ID | Metric | Type | Formula | Frequency | Target (example) | Audience | Frameworks |",
                  "|----|--------|------|---------|-----------|------------------|----------|------------|"]
        for m in group:
            lines.append(f"| {m['id']} | **{esc(m['name'])}** | {m['type']} | {esc(m['formula'])} | {esc(m['frequency'])} | "
                         f"{target_text(m)} | {audience_text(m)} | {esc(fw_text(m))} |")
        lines.append("")
        for m in group:
            lines += [f"### {m['id']} — {esc(m['name'])}", "",
                      f"*{m['type'].capitalize()} indicator · unit: {m['unit']} · {m['direction']} is better · {m['frequency']}*", "",
                      f"**Definition.** {m['definition']}", "",
                      f"**Formula.** `{m['formula']}`", "",
                      f"**Data source.** {m['data_source']}", "",
                      f"**Target example.** {m['target_example']}", "",
                      f"**Frameworks.** {fw_text(m)}", "",
                      "**Pitfalls and gaming risks.**", ""]
            lines += [f"- {p}" for p in m["pitfalls"]]
            lines.append("")
    return lines


# --------------------------------------------------------------------------- #
# docs/board-pack.md
# --------------------------------------------------------------------------- #
def render_board_pack(metrics: list[dict[str, Any]]) -> list[str]:
    board = sorted((m for m in metrics if m.get("board")), key=lambda m: m["board"]["rank"])
    lines = [
        "# Board pack: ten security metrics for the board",
        "",
        "<!-- Generated by scripts/build_catalogue.py from data/metrics.yaml. Do not edit by hand. -->",
        "",
        "A board does not need forty metrics. It needs ten that answer three questions: *are we protected against the "
        "attacks that matter*, *would we notice and recover*, and *are we meeting our obligations*. Each metric below is "
        "shown with a plain-language narrative, the target, and the question a director can ask to test the number.",
        "",
        "Present each metric the same way every quarter: current value, previous quarter, target, 12-month trend "
        "(a sparkline is enough), and one sentence of commentary. Do not change definitions between quarters without "
        "saying so.",
        "",
        "## The ten, on one page",
        "",
        "| # | Metric | Answers the question | Target (example) | Frequency |",
        "|---|--------|----------------------|------------------|-----------|",
    ]
    questions = {
        "IDN-01": "Can accounts be taken over with just a password?",
        "VUL-01": "Do we fix the dangerous weaknesses in time?",
        "END-01": "Are our devices watched?",
        "DR-02": "How fast do we shut an attacker out?",
        "DR-06": "What actually happened this period?",
        "AWR-01": "Would our people fall for a fake email?",
        "TPR-01": "Are our critical suppliers checked?",
        "GOV-03": "How much of our security framework is really in place?",
        "CLD-04": "Could we recover from a destructive attack?",
        "AI-02": "Was our AI checked for harm before go-live?",
    }
    for m in board:
        q = questions.get(m["id"], m["definition"])
        lines.append(f"| {m['board']['rank']} | **{esc(m['name'])}** ({m['id']}) | {esc(q)} | {target_text(m)} | {esc(m['frequency'])} |")
    lines += ["", "## How to read the pack", "",
              "- **Leading** indicators (coverage, hygiene) predict future incidents; **lagging** ones (incidents, containment time) "
              "record what happened. A healthy pack has both, and the leading ones should move first.",
              "- Arrows show direction against target, not against last quarter. A metric can improve and still be red.",
              "- Every red metric comes with an owner, a date and a decision requested from the board (budget, priority, risk acceptance) — or it does not belong in the pack.",
              "- Definitions and targets are stable for the year. Changes are announced one quarter ahead.",
              ""]
    for m in board:
        lines += [f"## {m['board']['rank']}. {esc(m['name'])} ({m['id']})", "",
                  f"**In plain language.** {m['board']['narrative']}", "",
                  f"**Definition.** {m['definition']}", "",
                  f"**Formula.** `{m['formula']}` — reported {m['frequency'].lower()}, {m['direction']} is better.", "",
                  f"**Target example.** {m['target_example']}", "",
                  f"**Watch for.** {m['pitfalls'][0]}", "",
                  f"**Frameworks.** {fw_text(m)}", ""]
    lines += ["## Suggested one-slide layout", "",
              "```",
              "+--------------------------------------------------------------------------------+",
              "| SECURITY SCORECARD - Q3 2026                              RAG vs target        |",
              "+-----------------------------+----------+----------+--------+------------------+",
              "| Metric                      | Current  | Previous | Target | 12-month trend   |",
              "+-----------------------------+----------+----------+--------+------------------+",
              "| 1. MFA coverage             |  99.1 %  |  98.3 %  | 99 %   | ▁▂▃▄▅▆▆▇▇███ G   |",
              "| 2. Critical vulns in SLA    |  93 %    |  88 %    | 90 %   | ▁▂▃▂▄▅▆▅▇▇██ G   |",
              "| ...                         |          |          |        |                  |",
              "+-----------------------------+----------+----------+--------+------------------+",
              "| Decisions requested: 1) ...   2) ...                                            |",
              "+--------------------------------------------------------------------------------+",
              "```", "",
              "See [dashboard-wireframes.md](dashboard-wireframes.md) for the CISO and operations views that sit behind this page, "
              "and `scripts/trend_report.py` for a generator that produces the sparklines from a CSV of monthly values.", ""]
    return lines


# --------------------------------------------------------------------------- #
# data/metrics.csv
# --------------------------------------------------------------------------- #
CSV_COLUMNS = ["id", "name", "category", "type", "unit", "direction", "definition", "formula", "data_source",
               "frequency", "target_example", "target_value", "audience", "nist_csf", "iso27001", "cis_v8",
               "pitfalls", "board_rank"]


def write_csv(metrics: list[dict[str, Any]], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_COLUMNS, lineterminator="\n")
        w.writeheader()
        for m in metrics:
            fw = m["frameworks"]
            w.writerow({
                "id": m["id"], "name": m["name"], "category": m["category"], "type": m["type"], "unit": m["unit"],
                "direction": m["direction"], "definition": m["definition"], "formula": m["formula"],
                "data_source": m["data_source"], "frequency": m["frequency"], "target_example": m["target_example"],
                "target_value": m["target_value"], "audience": "; ".join(m["audience"]),
                "nist_csf": "; ".join(fw["nist_csf"]), "iso27001": "; ".join(fw["iso27001"]),
                "cis_v8": "; ".join(str(x) for x in fw["cis_v8"]), "pitfalls": " | ".join(m["pitfalls"]),
                "board_rank": m["board"]["rank"] if m.get("board") else "",
            })
    print(f"Wrote {path.relative_to(ROOT).as_posix()}")


# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="validate only; write nothing")
    args = parser.parse_args(argv)

    metrics = load_metrics()
    problems = validate(metrics)
    if problems:
        print("metrics.yaml is invalid:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print(f"metrics.yaml OK: {len(metrics)} metrics, {sum(1 for m in metrics if m.get('board'))} board metrics")
    if args.check:
        return 0
    write_text(ROOT / "docs" / "catalogue.md", render_catalogue(metrics))
    write_text(ROOT / "docs" / "board-pack.md", render_board_pack(metrics))
    write_csv(metrics, ROOT / "data" / "metrics.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
