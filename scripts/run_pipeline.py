"""
run_pipeline.py

Hlavní "orchestrátor" datové pipeline pro tuto práci.

Cíl:
- umožnit spouštění různých scénářů sběru a obohacování dat
  pomocí jednoduchého rozhraní z příkazové řádky.

Verze 0.2:
- podporuje kompletní pipeline: download → extract → transform → load
- podporuje filtrování podle IČO
- podporuje inkrementální aktualizace
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.download_smlouvy_gov import get_latest_dump_path, get_dump_for_year_month, RAW_DIR
from scripts.extract_smlouvy_contracts import extract_dump, extract_latest_dump, extract_dump_for_month
from scripts.transform_to_neo4j import Neo4jTransformer

# Lazy import for Neo4j (optional dependency)
try:
    from scripts.load_to_neo4j import Neo4jLoader
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    Neo4jLoader = None



def step_1_download_dump(year=None, month=None):
    """
    KROK 1: Stažení XML dumpu z Registru smluv.

    - pokud je zadán year+month, stáhne se dump pro daný měsíc
    - jinak se stáhne poslední dokončený dump
    """
    if year is not None and month is not None:
        dump_path = get_dump_for_year_month(year, month)
        label = f"{year}-{month:02d}"
    else:
        dump_path = get_latest_dump_path()
        label = "nejnovější dokončený měsíc"

    print(f"[KROK 1] ✓ Stažený dump Registru smluv ({label}): {dump_path.name}")
    return dump_path



def step_2_extract_contracts(dump_path: Path, ico=None, incremental=True) -> Path:
    """
    KROK 2: Extrakce smluv z XML dumpu.

    - parsuje XML dump
    - extrahuje informace o smlouvách (zadavatel, dodavatel, hodnota, datum)
    - volitelně filtruje podle IČO
    - ukládá do strukturovaného JSON formátu
    """
    print(f"[KROK 2] Extrahuji smlouvy z {dump_path.name}...")
    
    if ico:
        print(f"[KROK 2] Filtruji podle IČO: {ico}")
    
    extracted_path = extract_dump(dump_path, filter_ico=ico, incremental=incremental)
    print(f"[KROK 2] ✓ Extrahováno do: {extracted_path.name}")
    return extracted_path


def step_3_transform_to_neo4j(ico=None):
    """
    KROK 3: Transformace dat do Neo4j formátu.

    - načte extrahované smlouvy
    - vytvoří Company nodes (z authority a contractor)
    - vytvoří Contract/Tender nodes
    - vytvoří relationships (CONTRACTED_WITH, PUBLISHED_CONTRACT, WON_CONTRACT)
    """
    print("[KROK 3] Transformuji data do Neo4j formátu...")
    
    transformer = Neo4jTransformer()
    transformer.transform_all(filter_ico=ico)
    
    print("[KROK 3] ✓ Transformace dokončena")


def step_4_load_to_neo4j(clear_first=False):
    """
    KROK 4: Načtení dat do Neo4j databáze.

    - připojí se k Neo4j databázi
    - vytvoří constraints/indexy
    - načte nodes a relationships z transformovaných dat
    - použije MERGE pro inkrementální aktualizace
    """
    if not NEO4J_AVAILABLE:
        print("[KROK 4] ⚠ Neo4j není dostupný (modul neo4j není nainstalován)")
        print("[KROK 4]   Pro načtení dat do Neo4j nainstalujte: pip install neo4j")
        return
    
    print("[KROK 4] Načítám data do Neo4j...")
    
    loader = Neo4jLoader()
    loader.load_all(clear_first=clear_first)
    
    print("[KROK 4] ✓ Data načtena do Neo4j")


def run_for_authority_ico(ico, year=None, month=None, incremental=True, skip_download=False, skip_extract=False, skip_transform=False, skip_load=False, clear_neo4j=False):
    """
    Spustí kompletní pipeline pro vybraného zadavatele (IČO):
    
    1. Download: Stáhne XML dump z smlouvy.gov.cz
    2. Extract: Extrahuje smlouvy z XML (volitelně filtrováno podle IČO)
    3. Transform: Transformuje do Neo4j formátu
    4. Load: Načte data do Neo4j databáze
    
    Args:
        ico: IČO zadavatele (pro filtrování)
        year: Rok dumpu (volitelné)
        month: Měsíc dumpu (volitelné)
        incremental: Použít inkrementální režim (přeskočit existující soubory)
        skip_download: Přeskočit download (použít existující dump)
        skip_extract: Přeskočit extract (použít existující extrakce)
        skip_transform: Přeskočit transform (použít existující transformace)
        skip_load: Přeskočit load do Neo4j
        clear_neo4j: Vymazat Neo4j databázi před načtením
    """
    print(f"═══════════════════════════════════════════════════════════")
    print(f"Spouštím pipeline pro zadavatele s IČO: {ico}")
    if year and month:
        print(f"Pro období: {year}-{month:02d}")
    print(f"═══════════════════════════════════════════════════════════\n")
    
    # KROK 1: Download
    if not skip_download:
        dump_path = step_1_download_dump(year=year, month=month)
    else:
        # Najít nejnovější dump
        dump_files = sorted(RAW_DIR.glob("dump_*.xml"), reverse=True)
        if not dump_files:
            print("❌ Chyba: Nenalezen žádný dump. Spusťte bez --skip-download.")
            return
        dump_path = dump_files[0]
        print(f"[KROK 1] ⏭ Přeskakuji download, používám: {dump_path.name}")
    
    # KROK 2: Extract
    if not skip_extract:
        extracted_path = step_2_extract_contracts(dump_path, ico=ico, incremental=incremental)
    else:
        print("[KROK 2] ⏭ Přeskakuji extract")
    
    # KROK 3: Transform
    if not skip_transform:
        step_3_transform_to_neo4j(ico=ico)
    else:
        print("[KROK 3] ⏭ Přeskakuji transform")
    
    # KROK 4: Load
    if not skip_load:
        step_4_load_to_neo4j(clear_first=clear_neo4j)
    else:
        print("[KROK 4] ⏭ Přeskakuji load do Neo4j")
    
    print("\n" + "="*55)
    print("✓ Pipeline dokončena!")
    print("="*55)



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Datová pipeline pro sběr a obohacování dat o veřejných zakázkách.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Příklady použití:

  # Kompletní pipeline pro IČO (nejnovější měsíc)
  python3 scripts/run_pipeline.py --ico 70886288

  # Kompletní pipeline pro konkrétní měsíc
  python3 scripts/run_pipeline.py --ico 70886288 --year 2025 --month 11

  # Pouze transform a load (přeskočit download/extract)
  python3 scripts/run_pipeline.py --ico 70886288 --skip-download --skip-extract

  # Vymazat Neo4j před načtením
  python3 scripts/run_pipeline.py --ico 70886288 --clear-neo4j
        """
    )

    parser.add_argument(
        "--ico",
        type=str,
        help="IČO zadavatele/dodavatele pro filtrování smluv.",
    )

    parser.add_argument(
        "--year",
        type=int,
        help="Rok dumpu z Registru smluv (např. 2024). Volitelné.",
    )

    parser.add_argument(
        "--month",
        type=int,
        help="Měsíc dumpu z Registru smluv (1–12). Volitelné.",
    )

    parser.add_argument(
        "--no-incremental",
        action="store_true",
        help="Přeprocessovat i když už soubory existují (vypne inkrementální režim)."
    )

    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Přeskočit download (použít existující dump)."
    )

    parser.add_argument(
        "--skip-extract",
        action="store_true",
        help="Přeskočit extract (použít existující extrakce)."
    )

    parser.add_argument(
        "--skip-transform",
        action="store_true",
        help="Přeskočit transform (použít existující transformace)."
    )

    parser.add_argument(
        "--skip-load",
        action="store_true",
        help="Přeskočit load do Neo4j."
    )

    parser.add_argument(
        "--clear-neo4j",
        action="store_true",
        help="Vymazat Neo4j databázi před načtením (POZOR: smaže všechna data!)."
    )

    return parser.parse_args()



def main() -> None:
    args = parse_args()

    # jednoduchá validace kombinace year/month
    if (args.year is None) != (args.month is None):
        print("❌ Chyba: Prosím zadej buď oba parametry --year a --month, nebo žádný.")
        return

    if args.ico:
        run_for_authority_ico(
            args.ico,
            year=args.year,
            month=args.month,
            incremental=not args.no_incremental,
            skip_download=args.skip_download,
            skip_extract=args.skip_extract,
            skip_transform=args.skip_transform,
            skip_load=args.skip_load,
            clear_neo4j=args.clear_neo4j
        )
    else:
        print("❌ Nebyl zadán parametr --ico")
        print("\nPro spuštění pipeline použijte např.:")
        print("  python3 scripts/run_pipeline.py --ico 70886288")
        print("  python3 scripts/run_pipeline.py --ico 70886288 --year 2025 --month 11")
        print("\nPro nápovědu: python3 scripts/run_pipeline.py --help")


if __name__ == "__main__":
    main()
