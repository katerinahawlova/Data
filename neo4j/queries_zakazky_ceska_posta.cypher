// ============================================
// DOTAZY PRO ZAKÁZKY ČESKÉ POŠTY
// ============================================

// 1. ZAKÁZKY, KDE JE ČESKÁ POŠTA ZADAVATELEM A JE ZNÁM DODAVATEL
// ----------------------------------------------------------------
// Zobrazí zakázky, kde Česká pošta vyhlásila zakázku a komu byla přidělena
MATCH (zv:Zadavatel {ico: "47114983"})-[r1:VYHLASUJE_ZAKAZKU]->(z:Zakazka)<-[r2:JE_PRIDELENA]-(f:Firma)
RETURN 
    z.zakazka_id AS zakazka_id,
    z.nazev AS nazev_zakazky,
    z.hodnota AS hodnota_zakazky,
    z.mena AS mena,
    z.rok AS rok,
    f.ico AS dodavatel_ico,
    f.nazev AS dodavatel_nazev,
    r2.hodnota AS hodnota_smlouvy,
    r2.smlouva_id AS smlouva_id
ORDER BY z.hodnota DESC
LIMIT 50;

// 2. STATISTIKA DODAVATELŮ ČESKÉ POŠTY
// ----------------------------------------------------------------
// Zobrazí, kolik zakázek má každý dodavatel od České pošty
MATCH (zv:Zadavatel {ico: "47114983"})-[r1:VYHLASUJE_ZAKAZKU]->(z:Zakazka)<-[r2:JE_PRIDELENA]-(f:Firma)
RETURN 
    f.ico AS dodavatel_ico,
    f.nazev AS dodavatel_nazev,
    count(z) AS pocet_zakazek,
    sum(z.hodnota) AS celkova_hodnota_zakazek,
    sum(r2.hodnota) AS celkova_hodnota_smluv,
    collect(z.zakazka_id)[0..5] AS prvni_zakazky
ORDER BY pocet_zakazek DESC, celkova_hodnota_smluv DESC
LIMIT 20;

// 3. ZAKÁZKY BEZ DODAVATELE
// ----------------------------------------------------------------
// Zobrazí zakázky, kde Česká pošta je zadavatelem, ale ještě není přiřazen dodavatel
MATCH (zv:Zadavatel {ico: "47114983"})-[r1:VYHLASUJE_ZAKAZKU]->(z:Zakazka)
WHERE NOT EXISTS {
    (z)<-[:JE_PRIDELENA]-(:Firma)
}
RETURN 
    z.zakazka_id AS zakazka_id,
    z.nazev AS nazev_zakazky,
    z.hodnota AS hodnota,
    z.stav AS stav,
    z.rok AS rok,
    r1.datum_vyhlaseni AS datum_vyhlaseni
ORDER BY z.rok DESC, z.hodnota DESC NULLS LAST
LIMIT 20;

// 4. KOMPLETNÍ PŘEHLED ZAKÁZKY S DODAVATELEM
// ----------------------------------------------------------------
// Zobrazí kompletní informace o zakázce včetně zadavatele a dodavatele
MATCH (zv:Zadavatel {ico: "47114983"})-[r1:VYHLASUJE_ZAKAZKU]->(z:Zakazka)
OPTIONAL MATCH (z)<-[r2:JE_PRIDELENA]-(f:Firma)
RETURN 
    z.zakazka_id AS zakazka_id,
    z.nazev AS nazev,
    z.hodnota AS hodnota_zakazky,
    z.stav AS stav,
    z.rok AS rok,
    zv.nazev AS zadavatel,
    f.nazev AS dodavatel,
    f.ico AS dodavatel_ico,
    r2.hodnota AS hodnota_smlouvy,
    r2.smlouva_id AS smlouva_id,
    r2.platnost_od AS platnost_od,
    r2.platnost_do AS platnost_do
ORDER BY z.rok DESC, z.hodnota DESC NULLS LAST
LIMIT 50;

// 5. NEJVĚTŠÍ ZAKÁZKY ČESKÉ POŠTY
// ----------------------------------------------------------------
// Zobrazí největší zakázky, kde je Česká pošta zadavatelem
MATCH (zv:Zadavatel {ico: "47114983"})-[r1:VYHLASUJE_ZAKAZKU]->(z:Zakazka)
OPTIONAL MATCH (z)<-[r2:JE_PRIDELENA]-(f:Firma)
WHERE z.hodnota IS NOT NULL
RETURN 
    z.zakazka_id AS zakazka_id,
    z.nazev AS nazev,
    z.hodnota AS hodnota,
    z.mena AS mena,
    z.rok AS rok,
    f.nazev AS dodavatel,
    r2.hodnota AS hodnota_smlouvy
ORDER BY z.hodnota DESC
LIMIT 20;

