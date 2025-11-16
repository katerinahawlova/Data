// Neo4j Schema Definition for MBA Thesis Project
// Czech Schema - Public Tenders Relationship Analysis

// ---------- UZLY: UNIQUE CONSTRAINTS ----------

// Osoba – interní ID
CREATE CONSTRAINT osoba_id_unique IF NOT EXISTS
FOR (o:Osoba)
REQUIRE o.osoba_id IS UNIQUE;

// Firma – IČO
CREATE CONSTRAINT firma_ico_unique IF NOT EXISTS
FOR (f:Firma)
REQUIRE f.ico IS UNIQUE;

// Zadavatel – IČO (pokud existuje)
CREATE CONSTRAINT zadavatel_id_unique IF NOT EXISTS
FOR (z:Zadavatel)
REQUIRE z.zadavatel_id IS UNIQUE;

// Zakázka – ID
CREATE CONSTRAINT zakazka_id_unique IF NOT EXISTS
FOR (z:Zakazka)
REQUIRE z.zakazka_id IS UNIQUE;

// Škola – ID
CREATE CONSTRAINT skola_id_unique IF NOT EXISTS
FOR (s:Skola)
REQUIRE s.skola_id IS UNIQUE;

// Zdroj – ID
CREATE CONSTRAINT zdroj_id_unique IF NOT EXISTS
FOR (zd:Zdroj)
REQUIRE zd.zdroj_id IS UNIQUE;

// ---------- INDEXY PRO VYHLEDÁVÁNÍ ----------

// Osoba – jméno + příjmení
CREATE INDEX osoba_jmeno_index IF NOT EXISTS
FOR (o:Osoba)
ON (o.prijmeni, o.datum_narozeni);

// Firma – název
CREATE INDEX firma_nazev_index IF NOT EXISTS
FOR (f:Firma)
ON (f.nazev);

// Zakázka – rok
CREATE INDEX zakazka_rok_index IF NOT EXISTS
FOR (z:Zakazka)
ON (z.rok);

// Zadavatel – název
CREATE INDEX zadavatel_nazev_index IF NOT EXISTS
FOR (z:Zadavatel)
ON (z.nazev);

// Škola – název + město
CREATE INDEX skola_nazev_mesto_index IF NOT EXISTS
FOR (s:Skola)
ON (s.nazev, s.mesto);

// ---------- NODE SCHEMA ----------

// (:Osoba)
//   - osoba_id (unique)
//   - cele_jmeno
//   - jmeno
//   - prijmeni
//   - datum_narozeni
//   - statni_prislusnost
//   - stav_zaznamu  // draft / overeny / odmitnuty

// (:Firma)
//   - firma_id
//   - ico (unique)
//   - nazev
//   - jurisdikce
//   - stav_zaznamu

// (:Zadavatel)
//   - zadavatel_id (unique)
//   - ico
//   - nazev
//   - typ
//   - uroven
//   - jurisdikce
//   - stav_zaznamu

// (:Zakazka)
//   - zakazka_id (unique)
//   - nazev
//   - stav_zaznamu
//   - popis
//   - stav  // vypsana / probiha / ukoncena
//   - hodnota
//   - mena
//   - rok
//   - jurisdikce
//   - externi_id

// (:Skola)
//   - skola_id (unique)
//   - nazev
//   - mesto
//   - typ
//   - obor

// (:Zdroj)
//   - zdroj_id (unique)
//   - nazev
//   - url
//   - typ
//   - vydavatel
//   - licence
//   - datum_ziskani

// ---------- RELATIONSHIP TYPES ----------

// (:Osoba)-[:VYKONAVA_FUNKCI {role, platnost_od, platnost_do, zdroj_id}]->(:Firma)
// (:Osoba)-[:VLASTNI_PODIL {podil_procent, platnost_od, platnost_do, zdroj_id}]->(:Firma)
// (:Firma)-[:PODAVA_NABIDKU {datum_podani, nabidkova_cena, mena, zdroj_id}]->(:Zakazka)
// (:Firma)-[:JE_PRIDELENA {smlouva_id, platnost_od, platnost_do, hodnota, mena, zdroj_id}]->(:Zakazka)
// (:Osoba)-[:STUDOVAL_NA {obor, od, do, zdroj_id}]->(:Skola)
// (:Any)-[:POCHAZI_Z {datum_ziskani}]->(:Zdroj)
// (:Zadavatel)-[:VYHLASUJE_ZAKAZKU {datum_vyhlaseni, zdroj_id}]->(:Zakazka)
