"""
download_smlouvy_gov.py

Stahování open dat z Registru smluv (smlouvy.gov.cz).

Verze 0.2:
- stáhne index dumpů (index.xml)
- umí:
    a) najít a stáhnout poslední "dokončený" měsíční dump
    b) nebo stáhnout konkrétní rok + měsíc (pokud jsou zadány)
- soubory ukládá do: data/tenders/raw/smlouvy_gov/
"""

from pathlib import Path
import requests
import xml.etree.ElementTree as ET
import argparse

BASE_URL = "https://data.smlouvy.gov.cz"
INDEX_URL = f"{BASE_URL}/index.xml"

# XML namespace for smlouvy.gov.cz index
XML_NS = "http://portal.gov.cz/rejstriky/ISRS/1.2/"

# Make path relative to script location, not current working directory
RAW_DIR = Path(__file__).parent.parent / "data" / "tenders" / "raw" / "smlouvy_gov"


def download_index() -> ET.Element:
    """
    Stáhne indexový soubor (index.xml) a vrátí jej jako XML root element.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    resp = requests.get(INDEX_URL, timeout=60)
    resp.raise_for_status()
    
    try:
        return ET.fromstring(resp.content)
    except ET.ParseError as e:
        raise ValueError(f"Chyba při parsování XML indexu: {e}") from e


def select_latest_finished_dump(index_root: ET.Element) -> dict:
    """
    Z indexu vybere poslední "dokončený" dump.

    Index obsahuje prvky <dump>, u nichž je:
    - rok
    - mesic
    - dokoncenyMesic (0/1)
    - odkaz (URL na dump)

    Vrací slovník s klíči: rok, mesic, url
    """
    dumps = []

    for dump in index_root.findall(f".//{{{XML_NS}}}dump"):
        try:
            rok = int(dump.findtext(f"{{{XML_NS}}}rok"))
            mesic = int(dump.findtext(f"{{{XML_NS}}}mesic"))
        except (TypeError, ValueError):
            continue

        dokonceny = dump.findtext(f"{{{XML_NS}}}dokoncenyMesic") == "1"
        url = dump.findtext(f"{{{XML_NS}}}odkaz")

        if not url:
            continue

        dumps.append(
            {
                "rok": rok,
                "mesic": mesic,
                "dokonceny": dokonceny,
                "url": url,
            }
        )

    finished = [d for d in dumps if d["dokonceny"]]
    if not finished:
        raise ValueError("V indexu není žádný dump označený jako dokončený měsíc.")

    finished.sort(key=lambda d: (d["rok"], d["mesic"]), reverse=True)
    return finished[0]


def select_specific_dump(index_root: ET.Element, year: int, month: int) -> dict:
    """
    Z indexu vybere dump pro konkrétní rok+měsíc.

    Pokud dump neexistuje nebo není označený jako dokončený,
    vyhodí výjimku.
    """
    for dump in index_root.findall(f".//{{{XML_NS}}}dump"):
        try:
            rok = int(dump.findtext(f"{{{XML_NS}}}rok"))
            mesic = int(dump.findtext(f"{{{XML_NS}}}mesic"))
        except (TypeError, ValueError):
            continue

        if rok == year and mesic == month:
            dokonceny = dump.findtext(f"{{{XML_NS}}}dokoncenyMesic") == "1"
            url = dump.findtext(f"{{{XML_NS}}}odkaz")
            if not dokonceny:
                raise ValueError(f"Dump {year}-{month:02d} není označen jako dokončený.")
            if not url:
                raise ValueError(f"Dump {year}-{month:02d} nemá URL v indexu.")
            return {"rok": rok, "mesic": mesic, "url": url}

    raise ValueError(f"Dump pro {year}-{month:02d} nebyl v indexu nalezen.")


def download_dump(dump_url: str) -> Path:
    """
    Stáhne XML dump z dané URL do RAW_DIR.

    Pokud soubor už existuje, znovu ho nestahuje a pouze vrátí cestu.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    filename = dump_url.split("/")[-1]
    target_path = RAW_DIR / filename

    if target_path.exists():
        print(f"[smlouvy.gov.cz] Dump už existuje, nestahuji znovu: {target_path}")
        return target_path

    print(f"[smlouvy.gov.cz] Stahuji dump z {dump_url}")
    resp = requests.get(dump_url, stream=True, timeout=300)
    resp.raise_for_status()

    with target_path.open("wb") as f:
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)

    print(f"[smlouvy.gov.cz] Dump uložen jako: {target_path}")
    return target_path


def get_latest_dump_path() -> Path:
    """
    Vyhledá a stáhne poslední dokončený dump z Registru smluv.

    Vrací:
        Path k lokálnímu XML souboru s dumpem.
    """
    print("[smlouvy.gov.cz] Stahuji index dumpů...")
    index_root = download_index()
    latest = select_latest_finished_dump(index_root)

    rok = latest["rok"]
    mesic = latest["mesic"]
    url = latest["url"]

    print(f"[smlouvy.gov.cz] Nejnovější dokončený dump: {rok}-{mesic:02d}")
    print(f"[smlouvy.gov.cz] URL dumpu: {url}")

    dump_path = download_dump(url)
    return dump_path


def get_dump_for_year_month(year: int, month: int) -> Path:
    """
    Vyhledá a stáhne dump pro konkrétní rok a měsíc.

    Vrací:
        Path k lokálnímu XML souboru s dumpem.
    """
    if not (1 <= month <= 12):
        raise ValueError(f"Měsíc musí být v rozsahu 1-12, zadáno: {month}")
    
    print("[smlouvy.gov.cz] Stahuji index dumpů...")
    index_root = download_index()
    selected = select_specific_dump(index_root, year, month)

    rok = selected["rok"]
    mesic = selected["mesic"]
    url = selected["url"]

    print(f"[smlouvy.gov.cz] Vybraný dump: {rok}-{mesic:02d}")
    print(f"[smlouvy.gov.cz] URL dumpu: {url}")

    dump_path = download_dump(url)
    return dump_path


def parse_args() -> argparse.Namespace:
    """
    Jednoduché CLI pro samostatné použití skriptu.
    """
    parser = argparse.ArgumentParser(
        description="Stahování dumpů z Registru smluv (smlouvy.gov.cz)."
    )

    parser.add_argument("--year", type=int, help="Rok dumpu (např. 2024)")
    parser.add_argument("--month", type=int, help="Měsíc dumpu (1–12)")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.year and args.month:
        path = get_dump_for_year_month(args.year, args.month)
    elif args.year or args.month:
        print("Prosím zadej buď oba parametry --year a --month, nebo žádný.")
        path = None
    else:
        path = get_latest_dump_path()

    if path:
        print(f"Stažený dump: {path}")
