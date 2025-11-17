"""
Aktualizuje názvy firem v Neo4j z dat smlouvy.

Použije se pro doplnění názvů firem, které máme v databázi pouze s IČO.
"""

import json
from pathlib import Path
from typing import Dict
import sys

# Přidat parent directory do path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from neo4j import GraphDatabase
    from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
except ImportError:
    print("❌ Neo4j driver není nainstalován. Spusť: pip install neo4j")
    sys.exit(1)


def get_firma_names_from_contracts() -> Dict[str, str]:
    """
    Získá názvy firem z dat smlouvy.
    
    Returns:
        Dict[ico, nazev]
    """
    firma_names = {}
    
    extracted_dir = Path(__file__).parent.parent / "data" / "tenders" / "extracted" / "smlouvy_gov"
    
    if not extracted_dir.exists():
        print(f"[update_firma_names] Adresář neexistuje: {extracted_dir}")
        return firma_names
    
    for json_file in extracted_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                contracts = json.load(f)
            
            for contract in contracts:
                # Zadavatel (může být objekt nebo přímo ico/name)
                if isinstance(contract.get('authority'), dict):
                    zadavatel_ico = contract.get('authority', {}).get('ico')
                    zadavatel_name = contract.get('authority', {}).get('name', '')
                else:
                    zadavatel_ico = contract.get('authority_ico')
                    zadavatel_name = contract.get('authority_name', '')
                
                if zadavatel_ico and zadavatel_name:
                    if zadavatel_ico not in firma_names or not firma_names[zadavatel_ico]:
                        firma_names[zadavatel_ico] = zadavatel_name
                
                # Dodavatel (může být objekt nebo přímo ico/name)
                if isinstance(contract.get('contractor'), dict):
                    contractor_ico = contract.get('contractor', {}).get('ico')
                    contractor_name = contract.get('contractor', {}).get('name', '')
                else:
                    contractor_ico = contract.get('contractor_ico')
                    contractor_name = contract.get('contractor_name', '')
                
                if contractor_ico and contractor_name:
                    if contractor_ico not in firma_names or not firma_names[contractor_ico]:
                        firma_names[contractor_ico] = contractor_name
        
        except Exception as e:
            print(f"[update_firma_names] Chyba při zpracování {json_file.name}: {e}")
            continue
    
    print(f"[update_firma_names] Nalezeno {len(firma_names)} firem s názvy")
    return firma_names


def update_neo4j_firma_names(firma_names: Dict[str, str]):
    """
    Aktualizuje názvy firem v Neo4j.
    """
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    try:
        with driver.session() as session:
            updated_count = 0
            
            for ico, nazev in firma_names.items():
                if not ico or not nazev:
                    continue
                
                # Aktualizovat název firmy
                result = session.run(
                    """
                    MATCH (f:Firma {ico: $ico})
                    WHERE f.nazev IS NULL OR f.nazev = ''
                    SET f.nazev = $nazev
                    RETURN f
                    """,
                    ico=ico,
                    nazev=nazev
                )
                
                if result.single():
                    updated_count += 1
            
            print(f"[update_firma_names] Aktualizováno {updated_count} firem")
    
    finally:
        driver.close()


if __name__ == "__main__":
    print("[update_firma_names] Získávám názvy firem z dat smlouvy...")
    firma_names = get_firma_names_from_contracts()
    
    if not firma_names:
        print("❌ Nebyly nalezeny žádné názvy firem")
        sys.exit(1)
    
    print(f"[update_firma_names] Aktualizuji Neo4j...")
    update_neo4j_firma_names(firma_names)
    
    print("✓ Hotovo!")

