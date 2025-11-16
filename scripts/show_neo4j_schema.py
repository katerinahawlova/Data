"""
Show current Neo4j schema - nodes, relationships, and properties.
Helps compare with thesis schema definition.
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
    print("CURRENT NEO4J SCHEMA")
    print("=" * 70)
    
    with loader.driver.session() as session:
        # Get all node labels
        print("\n📊 NODE LABELS:")
        print("-" * 70)
        result = session.run("CALL db.labels()")
        labels = [record["label"] for record in result]
        for label in sorted(labels):
            # Count nodes
            count_result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
            count = count_result.single()["count"]
            print(f"  • {label}: {count} nodes")
            
            # Get sample properties
            sample_result = session.run(f"MATCH (n:{label}) RETURN keys(n) as keys LIMIT 1")
            sample = sample_result.single()
            if sample and sample["keys"]:
                props = ", ".join(sorted(sample["keys"]))
                print(f"    Properties: {props}")
        
        # Get all relationship types
        print("\n🔗 RELATIONSHIP TYPES:")
        print("-" * 70)
        result = session.run("CALL db.relationshipTypes()")
        rel_types = [record["relationshipType"] for record in result]
        for rel_type in sorted(rel_types):
            # Count relationships
            count_result = session.run(f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as count")
            count = count_result.single()["count"]
            print(f"  • {rel_type}: {count} relationships")
            
            # Get sample properties
            sample_result = session.run(f"MATCH ()-[r:{rel_type}]->() RETURN keys(r) as keys LIMIT 1")
            sample = sample_result.single()
            if sample and sample["keys"]:
                props = ", ".join(sorted(sample["keys"]))
                print(f"    Properties: {props}")
        
        # Get constraints
        print("\n🔒 CONSTRAINTS & INDEXES:")
        print("-" * 70)
        result = session.run("SHOW CONSTRAINTS")
        constraints = list(result)
        if constraints:
            for record in constraints:
                print(f"  • {record.get('name', 'N/A')}: {record.get('type', 'N/A')}")
        else:
            print("  (No constraints found)")
        
        result = session.run("SHOW INDEXES")
        indexes = list(result)
        if indexes:
            for record in indexes:
                if record.get('type') != 'LOOKUP':
                    print(f"  • Index: {record.get('name', 'N/A')}")
    
    print("\n" + "=" * 70)
    print("To view in Neo4j Browser, run:")
    print("  CALL db.schema.visualization()")
    print("=" * 70)
    
    loader.close()
    
except ImportError as e:
    print(f"Error: {e}")
    print("Make sure neo4j driver is installed: pip install neo4j")
except Exception as e:
    print(f"Error: {e}")

