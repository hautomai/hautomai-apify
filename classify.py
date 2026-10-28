import csv
import json
import os
import sys
import re
from collections import Counter, OrderedDict

USAGE = "python3 classify.py <src.csv> <out.csv> <rules.json> [--require-sg]"


def _norm(s):
    s = str(s).strip().lower()
    s = s.replace("\u00ae", "(r)").replace("\u00b0", " (r)").replace("\u00a0", " ")
    return re.sub(r"\s+", " ", s)


def load_rules(path):
    d = json.load(open(path))
    return {_norm(k): v for k, v in d.get("YES", {}).items()}, {_norm(k): v for k, v in d.get("NO", {}).items()}


POS_KEYWORDS = [
    "recruit", "headhunt", "head hunting", "head-hunt", "executive search",
    "staffing", "staff & recruiting", "staff and recruiting", "employment", "manpower",
    "talent acquisition", "human capital", "hr consult", "placement", "search & selection",
]


def keyword_verdict(name, industry, specialties, desc):
    blob = " ".join([name, industry, specialties, desc]).lower()
    hits = [k for k in POS_KEYWORDS if k in blob]
    return "YES", "auto: " + (", ".join(sorted(set(hits))) if hits else "keyword hit")


def _is_singapore(r):
    cc = (r.get("company_country") or "").strip().lower()
    ccty = (r.get("company_city") or "").strip().lower()
    pc = (r.get("country") or "").strip().lower()
    if cc:
        return cc == "singapore"
    if ccty:
        return ccty == "singapore"
    return pc == "singapore"


def _loc(r):
    cc = (r.get("company_country") or "").strip()
    ccty = (r.get("company_city") or "").strip()
    pc = (r.get("country") or "").strip()
    return cc or ccty or pc or "unknown"


def main():
    if len(sys.argv) < 4:
        print(USAGE)
        sys.exit(2)
    src, out, rules_path = sys.argv[1], sys.argv[2], sys.argv[3]
    require_sg = "--require-sg" in sys.argv
    yes, no = load_rules(rules_path)

    with open(src, newline="") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames)
        rows = list(reader)

    out_fields = fields + ["in_target", "target_reason"]
    with open(out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        for r in rows:
            name = r.get("companyName") or r.get("company_name") or ""
            k = _norm(name)
            if k in no:
                verdict, reason = "NO", no[k]
            elif k in yes:
                verdict, reason = "YES", yes[k]
            else:
                ind = " ".join(str(r.get(f"companyIndustry/{i}") or "") for i in range(10))
                spl = " ".join(str(r.get(f"companySpecialties/{i}") or "") for i in range(30))
                verdict, reason = keyword_verdict(name, ind, spl, r.get("companyDescription") or r.get("company_description") or "")
            if require_sg and verdict == "YES" and not _is_singapore(r):
                verdict, reason = "NO", f"not Singapore-based ({_loc(r)})"
            nr = dict(r)
            nr["in_target"] = verdict
            nr["target_reason"] = reason
            writer.writerow(nr)

    cnt = Counter()
    uniq = {}
    for r in rows:
        k = _norm(r.get("companyName") or r.get("company_name") or "")
        verdict, reason = ("NO", no[k]) if k in no else ("YES", yes[k]) if k in yes else ("YES", "keyword")
        if require_sg and verdict == "YES" and not _is_singapore(r):
            verdict = "NO"
        cnt[verdict] += 1
        uniq.setdefault(k, verdict)
    print("rows written:", len(rows), "->", out)
    print("verdicts:", dict(cnt))
    print("unique companies:", len(uniq))


if __name__ == "__main__":
    main()