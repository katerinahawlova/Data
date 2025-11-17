// ============================================
// CYPHER DOTAZY PRO ENTITU FIRMA
// ============================================

// 1. ZÁKLADNÍ INFORMACE O FIRMĚ
// --------------------------------
// Zobrazí základní informace o firmě podle IČO
MATCH (f:Firma {ico: "47114983"})
RETURN 
    f.ico AS ico,
    f.nazev AS nazev,
    f.jurisdikce AS jurisdikce,
    f.stav_zaznamu AS stav_zaznamu,
    f.firma_id AS firma_id
LIMIT 1;

// 2. VŠECHNY FIRMY S POČTEM VZTAHŮ
// --------------------------------
// Zobrazí všechny firmy s počtem vztahů
MATCH (f:Firma)
OPTIONAL MATCH (f)<-[:VYKONAVA_FUNKCI]-(o:Osoba)
OPTIONAL MATCH (f)-[:JE_PRIDELENA]->(z:Zakazka)
OPTIONAL MATCH (f)-[:PODAVA_NABIDKU]->(z2:Zakazka)
RETURN 
    f.ico AS ico,
    f.nazev AS nazev,
    count(DISTINCT o) AS pocet_osob,
    count(DISTINCT z) AS pocet_zakazek,
    count(DISTINCT z2) AS pocet_nabidek
ORDER BY pocet_osob DESC, pocet_zakazek DESC
LIMIT 20;

// 3. FIRMA S VŠEMI VZTAHY
// --------------------------------
// Zobrazí firmu a všechny její vztahy
MATCH (f:Firma {ico: "47114983"})
OPTIONAL MATCH (o:Osoba)-[r1:VYKONAVA_FUNKCI]->(f)
OPTIONAL MATCH (o2:Osoba)-[r2:VLASTNI_PODIL]->(f)
OPTIONAL MATCH (f)-[r3:JE_PRIDELENA]->(z:Zakazka)
OPTIONAL MATCH (f)-[r4:PODAVA_NABIDKU]->(z2:Zakazka)
OPTIONAL MATCH (f)-[r5:POCHAZI_Z]->(zd:Zdroj)
RETURN 
    f.ico AS ico,
    f.nazev AS nazev,
    collect(DISTINCT {
        osoba: o.cele_jmeno,
        role: r1.role,
        platnost_od: r1.platnost_od,
        platnost_do: r1.platnost_do
    }) AS osoby_ve_funkci,
    collect(DISTINCT {
        osoba: o2.cele_jmeno,
        podil: r2.podil_procent,
        platnost_od: r2.platnost_od
    }) AS spolecnici,
    collect(DISTINCT {
        zakazka: z.zakazka_id,
        nazev: z.nazev,
        hodnota: z.hodnota,
        mena: z.mena
    }) AS prideleny_zakazky,
    collect(DISTINCT {
        zakazka: z2.zakazka_id,
        nazev: z2.nazev,
        nabidkova_cena: r4.nabidkova_cena
    }) AS podane_nabidky,
    collect(DISTINCT zd.nazev) AS zdroje
LIMIT 1;

// 4. OSOBY VE FUNKCI U FIRMY
// --------------------------------
// Zobrazí všechny osoby, které vykonávají funkci u firmy
MATCH (o:Osoba)-[r:VYKONAVA_FUNKCI]->(f:Firma {ico: "47114983"})
RETURN 
    o.cele_jmeno AS osoba,
    o.jmeno AS jmeno,
    o.prijmeni AS prijmeni,
    o.datum_narozeni AS datum_narozeni,
    r.role AS role,
    r.platnost_od AS platnost_od,
    r.platnost_do AS platnost_do,
    r.zdroj_id AS zdroj
ORDER BY r.platnost_od DESC NULLS LAST
LIMIT 50;

// 5. ZAKÁZKY FIRMY
// --------------------------------
// Zobrazí všechny zakázky, které jsou firmě přiděleny
MATCH (f:Firma {ico: "47114983"})-[r:JE_PRIDELENA]->(z:Zakazka)
RETURN 
    z.zakazka_id AS zakazka_id,
    z.nazev AS nazev,
    z.hodnota AS hodnota,
    z.mena AS mena,
    z.rok AS rok,
    z.stav AS stav,
    r.smlouva_id AS smlouva_id,
    r.platnost_od AS platnost_od,
    r.platnost_do AS platnost_do
ORDER BY z.rok DESC, z.hodnota DESC
LIMIT 50;

// 6. STATISTIKA FIRMY
// --------------------------------
// Zobrazí statistiku o firmě
MATCH (f:Firma {ico: "47114983"})
OPTIONAL MATCH (o:Osoba)-[:VYKONAVA_FUNKCI]->(f)
OPTIONAL MATCH (o2:Osoba)-[:VLASTNI_PODIL]->(f)
OPTIONAL MATCH (f)-[:JE_PRIDELENA]->(z:Zakazka)
OPTIONAL MATCH (f)-[:PODAVA_NABIDKU]->(z2:Zakazka)
RETURN 
    f.ico AS ico,
    f.nazev AS nazev,
    count(DISTINCT o) AS pocet_osob_ve_funkci,
    count(DISTINCT o2) AS pocet_spolecniku,
    count(DISTINCT z) AS pocet_pridelenych_zakazek,
    sum(z.hodnota) AS celkova_hodnota_zakazek,
    count(DISTINCT z2) AS pocet_podanych_nabidek,
    collect(DISTINCT z.rok) AS roky_zakazek
LIMIT 1;

// 7. FIRMY BEZ NÁZVU
// --------------------------------
// Najde firmy, které nemají vyplněný název
MATCH (f:Firma)
WHERE f.nazev IS NULL OR f.nazev = ""
RETURN 
    f.ico AS ico,
    f.nazev AS nazev,
    count{(f)<-[:VYKONAVA_FUNKCI]-(:Osoba)} AS pocet_osob,
    count{(f)-[:JE_PRIDELENA]->(:Zakazka)} AS pocet_zakazek
ORDER BY pocet_osob DESC, pocet_zakazek DESC
LIMIT 20;

// 8. FIRMA S NEJVÍCE VZTAHY
// --------------------------------
// Najde firmu s nejvíce vztahy
MATCH (f:Firma)
OPTIONAL MATCH (f)<-[:VYKONAVA_FUNKCI]-(o:Osoba)
OPTIONAL MATCH (f)-[:JE_PRIDELENA]->(z:Zakazka)
WITH f, 
     count(DISTINCT o) AS pocet_osob,
     count(DISTINCT z) AS pocet_zakazek,
     pocet_osob + pocet_zakazek AS celkem_vztahu
RETURN 
    f.ico AS ico,
    f.nazev AS nazev,
    pocet_osob,
    pocet_zakazek,
    celkem_vztahu
ORDER BY celkem_vztahu DESC
LIMIT 10;

// 9. FIRMA A ZADAVATELÉ
// --------------------------------
// Zobrazí, které zadavatele mají zakázky s touto firmou
MATCH (f:Firma {ico: "47114983"})-[r:JE_PRIDELENA]->(z:Zakazka)<-[:VYHLASUJE_ZAKAZKU]-(zv:Zadavatel)
RETURN 
    DISTINCT zv.zadavatel_id AS zadavatel_id,
    zv.nazev AS zadavatel_nazev,
    zv.ico AS zadavatel_ico,
    count(z) AS pocet_zakazek,
    sum(z.hodnota) AS celkova_hodnota
ORDER BY celkova_hodnota DESC
LIMIT 20;

// 10. FIRMA - KOMPLETNÍ PŘEHLED
// --------------------------------
// Kompletní přehled všech informací o firmě
MATCH (f:Firma {ico: "47114983"})
OPTIONAL MATCH (o:Osoba)-[r1:VYKONAVA_FUNKCI]->(f)
OPTIONAL MATCH (o2:Osoba)-[r2:VLASTNI_PODIL]->(f)
OPTIONAL MATCH (f)-[r3:JE_PRIDELENA]->(z:Zakazka)<-[:VYHLASUJE_ZAKAZKU]-(zv:Zadavatel)
OPTIONAL MATCH (f)-[r4:PODAVA_NABIDKU]->(z2:Zakazka)
OPTIONAL MATCH (f)-[r5:POCHAZI_Z]->(zd:Zdroj)
RETURN 
    f AS firma,
    collect(DISTINCT {
        osoba: o,
        relationship: r1
    }) AS osoby_ve_funkci,
    collect(DISTINCT {
        osoba: o2,
        relationship: r2
    }) AS spolecnici,
    collect(DISTINCT {
        zakazka: z,
        zadavatel: zv,
        relationship: r3
    }) AS prideleny_zakazky,
    collect(DISTINCT {
        zakazka: z2,
        relationship: r4
    }) AS podane_nabidky,
    collect(DISTINCT zd) AS zdroje
LIMIT 1;

