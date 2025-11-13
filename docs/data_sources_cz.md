# Czech Republic Data Sources

This document describes Czech Republic-specific data sources for the MBA Thesis project.

## Public Tenders (Veřejné zakázky)

### 1. Věstník veřejných zakázek
- **URL**: https://www.vestnikverejnychzakazek.cz
- **Description**: Official Czech public procurement bulletin
- **Data Available**:
  - Tender notices
  - Award notices
  - Contract information
  - Publication dates and deadlines
- **Access**: 
  - Public access for browsing
  - CSV/XML exports may be available
  - May require web scraping for bulk data
- **Language**: Czech
- **Usage**: Download CSV files or implement web scraping

### 2. NEN - Národní elektronický nástroj
- **URL**: https://nen.nipez.cz
- **Description**: National Electronic Tool for public procurement
- **Data Available**:
  - Electronic tendering system
  - Tender documents
  - Bid submissions
- **Access**: 
  - Registration may be required
  - API access may be available
- **Language**: Czech
- **Usage**: Check for API access or manual data export

### 3. EU TED (Tenders Electronic Daily) - Czech Filter
- **URL**: https://ted.europa.eu
- **API**: https://ted.europa.eu/api/v2.1
- **Description**: EU-wide public procurement portal, filtered for Czech Republic
- **Data Available**: 
  - Tender notices from Czech Republic
  - Award notices
  - Contract information
- **Access**: 
  - Public access for browsing
  - API access may require registration
  - Filter by country code: CZ
- **Usage**: Use API with country filter or download CSV files filtered for CZ

## Company Data

### 1. Obchodní rejstřík (Commercial Register)
- **URL**: https://or.justice.cz
- **Description**: Official Czech Commercial Register maintained by Ministry of Justice
- **Data Available**:
  - Company registration details
  - IČO (Company ID)
  - DIČ (Tax ID)
  - Directors and executives
  - Company status
  - Incorporation dates
  - Company address
- **Access**: 
  - Public access for individual company searches
  - Bulk data access may require special permission
  - Web scraping may be necessary
- **Language**: Czech
- **Important Fields**:
  - **IČO** (Identifikační číslo osoby): Unique company identifier
  - **DIČ** (Daňové identifikační číslo): Tax identification number
- **Usage**: 
  - Manual search and download
  - Web scraping (respect robots.txt and rate limits)
  - Check for official data export options

### 2. OpenCorporates - Czech Republic
- **URL**: https://opencorporates.com
- **API**: https://api.opencorporates.com/v0.4
- **Description**: Open database including Czech companies
- **Data Available**:
  - Company registration details
  - Directors and officers
  - Company status
  - Incorporation dates
- **Access**: 
  - Free tier: Limited requests per day (~500)
  - Paid tier: Higher rate limits
  - API key required for production use
- **Jurisdiction Code**: `cz`
- **Usage**: Use API with jurisdiction filter: `jurisdiction_code=cz`

### 3. ARES (Administrativní registr ekonomických subjektů)
- **URL**: https://wwwinfo.mfcr.cz/ares/
- **Description**: Administrative Register of Economic Subjects
- **Data Available**:
  - Company information
  - IČO and DIČ
  - Company status
- **Access**: 
  - Public API available
  - REST API: https://wwwinfo.mfcr.cz/ares/ares_es.html.cz
- **Language**: Czech
- **Usage**: Use ARES API for company lookups by IČO

## People Data

### 1. Obchodní rejstřík - Directors and Executives
- **Source**: Same as company data above
- **Data Available**:
  - Directors (jednatelé)
  - Board members (členové představenstva)
  - Supervisory board members (členové dozorčí rady)
  - Appointment dates
  - Resignation dates
- **Access**: Extract from company records in Obchodní rejstřík

### 2. Public Officials
- **Source**: Various government transparency portals
- **Data Available**:
  - Public procurement authority officials
  - Government officials
- **Access**: Check individual ministry and authority websites

## Data Collection Strategy for Czech Republic

### Recommended Approach

1. **Start with OpenCorporates**: 
   - Easiest API access
   - Good coverage of Czech companies
   - Use jurisdiction filter: `cz`

2. **Supplement with Obchodní rejstřík**:
   - Most comprehensive and official source
   - May require web scraping or manual collection
   - Provides IČO and DIČ numbers

3. **Use EU TED for Tenders**:
   - Filter for Czech Republic (country code: CZ)
   - Good coverage of EU-level tenders

4. **Add Věstník veřejných zakázek**:
   - For comprehensive Czech tender coverage
   - May require manual data collection or web scraping

### Czech-Specific Data Fields

- **IČO** (Identifikační číslo osoby): Company registration number (8 digits)
- **DIČ** (Daňové identikační číslo): Tax identification number (CZ + 8-10 digits)
- **Company Types**:
  - s.r.o. (společnost s ručením omezeným) - Limited liability company
  - a.s. (akciová společnost) - Joint stock company
  - v.o.s. (veřejná obchodní společnost) - General partnership
  - k.s. (komanditní společnost) - Limited partnership

### Legal and Ethical Considerations

1. **GDPR Compliance**: Ensure compliance with EU GDPR regulations
2. **Terms of Service**: Review and comply with each data source's ToS
3. **Rate Limiting**: Respect API rate limits and implement delays
4. **Data Usage**: Ensure data is used only for research/academic purposes
5. **Attribution**: Credit data sources in your thesis

## API Configuration

Update your `.env` file with:

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
OPENCORPORATES_API_KEY=your_api_key_here
```

## Useful Links

- **Ministry of Justice**: https://www.justice.cz
- **Ministry of Finance**: https://www.mfcr.cz
- **Czech Statistical Office**: https://www.czso.cz
- **Public Procurement Authority**: https://www.nipez.cz

## Notes

- Most Czech government websites are in Czech language
- IČO is the primary identifier for Czech companies
- Data formats may use Czech date formats and encoding (UTF-8)
- Consider using Czech language search terms for better results

