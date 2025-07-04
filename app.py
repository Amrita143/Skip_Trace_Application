from WebSearchLLM import llm_contact_search
import asyncio

# llm_contact_search function returns a dictionary: {"business_name": "Balloons Boutique SA", "business_address": "10828 Gulfdale St Suite B, San Antonio, TX 78216", "contact_numbers": ["210-617-7200","210-347-2236"],"search_resources": "(balloonsboutiquesa.shop, balloonsboutiquesa.com)"} 
from typing import Dict, List
import pandas as pd

df = pd.read_csv('data.csv')

OUTPUT_CSV         = "output.csv"   # where we store the LLM results
CONCURRENCY_LIMIT  = 1000           # how many parallel calls to allow
                                     # (tune to avoid API throttling)

# columns are Business_Name, Address, web_page, other_info

async def process_row(row: pd.Series) -> None:
    prompt_parts = []

    if pd.notna(row.get("Business_Name")):
        prompt_parts.append(f"Business Name: {row['Business_Name']}")
    if pd.notna(row.get("Address")):
        prompt_parts.append(f"Address: {row['Address']}")
    if pd.notna(row.get("web_page")):
        prompt_parts.append(f"web_page: {row['web_page']}")
    if pd.notna(row.get("other_info")):
        prompt_parts.append(f"other_info: {row['other_info']}")

    prompt = ", ".join(prompt_parts)
    print("Prompt ->", prompt)

    # --- call the LLM and await the result -----------------------------------
    result = await llm_contact_search(prompt)
    print("LLM result ->", result)
    return {
        "business_name":    result.get("business_name", ""),
        "business_address": result.get("business_address", ""),
        "contact_numbers":  ", ".join(result.get("contact_numbers", [])),  # store list as csv-friendly string
        "search_resources": result.get("search_resources", ""),
    }

async def main() -> None:
    """
    Orchestrates concurrent processing of all rows and writes the CSV.
    """
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

    async def _worker(row: pd.Series) -> Dict:
        # Limit the number of in-flight requests with the semaphore
        async with semaphore:
            return await process_row(row)

    tasks = [_worker(row) for _, row in df.iterrows()]
    results = await asyncio.gather(*tasks, return_exceptions=False)

    out_df = pd.DataFrame(results, columns=[
        "business_name",
        "business_address",
        "contact_numbers",
        "search_resources",
    ])
    out_df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved {len(out_df)} rows to {OUTPUT_CSV}")


# ---------------------------------------------------------------------------  
# Entry-point  
# ---------------------------------------------------------------------------  
if __name__ == "__main__":
    asyncio.run(main())