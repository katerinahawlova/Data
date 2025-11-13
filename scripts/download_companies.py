"""
Script to download Czech Republic company data from various sources.
Supports OpenCorporates API (CZ jurisdiction) and Obchodní rejstřík.
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime
from time import sleep
from tqdm import tqdm
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COMPANIES_DIR, DATA_SOURCES, DOWNLOAD_SETTINGS, COUNTRY_CODE, COUNTRY

class CompanyDownloader:
    """Downloads company data from various public sources."""
    
    def __init__(self):
        self.output_dir = COMPANIES_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        self.delay = DOWNLOAD_SETTINGS["delay_between_requests"]
        self.timeout = DOWNLOAD_SETTINGS["timeout"]
        self.opencorporates_api_key = DATA_SOURCES["companies"]["opencorporates_cz"].get("api_key", "")
        
    def download_opencorporates_cz(self, company_names=None, max_records=None):
        """
        Download Czech Republic company data from OpenCorporates API.
        Focuses on Czech jurisdiction (cz) companies.
        
        Args:
            company_names: List of company names to search for
            max_records: Maximum number of records to download
        """
        print(f"Downloading Czech Republic company data from OpenCorporates...")
        
        if not self.opencorporates_api_key:
            print("Warning: OpenCorporates API key not set. Using free tier (limited requests).")
            print("Get API key from: https://opencorporates.com/api_accounts/new")
        
        base_url = DATA_SOURCES["companies"]["opencorporates_cz"]["api_url"]
        jurisdiction = DATA_SOURCES["companies"]["opencorporates_cz"]["jurisdiction"]
        companies = []
        max_records = max_records or DOWNLOAD_SETTINGS["max_records"]
        
        # If no company names provided, use Czech-specific search terms
        if not company_names:
            company_names = ["s.r.o.", "a.s.", "společnost", "firma"]  # Common Czech company terms
        
        for search_term in tqdm(company_names[:10], desc="Searching companies"):
            try:
                params = {
                    "q": search_term,
                    "sparse": "true",
                    "per_page": 100
                }
                
                if self.opencorporates_api_key:
                    params["api_token"] = self.opencorporates_api_key
                
                # Always filter for Czech Republic
                params["jurisdiction_code"] = jurisdiction
                
                response = requests.get(
                    f"{base_url}/companies/search",
                    params=params,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", {}).get("companies", [])
                    
                    for result in results[:20]:  # Limit per search term
                        company = result.get("company", {})
                        company_data = {
                            "id": f"OC-CZ-{company.get('company_number', '')}",
                            "name": company.get("name", ""),
                            "registration_number": company.get("company_number", ""),
                            "ico": company.get("company_number", ""),  # IČO - Czech company ID
                            "jurisdiction": company.get("jurisdiction_code", ""),
                            "country": COUNTRY_CODE,
                            "company_type": company.get("company_type", ""),
                            "status": company.get("current_status", ""),
                            "incorporation_date": company.get("incorporation_date", ""),
                            "dissolution_date": company.get("dissolution_date", ""),
                            "opencorporates_url": company.get("opencorporates_url", ""),
                            "source": "opencorporates_cz"
                        }
                        companies.append(company_data)
                        
                        if len(companies) >= max_records:
                            break
                    
                    if len(companies) >= max_records:
                        break
                        
                elif response.status_code == 429:
                    print(f"Rate limit reached. Waiting...")
                    sleep(60)
                else:
                    print(f"Error {response.status_code}: {response.text[:200]}")
                
                sleep(self.delay)
                
            except Exception as e:
                print(f"Error downloading company data: {e}")
                continue
        
        # Save to JSON
        output_file = os.path.join(self.output_dir, f"companies_cz_opencorporates_{datetime.now().strftime('%Y%m%d')}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(companies, f, indent=2, ensure_ascii=False, default=str)
        
        # Also save as CSV
        if companies:
            df = pd.DataFrame(companies)
            csv_file = output_file.replace('.json', '.csv')
            df.to_csv(csv_file, index=False, encoding='utf-8')
            print(f"\nSaved {len(companies)} Czech companies to {csv_file}")
        
        return companies
    
    def download_obchodni_rejstrik(self, csv_path=None):
        """
        Download or load data from Obchodní rejstřík (Czech Commercial Register).
        
        Note: This requires web scraping or manual CSV download.
        Place CSV files in data/companies/raw/ and specify the path.
        """
        print("Processing Obchodní rejstřík data...")
        
        if csv_path and os.path.exists(csv_path):
            return self.load_from_csv(csv_path)
        else:
            print("Note: Obchodní rejstřík data should be downloaded manually")
            print("from https://or.justice.cz")
            print("Place CSV files in data/companies/raw/ and use load_from_csv() method")
            return []
    
    def load_from_csv(self, csv_path):
        """Load company data from a CSV file."""
        print(f"Loading companies from {csv_path}...")
        df = pd.read_csv(csv_path)
        
        companies = []
        for _, row in df.iterrows():
            company = {
                "id": str(row.get("id", f"COMP-CZ-{len(companies)+1}")),
                "name": str(row.get("name", "")),
                "registration_number": str(row.get("registration_number", "")),
                "ico": str(row.get("ico", "") or row.get("registration_number", "")),  # IČO
                "dic": str(row.get("dic", "")),  # DIČ - Czech tax ID
                "country": COUNTRY_CODE,
                "address": str(row.get("address", "")),
                "founded_date": str(row.get("founded_date", "")),
                "source": str(row.get("source", "manual"))
            }
            companies.append(company)
        
        output_file = os.path.join(self.output_dir, f"companies_processed_{datetime.now().strftime('%Y%m%d')}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(companies, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"Processed {len(companies)} companies")
        return companies

if __name__ == "__main__":
    downloader = CompanyDownloader()
    
    # Download Czech Republic companies from OpenCorporates
    downloader.download_opencorporates_cz(
        company_names=None,  # Will use Czech-specific search terms
        max_records=500
    )
    
    # Download from Obchodní rejstřík (if CSV available)
    # downloader.download_obchodni_rejstrik("data/companies/raw/obchodni_rejstrik.csv")
    
    # If you have CSV files, uncomment:
    # downloader.load_from_csv("data/companies/raw/your_companies.csv")
    
    print("\nCzech Republic company download complete!")

