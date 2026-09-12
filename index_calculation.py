import pandas as pd
import numpy as np

def calculate_years_to_zero_profit(metrics_file, costs_file, output_file):
    print("Loading datasets...")
    # Load the datasets
    df_metrics = pd.read_csv(metrics_file)
    df_costs = pd.read_csv(costs_file)
    
    # Sort costs by year to ensure chronological order
    df_costs = df_costs.sort_values(by='year').reset_index(drop=True)
    base_year = df_costs['year'].iloc[0]
    max_years = df_costs['year'].iloc[-1] - base_year
    
    # Extract base costs (for the current/starting year)
    base_co2_cost = df_costs['co2_cost'].iloc[0]
    base_water_cost = df_costs['water_cost'].iloc[0]
    base_elec_cost = df_costs['electricity_cost'].iloc[0]
    
    # Calculate the price increase factor for each year compared to the base year
    df_costs['add_co2_factor'] = df_costs['co2_cost'] - base_co2_cost
    df_costs['add_water_factor'] = df_costs['water_cost'] - base_water_cost
    df_costs['add_elec_factor'] = df_costs['electricity_cost'] - base_elec_cost
    
    results = []
    
    print("Processing companies...")
    for index, row in df_metrics.iterrows():
        ticker = row['Ticker']
        company = row['Company Name']
        
        # Handle potential non-numeric data (like "Error" or "N/A" from the scraper script)
        try:
            profit = float(row['Profit (USD)'])
            co2_usage = float(row['CO2 Emissions (Metric Tons)'])
            water_usage = float(row['Water Usage (Cubic Meters)'])
            elec_usage = float(row['Electricity Usage (MWh)'])
        except (ValueError, TypeError):
            # Skip or mark as invalid if data is missing or "Error"
            results.append({
                'Ticker': ticker,
                'Company Name': company,
                'Years to 0 Profit (All)': 'Invalid Data',
                'Years to 0 Profit (CO2 only)': 'Invalid Data',
                'Years to 0 Profit (Water only)': 'Invalid Data',
                'Years to 0 Profit (Electricity only)': 'Invalid Data'
            })
            continue
            
        # If profit is already 0 or negative, they are at 0 years
        if pd.isna(profit) or profit <= 0:
            results.append({
                'Ticker': ticker,
                'Company Name': company,
                'Years to 0 Profit (All)': 0,
                'Years to 0 Profit (CO2 only)': 0,
                'Years to 0 Profit (Water only)': 0,
                'Years to 0 Profit (Electricity only)': 0
            })
            continue

        # Calculate the cumulative additional cost impact over time for this specific company
        add_co2_cost = co2_usage * df_costs['add_co2_factor']
        add_water_cost = water_usage * df_costs['add_water_factor']
        add_elec_cost = elec_usage * df_costs['add_elec_factor']
        
        # Total combined impact
        add_total_cost = add_co2_cost + add_water_cost + add_elec_cost
        
        # Helper function to find the first year the additional cost exceeds current profit
        def get_years_until_zero(cost_series):
            exceeds = cost_series >= profit
            if exceeds.any():
                idx = exceeds.idxmax() # Gets the first index where the condition is True
                return int(df_costs.loc[idx, 'year'] - base_year)
            else:
                return f'> {max_years}'

        # 1. Calculate combined
        years_all = get_years_until_zero(add_total_cost)
        # 2. Calculate isolated metrics
        years_co2 = get_years_until_zero(add_co2_cost)
        years_water = get_years_until_zero(add_water_cost)
        years_elec = get_years_until_zero(add_elec_cost)
        
        results.append({
            'Ticker': ticker,
            'Company Name': company,
            'Years to 0 Profit (All)': years_all,
            'Years to 0 Profit (CO2 only)': years_co2,
            'Years to 0 Profit (Water only)': years_water,
            'Years to 0 Profit (Electricity only)': years_elec
        })
        
    # Create output dataframe and save to CSV
    df_results = pd.DataFrame(results)
    df_results.to_csv(output_file, index=False)
    print(f"Success! Data exported to: {output_file}")

if __name__ == "__main__":
    calculate_years_to_zero_profit(
        metrics_file='sp500_metrics.csv',
        costs_file='projected_resource_costs.csv',
        output_file='profit_impact_years.csv'
    )