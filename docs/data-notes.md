# Data notes

Sources: the official fact sheet "Current Property Sales Data File (Format 2001 - current)", May 2020
(`data/reference/Current_Property_Sales_Data_File_Format_2001_to_Current.pdf`), and my own exploration of
the 20261019 weekly file. Where the guide and the real files disagree, both are written down. Do not guess.

## File layout
- Download source: https://www.valuergeneral.nsw.gov.au/__psi/weekly/YYYYMMDD.zip, opened in a browser.
  The official page (https://valuation.property.nsw.gov.au/embed/propertySalesInformation) shows
  "Content cannot be accessed" for its file list (Cloudflare bot protection, ~June 2026).
  URL pattern from github.com/jameselks/nsw-property-sales-data-cleaner, confirmed by downloading 4 files.
- Zip naming: YYYYMMDD.zip, the Monday of the reporting week.
- Zip contents: creative_commons.txt (CC Attribution, Australian port, no version, dated 2015-09-21)
  plus one .DAT per district (~130 files in 20261019.zip).
- .DAT naming: `<district code>_SALES_DATA_NNME_<DDMMYYYY>.DAT`
  - The 3-digit prefix matches the District Code in the A record (checked on file 043).
  - Date in the .DAT name is DDMMYYYY; the zip name is YYYYMMDD.
  - "NNME": not explained in the guide. TBC.
- File structure: delimited flat ASCII (guide), confirmed by `file` ("ASCII text").
- Delimiter: semicolon `;`. Empty fields appear as `;;`. Every record ends with a trailing `;`,
  so splitting a line gives one extra empty field at the end.
- Line ending: LF.
- Multi-record-type file: the first field is the record type. A is first, Z is last.

## Record types
| Record type | What it represents | Key fields |
| --- | --- | --- |
| A | Header, first record. File type, district code, download date/time | district_code |
| B | One sale: property address and sale details | district_code, property_id, sale_counter |
| C | Property legal description. **There can be several C records per property**; join their text without a space, in file order | district_code, property_id, sale_counter |
| D | Purchaser / vendor marker. Owner details are suppressed, only P or V is given | district_code, property_id, sale_counter |
| Z | Trailer, last record. Total records (incl. A and Z) and counts of B, C, D | — |

`sale_counter` is "unique for file" (guide), so it is **not** a global id. B, C and D link on
(district_code, property_id, sale_counter) within one file only.

## Field notes
Type in the guide: A = alphanumeric, N = numeric, Date. Size = maximum length. Req = required (Y/N).

### A — Header
| # | Field | Type | Size | Req | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | Record type | A | 1 | Y | `A` |
| 2 | File type | A | 12 | Y | `RTSALEDATA` |
| 3 | District code | A | 3 | Y | e.g. `077`; keep as string (leading zeros) |
| 4 | Download date/time | Date | 16 | Y | `CCYYMMDD HH24:MI` |
| 5 | Submitter's user id | A | 35 | N | |

### B — Sale
| # | Field | Type | Size | Req | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | Record type | — | 1 | Y | `B` |
| 2 | District code | A | 3 | Y | |
| 3 | Property id | A | 10 | Y | Guide says A here but N in C/D. Keep as string |
| 4 | Sale counter | A | 7 | Y | Unique within the file only |
| 5 | Download date/time | A | 16 | Y | `CCYYMMDD HH24:MI` |
| 6 | Property name | N | 40 | N | Guide says N, but it is a name. Treat as string |
| 7 | Unit number | A | 10 | N | Unit number + suffix, space separated |
| 8 | House number | A | 10 | N | Prefix + number + suffix, e.g. `A125B` |
| 9 | Street name | A | 38 | N | Name + type + suffix + locality descriptor, e.g. `Green Lane NW` |
| 10 | Locality (suburb) | A | 40 | N | Guide comment for this field is a copy-paste error (describes a date) |
| 11 | Post code | N | 4 | N | Keep as string |
| 12 | Area | N | 7.3 | N | e.g. `7777777.333` |
| 13 | Area type | A | 1 | N | `M` = square metres, `H` = hectares. Needed to convert units |
| 14 | Contract date | Date | 8 | Y | `CCYYMMDD` |
| 15 | Settlement date | Date | 8 | Y | `CCYYMMDD` |
| 16 | Purchase price | N | 12 | Y | Whole dollars (TBC: check for cents/zero) |
| 17 | Zoning | A | 4 | N | Codes in the Zone Codes guide |
| 18 | Nature of property | A | 1 | N | `V` = vacant, `R` = residence, `3` = other |
| 19 | Primary purpose | A | 20 | N | Guide: filled when nature = 3. Seen filled when nature = R too |
| 20 | Strata lot number | A | 5 | N | Strata properties only |
| 21 | Component code | A | 3 | N | Not explained in this guide. TBC |
| 22 | Sale code | A | 3 | N | Not explained in this guide. TBC |
| 23 | % interest of sale | A | 3 | N | Empty means 100% |
| 24 | Dealing number | A | 10 | Y | Candidate for a cross-file sale id. TBC in phase 1 |

Observed: a real B record has exactly 24 fields plus the trailing empty one, matching the guide.

### C — Legal description
| # | Field | Type | Size | Req | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | Record type | A | 1 | Y | `C` |
| 2 | District code | A | 3 | Y | |
| 3 | Property id | N | 10 | Y | |
| 4 | Sale counter | N | 7 | Y | |
| 5 | Download date/time | Date | 16 | Y | |
| 6 | Property legal description | A | 70 | Y | Cut at 70 chars; multiple C records are joined without a space |

### D — Purchaser / vendor
| # | Field | Type | Size | Req | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | Record type | A | 1 | Y | `D` |
| 2 | District code | A | 3 | Y | |
| 3 | Property id | N | 10 | Y | |
| 4 | Sale counter | N | 7 | Y | |
| 5 | Download date/time | Date | 16 | Y | |
| 6 | Purchaser / vendor | A | 1 | Y | `P` = purchaser, `V` = vendor |

Observed: real D records have **5 extra empty fields** after field 6 (suppressed owner details).
The parser must not assume the field count in the guide.

### Z — Trailer
| # | Field | Type | Size | Req | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | Record type | A | 1 | Y | `Z` |
| 2 | Total records | N | 12 | Y | Includes A and Z |
| 3 | Total B records | N | 12 | Y | |
| 4 | Total C records | N | 12 | Y | |
| 5 | Total D records | N | 12 | N | |

The Z counts give a free quality check: counted rows must equal the trailer.

## Data problems found during exploration
- [x] Is the 3-digit file name code the district code? Yes, matches the A record (file 043).
- [x] Do B, C, D link on their first fields? Yes: district + property id + sale counter (guide).
- [x] One B had two D lines (P and V): yes, one-to-many, one per party.
- [ ] Z trailer present in every file? Check with `tail -1` on several files.
- [ ] Does the same sale (same dealing number) appear in more than one weekly file?
- [ ] Guide types disagree between records (property id A vs N; property name N). Store ids as strings.
- [ ] D records have more fields than the guide lists.
- [ ] Primary purpose filled when nature = R, not only when nature = 3.
- [ ] Meaning of NNME, component code, sale code: not in this guide (check Data Elements / user guide).
- [ ] Licence: the guide's own footer says "Creative Commons Attribution 4.0" but links to by-nd/4.0/au.
      A third conflicting statement; see decisions.md.
