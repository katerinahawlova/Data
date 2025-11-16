"""
Test Czech schema in Neo4j - verify relationships work correctly.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from scripts.load_to_neo4j import Neo4jLoader
    from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
    
    loader = Neo4jLoader()
    
    if not loader.connect():
        print("Failed to connect to Neo4j")
        exit(1)
    
    print("=" * 70)
    print("TESTING CZECH SCHEMA")
    print("=" * 70)
    
    with loader.driver.session() as session:
        # Test 1: Zadavatel -> Zakazka
        print("\n1. Zadavatel VYHLASUJE_ZAKAZKU:")
        print("-" * 70)
        result = session.run("""
            MATCH (z:Zadavatel)-[r:VYHLASUJE_ZAKAZKU]->(zak:Zakazka)
            RETURN z.nazev as zadavatel, zak.nazev as zakazka, r.datum_vyhlaseni as datum
            LIMIT 5
        """)
        for record in result:
            print(f"  {record['zadavatel']} -> {record['zakazka'][:50]}... ({record['datum']})")
        
        # Test 2: Firma -> Zakazka (JE_PRIDELENA)
        print("\n2. Firma JE_PRIDELENA:")
        print("-" * 70)
        result = session.run("""
            MATCH (f:Firma)-[r:JE_PRIDELENA]->(zak:Zakazka)
            RETURN f.nazev as firma, zak.nazev as zakazka, r.hodnota as hodnota
            LIMIT 5
        """)
        for record in result:
            hodnota = record['hodnota']
            if hodnota:
                hodnota_str = f"{hodnota:,.0f} CZK"
            else:
                hodnota_str = "N/A"
            print(f"  {record['firma']} -> {record['zakazka'][:50]}... ({hodnota_str})")
        
        # Test 3: POCHAZI_Z relationships
        print("\n3. POCHAZI_Z (data source tracking):")
        print("-" * 70)
        result = session.run("""
            MATCH (n)-[r:POCHAZI_Z]->(zd:Zdroj)
            WITH labels(n) as node_labels, zd.nazev as zdroj, count(*) as count
            RETURN node_labels[0] as node_type, zdroj, count
            ORDER BY count DESC
        """)
        for record in result:
            print(f"  {record['node_type']} -> {record['zdroj']}: {record['count']} relationships")
        
        # Test 4: Count summary
        print("\n4. Summary:")
        print("-" * 70)
        result = session.run("""
            MATCH (n)
            WITH labels(n)[0] as label, count(*) as count
            RETURN label, count
            ORDER BY count DESC
        """)
        for record in result:
            print(f"  {record['label']}: {record['count']} nodes")
        
        result = session.run("""
            MATCH ()-[r]->()
            WITH type(r) as rel_type, count(*) as count
            RETURN rel_type, count
            ORDER BY count DESC
        """)
        for record in result:
            print(f"  {record['rel_type']}: {record['count']} relationships")
    
    print("\n" + "=" * 70)
    print("✓ Schema test complete!")
    print("=" * 70)
    
    loader.close()
    
except ImportError as e:
    print(f"Error: {e}")
    print("Make sure neo4j driver is installed: pip install neo4j")
except Exception as e:
    print(f"Error: {e}")

