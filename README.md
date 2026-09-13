# Sustainability Profit Horizon

Sustainability is the ability of a system to continue over time; a perfectly sustainable company could continue operating indefinitely by definition. We turn that idea into a measurable score by asking how many years a company can absorb projected increases in the costs of freshwater, electricity, and CO₂ emissions. Using research-based cost projections and each company's current resource use and profit, the score is the number of years until the additional annual costs consume its current annual profit. A larger score therefore represents a longer sustainability horizon.

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

The method follows directly from the definition above. If sustainability is the ability to continue operating, then a natural measure is the length of time for which a company can withstand increasing resource costs. We use research-based projections of the unit costs of freshwater, electricity, and CO₂ emissions, and apply their increases to each company's present annual resource use. We then compare the resulting additional annual cost with the company's current annual profit.

Formally, let $\mathcal{R}=\{\mathrm{CO_2},\mathrm{water},\mathrm{electricity}\}$ be the set of resources. For company $i$, let $P_i$ denote current annual profit and $u_{i,r}$ its annual use of resource $r\in\mathcal{R}$. Let $c_r(t)$ be the projected unit cost of resource $r$ in year $t$, and let the base year be $b=2026$. Holding resource use constant, the additional annual cost caused by price increases in year $t$ is

$$
\Delta C_i(t)=\sum_{r\in\mathcal{R}}u_{i,r}\bigl(c_r(t)-c_r(b)\bigr).
$$

The company's profit after this modeled cost increase is therefore

$$
P_i(t)=P_i-\Delta C_i(t).
$$

Its sustainability horizon is the number of years from the base year until this modeled profit first reaches zero:

$$
\tau_i=\min\bigl\{t-b\mid P_i(t)\le 0\bigr\}
=\min\bigl\{t-b\mid \Delta C_i(t)\ge P_i\bigr\}.
$$

The same calculation is also performed for each resource separately by retaining only that resource's term in the sum. If the threshold is not reached during the available projection period, the score is reported as greater than the final modeled horizon.

This score is a comparative stress-test index, not a prediction of bankruptcy or literal cash exhaustion. It holds profit and resource use constant, includes only cost increases relative to the base year, and does not model growth, adaptation, substitution, or mitigation. Company metrics produced by the extraction script may also contain model estimates when reported values are unavailable. The results should therefore be interpreted as indicative sustainability horizons rather than financial forecasts.
