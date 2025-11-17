"""
Download detailed RZP data including statutární orgán using ssarzp hash.

Workflow:
1. Get basic info by IČO → get ssarzp hash
2. Use ssarzp to download detailed XML with statutární orgán
"""

import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

RZP_API_URL = "https://rzp.gov.cz/rzp/api3-c/srv/vw/v31/vwinterface/xml"
RZP_NS = "urn:cz:isvs:rzp:schemas:VerejnaCast:v1"

BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / "data" / "people" / "raw" / "rzp"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def get_ssarzp_from_ico(ico: str) -> Optional[str]:
    """
    Získá ssarzp hash z první odpovědi podle IČO.
    
    Args:
        ico: IČO podnikatele
    
    Returns:
        ssarzp hash nebo None
    """
    # Základní dotaz podle IČO
    xml_query = f"""<?xml version="1.0" encoding="ISO-8859-2"?>
<VerejnyWebDotaz xmlns="{RZP_NS}" version="3.1">
    <Kriteria>
        <IdentifikacniCislo>{ico}</IdentifikacniCislo>
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
        
        # Hledat ssarzp v odpovědi - může být v různých elementech
        # Zkusit najít v PodnikatelSeznam nebo přímo v root
        for elem in root.iter():
            if 'ssarzp' in elem.tag.lower() or 'ssa' in elem.tag.lower():
                return elem.text
            # Nebo možná je to atribut
            for attr_name, attr_value in elem.attrib.items():
                if 'ssarzp' in attr_name.lower() or 'ssa' in attr_name.lower():
                    return attr_value
        
        # Pokud není ssarzp, zkusit získat z webu pomocí web scraping
        # Nebo použít PodnikatelID pro konstrukci URL
        podnikatel_id = None
        for elem in root.iter():
            if elem.tag.endswith('PodnikatelID'):
                podnikatel_id = elem.text
                break
        
        if podnikatel_id:
            # Zkusit získat ssarzp z webu
            # URL formát: https://rzp.gov.cz/verejne-udaje/cs/udaje/vyber-subjektu;ico=47114983;roleSubjektu=P
            web_url = f"https://rzp.gov.cz/verejne-udaje/cs/udaje/vyber-subjektu;ico={ico};roleSubjektu=P"
            # Pro web scraping by bylo potřeba použít Selenium nebo podobný nástroj
            # Pro teď vrátit None a použít jiný přístup
            return None
        
        return None
    except Exception as e:
        print(f"Chyba při získávání ssarzp: {e}")
        return None


def download_xml_by_ssarzp(ssarzp: str) -> Optional[ET.Element]:
    """
    Stáhne detailní XML podle ssarzp hash.
    
    Možné endpointy:
    - https://rzp.gov.cz/verejne-udaje/cs/udaje/vyber-subjektu;ico=.../subjekt;ssarzp=.../download
    - Nebo API endpoint s ssarzp parametrem
    
    Args:
        ssarzp: ssarzp hash
    
    Returns:
        XML root element nebo None
    """
    # Zkusit různé možnosti endpointu
    endpoints = [
        f"https://rzp.gov.cz/verejne-udaje/cs/udaje/subjekt;ssarzp={ssarzp}/download",
        f"https://rzp.gov.cz/verejne-udaje/cs/udaje/subjekt;ssarzp={ssarzp}/xml",
        f"https://rzp.gov.cz/rzp/api3-c/srv/vw/v31/vwinterface/xml?ssarzp={ssarzp}",
    ]
    
    # Nebo zkusit XML dotaz s ssarzp
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
        
        # Zkontrolovat, jestli odpověď obsahuje data
        if len(list(root)) > 2:  # Více než Datum a Kriteria
            return root
        
        return None
    except Exception as e:
        print(f"Chyba při stahování podle ssarzp: {e}")
        return None


def download_rzp_with_statutarni_organ(ico: str) -> Optional[Path]:
    """
    Stáhne RZP data včetně statutárního orgánu.
    
    Workflow:
    1. Získat ssarzp z první odpovědi nebo z webu
    2. Použít ssarzp pro stažení detailního XML
    
    Args:
        ico: IČO podnikatele
    
    Returns:
        Path k uloženému XML souboru nebo None
    """
    print(f"[download_rzp_detail] Získávám ssarzp pro IČO: {ico}")
    
    # Zkusit získat ssarzp
    ssarzp = get_ssarzp_from_ico(ico)
    
    if not ssarzp:
        print(f"[download_rzp_detail] Nepodařilo se získat ssarzp automaticky")
        print(f"[download_rzp_detail] Pro získání statutárního orgánu je potřeba:")
        print(f"  1. Otevřít: https://rzp.gov.cz/verejne-udaje/cs/udaje/vyber-subjektu;ico={ico};roleSubjektu=P")
        print(f"  2. Kliknout na 'Údaje s historií'")
        print(f"  3. Stáhnout XML ze stránky")
        print(f"  4. Nebo zkopírovat ssarzp z URL a použít: python3 scripts/download_rzp_detail.py --ssarzp <hash>")
        return None
    
    print(f"[download_rzp_detail] Nalezeno ssarzp: {ssarzp[:20]}...")
    
    # Stáhnout detailní XML
    detail_root = download_xml_by_ssarzp(ssarzp)
    
    if detail_root:
        output_path = RAW_DIR / f"rzp_ico_{ico}_detail.xml"
        tree = ET.ElementTree(detail_root)
        tree.write(output_path, encoding='iso-8859-2', xml_declaration=True)
        print(f"[download_rzp_detail] Uloženo do: {output_path.name}")
        return output_path
    else:
        print(f"[download_rzp_detail] Nepodařilo se stáhnout detailní data")
        return None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Stahování detailních RZP dat včetně statutárního orgánu"
    )
    parser.add_argument(
        "--ico",
        type=str,
        help="IČO podnikatele"
    )
    parser.add_argument(
        "--ssarzp",
        type=str,
        help="ssarzp hash (z URL RZP webu)"
    )
    
    args = parser.parse_args()
    
    if args.ssarzp:
        detail_root = download_xml_by_ssarzp(args.ssarzp)
        if detail_root:
            output_path = RAW_DIR / f"rzp_ssarzp_{args.ssarzp[:20]}.xml"
            tree = ET.ElementTree(detail_root)
            tree.write(output_path, encoding='iso-8859-2', xml_declaration=True)
            print(f"✓ Detailní data uložena: {output_path}")
        else:
            print("❌ Nepodařilo se stáhnout detailní data")
    elif args.ico:
        path = download_rzp_with_statutarni_organ(args.ico)
        if path:
            print(f"✓ Data uložena: {path}")
    else:
        print("❌ Musí být zadáno buď --ico nebo --ssarzp")
        parser.print_help()

