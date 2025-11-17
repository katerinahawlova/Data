"""
download_rzp.py

Stahování dat z RZP (Registr živnostenského podnikání).

RZP API: https://rzp.gov.cz/rzp/api3-c/srv/vw/v31/vwinterface/xml
Metoda: HTTP POST s XML dotazem
Dokumentace: https://rzp.gov.cz/docs/RZP02_XML_31.pdf
"""

import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Dict, Any
import argparse
from datetime import datetime

# RZP API konfigurace
RZP_API_URL = "https://rzp.gov.cz/rzp/api3-c/srv/vw/v31/vwinterface/xml"
RZP_NS = "urn:cz:isvs:rzp:schemas:VerejnaCast:v1"

# Paths
BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / "data" / "people" / "raw" / "rzp"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def normalize_ico(ico: Optional[str]) -> Optional[str]:
    """
    Normalizuje IČO na formát bez mezer a s leading zeros.
    
    Args:
        ico: IČO jako string (může obsahovat mezery)
    
    Returns:
        Normalizované IČO (8 číslic) nebo None
    """
    if not ico:
        return None
    
    # Odstranit mezery a nečíselné znaky
    ico_clean = ''.join(filter(str.isdigit, str(ico)))
    
    # Doplní leading zeros pokud je potřeba
    if len(ico_clean) < 8:
        ico_clean = ico_clean.zfill(8)
    elif len(ico_clean) > 8:
        ico_clean = ico_clean[:8]
    
    return ico_clean if ico_clean else None


def create_xml_query_by_ico(ico: str, include_details: bool = True) -> str:
    """
    Vytvoří XML dotaz pro vyhledání podle IČO.
    
    Args:
        ico: IČO podnikatele (8 číslic)
        include_details: Zahrnout detailní informace (statutární orgán, atd.)
    
    Returns:
        XML dotaz jako string
    """
    # Podle dokumentace RZP musí být správná struktura s verzí
    # Pro získání detailních informací včetně statutárního orgánu
    # je potřeba použít správnou strukturu dotazu
    if include_details:
        xml_query = f"""<?xml version="1.0" encoding="ISO-8859-2"?>
<VerejnyWebDotaz xmlns="{RZP_NS}" version="3.1">
    <Kriteria>
        <IdentifikacniCislo>{ico}</IdentifikacniCislo>
        <PlatnostZaznamu>0</PlatnostZaznamu>
    </Kriteria>
    <DetailDotazu>true</DetailDotazu>
</VerejnyWebDotaz>"""
    else:
        xml_query = f"""<?xml version="1.0" encoding="ISO-8859-2"?>
<VerejnyWebDotaz xmlns="{RZP_NS}" version="3.1">
    <Kriteria>
        <IdentifikacniCislo>{ico}</IdentifikacniCislo>
    </Kriteria>
</VerejnyWebDotaz>"""
    return xml_query


def create_xml_query_by_name(name: str) -> str:
    """
    Vytvoří XML dotaz pro vyhledání podle názvu.
    
    Args:
        name: Název nebo část názvu podnikatele
    
    Returns:
        XML dotaz jako string
    """
    # Podle dokumentace RZP musí být správná struktura s verzí
    xml_query = f"""<?xml version="1.0" encoding="ISO-8859-2"?>
<VerejnyWebDotaz xmlns="{RZP_NS}" version="3.1">
    <Kriteria>
        <Nazev>{name}</Nazev>
    </Kriteria>
</VerejnyWebDotaz>"""
    return xml_query


def create_xml_query_by_ssarzp(ssarzp: str) -> str:
    """
    Vytvoří XML dotaz pro získání detailních informací podle ssarzp (hash z URL).
    
    Args:
        ssarzp: ssarzp hash z RZP web URL
    
    Returns:
        XML dotaz jako string
    """
    xml_query = f"""<?xml version="1.0" encoding="ISO-8859-2"?>
<VerejnyWebDotaz xmlns="{RZP_NS}" version="3.1">
    <Kriteria>
        <SsaRzp>{ssarzp}</SsaRzp>
    </Kriteria>
</VerejnyWebDotaz>"""
    return xml_query


def create_xml_query_by_podnikatel_id(podnikatel_id: str) -> str:
    """
    Vytvoří XML dotaz pro získání detailních informací podle PodnikatelID.
    
    Podle dokumentace RZP lze použít PodnikatelID pro získání detailních informací
    včetně statutárního orgánu.
    
    Args:
        podnikatel_id: PodnikatelID z předchozího dotazu
    
    Returns:
        XML dotaz jako string
    """
    xml_query = f"""<?xml version="1.0" encoding="ISO-8859-2"?>
<VerejnyWebDotaz xmlns="{RZP_NS}" version="3.1">
    <Kriteria>
        <PodnikatelID>{podnikatel_id}</PodnikatelID>
    </Kriteria>
    <DetailDotazu>true</DetailDotazu>
</VerejnyWebDotaz>"""
    return xml_query


def create_xml_query_by_company_relation(ico: str) -> str:
    """
    Vytvoří XML dotaz pro vyhledání osob spojených s firmou (jednatel, společník, atd.).
    
    Podle dokumentace RZP lze vyhledat osoby podle vazby na firmu pomocí RoleSubjektu.
    
    Args:
        ico: IČO firmy
    
    Returns:
        XML dotaz jako string
    """
    # Vyhledat osoby, které mají vazbu na firmu s daným IČO
    # Použijeme vyhledávání podle role subjektu
    xml_query = f"""<?xml version="1.0" encoding="ISO-8859-2"?>
<VerejnyWebDotaz xmlns="{RZP_NS}" version="3.1">
    <Kriteria>
        <RoleSubjektu>
            <IdentifikacniCislo>{ico}</IdentifikacniCislo>
        </RoleSubjektu>
    </Kriteria>
</VerejnyWebDotaz>"""
    return xml_query


def download_by_ico(ico: str, include_details: bool = True) -> ET.Element:
    """
    Stáhne data o podnikateli podle IČO z RZP API.
    
    Args:
        ico: IČO podnikatele (8 číslic)
        include_details: Zahrnout detailní informace (statutární orgán, atd.)
    
    Returns:
        XML root element s odpovědí
    
    Raises:
        requests.RequestException: Pokud request selže
        ET.ParseError: Pokud XML není validní
    """
    ico_normalized = normalize_ico(ico)
    if not ico_normalized:
        raise ValueError(f"Neplatné IČO: {ico}")
    
    print(f"[download_rzp] Stahuji data pro IČO: {ico_normalized} (details: {include_details})")
    
    # Vytvořit XML dotaz
    xml_query = create_xml_query_by_ico(ico_normalized, include_details)
    
    # Odeslat POST request
    try:
        response = requests.post(
            RZP_API_URL,
            data=xml_query.encode('iso-8859-2'),
            headers={'Content-Type': 'text/xml; charset=iso-8859-2'},
            timeout=30
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(f"Chyba při stahování z RZP API: {e}") from e
    
    # Parsovat XML odpověď
    try:
        root = ET.fromstring(response.content)
        return root
    except ET.ParseError as e:
        raise ValueError(f"Chyba při parsování XML odpovědi: {e}") from e


def download_by_company_relation(ico: str) -> ET.Element:
    """
    Stáhne data o osobách spojených s firmou (jednatel, společník, atd.) z RZP API.
    
    Args:
        ico: IČO firmy
    
    Returns:
        XML root element s odpovědí
    
    Raises:
        requests.RequestException: Pokud request selže
        ET.ParseError: Pokud XML není validní
    """
    ico_normalized = normalize_ico(ico)
    if not ico_normalized:
        raise ValueError(f"Neplatné IČO: {ico}")
    
    print(f"[download_rzp] Stahuji osoby spojené s firmou IČO: {ico_normalized}")
    
    # Vytvořit XML dotaz
    xml_query = create_xml_query_by_company_relation(ico_normalized)
    
    # Odeslat POST request
    try:
        response = requests.post(
            RZP_API_URL,
            data=xml_query.encode('iso-8859-2'),
            headers={'Content-Type': 'text/xml; charset=iso-8859-2'},
            timeout=30
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(f"Chyba při stahování z RZP API: {e}") from e
    
    # Parsovat XML odpověď
    try:
        root = ET.fromstring(response.content)
        return root
    except ET.ParseError as e:
        raise ValueError(f"Chyba při parsování XML odpovědi: {e}") from e


def download_by_name(name: str) -> ET.Element:
    """
    Stáhne data o podnikateli podle názvu z RZP API.
    
    Args:
        name: Název nebo část názvu podnikatele
    
    Returns:
        XML root element s odpovědí
    
    Raises:
        requests.RequestException: Pokud request selže
        ET.ParseError: Pokud XML není validní
    """
    print(f"[download_rzp] Stahuji data pro název: {name}")
    
    # Vytvořit XML dotaz
    xml_query = create_xml_query_by_name(name)
    
    # Odeslat POST request
    try:
        response = requests.post(
            RZP_API_URL,
            data=xml_query.encode('iso-8859-2'),
            headers={'Content-Type': 'text/xml; charset=iso-8859-2'},
            timeout=30
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(f"Chyba při stahování z RZP API: {e}") from e
    
    # Parsovat XML odpověď
    try:
        root = ET.fromstring(response.content)
        return root
    except ET.ParseError as e:
        raise ValueError(f"Chyba při parsování XML odpovědi: {e}") from e


def save_rzp_xml(xml_root: ET.Element, ico: Optional[str] = None) -> Path:
    """
    Uloží XML odpověď z RZP do souboru.
    
    Args:
        xml_root: XML root element
        ico: IČO pro pojmenování souboru (volitelné)
    
    Returns:
        Path k uloženému souboru
    """
    if ico:
        filename = f"rzp_ico_{normalize_ico(ico)}.xml"
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"rzp_{timestamp}.xml"
    
    output_path = RAW_DIR / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Vytvořit ElementTree a uložit
    tree = ET.ElementTree(xml_root)
    tree.write(output_path, encoding='iso-8859-2', xml_declaration=True)
    
    print(f"[download_rzp] Uloženo do: {output_path.name}")
    return output_path


def download_by_podnikatel_id(podnikatel_id: str) -> ET.Element:
    """
    Stáhne detailní data podle PodnikatelID z RZP API.
    
    Args:
        podnikatel_id: PodnikatelID z předchozího dotazu
    
    Returns:
        XML root element s odpovědí
    """
    print(f"[download_rzp] Stahuji detailní data pro PodnikatelID: {podnikatel_id[:20]}...")
    
    xml_query = create_xml_query_by_podnikatel_id(podnikatel_id)
    
    try:
        response = requests.post(
            RZP_API_URL,
            data=xml_query.encode('iso-8859-2'),
            headers={'Content-Type': 'text/xml; charset=iso-8859-2'},
            timeout=30
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(f"Chyba při stahování z RZP API: {e}") from e
    
    try:
        root = ET.fromstring(response.content)
        return root
    except ET.ParseError as e:
        raise ValueError(f"Chyba při parsování XML odpovědi: {e}") from e


def download_rzp_for_ico(ico: str, get_details: bool = True) -> Path:
    """
    Stáhne a uloží data z RZP pro dané IČO.
    Pokud get_details=True, stáhne i detailní informace včetně statutárního orgánu.
    
    Args:
        ico: IČO podnikatele
        get_details: Stáhnout detailní informace pomocí PodnikatelID
    
    Returns:
        Path k uloženému XML souboru
    """
    # Nejdřív základní dotaz
    xml_root = download_by_ico(ico, include_details=True)
    
    # Pokud chceme detailní informace, zkusit získat PodnikatelID a stáhnout detail
    if get_details:
        podnikatel_id = None
        for elem in xml_root.iter():
            if elem.tag.endswith('PodnikatelID'):
                podnikatel_id = elem.text
                break
        
        if podnikatel_id:
            print(f"[download_rzp] Nalezeno PodnikatelID, stahuji detailní informace...")
            try:
                detail_root = download_by_podnikatel_id(podnikatel_id)
                # Uložit detailní data
                return save_rzp_xml(detail_root, f"{ico}_detail")
            except Exception as e:
                print(f"[download_rzp] Varování: Nepodařilo se stáhnout detailní data: {e}")
                print(f"[download_rzp] Používám základní data")
    
    return save_rzp_xml(xml_root, ico)


def download_rzp_for_name(name: str) -> Path:
    """
    Stáhne a uloží data z RZP pro daný název.
    
    Args:
        name: Název podnikatele
    
    Returns:
        Path k uloženému XML souboru
    """
    xml_root = download_by_name(name)
    return save_rzp_xml(xml_root)


def download_rzp_for_company_relation(ico: str) -> Path:
    """
    Stáhne a uloží data z RZP o osobách spojených s firmou.
    
    Args:
        ico: IČO firmy
    
    Returns:
        Path k uloženému XML souboru
    """
    xml_root = download_by_company_relation(ico)
    return save_rzp_xml(xml_root, f"{ico}_relations")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Stahování dat z RZP (Registr živnostenského podnikání)"
    )
    parser.add_argument(
        "--ico",
        type=str,
        help="IČO podnikatele pro stáhnutí dat"
    )
    parser.add_argument(
        "--name",
        type=str,
        help="Název podnikatele pro stáhnutí dat"
    )
    parser.add_argument(
        "--company-relations",
        type=str,
        help="IČO firmy pro vyhledání osob spojených s firmou (jednatel, společník, atd.)"
    )
    
    args = parser.parse_args()
    
    if args.ico:
        try:
            path = download_rzp_for_ico(args.ico)
            print(f"✓ Data stažena a uložena: {path}")
        except Exception as e:
            print(f"❌ Chyba: {e}")
            exit(1)
    elif args.name:
        try:
            path = download_rzp_for_name(args.name)
            print(f"✓ Data stažena a uložena: {path}")
        except Exception as e:
            print(f"❌ Chyba: {e}")
            exit(1)
    elif args.company_relations:
        try:
            path = download_rzp_for_company_relation(args.company_relations)
            print(f"✓ Data stažena a uložena: {path}")
        except Exception as e:
            print(f"❌ Chyba: {e}")
            exit(1)
    else:
        print("❌ Musí být zadáno buď --ico, --name nebo --company-relations")
        parser.print_help()
        exit(1)

