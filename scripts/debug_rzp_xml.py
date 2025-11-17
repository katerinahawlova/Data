"""Debug script to inspect RZP XML structure"""
import xml.etree.ElementTree as ET
from pathlib import Path

xml_file = Path("data/people/raw/rzp/rzp_ico_47114983.xml")
tree = ET.parse(xml_file)
root = tree.getroot()

ns = "{urn:cz:isvs:rzp:schemas:VerejnaCast:v1}"

def print_tree(elem, indent=0):
    """Recursively print XML tree"""
    prefix = "  " * indent
    tag = elem.tag.replace(ns, "")
    text = elem.text.strip() if elem.text and elem.text.strip() else ""
    attrs = " ".join([f'{k}="{v}"' for k, v in elem.attrib.items()])
    
    if text:
        print(f"{prefix}<{tag} {attrs}>{text}</{tag}>")
    else:
        print(f"{prefix}<{tag} {attrs}>")
        for child in elem:
            print_tree(child, indent + 1)
        print(f"{prefix}</{tag}>")

print("Full XML structure:")
print_tree(root)

