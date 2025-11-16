"""
Configuration file for MBA Thesis data collection and Neo4j integration.
Focused on Czech Republic (Česká republika) data sources.
"""

import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional

# Geographic Focus
COUNTRY = "Czech Republic"
COUNTRY_CODE = "CZ"
CURRENCY = "CZK"

# Neo4j Connection Settings
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Data directories
DATA_DIR = "data"
TENDERS_DIR = os.path.join(DATA_DIR, "tenders")
COMPANIES_DIR = os.path.join(DATA_DIR, "companies")
PEOPLE_DIR = os.path.join(DATA_DIR, "people")
TRANSFORMED_DIR = os.path.join(DATA_DIR, "transformed")

# Data source URLs and settings - Czech Republic specific
DATA_SOURCES = {
    "tenders": {
        "eu_ted_cz": {
            "base_url": "https://ted.europa.eu",
            "api_url": "https://ted.europa.eu/api/v2.1",
            "country_filter": "CZ",
            "enabled": True,
            "description": "EU TED filtered for Czech Republic tenders"
        },
        "vestnik_vz": {
            "base_url": "https://www.vestnikverejnychzakazek.cz",
            "enabled": True,
            "description": "Věstník veřejných zakázek - Czech public procurement portal"
        },
        "nen_zakazky": {
            "base_url": "https://nen.nipez.cz",
            "enabled": True,
            "description": "NEN - Národní elektronický nástroj (National Electronic Tool)"
        }
    },
    "companies": {
        "opencorporates_cz": {
            "base_url": "https://opencorporates.com",
            "api_url": "https://api.opencorporates.com/v0.4",
            "api_key": os.getenv("OPENCORPORATES_API_KEY", ""),
            "jurisdiction": "cz",
            "enabled": True,
            "description": "OpenCorporates API for Czech companies"
        },
        "obchodni_rejstrik": {
            "base_url": "https://or.justice.cz",
            "enabled": True,
            "description": "Obchodní rejstřík - Czech Commercial Register (requires web scraping or API access)"
        }
    },
    "people": {
        "obchodni_rejstrik_people": {
            "base_url": "https://or.justice.cz",
            "enabled": True,
            "description": "People data from Obchodní rejstřík (directors, executives)"
        }
    }
}

# Download settings
DOWNLOAD_SETTINGS = {
    "max_records": 10000,  # Limit for initial testing
    "batch_size": 100,
    "delay_between_requests": 1.0,  # seconds
    "timeout": 30,  # seconds
}

# Neo4j node and relationship labels
NEO4J_SCHEMA = {
    "nodes": {
        "Tender": {
            "properties": ["id", "title", "description", "value", "currency", "publication_date", "deadline", "status"]
        },
        "Company": {
            "properties": ["id", "name", "registration_number", "country", "address", "founded_date", "ico", "dic"]
        },
        "Person": {
            "properties": ["id", "name", "role", "company_id"]
        },
        "Organization": {
            "properties": ["id", "name", "type", "country"]
        }
    },
    "relationships": {
        "SUBMITTED_BID": {
            "from": "Company",
            "to": "Tender",
            "properties": ["bid_value", "bid_date", "status"]
        },
        "WON": {
            "from": "Company",
            "to": "Tender",
            "properties": ["award_date", "award_value"]
        },
        "WORKS_FOR": {
            "from": "Person",
            "to": "Company",
            "properties": ["position", "start_date", "end_date"]
        },
        "DIRECTS": {
            "from": "Person",
            "to": "Company",
            "properties": ["role", "appointment_date"]
        },
        "PUBLISHED": {
            "from": "Organization",
            "to": "Tender",
            "properties": ["publication_date"]
        }
    }
}

