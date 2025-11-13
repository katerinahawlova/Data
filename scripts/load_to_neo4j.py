"""
Load transformed data into Neo4j graph database.
Creates nodes and relationships based on transformed JSON files.
"""

import os
import json
import glob
from neo4j import GraphDatabase
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TRANSFORMED_DIR, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

class Neo4jLoader:
    """Loads data into Neo4j graph database."""
    
    def __init__(self, uri=None, user=None, password=None):
        self.uri = uri or NEO4J_URI
        self.user = user or NEO4J_USER
        self.password = password or NEO4J_PASSWORD
        self.driver = None
        
    def connect(self):
        """Establish connection to Neo4j."""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Verify connection
            self.driver.verify_connectivity()
            print(f"Connected to Neo4j at {self.uri}")
            return True
        except Exception as e:
            print(f"Error connecting to Neo4j: {e}")
            print("\nMake sure Neo4j is running and credentials are correct in config.py or .env file")
            return False
    
    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()
            print("Disconnected from Neo4j")
    
    def clear_database(self, confirm=False):
        """Clear all nodes and relationships from the database."""
        if not confirm:
            print("Warning: This will delete all data. Set confirm=True to proceed.")
            return
        
        with self.driver.session() as session:
            result = session.run("MATCH (n) DETACH DELETE n")
            print("Database cleared")
    
    def create_constraints(self):
        """Create unique constraints and indexes for better performance."""
        constraints = [
            "CREATE CONSTRAINT tender_id IF NOT EXISTS FOR (t:Tender) REQUIRE t.id IS UNIQUE",
            "CREATE CONSTRAINT company_id IF NOT EXISTS FOR (c:Company) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT org_id IF NOT EXISTS FOR (o:Organization) REQUIRE o.id IS UNIQUE",
        ]
        
        with self.driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                    print(f"Created constraint/index")
                except Exception as e:
                    # Constraint might already exist
                    if "already exists" not in str(e).lower():
                        print(f"Note: {e}")
    
    def load_nodes(self, node_type, nodes):
        """Load nodes of a specific type into Neo4j."""
        if not nodes:
            return 0
        
        query = f"""
        UNWIND $nodes AS node
        MERGE (n:{node_type} {{id: node.id}})
        SET n += node
        RETURN count(n) as count
        """
        
        with self.driver.session() as session:
            result = session.run(query, nodes=nodes)
            count = result.single()["count"]
            return count
    
    def load_relationships(self, rel_type, relationships):
        """Load relationships of a specific type into Neo4j."""
        if not relationships:
            return 0
        
        # Determine node types from relationship direction
        # This is a simplified version - you may need to adjust based on your schema
        from_type = "Company"  # Default, adjust as needed
        to_type = "Tender"     # Default, adjust as needed
        
        if rel_type == "WORKS_FOR" or rel_type == "DIRECTS":
            from_type = "Person"
            to_type = "Company"
        elif rel_type == "SUBMITTED_BID" or rel_type == "WON":
            from_type = "Company"
            to_type = "Tender"
        elif rel_type == "PUBLISHED":
            from_type = "Organization"
            to_type = "Tender"
        
        query = f"""
        UNWIND $rels AS rel
        MATCH (from:{from_type} {{id: rel.from}})
        MATCH (to:{to_type} {{id: rel.to}})
        MERGE (from)-[r:{rel_type}]->(to)
        SET r += rel
        RETURN count(r) as count
        """
        
        with self.driver.session() as session:
            result = session.run(query, rels=relationships)
            count = result.single()["count"]
            return count
    
    def load_from_file(self, file_path):
        """Load data from a transformed JSON file."""
        print(f"\nLoading data from {os.path.basename(file_path)}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        total_nodes = 0
        total_rels = 0
        
        # Load nodes
        if "nodes" in data:
            for node_type, nodes in data["nodes"].items():
                if nodes:
                    count = self.load_nodes(node_type, nodes)
                    total_nodes += count
                    print(f"  Loaded {count} {node_type} nodes")
        
        # Load relationships
        if "relationships" in data:
            for rel_type, rels in data["relationships"].items():
                if rels:
                    count = self.load_relationships(rel_type, rels)
                    total_rels += count
                    print(f"  Loaded {count} {rel_type} relationships")
        
        return total_nodes, total_rels
    
    def load_all(self, clear_first=False):
        """Load all transformed data files."""
        if not self.connect():
            return
        
        try:
            # Create constraints
            self.create_constraints()
            
            # Clear database if requested
            if clear_first:
                self.clear_database(confirm=True)
            
            # Find all transformed data files
            data_files = glob.glob(os.path.join(TRANSFORMED_DIR, "neo4j_data_*.json"))
            
            if not data_files:
                print(f"No transformed data files found in {TRANSFORMED_DIR}")
                print("Run transform_to_neo4j.py first to create transformed data files.")
                return
            
            # Load most recent file
            latest_file = max(data_files, key=os.path.getctime)
            print(f"Loading from: {os.path.basename(latest_file)}")
            
            total_nodes, total_rels = self.load_from_file(latest_file)
            
            print(f"\n✓ Load complete!")
            print(f"  Total nodes: {total_nodes}")
            print(f"  Total relationships: {total_rels}")
            
        finally:
            self.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Load data into Neo4j")
    parser.add_argument("--clear", action="store_true", help="Clear database before loading")
    args = parser.parse_args()
    
    loader = Neo4jLoader()
    loader.load_all(clear_first=args.clear)

