"""
Jednoduchý skript pro zpracování ručně staženého RZP XML.

Workflow:
1. Ručně stáhni XML z RZP webu (s názvem obsahujícím ico_XXXXX)
2. Zkopíruj do data/people/raw/rzp/
3. Spusť tento skript

Příklad:
  python3 scripts/process_manual_rzp.py --file ~/Downloads/rzp_ico_47114983.xml
  python3 scripts/process_manual_rzp.py --file data/people/raw/rzp/rzp_ico_47114983.xml
"""

import argparse
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / "data" / "people" / "raw" / "rzp"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def process_manual_rzp_xml(xml_path: Path):
    """
    Zpracuje ručně stažený RZP XML soubor.
    
    Args:
        xml_path: Cesta k XML souboru
    """
    xml_path = xml_path.resolve()
    
    if not xml_path.exists():
        print(f"❌ Soubor neexistuje: {xml_path}")
        sys.exit(1)
    
    # Zkopírovat do RAW_DIR, pokud není už tam
    if not xml_path.is_relative_to(RAW_DIR):
        target_path = RAW_DIR / xml_path.name
        if target_path.exists():
            print(f"⚠ Soubor už existuje v {RAW_DIR}, použiji existující")
        else:
            import shutil
            shutil.copy2(xml_path, target_path)
            print(f"✓ Zkopírováno do: {target_path}")
            xml_path = target_path
    else:
        print(f"✓ Používám soubor: {xml_path}")
    
    # Krok 1: Extrahovat data
    print("\n[1/3] Extrahuji data z XML...")
    result = subprocess.run(
        [sys.executable, "scripts/extract_rzp.py", "--file", str(xml_path)],
        cwd=BASE_DIR
    )
    
    if result.returncode != 0:
        print("❌ Chyba při extrakci dat")
        sys.exit(1)
    
    # Krok 2: Transformovat do Neo4j formátu
    print("\n[2/3] Transformuji do Neo4j formátu...")
    result = subprocess.run(
        [sys.executable, "scripts/transform_to_neo4j.py"],
        cwd=BASE_DIR
    )
    
    if result.returncode != 0:
        print("❌ Chyba při transformaci")
        sys.exit(1)
    
    # Krok 3: Načíst do Neo4j
    print("\n[3/3] Načítám do Neo4j...")
    result = subprocess.run(
        [sys.executable, "scripts/load_to_neo4j.py"],
        cwd=BASE_DIR
    )
    
    if result.returncode != 0:
        print("❌ Chyba při načítání do Neo4j")
        sys.exit(1)
    
    print("\n✓ Hotovo! Data jsou v Neo4j.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Zpracování ručně staženého RZP XML souboru"
    )
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="Cesta k ručně staženému XML souboru"
    )
    
    args = parser.parse_args()
    
    xml_path = Path(args.file).expanduser()
    process_manual_rzp_xml(xml_path)

