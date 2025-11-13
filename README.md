# MBA Thesis: Public Tenders Relationship Analysis - Czech Republic

This project downloads publicly available data about public tenders, companies, and people from **Czech Republic** sources, then visualizes relationships using Neo4j graph database.

## Geographic Focus: Czech Republic (Česká republika)

The project is specifically designed to collect and analyze data from Czech public procurement sources, Czech company registries, and related entities.

## Project Structure

```
.
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── config.py                 # Configuration settings
├── data/                     # Raw downloaded data
│   ├── tenders/
│   ├── companies/
│   └── people/
├── scripts/                  # Data processing scripts
│   ├── download_tenders.py
│   ├── download_companies.py
│   ├── download_people.py
│   ├── transform_to_neo4j.py
│   └── load_to_neo4j.py
├── neo4j/                    # Neo4j scripts and queries
│   ├── schema.cypher        # Database schema definition
│   └── example_queries.cypher
└── docs/                     # Additional documentation
    └── data_sources.md
```

## 🚀 Quick Start (For Beginners)

**New to programming?** Start here!

1. **Read [GET_STARTED.md](GET_STARTED.md)** - Complete step-by-step guide
2. **Or try the quick test:**
   ```bash
   # 1. Install dependencies
   pip install -r requirements.txt
   
   # 2. Set up Neo4j (see GET_STARTED.md)
   
   # 3. Test with one company IČO
   python scripts/test_single_company.py 27074358
   ```
   Replace `27074358` with a real Czech company IČO (8-digit number).

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Neo4j:
   - Install Neo4j Desktop or Community Edition
   - Create a new database
   - Update connection details in `config.py` or `.env` file

3. Configure data sources:
   - Create `.env` file with Neo4j connection details (see QUICK_START.md)
   - Add OpenCorporates API key to `.env` (optional but recommended)
   - See `docs/data_sources_cz.md` for Czech Republic-specific data sources

## Usage

1. Download data:
```bash
python scripts/download_tenders.py
python scripts/download_companies.py
python scripts/download_people.py
```

2. Transform data for Neo4j:
```bash
python scripts/transform_to_neo4j.py
```

3. Load data into Neo4j:
```bash
python scripts/load_to_neo4j.py
```

## Data Sources

- **Czech Republic Focus**: All data sources are configured for Czech Republic
- See `docs/data_sources_cz.md` for detailed Czech Republic data source information
- See `docs/data_sources.md` for general data source documentation

### Key Czech Data Sources:
- **Tenders**: EU TED (CZ filter), Věstník veřejných zakázek, NEN
- **Companies**: OpenCorporates (CZ jurisdiction), Obchodní rejstřík
- **People**: Extracted from company registries and public records

### Czech-Specific Fields:
- **IČO** (Identifikační číslo osoby): Company registration number
- **DIČ** (Daňové identifikační číslo): Tax identification number

## License

For academic/research purposes only.

