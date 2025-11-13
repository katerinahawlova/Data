# Quick Start Guide - Test Run with One Company

This guide will help you do a test run with one Czech company (by IČO).

## Step 1: Install Dependencies

Open terminal in this folder and run:
```bash
pip install -r requirements.txt
```

## Step 2: Set Up Neo4j (if you haven't already)

1. Download Neo4j Desktop from: https://neo4j.com/download/
2. Install and create a new database
3. Start the database
4. Note your password (you'll need it in Step 3)

## Step 3: Configure Connection

Create a file named `.env` in this folder with:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password_here
```

Replace `your_neo4j_password_here` with your actual Neo4j password.

## Step 4: Run Test Script

We'll test with one company IČO. You can either:
- Use the example script with a sample IČO
- Provide your own IČO to test

Run:
```bash
python scripts/test_single_company.py
```

This will:
1. Download company data for one IČO
2. Transform it for Neo4j
3. Load it into Neo4j
4. Show you how to query it

## Step 5: Verify in Neo4j

1. Open Neo4j Browser (usually at http://localhost:7474)
2. Run this query to see your company:
```cypher
MATCH (c:Company) RETURN c LIMIT 10
```

## What's Next?

Once this works, you can:
- Test with more companies
- Download tender data
- Build relationships between companies and tenders

