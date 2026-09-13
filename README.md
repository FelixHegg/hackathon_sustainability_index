# Sustainability Profit Horizon

Sustainability is defined as the capacity to maintain, support, or continue a process or system over a long period of time. This hackathon project estimates how many years a company can absorb rising CO₂, water, and electricity prices before its current annual profit is fully consumed by the additional costs. Thus, the longer it can absorb these costs, the more sustainable it is.

## Run and reproduce

Python 3 is required. From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install pandas numpy pydantic google-genai
python3 index_calculation.py
```

The calculation reads `sp500_metrics.csv` and `projected_resource_costs.csv`, then recreates `profit_impact_years.csv`.

The committed company metrics can optionally be refreshed with Gemini and live web search. This is slower, requires a `GEMINI_API_KEY`, and may not reproduce the committed values exactly because web sources and model responses can change:

```bash
GEMINI_API_KEY="your-key" python3 data_extraction.py
```

This writes `sp500_metrics.csv`, which can be reviewed before replacing or otherwise using the committed metrics.

## Methodology

Let company $i$ have current profit $P_i$ and annual usage $u_{i,r}$ of resource $r$, where $r$ is CO₂, water, or electricity. Let $c_r(t)$ be the projected unit price in year $t$, and let the base year be $b=2026$. The additional annual cost in year $t$ is

$$
\Delta C_i(t)=\sum_r u_{i,r}\bigl(c_r(t)-c_r(b)\bigr),
$$

so projected profit after the price increase is $P_i(t)=P_i-\Delta C_i(t)$. The reported sustainability horizon is

$$
\tau_i=\min\{t-b\mid \Delta C_i(t)\ge P_i\}.
$$

The same calculation is also made for each resource separately. `> 74` means the company does not reach zero profit within the available 2026–2100 projections. The model is a stress-test index: it assumes constant profit and resource use, attributes no growth or mitigation, and counts only price increases above the base-year costs. Company data gathered by the extraction script may include model estimates when reported values are unavailable, so results should be treated as indicative rather than forecasts.
