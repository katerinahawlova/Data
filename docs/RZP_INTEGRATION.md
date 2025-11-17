# Integrace RZP (Registr živnostenského podnikání)

## Přehled zdroje

**RZP (Registr živnostenského podnikání)** - [rzp.gov.cz](https://rzp.gov.cz)

### Co RZP obsahuje:
- ✅ **Informace o živnostnících** (fyzické osoby)
- ✅ **Vazby osob na firmy** (jednatel, společník, statutární orgán)
- ✅ **Oblasti podnikání** (obory živnosti)
- ✅ **Adresy sídla a provozoven**
- ✅ **IČO a další identifikátory**

### API informace:
- **URL:** `https://rzp.gov.cz/rzp/api3-c/srv/vw/v31/vwinterface/xml`
- **Metoda:** HTTP POST s XML
- **Dokumentace:** [RZP02_XML_31.pdf](https://rzp.gov.cz/docs/RZP02_XML_31.pdf)

## Jak RZP zapadá do schématu

### Nodes, které můžeme vytvořit:

1. **Osoba** nodes
   - `osoba_id` - unikátní ID
   - `cele_jmeno`, `jmeno`, `prijmeni`
   - `datum_narozeni` (pokud je v RZP)
   - `statni_prislusnost` = "CZ"
   - `stav_zaznamu` = "overeny"

2. **Firma** nodes (pokud ještě neexistují)
   - `ico` - z RZP
   - `nazev` - název podnikatele
   - `jurisdikce` = "CZ"
   - `stav_zaznamu` = "overeny"

### Relationships, které můžeme vytvořit:

1. **VYKONAVA_FUNKCI** (Osoba → Firma)
   - `role` - "jednatel", "společník", "statutární orgán", atd.
   - `platnost_od` - datum začátku
   - `platnost_do` - datum konce (pokud je ukončeno)
   - `zdroj_id` = "RZP"

2. **VLASTNI_PODIL** (Osoba → Firma)
   - `podil_procent` - pokud je v RZP
   - `platnost_od`, `platnost_do`
   - `zdroj_id` = "RZP"

3. **POCHAZI_Z** (Osoba → Zdroj, Firma → Zdroj)
   - Propojení se Zdroj node "RZP"

## Implementační plán

### Krok 1: Download Script (`scripts/download_rzp.py`)

```python
"""
Download data from RZP (Registr živnostenského podnikání).

RZP API: https://rzp.gov.cz/rzp/api3-c/srv/vw/v31/vwinterface/xml
Metoda: HTTP POST s XML dotazem
"""

import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List, Dict

RZP_API_URL = "https://rzp.gov.cz/rzp/api3-c/srv/vw/v31/vwinterface/xml"
RZP_NS = "urn:cz:isvs:rzp:schemas:VerejnaCast:v1"

def download_by_ico(ico: str) -> Dict:
    """
    Stáhne data o podnikateli podle IČO.
    
    Args:
        ico: IČO podnikatele (8 číslic)
    
    Returns:
        XML response jako dictionary
    """
    # Vytvořit XML dotaz
    xml_query = f"""<?xml version="1.0" encoding="ISO-8859-2"?>
<VerejnyWebDotaz xmlns="{RZP_NS}">
    <Kriteria>
        <IdentifikacniCislo>{ico}</IdentifikacniCislo>
    </Kriteria>
</VerejnyWebDotaz>"""
    
    # Odeslat POST request
    response = requests.post(
        RZP_API_URL,
        data=xml_query.encode('iso-8859-2'),
        headers={'Content-Type': 'text/xml; charset=iso-8859-2'}
    )
    
    response.raise_for_status()
    return ET.fromstring(response.content)

def download_by_name(name: str) -> Dict:
    """
    Stáhne data podle názvu podnikatele.
    """
    xml_query = f"""<?xml version="1.0" encoding="ISO-8859-2"?>
<VerejnyWebDotaz xmlns="{RZP_NS}">
    <Kriteria>
        <Nazev>{name}</Nazev>
    </Kriteria>
</VerejnyWebDotaz>"""
    
    response = requests.post(
        RZP_API_URL,
        data=xml_query.encode('iso-8859-2'),
        headers={'Content-Type': 'text/xml; charset=iso-8859-2'}
    )
    
    response.raise_for_status()
    return ET.fromstring(response.content)

def save_rzp_data(data: ET.Element, output_path: Path):
    """Uloží XML odpověď do souboru."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree = ET.ElementTree(data)
    tree.write(output_path, encoding='iso-8859-2', xml_declaration=True)
```

### Krok 2: Extract Script (`scripts/extract_rzp.py`)

```python
"""
Extract structured data from RZP XML responses.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import json
from typing import Optional, Dict, List

RZP_NS = "urn:cz:isvs:rzp:schemas:VerejnaCast:v1"

def extract_person_from_xml(xml_path: Path) -> List[Dict]:
    """
    Extrahuje informace o osobách z RZP XML.
    
    Vrací seznam osob s jejich vazbami na firmy.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    persons = []
    
    # Najít všechny podnikatele
    for podnikatel in root.findall(f".//{{{RZP_NS}}}Podnikatel"):
        # Extrahovat informace o osobě
        osoba = {
            "jmeno": podnikatel.findtext(f"{{{RZP_NS}}}Jmeno", ""),
            "prijmeni": podnikatel.findtext(f"{{{RZP_NS}}}Prijmeni", ""),
            "datum_narozeni": podnikatel.findtext(f"{{{RZP_NS}}}DatumNarozeni", ""),
            "ico": podnikatel.findtext(f"{{{RZP_NS}}}IdentifikacniCislo", ""),
            "adresa": extract_address(podnikatel),
            "role": extract_roles(podnikatel),  # Vazby na firmy
            "obory": extract_business_fields(podnikatel)
        }
        persons.append(osoba)
    
    return persons

def extract_company_relationships(podnikatel: ET.Element) -> List[Dict]:
    """
    Extrahuje vztahy mezi osobou a firmami.
    
    Vrací seznam vztahů:
    - VYKONAVA_FUNKCI (jednatel, společník, atd.)
    - VLASTNI_PODIL (pokud je v RZP)
    """
    relationships = []
    
    # Najít vazby na firmy (společníci, jednatelé, atd.)
    for vazba in podnikatel.findall(f".//{{{RZP_NS}}}Vazba"):
        firma_ico = vazba.findtext(f"{{{RZP_NS}}}IdentifikacniCislo", "")
        role = vazba.findtext(f"{{{RZP_NS}}}Role", "")
        platnost_od = vazba.findtext(f"{{{RZP_NS}}}PlatnostOd", "")
        platnost_do = vazba.findtext(f"{{{RZP_NS}}}PlatnostDo", "")
        
        relationships.append({
            "firma_ico": firma_ico,
            "role": role,
            "platnost_od": platnost_od,
            "platnost_do": platnost_do,
            "type": "VYKONAVA_FUNKCI"
        })
    
    return relationships
```

### Krok 3: Transform Method (`transform_to_neo4j.py`)

```python
def transform_rzp_data(self, file_path, zdroj_id: str, filter_ico=None):
    """
    Transformuje data z RZP do Neo4j formátu.
    
    Vytvoří:
    - Osoba nodes (živnostníci)
    - Firma nodes (pokud ještě neexistují)
    - VYKONAVA_FUNKCI relationships (Osoba -> Firma)
    - VLASTNI_PODIL relationships (pokud jsou data)
    """
    print(f"Processing RZP data from {os.path.basename(file_path)}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        rzp_data = json.load(f)
    
    for person_data in rzp_data:
        # Filtrování podle IČO
        if filter_ico:
            person_ico = person_data.get("ico")
            if person_ico != filter_ico:
                continue
        
        # Vytvořit Osoba node
        osoba_id = f"OSOBA-{person_data.get('ico', len(self.nodes['Osoba']))}"
        
        jmeno = person_data.get("jmeno", "")
        prijmeni = person_data.get("prijmeni", "")
        cele_jmeno = f"{jmeno} {prijmeni}".strip()
        
        osoba_node = {
            "osoba_id": osoba_id,
            "cele_jmeno": cele_jmeno,
            "jmeno": jmeno,
            "prijmeni": prijmeni,
            "datum_narozeni": person_data.get("datum_narozeni"),
            "statni_prislusnost": "CZ",
            "stav_zaznamu": "overeny"
        }
        
        osoba_node = {k: v for k, v in osoba_node.items() if v is not None and v != ""}
        self.nodes["Osoba"].append(osoba_node)
        
        # Propojit se Zdroj
        rel_zdroj = {
            "from": osoba_id,
            "to": zdroj_id,
            "datum_ziskani": datetime.now().isoformat()
        }
        self.relationships["POCHAZI_Z"].append(rel_zdroj)
        
        # Vytvořit vztahy s firmami
        for relationship in person_data.get("relationships", []):
            firma_ico = relationship.get("firma_ico")
            if not firma_ico:
                continue
            
            # Zajistit, že Firma node existuje
            firma_id = self.get_or_create_firma(
                {"ico": firma_ico, "name": ""},  # Název může být doplněn později
                zdroj_id
            )
            
            # Vytvořit VYKONAVA_FUNKCI relationship
            if relationship.get("type") == "VYKONAVA_FUNKCI":
                rel = {
                    "from": osoba_id,
                    "to": firma_ico,  # Firma používá IČO jako ID
                    "role": relationship.get("role", ""),
                    "platnost_od": relationship.get("platnost_od", ""),
                    "platnost_do": relationship.get("platnost_do", ""),
                    "zdroj_id": zdroj_id
                }
                rel = {k: v for k, v in rel.items() if v is not None and v != ""}
                self.relationships["VYKONAVA_FUNKCI"].append(rel)
```

### Krok 4: Přidat do transform_all()

```python
def transform_all(self, filter_ico=None):
    # ... existující kód ...
    
    # Create Zdroj for RZP
    zdroj_rzp = self.get_or_create_zdroj(
        "RZP",
        "Registr živnostenského podnikání",
        "https://rzp.gov.cz",
        "registr"
    )
    
    # Transform RZP data
    rzp_dir = Path(__file__).parent.parent / "data" / "people" / "extracted" / "rzp"
    if rzp_dir.exists():
        rzp_files = list(rzp_dir.glob("*.json"))
        for file in rzp_files:
            if "transformed" not in str(file):
                self.transform_rzp_data(str(file), zdroj_rzp, filter_ico=filter_ico)
```

## Výhody RZP jako zdroje

1. ✅ **Doplňuje chybějící data** - Osoba nodes a vztahy
2. ✅ **VYKONAVA_FUNKCI** - Vazby osob na firmy (jednatel, společník)
3. ✅ **VLASTNI_PODIL** - Pokud jsou data o podílech
4. ✅ **Ověřené údaje** - Oficiální registr
5. ✅ **Aktuální data** - API poskytuje aktuální stav

## Příklad workflow

```bash
# 1. Stáhnout data z RZP pro IČO
python3 scripts/download_rzp.py --ico 70886288

# 2. Extrahovat strukturovaná data
python3 scripts/extract_rzp.py --ico 70886288

# 3. Transformovat do Neo4j (spolu s ostatními zdroji)
python3 scripts/transform_to_neo4j.py --ico 70886288

# 4. Načíst do Neo4j
python3 scripts/load_to_neo4j.py
```

## Poznámky

- RZP API vyžaduje XML dotazy v encoding ISO-8859-2
- API podporuje vyhledávání podle IČO, názvu, adresy, role, atd.
- Odpovědi jsou také v XML formátu
- Je potřeba správně parsovat XML namespace: `urn:cz:isvs:rzp:schemas:VerejnaCast:v1`

## Závěr

RZP je **výborný zdroj** pro doplnění dat o osobách a jejich vztazích k firmám. Zapadá perfektně do tvého schématu a umožní vytvořit `VYKONAVA_FUNKCI` a `VLASTNI_PODIL` relationships, které zatím nemáš z `smlouvy.gov.cz`.

