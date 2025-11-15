"""
run_pipeline.py

Hlavní "orchestrátor" datové pipeline pro tuto práci.

Cíl:
- umožnit spouštění různých scénářů sběru a obohacování dat
  pomocí jednoduchého rozhraní z příkazové řádky.

Verze 0.1:
- podporuje základní scénář: pilotní sběr dat pro jednoho zadavatele podle IČO
- zatím pouze vypisuje, jaké kroky by se provedly (bez reálného stahování dat)
"""

import argparse

from scripts.download_smlouvy_gov import get_latest_dump_path, get_dump_for_year_month



def step_1_download_tenders_for_authority(ico, year=None, month=None):

    """
    KROK 1: Získání smluv pro vybraného zadavatele (podle IČO)

    - pokud je zadán year+month, stáhne se dump pro daný měsíc
    - jinak se stáhne poslední dokončený dump

    V této verzi ještě dump pouze stahujeme; filtrování podle IČO
    doplníme v dalším kroku.
    """
    if year is not None and month is not None:
        dump_path = get_dump_for_year_month(year, month)
        label = f"{year}-{month:02d}"
    else:
        dump_path = get_latest_dump_path()
        label = "nejnovější dokončený měsíc"

    print(f"[KROK 1] Stažený dump Registru smluv ({label}): {dump_path}")
    print(f"[KROK 1] Dalším krokem bude filtrování dumpu pro IČO {ico}.")



def step_2_extract_parties_and_companies() -> None:
    """
    KROK 2: Extrakce smluvních stran a seznamu IČO firem
    ----------------------------------------------------------------
    V budoucnu:
    - načte stažené smlouvy z KROKU 1
    - z každé smlouvy vytáhne IČO zadavatele a dodavatelů
    - připraví tabulky contracts_raw a parties_raw

    Aktuálně:
    - pouze vypisuje, co by se provedlo.
    """
    print("[KROK 2] Extrakce smluvních stran a seznamu firem (TODO: implementovat).")


def step_3_enrich_companies_from_ares() -> None:
    """
    KROK 3: Obohacení údajů o firmách z ARES
    ----------------------------------------------------------------
    V budoucnu:
    - pro všechna IČO z KROKU 2 zavolá API ARES
    - uloží informace o firmách (název, právní forma, adresa, NACE)
      do tabulky companies_master

    Aktuálně:
    - pouze vypisuje, co by se provedlo.
    """
    print("[KROK 3] Obohacení firem pomocí ARES (TODO: implementovat).")


def step_4_update_neo4j() -> None:
    """
    KROK 4: Aktualizace grafové databáze Neo4j
    ----------------------------------------------------------------
    V budoucnu:
    - vezme výsledné CSV/tabulky (contracts_raw, parties_raw, companies_master)
    - převede je na uzly a hrany pro Neo4j
    - provede import / aktualizaci grafu

    Aktuálně:
    - pouze vypisuje, co by se provedlo.
    """
    print("[KROK 4] Aktualizace grafové databáze Neo4j (TODO: implementovat).")


def run_for_authority_ico(ico, year=None, month=None):

    """
    Spustí sekvenci kroků pro pilotní scénář:
    - vybraný zadavatel (IČO)
    - volitelně konkrétní rok+měsíc dumpu
    """
    print(f"Spouštím pipeline pro zadavatele s IČO {ico}...\n")
    step_1_download_tenders_for_authority(ico, year=year, month=month)
    step_2_extract_parties_and_companies()
    step_3_enrich_companies_from_ares()
    step_4_update_neo4j()
    print("\nPipeline dokončena (zatím pouze v režimu 'dry-run').")



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Datová pipeline pro sběr a obohacování dat o veřejných zakázkách."
    )

    parser.add_argument(
        "--ico",
        type=str,
        help="IČO zadavatele, pro kterého se má spustit pilotní sběr dat.",
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

    return parser.parse_args()



def main() -> None:
    args = parse_args()

    # jednoduchá validace kombinace year/month
    if (args.year is None) != (args.month is None):
        print("Prosím zadej buď oba parametry --year a --month, nebo žádný.")
        return

    if args.ico:
        run_for_authority_ico(args.ico, year=args.year, month=args.month)
    else:
        print("Nebyl zadán žádný parametr. Pro pilotní scénář použijte např.:")
        print("  python3 scripts/run_pipeline.py --ico 00023698 --year 2024 --month 9")


if __name__ == "__main__":
    main()
