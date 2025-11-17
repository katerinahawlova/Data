# Schema Overview - Entity a Vztahy

## Entity (Nodes)

### Osoba
- **osoba_id** (unique) - Interní ID osoby
- **cele_jmeno** - Celé jméno
- **jmeno** - Jméno
- **prijmeni** - Příjmení
- **datum_narozeni** - Datum narození
- **statni_prislusnost** - Státní příslušnost (např. "CZ")
- **stav_zaznamu** - Stav záznamu (draft / overeny / odmitnuty)

### Firma
- **ico** (unique) - IČO firmy
- **firma_id** - Interní ID firmy
- **nazev** - Název firmy
- **jurisdikce** - Jurisdikce (např. "CZ")
- **stav_zaznamu** - Stav záznamu

### Zadavatel
- **zadavatel_id** (unique) - ID zadavatele
- **ico** - IČO zadavatele (pokud existuje)
- **nazev** - Název zadavatele
- **typ** - Typ zadavatele (např. "ministerstvo")
- **uroven** - Úroveň (např. "centralni")
- **jurisdikce** - Jurisdikce
- **stav_zaznamu** - Stav záznamu

### Zakazka
- **zakazka_id** (unique) - ID zakázky
- **nazev** - Název zakázky
- **stav_zaznamu** - Stav záznamu
- **popis** - Popis zakázky
- **stav** - Stav zakázky (vypsana / probiha / ukoncena)
- **hodnota** - Hodnota zakázky
- **mena** - Měna (např. "CZK")
- **rok** - Rok zakázky
- **jurisdikce** - Jurisdikce
- **externi_id** - Externí ID zakázky

### Skola
- **skola_id** (unique) - ID školy
- **nazev** - Název školy
- **mesto** - Město
- **typ** - Typ školy (např. "univerzita")
- **obor** - Obor

### Zdroj
- **zdroj_id** (unique) - ID zdroje
- **nazev** - Název zdroje
- **url** - URL zdroje
- **typ** - Typ zdroje (např. "registr")
- **vydavatel** - Vydavatel
- **licence** - Licence
- **datum_ziskani** - Datum získání

## Vztahy (Relationships)

### VYKONAVA_FUNKCI
- **from**: Osoba → **to**: Firma
- **role** - Role osoby (např. "statutární orgán", "jednatel")
- **platnost_od** - Datum začátku platnosti
- **platnost_do** - Datum konce platnosti
- **zdroj_id** - ID zdroje dat

### VLASTNI_PODIL
- **from**: Osoba → **to**: Firma
- **podil_procent** - Podíl v procentech
- **platnost_od** - Datum začátku platnosti
- **platnost_do** - Datum konce platnosti
- **zdroj_id** - ID zdroje dat

### PODAVA_NABIDKU
- **from**: Firma → **to**: Zakazka
- **datum_podani** - Datum podání nabídky
- **nabidkova_cena** - Nabídková cena
- **mena** - Měna
- **zdroj_id** - ID zdroje dat

### JE_PRIDELENA
- **from**: Firma → **to**: Zakazka
- **smlouva_id** - ID smlouvy
- **platnost_od** - Datum začátku platnosti
- **platnost_do** - Datum konce platnosti
- **hodnota** - Hodnota smlouvy
- **mena** - Měna
- **zdroj_id** - ID zdroje dat

### STUDOVAL_NA
- **from**: Osoba → **to**: Skola
- **obor** - Obor studia
- **od** - Datum začátku studia
- **do** - Datum konce studia
- **zdroj_id** - ID zdroje dat

### POCHAZI_Z
- **from**: Any → **to**: Zdroj
- **datum_ziskani** - Datum získání dat

### VYHLASUJE_ZAKAZKU
- **from**: Zadavatel → **to**: Zakazka
- **datum_vyhlaseni** - Datum vyhlášení zakázky
- **zdroj_id** - ID zdroje dat

## Constraints

- `osoba_id_unique` - Osoba.osoba_id IS UNIQUE
- `firma_ico_unique` - Firma.ico IS UNIQUE
- `zadavatel_id_unique` - Zadavatel.zadavatel_id IS UNIQUE
- `zakazka_id_unique` - Zakazka.zakazka_id IS UNIQUE
- `skola_id_unique` - Skola.skola_id IS UNIQUE
- `zdroj_id_unique` - Zdroj.zdroj_id IS UNIQUE

## Indexy

- `osoba_jmeno_index` - Osoba(prijmeni, datum_narozeni)
- `firma_nazev_index` - Firma(nazev)
- `zakazka_rok_index` - Zakazka(rok)
- `zadavatel_nazev_index` - Zadavatel(nazev)
- `skola_nazev_mesto_index` - Skola(nazev, mesto)

