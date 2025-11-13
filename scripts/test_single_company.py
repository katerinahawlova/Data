"""
Simple test script to download and load data for ONE Czech company by IČO.
Perfect for beginners to test the system!
"""

import os
import json
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COMPANIES_DIR, TRANSFORMED_DIR, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from scripts.download_companies import CompanyDownloader
from scripts.transform_to_neo4j import Neo4jTransformer
from scripts.load_to_neo4j import Neo4jLoader

def test_single_company(ico):
    """
    Test the entire pipeline with one company IČO.
    
    Args:
        ico: Czech company IČO (8 digits, e.g., "27074358")
    """
    print("=" * 60)
    print("TEST RUN: Single Company Pipeline")
    print("=" * 60)
    print(f"\nTesting with IČO: {ico}")
    print("\nThis will:")
    print("1. Download company data")
    print("2. Transform it for Neo4j")
    print("3. Load it into Neo4j")
    print("\n" + "-" * 60 + "\n")
    
    # Step 1: Download company data
    print("STEP 1: Downloading company data...")
    print("-" * 60)
    
    downloader = CompanyDownloader()
    
    # Try to get company by IČO from OpenCorporates
    try:
        import requests
        from config import DATA_SOURCES
        
        api_key = DATA_SOURCES["companies"]["opencorporates_cz"].get("api_key", "")
        base_url = DATA_SOURCES["companies"]["opencorporates_cz"]["api_url"]
        jurisdiction = "cz"
        
        # Search by company number (IČO)
        params = {
            "q": ico,
            "jurisdiction_code": jurisdiction,
            "per_page": 1
        }
        
        if api_key:
            params["api_token"] = api_key
        
        response = requests.get(
            f"{base_url}/companies/search",
            params=params,
            timeout=30
        )
        
        companies = []
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", {}).get("companies", [])
            
            if results:
                company = results[0].get("company", {})
                company_data = {
                    "id": f"OC-CZ-{company.get('company_number', ico)}",
                    "name": company.get("name", ""),
                    "registration_number": company.get("company_number", ico),
                    "ico": company.get("company_number", ico),
                    "jurisdiction": company.get("jurisdiction_code", "cz"),
                    "country": "CZ",
                    "company_type": company.get("company_type", ""),
                    "status": company.get("current_status", ""),
                    "incorporation_date": company.get("incorporation_date", ""),
                    "source": "opencorporates_cz"
                }
                companies.append(company_data)
                print(f"✓ Found company: {company_data['name']}")
            else:
                print(f"⚠ Company with IČO {ico} not found in OpenCorporates")
                print("Creating sample company data for testing...")
                companies.append({
                    "id": f"TEST-CZ-{ico}",
                    "name": f"Test Company {ico}",
                    "registration_number": ico,
                    "ico": ico,
                    "country": "CZ",
                    "source": "test"
                })
        else:
            print(f"⚠ API request failed. Creating sample data for testing...")
            companies.append({
                "id": f"TEST-CZ-{ico}",
                "name": f"Test Company {ico}",
                "registration_number": ico,
                "ico": ico,
                "country": "CZ",
                "source": "test"
            })
    
    except Exception as e:
        print(f"⚠ Error downloading: {e}")
        print("Creating sample company data for testing...")
        companies = [{
            "id": f"TEST-CZ-{ico}",
            "name": f"Test Company {ico}",
            "registration_number": ico,
            "ico": ico,
            "country": "CZ",
            "source": "test"
        }]
    
    # Save company data
    os.makedirs(COMPANIES_DIR, exist_ok=True)
    test_file = os.path.join(COMPANIES_DIR, f"test_company_{ico}.json")
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(companies, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"✓ Saved company data to: {test_file}\n")
    
    # Step 2: Transform data
    print("STEP 2: Transforming data for Neo4j...")
    print("-" * 60)
    
    transformer = Neo4jTransformer()
    transformer.transform_companies(test_file)
    
    # Save transformed data
    os.makedirs(TRANSFORMED_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    transformed_file = os.path.join(TRANSFORMED_DIR, f"test_neo4j_data_{timestamp}.json")
    
    transformed_data = {
        "nodes": transformer.nodes,
        "relationships": transformer.relationships,
        "timestamp": timestamp
    }
    
    with open(transformed_file, 'w', encoding='utf-8') as f:
        json.dump(transformed_data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"✓ Transformed data saved to: {transformed_file}")
    print(f"  - Nodes: {sum(len(v) for v in transformer.nodes.values())}")
    print(f"  - Relationships: {sum(len(v) for v in transformer.relationships.values())}\n")
    
    # Step 3: Load into Neo4j
    print("STEP 3: Loading data into Neo4j...")
    print("-" * 60)
    
    try:
        loader = Neo4jLoader()
        if loader.connect():
            # Load nodes
            total_nodes = 0
            for node_type, nodes in transformer.nodes.items():
                if nodes:
                    count = loader.load_nodes(node_type, nodes)
                    total_nodes += count
                    if count > 0:
                        print(f"  ✓ Loaded {count} {node_type} nodes")
            
            # Load relationships
            total_rels = 0
            for rel_type, rels in transformer.relationships.items():
                if rels:
                    count = loader.load_relationships(rel_type, rels)
                    total_rels += count
                    if count > 0:
                        print(f"  ✓ Loaded {count} {rel_type} relationships")
            
            loader.close()
            
            print(f"\n✓ Successfully loaded {total_nodes} nodes and {total_rels} relationships into Neo4j!")
            
        else:
            print("⚠ Could not connect to Neo4j. Please check:")
            print("  1. Is Neo4j running?")
            print("  2. Are connection details correct in config.py or .env?")
            print("  3. Is the database started?")
            
    except Exception as e:
        print(f"⚠ Error loading to Neo4j: {e}")
        print("\nYou can still view the transformed data in:")
        print(f"  {transformed_file}")
    
    # Step 4: Show next steps
    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Open Neo4j Browser (usually at http://localhost:7474)")
    print("2. Run this query to see your company:")
    print(f"   MATCH (c:Company {{ico: '{ico}'}}) RETURN c")
    print("\n3. Or see all companies:")
    print("   MATCH (c:Company) RETURN c LIMIT 10")
    print("\n4. Check the data files:")
    print(f"   - Company data: {test_file}")
    print(f"   - Transformed data: {transformed_file}")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    # You can provide IČO as command line argument or use example
    if len(sys.argv) > 1:
        ico = sys.argv[1]
    else:
        # Example IČO - you can replace this with a real one
        # This is just an example - replace with a real Czech company IČO
        ico = "27074358"  # Example - replace with real IČO
        print("No IČO provided. Using example IČO.")
        print("To use your own IČO, run: python scripts/test_single_company.py YOUR_ICO")
        print(f"Example IČO: {ico}\n")
    
    # Validate IČO format (should be 8 digits for Czech companies)
    if not ico.isdigit() or len(ico) != 8:
        print(f"⚠ Warning: IČO should be 8 digits. Using '{ico}' anyway...")
        print("   (This might be a test IČO)\n")
    
    test_single_company(ico)

