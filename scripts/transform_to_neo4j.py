"""
Transform downloaded data into Neo4j-compatible format.
Creates nodes and relationships in a structured format ready for import.
"""

import os
import json
import glob
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TENDERS_DIR, COMPANIES_DIR, PEOPLE_DIR, TRANSFORMED_DIR, NEO4J_SCHEMA

class Neo4jTransformer:
    """Transforms raw data into Neo4j node and relationship format."""
    
    def __init__(self):
        self.output_dir = TRANSFORMED_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        self.nodes = {
            "Tender": [],
            "Company": [],
            "Person": [],
            "Organization": []
        }
        self.relationships = {
            "SUBMITTED_BID": [],
            "WON": [],
            "WORKS_FOR": [],
            "DIRECTS": [],
            "PUBLISHED": []
        }
    
    def transform_all(self):
        """Transform all available data files."""
        print("Transforming data for Neo4j...")
        
        # Transform tenders
        tender_files = glob.glob(os.path.join(TENDERS_DIR, "*.json"))
        for file in tender_files:
            if "transformed" not in file:
                self.transform_tenders(file)
        
        # Transform companies
        company_files = glob.glob(os.path.join(COMPANIES_DIR, "*.json"))
        for file in company_files:
            if "transformed" not in file:
                self.transform_companies(file)
        
        # Transform people
        people_files = glob.glob(os.path.join(PEOPLE_DIR, "*.json"))
        for file in people_files:
            if "transformed" not in file:
                self.transform_people(file)
        
        # Create relationships
        self.create_relationships()
        
        # Save transformed data
        self.save_transformed_data()
        
        print(f"\nTransformation complete!")
        print(f"Nodes: {sum(len(v) for v in self.nodes.values())}")
        print(f"Relationships: {sum(len(v) for v in self.relationships.values())}")
    
    def transform_tenders(self, file_path):
        """Transform tender data into Tender nodes."""
        print(f"Processing tenders from {os.path.basename(file_path)}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            tenders = json.load(f)
        
        for tender in tenders:
            node = {
                "id": tender.get("id", f"TENDER-{len(self.nodes['Tender'])}"),
                "title": tender.get("title", ""),
                "description": tender.get("description", ""),
                "value": tender.get("value"),
                "currency": tender.get("currency", "CZK"),  # Default to CZK for Czech Republic
                "publication_date": tender.get("publication_date", ""),
                "deadline": tender.get("deadline", ""),
                "status": tender.get("status", "unknown"),
                "country": tender.get("country", "CZ"),  # Default to Czech Republic
                "source": tender.get("source", "unknown")
            }
            
            # Clean None values
            node = {k: v for k, v in node.items() if v is not None}
            self.nodes["Tender"].append(node)
            
            # Create Organization node for publisher if available
            publisher = tender.get("publisher", {})
            if publisher:
                org_id = f"ORG-{publisher.get('name', '').replace(' ', '_')}"
                org_node = {
                    "id": org_id,
                    "name": publisher.get("name", ""),
                    "type": publisher.get("type", "public_authority"),
                    "country": publisher.get("country", "")
                }
                
                # Check if organization already exists
                if not any(o["id"] == org_id for o in self.nodes["Organization"]):
                    self.nodes["Organization"].append(org_node)
                
                # Create PUBLISHED relationship
                rel = {
                    "from": org_id,
                    "to": node["id"],
                    "publication_date": node.get("publication_date", "")
                }
                self.relationships["PUBLISHED"].append(rel)
    
    def transform_companies(self, file_path):
        """Transform company data into Company nodes."""
        print(f"Processing companies from {os.path.basename(file_path)}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            companies = json.load(f)
        
        for company in companies:
            node = {
                "id": company.get("id", f"COMP-{len(self.nodes['Company'])}"),
                "name": company.get("name", ""),
                "registration_number": company.get("registration_number", ""),
                "ico": company.get("ico", ""),  # IČO - Czech company ID
                "dic": company.get("dic", ""),  # DIČ - Czech tax ID
                "country": company.get("country") or company.get("jurisdiction", ""),
                "address": company.get("address", ""),
                "founded_date": company.get("incorporation_date") or company.get("founded_date", ""),
                "company_type": company.get("company_type", ""),
                "status": company.get("status", ""),
                "source": company.get("source", "unknown")
            }
            
            # Clean None values
            node = {k: v for k, v in node.items() if v is not None and v != ""}
            self.nodes["Company"].append(node)
    
    def transform_people(self, file_path):
        """Transform people data into Person nodes and relationships."""
        print(f"Processing people from {os.path.basename(file_path)}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            people = json.load(f)
        
        for person in people:
            node = {
                "id": person.get("id", f"PERSON-{len(self.nodes['Person'])}"),
                "name": person.get("name", ""),
                "role": person.get("role", ""),
                "nationality": person.get("nationality", ""),
                "source": person.get("source", "unknown")
            }
            
            # Clean None values
            node = {k: v for k, v in node.items() if v is not None and v != ""}
            self.nodes["Person"].append(node)
            
            # Create WORKS_FOR or DIRECTS relationship if company_id exists
            company_id = person.get("company_id")
            if company_id:
                rel_type = "DIRECTS" if person.get("role", "").lower() in ["director", "ceo", "cfo", "chairman"] else "WORKS_FOR"
                rel = {
                    "from": node["id"],
                    "to": company_id,
                    "position": person.get("position", ""),
                    "start_date": person.get("start_date", ""),
                    "end_date": person.get("end_date", ""),
                    "appointment_date": person.get("appointment_date", "")
                }
                
                # Clean None values
                rel = {k: v for k, v in rel.items() if v is not None and v != ""}
                self.relationships[rel_type].append(rel)
    
    def create_relationships(self):
        """Create additional relationships based on data patterns."""
        print("Creating relationships...")
        
        # Example: If you have bid data, create SUBMITTED_BID relationships
        # This would come from additional data sources or manual mapping
        # For now, this is a placeholder for custom relationship creation
        
        pass
    
    def save_transformed_data(self):
        """Save transformed nodes and relationships to JSON files."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save nodes
        for node_type, nodes in self.nodes.items():
            if nodes:
                output_file = os.path.join(self.output_dir, f"nodes_{node_type.lower()}_{timestamp}.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(nodes, f, indent=2, ensure_ascii=False, default=str)
                print(f"Saved {len(nodes)} {node_type} nodes to {os.path.basename(output_file)}")
        
        # Save relationships
        for rel_type, rels in self.relationships.items():
            if rels:
                output_file = os.path.join(self.output_dir, f"rels_{rel_type.lower()}_{timestamp}.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(rels, f, indent=2, ensure_ascii=False, default=str)
                print(f"Saved {len(rels)} {rel_type} relationships to {os.path.basename(output_file)}")
        
        # Save combined file
        combined = {
            "nodes": self.nodes,
            "relationships": self.relationships,
            "timestamp": timestamp
        }
        combined_file = os.path.join(self.output_dir, f"neo4j_data_{timestamp}.json")
        with open(combined_file, 'w', encoding='utf-8') as f:
            json.dump(combined, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\nAll transformed data saved to {self.output_dir}")

if __name__ == "__main__":
    transformer = Neo4jTransformer()
    transformer.transform_all()

