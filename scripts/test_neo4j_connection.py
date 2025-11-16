"""
Test Neo4j connection script.
Use this to verify your Neo4j database is accessible.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from scripts.load_to_neo4j import Neo4jLoader
    from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
    
    print("Testing Neo4j connection...")
    print(f"URI: {NEO4J_URI}")
    print(f"User: {NEO4J_USER}")
    print(f"Password: {'*' * len(NEO4J_PASSWORD) if NEO4J_PASSWORD else '(not set)'}")
    print()
    
    loader = Neo4jLoader()
    
    if loader.connect():
        print("✓ Successfully connected to Neo4j!")
        
        # Test query
        with loader.driver.session() as session:
            result = session.run("RETURN 'Hello from Neo4j!' as message")
            message = result.single()["message"]
            print(f"✓ Test query successful: {message}")
            
            # Check database info (try different methods for different Neo4j versions)
            try:
                result = session.run("CALL dbms.components() YIELD name, versions")
                info = result.single()
                if info:
                    print(f"✓ Neo4j component: {info.get('name', 'unknown')}")
                    version = info.get('versions', ['unknown'])[0] if info.get('versions') else 'unknown'
                    print(f"✓ Version: {version}")
            except:
                # Fallback for older versions
                result = session.run("RETURN 1 as test")
                print("✓ Database connection verified")
        
        loader.close()
        print("\n✓ Connection test passed! Your Neo4j is ready to use.")
    else:
        print("✗ Failed to connect to Neo4j")
        print("\nTroubleshooting:")
        print("1. Make sure Neo4j Desktop is running")
        print("2. Make sure your database is started (green status)")
        print("3. Check your password in .env file")
        print("4. Verify URI is correct (usually bolt://localhost:7687)")
        
except ImportError as e:
    print(f"✗ Error: {e}")
    print("Make sure neo4j driver is installed: pip install neo4j")
except Exception as e:
    print(f"✗ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure Neo4j Desktop is running")
    print("2. Make sure your database is started")
    print("3. Check your password in .env file")

