"""
Clean up English entities (Company, Organization, Person, Tender) from Neo4j.
Keep only Czech schema entities.
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
    print("CLEANING UP ENGLISH ENTITIES")
    print("=" * 70)
    
    with loader.driver.session() as session:
        # Delete English entity nodes
        english_labels = ["Company", "Organization", "Person", "Tender"]
        
        for label in english_labels:
            result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
            count = result.single()["count"]
            if count > 0:
                print(f"\nDeleting {count} {label} nodes...")
                session.run(f"MATCH (n:{label}) DETACH DELETE n")
                print(f"  ✓ Deleted {count} {label} nodes")
            else:
                print(f"  No {label} nodes found")
        
        # Delete English relationship types (if any exist)
        english_rels = ["SUBMITTED_BID", "WON", "WORKS_FOR", "DIRECTS", "PUBLISHED", 
                       "CONTRACTED_WITH", "PUBLISHED_CONTRACT", "WON_CONTRACT"]
        
        print("\nChecking for English relationships...")
        for rel_type in english_rels:
            result = session.run(f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as count")
            count = result.single()["count"]
            if count > 0:
                print(f"  Deleting {count} {rel_type} relationships...")
                session.run(f"MATCH ()-[r:{rel_type}]->() DELETE r")
                print(f"    ✓ Deleted {count} {rel_type} relationships")
        
        # Drop old English constraints
        print("\nDropping old English constraints...")
        old_constraints = [
            "company_id",
            "person_id", 
            "org_id",
            "tender_id"
        ]
        
        for constraint_name in old_constraints:
            try:
                # Try to drop constraint (syntax varies by Neo4j version)
                session.run(f"DROP CONSTRAINT {constraint_name} IF EXISTS")
                print(f"  ✓ Dropped constraint: {constraint_name}")
            except Exception as e:
                # Try alternative syntax
                try:
                    session.run(f"DROP CONSTRAINT {constraint_name}")
                    print(f"  ✓ Dropped constraint: {constraint_name}")
                except:
                    print(f"  Note: Could not drop {constraint_name} (may not exist)")
        
        # Show remaining schema
        print("\n" + "=" * 70)
        print("REMAINING SCHEMA:")
        print("=" * 70)
        
        result = session.run("CALL db.labels()")
        labels = [record["label"] for record in result]
        print("\nNode Labels:")
        for label in sorted(labels):
            count_result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
            count = count_result.single()["count"]
            if count > 0:
                print(f"  • {label}: {count} nodes")
        
        result = session.run("CALL db.relationshipTypes()")
        rel_types = [record["relationshipType"] for record in result]
        print("\nRelationship Types:")
        for rel_type in sorted(rel_types):
            count_result = session.run(f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as count")
            count = count_result.single()["count"]
            if count > 0:
                print(f"  • {rel_type}: {count} relationships")
    
    print("\n" + "=" * 70)
    print("✓ Cleanup complete!")
    print("=" * 70)
    
    loader.close()
    
except ImportError as e:
    print(f"Error: {e}")
    print("Make sure neo4j driver is installed: pip install neo4j")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

