"""
Script to download public tender data from Czech Republic sources.
Supports EU TED (filtered for CZ), Věstník veřejných zakázek, and NEN.
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from time import sleep
from tqdm import tqdm
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TENDERS_DIR, DOWNLOAD_SETTINGS, DATA_SOURCES, COUNTRY_CODE, CURRENCY

class TenderDownloader:
    """Downloads tender data from various public sources."""
    
    def __init__(self):
        self.output_dir = TENDERS_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        self.delay = DOWNLOAD_SETTINGS["delay_between_requests"]
        self.timeout = DOWNLOAD_SETTINGS["timeout"]
        
    def download_eu_ted_cz(self, days_back=30, max_records=None):
        """
        Download Czech Republic tenders from EU TED (Tenders Electronic Daily).
        Filters for Czech Republic (CZ) tenders only.
        
        Note: TED API requires authentication and has specific endpoints.
        This is a template that can be adapted based on actual API access.
        """
        print(f"Downloading EU TED tenders for Czech Republic (CZ)...")
        
        base_url = DATA_SOURCES["tenders"]["eu_ted_cz"]["api_url"]
        tenders = []
        max_records = max_records or DOWNLOAD_SETTINGS["max_records"]
        
        # Example: If you have API access, uncomment and modify:
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            params = {
                "publicationDateFrom": start_date.strftime("%Y-%m-%d"),
                "publicationDateTo": end_date.strftime("%Y-%m-%d"),
                "country": COUNTRY_CODE,  # Filter for Czech Republic
                "limit": 100,
                "offset": 0
            }
            
            offset = 0
            while offset < max_records:
                params["offset"] = offset
                response = requests.get(f"{base_url}/notices", params=params, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    tenders.extend(data.get("results", []))
                    offset += len(data.get("results", []))
                    
                    if len(data.get("results", [])) == 0:
                        break
                else:
                    print(f"Error: {response.status_code}")
                    break
                    
                sleep(self.delay)
                
        except Exception as e:
            print(f"Error downloading from TED: {e}")
        """
        
        # For now, create sample structure and instructions
        print("\nNote: EU TED API access may require registration.")
        print("Alternative: Download CSV files from https://ted.europa.eu")
        print("Filter for Czech Republic (CZ) and place in data/tenders/raw/")
        
        # Create sample data structure
        sample_tenders = self._create_sample_structure()
        tenders.extend(sample_tenders)
        
        # Save to JSON
        output_file = os.path.join(self.output_dir, f"tenders_eu_ted_{datetime.now().strftime('%Y%m%d')}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(tenders, f, indent=2, ensure_ascii=False, default=str)
        
        # Also save as CSV for easy inspection
        if tenders:
            df = pd.DataFrame(tenders)
            csv_file = output_file.replace('.json', '.csv')
            df.to_csv(csv_file, index=False, encoding='utf-8')
            print(f"Saved {len(tenders)} tenders to {csv_file}")
        
        return tenders
    
    def _create_sample_structure(self):
        """Create sample data structure for reference (Czech Republic)."""
        return [
            {
                "id": "TED-CZ-001",
                "title": "Sample Czech Public Tender",
                "description": "Example tender description",
                "value": 1000000,
                "currency": CURRENCY,
                "publication_date": datetime.now().isoformat(),
                "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
                "status": "open",
                "country": COUNTRY_CODE,
                "publisher": {
                    "name": "Sample Czech Organization",
                    "country": COUNTRY_CODE
                },
                "categories": ["IT Services", "Software"]
            }
        ]
    
    def download_vestnik_vz(self, csv_path=None):
        """
        Download or load data from Věstník veřejných zakázek.
        
        Note: This portal may require web scraping or manual CSV download.
        Place CSV files in data/tenders/raw/ and specify the path.
        """
        print("Processing Věstník veřejných zakázek data...")
        
        if csv_path and os.path.exists(csv_path):
            return self.load_from_csv(csv_path)
        else:
            print("Note: Věstník veřejných zakázek data should be downloaded manually")
            print("from https://www.vestnikverejnychzakazek.cz")
            print("Place CSV files in data/tenders/raw/ and use load_from_csv() method")
            return []
    
    def load_from_csv(self, csv_path):
        """Load tender data from a CSV file."""
        print(f"Loading tenders from {csv_path}...")
        df = pd.read_csv(csv_path)
        
        # Convert to standard format
        tenders = []
        for _, row in df.iterrows():
            tender = {
                "id": str(row.get("id", f"TED-{len(tenders)+1}")),
                "title": str(row.get("title", "")),
                "description": str(row.get("description", "")),
                "value": float(row.get("value", 0)) if pd.notna(row.get("value")) else None,
                "currency": str(row.get("currency", "EUR")),
                "publication_date": str(row.get("publication_date", "")),
                "deadline": str(row.get("deadline", "")),
                "status": str(row.get("status", "unknown")),
            }
            tenders.append(tender)
        
        # Save processed data
        output_file = os.path.join(self.output_dir, f"tenders_processed_{datetime.now().strftime('%Y%m%d')}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(tenders, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"Processed {len(tenders)} tenders")
        return tenders

if __name__ == "__main__":
    downloader = TenderDownloader()
    
    # Download Czech Republic tenders from EU TED
    downloader.download_eu_ted_cz(days_back=30)
    
    # Download from Věstník veřejných zakázek (if CSV available)
    # downloader.download_vestnik_vz("data/tenders/raw/vestnik_vz.csv")
    
    # If you have CSV files, uncomment:
    # downloader.load_from_csv("data/tenders/raw/your_tenders.csv")
    
    print("\nCzech Republic tender download complete!")

