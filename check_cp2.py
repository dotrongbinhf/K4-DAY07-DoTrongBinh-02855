import csv
import re
from pathlib import Path

D = Path("data/tiki-doi-tra")
REQ = ["doc_id", "title", "source_url", "retrieved_at", "document_version", "audience"]

mds = sorted(D.glob("*.md"))
rows = list(csv.DictReader(open(D / "sources.csv", encoding="utf-8")))

ids = []
auds = {}

for p in mds:
    frontmatter = p.read_text(encoding="utf-8").split("---")[1]
    raw_fm = dict(re.findall(r"^(\w+):\s*(.+)$", frontmatter, re.M))
    fm = {key: value.strip().strip('"').strip("'") for key, value in raw_fm.items()}

    ids.append(fm.get("doc_id"))
    audience = fm.get("audience")
    auds[audience] = auds.get(audience, 0) + 1

    valid = all(key in fm for key in REQ) and fm.get("doc_id") == p.stem
    print(f'{p.name:40} {"OK" if valid else "THIEU METADATA"}')

print("so file :", len(mds), "(can 5-10)")
print("csv     :", "khop" if sorted(row["doc_id"] for row in rows) == sorted(ids) else "LECH")
print("audience:", auds)