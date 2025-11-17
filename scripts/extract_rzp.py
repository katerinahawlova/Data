"""
extract_rzp.py

Extrakce strukturovaných dat z XML odpovědí z RZP (Registr živnostenského podnikání).

Funkce:
- parsuje XML soubory z RZP API
- extrahuje informace o osobách (živnostnících)
- extrahuje vazby mezi osobami a firmami
- ukládá do strukturovaného JSON formátu
"""

from pathlib import Path
import xml.etree.ElementTree as ET
import json
import argparse
from typing import Optional, List, Dict, Any
from datetime import datetime

# RZP XML namespace
RZP_NS = "urn:cz:isvs:rzp:schemas:VerejnaCast:v1"

# Paths
BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / "data" / "people" / "raw" / "rzp"
EXTRACTED_DIR = BASE_DIR / "data" / "people" / "extracted" / "rzp"
EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)


def normalize_ico(ico: Optional[str]) -> Optional[str]:
    """Normalizuje IČO na formát bez mezer a s leading zeros."""
    if not ico:
        return None
    ico_clean = ''.join(filter(str.isdigit, str(ico)))
    if len(ico_clean) < 8:
        ico_clean = ico_clean.zfill(8)
    elif len(ico_clean) > 8:
        ico_clean = ico_clean[:8]
    return ico_clean if ico_clean else None


def extract_address(element: ET.Element, prefix: str = "") -> Dict[str, str]:
    """
    Extrahuje adresu z XML elementu.
    
    Args:
        element: XML element obsahující adresu
        prefix: Prefix pro názvy elementů (např. "Sidlo", "Provozovna")
    
    Returns:
        Dictionary s adresou
    """
    address = {}
    
    if prefix:
        street_elem = element.find(f"{{{RZP_NS}}}{prefix}Ulice")
        city_elem = element.find(f"{{{RZP_NS}}}{prefix}Mesto")
        psc_elem = element.find(f"{{{RZP_NS}}}{prefix}Psc")
    else:
        street_elem = element.find(f"{{{RZP_NS}}}Ulice")
        city_elem = element.find(f"{{{RZP_NS}}}Mesto")
        psc_elem = element.find(f"{{{RZP_NS}}}Psc")
    
    if street_elem is not None:
        address["ulice"] = street_elem.text or ""
    if city_elem is not None:
        address["mesto"] = city_elem.text or ""
    if psc_elem is not None:
        address["psc"] = psc_elem.text or ""
    
    return address


def extract_roles(podnikatel: ET.Element) -> List[Dict[str, Any]]:
    """
    Extrahuje vazby mezi osobou a firmami (role, podíly).
    
    Args:
        podnikatel: XML element s informacemi o podnikateli
    
    Returns:
        Seznam vztahů (VYKONAVA_FUNKCI, VLASTNI_PODIL)
    """
    relationships = []
    
    # Hledat vazby na firmy
    # RZP může obsahovat různé typy vazeb - statutární orgán, společník, atd.
    
    # Statutární orgán - může být přímo v podnikateli nebo v Clen elementech
    # Hledat všechny StatutarniOrgan elementy
    statutarni_organy = podnikatel.findall(f".//{{{RZP_NS}}}StatutarniOrgan")
    
    for stat_org in statutarni_organy:
        # Statutární orgán může obsahovat Clen elementy (členy orgánu)
        clenove = stat_org.findall(f"{{{RZP_NS}}}Clen")
        
        if clenove:
            # Pro každého člena statutárního orgánu
            for clen in clenove:
                jmeno = clen.findtext(f"{{{RZP_NS}}}Jmeno", "")
                prijmeni = clen.findtext(f"{{{RZP_NS}}}Prijmeni", "")
                cele_jmeno = f"{jmeno} {prijmeni}".strip()
                platnost_od = clen.findtext(f"{{{RZP_NS}}}VznikFunkce", "") or clen.findtext(f"{{{RZP_NS}}}PlatnostOd", "")
                platnost_do = clen.findtext(f"{{{RZP_NS}}}ZanikFunkce", "") or clen.findtext(f"{{{RZP_NS}}}PlatnostDo", "")
                
                # Získat IČO firmy z nadřazeného elementu
                # Statutární orgán je v kontextu firmy
                firma_ico = None
                # Zkusit najít IČO v nadřazených elementech
                parent = stat_org
                while parent is not None:
                    ico_elem = parent.find(f"{{{RZP_NS}}}IdentifikacniCislo")
                    if ico_elem is not None:
                        firma_ico = normalize_ico(ico_elem.text)
                        break
                    parent = parent.getparent() if hasattr(parent, 'getparent') else None
                
                if firma_ico and cele_jmeno:
                    relationships.append({
                        "osoba_jmeno": cele_jmeno,
                        "firma_ico": firma_ico,
                        "role": "statutární orgán",
                        "platnost_od": platnost_od,
                        "platnost_do": platnost_do,
                        "type": "VYKONAVA_FUNKCI"
                    })
        else:
            # Statutární orgán bez členů - zkusit získat IČO přímo
            firma_ico = stat_org.findtext(f"{{{RZP_NS}}}IdentifikacniCislo", "")
            platnost_od = stat_org.findtext(f"{{{RZP_NS}}}PlatnostOd", "")
            platnost_do = stat_org.findtext(f"{{{RZP_NS}}}PlatnostDo", "")
            
            if firma_ico:
                relationships.append({
                    "firma_ico": normalize_ico(firma_ico),
                    "role": "statutární orgán",
                    "platnost_od": platnost_od,
                    "platnost_do": platnost_do,
                    "type": "VYKONAVA_FUNKCI"
                })
    
    # Také hledat přímo Clen elementy (mohou být členy statutárního orgánu)
    clenove = podnikatel.findall(f".//{{{RZP_NS}}}Clen")
    for clen in clenove:
        jmeno = clen.findtext(f"{{{RZP_NS}}}Jmeno", "")
        prijmeni = clen.findtext(f"{{{RZP_NS}}}Prijmeni", "")
        cele_jmeno = f"{jmeno} {prijmeni}".strip()
        platnost_od = clen.findtext(f"{{{RZP_NS}}}VznikFunkce", "") or clen.findtext(f"{{{RZP_NS}}}PlatnostOd", "")
        platnost_do = clen.findtext(f"{{{RZP_NS}}}ZanikFunkce", "") or clen.findtext(f"{{{RZP_NS}}}PlatnostDo", "")
        
        # Zkusit najít IČO firmy z kontextu
        firma_ico = None
        parent = clen
        for _ in range(5):  # Max 5 úrovní nahoru
            if parent is None:
                break
            ico_elem = parent.find(f"{{{RZP_NS}}}IdentifikacniCislo")
            if ico_elem is not None:
                firma_ico = normalize_ico(ico_elem.text)
                break
            # Zkusit getparent nebo iterovat přes rodiče
            if hasattr(parent, 'getparent'):
                parent = parent.getparent()
            else:
                break
        
        if firma_ico and cele_jmeno:
            relationships.append({
                "osoba_jmeno": cele_jmeno,
                "firma_ico": firma_ico,
                "role": "člen statutárního orgánu",
                "platnost_od": platnost_od,
                "platnost_do": platnost_do,
                "type": "VYKONAVA_FUNKCI"
            })
    
    # Společníci
    spolecnici = podnikatel.findall(f".//{{{RZP_NS}}}Spolecnik")
    for spolecnik in spolecnici:
        firma_ico = spolecnik.findtext(f"{{{RZP_NS}}}IdentifikacniCislo", "")
        podil = spolecnik.findtext(f"{{{RZP_NS}}}Podil", "")
        platnost_od = spolecnik.findtext(f"{{{RZP_NS}}}PlatnostOd", "")
        platnost_do = spolecnik.findtext(f"{{{RZP_NS}}}PlatnostDo", "")
        
        if firma_ico:
            relationships.append({
                "firma_ico": normalize_ico(firma_ico),
                "role": "společník",
                "platnost_od": platnost_od,
                "platnost_do": platnost_do,
                "type": "VYKONAVA_FUNKCI"
            })
            
            # Pokud je podíl, vytvořit i VLASTNI_PODIL
            if podil:
                try:
                    podil_procent = float(podil.replace("%", "").replace(",", "."))
                    relationships.append({
                        "firma_ico": normalize_ico(firma_ico),
                        "podil_procent": podil_procent,
                        "platnost_od": platnost_od,
                        "platnost_do": platnost_do,
                        "type": "VLASTNI_PODIL"
                    })
                except (ValueError, AttributeError):
                    pass
    
    # Obecné vazby (pokud existují)
    vazby = podnikatel.findall(f".//{{{RZP_NS}}}Vazba")
    for vazba in vazby:
        firma_ico = vazba.findtext(f"{{{RZP_NS}}}IdentifikacniCislo", "")
        role = vazba.findtext(f"{{{RZP_NS}}}Role", "")
        platnost_od = vazba.findtext(f"{{{RZP_NS}}}PlatnostOd", "")
        platnost_do = vazba.findtext(f"{{{RZP_NS}}}PlatnostDo", "")
        
        if firma_ico and role:
            relationships.append({
                "firma_ico": normalize_ico(firma_ico),
                "role": role.lower(),
                "platnost_od": platnost_od,
                "platnost_do": platnost_do,
                "type": "VYKONAVA_FUNKCI"
            })
    
    return relationships


def extract_business_fields(podnikatel: ET.Element) -> List[str]:
    """
    Extrahuje obory podnikání (živnosti).
    
    Args:
        podnikatel: XML element s informacemi o podnikateli
    
    Returns:
        Seznam oborů podnikání
    """
    obory = []
    
    # Hledat živnosti
    zivnosti = podnikatel.findall(f".//{{{RZP_NS}}}Zivnost")
    for zivnost in zivnosti:
        predmet = zivnost.findtext(f"{{{RZP_NS}}}Predmet", "")
        if predmet:
            obory.append(predmet)
    
    return obory


def extract_statutarni_organ_from_firma(root: ET.Element, xml_path: Path = None) -> List[Dict[str, Any]]:
    """
    Extrahuje statutární orgán z detailního XML firmy.
    
    Podporuje různé struktury:
    1. StatutarniOrgan/Clen (standardní)
    2. OsobaVeFunkci (detailní XML z webu)
    
    Args:
        root: XML root element
        xml_path: Cesta k XML souboru (pro získání IČO z názvu souboru)
    
    Returns:
        Seznam osob (členů statutárního orgánu) s vazbami na firmu
    """
    persons = []
    
    # Nejdřív zkusit najít IČO firmy (může být na různých místech)
    firma_ico = None
    ico_elem = root.find(f".//{{{RZP_NS}}}IdentifikacniCislo")
    if ico_elem is not None and ico_elem.text and ico_elem.text.strip():
        firma_ico = normalize_ico(ico_elem.text.strip())
    
    # Pokud IČO není v XML, zkusit získat z názvu souboru
    if not firma_ico and xml_path:
        if 'ico_' in xml_path.stem:
            parts = xml_path.stem.split('ico_')
            if len(parts) > 1:
                ico_from_filename = parts[1].split('_')[0]
                firma_ico = normalize_ico(ico_from_filename)
                print(f"[extract_statutarni_organ] IČO z názvu souboru: {firma_ico}")
    
    # Metoda 1: StatutarniOrgan/Clen struktura
    stat_orgs = root.findall(f".//{{{RZP_NS}}}StatutarniOrgan")
    
    for stat_org in stat_orgs:
        # Získat IČO firmy z kontextu (pokud ještě nemáme)
        if not firma_ico:
            parent = stat_org
            for _ in range(10):
                if parent is None:
                    break
                ico_elem = parent.find(f"{{{RZP_NS}}}IdentifikacniCislo")
                if ico_elem is not None and ico_elem.text:
                    firma_ico = normalize_ico(ico_elem.text.strip())
                    break
                ico_seznam = parent.find(f"{{{RZP_NS}}}IdentifikacniCisloSeznam")
                if ico_seznam is not None and ico_seznam.text:
                    firma_ico = normalize_ico(ico_seznam.text.strip())
                    break
                if hasattr(parent, 'getparent'):
                    parent = parent.getparent()
                else:
                    break
        
        # Najít všechny Clen elementy
        clenove = stat_org.findall(f"{{{RZP_NS}}}Clen")
        
        for clen in clenove:
            jmeno = clen.findtext(f"{{{RZP_NS}}}Jmeno", "")
            prijmeni = clen.findtext(f"{{{RZP_NS}}}Prijmeni", "")
            cele_jmeno = f"{jmeno} {prijmeni}".strip()
            datum_narozeni = clen.findtext(f"{{{RZP_NS}}}DatumNarozeni", "")
            platnost_od = clen.findtext(f"{{{RZP_NS}}}VznikFunkce", "") or clen.findtext(f"{{{RZP_NS}}}PlatnostOd", "")
            platnost_do = clen.findtext(f"{{{RZP_NS}}}ZanikFunkce", "") or clen.findtext(f"{{{RZP_NS}}}PlatnostDo", "")
            
            if cele_jmeno and firma_ico:
                person = {
                    "jmeno": jmeno,
                    "prijmeni": prijmeni,
                    "cele_jmeno": cele_jmeno,
                    "datum_narozeni": datum_narozeni,
                    "relationships": [{
                        "osoba_jmeno": cele_jmeno,
                        "firma_ico": firma_ico,
                        "role": "statutární orgán",
                        "platnost_od": platnost_od,
                        "platnost_do": platnost_do,
                        "type": "VYKONAVA_FUNKCI"
                    }],
                    "source": "rzp"
                }
                person = {k: v for k, v in person.items() if v}
                persons.append(person)
    
    # Metoda 2: OsobaVeFunkci struktura (detailní XML z webu)
    osoby_ve_funkci = root.findall(f".//{{{RZP_NS}}}OsobaVeFunkci")
    
    # Najít všechny ObdobiFunkce předem (pro mapování)
    obdobi_all = root.findall(f".//{{{RZP_NS}}}ObdobiFunkce")
    
    # Najít název firmy
    firma_nazev = None
    nazev_elem = root.find(f".//{{{RZP_NS}}}ObchodniJmeno")
    if nazev_elem is not None and nazev_elem.text:
        firma_nazev = nazev_elem.text.strip()
    
    for idx, osoba_elem in enumerate(osoby_ve_funkci):
        # Získat jméno
        jmeno_prijmeni = osoba_elem.findtext(f"{{{RZP_NS}}}OsobaJmenoPrijmeni", "")
        if not jmeno_prijmeni:
            continue
        
        jmeno_prijmeni = jmeno_prijmeni.strip()
        # Rozdělit jméno a příjmení (obvykle "Jméno Příjmení")
        parts = jmeno_prijmeni.split(" ", 1)
        jmeno = parts[0] if parts else ""
        prijmeni = parts[1] if len(parts) > 1 else ""
        
        # Získat období funkce - zkusit najít odpovídající ObdobiFunkce
        platnost_od = None
        platnost_do = None
        
        # Zkusit najít ObdobiFunkce přímo v osobě
        obdobi = osoba_elem.find(f"{{{RZP_NS}}}ObdobiFunkce")
        if obdobi is not None:
            # Zkusit různé názvy elementů pro datum
            platnost_od = (obdobi.findtext(f"{{{RZP_NS}}}Ustanoven", "") or 
                          obdobi.findtext(f"{{{RZP_NS}}}DatumZapisuOd", "") or 
                          obdobi.findtext(f"{{{RZP_NS}}}DatumPlatnostiOd", ""))
            platnost_do = (obdobi.findtext(f"{{{RZP_NS}}}Ukoncen", "") or 
                          obdobi.findtext(f"{{{RZP_NS}}}DatumZapisuDo", "") or 
                          obdobi.findtext(f"{{{RZP_NS}}}DatumPlatnostiDo", ""))
        
        # Pokud není ObdobiFunkce v osobě, zkusit najít podle indexu
        # (pokud jsou ve stejném pořadí jako osoby)
        if not platnost_od and idx < len(obdobi_all):
            obdobi = obdobi_all[idx]
            platnost_od = (obdobi.findtext(f"{{{RZP_NS}}}Ustanoven", "") or 
                          obdobi.findtext(f"{{{RZP_NS}}}DatumZapisuOd", "") or 
                          obdobi.findtext(f"{{{RZP_NS}}}DatumPlatnostiOd", ""))
            platnost_do = (obdobi.findtext(f"{{{RZP_NS}}}Ukoncen", "") or 
                          obdobi.findtext(f"{{{RZP_NS}}}DatumZapisuDo", "") or 
                          obdobi.findtext(f"{{{RZP_NS}}}DatumPlatnostiDo", ""))
        
        # Získat datum narození (pokud je k dispozici)
        datum_narozeni = osoba_elem.findtext(f"{{{RZP_NS}}}DatumNarozeni", "")
        
        # Získat funkci - VeFunkci může být prázdné, použijeme výchozí hodnotu
        funkce = osoba_elem.findtext(f"{{{RZP_NS}}}VeFunkci", "")
        if not funkce or not funkce.strip():
            funkce = "statutární orgán"
        
        if jmeno_prijmeni and firma_ico:
            person = {
                "jmeno": jmeno,
                "prijmeni": prijmeni,
                "cele_jmeno": jmeno_prijmeni,
                "datum_narozeni": datum_narozeni.strip() if datum_narozeni else None,
                "relationships": [{
                    "osoba_jmeno": jmeno_prijmeni,
                    "firma_ico": firma_ico,
                    "firma_nazev": firma_nazev,  # Přidat název firmy
                    "role": funkce.strip() if funkce else "statutární orgán",
                    "platnost_od": platnost_od.strip() if platnost_od else None,
                    "platnost_do": platnost_do.strip() if platnost_do else None,
                    "type": "VYKONAVA_FUNKCI"
                }],
                "source": "rzp"
            }
            person = {k: v for k, v in person.items() if v}
            persons.append(person)
    
    return persons


def extract_person_from_xml(xml_path: Path) -> List[Dict[str, Any]]:
    """
    Extrahuje informace o osobách z RZP XML.
    
    Podporuje jak základní XML (PodnikatelSeznam), tak detailní XML s statutárním orgánem.
    
    Args:
        xml_path: Cesta k XML souboru z RZP
    
    Returns:
        Seznam osob s jejich vazbami na firmy
    """
    print(f"[extract_rzp] Parsuji XML soubor: {xml_path.name}")
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError as e:
        raise ValueError(f"Chyba při parsování XML: {e}") from e
    
    persons = []
    
    # Nejdřív zkusit extrahovat statutární orgán z detailního XML (pokud je to detailní XML)
    stat_org_persons = extract_statutarni_organ_from_firma(root, xml_path)
    if stat_org_persons:
        print(f"[extract_rzp] Nalezeno {len(stat_org_persons)} osob ze statutárního orgánu")
        persons.extend(stat_org_persons)
    
    # Najít všechny podnikatele v odpovědi
    # RZP může vrátit více výsledků - struktura může být PodnikatelSeznam nebo Podnikatel
    podnikatele = root.findall(f".//{{{RZP_NS}}}PodnikatelSeznam")
    
    if not podnikatele:
        # Zkusit najít jinou strukturu
        podnikatele = root.findall(f".//{{{RZP_NS}}}Podnikatel")
    
    if not podnikatele:
        # Zkusit najít Vysledek
        podnikatele = root.findall(f".//{{{RZP_NS}}}Vysledek")
    
    print(f"[extract_rzp] Nalezeno {len(podnikatele)} podnikatelů")
    
    for podnikatel in podnikatele:
        # Základní informace - struktura může být různá
        # Pro PodnikatelSeznam:
        ico_elem = podnikatel.find(f"{{{RZP_NS}}}IdentifikacniCisloSeznam")
        if ico_elem is not None:
            ico = normalize_ico(ico_elem.text)
        else:
            ico = normalize_ico(podnikatel.findtext(f"{{{RZP_NS}}}IdentifikacniCislo", ""))
        
        # Jméno a příjmení - může být v ObchodniJmenoSeznam nebo Jmeno/Prijmeni
        obchodni_jmeno_elem = podnikatel.find(f"{{{RZP_NS}}}ObchodniJmenoSeznam")
        if obchodni_jmeno_elem is not None:
            cele_jmeno = obchodni_jmeno_elem.text or ""
            # Zkusit rozdělit na jméno a příjmení
            name_parts = cele_jmeno.split(" ", 1)
            jmeno = name_parts[0] if name_parts else ""
            prijmeni = name_parts[1] if len(name_parts) > 1 else ""
        else:
            jmeno = podnikatel.findtext(f"{{{RZP_NS}}}Jmeno", "")
            prijmeni = podnikatel.findtext(f"{{{RZP_NS}}}Prijmeni", "")
            cele_jmeno = f"{jmeno} {prijmeni}".strip()
        
        datum_narozeni = podnikatel.findtext(f"{{{RZP_NS}}}DatumNarozeni", "")
        
        # Adresa - může být v AdresaPodnikaniSeznam
        adresa_elem = podnikatel.find(f"{{{RZP_NS}}}AdresaPodnikaniSeznam")
        if adresa_elem is not None:
            adresa_text = adresa_elem.text or ""
            # Parsovat adresu (formát: "Ulice, PSC, Mesto")
            sidlo = {"adresa": adresa_text}
        else:
            sidlo = extract_address(podnikatel, "Sidlo")
        
        # Vazby na firmy
        relationships = extract_roles(podnikatel)
        
        # Obory podnikání
        obory = extract_business_fields(podnikatel)
        
        # Sestavit objekt osoby
        person = {
            "ico": ico,
            "jmeno": jmeno,
            "prijmeni": prijmeni,
            "cele_jmeno": cele_jmeno,
            "datum_narozeni": datum_narozeni,
            "adresa": sidlo,
            "obory": obory,
            "relationships": relationships,
            "source": "rzp"
        }
        
        # Odstranit prázdné hodnoty
        person = {k: v for k, v in person.items() if v}
        
        # Přidat pouze pokud má nějaká data (ne prázdný objekt)
        if person.get("ico") or person.get("cele_jmeno") or person.get("relationships"):
            persons.append(person)
    
    print(f"[extract_rzp] Extrahováno {len(persons)} osob")
    return persons


def extract_rzp_file(xml_path: Path, filter_ico: Optional[str] = None) -> Path:
    """
    Extrahuje data z RZP XML souboru a uloží do JSON.
    
    Args:
        xml_path: Cesta k XML souboru
        filter_ico: Volitelné IČO pro filtrování
    
    Returns:
        Path k uloženému JSON souboru
    """
    persons = extract_person_from_xml(xml_path)
    
    # Filtrování podle IČO
    if filter_ico:
        filter_ico_normalized = normalize_ico(filter_ico)
        persons = [p for p in persons if p.get("ico") == filter_ico_normalized]
        print(f"[extract_rzp] Po filtrování podle IČO {filter_ico}: {len(persons)} osob")
    
    if not persons:
        print("[extract_rzp] Žádné osoby k uložení")
        return None
    
    # Vytvořit název výstupního souboru
    if filter_ico:
        ico_normalized = normalize_ico(filter_ico)
        filename = f"rzp_persons_ico_{ico_normalized}.json"
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"rzp_persons_{timestamp}.json"
    
    output_path = EXTRACTED_DIR / filename
    
    # Uložit do JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(persons, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"[extract_rzp] Uloženo do: {output_path.name}")
    return output_path


def extract_all_rzp_files(filter_ico: Optional[str] = None):
    """
    Extrahuje všechny XML soubory z RAW_DIR.
    
    Args:
        filter_ico: Volitelné IČO pro filtrování
    """
    xml_files = list(RAW_DIR.glob("rzp_*.xml"))
    
    if not xml_files:
        print(f"[extract_rzp] Nenalezeny žádné XML soubory v {RAW_DIR}")
        return
    
    print(f"[extract_rzp] Nalezeno {len(xml_files)} XML souborů")
    
    for xml_file in xml_files:
        try:
            extract_rzp_file(xml_file, filter_ico=filter_ico)
        except Exception as e:
            print(f"[extract_rzp] Chyba při zpracování {xml_file.name}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extrakce strukturovaných dat z RZP XML souborů"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Cesta k XML souboru pro extrakci"
    )
    parser.add_argument(
        "--ico",
        type=str,
        help="Filtrovat podle IČO"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Zpracovat všechny XML soubory v raw adresáři"
    )
    
    args = parser.parse_args()
    
    if args.file:
        try:
            path = extract_rzp_file(Path(args.file), filter_ico=args.ico)
            if path:
                print(f"✓ Data extrahována: {path}")
        except Exception as e:
            print(f"❌ Chyba: {e}")
            exit(1)
    elif args.all:
        try:
            extract_all_rzp_files(filter_ico=args.ico)
            print("✓ Všechny soubory zpracovány")
        except Exception as e:
            print(f"❌ Chyba: {e}")
            exit(1)
    else:
        print("❌ Musí být zadáno buď --file nebo --all")
        parser.print_help()
        exit(1)

