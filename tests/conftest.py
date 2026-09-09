from __future__ import annotations

from copy import deepcopy

import pytest


@pytest.fixture
def synthetic_evidence() -> dict:
    metrics = {"observations": 20, "total_return": .02, "cagr": .01, "annual_volatility": .08, "sharpe": .12, "max_drawdown": -.04, "calmar": .25}
    document = {
        "schema_version": "3.0",
        "study_id": "LLM-ALPHA-DISCOVERY",
        "evidence_label": "walk_forward_out_of_sample",
        "generated_at_utc": "2030-01-15T00:00:00Z",
        "period": {"start": "2029-01-01", "end": "2029-12-31", "observations": 20},
        "research_scale": {"instrument_count": 10, "qualified_observations": 80, "positive_annual_buckets": 5},
        "performance": [
            {"profile": profile, "one_way_cost_bps": cost, "metrics": deepcopy(metrics)}
            for profile in ("primary", "higher_risk") for cost in (5, 10, 20)
        ],
        "annual_evidence": [{"profile": "primary", "one_way_cost_bps": 5, "year": year, "period_return": .01} for year in range(2025, 2030)],
        "capacity": [{"profile": profile, "capital_scenario_mn": capital, "p95_adv_participation": .02, "maximum_adv_participation": .08} for profile in ("primary", "higher_risk") for capital in (2, 5)],
        "statistical_evidence": {"qualified_observations": 80, "hac_t_statistic": 2.5, "positive_annual_buckets": 5},
        "disclosures": ["historical_simulation_not_live", "walk_forward_out_of_sample", "transaction_costs_are_scenarios", "capacity_is_scenario_based", "private_discovery_system_not_distributed"],
    }
    return deepcopy(document)
