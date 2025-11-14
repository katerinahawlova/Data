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


def step_1_download_tenders_for_authority(ico: str) -> None:
    """
    KROK 1: Získání smluv pro vybraného zadavatele (podle IČO)
    ----------------------------------------------------------------
    V budoucnu:
    - zde bude volání logiky pro Registr smluv (nebo jiný zdroj)
    - funkce stáhne smlouvy pro dané IČO (zadavatel)
    - uloží je do struktury data/tenders/ ve formátu vhodném pro další zpracování

    Aktuálně:
    - pouze vypisuje, co by se provedlo.
    """
    print(f"[KROK 1] Získání smluv pro zadavatele s IČO {ico} (TODO: implementovat).")


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


def run_for_authority_ico(ico: str) -> None:
    """
    Spustí sekvenci kroků pro pilotní scénář:
    - vybraný zadavatel (IČO)
    - stažení smluv, extrakce firem, obohacení ARES, Neo4j
    """
    print(f"Spouštím pipeline pro zadavatele s IČO {ico}...\n")
    step_1_download_tenders_for_authority(ico)
    step_2_extract_parties_and_companies()
    step_3_enrich_companies_from_ares()
    step_4_update_neo4j()
    print("\nPipeline dokončena (zatím pouze v režimu 'dry-run').")


def parse_args() -> argparse.Namespace:
    """
    Zpracuje argumenty z příkazové řádky.

    Verze 0.1:
    - podporuje pouze parametr --ico pro pilotní scénář
    """
    parser = argparse.ArgumentParser(
        description="Datová pipeline pro sběr a obohacování dat o veřejných zakázkách."
    )

    parser.add_argument(
        "--ico",
        type=str,
        help="IČO zadavatele, pro kterého se má spustit pilotní sběr dat.",
    )

    # do budoucna sem můžeme přidávat další módy:
    # --company-name, --tender-id, --mode atd.

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.ico:
        run_for_authority_ico(args.ico)
    else:
        # v budoucnu můžeme dopsat nápovědu nebo interaktivní režim
        print("Nebyl zadán žádný parametr. Pro pilotní scénář použijte např.:")
        print("  python scripts/run_pipeline.py --ico 00023698")


if __name__ == "__main__":
    main()
