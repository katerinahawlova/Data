# Getting Started - Step by Step

## What You Need

1. **Python** (3.8 or newer) - [Download here](https://www.python.org/downloads/)
2. **Neo4j** - [Download Neo4j Desktop](https://neo4j.com/download/)
3. **A Czech company IČO** to test with (8-digit number)

## Step-by-Step Instructions

### Step 1: Install Python Dependencies

Open Terminal (Mac) or Command Prompt (Windows) in this folder and run:

```bash
pip install -r requirements.txt
```

**Troubleshooting:**
- If `pip` doesn't work, try `pip3`
- If you get permission errors, try `pip install --user -r requirements.txt`

### Step 2: Install and Set Up Neo4j

1. Download Neo4j Desktop from: https://neo4j.com/download/
2. Install and open Neo4j Desktop
3. Click "Add Database" → "Create a Local Database"
4. Give it a name (e.g., "MBA Thesis")
5. Set a password (remember this!)
6. Click "Start" to start the database

### Step 3: Create Configuration File

Create a file named `.env` in this folder (same folder as README.md).

**On Mac/Linux:**
```bash
touch .env
```

**On Windows:**
Create a new file named `.env` (no extension)

**Add this content to `.env`:**
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
```

Replace `your_password_here` with the password you set in Step 2.

### Step 4: Get a Company IČO to Test

You need a Czech company IČO (8-digit number). You can:

**Option A:** Use a known company IČO
- Example: `27074358` (Česká spořitelna)
- Or find any Czech company IČO online

**Option B:** Find one at https://or.justice.cz
- Search for any company
- The IČO is the 8-digit number

### Step 5: Run the Test

In Terminal/Command Prompt, run:

```bash
python scripts/test_single_company.py YOUR_ICO
```

Replace `YOUR_ICO` with the 8-digit IČO.

**Example:**
```bash
python scripts/test_single_company.py 27074358
```

### Step 6: Check the Results

1. **In Terminal:** You should see success messages
2. **In Neo4j Browser:**
   - Open Neo4j Desktop
   - Click "Open" next to your database
   - This opens Neo4j Browser (usually at http://localhost:7474)
   - Run this query:
   ```cypher
   MATCH (c:Company) RETURN c LIMIT 10
   ```
   - You should see your company!

### What If Something Goes Wrong?

**"Module not found" error:**
- Run `pip install -r requirements.txt` again

**"Cannot connect to Neo4j" error:**
- Check if Neo4j database is running (green "Start" button in Neo4j Desktop)
- Check if password in `.env` is correct
- Check if URI is `bolt://localhost:7687`

**"Company not found" error:**
- This is OK! The script will create test data
- You can still see how the system works

**Need help?** Check the error message - it usually tells you what's wrong!

## Next Steps

Once the test works:

1. **Try with more companies:**
   ```bash
   python scripts/test_single_company.py 12345678
   python scripts/test_single_company.py 87654321
   ```

2. **Download real data:**
   - See `QUICK_START.md` for next steps
   - Or check `docs/data_sources_cz.md` for data sources

3. **Explore Neo4j:**
   - Try queries from `neo4j/example_queries.cypher`
   - Visualize relationships in Neo4j Browser

## Common Questions

**Q: Do I need an API key?**
A: Not for the test! The test script will work without one (it creates sample data if needed).

**Q: What's an IČO?**
A: IČO (Identifikační číslo osoby) is an 8-digit Czech company registration number.

**Q: Can I use this without Neo4j?**
A: Yes! The script saves data to JSON files, so you can see the data even without Neo4j.

**Q: I'm stuck!**
A: Check the error message carefully - it usually tells you what's wrong. Common issues:
- Neo4j not running
- Wrong password
- Missing Python packages

