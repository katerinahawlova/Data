// Example Cypher Queries for MBA Thesis Analysis
// Public Tenders Relationship Analysis

// ============================================
// BASIC EXPLORATION QUERIES
// ============================================

// 1. Count all nodes by type
MATCH (n)
RETURN labels(n)[0] AS node_type, count(n) AS count
ORDER BY count DESC;

// 2. Count all relationships by type
MATCH ()-[r]->()
RETURN type(r) AS relationship_type, count(r) AS count
ORDER BY count DESC;

// 3. View database statistics
MATCH (n)
OPTIONAL MATCH (n)-[r]->()
RETURN 
  count(DISTINCT n) AS total_nodes,
  count(DISTINCT r) AS total_relationships,
  count(DISTINCT labels(n)) AS node_types,
  count(DISTINCT type(r)) AS relationship_types;

// ============================================
// TENDER ANALYSIS
// ============================================

// 4. Find all tenders with their publishing organizations
MATCH (org:Organization)-[:PUBLISHED]->(t:Tender)
RETURN org.name AS organization, t.title AS tender_title, t.value AS value, t.status AS status
ORDER BY t.value DESC
LIMIT 50;

// 5. Find companies that submitted bids for tenders
MATCH (c:Company)-[r:SUBMITTED_BID]->(t:Tender)
RETURN c.name AS company, t.title AS tender, r.bid_value AS bid_value, t.value AS tender_value
ORDER BY r.bid_value DESC
LIMIT 50;

// 6. Find companies that won tenders
MATCH (c:Company)-[r:WON]->(t:Tender)
RETURN c.name AS company, t.title AS tender, r.award_value AS award_value, t.publication_date AS date
ORDER BY r.award_value DESC
LIMIT 50;

// 7. Find tenders by status
MATCH (t:Tender)
RETURN t.status AS status, count(t) AS count, avg(t.value) AS avg_value
ORDER BY count DESC;

// ============================================
// COMPANY ANALYSIS
// ============================================

// 8. Find companies with most tender wins
MATCH (c:Company)-[:WON]->(t:Tender)
WITH c, count(t) AS wins, sum(t.value) AS total_value
RETURN c.name AS company, c.country AS country, wins, total_value
ORDER BY wins DESC, total_value DESC
LIMIT 20;

// 9. Find companies with most bid submissions
MATCH (c:Company)-[:SUBMITTED_BID]->(t:Tender)
WITH c, count(t) AS submissions
RETURN c.name AS company, c.country AS country, submissions
ORDER BY submissions DESC
LIMIT 20;

// 10. Find companies by country
MATCH (c:Company)
RETURN c.country AS country, count(c) AS company_count
ORDER BY company_count DESC;

// ============================================
// PERSON/COMPANY RELATIONSHIPS
// ============================================

// 11. Find people who work for companies that won tenders
MATCH (p:Person)-[:WORKS_FOR|DIRECTS]->(c:Company)-[:WON]->(t:Tender)
RETURN p.name AS person, p.role AS role, c.name AS company, count(t) AS tenders_won
ORDER BY tenders_won DESC
LIMIT 30;

// 12. Find directors of companies
MATCH (p:Person)-[r:DIRECTS]->(c:Company)
RETURN p.name AS director, c.name AS company, r.role AS role, r.appointment_date AS appointment_date
LIMIT 50;

// 13. Find people connected to multiple companies
MATCH (p:Person)-[:WORKS_FOR|DIRECTS]->(c:Company)
WITH p, count(DISTINCT c) AS company_count
WHERE company_count > 1
RETURN p.name AS person, company_count
ORDER BY company_count DESC
LIMIT 30;

// ============================================
// NETWORK ANALYSIS
// ============================================

// 14. Find companies that bid on the same tenders (potential competitors)
MATCH (c1:Company)-[:SUBMITTED_BID]->(t:Tender)<-[:SUBMITTED_BID]-(c2:Company)
WHERE c1.id < c2.id
RETURN c1.name AS company1, c2.name AS company2, count(t) AS common_tenders
ORDER BY common_tenders DESC
LIMIT 30;

// 15. Find companies connected through shared directors
MATCH (p:Person)-[:DIRECTS]->(c1:Company), (p)-[:DIRECTS]->(c2:Company)
WHERE c1.id < c2.id
RETURN c1.name AS company1, c2.name AS company2, p.name AS shared_director
LIMIT 30;

// 16. Find paths between companies and tenders (up to 2 hops)
MATCH path = (c:Company)-[*1..2]-(t:Tender)
RETURN c.name AS company, t.title AS tender, length(path) AS path_length
LIMIT 50;

// ============================================
// COMPLEX ANALYSIS QUERIES
// ============================================

// 17. Find organizations that publish tenders won by companies with specific directors
MATCH (org:Organization)-[:PUBLISHED]->(t:Tender)<-[:WON]-(c:Company)<-[:DIRECTS]-(p:Person)
WHERE p.role CONTAINS 'Director'
RETURN org.name AS organization, p.name AS director, c.name AS company, count(t) AS tenders_won
ORDER BY tenders_won DESC
LIMIT 30;

// 18. Calculate win rate for companies
MATCH (c:Company)-[submitted:SUBMITTED_BID]->(t:Tender)
OPTIONAL MATCH (c)-[won:WON]->(t)
WITH c, count(submitted) AS total_bids, count(won) AS wins
RETURN c.name AS company, total_bids, wins, 
       CASE WHEN total_bids > 0 THEN round(100.0 * wins / total_bids, 2) ELSE 0 END AS win_rate_percent
ORDER BY win_rate_percent DESC, total_bids DESC
LIMIT 30;

// 19. Find clusters of companies (companies that frequently interact)
MATCH (c1:Company)-[:SUBMITTED_BID|WON]->(t:Tender)<-[:SUBMITTED_BID|WON]-(c2:Company)
WHERE c1.id < c2.id
WITH c1, c2, count(t) AS interactions
WHERE interactions >= 3
RETURN c1.name AS company1, c2.name AS company2, interactions
ORDER BY interactions DESC
LIMIT 30;

// 20. Find most influential people (directors of companies with most wins)
MATCH (p:Person)-[:DIRECTS]->(c:Company)-[:WON]->(t:Tender)
WITH p, c, count(t) AS wins, sum(t.value) AS total_value
RETURN p.name AS person, c.name AS company, wins, total_value
ORDER BY wins DESC, total_value DESC
LIMIT 20;

// ============================================
// VISUALIZATION QUERIES
// ============================================

// 21. Get subgraph for a specific company (all related entities)
MATCH path = (c:Company {name: 'Company Name'})-[*1..2]-(connected)
RETURN path
LIMIT 100;

// 22. Get subgraph for a specific tender
MATCH path = (t:Tender {id: 'TENDER-001'})-[*1..2]-(connected)
RETURN path
LIMIT 100;

// 23. Find all relationships for a person
MATCH (p:Person {name: 'Person Name'})-[r]-(connected)
RETURN p, r, connected
LIMIT 50;

