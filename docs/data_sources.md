# Data Sources Documentation

This document describes the data sources used in the MBA Thesis project for collecting public tender, company, and people data.

**Note**: This project focuses on **Czech Republic** data sources. For Czech-specific detailed information, see [data_sources_cz.md](./data_sources_cz.md).

## Public Tenders

### 1. EU Tenders Electronic Daily (TED)
- **URL**: https://ted.europa.eu
- **API**: https://ted.europa.eu/api/v2.1
- **Description**: Official EU portal for public procurement notices
- **Data Available**: 
  - Tender notices
  - Award notices
  - Contract information
  - Publication dates and deadlines
- **Access**: 
  - Public access for browsing
  - API access may require registration
  - CSV/XML exports available
- **Usage**: Download CSV files or use API (if available)

### 2. National Tender Portals
Many countries have their own public procurement portals:
- **UK**: Contracts Finder (https://www.contractsfinder.service.gov.uk)
- **US**: SAM.gov (https://sam.gov)
- **Germany**: Vergabeportal (https://www.vergabeportal.de)
- **France**: BOAMP (https://www.boamp.fr)

**Note**: Each portal has different access methods (APIs, CSV exports, web scraping)

## Company Data

### 1. OpenCorporates
- **URL**: https://opencorporates.com
- **API**: https://api.opencorporates.com/v0.4
- **Description**: Largest open database of companies in the world
- **Data Available**:
  - Company registration details
  - Directors and officers
  - Company status
  - Incorporation dates
- **Access**: 
  - Free tier: Limited requests per day
  - Paid tier: Higher rate limits
  - API key required for production use
- **Rate Limits**: 
  - Free: ~500 requests/day
  - Paid: Varies by plan

### 2. National Company Registries
Many countries provide public access to company registries:
- **UK**: Companies House (https://find-and-update.company-information.service.gov.uk)
- **US**: SEC EDGAR (https://www.sec.gov/edgar.shtml)
- **EU**: Various national registries

### 3. Other Sources
- **Orbis**: Commercial database (requires subscription)
- **Bureau van Dijk**: Commercial database (requires subscription)

## People Data

### 1. Company Registries
People data is often extracted from company registries:
- Directors and officers from OpenCorporates
- Company House (UK) provides director information
- SEC filings (US) include executive information

### 2. Public Officials
- Government transparency portals
- Public procurement authority websites
- Official gazettes

### 3. Data Protection Considerations
⚠️ **Important**: When collecting people data:
- Ensure compliance with GDPR and local data protection laws
- Only collect publicly available information
- Consider anonymization for research purposes
- Check terms of service of data sources

## Data Collection Strategy

### Recommended Approach

1. **Start Small**: Begin with a specific country or region
2. **Use Official Sources**: Prefer government/official sources over commercial
3. **Respect Rate Limits**: Implement delays between API requests
4. **Store Raw Data**: Keep original data before transformation
5. **Document Sources**: Track where each piece of data came from

### Data Quality

- **Verification**: Cross-reference data from multiple sources when possible
- **Cleaning**: Remove duplicates and standardize formats
- **Validation**: Check for required fields before loading to Neo4j

## API Keys and Configuration

Create a `.env` file in the project root with:

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
OPENCORPORATES_API_KEY=your_api_key_here
```

## Legal and Ethical Considerations

1. **Terms of Service**: Review and comply with each data source's ToS
2. **Rate Limiting**: Respect API rate limits and implement delays
3. **Data Usage**: Ensure data is used only for research/academic purposes
4. **Privacy**: Be mindful of personal data and privacy regulations
5. **Attribution**: Credit data sources in your thesis

## Future Data Sources

Potential additional sources to consider:
- **LinkedIn**: Company and people connections (requires API access)
- **News Articles**: Extract relationships from news data
- **Social Media**: Public company and person connections
- **Patent Databases**: Company and inventor relationships
- **Research Publications**: Academic and industry connections

