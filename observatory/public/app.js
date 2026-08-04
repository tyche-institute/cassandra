const numberFormat = new Intl.NumberFormat("en-US");
const dateFormat = new Intl.DateTimeFormat("en-GB", {
  day: "2-digit",
  month: "short",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
  timeZoneName: "short",
});

const text = (id, value) => {
  const node = document.getElementById(id);
  if (node) node.textContent = value;
};

const link = (id, href, label) => {
  const node = document.getElementById(id);
  if (!node) return;
  if (!href) {
    node.removeAttribute("href");
    node.setAttribute("aria-disabled", "true");
    node.textContent = `${label} unavailable`;
    return;
  }
  node.href = href;
  node.removeAttribute("aria-disabled");
  node.textContent = label;
};

const formatDateTime = (value) => {
  if (!value) return "-";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.valueOf())) return value;
  return dateFormat.format(parsed);
};

const nextDailyRun = () => {
  const now = new Date();
  const next = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), 3, 23, 0));
  if (next <= now) next.setUTCDate(next.getUTCDate() + 1);
  return dateFormat.format(next);
};

const humanize = (value) => String(value || "-").replaceAll("_", " ");

const shortHash = (value) => {
  if (!value || value === "-") return "-";
  if (value.length <= 26) return value;
  return `${value.slice(0, 12)}...${value.slice(-8)}`;
};

const cell = (value, className) => {
  const td = document.createElement("td");
  if (className) td.className = className;
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
  return entries.map(([key, count]) => `${humanize(key)} (${count})`).join(", ");
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
  return humanize(eatfStatus);
};

const renderClaimBoundary = (boundary) => {
  const list = document.getElementById("claimBoundaryList");
  if (!list) return;
  list.textContent = "";

  const asserts = boundary?.asserts || [];
  const limits = boundary?.does_not_assert || [];
  const rows = [
    ...asserts.map((item) => `Asserts: ${item}`),
    ...limits.map((item) => `Does not assert: ${item}`),
  ];

  rows.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    list.appendChild(li);
  });
};

const evidenceValue = (value, isHash) => {
  const span = document.createElement("span");
  if (isHash) {
    span.className = "hash-cell";
    span.title = value || "-";
    span.textContent = shortHash(value);
    return span;
  }
  span.textContent = value || "-";
  return span;
};

const setEvidence = (latest) => {
  const dl = document.getElementById("latestEvidence");
  if (!dl) return;
  dl.textContent = "";
  const rows = [
    ["Date", latest.date],
    ["Diff SHA-256", latest.artifacts?.diff_sha256, true],
    ["Bundle SHA-256", latest.artifacts?.bundle_manifest_sha256, true],
    ["Payload SHA-256", latest.eatf?.payload_sha256, true],
    ["AEP SHA-256", latest.eatf?.package_sha256, true],
    ["Receipt SHA-256", latest.eatf?.receipt_sha256, true],
    ["Signing profile", latest.eatf?.signing_profile],
    ["Timestamp source", latest.eatf?.timestamp],
  ];
  rows.forEach(([label, value, isHash]) => {
    const dt = document.createElement("dt");
    const dd = document.createElement("dd");
    dt.textContent = label;
    dd.appendChild(evidenceValue(value || "-", isHash));
    dl.append(dt, dd);
  });
};

const setVerifier = (latest) => {
  const eatf = latest.eatf || {};
  const verifier = eatf.verifier_url || "https://eatf.eu/verify";

  text("verifyDate", latest.date || "latest run");
  link("downloadAep", eatf.public_package?.path, "AEP package");
  link("downloadPayload", eatf.public_payload?.path, "Payload JSON");
  link("downloadReceipt", eatf.public_receipt?.path, "EATF receipt");
  link("downloadMetadata", eatf.public_metadata?.path, "EATF metadata");
  link("openVerifier", verifier, "Open verifier");

  const dl = document.getElementById("verifyHashes");
  if (!dl) return;
  dl.textContent = "";
  [
    ["Package SHA-256", eatf.package_sha256, true],
    ["Payload SHA-256", eatf.payload_sha256, true],
    ["Receipt SHA-256", eatf.receipt_sha256, true],
    ["Status", statusLabel(latest)],
    ["Verifier", verifier],
  ].forEach(([label, value, isHash]) => {
    const dt = document.createElement("dt");
    const dd = document.createElement("dd");
    dt.textContent = label;
    dd.appendChild(evidenceValue(value || "-", isHash));
    dl.append(dt, dd);
  });
};

const renderDiffBars = (aggregate) => {
  const container = document.getElementById("diffBars");
  if (!container) return;
  container.textContent = "";

  const totals = aggregate?.diff_class_totals || {};
  const entries = Object.entries(totals)
    .sort(([, a], [, b]) => b - a)
    .filter(([, count]) => count > 0);
  const max = Math.max(1, ...entries.map(([, count]) => count));

  if (!entries.length) {
    const empty = document.createElement("p");
    empty.className = "quiet-note";
    empty.textContent = "No structural diff classes have been observed in the current aggregate.";
    container.appendChild(empty);
    return;
  }

  entries.forEach(([name, count]) => {
    const row = document.createElement("div");
    const label = document.createElement("span");
    const track = document.createElement("span");
    const fill = document.createElement("span");
    const value = document.createElement("span");

    row.className = "diff-row";
    label.className = "diff-name";
    track.className = "bar-track";
    fill.className = "bar-fill";
    value.className = "diff-count";

    label.textContent = humanize(name);
    fill.style.width = `${Math.max(4, Math.round((count / max) * 100))}%`;
    value.textContent = numberFormat.format(count);

    track.appendChild(fill);
    row.append(label, track, value);
    container.appendChild(row);
  });
};

const renderRuns = (runs) => {
  const tbody = document.getElementById("runsTable");
  if (!tbody) return;
  tbody.textContent = "";
  runs.slice().reverse().forEach((run) => {
    const tr = document.createElement("tr");
    const eventTd = cell(compactEvent(run.alert_event_types), "event-cell");
    const eatfTd = document.createElement("td");
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

const render = (index) => {
  const runs = index.runs || [];
  const latest = runs[runs.length - 1] || {};
  const totals = index.aggregate?.totals || {};

  text("lastUpdated", `Updated ${formatDateTime(index.created_at)}`);
  text("metricLatest", index.latest_date || "-");
  text("metricRuns", numberFormat.format(index.run_count || runs.length || 0));
  text("metricDiffs", numberFormat.format(totals.diff_change_count || 0));
  text(
    "metricEatf",
    `${numberFormat.format(index.eatf_verified_count || 0)} / ${numberFormat.format(runs.length || 0)}`,
  );
  text("nextCadence", `Next scheduled window: ${nextDailyRun()}.`);
  text("claimBoundary", "EATF receipts verify packages and hashes, not legal trusted-list status.");
  text("caveat", index.caveat || "");

  const latestStatus = document.getElementById("latestReceiptStatus");
  if (latestStatus) {
    const statusChip = chip(statusLabel(latest), statusClass(latest));
    statusChip.id = "latestReceiptStatus";
    latestStatus.replaceWith(statusChip);
  }

  renderClaimBoundary(index.claim_boundary);
  renderRuns(runs);
  renderDiffBars(index.aggregate);
  setEvidence(latest);
  setVerifier(latest);
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
