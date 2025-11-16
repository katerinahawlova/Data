# Architecture & Workflow Design

## Data Flow Strategy

### Recommended Workflow: **Download All → Parse All → Transform All**

```
┌─────────────────┐
│  Download Phase │
│  (All Sources) │
└────────┬────────┘
         │
         ├─→ smlouvy.gov.cz (XML dump)
         ├─→ EU TED (JSON/XML)
         └─→ Věstník VZ (HTML/CSV)
         │
         ▼
┌─────────────────┐
│  Extract Phase  │
│  (All Sources)  │
└────────┬────────┘
         │
         ├─→ extract_smlouvy_contracts.py
         ├─→ extract_ted_tenders.py
         └─→ extract_vestnik_vz.py
         │
         ▼
┌─────────────────┐
│ Transform Phase │
│  (Unified)      │
└────────┬────────┘
         │
         └─→ transform_to_neo4j.py (merges all sources)
         │
         ▼
┌─────────────────┐
│   Load Phase    │
│   (Neo4j)       │
└─────────────────┘
```

## Why This Approach?

### ✅ Advantages:
1. **Incremental Updates**: Can add new months/ICOs without reprocessing old data
2. **Parallel Processing**: Download/parse can run in parallel
3. **Source Independence**: Each source parser is independent
4. **Flexible Filtering**: Filter by IČO at extraction or transform stage
5. **Data Tracking**: Track what's been processed with metadata files

## Incremental Update Strategy

### Tracking Processed Data

Each data source should track:
- **What months have been downloaded**
- **What months have been extracted**
- **What IČOs have been processed**
- **Last update timestamp**

### Metadata Structure

```json
{
  "source": "smlouvy_gov",
  "downloaded_months": ["2024-09", "2024-10", "2024-11"],
  "extracted_months": ["2024-09", "2024-10"],
  "processed_icos": ["00023698", "70886288"],
  "last_download": "2025-11-15T16:00:00",
  "last_extract": "2025-11-15T16:30:00"
}
```

### Incremental Workflow

```python
# Add new month without reprocessing old data
python3 scripts/run_pipeline.py \
  --source smlouvy_gov \
  --year 2024 --month 12 \
  --incremental

# Add new IČO to existing data
python3 scripts/run_pipeline.py \
  --source smlouvy_gov \
  --ico 00023698 \
  --year 2024 --month 9 \
  --incremental
```

## File Structure

```
data/
├── tenders/
│   ├── raw/                    # Raw downloads (never delete)
│   │   ├── smlouvy_gov/
│   │   │   ├── dump_2024_09.xml
│   │   │   └── dump_2024_10.xml
│   │   └── ted/
│   │       └── ted_2024_09.json
│   │
│   ├── extracted/              # Parsed contracts (JSON)
│   │   ├── smlouvy_gov/
│   │   │   ├── contracts_2024_09.json
│   │   │   └── contracts_2024_10.json
│   │   └── ted/
│   │       └── tenders_2024_09.json
│   │
│   └── metadata/              # Processing tracking
│       ├── smlouvy_gov_status.json
│       └── ted_status.json
│
├── companies/
│   ├── raw/
│   ├── extracted/
│   └── metadata/
│
└── transformed/               # Neo4j-ready data
    ├── neo4j_data_20241115.json
    └── neo4j_data_20241116.json
```

## Parser Architecture

### Base Parser Class

```python
# scripts/extract/extract_base.py
class BaseExtractor:
    def __init__(self, source_name):
        self.source_name = source_name
        self.metadata_file = f"data/tenders/metadata/{source_name}_status.json"
    
    def load_metadata(self):
        """Load processing status"""
        pass
    
    def save_metadata(self):
        """Save processing status"""
        pass
    
    def is_month_processed(self, year, month):
        """Check if month already extracted"""
        pass
    
    def extract(self, input_path, output_path, filter_ico=None):
        """Extract contracts - to be implemented by subclasses"""
        raise NotImplementedError
```

### Source-Specific Parsers

```python
# scripts/extract/extract_smlouvy_contracts.py
class SmlouvyExtractor(BaseExtractor):
    def extract(self, xml_path, output_path, filter_ico=None):
        """Parse XML and extract contracts"""
        # Filter by IČO if provided
        # Save to JSON
        # Update metadata
```

## Pipeline Orchestration

### Updated run_pipeline.py Structure

```python
def run_pipeline(
    sources=["smlouvy_gov"],  # Can specify multiple sources
    ico=None,                  # Filter by IČO
    year=None, month=None,     # Specific month
    incremental=True,          # Only process new data
    skip_download=False,       # Use existing downloads
    skip_extract=False,         # Use existing extracts
):
    """
    Orchestrates the full pipeline:
    1. Download (all sources)
    2. Extract (all sources)
    3. Transform (merge all sources)
    4. Load (Neo4j)
    """
    # Phase 1: Download
    if not skip_download:
        for source in sources:
            download_source(source, year, month, incremental)
    
    # Phase 2: Extract
    if not skip_extract:
        for source in sources:
            extract_source(source, ico, year, month, incremental)
    
    # Phase 3: Transform (merges all sources)
    transform_all_sources(ico)
    
    # Phase 4: Load
    load_to_neo4j(incremental=True)  # MERGE, don't replace
```

## Incremental Neo4j Updates

### MERGE Strategy

```cypher
// Instead of DELETE all, use MERGE
MERGE (c:Company {ico: $ico})
SET c.name = $name,
    c.last_updated = datetime()

MERGE (c1:Company {ico: $ico1})
MERGE (c2:Company {ico: $ico2})
MERGE (c1)-[r:CONTRACTED_WITH]->(c2)
SET r.value = $value,
    r.contract_date = $date,
    r.last_updated = datetime()
```

## Benefits of This Architecture

1. ✅ **Add new months**: Just download new month, extract, transform, load
2. ✅ **Add new IČOs**: Filter extraction for new IČO, merge into existing graph
3. ✅ **Add new sources**: Create new extractor, add to pipeline
4. ✅ **Reprocess if needed**: Can skip incremental flag to reprocess
5. ✅ **Parallel processing**: Download/extract can run in parallel
6. ✅ **Data integrity**: Raw data preserved, can always re-extract

