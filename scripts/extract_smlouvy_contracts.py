"""
extract_smlouvy_contracts.py

Extrakce smluv z XML dumpů z Registru smluv (smlouvy.gov.cz).

Funkce:
- parsuje XML dump soubory
- extrahuje informace o smlouvách (zadavatel, dodavatel, hodnota, datum)
- umožňuje filtrování podle IČO
- ukládá do strukturovaného JSON formátu
- podporuje inkrementální aktualizace (sleduje, co už bylo zpracováno)
"""

from pathlib import Path
import xml.etree.ElementTree as ET
import json
import argparse
from datetime import datetime
from typing import Optional, List, Dict, Any

# XML namespace for smlouvy.gov.cz
XML_NS = "http://portal.gov.cz/rejstriky/ISRS/1.2/"

# Paths
BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / "data" / "tenders" / "raw" / "smlouvy_gov"
EXTRACTED_DIR = BASE_DIR / "data" / "tenders" / "extracted" / "smlouvy_gov"
METADATA_DIR = BASE_DIR / "data" / "tenders" / "metadata"
METADATA_FILE = METADATA_DIR / "smlouvy_gov_status.json"


def load_metadata() -> Dict[str, Any]:
    """Načte metadata o zpracovaných datech."""
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    
    if METADATA_FILE.exists():
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return {
        "source": "smlouvy_gov",
        "downloaded_months": [],
        "extracted_months": [],
        "processed_icos": [],
        "last_download": None,
        "last_extract": None
    }


def save_metadata(metadata: Dict[str, Any]) -> None:
    """Uloží metadata o zpracovaných datech."""
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    metadata["last_extract"] = datetime.now().isoformat()
    
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def normalize_ico(ico: Optional[str]) -> Optional[str]:
    """
    Normalizuje IČO - odstraní mezery a převede na string.
    
    IČO může být v různých formátech:
    - "70886288"
    - "604 69 803" (s mezerami)
    - "28.05.1955" (někdy je to datum narození místo IČO)
    """
    if not ico:
        return None
    
    # Odstranit mezery
    ico_clean = str(ico).replace(" ", "").replace(".", "")
    
    # Pokud vypadá jako datum (obsahuje tečky a je delší), vrátit None
    if "." in str(ico) and len(str(ico)) > 10:
        return None
    
    return ico_clean if ico_clean else None


def extract_contract_from_zaznam(zaznam: ET.Element) -> Optional[Dict[str, Any]]:
    """
    Extrahuje informace o smlouvě z XML elementu <zaznam>.
    
    Vrací slovník s informacemi o smlouvě nebo None, pokud není platný záznam.
    """
    # Zkontrolovat, zda je záznam platný
    platny = zaznam.findtext(f"{{{XML_NS}}}platnyZaznam")
    if platny != "1":
        return None
    
    # Identifikátory
    identifikator = zaznam.find(f"{{{XML_NS}}}identifikator")
    if identifikator is None:
        return None
    
    contract_id = identifikator.findtext(f"{{{XML_NS}}}idSmlouvy")
    version_id = identifikator.findtext(f"{{{XML_NS}}}idVerze")
    url = zaznam.findtext(f"{{{XML_NS}}}odkaz")
    published_date = zaznam.findtext(f"{{{XML_NS}}}casZverejneni")
    
    # Smlouva
    smlouva = zaznam.find(f"{{{XML_NS}}}smlouva")
    if smlouva is None:
        return None
    
    # Zadavatel (subjekt)
    subjekt = smlouva.find(f"{{{XML_NS}}}subjekt")
    authority = {}
    if subjekt is not None:
        authority = {
            "ico": normalize_ico(subjekt.findtext(f"{{{XML_NS}}}ico")),
            "name": subjekt.findtext(f"{{{XML_NS}}}nazev") or "",
            "address": subjekt.findtext(f"{{{XML_NS}}}adresa") or "",
            "datova_schranka": subjekt.findtext(f"{{{XML_NS}}}datovaSchranka") or "",
            "utvar": subjekt.findtext(f"{{{XML_NS}}}utvar") or ""
        }
    
    # Dodavatel (smluvniStrana)
    smluvni_strana = smlouva.find(f"{{{XML_NS}}}smluvniStrana")
    contractor = {}
    if smluvni_strana is not None:
        contractor = {
            "ico": normalize_ico(smluvni_strana.findtext(f"{{{XML_NS}}}ico")),
            "name": smluvni_strana.findtext(f"{{{XML_NS}}}nazev") or "",
            "address": smluvni_strana.findtext(f"{{{XML_NS}}}adresa") or "",
            "datova_schranka": smluvni_strana.findtext(f"{{{XML_NS}}}datovaSchranka") or "",
            "utvar": smluvni_strana.findtext(f"{{{XML_NS}}}utvar") or ""
        }
    
    # Detaily smlouvy
    subject = smlouva.findtext(f"{{{XML_NS}}}predmet") or ""
    contract_date = smlouva.findtext(f"{{{XML_NS}}}datumUzavreni") or ""
    contract_number = smlouva.findtext(f"{{{XML_NS}}}cisloSmlouvy") or ""
    approved_by = smlouva.findtext(f"{{{XML_NS}}}schvalil") or ""
    
    # Hodnoty
    value_with_vat = smlouva.findtext(f"{{{XML_NS}}}hodnotaVcetneDph")
    value_without_vat = smlouva.findtext(f"{{{XML_NS}}}hodnotaBezDph")
    
    # Převést na čísla
    try:
        value_with_vat = float(value_with_vat) if value_with_vat else None
    except (ValueError, TypeError):
        value_with_vat = None
    
    try:
        value_without_vat = float(value_without_vat) if value_without_vat else None
    except (ValueError, TypeError):
        value_without_vat = None
    
    # Přílohy
    attachments = []
    prilohy = smlouva.find(f"{{{XML_NS}}}prilohy")
    if prilohy is not None:
        for priloha in prilohy.findall(f"{{{XML_NS}}}priloha"):
            attachment = {
                "filename": priloha.findtext(f"{{{XML_NS}}}nazevSouboru") or "",
                "hash": priloha.findtext(f"{{{XML_NS}}}hash") or "",
                "url": priloha.findtext(f"{{{XML_NS}}}odkaz") or ""
            }
            attachments.append(attachment)
    
    # Sestavit výsledný objekt
    contract = {
        "contract_id": contract_id,
        "version_id": version_id,
        "url": url,
        "published_date": published_date,
        "authority": authority,
        "contractor": contractor,
        "subject": subject,
        "contract_date": contract_date,
        "contract_number": contract_number,
        "approved_by": approved_by,
        "value_with_vat": value_with_vat,
        "value_without_vat": value_without_vat,
        "attachments": attachments,
        "source": "smlouvy_gov"
    }
    
    return contract


def extract_contracts_from_xml(
    xml_path: Path,
    filter_ico: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Extrahuje všechny smlouvy z XML souboru.
    
    Args:
        xml_path: Cesta k XML dump souboru
        filter_ico: Volitelné IČO pro filtrování (zobrazí pouze smlouvy, kde je toto IČO zadavatel nebo dodavatel)
    
    Returns:
        Seznam slovníků s informacemi o smlouvách
    """
    print(f"[extract] Parsuji XML soubor: {xml_path.name}")
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError as e:
        raise ValueError(f"Chyba při parsování XML: {e}")
    
    contracts = []
    filter_ico_normalized = normalize_ico(filter_ico) if filter_ico else None
    
    # Najít všechny <zaznam> elementy (s namespace)
    # XML struktura: <daily> -> <den> -> <zaznam>
    zaznamy = root.findall(f".//{{{XML_NS}}}zaznam")
    print(f"[extract] Nalezeno {len(zaznamy)} záznamů v XML")
    
    for i, zaznam in enumerate(zaznamy):
        if (i + 1) % 1000 == 0:
            print(f"[extract] Zpracováno {i + 1}/{len(zaznamy)} záznamů...")
        
        contract = extract_contract_from_zaznam(zaznam)
        
        if contract is None:
            continue
        
        # Filtrování podle IČO
        if filter_ico_normalized:
            authority_ico = contract["authority"].get("ico")
            contractor_ico = contract["contractor"].get("ico")
            
            if (authority_ico != filter_ico_normalized and 
                contractor_ico != filter_ico_normalized):
                continue
        
        contracts.append(contract)
    
    print(f"[extract] Extrahováno {len(contracts)} smluv")
    if filter_ico:
        print(f"[extract] Filtrováno podle IČO: {filter_ico}")
    
    return contracts


def extract_dump(
    dump_path: Path,
    filter_ico: Optional[str] = None,
    incremental: bool = True
) -> Path:
    """
    Extrahuje smlouvy z XML dump souboru a uloží je do JSON.
    
    Args:
        dump_path: Cesta k XML dump souboru
        filter_ico: Volitelné IČO pro filtrování
        incremental: Pokud True, přeskočí, pokud už byl soubor zpracován
    
    Returns:
        Cesta k vytvořenému JSON souboru
    """
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Určit název výstupního souboru
    dump_name = dump_path.stem  # např. "dump_2025_11_01"
    
    if filter_ico:
        output_filename = f"contracts_{dump_name}_ico_{filter_ico}.json"
    else:
        output_filename = f"contracts_{dump_name}.json"
    
    output_path = EXTRACTED_DIR / output_filename
    
    # Zkontrolovat, zda už není zpracováno (inkrementální režim)
    if incremental and output_path.exists():
        print(f"[extract] Soubor už existuje, přeskakuji: {output_path.name}")
        return output_path
    
    # Extrahovat smlouvy
    contracts = extract_contracts_from_xml(dump_path, filter_ico=filter_ico)
    
    # Uložit do JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(contracts, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"[extract] Uloženo {len(contracts)} smluv do: {output_path.name}")
    
    # Aktualizovat metadata
    metadata = load_metadata()
    month_key = dump_name.replace("dump_", "").replace("_01", "")  # "2025_11_01" -> "2025_11"
    if month_key not in metadata["extracted_months"]:
        metadata["extracted_months"].append(month_key)
    if filter_ico:
        ico_normalized = normalize_ico(filter_ico)
        if ico_normalized and ico_normalized not in metadata["processed_icos"]:
            metadata["processed_icos"].append(ico_normalized)
    save_metadata(metadata)
    
    return output_path


def extract_latest_dump(
    filter_ico: Optional[str] = None,
    incremental: bool = True
) -> Path:
    """
    Extrahuje smlouvy z nejnovějšího staženého dumpu.
    """
    # Najít nejnovější XML soubor
    xml_files = sorted(RAW_DIR.glob("dump_*.xml"), reverse=True)
    
    if not xml_files:
        raise FileNotFoundError(f"Nenalezen žádný XML dump v {RAW_DIR}")
    
    latest_dump = xml_files[0]
    print(f"[extract] Používám nejnovější dump: {latest_dump.name}")
    
    return extract_dump(latest_dump, filter_ico=filter_ico, incremental=incremental)


def extract_dump_for_month(
    year: int,
    month: int,
    filter_ico: Optional[str] = None,
    incremental: bool = True
) -> Path:
    """
    Extrahuje smlouvy z dumpu pro konkrétní měsíc.
    """
    # Najít odpovídající XML soubor
    pattern = f"dump_{year}_{month:02d}_*.xml"
    xml_files = list(RAW_DIR.glob(pattern))
    
    if not xml_files:
        raise FileNotFoundError(f"Nenalezen dump pro {year}-{month:02d} v {RAW_DIR}")
    
    if len(xml_files) > 1:
        # Pokud je více souborů, použít nejnovější
        dump_path = sorted(xml_files, reverse=True)[0]
        print(f"[extract] Nalezeno více dumpů, používám: {dump_path.name}")
    else:
        dump_path = xml_files[0]
    
    return extract_dump(dump_path, filter_ico=filter_ico, incremental=incremental)


def parse_args() -> argparse.Namespace:
    """CLI argumenty pro samostatné použití."""
    parser = argparse.ArgumentParser(
        description="Extrakce smluv z XML dumpů z Registru smluv."
    )
    
    parser.add_argument(
        "--dump",
        type=str,
        help="Cesta k XML dump souboru (pokud není zadáno, použije se nejnovější)"
    )
    
    parser.add_argument(
        "--year",
        type=int,
        help="Rok dumpu (použije se spolu s --month)"
    )
    
    parser.add_argument(
        "--month",
        type=int,
        help="Měsíc dumpu (1-12, použije se spolu s --year)"
    )
    
    parser.add_argument(
        "--ico",
        type=str,
        help="Filtrovat podle IČO (zobrazí pouze smlouvy s tímto IČO jako zadavatel nebo dodavatel)"
    )
    
    parser.add_argument(
        "--no-incremental",
        action="store_true",
        help="Přeprocessovat i když už soubor existuje"
    )
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    
    incremental = not args.no_incremental
    
    try:
        if args.dump:
            dump_path = Path(args.dump)
            if not dump_path.is_absolute():
                dump_path = RAW_DIR / dump_path
            output_path = extract_dump(dump_path, filter_ico=args.ico, incremental=incremental)
        
        elif args.year and args.month:
            if not (1 <= args.month <= 12):
                print(f"Chyba: Měsíc musí být v rozsahu 1-12, zadáno: {args.month}")
                exit(1)
            output_path = extract_dump_for_month(
                args.year, args.month,
                filter_ico=args.ico,
                incremental=incremental
            )
        
        else:
            output_path = extract_latest_dump(filter_ico=args.ico, incremental=incremental)
        
        print(f"\n✓ Extrakce dokončena: {output_path}")
        
    except Exception as e:
        print(f"\n✗ Chyba: {e}")
        exit(1)

