import csv
import json
import time
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# Initialize the standard Google GenAI client.
# Ensure your API key is stored in the GEMINI_API_KEY environment variable.
client = genai.Client()

# # 1. The Researcher: Needs web search capabilities and good reasoning
# RESEARCH_MODEL = "gemini-3.5-flash"

# # 2. The Extractor: Only needs to read plain text and output JSON. 
# # Using Flash-Lite here significantly reduces your API costs.
# EXTRACTOR_MODEL = "gemini-3.5-flash-lite"

RESEARCH_MODEL = "gemini-3.5-flash-lite"

# 2. The Extractor: Only needs to read plain text and output JSON. 
# Using Flash-Lite here significantly reduces your API costs.
EXTRACTOR_MODEL = "gemini-3.5-flash-lite"

# Pydantic schema using float types and explicit units
class CompanyMetrics(BaseModel):
    electricity_usage_mwh: float = Field(
        description="Annual electricity usage in MWh. Output the pure number only."
    )
    co2_emissions_metric_tons: float = Field(
        description="Annual CO2 emissions in metric tons. Output the pure number only."
    )
    water_usage_cubic_meters: float = Field(
        description="Annual water usage in cubic meters. Output the pure number only."
    )
    revenue_usd: float = Field(
        description="Annual revenue in absolute USD (e.g., 32680000000 for $32.68 Billion). Output the pure number only."
    )
    profit_usd: float = Field(
        description="Annual profit or net income in absolute USD. Output the pure number only."
    )

def process_companies():
    input_filename = "sp500_remaining.csv"
    output_filename = "sp500_metrics_remaining.csv"
    
    # Read the input companies
    with open(input_filename, mode="r", encoding="utf-8") as infile:
        reader = csv.reader(infile)
        # Uncomment the next line if your CSV has a header row
        # next(reader, None) 
        companies = list(reader)

    print(f"Loaded {len(companies)} companies.")
        
    # Open the output CSV
    with open(output_filename, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.writer(outfile)
        
        # Write the updated header indicating the specific units
        writer.writerow([
            "Ticker", "Company Name", "Electricity Usage (MWh)", 
            "CO2 Emissions (Metric Tons)", "Water Usage (Cubic Meters)", 
            "Revenue (USD)", "Profit (USD)"
        ])
        
        for i, row in enumerate(companies):
            if len(row) < 2:
                print(f"warning: stopped at row {i} {row}")
                continue
                
            ticker, company_name = row[0].strip(), row[1].strip()
            print(f"Processing {i+1}/{len(companies)}: {company_name} ({ticker})")
            
            try:
                # --- STEP 1: THE RESEARCHER ---
                # Search the live web for the latest reports and return plain text
                research_prompt = (
                    f"Search the web for the latest annual ESG (Environmental, Social, and Governance) "
                    f"and financial reports for {company_name} ({ticker}). "
                    f"Find their exact annual usage of electricity (in MWh), CO2 emissions (in metric tons), "
                    f"water usage (in cubic meters), revenue (in USD), and profit (in USD)."
                )
                
                research_response = client.models.generate_content(
                    model=RESEARCH_MODEL,
                    contents=research_prompt,
                    config=types.GenerateContentConfig(
                        tools=[{"google_search": {}}], 
                        temperature=0.2,
                        thinking_config=types.ThinkingConfig(thinking_budget=1024),
                    )
                )
                
                research_text = research_response.text
                print(f"  -> Research complete. Extracting metrics...")

                # --- STEP 2: THE EXTRACTOR ---
                # Parse the raw text into the strict JSON schema
                extraction_prompt = (
                    f"Extract the requested numerical metrics for {company_name} from the following text. "
                    f"Output strictly according to the schema. If a metric is not present, estimate it based on industry scale.\n\n"
                    f"TEXT:\n{research_text}"
                )

                extraction_response = client.models.generate_content(
                    model=EXTRACTOR_MODEL,
                    contents=extraction_prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=CompanyMetrics,
                        temperature=0.0, # Zero temperature is ideal for strict data extraction
                    )
                )
                
                # Parse the guaranteed JSON string
                data = json.loads(extraction_response.text)
                
                # Append to CSV using the explicit keys
                writer.writerow([
                    ticker, 
                    company_name, 
                    data.get("electricity_usage_mwh", "N/A"),
                    data.get("co2_emissions_metric_tons", "N/A"),
                    data.get("water_usage_cubic_meters", "N/A"),
                    data.get("revenue_usd", "N/A"),
                    data.get("profit_usd", "N/A")
                ])
                print(f"  -> Successfully extracted data to CSV.")
                
            except Exception as e:
                print(f"  -> Error extracting data for {company_name}: {e}")
                writer.writerow([ticker, company_name, "Error", "Error", "Error", "Error", "Error"])
            
            # --- FORCE WRITE TO DISK ---
            # This ensures you can open the CSV and see results while the script is still running
            outfile.flush() 
            
            # Pause to respect rate limits. Two API calls are made per iteration now.
            time.sleep(1)
            
            # Remove or comment out the line below when you are ready to process all rows
            # raise ValueError("stop here")
            
if __name__ == "__main__":
    process_companies()