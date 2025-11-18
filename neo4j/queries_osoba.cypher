// ============================================
// DOTAZY PRO VYHLEDÁVÁNÍ OSOB
// ============================================

// 1. VYHLEDÁNÍ PODLE CELÉHO JMÉNA
// ----------------------------------------------------------------
// Najde osobu podle celého jména
MATCH (o:Osoba)
WHERE o.cele_jmeno CONTAINS "Pavlína Čížková"
RETURN o
LIMIT 10;

// 2. VYHLEDÁVÁNÍ PODLE JMÉNA A PŘÍJMENÍ
// ----------------------------------------------------------------
// Najde osobu podle jména a příjmení
MATCH (o:Osoba)
WHERE o.jmeno = "Pavlína" AND o.prijmeni = "Čížková"
RETURN o
LIMIT 10;

// 3. VYHLEDÁVÁNÍ PODLE PŘÍJMENÍ (ČÁSTEČNÁ SHODA)
// ----------------------------------------------------------------
// Najde všechny osoby s daným příjmením
MATCH (o:Osoba)
WHERE o.prijmeni CONTAINS "Novák"
RETURN 
    o.osoba_id AS osoba_id,
    o.cele_jmeno AS cele_jmeno,
    o.jmeno AS jmeno,
    o.prijmeni AS prijmeni,
    o.datum_narozeni AS datum_narozeni
ORDER BY o.prijmeni, o.jmeno
LIMIT 20;

// 4. VYHLEDÁVÁNÍ PODLE JMÉNA (ČÁSTEČNÁ SHODA)
// ----------------------------------------------------------------
// Najde všechny osoby s daným jménem
MATCH (o:Osoba)
WHERE o.jmeno CONTAINS "Jan"
RETURN 
    o.osoba_id AS osoba_id,
    o.cele_jmeno AS cele_jmeno,
    o.prijmeni AS prijmeni,
    o.datum_narozeni AS datum_narozeni
ORDER BY o.prijmeni, o.jmeno
LIMIT 20;

// 5. OSOBA S VŠEMI VZTAHY
// ----------------------------------------------------------------
// Zobrazí osobu a všechny její vztahy (firmy, školy, atd.)
MATCH (o:Osoba {cele_jmeno: "Pavlína Čížková"})
OPTIONAL MATCH (o)-[r1:VYKONAVA_FUNKCI]->(f:Firma)
OPTIONAL MATCH (o)-[r2:VLASTNI_PODIL]->(f2:Firma)
OPTIONAL MATCH (o)-[r3:STUDOVAL_NA]->(s:Skola)
OPTIONAL MATCH (o)-[r4:POCHAZI_Z]->(zd:Zdroj)
RETURN 
    o AS osoba,
    collect(DISTINCT {firma: f, relationship: r1}) AS firmy_ve_funkci,
    collect(DISTINCT {firma: f2, relationship: r2}) AS spolecnici,
    collect(DISTINCT {skola: s, relationship: r3}) AS skoly,
    collect(DISTINCT zd) AS zdroje
LIMIT 1;

// 6. OSOBA A FIRMY, KDE VYKONÁVÁ FUNKCI
// ----------------------------------------------------------------
// Zobrazí osobu a firmy, kde vykonává funkci
MATCH (o:Osoba {cele_jmeno: "Pavlína Čížková"})-[r:VYKONAVA_FUNKCI]->(f:Firma)
RETURN 
    o.cele_jmeno AS osoba,
    o.datum_narozeni AS datum_narozeni,
    f.ico AS firma_ico,
    f.nazev AS firma_nazev,
    r.role AS role,
    r.platnost_od AS platnost_od,
    r.platnost_do AS platnost_do
ORDER BY r.platnost_od DESC NULLS LAST
LIMIT 20;

// 7. OSOBA A FIRMY, KDE MÁ PODÍL
// ----------------------------------------------------------------
// Zobrazí osobu a firmy, kde má podíl
MATCH (o:Osoba {cele_jmeno: "Pavlína Čížková"})-[r:VLASTNI_PODIL]->(f:Firma)
RETURN 
    o.cele_jmeno AS osoba,
    f.ico AS firma_ico,
    f.nazev AS firma_nazev,
    r.podil_procent AS podil_procent,
    r.platnost_od AS platnost_od,
    r.platnost_do AS platnost_do
ORDER BY r.podil_procent DESC
LIMIT 20;

// 8. VYHLEDÁVÁNÍ PODLE DATUMU NAROZENÍ
// ----------------------------------------------------------------
// Najde osoby narozené v daném roce
MATCH (o:Osoba)
WHERE o.datum_narozeni STARTS WITH "1980"
RETURN 
    o.osoba_id AS osoba_id,
    o.cele_jmeno AS cele_jmeno,
    o.datum_narozeni AS datum_narozeni
ORDER BY o.datum_narozeni
LIMIT 20;

// 9. OSOBA - KOMPLETNÍ PŘEHLED
// ----------------------------------------------------------------
// Kompletní přehled o osobě včetně všech vztahů
MATCH (o:Osoba {cele_jmeno: "Pavlína Čížková"})
OPTIONAL MATCH (o)-[r1:VYKONAVA_FUNKCI]->(f1:Firma)
OPTIONAL MATCH (o)-[r2:VLASTNI_PODIL]->(f2:Firma)
OPTIONAL MATCH (o)-[r3:STUDOVAL_NA]->(s:Skola)
OPTIONAL MATCH (o)-[r4:POCHAZI_Z]->(zd:Zdroj)
RETURN 
    o AS osoba,
    collect(DISTINCT {
        firma: f1.nazev,
        ico: f1.ico,
        role: r1.role,
        platnost_od: r1.platnost_od,
        platnost_do: r1.platnost_do
    }) AS funkce_ve_firmach,
    collect(DISTINCT {
        firma: f2.nazev,
        ico: f2.ico,
        podil: r2.podil_procent,
        platnost_od: r2.platnost_od
    }) AS podily,
    collect(DISTINCT {
        skola: s.nazev,
        obor: r3.obor,
        od: r3.od,
        do: r3.do
    }) AS skoly
LIMIT 1;

// 10. VYHLEDÁVÁNÍ PODLE FIRMY
// ----------------------------------------------------------------
// Najde všechny osoby, které vykonávají funkci v dané firmě
MATCH (o:Osoba)-[r:VYKONAVA_FUNKCI]->(f:Firma {ico: "47114983"})
RETURN 
    o.osoba_id AS osoba_id,
    o.cele_jmeno AS cele_jmeno,
    o.jmeno AS jmeno,
    o.prijmeni AS prijmeni,
    o.datum_narozeni AS datum_narozeni,
    r.role AS role,
    r.platnost_od AS platnost_od,
    r.platnost_do AS platnost_do,
    f.nazev AS firma
ORDER BY r.platnost_od DESC NULLS LAST
LIMIT 50;

// 11. VYHLEDÁVÁNÍ PODLE ROLE
// ----------------------------------------------------------------
// Najde všechny osoby s danou rolí
MATCH (o:Osoba)-[r:VYKONAVA_FUNKCI]->(f:Firma)
WHERE r.role CONTAINS "statutární orgán"
RETURN 
    o.cele_jmeno AS osoba,
    f.nazev AS firma,
    f.ico AS firma_ico,
    r.role AS role,
    r.platnost_od AS platnost_od,
    r.platnost_do AS platnost_do
ORDER BY f.nazev, o.prijmeni
LIMIT 50;

// 12. VIZUALIZACE OSOBY S VŠEMI VZTAHY
// ----------------------------------------------------------------
// Zobrazí osobu a všechny její vztahy pro vizualizaci
MATCH (o:Osoba {cele_jmeno: "Pavlína Čížková"})
OPTIONAL MATCH (o)-[r1:VYKONAVA_FUNKCI]->(f1:Firma)
OPTIONAL MATCH (o)-[r2:VLASTNI_PODIL]->(f2:Firma)
OPTIONAL MATCH (o)-[r3:STUDOVAL_NA]->(s:Skola)
RETURN o, f1, f2, s, r1, r2, r3
LIMIT 50;

// 13. VYHLEDÁVÁNÍ PODLE ČÁSTEČNÉHO JMÉNA (CASE INSENSITIVE)
// ----------------------------------------------------------------
// Najde osoby podle části jména (case insensitive)
MATCH (o:Osoba)
WHERE toLower(o.cele_jmeno) CONTAINS toLower("pavlína")
   OR toLower(o.jmeno) CONTAINS toLower("pavlína")
   OR toLower(o.prijmeni) CONTAINS toLower("čížková")
RETURN 
    o.osoba_id AS osoba_id,
    o.cele_jmeno AS cele_jmeno,
    o.jmeno AS jmeno,
    o.prijmeni AS prijmeni,
    o.datum_narozeni AS datum_narozeni
ORDER BY o.prijmeni, o.jmeno
LIMIT 20;

// 14. STATISTIKA OSOBY
// ----------------------------------------------------------------
// Zobrazí statistiku o osobě
MATCH (o:Osoba {cele_jmeno: "Pavlína Čížková"})
OPTIONAL MATCH (o)-[r1:VYKONAVA_FUNKCI]->(f1:Firma)
OPTIONAL MATCH (o)-[r2:VLASTNI_PODIL]->(f2:Firma)
OPTIONAL MATCH (o)-[r3:STUDOVAL_NA]->(s:Skola)
RETURN 
    o.cele_jmeno AS osoba,
    o.datum_narozeni AS datum_narozeni,
    count(DISTINCT f1) AS pocet_firem_ve_funkci,
    count(DISTINCT f2) AS pocet_firem_s_podilem,
    count(DISTINCT s) AS pocet_skol,
    collect(DISTINCT f1.nazev) AS firmy_ve_funkci,
    collect(DISTINCT f2.nazev) AS firmy_s_podilem
LIMIT 1;

