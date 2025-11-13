# What to Do Next?

## You Asked: "What should be the next step?"

Here's the answer! 🎯

## Recommended Next Steps

### 1. **Do a Test Run** (Start Here!)

Test the system with **one company IČO** to make sure everything works:

```bash
python scripts/test_single_company.py YOUR_ICO_HERE
```

**What you need:**
- A Czech company IČO (8-digit number)
- Neo4j installed and running
- Python dependencies installed

**Where to get an IČO:**
- Visit https://or.justice.cz and search for any company
- Or use a known company like `27074358` (Česká spořitelna)

**See [GET_STARTED.md](GET_STARTED.md) for detailed instructions!**

### 2. **If Test Works: Expand to More Companies**

Once the test works, you can:
- Run the test script with multiple IČOs
- Or modify `scripts/download_companies.py` to download many companies

### 3. **Add Tender Data**

After companies work, add tender data:
```bash
python scripts/download_tenders.py
```

### 4. **Build Relationships**

The system will automatically create relationships when you:
- Link companies to tenders (who bid, who won)
- Link people to companies (directors, employees)

## About Data Sources

**You asked:** "Do you need me to define specific data sources?"

**Answer:** The system is already configured for Czech Republic! But you can:

### Option A: Use What's Already Set Up
- **OpenCorporates API** - Already configured (works with or without API key)
- **EU TED** - Already configured for Czech Republic
- **Obchodní rejstřík** - Structure ready, needs manual CSV or web scraping

### Option B: Add Your Own Data Sources
If you have:
- CSV files with company data
- CSV files with tender data
- Other data sources

Just place them in:
- `data/companies/raw/` for company CSVs
- `data/tenders/raw/` for tender CSVs

Then use:
```bash
python scripts/download_companies.py  # Has load_from_csv() method
python scripts/download_tenders.py    # Has load_from_csv() method
```

### Option C: Tell Me Your Data Sources
If you have specific data sources you want to use, tell me:
- What is the source? (website, API, CSV file, etc.)
- What data does it have? (companies, tenders, people?)
- How do you access it? (API key, download link, etc.)

I can help you integrate it!

## Current Status

✅ **What's Ready:**
- Project structure
- Download scripts (for OpenCorporates, EU TED)
- Transformation scripts
- Neo4j loading scripts
- Test script for one company

⏳ **What Needs Your Input:**
- Which IČO to test with
- Whether you have CSV files to import
- Whether you want to add other data sources
- Neo4j connection details

## Quick Decision Tree

**"I want to test right now!"**
→ Read [GET_STARTED.md](GET_STARTED.md) and run the test script

**"I have CSV files with data"**
→ Place them in `data/companies/raw/` or `data/tenders/raw/` and use `load_from_csv()`

**"I want to use a different data source"**
→ Tell me what it is and I'll help you integrate it

**"I want to understand how it works first"**
→ Read the scripts in `scripts/` folder - they have comments explaining each step

## Need Help?

1. Check [GET_STARTED.md](GET_STARTED.md) for setup help
2. Check error messages - they usually tell you what's wrong
3. Common issues:
   - Neo4j not running → Start it in Neo4j Desktop
   - Wrong password → Check `.env` file
   - Missing packages → Run `pip install -r requirements.txt`

## My Recommendation

**Start with the test script!** It's the fastest way to:
1. Verify everything works
2. See how the system processes data
3. Understand the workflow
4. Get comfortable with the tools

Then we can expand from there! 🚀

