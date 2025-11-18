# LinkedIn Integration - Analýza a Návrh

## ⚠️ Důležité upozornění

LinkedIn **nemá veřejně dostupné API** pro hromadné získávání dat. Pro získání dat je potřeba použít:
- Web scraping (právně citlivé)
- Komerční scraping služby (ScraperAPI, Apify, ZenRows)
- LinkedIn Learning API (pouze pro vzdělávací obsah)

**Právní aspekty:**
- LinkedIn má přísné zásady proti automatizovanému sběru dat
- Scraping může porušovat Terms of Service
- Doporučuje se konzultace s právníkem

---

## 🎯 Co bychom mohli získat z LinkedIn

### Pro Osoba nodes:
- ✅ Jméno, příjmení, celé jméno
- ✅ Profesní zkušenosti (pracovní historie)
- ✅ Vzdělání (školy, obory, roky) → `STUDOVAL_NA` relationship
- ✅ Dovednosti
- ✅ Současné/předchozí zaměstnání → `VYKONAVA_FUNKCI` relationship

### Pro Firma nodes:
- ✅ Název firmy
- ✅ Počet zaměstnanců
- ✅ Lokace
- ✅ Odvětví

### Pro relationships:
- ✅ `VYKONAVA_FUNKCI` - Osoba → Firma (z pracovní historie)
- ✅ `STUDOVAL_NA` - Osoba → Skola (z vzdělání)
- ✅ `POCHAZI_Z` - Any → Zdroj (LinkedIn)

---

## 🔧 Možné přístupy

### Varianta 1: Komerční Scraping API (Doporučeno)

**Výhody:**
- Legální (služba řeší právní aspekty)
- Spolehlivé
- Obejde anti-scraping mechanismy

**Nevýhody:**
- Placené (cca $50-200/měsíc)
- Rate limits

**Služby:**
- **ScraperAPI** - https://www.scraperapi.com/linkedin-scraper/
- **Apify** - https://apify.com/api/linkedin-search-api
- **ZenRows** - https://www.zenrows.com/products/scraper-api/social-media/linkedin

**Implementace:**
```python
# scripts/download_linkedin.py
import requests

def download_linkedin_profile(profile_url, api_key):
    """Stáhne LinkedIn profil pomocí ScraperAPI"""
    url = "https://api.scraperapi.com"
    params = {
        "api_key": api_key,
        "url": profile_url
    }
    response = requests.get(url, params=params)
    return response.text  # HTML
```

---

### Varianta 2: Vlastní Scraper (Selenium/Playwright)

**Výhody:**
- Zdarma
- Plná kontrola

**Nevýhody:**
- Právně rizikové
- LinkedIn má anti-scraping (CAPTCHA, rate limiting)
- Vyžaduje přihlášení
- Pomalé

**Implementace:**
```python
# scripts/download_linkedin.py
from selenium import webdriver
from selenium.webdriver.common.by import By

def download_linkedin_profile_selenium(profile_url, username, password):
    """Stáhne LinkedIn profil pomocí Selenium"""
    driver = webdriver.Chrome()
    driver.get("https://www.linkedin.com/login")
    # Login...
    driver.get(profile_url)
    html = driver.page_source
    driver.quit()
    return html
```

---

### Varianta 3: LinkedIn Learning API (Omezené)

**Účel:** Pouze vzdělávací obsah
**Omezení:** Nezahrnuje profily, pracovní zkušenosti

---

## 📋 Návrh implementace

### 1. Download Script (`scripts/download_linkedin.py`)

```python
"""
Download LinkedIn data using ScraperAPI or Selenium.

Supports:
- Profile URLs
- Company pages
- Search results
"""

def download_linkedin_profile(profile_url: str, method: str = "scraperapi") -> str:
    """
    Stáhne LinkedIn profil.
    
    Args:
        profile_url: URL LinkedIn profilu (např. "https://linkedin.com/in/jan-novak")
        method: "scraperapi" nebo "selenium"
    
    Returns:
        HTML obsah profilu
    """
    pass

def download_linkedin_company(company_url: str) -> str:
    """Stáhne LinkedIn stránku firmy."""
    pass

def download_linkedin_search(query: str, max_results: int = 100) -> List[str]:
    """Stáhne výsledky vyhledávání."""
    pass
```

**Výstup:** HTML soubory v `data/people/raw/linkedin/`

---

### 2. Extract Script (`scripts/extract_linkedin.py`)

```python
"""
Extract structured data from LinkedIn HTML.

Extracts:
- Person data (name, experience, education)
- Company data
- Relationships (person -> company, person -> school)
"""

def extract_linkedin_profile(html_path: Path) -> Dict[str, Any]:
    """
    Extrahuje data z LinkedIn profilu.
    
    Returns:
        {
            "cele_jmeno": "Jan Novák",
            "jmeno": "Jan",
            "prijmeni": "Novák",
            "pracovni_zkusenosti": [
                {
                    "firma_nazev": "Česká pošta, s.p.",
                    "firma_ico": "47114983",  # Pokud se podaří najít
                    "pozice": "Ředitel",
                    "od": "2020-01",
                    "do": None
                }
            ],
            "vzdelani": [
                {
                    "skola_nazev": "VŠE v Praze",
                    "obor": "Informatika",
                    "od": "2000",
                    "do": "2005"
                }
            ]
        }
    """
    pass
```

**Výstup:** JSON soubory v `data/people/extracted/linkedin/`

---

### 3. Transform Method (`transform_to_neo4j.py`)

```python
def transform_linkedin_data(self, file_path: str, zdroj_id: str, filter_ico=None):
    """
    Transformuje LinkedIn data do Neo4j formátu.
    
    Vytvoří:
    - Osoba nodes
    - Firma nodes (z pracovních zkušeností)
    - Skola nodes (z vzdělání)
    - VYKONAVA_FUNKCI relationships (Osoba -> Firma)
    - STUDOVAL_NA relationships (Osoba -> Skola)
    """
    with open(file_path, 'r') as f:
        profile_data = json.load(f)
    
    # Vytvořit Osoba node
    osoba_id = self.get_or_create_osoba(profile_data)
    
    # Vytvořit VYKONAVA_FUNKCI relationships
    for zkusenost in profile_data.get("pracovni_zkusenosti", []):
        firma_ico = zkusenost.get("firma_ico")
        if firma_ico:
            firma_id = self.get_or_create_firma(
                {"ico": firma_ico, "name": zkusenost.get("firma_nazev", "")},
                zdroj_id
            )
            # Vytvořit relationship
            rel = {
                "from": osoba_id,
                "to": firma_ico,
                "role": zkusenost.get("pozice", ""),
                "platnost_od": zkusenost.get("od"),
                "platnost_do": zkusenost.get("do"),
                "zdroj_id": zdroj_id
            }
            self.relationships["VYKONAVA_FUNKCI"].append(rel)
    
    # Vytvořit STUDOVAL_NA relationships
    for vzdelani in profile_data.get("vzdelani", []):
        skola_id = self.get_or_create_skola(vzdelani)
        rel = {
            "from": osoba_id,
            "to": skola_id,
            "obor": vzdelani.get("obor", ""),
            "od": vzdelani.get("od"),
            "do": vzdelani.get("do"),
            "zdroj_id": zdroj_id
        }
        self.relationships["STUDOVAL_NA"].append(rel)
```

---

## 🚧 Výzvy a omezení

### 1. **IČO matching**
- LinkedIn profily neobsahují IČO firem
- **Řešení:** Matchovat podle názvu firmy s existujícími Firma nodes v Neo4j
- **Alternativa:** Použít externí API pro IČO lookup (ARES, Google)

### 2. **Rate limiting**
- LinkedIn má přísné rate limits
- **Řešení:** Implementovat delays, použít proxy, použít komerční API

### 3. **Autentizace**
- Vlastní scraper vyžaduje přihlášení
- **Řešení:** Selenium s cookies, nebo komerční API

### 4. **Dynamický obsah**
- LinkedIn používá JavaScript
- **Řešení:** Selenium/Playwright nebo komerční API

---

## 💡 Doporučený přístup

### Fáze 1: Proof of Concept (Selenium)
1. Vytvořit jednoduchý Selenium scraper
2. Otestovat na několika profilech
3. Zkontrolovat, co se dá extrahovat

### Fáze 2: Produkční řešení (Komerční API)
1. Zvolit komerční službu (ScraperAPI/Apify)
2. Implementovat download script
3. Implementovat extract script
4. Přidat transform metodu

### Fáze 3: IČO Matching
1. Implementovat matching názvu firmy s IČO
2. Použít ARES API nebo existující data v Neo4j

---

## 📝 Checklist pro implementaci

- [ ] Rozhodnout se pro přístup (Selenium vs. komerční API)
- [ ] Vytvořit `scripts/download_linkedin.py`
- [ ] Vytvořit `scripts/extract_linkedin.py`
- [ ] Přidat `transform_linkedin_data()` do `transform_to_neo4j.py`
- [ ] Vytvořit Zdroj node pro LinkedIn
- [ ] Implementovat IČO matching
- [ ] Otestovat na několika profilech
- [ ] Zkontrolovat právní aspekty

---

## 🔗 Užitečné odkazy

- ScraperAPI: https://www.scraperapi.com/linkedin-scraper/
- Apify LinkedIn Actors: https://apify.com/store?q=linkedin
- LinkedIn Terms of Service: https://www.linkedin.com/legal/user-agreement
- hiQ Labs v. LinkedIn case: https://en.wikipedia.org/wiki/HiQ_Labs_v._LinkedIn

---

## ❓ Otázky k zodpovězení

1. **Jaký přístup preferuješ?** (Selenium vs. komerční API)
2. **Kolik profilů chceš stáhnout?** (ovlivní volbu přístupu)
3. **Máš přístup k LinkedIn účtu?** (pro Selenium)
4. **Jaký rozpočet?** (pro komerční API)
5. **Co konkrétně chceš extrahovat?** (profily, firmy, vzdělání, atd.)

---

## 🎯 Alternativní zdroje dat

Pokud LinkedIn není vhodný, zvaž:
- **ARES** - Obchodní rejstřík (IČO, statutární orgán)
- **VVZ** - Věstník veřejných zakázek (nabídky, zakázky)
- **NEN** - Národní elektronický nástěnka (veřejné zakázky)
- **Justice.cz** - Obchodní rejstřík (podrobnější data než RZP)


