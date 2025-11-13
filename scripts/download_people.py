"""
Script to download people data (directors, officers, public officials).
Can integrate with company registries and public records.
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
from config import PEOPLE_DIR, DOWNLOAD_SETTINGS

class PeopleDownloader:
    """Downloads people data from various public sources."""
    
    def __init__(self):
        self.output_dir = PEOPLE_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        self.delay = DOWNLOAD_SETTINGS["delay_between_requests"]
        self.timeout = DOWNLOAD_SETTINGS["timeout"]
    
    def download_from_companies(self, companies_file):
        """
        Extract people data from company records.
        This assumes company data includes director/officer information.
        """
        print("Extracting people data from company records...")
        
        if not os.path.exists(companies_file):
            print(f"Error: Companies file not found: {companies_file}")
            return []
        
        with open(companies_file, 'r', encoding='utf-8') as f:
            companies = json.load(f)
        
        people = []
        people_ids = set()
        
        for company in companies:
            # Extract directors/officers if available in company data
            # This is a template - adjust based on your data structure
            company_id = company.get("id", "")
            company_name = company.get("name", "")
            
            # If company data has officers/directors field
            officers = company.get("officers", [])
            directors = company.get("directors", [])
            
            for person_data in officers + directors:
                person_id = person_data.get("id") or f"{person_data.get('name', '').replace(' ', '_')}_{company_id}"
                
                if person_id not in people_ids:
                    person = {
                        "id": person_id,
                        "name": person_data.get("name", ""),
                        "role": person_data.get("role", ""),
                        "company_id": company_id,
                        "company_name": company_name,
                        "appointment_date": person_data.get("appointment_date", ""),
                        "resignation_date": person_data.get("resignation_date", ""),
                        "nationality": person_data.get("nationality", ""),
                        "source": "company_registry"
                    }
                    people.append(person)
                    people_ids.add(person_id)
        
        # Save to JSON
        output_file = os.path.join(self.output_dir, f"people_from_companies_{datetime.now().strftime('%Y%m%d')}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(people, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"Extracted {len(people)} people from company records")
        return people
    
    def load_from_csv(self, csv_path):
        """Load people data from a CSV file."""
        print(f"Loading people from {csv_path}...")
        df = pd.read_csv(csv_path)
        
        people = []
        for _, row in df.iterrows():
            person = {
                "id": str(row.get("id", f"PERSON-{len(people)+1}")),
                "name": str(row.get("name", "")),
                "role": str(row.get("role", "")),
                "company_id": str(row.get("company_id", "")),
                "position": str(row.get("position", "")),
                "start_date": str(row.get("start_date", "")),
                "end_date": str(row.get("end_date", "")),
                "source": str(row.get("source", "manual"))
            }
            people.append(person)
        
        output_file = os.path.join(self.output_dir, f"people_processed_{datetime.now().strftime('%Y%m%d')}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(people, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"Processed {len(people)} people")
        return people
    
    def create_sample_data(self):
        """Create sample people data structure for testing."""
        sample_people = [
            {
                "id": "PERSON-001",
                "name": "John Smith",
                "role": "Director",
                "company_id": "COMP-001",
                "position": "CEO",
                "start_date": "2020-01-01",
                "end_date": None,
                "source": "sample"
            },
            {
                "id": "PERSON-002",
                "name": "Jane Doe",
                "role": "Director",
                "company_id": "COMP-001",
                "position": "CFO",
                "start_date": "2019-06-01",
                "end_date": None,
                "source": "sample"
            }
        ]
        
        output_file = os.path.join(self.output_dir, f"people_sample_{datetime.now().strftime('%Y%m%d')}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sample_people, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"Created sample data with {len(sample_people)} people")
        return sample_people

if __name__ == "__main__":
    downloader = PeopleDownloader()
    
    # Create sample data for testing
    downloader.create_sample_data()
    
    # If you have company files with people data:
    # companies_file = "data/companies/companies_opencorporates_YYYYMMDD.json"
    # downloader.download_from_companies(companies_file)
    
    # If you have CSV files:
    # downloader.load_from_csv("path/to/your/people.csv")
    
    print("\nPeople download complete!")

