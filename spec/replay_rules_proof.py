"""Offline proof: replay spec/full_test_results.csv through old vs new extraction.build_extraction_result."""
import csv, importlib.util, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(sys.argv[1])
BASE = sys.argv[2]  # commit before the work
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "spec"))
import score  # noqa: E402
from app.features.ocr import extraction as new  # noqa: E402

old_src = subprocess.check_output(["git", "-C", str(ROOT), "show", f"{BASE}:backend/app/features/ocr/extraction.py"], text=True, encoding="utf-8")
spec = importlib.util.spec_from_loader("old_extraction", loader=None)
old = importlib.util.module_from_spec(spec)
exec(compile(old_src, "old_extraction.py", "exec"), old.__dict__)

def camel(s):
    p = s.split("_"); return p[0] + "".join(x.title() for x in p[1:])
SNAKE = score.ALL_FIELDS
FLAGS = {  # truth field -> flag keys that mean "suspect"
    "date": ["dateNeedsReview"], "time": ["timeNeedsReview"], "receipt_number": ["receiptNumberNeedsReview"],
    "operator_gstin": ["operatorGstinNeedsReview"], "consignor_gstin": ["consignorGstinNeedsReview"],
    "consignee_gstin": ["consigneeGstinNeedsReview"], "consignor_phone": ["consignorPhoneNeedsReview"],
    "consignee_phone": ["consigneePhoneNeedsReview"], "consignor_name": ["consignorNameNeedsReview"],
    "consignee_name": ["consigneeNameNeedsReview"], "to_place": ["toPlaceNeedsReview"],
    "from_place": ["fromPlaceNeedsReview"], "prepared_by": ["preparedByNeedsReview"],
    **{f: [camel(f) + "NeedsReview"] for f in ("package_count", "freight", "delivery_charge", "demurrage", "sgst", "cgst", "igst", "total_amount")},
}

def replay(mod, row):
    parsed = {camel(f): row.get(f, "") for f in SNAKE}
    out = mod.build_extraction_result(parsed)
    return {f: out[camel(f)] for f in SNAKE}, out

truth = score._load_ground_truth(ROOT / "spec" / "ground_truth.json")
rows = score._load_results(ROOT / "spec" / "full_test_results.csv")
res = {"before": [], "after": []}
false_flags, remaining = [], []
n_rows = 0
for run in ("A", "B"):
    seen, docs_b, docs_a = set(), [], []
    for row in (r for r in rows if r["run"] == run):
        t = truth.get(row["file"])
        if t is None:
            continue
        n_rows += 1
        pb, ob = replay(old, row)
        pa, oa = replay(new, row)
        for f in SNAKE:  # false flags over EVERY row (incl. duplicate photos)
            for fl in FLAGS.get(f, []):
                if oa.get(fl) and not ob.get(fl):
                    ok = score.score_value(f, t.get(f, ""), pa[f])[0]
                    false_flags.append((run, row["file"][-18:], f, fl, t.get(f, ""), pa[f], "NEW FLAG ON CORRECT VALUE" if ok else "new flag on wrong value (true positive)"))
        if id(t) in seen:
            continue
        seen.add(id(t))
        docs_b.append(score.score_document(t, pb)); docs_a.append(score.score_document(t, pa))
        for f in SNAKE:
            tv = t.get(f, "")
            if tv and not score.score_value(f, tv, pa[f])[0]:
                why = "OCR returned empty (absent data, not fixable)" if not row.get(f, "").strip() else "OCR returned wrong value, rules did not fix"
                remaining.append((run, row["file"][-18:], f, tv, row.get(f, ""), pa[f], why))
    res["before"].append(score.aggregate(docs_b)); res["after"].append(score.aggregate(docs_a))

def pct(a):
    return f"{a['strict']}/{a['total']} ({a['strict_pct']}%)"
print(f"rows replayed: {n_rows}")
for i, run in enumerate("AB"):
    print(f"\n## Run {run}: strict accuracy (unique receipts) before -> after")
    for k in ("overall", "core", "optional"):
        print(f"- {k}: {pct(res['before'][i][k])} -> {pct(res['after'][i][k])}")
    print("| field | before | after |\n|---|---|---|")
    for f in SNAKE:
        b, a = res["before"][i]["per_field"][f], res["after"][i]["per_field"][f]
        if a["total"]:
            print(f"| {f} | {pct(b)} | {pct(a)}{' *' if a['strict'] != b['strict'] else ''} |")
print("\n## Flags newly raised (after but not before)")
bad = [x for x in false_flags if x[-1].startswith("NEW FLAG ON CORRECT")]
print(f"FALSE FLAGS on correct values: {len(bad)}")
for x in false_flags:
    print("-", x)
print(f"\n## Still failing after rules: {len(remaining)}")
empty = [r for r in remaining if r[-1].startswith("OCR returned empty")]
print(f"empty-OCR (not fixable): {len(empty)}; wrong-value not fixed: {len(remaining) - len(empty)}")
for r in remaining:
    if not r[-1].startswith("OCR returned empty"):
        print("-", r)
