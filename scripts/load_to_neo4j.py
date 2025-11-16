"""
Load transformed data into Neo4j graph database.
Matches Czech schema: Osoba, Firma, Zadavatel, Zakazka, Zdroj, Skola
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
    """Loads data into Neo4j graph database using Czech schema."""
    
    def __init__(self, uri=None, user=None, password=None):
        self.uri = uri or NEO4J_URI
        self.user = user or NEO4J_USER
        self.password = password or NEO4J_PASSWORD
        self.driver = None
        
        # Map node types to their unique ID field names (Czech schema)
        self.node_id_fields = {
            "Osoba": "osoba_id",
            "Firma": "ico",  # IČO is unique
            "Zadavatel": "zadavatel_id",
            "Zakazka": "zakazka_id",
            "Zdroj": "zdroj_id",
            "Skola": "skola_id"
        }
        
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
        """Create unique constraints and indexes matching Czech schema."""
        constraints = [
            # Unique constraints
            "CREATE CONSTRAINT osoba_id_unique IF NOT EXISTS FOR (o:Osoba) REQUIRE o.osoba_id IS UNIQUE",
            "CREATE CONSTRAINT firma_ico_unique IF NOT EXISTS FOR (f:Firma) REQUIRE f.ico IS UNIQUE",
            "CREATE CONSTRAINT zadavatel_id_unique IF NOT EXISTS FOR (z:Zadavatel) REQUIRE z.zadavatel_id IS UNIQUE",
            "CREATE CONSTRAINT zakazka_id_unique IF NOT EXISTS FOR (z:Zakazka) REQUIRE z.zakazka_id IS UNIQUE",
            "CREATE CONSTRAINT skola_id_unique IF NOT EXISTS FOR (s:Skola) REQUIRE s.skola_id IS UNIQUE",
            "CREATE CONSTRAINT zdroj_id_unique IF NOT EXISTS FOR (zd:Zdroj) REQUIRE zd.zdroj_id IS UNIQUE",
            
            # Indexes for searching
            "CREATE INDEX osoba_jmeno_index IF NOT EXISTS FOR (o:Osoba) ON (o.prijmeni, o.datum_narozeni)",
            "CREATE INDEX firma_nazev_index IF NOT EXISTS FOR (f:Firma) ON (f.nazev)",
            "CREATE INDEX zakazka_rok_index IF NOT EXISTS FOR (z:Zakazka) ON (z.rok)",
            "CREATE INDEX zadavatel_nazev_index IF NOT EXISTS FOR (z:Zadavatel) ON (z.nazev)",
            "CREATE INDEX skola_nazev_mesto_index IF NOT EXISTS FOR (s:Skola) ON (s.nazev, s.mesto)",
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
        """Load nodes of a specific type into Neo4j using Czech schema ID fields."""
        if not nodes:
            return 0
        
        # Get the unique ID field for this node type
        id_field = self.node_id_fields.get(node_type, "id")
        
        # Build MERGE query based on ID field
        if id_field == "ico":  # Special case for Firma - use IČO
            query = f"""
            UNWIND $nodes AS node
            MERGE (n:{node_type} {{ico: node.ico}})
            SET n += node
            RETURN count(n) as count
            """
        else:
            query = f"""
            UNWIND $nodes AS node
            MERGE (n:{node_type} {{{id_field}: node.{id_field}}})
            SET n += node
            RETURN count(n) as count
            """
        
        with self.driver.session() as session:
            result = session.run(query, nodes=nodes)
            count = result.single()["count"]
            return count
    
    def load_relationships(self, rel_type, relationships):
        """Load relationships of a specific type into Neo4j using Czech schema."""
        if not relationships:
            return 0
        
        # Map relationship types to node types (Czech schema)
        # Default: assume from/to are IDs that need to be matched
        # We need to determine node types from the relationship
        
        # Determine node types based on relationship type
        from_type = None
        to_type = None
        from_id_field = "id"
        to_id_field = "id"
        
        if rel_type == "VYKONAVA_FUNKCI" or rel_type == "VLASTNI_PODIL":
            from_type = "Osoba"
            to_type = "Firma"
            from_id_field = "osoba_id"
            to_id_field = "ico"  # Firma uses IČO
        elif rel_type == "PODAVA_NABIDKU" or rel_type == "JE_PRIDELENA":
            from_type = "Firma"
            to_type = "Zakazka"
            from_id_field = "ico"  # Firma uses IČO
            to_id_field = "zakazka_id"
        elif rel_type == "STUDOVAL_NA":
            from_type = "Osoba"
            to_type = "Skola"
            from_id_field = "osoba_id"
            to_id_field = "skola_id"
        elif rel_type == "POCHAZI_Z":
            # This can link any node type to Zdroj
            # We'll need to try matching from different node types
            from_type = None  # Will be determined dynamically
            to_type = "Zdroj"
            to_id_field = "zdroj_id"
        elif rel_type == "VYHLASUJE_ZAKAZKU":
            from_type = "Zadavatel"
            to_type = "Zakazka"
            from_id_field = "zadavatel_id"
            to_id_field = "zakazka_id"
        else:
            # Fallback: try to match by common patterns
            from_type = "Firma"
            to_type = "Zakazka"
            from_id_field = "ico"
            to_id_field = "zakazka_id"
        
        if from_type is None:
            # For POCHAZI_Z, try to match from different node types
            # This is a simplified approach - in production you might want more sophisticated matching
            node_types_to_try = ["Osoba", "Firma", "Zadavatel", "Zakazka", "Skola"]
            total_count = 0
            
            for try_from_type in node_types_to_try:
                try_from_id = self.node_id_fields.get(try_from_type, "id")
                if try_from_id == "ico":
                    query = f"""
                    UNWIND $rels AS rel
                    MATCH (from:{try_from_type} {{ico: rel.from}})
                    MATCH (to:{to_type} {{{to_id_field}: rel.to}})
                    MERGE (from)-[r:{rel_type}]->(to)
                    SET r += rel
                    RETURN count(r) as count
                    """
                else:
                    query = f"""
                    UNWIND $rels AS rel
                    MATCH (from:{try_from_type} {{{try_from_id}: rel.from}})
                    MATCH (to:{to_type} {{{to_id_field}: rel.to}})
                    MERGE (from)-[r:{rel_type}]->(to)
                    SET r += rel
                    RETURN count(r) as count
                    """
                
                with self.driver.session() as session:
                    try:
                        result = session.run(query, rels=relationships)
                        count = result.single()["count"]
                        total_count += count
                    except:
                        pass  # Node type doesn't match, try next
            
            return total_count
        else:
            # Standard relationship loading
            if from_id_field == "ico":
                if to_id_field == "ico":
                    query = f"""
                    UNWIND $rels AS rel
                    MATCH (from:{from_type} {{ico: rel.from}})
                    MATCH (to:{to_type} {{ico: rel.to}})
                    MERGE (from)-[r:{rel_type}]->(to)
                    SET r += rel
                    RETURN count(r) as count
                    """
                else:
                    query = f"""
                    UNWIND $rels AS rel
                    MATCH (from:{from_type} {{ico: rel.from}})
                    MATCH (to:{to_type} {{{to_id_field}: rel.to}})
                    MERGE (from)-[r:{rel_type}]->(to)
                    SET r += rel
                    RETURN count(r) as count
                    """
            else:
                if to_id_field == "ico":
                    query = f"""
                    UNWIND $rels AS rel
                    MATCH (from:{from_type} {{{from_id_field}: rel.from}})
                    MATCH (to:{to_type} {{ico: rel.to}})
                    MERGE (from)-[r:{rel_type}]->(to)
                    SET r += rel
                    RETURN count(r) as count
                    """
                else:
                    query = f"""
                    UNWIND $rels AS rel
                    MATCH (from:{from_type} {{{from_id_field}: rel.from}})
                    MATCH (to:{to_type} {{{to_id_field}: rel.to}})
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
    
    parser = argparse.ArgumentParser(description="Load data into Neo4j (Czech schema)")
    parser.add_argument("--clear", action="store_true", help="Clear database before loading")
    args = parser.parse_args()
    
    loader = Neo4jLoader()
    loader.load_all(clear_first=args.clear)
