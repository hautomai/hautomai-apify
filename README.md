# apify

Classification scripts for Apify-sourced lead exports.

`classify.py` takes a raw lead export and a rules file and emits a filtered CSV,
using keyword rules to decide which companies match the target industries
(recruiting / staffing / HR by default, plus a Singapore-specific toggle).

`classify_descriptions.py` scores free-text company descriptions against the same
rule sets, which is useful when the export only has prose instead of a category.

## Usage

```bash
python3 classify.py raw_leads.csv classified.csv rules.json
python3 classify_descriptions.py raw_leads.csv scored.csv rules.json
```

Input and output CSVs are intentionally not included in this repository.
