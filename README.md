# Sustainability Profit Horizon

Sustainability is defined as the capacity to maintain, support, or continue a process or system over a long period of time. This hackathon project estimates how many years a company can absorb rising CO₂, water, and electricity prices before its current annual profit is fully consumed by the additional costs. Thus, the longer it can absorb these costs, the more sustainable it is.

## Run and reproduce

Python 3 is required. From the repository root:

```bash
python3 -m pip install pandas numpy pydantic google-genai
python3 index_calculation.py
```

The calculation reads `sp500_metrics.csv` and `projected_resource_costs.csv`, then recreates `profit_impact_years.csv`.

The committed company metrics can optionally be regenerated with Gemini and live web search. After installing the dependencies shown above, set your Gemini API key and run the extraction script from the repository root:

```bash
export GEMINI_API_KEY="your-gemini-api-key"
python3 data_extraction.py
```

The script reads the company list from `sp500.csv` and writes the generated values to `sp500_metrics.csv`. It makes two LLM calls per company—one to research current web sources and one to extract structured metrics—so a full run can take some time and consume API quota.


## Methodology

Let company $i$ have current profit $P_i$ and annual usage $u_{i,r}$ of resource $r$, where $r$ is CO₂, water, or electricity. Let $c_r(t)$ be the projected unit price in year $t$, and let the base year be $b=2026$. The additional annual cost in year $t$ is

$$
\Delta C_i(t)=\sum_r u_{i,r}\bigl(c_r(t)-c_r(b)\bigr),
$$

so projected profit after the price increase is $P_i(t)=P_i-\Delta C_i(t)$. The reported sustainability horizon is

$$
\tau_i=\min\{t-b\mid \Delta C_i(t)\ge P_i\}.
$$

The same calculation is also made for each resource separately. `> 150` means the company does not reach zero profit within the available 2026–2100 projections. The model is a stress-test index: it assumes constant profit and resource use, attributes no growth or mitigation, and counts only price increases above the base-year costs. Company data gathered by the extraction script may include model estimates when reported values are unavailable, so results should be treated as indicative rather than forecasts.
