import csv
import re
from collections import OrderedDict

SRC = "check_descriptions.csv"
OUT = "check_descriptions_classified.csv"

YES = OrderedDict()
NO = OrderedDict()


def _norm(s):
    s = str(s).strip().lower()
    s = s.replace("\u00ae", "(r)").replace("\u00b0", " (r)").replace("\u00a0", " ")
    return re.sub(r"\s+", " ", s)


def y(name, reason):
    YES[_norm(name)] = reason


def n(name, reason):
    NO[_norm(name)] = reason


y("talentvis", "HR & recruitment consultancy")
y("resource consulting pte ltd", "recruitment & HR consulting")
y("timeoperformance", "recruitment, executive search & headhunting")
y("scientec consulting", "staffing & recruiting / executive search")
y("scientec consulting pte ltd", "staffing & recruiting / executive search")
y("it works consultancy pte ltd", "staffing & recruiting / executive search")
y("one nexus consulting pte ltd", "HR consulting & advisory")
y("peopleplus consulting pte ltd", "executive search & HR consulting")
y("calico(r) asia recruitment pte ltd", "legal recruitment consultancy")
y("career express pte ltd", "recruitment agency")
y("ayp group", "staffing & recruiting (+ HR tech)")
y("chris hunter pte ltd", "headhunting / recruitment (RecruitPlus)")
y("formative search pte ltd", "recruitment agency (legal/ESG)")
y("recruitplus consulting pte ltd", "recruitment & placement specialist")
y("asia hr", "HR consultancy & headhunting")
y("ultimate asset media recruitment", "media/advertising recruitment firm")
y("phildon", "recruitment & talent management consultancy")
y("olmec search pte ltd", "executive search & human capital consulting")
y("aci hr solutions", "executive search / recruitment & staffing")
y("icube consortium pte ltd", "HR capability consulting")
y("jobplus employment agency jobplus pte ltd", "employment agency / executive search")
y("jobone pte ltd", "recruitment consultancy")
y("jlegal", "legal recruitment consultancy")
y("executive search firm", "professional recruitment services")
y("matix  the talent consulting company", "talent consulting / staffing & recruiting")
y("doris cheng  associates pte ltd", "technical recruitment for tech MNCs")
y("wisenet asia pte ltd", "HR services & staffing")
y("assure recruitment pte ltd", "employment agency")
y("inter island", "recruitment & staffing firm")
y("itforce singapore pte ltd", "IT services + IT recruitment (staffing)")
y("volt  singapore", "commerce & industry recruitment / headhunting")
y("spearing search consultancy", "HR & recruitment search consultancy")
y("connect energy services pte ltd", "workforce mgmt & recruitment (oil & gas)")
y("whitestone consulting pte ltd", "executive search firm")
y("kingsforce management services pte ltd", "HR & staffing consultancy")
y("page personnel singapore", "recruitment consultancy")
y("hr transitions", "HR/career-transition consulting per name")
y("evolution recruitment solutions pte ltd singapore", "IT & digital recruitment consultancy")
y("tempteam pte ltd", "recruitment agency (JuhlerGroup)")
y("sg1 hro pte ltd", "HR outsourcing (staffing-adjacent)")
y("global talent solutions", "boutique recruitment / executive search")
y("searchplus asia pte ltd", "executive search firm")
y("absolute search recruitment agency", "recruitment agency")
y("ambition", "recruitment consultancy")
y("dezire technologies", "IT services + contract/permanent staffing")
y("nsearch global pte ltd", "staffing / executive search")
y("reiser corporation  executive search", "boutique executive search")
y("focuscore singapore", "executive/team recruitment")
y("decodehrcom", "HR consulting & advisory")
y("elite global partners pte ltd", "HR resourcing consultancy")
y("search lab", "executive search & talent management")
y("executive workplace", "executive search / headhunting")
y("jb", "executive-level talent placement")

n("addedsport", "sports/athlete management firm")
n("zahara", "cosmetics brand (not a recruitment firm)")
n("fieldwork 360 (r)", "market research fieldwork agency")
n("execoursescom", "training/education provider")
n("channel partners pte ltd", "channel strategy consulting (partner-recruitment != job recruitment)")
n("hreasily", "HR software product")
n("payrollserve", "payroll services provider")
n("contact singapore", "SG government agency (row description is a data mismatch)")
n("ministry of manpower", "SG government agency (row description is a data mismatch)")
n("headhunt", "recruitment newspaper / media, not a consultancy")
n("hatchme", "AI job portal / tech product")


def classify(name):
    k = _norm(name)
    if k in YES:
        return "YES", YES[k]
    if k in NO:
        return "NO", NO[k]
    return "MISSING", "no rule matched"


with open(SRC, newline="") as f:
    reader = csv.DictReader(f)
    fields = list(reader.fieldnames)
    rows = list(reader)

extra = ["in_target", "target_reason"]
out_fields = fields + extra

with open(OUT, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=out_fields)
    writer.writeheader()
    for r in rows:
        verdict, reason = classify(r.get("companyName") or "")
        nr = dict(r)
        nr["in_target"] = verdict
        nr["target_reason"] = reason
        writer.writerow(nr)

from collections import Counter

cnt = Counter()
for r in rows:
    verdict, _ = classify(r.get("companyName") or "")
    cnt[verdict] += 1

miss = sorted({k for k in (_norm(r.get("companyName") or "") for r in rows) if k not in YES and k not in NO})
uniq = {_norm(r.get("companyName") or "") for r in rows}
covered = sum(1 for k in uniq if k in YES or k in NO)
print("rows written:", len(rows))
print("verdicts:", dict(cnt))
print("rule coverage:", covered, "/", len(uniq), "unique companies")
print("no-rule companies:", miss)