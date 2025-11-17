// ============================================
// SCHEMA DOTAZY - ENTITY A VZTAHY S ATRIBUTY
// ============================================

// 1. VŠECHNY ENTITY (NODE LABELS) S ATRIBUTY
// -------------------------------------------
// Zobrazí všechny entity a jejich atributy s příklady hodnot
MATCH (n)
WITH labels(n) AS labels, keys(n) AS keys, n AS node
UNWIND labels AS label
WITH DISTINCT label, keys, node
WHERE label IN ['Osoba', 'Firma', 'Zadavatel', 'Zakazka', 'Skola', 'Zdroj']
RETURN 
    label AS entita,
    collect(DISTINCT keys(node))[0] AS vsechny_atributy,
    collect(DISTINCT {
        atribut: keys(node),
        hodnoty: [k IN keys(node) | {k: node[k]}]
    })[0] AS priklad_hodnot
ORDER BY label;

// 2. DETAILNÍ VÝPIS ENTITY S ATRIBUTY
// -------------------------------------------
// Pro každou entitu zobrazí všechny atributy a jejich typy/hodnoty
CALL db.schema.nodeTypeProperties()
YIELD nodeType, propertyName, propertyTypes, mandatory
WHERE nodeType IN ['Osoba', 'Firma', 'Zadavatel', 'Zakazka', 'Skola', 'Zdroj']
RETURN 
    nodeType AS entita,
    propertyName AS atribut,
    propertyTypes AS typy,
    mandatory AS povinny
ORDER BY nodeType, propertyName;

// 3. VŠECHNY VZTAHY (RELATIONSHIP TYPES) S ATRIBUTY
// -------------------------------------------
// Zobrazí všechny typy vztahů a jejich atributy
MATCH ()-[r]-()
WITH type(r) AS relationshipType, keys(r) AS keys, r AS rel
RETURN 
    DISTINCT relationshipType AS vztah,
    collect(DISTINCT keys(rel))[0] AS vsechny_atributy,
    collect(DISTINCT {
        atribut: keys(rel),
        hodnoty: [k IN keys(rel) | {k: rel[k]}]
    })[0] AS priklad_hodnot
ORDER BY relationshipType;

// 4. DETAILNÍ VÝPIS VZTAHŮ S ATRIBUTY
// -------------------------------------------
// Pro každý vztah zobrazí všechny atributy
CALL db.schema.relTypeProperties()
YIELD relType, propertyName, propertyTypes, mandatory
RETURN 
    relType AS vztah,
    propertyName AS atribut,
    propertyTypes AS typy,
    mandatory AS povinny
ORDER BY relType, propertyName;

// 5. ENTITY OSOBA - VŠECHNY ATRIBUTY
// -------------------------------------------
MATCH (o:Osoba)
WITH o LIMIT 1
RETURN 
    'Osoba' AS entita,
    keys(o) AS atributy,
    [k IN keys(o) | {atribut: k, hodnota: o[k], typ: toString(type(o[k]))}] AS atributy_s_hodnotami;

// 6. ENTITY FIRMA - VŠECHNY ATRIBUTY
// -------------------------------------------
MATCH (f:Firma)
WITH f LIMIT 1
RETURN 
    'Firma' AS entita,
    keys(f) AS atributy,
    [k IN keys(f) | {atribut: k, hodnota: f[k], typ: toString(type(f[k]))}] AS atributy_s_hodnotami;

// 7. ENTITY ZADAVATEL - VŠECHNY ATRIBUTY
// -------------------------------------------
MATCH (z:Zadavatel)
WITH z LIMIT 1
RETURN 
    'Zadavatel' AS entita,
    keys(z) AS atributy,
    [k IN keys(z) | {atribut: k, hodnota: z[k], typ: toString(type(z[k]))}] AS atributy_s_hodnotami;

// 8. ENTITY ZAKAZKA - VŠECHNY ATRIBUTY
// -------------------------------------------
MATCH (z:Zakazka)
WITH z LIMIT 1
RETURN 
    'Zakazka' AS entita,
    keys(z) AS atributy,
    [k IN keys(z) | {atribut: k, hodnota: z[k], typ: toString(type(z[k]))}] AS atributy_s_hodnotami;

// 9. ENTITY ZDROJ - VŠECHNY ATRIBUTY
// -------------------------------------------
MATCH (zd:Zdroj)
WITH zd LIMIT 1
RETURN 
    'Zdroj' AS entita,
    keys(zd) AS atributy,
    [k IN keys(zd) | {atribut: k, hodnota: zd[k], typ: toString(type(zd[k]))}] AS atributy_s_hodnotami;

// 10. VZTAH VYKONAVA_FUNKCI - VŠECHNY ATRIBUTY
// -------------------------------------------
MATCH ()-[r:VYKONAVA_FUNKCI]->()
WITH r LIMIT 1
RETURN 
    'VYKONAVA_FUNKCI' AS vztah,
    keys(r) AS atributy,
    [k IN keys(r) | {atribut: k, hodnota: r[k], typ: toString(type(r[k]))}] AS atributy_s_hodnotami;

// 11. VZTAH JE_PRIDELENA - VŠECHNY ATRIBUTY
// -------------------------------------------
MATCH ()-[r:JE_PRIDELENA]->()
WITH r LIMIT 1
RETURN 
    'JE_PRIDELENA' AS vztah,
    keys(r) AS atributy,
    [k IN keys(r) | {atribut: k, hodnota: r[k], typ: toString(type(r[k]))}] AS atributy_s_hodnotami;

// 12. VZTAH VYHLASUJE_ZAKAZKU - VŠECHNY ATRIBUTY
// -------------------------------------------
MATCH ()-[r:VYHLASUJE_ZAKAZKU]->()
WITH r LIMIT 1
RETURN 
    'VYHLASUJE_ZAKAZKU' AS vztah,
    keys(r) AS atributy,
    [k IN keys(r) | {atribut: k, hodnota: r[k], typ: toString(type(r[k]))}] AS atributy_s_hodnotami;

// 13. VZTAH POCHAZI_Z - VŠECHNY ATRIBUTY
// -------------------------------------------
MATCH ()-[r:POCHAZI_Z]->()
WITH r LIMIT 1
RETURN 
    'POCHAZI_Z' AS vztah,
    keys(r) AS atributy,
    [k IN keys(r) | {atribut: k, hodnota: r[k], typ: toString(type(r[k]))}] AS atributy_s_hodnotami;

// 14. VZTAH VLASTNI_PODIL - VŠECHNY ATRIBUTY
// -------------------------------------------
MATCH ()-[r:VLASTNI_PODIL]->()
WITH r LIMIT 1
RETURN 
    'VLASTNI_PODIL' AS vztah,
    keys(r) AS atributy,
    [k IN keys(r) | {atribut: k, hodnota: r[k], typ: toString(type(r[k]))}] AS atributy_s_hodnotami;

// 15. VZTAH PODAVA_NABIDKU - VŠECHNY ATRIBUTY
// -------------------------------------------
MATCH ()-[r:PODAVA_NABIDKU]->()
WITH r LIMIT 1
RETURN 
    'PODAVA_NABIDKU' AS vztah,
    keys(r) AS atributy,
    [k IN keys(r) | {atribut: k, hodnota: r[k], typ: toString(type(r[k]))}] AS atributy_s_hodnotami;

// 16. KOMPLETNÍ PŘEHLED - VŠECHNY ENTITY A VZTAHY
// -------------------------------------------
// Zobrazí všechny entity a vztahy s jejich atributy
CALL db.schema.visualization()
YIELD nodes, relationships
RETURN nodes, relationships;

// 17. STATISTIKA ENTIT A VZTAHŮ
// -------------------------------------------
// Zobrazí počet uzlů a vztahů pro každý typ
MATCH (n)
WITH labels(n) AS labels, n
UNWIND labels AS label
WITH label, count(n) AS pocet
WHERE label IN ['Osoba', 'Firma', 'Zadavatel', 'Zakazka', 'Skola', 'Zdroj']
RETURN label AS entita, pocet
ORDER BY pocet DESC
UNION ALL
MATCH ()-[r]->()
WITH type(r) AS vztah, count(r) AS pocet
RETURN vztah AS entita, pocet
ORDER BY pocet DESC;

