// Neo4j Schema Definition for MBA Thesis Project
// Public Tenders Relationship Analysis

// Create unique constraints for node IDs
CREATE CONSTRAINT tender_id IF NOT EXISTS FOR (t:Tender) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT company_id IF NOT EXISTS FOR (c:Company) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT org_id IF NOT EXISTS FOR (o:Organization) REQUIRE o.id IS UNIQUE;

// Create indexes for common query patterns
CREATE INDEX tender_status IF NOT EXISTS FOR (t:Tender) ON (t.status);
CREATE INDEX tender_publication_date IF NOT EXISTS FOR (t:Tender) ON (t.publication_date);
CREATE INDEX company_name IF NOT EXISTS FOR (c:Company) ON (c.name);
CREATE INDEX company_country IF NOT EXISTS FOR (c:Company) ON (c.country);
CREATE INDEX person_name IF NOT EXISTS FOR (p:Person) ON (p.name);

// Node Labels and Properties:
// 
// (:Tender)
//   - id (unique)
//   - title
//   - description
//   - value
//   - currency
//   - publication_date
//   - deadline
//   - status
//   - source
//
// (:Company)
//   - id (unique)
//   - name
//   - registration_number
//   - country
//   - address
//   - founded_date
//   - company_type
//   - status
//   - source
//
// (:Person)
//   - id (unique)
//   - name
//   - role
//   - nationality
//   - source
//
// (:Organization)
//   - id (unique)
//   - name
//   - type
//   - country
//
// Relationship Types:
//
// (:Company)-[:SUBMITTED_BID {bid_value, bid_date, status}]->(:Tender)
// (:Company)-[:WON {award_date, award_value}]->(:Tender)
// (:Person)-[:WORKS_FOR {position, start_date, end_date}]->(:Company)
// (:Person)-[:DIRECTS {role, appointment_date}]->(:Company)
// (:Organization)-[:PUBLISHED {publication_date}]->(:Tender)

