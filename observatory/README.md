# Cassandra Observatory

Static Cloudflare Pages surface for the Cassandra case study:

> Cassandra: from governance infrastructure to evidence infrastructure.

The dashboard is generated from local Cassandra observation artifacts, aggregate
tables, SVG figures, and optional EATF/AEP evidence packages.

## Production Setup

The scheduled workflow in `.github/workflows/cassandra-observatory.yml` runs the
observation lane, refreshes aggregate outputs, creates an EATF package receipt,
commits the new artifacts, and deploys `observatory/public` to Cloudflare Pages
when Cloudflare secrets are present.

Required GitHub secrets for signed EATF packages:

- `CASSANDRA_EATF_PRIVATE_KEY_PEM`
- `CASSANDRA_EATF_PUBLIC_KEY_PEM`

Optional timestamp secret:

- `CASSANDRA_EATF_TIMESTAMP_TSR_BASE64`

If no timestamp secret is provided, the workflow uses the EATF repository's test
timestamp fixture and the receipt makes that visible. That is useful for
reproducible research runs, but production publication should use a real
timestamp source.

Required GitHub secrets for Cloudflare deployment:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

Optional Cloudflare secret:

- `CLOUDFLARE_PROJECT_NAME` defaults to `cassandra-observatory`

## Local Build

```bash
python notes/aggregate_results.py \
  --workspace . \
  --output notes/aggregate-results-$(date -u +%F)-output.json \
  --csv notes/aggregate-results-table.csv

python notes/render_aggregate_figures.py \
  --workspace . \
  --aggregate-json notes/aggregate-results-$(date -u +%F)-output.json \
  --aggregate-csv notes/aggregate-results-table.csv \
  --output notes/figure-render-$(date -u +%F)-output.json \
  --figures-dir figures

python scripts/eatf_package_snapshot.py \
  --workspace . \
  --date "$(date -u +%F)" \
  --out-dir evidence

python scripts/build_observatory_index.py \
  --workspace . \
  --public-dir observatory/public
```

The static site can be served from `observatory/public`.

## Claim Boundary

EATF/AEP evidence packaging verifies package bytes and declared hashes. It does
not turn Cassandra into a relying-party validator and does not assert legal
status, signature validity, supervision, or public alerting.
