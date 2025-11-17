"""
Manual download of RZP XML with statutární orgán.

Since RZP web is a JavaScript app, we need to:
1. Get ssarzp hash from URL (user provides it)
2. Try to find the correct download endpoint
3. Or use web scraping if needed

Usage:
  python3 scripts/download_rzp_manual.py --ssarzp <hash>
  
To get ssarzp:
  1. Go to https://rzp.gov.cz/verejne-udaje/cs/udaje/vyber-subjektu;ico=47114983;roleSubjektu=P
  2. Click "Údaje s historií"
  3. Copy ssarzp from URL: .../subjekt;ssarzp=HASH;historie=true
"""

import requests
import xml.etree.ElementTree as ET
from pathlib import Path
import argparse
import re

BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / "data" / "people" / "raw" / "rzp"
RAW_DIR.mkdir(parents=True, exist_ok=True)

RZP_API_URL = "https://rzp.gov.cz/rzp/api3-c/srv/vw/v31/vwinterface/xml"
RZP_NS = "urn:cz:isvs:rzp:schemas:VerejnaCast:v1"


def try_download_by_ssarzp(ssarzp: str) -> ET.Element:
    """
    Zkusí stáhnout XML podle ssarzp pomocí různých metod.
    """
    print(f"[download_rzp_manual] Zkouším stáhnout XML pro ssarzp: {ssarzp[:20]}...")
    
    # Metoda 1: Zkusit XML dotaz s ssarzp
    xml_query = f"""<?xml version="1.0" encoding="ISO-8859-2"?>
<VerejnyWebDotaz xmlns="{RZP_NS}" version="3.1">
    <Kriteria>
        <SsaRzp>{ssarzp}</SsaRzp>
    </Kriteria>
</VerejnyWebDotaz>"""
    
    try:
        response = requests.post(
            RZP_API_URL,
            data=xml_query.encode('iso-8859-2'),
            headers={'Content-Type': 'text/xml; charset=iso-8859-2'},
            timeout=30
        )
        response.raise_for_status()
        root = ET.fromstring(response.content)
        
        # Zkontrolovat, jestli odpověď obsahuje data (více než Datum a Kriteria)
        if len(list(root)) > 2:
            print(f"[download_rzp_manual] ✓ Úspěšně staženo pomocí XML API")
            return root
    except Exception as e:
        print(f"[download_rzp_manual] XML API nefunguje: {e}")
    
    # Metoda 2: Zkusit různé možné endpointy
    endpoints = [
        f"https://rzp.gov.cz/verejne-udaje/cs/api/subjekt;ssarzp={ssarzp}/xml",
        f"https://rzp.gov.cz/verejne-udaje/cs/udaje/subjekt;ssarzp={ssarzp}/export",
        f"https://rzp.gov.cz/verejne-udaje/cs/udaje/subjekt;ssarzp={ssarzp}/download.xml",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=30)
            response.raise_for_status()
            
            # Zkontrolovat, jestli je to XML
            content_type = response.headers.get('Content-Type', '')
            if 'xml' in content_type.lower() or response.text.strip().startswith('<?xml'):
                print(f"[download_rzp_manual] ✓ Úspěšně staženo z: {endpoint}")
                return ET.fromstring(response.content)
        except Exception as e:
            continue
    
    print(f"[download_rzp_manual] ❌ Nepodařilo se stáhnout XML automaticky")
    return None


def save_xml(xml_root: ET.Element, filename: str) -> Path:
    """Uloží XML do souboru."""
    output_path = RAW_DIR / filename
    tree = ET.ElementTree(xml_root)
    tree.write(output_path, encoding='iso-8859-2', xml_declaration=True)
    print(f"[download_rzp_manual] Uloženo do: {output_path.name}")
    return output_path


def extract_ssarzp_from_url(url: str) -> str:
    """Extrahuje ssarzp hash z RZP URL."""
    match = re.search(r'ssarzp=([A-Za-z0-9]+)', url)
    if match:
        return match.group(1)
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Manuální stažení RZP XML s statutárním orgánem pomocí ssarzp hash"
    )
    parser.add_argument(
        "--ssarzp",
        type=str,
        help="ssarzp hash z RZP URL (např. z https://rzp.gov.cz/.../subjekt;ssarzp=HASH;historie=true)"
    )
    parser.add_argument(
        "--url",
        type=str,
        help="Celá RZP URL s ssarzp (automaticky extrahuje hash)"
    )
    
    args = parser.parse_args()
    
    ssarzp = None
    
    if args.url:
        ssarzp = extract_ssarzp_from_url(args.url)
        if not ssarzp:
            print("❌ Nepodařilo se extrahovat ssarzp z URL")
            exit(1)
        print(f"[download_rzp_manual] Extrahováno ssarzp z URL: {ssarzp[:20]}...")
    elif args.ssarzp:
        ssarzp = args.ssarzp
    else:
        print("❌ Musí být zadáno buď --ssarzp nebo --url")
        print("\nJak získat ssarzp:")
        print("1. Otevři: https://rzp.gov.cz/verejne-udaje/cs/udaje/vyber-subjektu;ico=47114983;roleSubjektu=P")
        print("2. Klikni na 'Údaje s historií'")
        print("3. Zkopíruj ssarzp z URL: .../subjekt;ssarzp=HASH;historie=true")
        print("\nPříklad:")
        print("  python3 scripts/download_rzp_manual.py --ssarzp A655989f672f8db3efca7170ed02cb35b7040ffdc2649a59e8f36c15604224ca91a9f")
        print("  python3 scripts/download_rzp_manual.py --url 'https://rzp.gov.cz/.../subjekt;ssarzp=HASH;historie=true'")
        exit(1)
    
    xml_root = try_download_by_ssarzp(ssarzp)
    
    if xml_root:
        path = save_xml(xml_root, f"rzp_ssarzp_{ssarzp[:20]}.xml")
        print(f"✓ XML uloženo: {path}")
        
        # Zkontrolovat, jestli obsahuje statutární orgán
        stat_org = xml_root.findall(f".//{{{RZP_NS}}}StatutarniOrgan")
        if stat_org:
            print(f"✓ Nalezeno {len(stat_org)} statutárních orgánů")
        else:
            print("⚠ Statutární orgán nebyl nalezen v XML")
    else:
        print("\n❌ Nepodařilo se stáhnout XML automaticky.")
        print("\nMožná řešení:")
        print("1. Zkusit použít web scraping (vyžaduje Selenium)")
        print("2. Stáhnout XML ručně ze stránky a uložit do data/people/raw/rzp/")
        print("3. Kontaktovat RZP podporu pro API endpoint")

