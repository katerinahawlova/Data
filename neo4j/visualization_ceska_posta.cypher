// ============================================
// VIZUALIZACE: ČESKÁ POŠTA A JEJÍ DODAVATELÉ
// ============================================

// 1. ZÁKLADNÍ VIZUALIZACE - ČESKÁ POŠTA A DODAVATELÉ
// ----------------------------------------------------------------
// Zobrazí Českou poštu jako zadavatele, zakázky a dodavatele
MATCH (zv:Zadavatel {ico: "47114983"})-[r1:VYHLASUJE_ZAKAZKU]->(z:Zakazka)<-[r2:JE_PRIDELENA]-(f:Firma)
RETURN zv, z, f, r1, r2
LIMIT 50;

// 2. VIZUALIZACE S FILTREM - POUZE ZAKÁZKY S HODNOTOU
// ----------------------------------------------------------------
// Zobrazí pouze zakázky, které mají hodnotu
MATCH (zv:Zadavatel {ico: "47114983"})-[r1:VYHLASUJE_ZAKAZKU]->(z:Zakazka)<-[r2:JE_PRIDELENA]-(f:Firma)
WHERE r2.hodnota IS NOT NULL OR z.hodnota IS NOT NULL
RETURN zv, z, f, r1, r2
LIMIT 50;

// 3. VIZUALIZACE S AGGREGACÍ - DODAVATELÉ S POČTEM ZAKÁZEK
// ----------------------------------------------------------------
// Zobrazí Českou poštu a dodavatele s počtem zakázek (pro lepší přehled)
MATCH (zv:Zadavatel {ico: "47114983"})-[r1:VYHLASUJE_ZAKAZKU]->(z:Zakazka)<-[r2:JE_PRIDELENA]-(f:Firma)
WITH zv, f, count(z) AS pocet_zakazek, sum(r2.hodnota) AS celkova_hodnota
RETURN zv, f, pocet_zakazek, celkova_hodnota
ORDER BY pocet_zakazek DESC
LIMIT 30;

// 4. KOMPLETNÍ VIZUALIZACE - VŠECHNY VZTAHY
// ----------------------------------------------------------------
// Zobrazí Českou poštu se všemi vztahy (zakázky, dodavatelé, osoby ve funkci)
MATCH (cp:Zadavatel {ico: "47114983"})
OPTIONAL MATCH (cp)-[r1:VYHLASUJE_ZAKAZKU]->(z:Zakazka)<-[r2:JE_PRIDELENA]-(f:Firma)
OPTIONAL MATCH (cp_firma:Firma {ico: "47114983"})<-[r3:VYKONAVA_FUNKCI]-(o:Osoba)
RETURN cp, z, f, o, r1, r2, r3
LIMIT 100;

// 5. VIZUALIZACE PODLE HODNOTY - NEJVĚTŠÍ ZAKÁZKY
// ----------------------------------------------------------------
// Zobrazí pouze největší zakázky (top 20 podle hodnoty)
MATCH (zv:Zadavatel {ico: "47114983"})-[r1:VYHLASUJE_ZAKAZKU]->(z:Zakazka)<-[r2:JE_PRIDELENA]-(f:Firma)
WHERE r2.hodnota IS NOT NULL
WITH zv, z, f, r1, r2
ORDER BY r2.hodnota DESC
LIMIT 20
RETURN zv, z, f, r1, r2;

// 6. VIZUALIZACE S LABELY - PRO LEPSÍ ČITELNOST
// ----------------------------------------------------------------
// Zobrazí s popisky pro lepší čitelnost
MATCH (zv:Zadavatel {ico: "47114983"})-[r1:VYHLASUJE_ZAKAZKU]->(z:Zakazka)<-[r2:JE_PRIDELENA]-(f:Firma)
RETURN 
    zv.nazev AS zadavatel,
    z.nazev AS zakazka,
    z.hodnota AS hodnota_zakazky,
    f.nazev AS dodavatel,
    r2.hodnota AS hodnota_smlouvy
LIMIT 50;

// 7. VIZUALIZACE S VÁHAMI - VELIKOST PODLE HODNOTY
// ----------------------------------------------------------------
// Pro vizualizaci v Neo4j Browser - větší uzly = větší hodnota
MATCH (zv:Zadavatel {ico: "47114983"})-[r1:VYHLASUJE_ZAKAZKU]->(z:Zakazka)<-[r2:JE_PRIDELENA]-(f:Firma)
WHERE r2.hodnota IS NOT NULL
RETURN 
    zv,
    z,
    f,
    r1,
    r2,
    r2.hodnota AS edge_weight
ORDER BY r2.hodnota DESC
LIMIT 30;

// 8. VIZUALIZACE S OSOBAMI - STATUTÁRNÍ ORGÁN + ZAKÁZKY
// ----------------------------------------------------------------
// Zobrazí Českou poštu, osoby ve statutárním orgánu a zakázky s dodavateli
MATCH (cp_firma:Firma {ico: "47114983"})<-[r3:VYKONAVA_FUNKCI]-(o:Osoba)
WITH cp_firma, o, r3
LIMIT 10
MATCH (zv:Zadavatel {ico: "47114983"})-[r1:VYHLASUJE_ZAKAZKU]->(z:Zakazka)<-[r2:JE_PRIDELENA]-(f:Firma)
RETURN cp_firma, o, zv, z, f, r3, r1, r2
LIMIT 50;

