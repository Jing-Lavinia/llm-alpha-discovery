from __future__ import annotations

import json
from pathlib import Path

from alpha_evidence.manifest import read_allowlist


ROOT = Path(__file__).resolve().parents[1]


def test_readme_headline_metrics_match_evidence():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    evidence = json.loads((ROOT / "evidence/aggregate-evidence.v3.json").read_text(encoding="utf-8"))
    for profile in ("primary", "higher_risk"):
        metrics = next(x["metrics"] for x in evidence["performance"] if x["profile"] == profile and x["one_way_cost_bps"] == 5)
        assert f"{metrics['cagr'] * 100:.2f}%" in readme
        assert f"{metrics['sharpe']:.2f}" in readme
        assert f"{metrics['max_drawdown'] * 100:.2f}%".replace("-", "−") in readme


def test_public_release_is_narrow_and_complete():
    paths = read_allowlist(ROOT / "evidence/release-allowlist.txt")
    assert paths == tuple(sorted(paths))
    assert set(paths) == {
        "evidence/aggregate-evidence.v3.json", "figures/annual_consistency.png",
        "figures/capacity_scenarios.png", "figures/cost_sensitivity.png",
        "figures/evaluation_path.png", "figures/performance_profile.png",
        "figures/research_context.png", "figures/research_overview.png",
        "figures/research_roles.png", "figures/system_architecture.png",
    }
    assert (ROOT / "src/alpha_evidence").is_dir()
    assert not (ROOT / "docs/DATA_AND_TIMING.md").exists()


def test_frontier_story_and_public_boundary_are_visible():
    readme = (ROOT / "README.md").read_text(encoding="utf-8").casefold()
    assert "llm-driven alpha discovery" in readme
    assert "cumulative research" in readme
    assert "proprietary system boundary" in readme
