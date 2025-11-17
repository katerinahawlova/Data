"""
Process manually downloaded RZP XML file.

Since RZP API doesn't support downloading detailed XML with statutární orgán,
users need to download it manually from the web interface.

Usage:
  python3 scripts/process_manual_rzp_xml.py --file <path_to_xml>
  
To download XML manually:
  1. Go to https://rzp.gov.cz/verejne-udaje/cs/udaje/vyber-subjektu;ico=47114983;roleSubjektu=P
  2. Click "Údaje s historií"
  3. Click "Stáhnout údaje" button on the page
  4. Save the XML file
  5. Run this script to process it
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import argparse
import shutil

BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / "data" / "people" / "raw" / "rzp"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def process_manual_xml(xml_path: Path) -> Path:
    """
    Zpracuje ručně stažený RZP XML soubor.
    
    Args:
        xml_path: Cesta k ručně staženému XML souboru
    
    Returns:
        Path k uloženému souboru v RAW_DIR
    """
    print(f"[process_manual_rzp] Zpracovávám XML soubor: {xml_path.name}")
    
    # Zkontrolovat, jestli soubor existuje
    if not xml_path.exists():
        raise FileNotFoundError(f"Soubor neexistuje: {xml_path}")
    
    # Zkontrolovat, jestli je to XML
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError as e:
        raise ValueError(f"Neplatný XML soubor: {e}") from e
    
    # Zkontrolovat, jestli obsahuje statutární orgán
    RZP_NS = "urn:cz:isvs:rzp:schemas:VerejnaCast:v1"
    stat_org = root.findall(f".//{{{RZP_NS}}}StatutarniOrgan")
    clen = root.findall(f".//{{{RZP_NS}}}Clen")
    
    print(f"[process_manual_rzp] Nalezeno {len(stat_org)} StatutarniOrgan elementů")
    print(f"[process_manual_rzp] Nalezeno {len(clen)} Clen elementů")
    
    # Zkopírovat do RAW_DIR
    output_path = RAW_DIR / f"rzp_manual_{xml_path.stem}.xml"
    shutil.copy2(xml_path, output_path)
    
    print(f"[process_manual_rzp] ✓ Soubor zkopírován do: {output_path.name}")
    return output_path


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
    
    try:
        xml_path = Path(args.file).expanduser().resolve()
        output_path = process_manual_xml(xml_path)
        print(f"\n✓ XML soubor zpracován: {output_path}")
        print(f"\nNyní můžeš spustit:")
        print(f"  python3 scripts/extract_rzp.py --file {output_path}")
    except Exception as e:
        print(f"❌ Chyba: {e}")
        exit(1)

