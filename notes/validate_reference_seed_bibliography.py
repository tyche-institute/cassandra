#!/usr/bin/env python3
import hashlib, json, re
from pathlib import Path
root = Path(__file__).resolve().parents[1]
path = root / "paper" / "reference-seed-bibliography.md"
text = path.read_text(encoding="utf-8")
required = [
    "eIDAS-2014", "eIDAS2-2024", "EU-AI-Act-2024", "Trusted-list-format-2015",
    "ETSI-TS-119-612", "RFC-5280", "RFC-3161", "NIST-FIPS-203", "CABF-BRs", "PKIC",
    "Ellison", "Schneier", "Star", "Ruhleder", "Bowker", "Perez", "Lazer", "Salganik",
    "Cassandra: from governance infrastructure to evidence infrastructure",
    "does not validate trusted lists", "does not verify source signatures", "does not determine provider or service status",
]
forbidden_patterns = [
    r"Cassandra validates trusted lists",
    r"Cassandra verifies source signatures",
    r"Cassandra determines legal status",
    r"Cassandra provides public alerts",
    r"approved for publication",
    r"endorsed by (ETSI|NIST|PKI Consortium|CA/Browser Forum|European Union)",
]
errors=[]
for token in required:
    if token not in text:
        errors.append(f"missing required token: {token}")
for pat in forbidden_patterns:
    if re.search(pat, text, re.I):
        errors.append(f"forbidden pattern: {pat}")
cluster_headers = ["Primary legal and standards", "Scholarly and public-administration", "Tyche and adjacent-project", "Merge guidance", "Non-claims"]
for header in cluster_headers:
    if header not in text:
        errors.append(f"missing section: {header}")
result={
    "status":"ok" if not errors else "error",
    "errors":errors,
    "reference_seed_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
    "line_count":len(text.splitlines()),
    "official_source_rows": text.count("| eIDAS-") + text.count("| EU-AI") + text.count("| Trusted-list") + text.count("| ETSI-") + text.count("| RFC-") + text.count("| NIST-") + text.count("| CABF") + text.count("| PKIC"),
    "boundary":"reference drafting control only; not legal review, trusted-list validation, signature validation, supervision, public alerting, endorsement, or publication approval",
}
out=root/"notes/reference-seed-bibliography-validation-output.json"
out.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n", encoding="utf-8")
print(json.dumps(result, indent=2, sort_keys=True))
raise SystemExit(0 if not errors else 1)
