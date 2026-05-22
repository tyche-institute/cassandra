#!/usr/bin/env python3
"""Parse and normalize public trusted-list snapshots for research observation.

This script performs deterministic XML parsing and serialization for diffable
structural observation. It does not verify signatures, validate trusted-list
legal effect, supervise trust services, or determine any listed entity status.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
from typing import Any

from lxml import etree

TSL_NS = "http://uri.etsi.org/02231/v2#"
DS_NS = "http://www.w3.org/2000/09/xmldsig#"
XML_LIKE_SUFFIXES = {".xml", ".xtsl"}
RESEARCH_CAVEAT = (
    "Deterministic XML normalization and structural extraction for research "
    "observation only; not signature validation, supervision, legal-status "
    "determination, or relying-party processing."
)


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: pathlib.Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def collapse_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = " ".join(value.split())
    return text or None


def local_name(tag: str) -> str:
    return etree.QName(tag).localname if tag.startswith("{") else tag


def normalize_element_whitespace(element: etree._Element) -> None:
    """Collapse whitespace in text/tail nodes for stable observation diffs."""
    if element.text is not None:
        element.text = collapse_text(element.text)
    for child in element:
        normalize_element_whitespace(child)
        if child.tail is not None:
            child.tail = collapse_text(child.tail)


def canonicalize_xml(source: pathlib.Path) -> bytes:
    parser = etree.XMLParser(
        resolve_entities=False,
        remove_blank_text=True,
        remove_comments=False,
        huge_tree=True,
        recover=False,
    )
    tree = etree.parse(str(source), parser)
    root = tree.getroot()
    normalize_element_whitespace(root)
    # C14N provides deterministic namespace and attribute ordering. It is used
    # only for observation/diff stability and not as signature input.
    return etree.tostring(root, method="c14n", exclusive=False, with_comments=True)


def text_at(root: etree._Element, xpath: str, namespaces: dict[str, str]) -> str | None:
    values = root.xpath(xpath, namespaces=namespaces)
    if not values:
        return None
    first = values[0]
    if isinstance(first, etree._Element):
        return collapse_text(first.text)
    return collapse_text(str(first))


def first_text_at(element: etree._Element, xpath: str, namespaces: dict[str, str]) -> str | None:
    values = element.xpath(xpath, namespaces=namespaces)
    for value in values:
        if isinstance(value, etree._Element):
            text = collapse_text(" ".join(value.itertext()))
        else:
            text = collapse_text(str(value))
        if text:
            return text
    return None


def stable_observation_key(*parts: str | None) -> str:
    """Return a stable non-reversible key for machine-readable inventory diffs."""
    material = "\x1f".join(part or "" for part in parts).encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def element_fallback_key(element: etree._Element) -> str:
    data = etree.tostring(element, method="c14n", exclusive=False, with_comments=False)
    return hashlib.sha256(data).hexdigest()


def provider_service_inventory(root: etree._Element, namespaces: dict[str, str]) -> dict[str, Any]:
    """Extract hashed provider/service inventory for structural observation only.

    The resulting keys intentionally avoid raw listed names while remaining
    stable enough to explain provider/service count churn in machine-readable
    diff records. They are not identifiers for legal or supervisory use.
    """
    inventory_providers: list[dict[str, Any]] = []
    service_keys: list[str] = []
    providers = root.xpath(".//tsl:TrustServiceProvider", namespaces=namespaces)
    territory = text_at(root, ".//tsl:SchemeInformation/tsl:SchemeTerritory", namespaces)
    for provider_index, provider in enumerate(providers):
        provider_name = first_text_at(provider, "./tsl:TSPInformation/tsl:TSPName/tsl:Name", namespaces)
        provider_trade_name = first_text_at(provider, "./tsl:TSPInformation/tsl:TSPTradeName/tsl:Name", namespaces)
        provider_seed = provider_name or provider_trade_name or element_fallback_key(provider)
        provider_key = stable_observation_key("provider", territory, provider_seed)
        provider_services = provider.xpath("./tsl:TSPServices/tsl:TSPService", namespaces=namespaces)
        provider_service_keys: list[str] = []
        service_statuses: dict[str, int] = {}
        service_types: dict[str, int] = {}
        for service_index, service in enumerate(provider_services):
            service_name = first_text_at(service, "./tsl:ServiceInformation/tsl:ServiceName/tsl:Name", namespaces)
            service_type = first_text_at(service, "./tsl:ServiceInformation/tsl:ServiceTypeIdentifier", namespaces)
            service_status = first_text_at(service, "./tsl:ServiceInformation/tsl:ServiceStatus", namespaces)
            status_start = first_text_at(service, "./tsl:ServiceInformation/tsl:StatusStartingTime", namespaces)
            service_seed = service_name or element_fallback_key(service)
            service_key = stable_observation_key(
                "service",
                territory,
                provider_key,
                service_type,
                service_seed,
                status_start,
                str(service_index),
            )
            provider_service_keys.append(service_key)
            service_keys.append(service_key)
            if service_status:
                service_statuses[service_status] = service_statuses.get(service_status, 0) + 1
            if service_type:
                service_types[service_type] = service_types.get(service_type, 0) + 1
        inventory_providers.append({
            "provider_key": provider_key,
            "provider_index": provider_index,
            "service_count": len(provider_services),
            "service_keys": sorted(provider_service_keys),
            "service_status_counts": dict(sorted(service_statuses.items())),
            "service_type_counts": dict(sorted(service_types.items())),
            "caveat": "Hashed provider/service inventory for structural observation only; raw listed names omitted.",
        })
    return {
        "provider_count": len(providers),
        "provider_keys": sorted(provider["provider_key"] for provider in inventory_providers),
        "providers": sorted(inventory_providers, key=lambda provider: provider["provider_key"]),
        "service_count": len(service_keys),
        "service_keys": sorted(service_keys),
        "caveat": "Hashed inventory is not a legal-status or relying-party identifier.",
    }


def signature_shape(root: etree._Element) -> dict[str, Any]:
    ns = {"ds": DS_NS}
    signatures = root.xpath(".//ds:Signature", namespaces=ns)
    methods = sorted({
        alg
        for alg in root.xpath(".//ds:SignatureMethod/@Algorithm", namespaces=ns)
        if alg
    })
    digest_methods = sorted({
        alg
        for alg in root.xpath(".//ds:DigestMethod/@Algorithm", namespaces=ns)
        if alg
    })
    reference_count = len(root.xpath(".//ds:Reference", namespaces=ns))
    key_info_count = len(root.xpath(".//ds:KeyInfo", namespaces=ns))
    return {
        "signature_count": len(signatures),
        "signature_method_algorithms": methods,
        "digest_method_algorithms": digest_methods,
        "reference_count": reference_count,
        "key_info_count": key_info_count,
        "caveat": "Signature-shape observation only; no cryptographic verification performed.",
    }


def structural_summary(source: pathlib.Path) -> dict[str, Any]:
    parser = etree.XMLParser(resolve_entities=False, remove_blank_text=False, huge_tree=True, recover=False)
    tree = etree.parse(str(source), parser)
    root = tree.getroot()
    ns = {"tsl": TSL_NS, "ds": DS_NS}
    service_providers = root.xpath(".//tsl:TrustServiceProvider", namespaces=ns)
    services = root.xpath(".//tsl:TSPService", namespaces=ns)
    return {
        "root_name": local_name(root.tag),
        "root_namespace": etree.QName(root).namespace,
        "scheme_territory": text_at(root, ".//tsl:SchemeInformation/tsl:SchemeTerritory", ns),
        "sequence_number": text_at(root, ".//tsl:SchemeInformation/tsl:TSLSequenceNumber", ns),
        "issue_date_time": text_at(root, ".//tsl:SchemeInformation/tsl:ListIssueDateTime", ns),
        "next_update": text_at(root, ".//tsl:SchemeInformation/tsl:NextUpdate/tsl:dateTime", ns),
        "trust_service_provider_count": len(service_providers),
        "tsp_service_count": len(services),
        "provider_service_inventory": provider_service_inventory(root, ns),
        "signature_shape": signature_shape(root),
    }


def iter_snapshot_items(snapshot_dir: pathlib.Path) -> list[pathlib.Path]:
    items = []
    for path in sorted(snapshot_dir.iterdir()):
        if path.name == "manifest.json" or path.name.endswith(".meta.json"):
            continue
        if path.is_file():
            items.append(path)
    return items


def normalize_snapshot(workspace: pathlib.Path, date: str, limit: int | None = None) -> dict[str, Any]:
    snapshot_dir = workspace / "snapshots" / date
    if not snapshot_dir.exists():
        raise FileNotFoundError(f"snapshot directory not found: {snapshot_dir}")
    output_dir = workspace / "normalized" / date
    output_dir.mkdir(parents=True, exist_ok=True)
    items = iter_snapshot_items(snapshot_dir)
    if limit is not None:
        items = items[:limit]

    records: list[dict[str, Any]] = []
    ok_count = 0
    skipped_count = 0
    error_count = 0
    for source in items:
        rel_source = source.relative_to(workspace)
        suffix = source.suffix.lower()
        record: dict[str, Any] = {
            "source": str(rel_source),
            "source_sha256": sha256_file(source),
            "source_bytes": source.stat().st_size,
        }
        if suffix not in XML_LIKE_SUFFIXES:
            record.update({
                "status": "skipped_non_xml",
                "reason": f"suffix {source.suffix!r} is outside XML-like set {sorted(XML_LIKE_SUFFIXES)}",
            })
            skipped_count += 1
            records.append(record)
            continue
        try:
            normalized_bytes = canonicalize_xml(source)
            destination = output_dir / (source.name + ".normalized.xml")
            destination.write_bytes(normalized_bytes)
            summary = structural_summary(source)
            record.update({
                "status": "ok",
                "normalized_path": str(destination.relative_to(workspace)),
                "normalized_sha256": sha256_bytes(normalized_bytes),
                "normalized_bytes": len(normalized_bytes),
                "summary": summary,
            })
            ok_count += 1
        except (etree.XMLSyntaxError, OSError, ValueError) as exc:
            record.update({
                "status": "xml_parse_error",
                "error": exc.__class__.__name__,
                "error_detail": str(exc),
            })
            error_count += 1
        records.append(record)

    manifest = {
        "created": now_iso(),
        "date": date,
        "source_snapshot_dir": str(snapshot_dir.relative_to(workspace)),
        "output_dir": str(output_dir.relative_to(workspace)),
        "count": len(records),
        "ok_count": ok_count,
        "skipped_count": skipped_count,
        "error_count": error_count,
        "items": records,
        "research_caveat": RESEARCH_CAVEAT,
    }
    write_json(output_dir / "manifest.json", manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["normalize"])
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--date", required=True)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    manifest = normalize_snapshot(workspace, args.date, args.limit)
    print(json.dumps({
        "date": manifest["date"],
        "count": manifest["count"],
        "ok_count": manifest["ok_count"],
        "skipped_count": manifest["skipped_count"],
        "error_count": manifest["error_count"],
        "manifest": str(pathlib.Path(manifest["output_dir"]) / "manifest.json"),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
