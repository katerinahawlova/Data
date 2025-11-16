"""
Check which relationships are defined in the user's Cypher code vs what's implemented.
"""

print("=" * 70)
print("RELATIONSHIPS FROM USER'S CYPHER CODE:")
print("=" * 70)

cypher_relationships = [
    "VYKONAVA_FUNKCI",      # (Osoba) -> (Firma)
    "VLASTNI_PODIL",        # (Osoba) -> (Firma)
    "PODAVA_NABIDKU",       # (Firma) -> (Zakazka)
    "JE_PRIDELENA",         # (Firma) -> (Zakazka)
    "STUDOVAL_NA",          # (Osoba) -> (Skola)
    "POCHAZI_Z",            # (Any) -> (Zdroj)
    "VYHLASUJE_ZAKAZKU"     # (Zadavatel) -> (Zakazka)
]

print("\nFrom Cypher code:")
for i, rel in enumerate(cypher_relationships, 1):
    print(f"  {i}. {rel}")

print("\n" + "=" * 70)
print("RELATIONSHIPS IN TRANSFORM SCRIPT:")
print("=" * 70)

# Read transform script
with open("scripts/transform_to_neo4j.py", "r", encoding="utf-8") as f:
    content = f.read()
    
    # Find relationships definition
    if 'self.relationships = {' in content:
        start = content.find('self.relationships = {')
        end = content.find('}', start) + 1
        rels_section = content[start:end]
        
        print("\nIn transform_to_neo4j.py:")
        for rel in cypher_relationships:
            if f'"{rel}"' in rels_section or f"'{rel}'" in rels_section:
                print(f"  ✓ {rel}")
            else:
                print(f"  ✗ {rel} - MISSING!")

print("\n" + "=" * 70)
print("RELATIONSHIPS IN LOAD SCRIPT:")
print("=" * 70)

# Read load script
with open("scripts/load_to_neo4j.py", "r", encoding="utf-8") as f:
    content = f.read()
    
    print("\nIn load_to_neo4j.py:")
    for rel in cypher_relationships:
        if f'rel_type == "{rel}"' in content:
            print(f"  ✓ {rel}")
        else:
            print(f"  ✗ {rel} - MISSING!")

print("\n" + "=" * 70)

