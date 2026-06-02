/* Accountability Ledger — frontend */

const DOMAINS = [
  { key: "climate",        label: "Climate" },
  { key: "health",         label: "Health" },
  { key: "ai_safety",      label: "AI Safety" },
  { key: "digital_rights", label: "Digital Rights" },
  { key: "labor",          label: "Labor" },
  { key: "tax_governance", label: "Tax & Gov." },
];

const STANCE_LABEL = {
  net_positive: "Net positive",
  mixed:        "Mixed",
  net_negative: "Net negative",
  unrated:      "Unrated",
};

const GAP_LABEL = {
  severe:   "Severe pledge gap",
  moderate: "Moderate pledge gap",
  none:     "No gap",
  unknown:  "Gap unknown",
};

let allRecords = [];
let sortKey = "name";
let sortDir = 1;

// ── Load data ──────────────────────────────────────────────────────────────
async function loadData() {
  try {
    const resp = await fetch("../data/output/ledger.json");
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    allRecords = await resp.json();
    document.getElementById("last-run").textContent =
      allRecords[0]?.last_updated ?? "—";
  } catch (e) {
    document.getElementById("tbody").innerHTML =
      `<tr><td colspan="9" style="color:#e05050;padding:1.5rem;">
        Could not load ledger.json — run the pipeline first:<br>
        <code>python -m pipeline.run</code>
      </td></tr>`;
    console.error(e);
    return;
  }
  render();
}

// ── Filtering ──────────────────────────────────────────────────────────────
function filtered() {
  const q     = document.getElementById("search").value.toLowerCase();
  const type  = document.getElementById("type-filter").value;
  const domain = document.getElementById("domain-filter").value;
  const stance = document.getElementById("stance-filter").value;
  const gap    = document.getElementById("gap-filter").value;

  return allRecords.filter(r => {
    if (q && !r.name.toLowerCase().includes(q) && !r.ticker?.toLowerCase().includes(q)) return false;
    if (type && r.type !== type) return false;
    if (domain && stance) {
      const d = r.domains?.[domain];
      if (!d || d.stance !== stance) return false;
    } else if (domain) {
      const d = r.domains?.[domain];
      if (!d || d.stance === "unrated") return false;
    } else if (stance) {
      const hasStance = DOMAINS.some(({ key }) => r.domains?.[key]?.stance === stance);
      if (!hasStance) return false;
    }
    if (gap) {
      const domainKey = domain || null;
      if (domainKey) {
        if (r.domains?.[domainKey]?.pledge_vs_action_gap !== gap) return false;
      } else {
        const hasGap = DOMAINS.some(({ key }) => r.domains?.[key]?.pledge_vs_action_gap === gap);
        if (!hasGap) return false;
      }
    }
    return true;
  });
}

// ── Sorting ────────────────────────────────────────────────────────────────
function sorted(records) {
  return [...records].sort((a, b) => {
    let av, bv;
    if (DOMAINS.some(d => d.key === sortKey)) {
      av = a.domains?.[sortKey]?.stance ?? "unrated";
      bv = b.domains?.[sortKey]?.stance ?? "unrated";
      const order = ["net_positive", "mixed", "net_negative", "unrated"];
      av = order.indexOf(av); bv = order.indexOf(bv);
    } else if (sortKey === "name") {
      av = a.name?.toLowerCase() ?? "";
      bv = b.name?.toLowerCase() ?? "";
    } else {
      av = a[sortKey]?.toLowerCase() ?? "";
      bv = b[sortKey]?.toLowerCase() ?? "";
    }
    return av < bv ? -sortDir : av > bv ? sortDir : 0;
  });
}

// ── Rendering ──────────────────────────────────────────────────────────────
function stanceChip(stance) {
  return `<span class="stance stance-${stance}">${STANCE_LABEL[stance] ?? stance}</span>`;
}

function gapDot(gap) {
  if (!gap || gap === "unknown") return "";
  return `<span class="gap-dot gap-${gap}" title="${GAP_LABEL[gap] ?? gap}"></span>`;
}

function domainCell(domain) {
  if (!domain) return `<span class="stance stance-unrated">—</span>`;
  return stanceChip(domain.stance) + gapDot(domain.pledge_vs_action_gap);
}

function render() {
  const records = sorted(filtered());
  const tbody = document.getElementById("tbody");
  document.getElementById("count-bar").textContent =
    `${records.length} of ${allRecords.length} entities`;

  tbody.innerHTML = records.map(r => `
    <tr data-id="${r.entity_id}">
      <td class="col-name">
        ${r.name}
        ${r.ticker ? `<span style="color:var(--text-muted);font-size:.75rem;margin-left:.3rem">${r.ticker}</span>` : ""}
      </td>
      <td class="col-sector">${r.sector || "—"}</td>
      ${DOMAINS.map(({ key }) => `<td class="col-domain">${domainCell(r.domains?.[key])}</td>`).join("")}
      <td class="col-updated">${r.last_updated ?? "—"}</td>
    </tr>
  `).join("");

  // Sort headers
  document.querySelectorAll("thead th[data-sort]").forEach(th => {
    th.classList.remove("sorted-asc", "sorted-desc");
    if (th.dataset.sort === sortKey) {
      th.classList.add(sortDir === 1 ? "sorted-asc" : "sorted-desc");
    }
  });
}

// ── Detail panel ───────────────────────────────────────────────────────────
function openDetail(record) {
  const panel = document.getElementById("detail-panel");
  const content = document.getElementById("detail-content");

  const domainBlocks = DOMAINS.map(({ key, label }) => {
    const d = record.domains?.[key];
    if (!d || d.stance === "unrated") return `
      <div class="domain-block">
        <h3>${label} <span class="conf-badge conf-${d?.confidence ?? "low"}">unrated</span></h3>
        <span class="stance stance-unrated">—</span>
      </div>`;

    const evidenceItems = (d.evidence ?? []).map(ev => `
      <li>
        <span class="ev-source">${ev.source}</span>
        <span class="ev-metric">${ev.metric}:</span>
        <span class="ev-value">${ev.value}</span>
        <span class="ev-date">${ev.as_of ?? ""}</span>
        ${ev.url ? `<a href="${ev.url}" target="_blank" rel="noopener">↗</a>` : ""}
      </li>`).join("");

    return `
      <div class="domain-block">
        <h3>${label} <span class="conf-badge conf-${d.confidence}">${d.confidence}</span></h3>
        ${stanceChip(d.stance)}
        <div class="gap-label">Pledge gap: <strong>${GAP_LABEL[d.pledge_vs_action_gap] ?? d.pledge_vs_action_gap}</strong></div>
        <ul class="evidence-list">${evidenceItems}</ul>
      </div>`;
  }).join("");

  content.innerHTML = `
    <h2>${record.name}</h2>
    <div class="entity-meta">
      ${record.type} · ${record.sector || "No sector"} · Updated ${record.last_updated ?? "—"}
      ${record.notes ? `<br><em>${record.notes}</em>` : ""}
    </div>
    ${domainBlocks}
  `;

  panel.classList.remove("hidden");
}

// ── Events ─────────────────────────────────────────────────────────────────
document.getElementById("search").addEventListener("input", render);
document.getElementById("type-filter").addEventListener("change", render);
document.getElementById("domain-filter").addEventListener("change", render);
document.getElementById("stance-filter").addEventListener("change", render);
document.getElementById("gap-filter").addEventListener("change", render);
document.getElementById("close-panel").addEventListener("click", () => {
  document.getElementById("detail-panel").classList.add("hidden");
});

document.querySelectorAll("thead th[data-sort]").forEach(th => {
  th.addEventListener("click", () => {
    const key = th.dataset.sort;
    if (sortKey === key) {
      sortDir *= -1;
    } else {
      sortKey = key;
      sortDir = 1;
    }
    render();
  });
});

document.getElementById("tbody").addEventListener("click", e => {
  const row = e.target.closest("tr[data-id]");
  if (!row) return;
  const record = allRecords.find(r => r.entity_id === row.dataset.id);
  if (record) openDetail(record);
});

// Keyboard: Escape closes panel
document.addEventListener("keydown", e => {
  if (e.key === "Escape") document.getElementById("detail-panel").classList.add("hidden");
});

// ── Init ──────────────────────────────────────────────────────────────────
loadData();
