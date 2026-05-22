import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime, timezone

ws = Path('/home/anton/projects/cassandra')
date = '2026-05-20'
bundle_root = ws / 'bundles' / date
bundle_dir = bundle_root / 'snapshot-summary.json.bundle'
sources_dir = bundle_dir / 'sources'
sources_dir.mkdir(parents=True, exist_ok=True)

snap_manifest_path = ws / 'snapshots' / date / 'manifest.json'
norm_manifest_path = ws / 'normalized' / date / 'manifest.json'
diff_path = ws / 'diffs' / f'{date}.json'
baseline_path = ws / 'baselines' / f'{date}.json'
pointers_path = ws / 'notes' / 'pointers.json'
lotl_meta_path = ws / 'sources' / 'eu-lotl.xml.meta.json'

snap = json.loads(snap_manifest_path.read_text())
norm = json.loads(norm_manifest_path.read_text())
diff = json.loads(diff_path.read_text())

def now_z():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def sha256_path(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

artifact = {
    'schema': 'urn:tyche:cassandra:snapshot-summary:0.1',
    'created_at': now_z(),
    'date': date,
    'workspace': str(ws),
    'scope': 'Research-only structural observation of public LOTL-derived trusted-list snapshots.',
    'caveats': [
        'This artifact does not perform relying-party validation, signature verification, supervision, or legal-status determination.',
        'Fetch failures, parser results, and diffs are operational or structural observations only.',
        'Listed names are intentionally not reproduced in prose; detailed machine-readable snapshot files remain local workspace artifacts.',
    ],
    'inputs': {
        'lotl_url': 'https://ec.europa.eu/tools/lotl/eu-lotl.xml',
        'pointers_file': 'notes/pointers.json',
    },
    'counts': {
        'pointer_attempts': snap.get('count'),
        'fetched_content_files': snap.get('ok_count'),
        'fetch_errors': snap.get('error_count'),
        'normalization_inputs': norm.get('count'),
        'normalized_xml_artifacts': norm.get('ok_count'),
        'normalization_skips': norm.get('skipped_count'),
        'normalization_errors': norm.get('error_count'),
        'diff_current_record_count': diff.get('current_record_count'),
        'diff_change_count': diff.get('change_count'),
        'baseline_created': diff.get('baseline_created'),
    },
    'artifact_paths': {
        'snapshot_manifest': 'snapshots/2026-05-20/manifest.json',
        'normalized_manifest': 'normalized/2026-05-20/manifest.json',
        'diff': 'diffs/2026-05-20.json',
        'baseline': 'baselines/2026-05-20.json',
    },
    'hashes': {
        'snapshot_manifest_sha256': sha256_path(snap_manifest_path),
        'normalized_manifest_sha256': sha256_path(norm_manifest_path),
        'diff_sha256': sha256_path(diff_path),
        'baseline_sha256': sha256_path(baseline_path),
        'pointers_sha256': sha256_path(pointers_path),
    },
}
artifact_path = bundle_root / 'snapshot-summary.json'
artifact_path.parent.mkdir(parents=True, exist_ok=True)
artifact_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + '\n')
artifact_sha = sha256_path(artifact_path)

source_specs = [
    ('src-001', 'local_file', snap_manifest_path, 'sources/snapshot-manifest.json', 'local-run-manifest'),
    ('src-002', 'local_file', norm_manifest_path, 'sources/normalized-manifest.json', 'local-run-manifest'),
    ('src-003', 'local_file', diff_path, 'sources/diff-2026-05-20.json', 'local-run-manifest'),
    ('src-004', 'local_file', baseline_path, 'sources/baseline-2026-05-20.json', 'local-run-baseline'),
    ('src-005', 'local_file', pointers_path, 'sources/pointers.json', 'local-derived'),
]
if lotl_meta_path.exists():
    source_specs.append(('src-006', 'local_file', lotl_meta_path, 'sources/eu-lotl.xml.meta.json', 'primary-metadata'))

sources = []
for sid, kind, src, rel, reliability in source_specs:
    dst = bundle_dir / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    sources.append({
        'id': sid,
        'kind': kind,
        'path': rel,
        'sha256': {'algorithm': 'SHA-256', 'value': sha256_path(dst)},
        'accessed_at': now_z(),
        'reliability': reliability,
    })

pointer_url_record = {
    'schema': 'urn:tyche:cassandra:pointer-url-records:0.1',
    'created_at': now_z(),
    'source': 'snapshots/2026-05-20/manifest.json',
    'urls': [
        {'territory': it.get('territory'), 'url': it.get('url'), 'http_status': it.get('http_status'), 'sha256': it.get('sha256'), 'destination': it.get('destination')}
        for it in snap.get('items', [])
    ],
    'caveat': 'URLs are recorded as public LOTL-derived fetch targets for structural observation only.'
}
url_record_path = sources_dir / 'pointer-url-records.json'
url_record_path.write_text(json.dumps(pointer_url_record, indent=2, sort_keys=True) + '\n')
sources.append({
    'id': 'src-007',
    'kind': 'url_record',
    'path': 'sources/pointer-url-records.json',
    'sha256': {'algorithm': 'SHA-256', 'value': sha256_path(url_record_path)},
    'accessed_at': now_z(),
    'reliability': 'primary-url-record',
})

bundle_id = 'urn:tyche:mirror:bundle:' + artifact_sha[:32]
manifest = {
    'schema': 'urn:tyche:mirror:bundle:0.1',
    'schema_version': '0.1.0',
    'bundle_version': '0.1.0',
    'bundle_id': bundle_id,
    'bundle_created_at': now_z(),
    'created_at': now_z(),
    'canonicalization': 'mirror-bundle-json-v0.1',
    'created_by': {'name': 'Anton Sokolov', 'affiliation': 'Tyche Institute, Tallinn, Estonia'},
    'producer': {'lane': 'cassandra', 'project': 'Project Zeus', 'mode': 'research-only structural observation'},
    'attestation': {'signed': False, 'timestamped': False, 'caveat': 'No regulated trust-service output is created by this bundle.'},
    'artifact': {'path': '../snapshot-summary.json', 'sha256': {'algorithm': 'SHA-256', 'value': artifact_sha}, 'media_type': 'application/json'},
    'sources': sources,
    'claims_file': 'claims.json',
    'notes_file': 'notes.md',
    'assumptions': [
        'The bundle summarizes local run artifacts already present in the Cassandra workspace.',
        'Counts are parser and fetcher telemetry, not legal or supervisory findings.',
        'The first-day diff is empty because a baseline was initialized, not because absence of external change was established.',
    ],
    'dependencies': [
        {'name': 'python', 'path': '.venv/bin/python'},
        {'name': 'lxml', 'purpose': 'XML parsing and canonicalization'},
        {'name': 'requests-cache', 'purpose': 'HTTP retrieval support'},
    ],
}
(bundle_dir / 'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')

claims = {
    'schema': 'urn:tyche:mirror:claims:0.1',
    'bundle_id': bundle_id,
    'claims': [
        {
            'id': 'claim-001',
            'text': 'The 2026-05-20 Cassandra run recorded 43 LOTL-derived pointer attempts, 41 fetched content files, and 2 fetch errors.',
            'evidence': [{'source_id': 'src-001', 'pointer': 'sources/snapshot-manifest.json', 'locator': '$.count,$.ok_count,$.error_count'}],
            'risk': 'low',
            'safe_wording': 'The 2026-05-20 structural-observation run recorded 41 fetched snapshot files and 2 fetch errors among 43 LOTL-derived pointers; these are operational observations only.',
            'notes': 'No trusted-list legal status is inferred.',
        },
        {
            'id': 'claim-002',
            'text': 'The normalizer produced 31 normalized XML artifacts, skipped 9 non-XML/PDF-like files, and recorded 1 XML parse error for the 2026-05-20 run.',
            'evidence': [{'source_id': 'src-002', 'pointer': 'sources/normalized-manifest.json', 'locator': '$.ok_count,$.skipped_count,$.error_count'}],
            'risk': 'low',
            'safe_wording': 'The 2026-05-20 normalizer recorded 31 normalized XML artifacts, 9 non-XML skips, and 1 XML parse error as parser telemetry only.',
            'notes': 'No signature validity or legal effect is asserted.',
        },
        {
            'id': 'claim-003',
            'text': 'The 2026-05-20 diff initialized a day-one baseline over 31 comparable records and emitted zero structural changes.',
            'evidence': [{'source_id': 'src-003', 'pointer': 'sources/diff-2026-05-20.json', 'locator': '$.baseline_created,$.current_record_count,$.change_count'}],
            'risk': 'medium',
            'safe_wording': 'The 2026-05-20 diff run initialized a structural-observation baseline with 31 comparable records and therefore emitted an empty day-one diff.',
            'notes': 'The empty diff is a baseline artifact, not evidence of no legally relevant change.',
        },
    ]
}
(bundle_dir / 'claims.json').write_text(json.dumps(claims, indent=2, sort_keys=True) + '\n')

notes = """# Cassandra 2026-05-20 snapshot summary bundle

## Purpose

This MIRROR-style bundle records reproducible local provenance for the Cassandra lane's 2026-05-20 snapshot, normalization, baseline, and diff summary. It is a research-only evidence bundle for structural observation.

## Methodology

The lane used the locally pinned Python environment to fetch the public EU LOTL XML, extract national-list pointers, fetch the listed public endpoints, normalize XML-like artifacts, and initialize a day-one diff baseline. This bundle summarizes local manifests rather than reproducing every large raw XML/PDF file.

## Known gaps

- The bundle does not perform cryptographic signature verification.
- The bundle does not determine or assert legal status for any listed entity or service.
- Two endpoint fetches produced operational errors during the recorded run.
- One fetched content file produced an XML parse error in the normalizer.
- The day-one diff is empty because the baseline was initialized on this date.

## Assumptions

- Local workspace files referenced by hashes remain available for deeper replay.
- Counts are tool telemetry and should be reviewed before public use.
- Prose should remain aggregate-only unless Anton explicitly approves named-entity discussion.
"""
(bundle_dir / 'notes.md').write_text(notes)

errors = []
for rel in ['manifest.json', 'claims.json', 'notes.md']:
    if not (bundle_dir / rel).exists():
        errors.append(f'missing {rel}')
if sha256_path(artifact_path) != manifest['artifact']['sha256']['value']:
    errors.append('artifact hash mismatch')
for src in manifest['sources']:
    p = bundle_dir / src['path']
    if not p.exists():
        errors.append(f"missing source {src['path']}")
    elif sha256_path(p) != src['sha256']['value']:
        errors.append(f"source hash mismatch {src['path']}")

verification = {'status': 'ok' if not errors else 'fail', 'errors': errors, 'bundle_dir': str(bundle_dir), 'artifact': str(artifact_path)}
verify_path = bundle_dir / 'verification.json'
verify_path.write_text(json.dumps(verification, indent=2, sort_keys=True) + '\n')

new_files = [artifact_path, bundle_dir/'manifest.json', bundle_dir/'claims.json', bundle_dir/'notes.md', verify_path] + [bundle_dir/s['path'] for s in sources]
hashes = {str(p.relative_to(ws)): sha256_path(p) for p in new_files}
output_path = ws / 'notes' / 'bundle-2026-05-20-output.json'
output_path.write_text(json.dumps({'verification': verification, 'hashes': hashes}, indent=2, sort_keys=True) + '\n')
hashes[str(output_path.relative_to(ws))] = sha256_path(output_path)
print(json.dumps({'verification': verification, 'hashes': hashes}, indent=2, sort_keys=True))
