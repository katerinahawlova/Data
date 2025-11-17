# RZP - Manuální stažení detailního XML

## Problém

RZP XML API neposkytuje detailní informace včetně statutárního orgánu automaticky. Pro získání těchto dat je potřeba stáhnout XML ručně z webového rozhraní.

## Postup

### Krok 1: Stáhnout XML ručně

1. Otevři: `https://rzp.gov.cz/verejne-udaje/cs/udaje/vyber-subjektu;ico=47114983;roleSubjektu=P`
2. Klikni na **"Údaje s historií"**
3. Na stránce najdi tlačítko **"Stáhnout údaje"** (obvykle dole na stránce)
4. Ulož XML soubor (např. `rzp_47114983_detail.xml`)

### Krok 2: Zpracovat XML (jednoduchý způsob)

```bash
# Automaticky provede extrakci, transformaci a načtení do Neo4j
python3 scripts/process_manual_rzp.py --file ~/Downloads/rzp_ico_47114983.xml
```

**Nebo ručně krok po kroku:**

```bash
# 2a. Extrahovat strukturovaná data
python3 scripts/extract_rzp.py --file ~/Downloads/rzp_ico_47114983.xml

# 2b. Transformovat do Neo4j formátu (automaticky zahrnuje RZP data)
python3 scripts/transform_to_neo4j.py

# 2c. Načíst do Neo4j
python3 scripts/load_to_neo4j.py
```

**Poznámka:** XML soubor by měl mít v názvu `ico_XXXXX`, aby se správně identifikovalo IČO firmy.

## Co se vytvoří

Z detailního XML se extrahují:
- **Osoba** nodes pro členy statutárního orgánu
- **VYKONAVA_FUNKCI** relationships (Osoba → Firma) s role "statutární orgán"
- Datumy platnosti funkcí (platnost_od, platnost_do)

## Alternativní řešení

Pokud potřebuješ automatizovat stažení detailního XML, můžeš použít:
- **Selenium** pro web scraping (vyžaduje instalaci)
- **Obchodní rejstřík** jako alternativní zdroj dat o statutárním orgánu

## Poznámka

Extract script (`extract_rzp.py`) je připravený na zpracování detailního XML s statutárním orgánem. Stačí mu poskytnout správně stažený XML soubor.

