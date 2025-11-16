# Checklist: Přidání dalšího zdroje dat

## ✅ Co je připravené:

### 1. **Schéma (Neo4j)**
- ✅ Všechny node types: `Osoba`, `Firma`, `Zadavatel`, `Zakazka`, `Zdroj`, `Skola`
- ✅ Všechny relationship types: `VYKONAVA_FUNKCI`, `VLASTNI_PODIL`, `PODAVA_NABIDKU`, `JE_PRIDELENA`, `STUDOVAL_NA`, `POCHAZI_Z`, `VYHLASUJE_ZAKAZKU`
- ✅ Constraints a indexy jsou vytvořené
- ✅ `Zdroj` node pro tracking zdrojů dat

### 2. **Transform Script** (`transform_to_neo4j.py`)
- ✅ Podporuje více zdrojů - metoda `transform_all()` může zpracovat více souborů
- ✅ Automatické vytváření `Zdroj` nodes
- ✅ Propojení entit se zdroji přes `POCHAZI_Z`
- ✅ Všechny relationship types jsou definované a připravené

### 3. **Load Script** (`load_to_neo4j.py`)
- ✅ Obecný - podporuje všechny node types a relationships
- ✅ Používá MERGE pro inkrementální aktualizace
- ✅ Správné mapování ID polí (ico, zadavatel_id, zakazka_id, etc.)

### 4. **Pipeline** (`run_pipeline.py`)
- ✅ Modulární struktura (download → extract → transform → load)
- ✅ Podporuje skip flags pro flexibilní workflow
- ✅ Inkrementální režim

## 📝 Co bude potřeba pro nový zdroj:

### Krok 1: Download Script
Vytvořit `scripts/download_NOVY_ZDROJ.py`:
```python
def download_data(year=None, month=None):
    # Stáhnout data z nového zdroje
    # Uložit do data/tenders/raw/NOVY_ZDROJ/ nebo data/companies/raw/NOVY_ZDROJ/
    pass
```

### Krok 2: Extract Script
Vytvořit `scripts/extract_NOVY_ZDROJ.py`:
```python
def extract_data(input_path, filter_ico=None):
    # Parsovat raw data (XML, JSON, CSV, HTML, etc.)
    # Extrahovat strukturovaná data
    # Uložit do data/tenders/extracted/NOVY_ZDROJ/ nebo data/companies/extracted/NOVY_ZDROJ/
    # Formát: JSON s konzistentní strukturou
    pass
```

### Krok 3: Transform Method
Přidat do `transform_to_neo4j.py`:
```python
def transform_NOVY_ZDROJ(self, file_path, zdroj_id: str, filter_ico=None):
    """
    Transformuje data z NOVY_ZDROJ do Neo4j formátu.
    
    Vytvoří:
    - Nodes (Firma, Zadavatel, Zakazka, Osoba, Skola - podle dat)
    - Relationships (podle dostupných dat)
    - Propojení se Zdroj přes POCHAZI_Z
    """
    # Načíst extrahovaná data
    # Vytvořit nodes
    # Vytvořit relationships
    # Propojit se Zdroj
    pass
```

A přidat volání do `transform_all()`:
```python
# Transform nový zdroj
extracted_dir = Path(__file__).parent.parent / "data" / "tenders" / "extracted" / "NOVY_ZDROJ"
if extracted_dir.exists():
    files = list(extracted_dir.glob("*.json"))
    for file in files:
        self.transform_NOVY_ZDROJ(str(file), zdroj_id, filter_ico=filter_ico)
```

### Krok 4: Vytvořit Zdroj Node
V `transform_all()`:
```python
zdroj_novy = self.get_or_create_zdroj(
    "NOVY_ZDROJ_ID",
    "Název nového zdroje",
    "https://url-zdroje.cz",
    "typ_zdroje"  # registr, api, scraper, etc.
)
```

### Krok 5: (Volitelné) Aktualizovat Pipeline
V `run_pipeline.py` přidat podporu pro nový zdroj:
```python
def step_1_download_NOVY_ZDROJ(year=None, month=None):
    # Download logic
    pass

def step_2_extract_NOVY_ZDROJ(dump_path, ico=None):
    # Extract logic
    pass
```

## 🎯 Příklad: Přidání VVZ (Věstník veřejných zakázek)

### 1. Download
```python
# scripts/download_vvz.py
def download_vvz_tenders(year=None, month=None):
    # Stáhnout tendry z VVZ
    # Uložit do data/tenders/raw/vvz/
```

### 2. Extract
```python
# scripts/extract_vvz.py
def extract_vvz_tenders(html_path, filter_ico=None):
    # Parsovat HTML/PDF z VVZ
    # Extrahovat: zadavatel, dodavatel, hodnota, datum, nabídky
    # Uložit do data/tenders/extracted/vvz/
```

### 3. Transform
```python
# V transform_to_neo4j.py
def transform_vvz_tenders(self, file_path, zdroj_id: str, filter_ico=None):
    # Vytvořit Zakazka nodes
    # Vytvořit Zadavatel nodes
    # Vytvořit Firma nodes (z nabídek)
    # Vytvořit VYHLASUJE_ZAKAZKU relationships
    # Vytvořit PODAVA_NABIDKU relationships (nové!)
    # Vytvořit JE_PRIDELENA relationships (pokud je známý vítěz)
```

## ✅ Testování nového zdroje

1. **Test download:**
   ```bash
   python3 scripts/download_NOVY_ZDROJ.py --year 2024 --month 11
   ```

2. **Test extract:**
   ```bash
   python3 scripts/extract_NOVY_ZDROJ.py --ico 70886288
   ```

3. **Test transform:**
   ```bash
   python3 scripts/transform_to_neo4j.py --ico 70886288
   ```

4. **Test load:**
   ```bash
   python3 scripts/load_to_neo4j.py
   ```

5. **Test celý pipeline:**
   ```bash
   python3 scripts/run_pipeline.py --ico 70886288
   ```

## 📊 Co funguje automaticky:

- ✅ **Deduplikace** - Firma nodes se deduplikují podle IČO
- ✅ **Zdroj tracking** - Všechny entity jsou propojené se Zdroj
- ✅ **Inkrementální updates** - MERGE v Neo4j zajišťuje, že se data nepřepisují
- ✅ **Filtrování podle IČO** - Funguje na všech úrovních

## 🎉 Závěr

**Ano, vše je připravené!** Pro přidání nového zdroje stačí:
1. Vytvořit download script
2. Vytvořit extract script  
3. Přidat transform metodu
4. Vytvořit Zdroj node

Transform a Load skripty jsou obecné a podporují všechny node types a relationships z tvého schématu.

