# Project Summary - MBA Thesis Data Pipeline

## Přehled projektu

Datová pipeline pro sběr, extrakci, transformaci a načtení dat o veřejných zakázkách, firmách a osobách do Neo4j graph databáze. Projekt podporuje více zdrojů dat a umožňuje analýzu vztahů mezi firmami, osobami a zakázkami.

---

## 📁 Struktura projektu

```
Data/
├── data/
│   ├── tenders/              # Data ze smlouvy.gov.cz
│   │   ├── raw/              # Raw XML dumpy
│   │   └── extracted/        # Extrahované JSON soubory
│   ├── people/               # Data z RZP
│   │   ├── raw/              # Raw XML soubory
│   │   └── extracted/        # Extrahované JSON soubory
│   └── transformed/          # Data transformovaná do Neo4j formátu
├── neo4j/                    # Neo4j schema a dotazy
│   ├── schema.cypher         # Schema definice
│   ├── queries_*.cypher      # Cypher dotazy
│   └── schema_overview.md    # Dokumentace schema
├── scripts/                  # Python skripty
└── config.py                 # Konfigurace
```

---

## 🔧 Skripty

### 1. Download Scripts

#### `scripts/download_smlouvy_gov.py`
**Účel:** Stahování XML dumpů z Registru smluv (smlouvy.gov.cz)

**Funkce:**
- `download_index()` - Stáhne index dumpů
- `select_latest_finished_dump()` - Vybere nejnovější dokončený dump
- `select_specific_dump()` - Vybere dump pro konkrétní rok+měsíc
- `select_daily_dump()` - Vybere denní dump (nové)
- `select_latest_daily_dump_in_month()` - Vybere nejnovější denní dump z měsíce (nové)
- `get_dump_for_year_month(year, month, day=None)` - Stáhne dump (podporuje denní dumpy)
- `get_latest_dump_path()` - Stáhne nejnovější dump

**Výstup:** XML soubory v `data/tenders/raw/smlouvy_gov/`

**Použití:**
```bash
python3 scripts/download_smlouvy_gov.py --year 2025 --month 11
```

---

#### `scripts/download_rzp.py`
**Účel:** Stahování dat z RZP (Registr živnostenského podnikání) API

**Funkce:**
- `create_xml_query_by_ico(ico, include_details=True)` - Vytvoří XML dotaz podle IČO
- `create_xml_query_by_name(name)` - Vytvoří XML dotaz podle jména
- `create_xml_query_by_company_relation(ico)` - Vytvoří dotaz pro osoby spojené s firmou
- `download_by_ico(ico, include_details=True)` - Stáhne data podle IČO
- `download_rzp_for_ico(ico, get_details=True)` - Orchestruje stažení pro IČO

**Výstup:** XML soubory v `data/people/raw/rzp/`

**Použití:**
```bash
python3 scripts/download_rzp.py --ico 47114983
```

**Omezení:** RZP XML API neposkytuje detailní informace o statutárním orgánu automaticky. Pro získání těchto dat je potřeba stáhnout XML ručně z webu.

---

#### `scripts/download_rzp_manual.py`
**Účel:** Zkusí stáhnout detailní RZP XML pomocí ssarzp hash (zatím nefunguje)

**Použití:**
```bash
python3 scripts/download_rzp_manual.py --ssarzp <hash>
```

---

### 2. Extract Scripts

#### `scripts/extract_smlouvy_contracts.py`
**Účel:** Extrahuje strukturovaná data ze XML dumpů ze smlouvy.gov.cz

**Funkce:**
- `normalize_ico(ico)` - Normalizuje IČO (odstraní mezery, nuly)
- `extract_contract_from_zaznam(zaznam)` - Extrahuje smlouvu z XML elementu
- `extract_contracts_from_xml(xml_path, filter_ico=None)` - Extrahuje všechny smlouvy z XML
- `save_extracted_data(contracts, output_path)` - Uloží extrahovaná data do JSON
- `update_metadata(source, month_year, ico=None)` - Aktualizuje metadata pro inkrementální zpracování

**Extrahovaná data:**
- `contract_id` - ID smlouvy
- `contract_number` - Číslo smlouvy
- `subject` - Předmět smlouvy
- `contract_date` - Datum uzavření
- `published_date` - Datum zveřejnění
- `value_without_vat` - Hodnota bez DPH
- `value_with_vat` - Hodnota s DPH
- `authority` - Zadavatel (dict s ico, name, address, atd.)
- `contractor` - Dodavatel (dict s ico, name, address, atd.)
- `attachments` - Přílohy

**Výstup:** JSON soubory v `data/tenders/extracted/smlouvy_gov/`

**Použití:**
```bash
python3 scripts/extract_smlouvy_contracts.py --file data/tenders/raw/smlouvy_gov/dump_2025_11_14.xml --ico 47114983
```

---

#### `scripts/extract_rzp.py`
**Účel:** Extrahuje strukturovaná data z RZP XML souborů

**Funkce:**
- `normalize_ico(ico)` - Normalizuje IČO
- `extract_address(element, tag_name)` - Extrahuje adresu
- `extract_roles(podnikatel)` - Extrahuje vztahy (VYKONAVA_FUNKCI, VLASTNI_PODIL)
- `extract_business_fields(podnikatel)` - Extrahuje obory podnikání
- `extract_statutarni_organ_from_firma(root, xml_path)` - Extrahuje statutární orgán (podporuje 3 struktury)
- `extract_person_from_xml(xml_path)` - Hlavní funkce pro extrakci osob

**Podporované XML struktury:**
1. `StatutarniOrgan/Clen` - Standardní struktura
2. `StatutarniOrganClen/ZapsanaOsoba` - Nová struktura (přidána podpora)
3. `OsobaVeFunkci` - Detailní XML z webu

**Extrahovaná data:**
- `ico` - IČO (pokud je fyzická osoba podnikatel)
- `jmeno` - Jméno
- `prijmeni` - Příjmení
- `cele_jmeno` - Celé jméno (bez titulů)
- `datum_narozeni` - Datum narození
- `adresa` - Adresa
- `relationships` - Vztahy s firmami:
  - `type`: "VYKONAVA_FUNKCI" nebo "VLASTNI_PODIL"
  - `firma_ico` - IČO firmy
  - `role` - Role (např. "statutární orgán")
  - `platnost_od` - Datum začátku
  - `platnost_do` - Datum konce
  - `podil_procent` - Podíl v % (pro VLASTNI_PODIL)

**Výstup:** JSON soubory v `data/people/extracted/rzp/`

**Použití:**
```bash
python3 scripts/extract_rzp.py --file data/people/raw/rzp/rzp_ico_47114983.xml
```

---

### 3. Transform Scripts

#### `scripts/transform_to_neo4j.py`
**Účel:** Transformuje extrahovaná data do formátu vhodného pro Neo4j

**Třída:** `Neo4jTransformer`

**Metody:**
- `get_or_create_zdroj(...)` - Vytvoří nebo najde Zdroj node
- `get_or_create_firma(...)` - Vytvoří nebo najde Firma node (podle IČO)
- `get_or_create_zadavatel(...)` - Vytvoří nebo najde Zadavatel node
- `transform_smlouvy_contracts(...)` - Transformuje smlouvy ze smlouvy.gov.cz
- `transform_rzp_data(...)` - Transformuje RZP data
- `transform_all(...)` - Transformuje všechna data

**Vytvářené nodes:**
- **Osoba** - Osoby (z RZP)
- **Firma** - Firmy (z smluv i RZP)
- **Zadavatel** - Zadavatelé zakázek
- **Zakazka** - Veřejné zakázky
- **Zdroj** - Zdroje dat (REGISTR_SMLUV, RZP)
- **Skola** - Školy (zatím nevyužíváno)

**Vytvářené relationships:**
- **VYKONAVA_FUNKCI** - Osoba → Firma (role, platnost_od, platnost_do)
- **VLASTNI_PODIL** - Osoba → Firma (podil_procent, platnost_od, platnost_do)
- **JE_PRIDELENA** - Firma → Zakazka (smlouva_id, hodnota, platnost_od, platnost_do)
- **VYHLASUJE_ZAKAZKU** - Zadavatel → Zakazka (datum_vyhlaseni)
- **POCHAZI_Z** - Any → Zdroj (datum_ziskani)
- **PODAVA_NABIDKU** - Firma → Zakazka (zatím placeholder, není v datech)
- **STUDOVAL_NA** - Osoba → Skola (zatím placeholder)

**Výstup:** JSON soubory v `data/transformed/` (nodes_*.json, rels_*.json)

**Použití:**
```bash
python3 scripts/transform_to_neo4j.py
```

---

### 4. Load Scripts

#### `scripts/load_to_neo4j.py`
**Účel:** Načítá transformovaná data do Neo4j databáze

**Funkce:**
- `create_constraints()` - Vytvoří unique constraints a indexy
- `load_nodes()` - Načte všechny nodes
- `load_relationships()` - Načte všechny relationships
- `load_all()` - Orchestruje načtení

**Constraints:**
- `osoba_id_unique` - Osoba.osoba_id IS UNIQUE
- `firma_ico_unique` - Firma.ico IS UNIQUE
- `zadavatel_id_unique` - Zadavatel.zadavatel_id IS UNIQUE
- `zakazka_id_unique` - Zakazka.zakazka_id IS UNIQUE
- `skola_id_unique` - Skola.skola_id IS UNIQUE
- `zdroj_id_unique` - Zdroj.zdroj_id IS UNIQUE

**Indexy:**
- `osoba_jmeno_index` - Osoba(prijmeni, datum_narozeni)
- `firma_nazev_index` - Firma(nazev)
- `zakazka_rok_index` - Zakazka(rok)
- `zadavatel_nazev_index` - Zadavatel(nazev)
- `skola_nazev_mesto_index` - Skola(nazev, mesto)

**Použití:**
```bash
python3 scripts/load_to_neo4j.py
```

---

### 5. Pipeline Orchestrator

#### `scripts/run_pipeline.py`
**Účel:** Hlavní orchestrátor pro celou pipeline

**Funkce:**
- `step_1_download_dump()` - Stáhne dump
- `step_2_extract_contracts()` - Extrahuje smlouvy
- `step_3_transform_to_neo4j()` - Transformuje do Neo4j
- `step_4_load_to_neo4j()` - Načte do Neo4j
- `run_for_authority_ico(ico, year, month, ...)` - Spustí celou pipeline

**Argumenty:**
- `--ico ICO` - IČO zadavatele/dodavatele
- `--year YEAR` - Rok dumpu
- `--month MONTH` - Měsíc dumpu
- `--skip-download` - Přeskočit download
- `--skip-extract` - Přeskočit extrakci
- `--skip-transform` - Přeskočit transformaci
- `--skip-load` - Přeskočit načtení
- `--no-incremental` - Přeprocessovat i existující soubory
- `--clear-neo4j` - Vymazat Neo4j před načtením

**Použití:**
```bash
# Kompletní pipeline
python3 scripts/run_pipeline.py --ico 47114983 --year 2025 --month 11

# Pouze transform a load
python3 scripts/run_pipeline.py --ico 47114983 --skip-download --skip-extract
```

---

### 6. Utility Scripts

#### `scripts/process_manual_rzp.py`
**Účel:** Zpracuje ručně stažený RZP XML soubor (extrakce + transformace + načtení)

**Použití:**
```bash
python3 scripts/process_manual_rzp.py --file ~/Downloads/rzp_ico_47114983.xml
```

---

#### `scripts/update_firma_names.py`
**Účel:** Aktualizuje názvy firem v Neo4j z dat smlouvy

**Použití:**
```bash
python3 scripts/update_firma_names.py
```

---

## 📊 Data Schema

### Entity (Nodes)

#### Osoba
- `osoba_id` (unique) - Interní ID osoby
- `cele_jmeno` - Celé jméno
- `jmeno` - Jméno
- `prijmeni` - Příjmení
- `datum_narozeni` - Datum narození
- `statni_prislusnost` - Státní příslušnost (např. "CZ")
- `stav_zaznamu` - Stav záznamu (draft / overeny / odmitnuty)

#### Firma
- `ico` (unique) - IČO firmy
- `firma_id` - Interní ID firmy
- `nazev` - Název firmy
- `jurisdikce` - Jurisdikce (např. "CZ")
- `stav_zaznamu` - Stav záznamu

#### Zadavatel
- `zadavatel_id` (unique) - ID zadavatele
- `ico` - IČO zadavatele (pokud existuje)
- `nazev` - Název zadavatele
- `typ` - Typ zadavatele (např. "ministerstvo")
- `uroven` - Úroveň (např. "centralni")
- `jurisdikce` - Jurisdikce
- `stav_zaznamu` - Stav záznamu

#### Zakazka
- `zakazka_id` (unique) - ID zakázky
- `nazev` - Název zakázky
- `stav_zaznamu` - Stav záznamu
- `popis` - Popis zakázky
- `stav` - Stav zakázky (vypsana / probiha / ukoncena)
- `hodnota` - Hodnota zakázky
- `mena` - Měna (např. "CZK")
- `rok` - Rok zakázky
- `jurisdikce` - Jurisdikce
- `externi_id` - Externí ID zakázky

#### Zdroj
- `zdroj_id` (unique) - ID zdroje
- `nazev` - Název zdroje
- `url` - URL zdroje
- `typ` - Typ zdroje (např. "registr")
- `vydavatel` - Vydavatel
- `licence` - Licence
- `datum_ziskani` - Datum získání

#### Skola
- `skola_id` (unique) - ID školy
- `nazev` - Název školy
- `mesto` - Město
- `typ` - Typ školy (např. "univerzita")
- `obor` - Obor

---

### Relationships (Vztahy)

#### VYKONAVA_FUNKCI
- **From:** Osoba
- **To:** Firma
- **Properties:**
  - `role` - Role osoby (např. "statutární orgán", "jednatel")
  - `platnost_od` - Datum začátku platnosti
  - `platnost_do` - Datum konce platnosti
  - `zdroj_id` - ID zdroje dat

#### VLASTNI_PODIL
- **From:** Osoba
- **To:** Firma
- **Properties:**
  - `podil_procent` - Podíl v procentech
  - `platnost_od` - Datum začátku platnosti
  - `platnost_do` - Datum konce platnosti
  - `zdroj_id` - ID zdroje dat

#### JE_PRIDELENA
- **From:** Firma
- **To:** Zakazka
- **Properties:**
  - `smlouva_id` - ID smlouvy
  - `platnost_od` - Datum začátku platnosti
  - `platnost_do` - Datum konce platnosti
  - `hodnota` - Hodnota smlouvy
  - `mena` - Měna
  - `zdroj_id` - ID zdroje dat

#### VYHLASUJE_ZAKAZKU
- **From:** Zadavatel
- **To:** Zakazka
- **Properties:**
  - `datum_vyhlaseni` - Datum vyhlášení zakázky
  - `zdroj_id` - ID zdroje dat

#### POCHAZI_Z
- **From:** Any (Osoba, Firma, Zadavatel, Zakazka)
- **To:** Zdroj
- **Properties:**
  - `datum_ziskani` - Datum získání dat

#### PODAVA_NABIDKU
- **From:** Firma
- **To:** Zakazka
- **Properties:**
  - `datum_podani` - Datum podání nabídky
  - `nabidkova_cena` - Nabídková cena
  - `mena` - Měna
  - `zdroj_id` - ID zdroje dat
- **Status:** Placeholder (není v datech ze smlouvy.gov.cz)

#### STUDOVAL_NA
- **From:** Osoba
- **To:** Skola
- **Properties:**
  - `obor` - Obor studia
  - `od` - Datum začátku studia
  - `do` - Datum konce studia
  - `zdroj_id` - ID zdroje dat
- **Status:** Placeholder (zatím nevyužíváno)

---

## 📁 Data Sources

### 1. smlouvy.gov.cz (REGISTR_SMLUV)
**Typ:** Veřejné zakázky a smlouvy

**Data:**
- Zakázky (Zakazka nodes)
- Zadavatelé (Zadavatel nodes)
- Dodavatelé (Firma nodes)
- Vztahy: VYHLASUJE_ZAKAZKU, JE_PRIDELENA

**Stažení:**
- Denní nebo měsíční XML dumpy
- URL: `https://data.smlouvy.gov.cz/`

**Extrakce:**
- Parsování XML s namespace `http://portal.gov.cz/rejstriky/ISRS/1.2/`
- Normalizace IČO
- Extrakce hodnot, datumů, subjektů

---

### 2. RZP (Registr živnostenského podnikání)
**Typ:** Informace o podnikatelích a statutárních orgánech

**Data:**
- Osoby (Osoba nodes)
- Firmy (Firma nodes)
- Vztahy: VYKONAVA_FUNKCI, VLASTNI_PODIL

**Stažení:**
- XML API: `https://rzp.gov.cz/rzp/api3-c/srv/vw/v31/vwinterface/xml`
- Pro detailní data (statutární orgán): ruční stažení z webu

**Extrakce:**
- Parsování XML s namespace `urn:cz:isvs:rzp:schemas:VerejnaCast:v1`
- Podpora 3 různých XML struktur
- Odstranění titulů (Mgr., Ing., atd.)

---

## 🔍 Neo4j Queries

### Soubory s dotazy:
- `neo4j/queries_firma.cypher` - Dotazy pro entitu Firma
- `neo4j/queries_osoba.cypher` - Dotazy pro entitu Osoba
- `neo4j/queries_schema.cypher` - Dotazy pro schema (entity a vztahy s atributy)
- `neo4j/queries_zakazky_ceska_posta.cypher` - Dotazy pro zakázky České pošty
- `neo4j/visualization_ceska_posta.cypher` - Vizualizační dotazy

### Dokumentace:
- `neo4j/schema_overview.md` - Přehled schema (entity a vztahy)
- `neo4j/schema.cypher` - Schema definice (constraints, indexy)

---

## 📈 Aktuální stav dat

**Nodes:**
- 135 Osoba
- 148 Firma
- 31 Zadavatel
- 346 Zakazka
- 2 Zdroj

**Relationships:**
- 1466 VYKONAVA_FUNKCI
- 346 JE_PRIDELENA
- 346 VYHLASUJE_ZAKAZKU
- 4889 POCHAZI_Z

**Celkem:** 662 nodes, 7047 relationships

---

## 🚀 Workflow

### Pro smlouvy.gov.cz:
```bash
# 1. Stáhnout dump
python3 scripts/download_smlouvy_gov.py --year 2025 --month 11

# 2. Extrahovat
python3 scripts/extract_smlouvy_contracts.py --file data/tenders/raw/smlouvy_gov/dump_2025_11_14.xml --ico 47114983

# 3. Transformovat
python3 scripts/transform_to_neo4j.py

# 4. Načíst do Neo4j
python3 scripts/load_to_neo4j.py
```

### Pro RZP (ručně stažené XML):
```bash
# Automaticky provede všechny kroky
python3 scripts/process_manual_rzp.py --file ~/Downloads/rzp_ico_47114983.xml
```

### Kompletní pipeline:
```bash
python3 scripts/run_pipeline.py --ico 47114983 --year 2025 --month 11
```

---

## 📝 Poznámky

### RZP - Manuální stažení
Pro získání detailních dat o statutárním orgánu z RZP je potřeba:
1. Otevřít: `https://rzp.gov.cz/verejne-udaje/cs/udaje/vyber-subjektu;ico=XXXXX;roleSubjektu=P`
2. Kliknout na "Údaje s historií"
3. Stáhnout XML ze stránky
4. Použít `process_manual_rzp.py` pro zpracování

### Denní vs. měsíční dumpy
- Index obsahuje denní dumpy (každý den má svůj dump)
- `get_dump_for_year_month()` nyní podporuje parametr `day` pro denní dumpy
- Pokud není zadán den, použije se nejnovější denní dump z měsíce

### Duplikace
- Firma nodes jsou deduplikovány podle IČO
- Osoba nodes jsou deduplikovány podle `osoba_id`
- Relationships používají MERGE pro zabránění duplikátům

---

## 🔗 Související dokumenty

- `README.md` - Základní informace o projektu
- `ARCHITECTURE.md` - Architektura projektu
- `CHECKLIST_NEXT_SOURCE.md` - Checklist pro přidání nového zdroje
- `RZP_MANUAL_DOWNLOAD.md` - Návod pro ruční stažení RZP dat

