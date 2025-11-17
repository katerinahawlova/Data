# RZP Integrace - Implementováno ✅

## Co bylo vytvořeno:

### 1. **Download Script** (`scripts/download_rzp.py`)
- ✅ Stahování dat z RZP API podle IČO nebo názvu
- ✅ XML dotazy v encoding ISO-8859-2
- ✅ Ukládání do `data/people/raw/rzp/`

### 2. **Extract Script** (`scripts/extract_rzp.py`)
- ✅ Parsování XML odpovědí z RZP
- ✅ Extrakce informací o osobách (živnostnících)
- ✅ Extrakce vazeb mezi osobami a firmami
- ✅ Ukládání do JSON formátu v `data/people/extracted/rzp/`

### 3. **Transform Method** (`transform_to_neo4j.py`)
- ✅ `transform_rzp_data()` metoda
- ✅ Vytváří `Osoba` nodes
- ✅ Vytváří `VYKONAVA_FUNKCI` relationships (Osoba → Firma)
- ✅ Vytváří `VLASTNI_PODIL` relationships (Osoba → Firma)
- ✅ Propojuje se `Zdroj` node přes `POCHAZI_Z`
- ✅ Automaticky voláno v `transform_all()`

## Jak použít:

### Krok 1: Stáhnout data z RZP
```bash
# Podle IČO
python3 scripts/download_rzp.py --ico 70886288

# Podle názvu
python3 scripts/download_rzp.py --name "Jan Novák"
```

### Krok 2: Extrahovat strukturovaná data
```bash
# Z konkrétního souboru
python3 scripts/extract_rzp.py --file data/people/raw/rzp/rzp_ico_70886288.xml

# Všechny soubory
python3 scripts/extract_rzp.py --all

# S filtrováním podle IČO
python3 scripts/extract_rzp.py --all --ico 70886288
```

### Krok 3: Transformovat do Neo4j
```bash
# Transformovat všechna data (včetně RZP)
python3 scripts/transform_to_neo4j.py

# S filtrováním podle IČO
python3 scripts/transform_to_neo4j.py --ico 70886288
```

### Krok 4: Načíst do Neo4j
```bash
python3 scripts/load_to_neo4j.py
```

## Co se vytvoří v Neo4j:

### Nodes:
- **Osoba** - živnostníci z RZP
- **Firma** - firmy, se kterými jsou osoby propojené (pokud ještě neexistují)
- **Zdroj** - node "RZP" pro tracking zdroje dat

### Relationships:
- **VYKONAVA_FUNKCI** (Osoba → Firma)
  - `role`: "jednatel", "společník", "statutární orgán", atd.
  - `platnost_od`, `platnost_do`
  - `zdroj_id`: "RZP"

- **VLASTNI_PODIL** (Osoba → Firma)
  - `podil_procent`: procento podílu
  - `platnost_od`, `platnost_do`
  - `zdroj_id`: "RZP"

- **POCHAZI_Z** (Osoba → Zdroj)
  - Propojení se Zdroj node "RZP"

## Integrace s existujícími daty:

RZP data se automaticky propojí s existujícími daty:
- Pokud `Firma` node už existuje (z `smlouvy.gov.cz`), použije se existující
- Pokud neexistuje, vytvoří se nový `Firma` node s IČO
- Všechny entity jsou propojené se svými `Zdroj` nodes

## Poznámky:

- RZP API vyžaduje XML dotazy v encoding **ISO-8859-2**
- API může vrátit více výsledků pro jeden dotaz
- Některá data nemusí být v RZP dostupná (např. název firmy)
- Transform script automaticky vytváří `Zdroj` node "RZP" při prvním použití

## Testování:

```bash
# Kompletní test workflow
python3 scripts/download_rzp.py --ico 70886288
python3 scripts/extract_rzp.py --all --ico 70886288
python3 scripts/transform_to_neo4j.py --ico 70886288
python3 scripts/load_to_neo4j.py
```

## Co dál:

RZP integrace je připravená a otestovaná. Můžeš:
1. Stáhnout data pro konkrétní IČO
2. Extrahovat a transformovat
3. Načíst do Neo4j
4. Propojit s existujícími daty z `smlouvy.gov.cz`

Všechny vztahy z tvého schématu jsou nyní podporované! 🎉

