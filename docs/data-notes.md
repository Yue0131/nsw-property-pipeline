# Data notes

Filled in from the official "Current Property Sales Data File Format (2001 to Current)" guide
and my own exploration. Do not guess.

## File layout
- Download source: https://www.valuergeneral.nsw.gov.au/__psi/weekly/YYYYMMDD.zip, opened in a browser.
  The official page (https://valuation.property.nsw.gov.au/embed/propertySalesInformation) shows
  "Content cannot be accessed" for its file list (Cloudflare bot protection, ~June 2026).
  URL pattern from github.com/jameselks/nsw-property-sales-data-cleaner, confirmed by downloading 4 files.
- Zip naming: YYYYMMDD.zip, the Monday of the reporting week.
- Zip contents: creative_commons.txt (CC Attribution, Australian port, no version, dated 2015-09-21)
  plus one .DAT per 3-digit code (~130 files in 20261019.zip).
- .DAT naming: <3-digit code>_SALES_DATA_NNME_<DDMMYYYY>.DAT (date is DDMMYYYY, zip name is YYYYMMDD).
  Code meaning: TBC. "NNME": TBC.
- Delimiter: semicolon `;`. Every line also ends with `;`, so splitting gives one extra empty field.
- Encoding: ASCII (`file` output).
- Line ending: LF.
- Structure: multi-record-type file. First field = record type. Seen so far: A, B, C, D.

## Record types
| Record type | What it represents | Key fields |
| --- | --- | --- |
| A | TBC (PDF) | |
| B | TBC (PDF) | |
| C | TBC (PDF) | |
| D | TBC (PDF) | |

## Field notes
| Field | Type | Example | Issues found |
| --- | --- | --- | --- |
|  |  |  |  |

## Data problems found during exploration
- [ ] Is the 3-digit code in the file name the same as the code in each record?
- [ ] B, C and D lines share their first 4 fields. Is that the key that links them?
- [ ] One B line had two D lines (P and V). Is B → D one-to-many?