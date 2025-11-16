"""
Remove old English indexes from Neo4j.
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
    print("CLEANING UP OLD INDEXES")
    print("=" * 70)
    
    with loader.driver.session() as session:
        # Get all indexes
        result = session.run("SHOW INDEXES")
        indexes = list(result)
        
        # Old English indexes to remove
        old_indexes = ["company_id", "person_id", "org_id", "tender_id"]
        
        print("\nRemoving old indexes...")
        for index_record in indexes:
            index_name = index_record.get("name", "")
            if index_name in old_indexes:
                try:
                    session.run(f"DROP INDEX {index_name} IF EXISTS")
                    print(f"  ✓ Dropped index: {index_name}")
                except Exception as e:
                    print(f"  Note: Could not drop {index_name}: {e}")
        
        # Show remaining indexes
        print("\nRemaining indexes:")
        result = session.run("SHOW INDEXES")
        for record in result:
            index_name = record.get("name", "")
            index_type = record.get("type", "")
            if index_type != "LOOKUP" and index_name not in old_indexes:
                print(f"  • {index_name} ({index_type})")
    
    print("\n" + "=" * 70)
    print("✓ Index cleanup complete!")
    print("=" * 70)
    
    loader.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

