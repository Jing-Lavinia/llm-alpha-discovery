# LLM-Driven Alpha Discovery

> A quantitative R&D system that turns machine-scale hypothesis exploration into validated alpha evidence.

![Research overview](figures/research_overview.png)

This project turns an LLM from a factor-idea generator into an operational quantitative research system. The language model expands and formalizes the hypothesis space; deterministic code controls whether any candidate is accepted as alpha. Generation increases research breadth, but measurement remains governed by conventional quantitative discipline.

The system was deployed on a 257-instrument exchange-traded universe. One discovered factor produced **13.83% net CAGR**, **1.55 Sharpe**, and **−4.25% maximum drawdown** in walk-forward out-of-sample evaluation from 2021-01-01 through 2025-08-21, after a modeled one-way trading cost of 5 bp. A higher-risk portfolio expression produced **27.80% net CAGR**, **1.52 Sharpe**, and **−8.47% maximum drawdown** under the same cost assumption.

## Why this system exists

Factor research is limited not only by computation, but by the number of economic ideas a researcher can formulate precisely, implement correctly, and evaluate consistently. Each candidate must cross several different forms of work: economic reasoning, formal specification, data alignment, statistical testing, portfolio construction, and implementation analysis. The process is expensive even when the final answer is rejection.

LLM-based quantitative research has begun moving from [human–AI factor formulation](https://arxiv.org/abs/2308.00016) toward [automated data-centric R&D](https://arxiv.org/abs/2310.11249) and [full-stack quantitative research agents](https://arxiv.org/abs/2505.15155). The important shift is no longer whether a language model can write a plausible formula. It is whether open-ended reasoning can be connected to an empirical process that is executable, chronologically valid, and economically measurable.

![Evolution of the research problem](figures/research_context.png)

That is the problem addressed here. Instead of treating every factor as a separate research project, the system establishes a repeatable path from a broad research objective to an executable candidate and, ultimately, a retained evidence record. The durable output is not a single formula: it is a cumulative research capability for producing and evaluating evidence at scale.

![System overview](figures/system_architecture.png)

## From plausible ideas to measurable research

A financially coherent hypothesis is not yet alpha. A candidate can look statistically interesting and still fail once information timing, turnover, portfolio construction, trading costs, drawdown, or liquidity are included. Conversely, increasing leverage can magnify an exposure but cannot repair a weak underlying return source.

The system therefore separates two responsibilities:

- **The LLM explores and formalizes.** It converts a research domain into structured, executable candidates instead of unstructured investment commentary.
- **The quantitative layer measures and decides.** It applies deterministic data, timing, statistical, portfolio, cost, and risk logic. The LLM never determines that its own output works.

![Division of research responsibilities](figures/research_roles.png)

This separation is the key control. It keeps the generative component open enough to broaden the hypothesis space while preventing persuasive language from becoming empirical evidence.

## One research path for every candidate

Every generated candidate enters the same evaluation path. It must be executable; use only information available at the simulated decision time; pass chronological out-of-sample measurement; survive portfolio construction and explicit frictions; and produce an evidence record that can be compared with other experiments.

![Candidate evaluation path](figures/evaluation_path.png)

These rules remain stable even when the internal discovery method evolves. The same measurement standard is applied to favorable and unfavorable candidates, and a failed experiment cannot be rescued through narrative reinterpretation. This is how the system connects the flexibility of an LLM to the auditability expected in quantitative research.

## A real empirical deployment

To test whether the system could produce more than plausible research language, it was deployed on an exchange-traded cross section of 257 instruments. A discovered factor was carried from machine-generated research output through point-in-time data preparation, chronological evaluation, portfolio construction, and cost analysis.

| Evidence | Published result |
|---|---:|
| Out-of-sample period | 2021-01-01 to 2025-08-21 |
| Portfolio observations | 1,123 |
| Research universe | 257 instruments |
| Qualified cross-sectional observations | 1,799 |
| HAC t-statistic | 5.27 |
| Positive calendar buckets | 5 / 5 |

The reported statistics describe walk-forward out-of-sample performance. Cross-sectional inference uses heteroskedasticity-and-autocorrelation-consistent statistics, while portfolio evidence is evaluated after modeled trading costs.

## Return and risk expression

The same discovered factor is shown through two portfolio risk expressions. The higher-risk version approximately doubles both return and volatility while preserving a similar Sharpe ratio; it is not presented as a separately discovered strategy.

![Return and risk profile](figures/performance_profile.png)

| Portfolio expression | One-way cost | Net CAGR | Sharpe | Max drawdown | Calmar |
|---|---:|---:|---:|---:|---:|
| Primary | 5 bp | **13.83%** | **1.55** | **−4.25%** | **3.25** |
| Primary | 10 bp | 8.58% | 1.00 | −5.67% | 1.51 |
| Primary | 20 bp | −1.21% | −0.10 | −19.08% | −0.06 |
| Higher risk | 5 bp | **27.80%** | **1.52** | **−8.47%** | **3.28** |
| Higher risk | 10 bp | 16.27% | 0.96 | −11.31% | 1.44 |
| Higher risk | 20 bp | −3.79% | −0.14 | −36.97% | −0.10 |

## What implementation changes

![Cost sensitivity](figures/cost_sensitivity.png)

Performance remains positive when the primary cost assumption is doubled from 5 to 10 bp, but both portfolio expressions lose money under the 20 bp stress. The factor therefore has measurable economic margin in its intended setting, while implementation quality remains part of the alpha rather than an afterthought.

The cost curve is also a useful research result. It identifies the region in which the statistical signal continues to support a viable portfolio and the point at which trading friction overwhelms the return source.

## What the result reveals across time

![Annual consistency](figures/annual_consistency.png)

The primary 5 bp expression was positive in all five reported calendar buckets. The weakest period returned 4.78% and the strongest 18.27%. The magnitude is not constant, which is expected for a market signal, but the positive sign across the reported periods provides evidence beyond the full-sample Sharpe ratio alone.

This does not require the factor to be equally strong in every regime. It asks a more realistic question: whether the measured return source persists through materially different market environments without one isolated period accounting for the entire result.

## Where scaling becomes difficult

![Capacity scenarios](figures/capacity_scenarios.png)

Typical participation remains moderate at the smaller capital scenario, while maximum participation rises much faster when both portfolio risk and capital increase. Tail liquidity, rather than average liquidity, is therefore the relevant scaling constraint.

| Portfolio expression | Capital scenario | p95 ADV participation | Maximum ADV participation |
|---|---:|---:|---:|
| Primary | 2m | 0.83% | 8.61% |
| Primary | 5m | 2.08% | 21.54% |
| Higher risk | 2m | 1.67% | 17.29% |
| Higher risk | 5m | 4.17% | 43.22% |

The capacity figures are scenario diagnostics rather than a claim of executable size. Their purpose is to show how the strategy’s implementation boundary changes as capital and risk are scaled.

## The factor is an output, not the endpoint

This deployment produced one validated factor, but the factor is not the limit of the project. The reusable asset is the system around it: a way to expand research breadth, apply one empirical standard, preserve successful and unsuccessful experiments, and continue building a cumulative factor inventory.

That distinction matters because automated discovery should not be judged by the most persuasive generated idea. It should be judged by the quality of the research objects it produces, the discipline of the experiments that reject them, and the portfolio evidence retained by the candidates that survive.

The discovery engine is a proprietary system boundary. This repository exposes the system-level reasoning and aggregate evidence needed to evaluate the work without distributing the methods required to reconstruct it. The public code validates the evidence contract and artifact manifest; it does not generate the reported factor.

## Repository map

```text
README.md                          Research story, system thesis, and evidence
RESEARCH_NOTE.md                   Concise research narrative
EVIDENCE_AND_LIMITATIONS.md        Metric definitions and interpretation bounds
docs/SYSTEM_OVERVIEW.md            Public capability map
docs/data-sources-and-licensing.md Data and redistribution boundary
evidence/                          Versioned aggregate evidence and checksums
schemas/                           Machine-readable evidence contracts
src/alpha_evidence/                Evidence and manifest validators
scripts/                           Deterministic figure and manifest builders
tests/                             Contract, consistency, and integrity tests
```

## Verify the public evidence

```bash
python -m pip install -e '.[dev]'
pytest
alpha-evidence evidence evidence/aggregate-evidence.v3.json
alpha-evidence manifest evidence/release-manifest.v1.json \
  --allowlist evidence/release-allowlist.txt
```

Historical simulation only; not investment advice or a guarantee of future results.
