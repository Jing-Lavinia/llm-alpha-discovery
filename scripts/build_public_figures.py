#!/usr/bin/env python3
"""Build the public figures from the approved aggregate evidence."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence/aggregate-evidence.v3.json"
OUT = ROOT / "figures"

NAVY = "#102F44"
BLUE = "#1F5A7A"
BLUE_LIGHT = "#B8D0DC"
BLUE_XLIGHT = "#E8F0F4"
GOLD = "#C58B2A"
ORANGE = "#B76745"
INK = "#1D2A33"
SLATE = "#687985"
GRID = "#DCE4E8"
BG = "#F6F8F7"
WHITE = "#FFFFFF"


def new_figure(title: str, subtitle: str):
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10.5,
        "axes.labelcolor": SLATE, "axes.titlecolor": INK,
        "xtick.color": SLATE, "ytick.color": SLATE,
        "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    })
    fig = plt.figure(figsize=(14.88, 8.35), dpi=200, facecolor=BG)
    fig.text(0.055, 0.935, title, fontsize=25, fontweight="bold", color=INK, va="top")
    fig.text(0.055, 0.885, subtitle, fontsize=11.5, color=SLATE, va="top")
    for dx, dy in ((0, .016), (.016, 0), (0, -.016), (-.016, 0)):
        fig.add_artist(plt.Circle((.942 + dx, .925 + dy), .009, color=GOLD, transform=fig.transFigure))
    fig.add_artist(plt.Circle((.942, .925), .006, color=NAVY, transform=fig.transFigure))
    return fig


def footer(fig, evidence):
    fig.text(.055, .035, f"{evidence['period']['start']} to {evidence['period']['end']}  |  chronological walk-forward OOS  |  simulated net results", fontsize=8.2, color=SLATE)


def concept_footer(fig, note="Research system overview  |  public capability view"):
    fig.text(.055, .035, note, fontsize=8.2, color=SLATE)


def save(fig, name: str):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    fig.savefig(path, facecolor=BG, metadata={})
    plt.close(fig)
    with Image.open(path) as loaded:
        clean = loaded.convert("RGB").copy()
    clean.save(path, format="PNG", optimize=True)


def record(evidence, profile, cost):
    return next(x for x in evidence["performance"] if x["profile"] == profile and x["one_way_cost_bps"] == cost)


def label_bars(ax, containers, fmt="{:.1f}%"):
    for container in containers:
        for bar in container:
            value = bar.get_height()
            ax.annotate(fmt.format(value), (bar.get_x() + bar.get_width() / 2, value), xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", color=INK, fontsize=9, fontweight="bold")


def card(fig, x, label, value, note, color):
    box = FancyBboxPatch((x, .61), .205, .18, boxstyle="round,pad=0.012,rounding_size=0.012", transform=fig.transFigure, facecolor=WHITE, edgecolor=GRID, linewidth=1.2)
    fig.add_artist(box)
    fig.add_artist(plt.Rectangle((x, .61), .008, .18, transform=fig.transFigure, color=color))
    fig.text(x + .025, .755, label, color=SLATE, fontsize=8.5, fontweight="bold")
    fig.text(x + .025, .68, value, color=INK, fontsize=24, fontweight="bold")
    fig.text(x + .025, .635, note, color=SLATE, fontsize=8.7)


def research_overview(evidence):
    fig = new_figure("LLM-Driven Alpha Discovery", "An automated factor research system with demonstrated out-of-sample performance")
    primary = record(evidence, "primary", 5)["metrics"]
    risk = record(evidence, "higher_risk", 5)["metrics"]
    card(fig, .055, "SYSTEM", "Deployed", "end-to-end discovery", BLUE)
    card(fig, .285, "RESEARCH UNIVERSE", f"{evidence['research_scale']['instrument_count']}", "exchange-traded instruments", BLUE)
    card(fig, .515, "PRIMARY NET CAGR", f"{primary['cagr']:.1%}", f"Sharpe {primary['sharpe']:.2f}", GOLD)
    card(fig, .745, "HIGHER-RISK NET CAGR", f"{risk['cagr']:.1%}", f"Sharpe {risk['sharpe']:.2f}", ORANGE)
    ax = fig.add_axes([.075, .18, .85, .32])
    names = ["Primary", "Higher risk"]
    cagr = [primary["cagr"] * 100, risk["cagr"] * 100]
    draw = [abs(primary["max_drawdown"]) * 100, abs(risk["max_drawdown"]) * 100]
    x = np.arange(2)
    ax.bar(x - .17, cagr, .34, label="Net CAGR", color=[GOLD, ORANGE])
    ax.bar(x + .17, draw, .34, label="Drawdown magnitude", color=[BLUE_LIGHT, BLUE])
    ax.set_xticks(x); ax.set_xticklabels(names); ax.set_ylabel("Percent")
    for side in ("top", "right", "left"): ax.spines[side].set_visible(False)
    ax.grid(axis="y", color=GRID, linewidth=.8); ax.set_axisbelow(True); ax.legend(frameon=False, ncol=2, loc="upper left")
    label_bars(ax, ax.containers)
    footer(fig, evidence); save(fig, "research_overview.png")


def system_architecture(evidence):
    fig = new_figure("A system for cumulative alpha discovery", "Machine-scale exploration; deterministic empirical measurement")
    ax = fig.add_axes([.05, .13, .90, .69]); ax.axis("off")
    labels = [
        ("RESEARCH DOMAIN", "Objectives and constraints", BLUE_XLIGHT, BLUE),
        ("PROPRIETARY LLM ALPHA\nDISCOVERY SYSTEM", "Private system boundary", NAVY, WHITE),
        ("EXECUTABLE CANDIDATES", "Structured research outputs", BLUE_XLIGHT, BLUE),
        ("EMPIRICAL EVALUATION", "Chronological OOS evidence", "#F3E8D2", GOLD),
        ("RESEARCH ASSETS", "Validated factors and evidence", "#F1DED6", ORANGE),
    ]
    xs = [.025, .215, .455, .645, .835]; widths = [.15, .20, .15, .15, .14]
    for i, ((title, note, face, color), x, width) in enumerate(zip(labels, xs, widths)):
        box = FancyBboxPatch((x, .38), width, .27, boxstyle="round,pad=.015,rounding_size=.018", transform=ax.transAxes, facecolor=face, edgecolor=color, linewidth=1.4)
        ax.add_patch(box)
        ax.text(x + width/2, .535, title, ha="center", va="center", transform=ax.transAxes, color=color, fontsize=10, fontweight="bold")
        ax.text(x + width/2, .425, note, ha="center", va="center", transform=ax.transAxes, color=SLATE if face != NAVY else BLUE_LIGHT, fontsize=8.4)
        if i < len(labels) - 1:
            ax.annotate("", xy=(xs[i+1] - .012, .515), xytext=(x + width + .012, .515), xycoords=ax.transAxes, arrowprops=dict(arrowstyle="->", color=SLATE, lw=1.5))
    ax.text(.5, .18, "The public release verifies system outputs without exposing the mechanism that produces them.", ha="center", transform=ax.transAxes, color=INK, fontsize=11)
    concept_footer(fig); save(fig, "system_architecture.png")


def research_context(evidence):
    fig = new_figure("Evolution of the research problem", "The research unit expands from one manually specified factor to a continuing R&D capability")
    ax = fig.add_axes([.05, .13, .90, .69]); ax.axis("off")
    stages = [
        ("MANUAL FACTOR\nRESEARCH", "Human hypothesis\nand implementation", BLUE_XLIGHT, BLUE),
        ("PROGRAMMATIC\nSEARCH", "Greater formula\nthroughput", WHITE, BLUE),
        ("LLM-ASSISTED\nFORMALIZATION", "Broader economic\nhypothesis space", "#F3E8D2", GOLD),
        ("AUTOMATED\nQUANTITATIVE R&D", "Hypothesis-to-evidence\nresearch system", "#F1DED6", ORANGE),
    ]
    xs = [.055, .285, .515, .745]
    for i, ((title, note, face, color), x) in enumerate(zip(stages, xs)):
        box = FancyBboxPatch((x, .34), .18, .34, boxstyle="round,pad=.016,rounding_size=.018", transform=ax.transAxes, facecolor=face, edgecolor=color, linewidth=1.6)
        ax.add_patch(box)
        ax.text(x + .09, .565, title, ha="center", va="center", transform=ax.transAxes, color=color, fontsize=11, fontweight="bold")
        ax.text(x + .09, .425, note, ha="center", va="center", transform=ax.transAxes, color=SLATE, fontsize=9.3, linespacing=1.45)
        if i < 3:
            ax.annotate("", xy=(xs[i + 1] - .012, .51), xytext=(x + .192, .51), xycoords=ax.transAxes, arrowprops=dict(arrowstyle="->", color=SLATE, lw=1.6))
    ax.text(.5, .20, "The central question shifts from generating more formulas to producing reliable research evidence.", ha="center", transform=ax.transAxes, color=INK, fontsize=11)
    concept_footer(fig, "Conceptual research progression  |  representative rather than exhaustive")
    save(fig, "research_context.png")


def research_roles(evidence):
    fig = new_figure("Division of research responsibilities", "Open-ended exploration and deterministic measurement serve different purposes")
    ax = fig.add_axes([.06, .13, .88, .69]); ax.axis("off")
    panels = [
        (.04, "LLM RESEARCH LAYER", "EXPLORE + FORMALIZE", ["Broaden economic hypotheses", "Translate reasoning into structure", "Produce executable candidates"], BLUE_XLIGHT, BLUE),
        (.57, "QUANTITATIVE EVALUATION", "MEASURE + DECIDE", ["Control information timing", "Run chronological OOS tests", "Measure portfolio economics"], "#F3E8D2", GOLD),
    ]
    for x, title, verb, bullets, face, color in panels:
        box = FancyBboxPatch((x, .25), .39, .49, boxstyle="round,pad=.018,rounding_size=.02", transform=ax.transAxes, facecolor=face, edgecolor=color, linewidth=1.7)
        ax.add_patch(box)
        ax.text(x + .03, .665, title, transform=ax.transAxes, color=color, fontsize=10, fontweight="bold")
        ax.text(x + .03, .575, verb, transform=ax.transAxes, color=INK, fontsize=18, fontweight="bold")
        for j, bullet in enumerate(bullets):
            ax.text(x + .04, .47 - j * .075, f"•  {bullet}", transform=ax.transAxes, color=SLATE, fontsize=10)
    ax.text(.50, .57, "EXECUTABLE INTERFACE", ha="center", va="center", transform=ax.transAxes, color=INK, fontsize=8.5, fontweight="bold")
    ax.annotate("", xy=(.56, .50), xytext=(.44, .50), xycoords=ax.transAxes, arrowprops=dict(arrowstyle="->", color=SLATE, lw=1.8))
    ax.text(.5, .12, "A candidate becomes alpha evidence only after the deterministic layer accepts it.", ha="center", transform=ax.transAxes, color=INK, fontsize=11)
    concept_footer(fig); save(fig, "research_roles.png")


def evaluation_path(evidence):
    fig = new_figure("Candidate evaluation path", "Every generated candidate is measured under the same research standard")
    ax = fig.add_axes([.045, .13, .91, .69]); ax.axis("off")
    stages = [
        ("01", "EXECUTABLE", "Structured research object", BLUE_XLIGHT, BLUE),
        ("02", "POINT-IN-TIME", "Available information only", BLUE_XLIGHT, BLUE),
        ("03", "OUT-OF-SAMPLE", "Chronological measurement", WHITE, NAVY),
        ("04", "PORTFOLIO", "Turnover, risk and costs", "#F3E8D2", GOLD),
        ("05", "EVIDENCE", "Comparable research record", "#F1DED6", ORANGE),
    ]
    xs = [.02, .215, .41, .605, .80]
    for i, ((number, title, note, face, color), x) in enumerate(zip(stages, xs)):
        ax.text(x + .075, .72, number, ha="center", transform=ax.transAxes, color=color, fontsize=12, fontweight="bold")
        box = FancyBboxPatch((x, .35), .15, .30, boxstyle="round,pad=.014,rounding_size=.018", transform=ax.transAxes, facecolor=face, edgecolor=color, linewidth=1.5)
        ax.add_patch(box)
        ax.text(x + .075, .535, title, ha="center", transform=ax.transAxes, color=color, fontsize=10, fontweight="bold")
        ax.text(x + .075, .425, note, ha="center", transform=ax.transAxes, color=SLATE, fontsize=8.6, wrap=True)
        if i < 4:
            ax.annotate("", xy=(xs[i + 1] - .01, .50), xytext=(x + .16, .50), xycoords=ax.transAxes, arrowprops=dict(arrowstyle="->", color=SLATE, lw=1.5))
    ax.text(.5, .19, "Failure at any stage returns a research result—not a narrative exception.", ha="center", transform=ax.transAxes, color=INK, fontsize=11)
    concept_footer(fig); save(fig, "evaluation_path.png")


def performance_profile(evidence):
    fig = new_figure("Return and risk profile", "Primary and higher-risk expressions of the same factor at 5 bp one-way cost")
    ax = fig.add_axes([.10, .18, .81, .57])
    primary = record(evidence, "primary", 5)["metrics"]
    higher = record(evidence, "higher_risk", 5)["metrics"]
    categories = ["Net CAGR", "Annual volatility", "Drawdown magnitude"]
    pvals = [primary["cagr"] * 100, primary["annual_volatility"] * 100, abs(primary["max_drawdown"]) * 100]
    hvals = [higher["cagr"] * 100, higher["annual_volatility"] * 100, abs(higher["max_drawdown"]) * 100]
    x = np.arange(3); width = .33
    first = ax.bar(x - width / 2, pvals, width, color=GOLD, label=f"Primary  |  Sharpe {primary['sharpe']:.2f}")
    second = ax.bar(x + width / 2, hvals, width, color=ORANGE, label=f"Higher risk  |  Sharpe {higher['sharpe']:.2f}")
    ax.set_xticks(x); ax.set_xticklabels(categories); ax.set_ylabel("Percent")
    for side in ("top", "right", "left"): ax.spines[side].set_visible(False)
    ax.grid(axis="y", color=GRID); ax.set_axisbelow(True); ax.legend(frameon=False, ncol=2, loc="upper left")
    label_bars(ax, [first, second])
    footer(fig, evidence); save(fig, "performance_profile.png")


def cost_sensitivity(evidence):
    fig = new_figure("Transaction-cost sensitivity", "Net CAGR across three one-way cost assumptions")
    ax = fig.add_axes([.10, .17, .82, .61])
    costs = [5, 10, 20]
    for profile, label, color in (("primary", "Primary", GOLD), ("higher_risk", "Higher risk", ORANGE)):
        values = [record(evidence, profile, c)["metrics"]["cagr"] * 100 for c in costs]
        ax.plot(costs, values, marker="o", markersize=8, linewidth=2.7, label=label, color=color)
        for x, y in zip(costs, values): ax.text(x, y + 1.3, f"{y:.1f}%", ha="center", color=color, fontweight="bold")
    ax.axhline(0, color=INK, linewidth=1); ax.set_xticks(costs); ax.set_xticklabels([f"{x} bp" for x in costs]); ax.set_ylabel("Net CAGR (%)")
    for side in ("top", "right"): ax.spines[side].set_visible(False)
    ax.grid(axis="y", color=GRID); ax.legend(frameon=False, loc="upper right")
    footer(fig, evidence); save(fig, "cost_sensitivity.png")


def annual_consistency(evidence):
    fig = new_figure("Annual consistency", "Primary portfolio at the 5 bp one-way cost assumption")
    ax = fig.add_axes([.10, .17, .82, .61])
    rows = evidence["annual_evidence"]; years = [str(x["year"]) for x in rows]; values = [x["period_return"] * 100 for x in rows]
    bars = ax.bar(years, values, color=[BLUE, BLUE, BLUE_LIGHT, GOLD, ORANGE], width=.62)
    label_bars(ax, [bars])
    ax.set_ylabel("Period return (%)")
    for side in ("top", "right", "left"): ax.spines[side].set_visible(False)
    ax.grid(axis="y", color=GRID); ax.set_axisbelow(True)
    footer(fig, evidence); save(fig, "annual_consistency.png")


def capacity_scenarios(evidence):
    fig = new_figure("Capacity scenarios", "Lagged-ADV participation rises with both capital and portfolio risk")
    ax = fig.add_axes([.10, .19, .82, .58])
    rows = evidence["capacity"]; labels = [f"{'Primary' if x['profile']=='primary' else 'Higher risk'}\n{x['capital_scenario_mn']}m" for x in rows]
    p95 = [x["p95_adv_participation"] * 100 for x in rows]; maximum = [x["maximum_adv_participation"] * 100 for x in rows]
    x = np.arange(len(rows)); ax.bar(x - .18, p95, .36, color=GOLD, label="p95"); ax.bar(x + .18, maximum, .36, color=BLUE, label="Maximum")
    ax.set_xticks(x); ax.set_xticklabels(labels); ax.set_ylabel("ADV participation (%)")
    for side in ("top", "right", "left"): ax.spines[side].set_visible(False)
    ax.grid(axis="y", color=GRID); ax.set_axisbelow(True); ax.legend(frameon=False)
    label_bars(ax, ax.containers)
    footer(fig, evidence); save(fig, "capacity_scenarios.png")


def main():
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    research_overview(evidence); research_context(evidence); system_architecture(evidence)
    research_roles(evidence); evaluation_path(evidence); performance_profile(evidence)
    cost_sensitivity(evidence); annual_consistency(evidence); capacity_scenarios(evidence)
    print("wrote 9 public figures")


if __name__ == "__main__":
    main()
