const numberFormat = new Intl.NumberFormat("en-US");

const text = (id, value) => {
  const node = document.getElementById(id);
  if (node) node.textContent = value;
};

const cell = (value) => {
  const td = document.createElement("td");
  td.textContent = value;
  return td;
};

const chip = (label, status) => {
  const span = document.createElement("span");
  span.className = `chip ${status || ""}`.trim();
  span.textContent = label;
  return span;
};

const compactEvent = (events) => {
  const entries = Object.entries(events || {});
  if (!entries.length) return "none";
  return entries.map(([key, count]) => `${key.replaceAll("_", " ")} (${count})`).join(", ");
};

const statusClass = (run) => {
  const eatfStatus = run.eatf?.status;
  if (eatfStatus === "ok") return "ok";
  if (eatfStatus === "not_packaged") return "missing";
  return "review";
};

const statusLabel = (run) => {
  const eatfStatus = run.eatf?.status || "unknown";
  const profile = run.eatf?.signing_profile || "";
  if (eatfStatus === "ok" && profile.includes("dev")) return "dev verified";
  if (eatfStatus === "ok") return "verified";
  if (eatfStatus === "skipped_missing_signing_inputs") return "unsigned";
  if (eatfStatus === "not_packaged") return "missing";
  return eatfStatus.replaceAll("_", " ");
};

const setEvidence = (latest) => {
  const dl = document.getElementById("latestEvidence");
  if (!dl) return;
  dl.textContent = "";
  const rows = [
    ["Date", latest.date],
    ["Diff SHA-256", latest.artifacts?.diff_sha256 || "-"],
    ["Bundle SHA-256", latest.artifacts?.bundle_manifest_sha256 || "-"],
    ["Payload SHA-256", latest.eatf?.payload_sha256 || "-"],
    ["AEP SHA-256", latest.eatf?.package_sha256 || "-"],
    ["Receipt SHA-256", latest.eatf?.receipt_sha256 || "-"],
    ["Signing Profile", latest.eatf?.signing_profile || "-"],
    ["Timestamp Source", latest.eatf?.timestamp || "-"],
  ];
  rows.forEach(([label, value]) => {
    const dt = document.createElement("dt");
    const dd = document.createElement("dd");
    dt.textContent = label;
    dd.textContent = value;
    dl.append(dt, dd);
  });
};

const render = (index) => {
  const runs = index.runs || [];
  const latest = runs[runs.length - 1] || {};
  const totals = index.aggregate?.totals || {};

  text("lastUpdated", `Updated ${index.created_at || "-"}`);
  text("metricLatest", index.latest_date || "-");
  text("metricRuns", numberFormat.format(index.run_count || runs.length || 0));
  text("metricDiffs", numberFormat.format(totals.diff_change_count || 0));
  text("metricEatf", `${numberFormat.format(index.eatf_verified_count || 0)} / ${numberFormat.format(runs.length || 0)}`);
  text("claimBoundary", "Evidence receipts verify packages and hashes, not legal trusted-list status.");
  text("caveat", index.caveat || "");
  setEvidence(latest);

  const tbody = document.getElementById("runsTable");
  if (!tbody) return;
  tbody.textContent = "";
  runs.slice().reverse().forEach((run) => {
    const tr = document.createElement("tr");
    const eventTd = document.createElement("td");
    const eatfTd = document.createElement("td");
    eventTd.textContent = compactEvent(run.alert_event_types);
    eatfTd.appendChild(chip(statusLabel(run), statusClass(run)));
    tr.append(
      cell(run.date),
      cell(numberFormat.format(run.counts?.fetched_content_files || 0)),
      cell(numberFormat.format(run.counts?.normalized_xml_artifacts || 0)),
      cell(numberFormat.format(run.counts?.diff_current_record_count || 0)),
      cell(numberFormat.format(run.counts?.diff_change_count || 0)),
      eventTd,
      eatfTd,
    );
    tbody.appendChild(tr);
  });
};

fetch("./data/index.json", { cache: "no-store" })
  .then((response) => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
  .then(render)
  .catch((error) => {
    text("lastUpdated", `Data unavailable: ${error.message}`);
  });
