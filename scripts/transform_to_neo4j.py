"""
Transform downloaded data into Neo4j-compatible format.
Matches Czech schema from thesis: Osoba, Firma, Zadavatel, Zakazka, Zdroj, Skola
"""

import os
import json
import glob
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TENDERS_DIR, COMPANIES_DIR, PEOPLE_DIR, TRANSFORMED_DIR, NEO4J_SCHEMA

class Neo4jTransformer:
    """Transforms raw data into Neo4j node and relationship format matching Czech thesis schema."""
    
    def __init__(self):
        self.output_dir = TRANSFORMED_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        # Czech schema nodes
        self.nodes = {
            "Osoba": [],
            "Firma": [],
            "Zadavatel": [],
            "Zakazka": [],
            "Zdroj": [],
            "Skola": []
        }
        # Czech schema relationships
        self.relationships = {
            "VYKONAVA_FUNKCI": [],      # Osoba -> Firma
            "VLASTNI_PODIL": [],        # Osoba -> Firma
            "PODAVA_NABIDKU": [],       # Firma -> Zakazka
            "JE_PRIDELENA": [],         # Firma -> Zakazka
            "STUDOVAL_NA": [],          # Osoba -> Skola
            "POCHAZI_Z": [],            # Any -> Zdroj
            "VYHLASUJE_ZAKAZKU": []     # Zadavatel -> Zakazka
        }
        # Track entities by IČO to avoid duplicates
        self.firmy_by_ico = {}
        self.zadavatele_by_ico = {}
        # Track Zdroj nodes
        self.zdroje = {}
    
    def get_or_create_zdroj(self, zdroj_id: str, nazev: str, url: str = "", typ: str = "registr") -> str:
        """Vytvoří nebo vrátí Zdroj node."""
        if zdroj_id in self.zdroje:
            return zdroj_id
        
        zdroj_node = {
            "zdroj_id": zdroj_id,
            "nazev": nazev,
            "url": url,
            "typ": typ,
            "vydavatel": "MVČR" if "smlouvy" in zdroj_id.lower() else "",
            "licence": "otevrena-data",
            "datum_ziskani": datetime.now().isoformat()
        }
        
        zdroj_node = {k: v for k, v in zdroj_node.items() if v is not None and v != ""}
        self.nodes["Zdroj"].append(zdroj_node)
        self.zdroje[zdroj_id] = zdroj_node
        
        return zdroj_id
    
    def get_or_create_firma(self, firma_data: dict, zdroj_id: str) -> str:
        """
        Vytvoří nebo vrátí IČO Firma node (IČO je unique identifier).
        Schema: firma_id, ico, nazev, jurisdikce, stav_zaznamu
        Returns: ico value (for use in relationships)
        """
        ico = firma_data.get("ico")
        if not ico:
            # Fallback if no IČO
            name = firma_data.get("name", "Unknown")
            ico = f"NO_ICO_{name.replace(' ', '_').replace(',', '')[:20]}"
        
        # Pokud už existuje, vrátit IČO
        if ico in self.firmy_by_ico:
            # Link to Zdroj if not already linked
            if zdroj_id:
                rel = {
                    "from": ico,
                    "to": zdroj_id,
                    "datum_ziskani": datetime.now().isoformat()
                }
                self.relationships["POCHAZI_Z"].append(rel)
            return ico
        
        # Vytvořit nový Firma node
        node = {
            "firma_id": ico,
            "ico": ico,
            "nazev": firma_data.get("name", ""),
            "jurisdikce": "CZ",
            "stav_zaznamu": "overeny"  # Default for smlouvy.gov.cz data
        }
        
        # Clean None values
        node = {k: v for k, v in node.items() if v is not None and v != ""}
        
        self.nodes["Firma"].append(node)
        self.firmy_by_ico[ico] = node
        
        # Link to Zdroj
        if zdroj_id:
            rel = {
                "from": ico,
                "to": zdroj_id,
                "datum_ziskani": datetime.now().isoformat()
            }
            self.relationships["POCHAZI_Z"].append(rel)
        
        return ico
    
    def get_or_create_zadavatel(self, zadavatel_data: dict, zdroj_id: str) -> str:
        """
        Vytvoří nebo vrátí zadavatel_id Zadavatel node.
        Schema: zadavatel_id, ico, nazev, typ, uroven, jurisdikce, stav_zaznamu
        Returns: zadavatel_id value (for use in relationships)
        """
        ico = zadavatel_data.get("ico")
        name = zadavatel_data.get("name", "Unknown")
        
        # Use IČO as zadavatel_id if available, otherwise generate from name
        if ico:
            zadavatel_id = ico
        else:
            zadavatel_id = f"ZADAVATEL_{name.replace(' ', '_').replace(',', '')[:20]}"
        
        # Check if already exists
        if zadavatel_id in self.zadavatele_by_ico:
            # Link to Zdroj if not already linked
            if zdroj_id:
                rel = {
                    "from": zadavatel_id,
                    "to": zdroj_id,
                    "datum_ziskani": datetime.now().isoformat()
                }
                self.relationships["POCHAZI_Z"].append(rel)
            return zadavatel_id
        
        # Create Zadavatel node
        node = {
            "zadavatel_id": zadavatel_id,
            "ico": ico,
            "nazev": name,
            "typ": "ministerstvo",  # Default, could be enhanced with classification
            "uroven": "centralni",  # Default for smlouvy.gov.cz
            "jurisdikce": "CZ",
            "stav_zaznamu": "overeny"
        }
        
        # Clean None values
        node = {k: v for k, v in node.items() if v is not None and v != ""}
        self.nodes["Zadavatel"].append(node)
        self.zadavatele_by_ico[zadavatel_id] = node
        
        # Link to Zdroj
        if zdroj_id:
            rel = {
                "from": zadavatel_id,
                "to": zdroj_id,
                "datum_ziskani": datetime.now().isoformat()
            }
            self.relationships["POCHAZI_Z"].append(rel)
        
        return zadavatel_id
    
    def transform_all(self, filter_ico=None):
        """Transform all available data files."""
        print("Transforming data for Neo4j (Czech schema)...")
        
        # Create Zdroj for smlouvy.gov.cz
        zdroj_smlouvy = self.get_or_create_zdroj(
            "REGISTR_SMLUV",
            "Registr smluv",
            "https://smlouvy.gov.cz",
            "registr"
        )
        
        # Transform smlouvy.gov.cz contracts (from extracted directory)
        extracted_dir = Path(__file__).parent.parent / "data" / "tenders" / "extracted" / "smlouvy_gov"
        if extracted_dir.exists():
            contract_files = list(extracted_dir.glob("contracts_*.json"))
            for file in contract_files:
                if "transformed" not in str(file):
                    self.transform_smlouvy_contracts(str(file), zdroj_smlouvy, filter_ico=filter_ico)
        
        # Transform tenders (legacy format)
        tender_files = glob.glob(os.path.join(TENDERS_DIR, "*.json"))
        for file in tender_files:
            if "transformed" not in file and "extracted" not in file:
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
        
        # Save transformed data
        self.save_transformed_data()
        
        print(f"\nTransformation complete!")
        print(f"Nodes: {sum(len(v) for v in self.nodes.values())}")
        print(f"Relationships: {sum(len(v) for v in self.relationships.values())}")
    
    def transform_smlouvy_contracts(self, file_path, zdroj_id: str, filter_ico=None):
        """
        Transformuje smlouvy z smlouvy.gov.cz do Neo4j formátu.
        
        Czech schema:
        - Zadavatel nodes (authority)
        - Firma nodes (contractor)
        - Zakazka nodes (contracts)
        - Relationships: VYHLASUJE_ZAKAZKU (Zadavatel -> Zakazka), JE_PRIDELENA (Firma -> Zakazka)
        """
        print(f"Processing smlouvy.gov.cz contracts from {os.path.basename(file_path)}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            contracts = json.load(f)
        
        contracts_processed = 0
        
        for contract in contracts:
            # Filtrování podle IČO (pokud je zadáno)
            if filter_ico:
                authority_ico = contract.get("authority", {}).get("ico")
                contractor_ico = contract.get("contractor", {}).get("ico")
                if authority_ico != filter_ico and contractor_ico != filter_ico:
                    continue
            
            # Vytvořit Zakazka node
            contract_id = contract.get("contract_id", "")
            zakazka_id = contract_id if contract_id else f"ZAKAZKA-{contracts_processed}"
            
            # Určit hodnotu (preferovat s DPH, jinak bez DPH)
            value = contract.get("value_with_vat") or contract.get("value_without_vat")
            
            # Parse dates
            publication_date = contract.get("published_date", "")
            contract_date = contract.get("contract_date", "")
            
            # Extract year from date
            rok = None
            if contract_date:
                try:
                    rok = int(contract_date[:4])
                except:
                    pass
            if not rok and publication_date:
                try:
                    rok = int(publication_date[:4])
                except:
                    pass
            if not rok:
                rok = datetime.now().year
            
            zakazka_node = {
                "zakazka_id": zakazka_id,
                "nazev": contract.get("subject", ""),
                "stav_zaznamu": "overeny",
                "popis": contract.get("subject", ""),
                "stav": "ukoncena",  # Smlouvy v registru jsou dokončené
                "hodnota": value,
                "mena": "CZK",
                "rok": rok,
                "jurisdikce": "CZ",
                "externi_id": contract_id
            }
            
            # Clean None values
            zakazka_node = {k: v for k, v in zakazka_node.items() if v is not None and v != ""}
            self.nodes["Zakazka"].append(zakazka_node)
            
            # Link Zakazka to Zdroj
            rel_zdroj = {
                "from": zakazka_id,
                "to": zdroj_id,
                "datum_ziskani": datetime.now().isoformat()
            }
            self.relationships["POCHAZI_Z"].append(rel_zdroj)
            
            # Vytvořit Zadavatel node (authority)
            authority = contract.get("authority", {})
            zadavatel_id = None
            if authority.get("ico") or authority.get("name"):
                zadavatel_id = self.get_or_create_zadavatel(authority, zdroj_id)
            
            # Vytvořit Firma node (contractor)
            contractor = contract.get("contractor", {})
            firma_id = None
            if contractor.get("ico") or contractor.get("name"):
                firma_id = self.get_or_create_firma(contractor, zdroj_id)
            
            # Vytvořit relationships
            if zadavatel_id and zakazka_id:
                # Zadavatel VYHLASUJE_ZAKAZKU
                rel = {
                    "from": zadavatel_id,
                    "to": zakazka_id,
                    "datum_vyhlaseni": publication_date or contract_date,
                    "zdroj_id": zdroj_id
                }
                rel = {k: v for k, v in rel.items() if v is not None and v != ""}
                self.relationships["VYHLASUJE_ZAKAZKU"].append(rel)
            
            if firma_id and zakazka_id:
                # Firma JE_PRIDELENA (won the contract)
                # Note: smlouvy.gov.cz contains only awarded contracts, not bids
                # PODAVA_NABIDKU would come from other sources (VVZ, NEN, etc.)
                rel = {
                    "from": firma_id,
                    "to": zakazka_id,
                    "smlouva_id": contract_id,
                    "platnost_od": contract_date,
                    "platnost_do": None,  # Not available
                    "hodnota": value,
                    "mena": "CZK",
                    "zdroj_id": zdroj_id
                }
                rel = {k: v for k, v in rel.items() if v is not None and v != ""}
                self.relationships["JE_PRIDELENA"].append(rel)
                
                # Note: PODAVA_NABIDKU would be created from bid data (not available in smlouvy.gov.cz)
                # Example structure when bid data is available:
                # rel_bid = {
                #     "from": firma_id,
                #     "to": zakazka_id,
                #     "datum_podani": bid_date,
                #     "nabidkova_cena": bid_value,
                #     "mena": "CZK",
                #     "zdroj_id": "VVZ" or "NEN"
                # }
                # self.relationships["PODAVA_NABIDKU"].append(rel_bid)
            
            contracts_processed += 1
        
        print(f"  Processed {contracts_processed} contracts")
    
    def transform_tenders(self, file_path):
        """Transform tender data into Zakazka nodes (legacy format)."""
        print(f"Processing tenders from {os.path.basename(file_path)}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            tenders = json.load(f)
        
        for tender in tenders:
            node = {
                "zakazka_id": tender.get("id", f"ZAKAZKA-{len(self.nodes['Zakazka'])}"),
                "nazev": tender.get("title", ""),
                "stav_zaznamu": "overeny",
                "popis": tender.get("description", ""),
                "stav": tender.get("status", "ukoncena"),
                "hodnota": tender.get("value"),
                "mena": tender.get("currency", "CZK"),
                "rok": tender.get("year") or datetime.now().year,
                "jurisdikce": tender.get("country", "CZ"),
                "externi_id": tender.get("external_id", "")
            }
            
            # Clean None values
            node = {k: v for k, v in node.items() if v is not None and v != ""}
            self.nodes["Zakazka"].append(node)
    
    def transform_companies(self, file_path):
        """Transform company data into Firma nodes (legacy format)."""
        print(f"Processing companies from {os.path.basename(file_path)}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            companies = json.load(f)
        
        for company in companies:
            ico = company.get("ico") or company.get("registration_number", "")
            firma_id = f"FIRMA-{ico}" if ico else f"FIRMA-{len(self.nodes['Firma'])}"
            
            node = {
                "firma_id": ico or firma_id.replace("FIRMA-", ""),
                "ico": ico,
                "nazev": company.get("name", ""),
                "jurisdikce": company.get("country") or company.get("jurisdiction", "CZ"),
                "stav_zaznamu": "overeny"
            }
            
            # Clean None values
            node = {k: v for k, v in node.items() if v is not None and v != ""}
            self.nodes["Firma"].append(node)
    
    def transform_people(self, file_path):
        """Transform people data into Osoba nodes and relationships (legacy format)."""
        print(f"Processing people from {os.path.basename(file_path)}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            people = json.load(f)
        
        for person in people:
            osoba_id = person.get("id", f"OSOBA-{len(self.nodes['Osoba'])}")
            
            # Parse name
            full_name = person.get("name", "")
            name_parts = full_name.split(" ", 1)
            jmeno = name_parts[0] if name_parts else ""
            prijmeni = name_parts[1] if len(name_parts) > 1 else ""
            
            node = {
                "osoba_id": osoba_id,
                "cele_jmeno": full_name,
                "jmeno": jmeno,
                "prijmeni": prijmeni,
                "datum_narozeni": person.get("birth_date"),
                "statni_prislusnost": person.get("nationality", "CZ"),
                "stav_zaznamu": "overeny"
            }
            
            # Clean None values
            node = {k: v for k, v in node.items() if v is not None and v != ""}
            self.nodes["Osoba"].append(node)
            
            # Create VYKONAVA_FUNKCI relationship if company_id exists
            company_id = person.get("company_id")
            if company_id:
                rel = {
                    "from": osoba_id,
                    "to": company_id,
                    "role": person.get("role", ""),
                    "platnost_od": person.get("start_date", ""),
                    "platnost_do": person.get("end_date", ""),
                    "zdroj_id": person.get("source", "unknown")
                }
                
                # Clean None values
                rel = {k: v for k, v in rel.items() if v is not None and v != ""}
                self.relationships["VYKONAVA_FUNKCI"].append(rel)
    
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
    import argparse
    
    parser = argparse.ArgumentParser(description="Transform data to Neo4j format (Czech schema)")
    parser.add_argument("--ico", type=str, help="Filter by IČO")
    args = parser.parse_args()
    
    transformer = Neo4jTransformer()
    transformer.transform_all(filter_ico=args.ico)
