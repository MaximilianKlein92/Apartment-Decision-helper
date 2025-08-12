import os, json, webbrowser
import numpy as np
import plotly.graph_objects as go

def fmt_val(v, unit=""):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "–"
    return f"{v}{unit}"

def fmt_bool(b):
    if b is None or (isinstance(b, float) and np.isnan(b)):
        return "–"
    return "Ja" if bool(b) else "Nein"

hover_text = []
for _, r in df.iterrows():
    hover_text.append(
        f"<b>{r['Name']}</b><br>"
        f"Warmiete: €{fmt_val(r['Warmiete'])}<br>"
        f"Entfernung: {fmt_val(r['Entfernung'],' km')}<br>"
        f"Zimmer: {fmt_val(r['Zimmer'])}<br>"
        f"Größe: {fmt_val(r['Größe'],' m²')}<br>"
        f"EBK: {fmt_bool(r['EBK'])}<br>"
        f"Möbliert: {fmt_bool(r['Möbliert'])}<br>"
        f"Internet: {fmt_val(r['Internetgeschw.'],' Mbit/s')}<br>"
        f"Besichtigung: {fmt_val(r['Besichtigungsthermin'])}<br>"
    )


# --- Daten vorbereiten ---

df = pd.read_csv("Data/wohnungen_stuttgart.csv")
# Sicher: Zeilennummer als ID
df = df.reset_index(drop=True).reset_index().rename(columns={"index": "row_id"})

# customdata robust bauen (2 Spalten, (n,2)-Array)
df["Link"] = df["Link"].fillna("").astype(str)
customdata = df[["Link", "row_id"]].to_numpy()

# Markergrößen robust skalieren
gmin, gmax = float(df["Größe"].min()), float(df["Größe"].max())
if gmin == gmax:
    marker_sizes = np.full(len(df), 28.0)
else:
    marker_sizes = np.interp(df["Größe"], (gmin, gmax), (14.0, 42.0))

# Scatter (graph_objects wie zuvor)
fig = go.Figure(
    go.Scatter(
        x=df["Entfernung"].to_numpy(),
        y=df["Warmiete"].to_numpy(),
        mode="markers",
        text=hover_text,                 # << vollständiger Hovertext
        customdata=customdata,           # bleibt für Klick-Link/Löschen
        marker=dict(
            size=marker_sizes,
            color=df["Zimmer"].to_numpy(),
            showscale=True,
            colorbar=dict(title="Zimmer"),
        ),
        hovertemplate="%{text}<extra></extra>",  # << Hover aus text nehmen
    )
)

fig.update_layout(
    title="Wohnungen in Stuttgart",
    autosize=True,
    margin=dict(l=40, r=40, t=80, b=40),
    font=dict(size=18),
    hoverlabel=dict(font_size=22)
)

plot_div = fig.to_html(
    full_html=False,
    include_plotlyjs="cdn",
    div_id="wohnungen",
    default_width="100%",
    default_height="100%",
)

records_json = json.dumps(df.to_dict("records"), ensure_ascii=False)

html = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Wohnungen in Stuttgart</title>
<style>
  html, body {{ height:100%; margin:0; font-family:system-ui, Arial, sans-serif; }}
  #wrap {{ display:flex; flex-direction:column; height:100vh; }}
  .controls {{ display:flex; gap:12px; align-items:center; padding:10px 14px; border-bottom:1px solid #eee; }}
  .controls button {{ font-size:16px; padding:8px 12px; border-radius:10px; border:1px solid #ccc; background:#f7f7f7; cursor:pointer; }}
  .chart {{ flex:1 1 auto; height:65vh; }}
  #wohnungen {{ width:100%; height:100%; }}
  .list {{ flex:0 0 auto; max-height:calc(35vh - 10px); overflow:auto; padding:10px 14px; border-top:1px solid #eee; }}
  .item {{
  display: flex;
  align-items: center;
  justify-content: flex-start; /* alles linksbündig */
  gap: 6px;                    /* kleiner Abstand zwischen X und Text */
  padding: 6px 0;
  border-bottom: 1px dashed #eee;
  font-size: 18px;
}}
  .item a {{ text-decoration:none; color:#0b6; font-weight:600; }}
  .xbtn {{ margin-left:12px; font-size:18px; line-height:1; border:1px solid #ccc; background:#fff; border-radius:8px; padding:2px 10px; cursor:pointer; }}
  .muted {{ color:#666; font-size:14px; }}
</style>
</head>
<body>
<div id="wrap">
  <div class="controls">
    <button id="saveCsv">CSV speichern</button>
    <span id="count" class="muted"></span>
  </div>
  <div class="chart">
    {plot_div}
  </div>
  <div class="formwrap">
  <div class="form" id="addForm">
    <div class="fld">
      <label for="fName">Name</label>
      <input id="fName" type="text" placeholder="Titel / Exposé-Name">
    </div>
    <div class="fld">
      <label for="fLink">Link</label>
      <input id="fLink" type="url" placeholder="https://…">
    </div>
    <div class="fld">
      <label for="fWarmiete">Warmiete (€)</label>
      <input id="fWarmiete" type="number" step="1" min="0">
    </div>
    <div class="fld">
      <label for="fEntfernung">Entfernung (km)</label>
      <input id="fEntfernung" type="number" step="0.1" min="0">
    </div>
    <div class="fld">
      <label for="fZimmer">Zimmer</label>
      <input id="fZimmer" type="number" step="0.5" min="0">
    </div>
    <div class="fld">
      <label for="fGroesse">Größe (m²)</label>
      <input id="fGroesse" type="number" step="0.5" min="0">
    </div>
    <div class="fld">
      <label for="fInternet">Internet (Mbit/s)</label>
      <input id="fInternet" type="number" step="1" min="0" placeholder="">
    </div>
    <div class="fld">
      <label for="fTermin">Besichtigungstermin</label>
      <input id="fTermin" type="text" placeholder="z. B. 16.08.2025 - 12:30">
    </div>

    <div class="row">
      <label><input id="fEBK" type="checkbox"> EBK</label>
      <label><input id="fMoebliert" type="checkbox"> Möbliert</label>
      <button id="addBtn" class="addbtn">＋ Hinzufügen</button>
    </div>
  </div>
</div>
  <div id="list" class="list"></div>
</div>

<script>
  var tableData = {records_json};
  var gd = document.getElementById('wohnungen');

  // Plot-Punkt: Link öffnen
  gd.on('plotly_click', function(d){{
    var url = d.points[0].customdata[0];
    if (url) window.open(url, '_blank');
  }});

  // Responsiv
  window.addEventListener('resize', function() {{ Plotly.Plots.resize(gd); }});

  function jsonToCsv(items) {{
    if (!items.length) return "";
    const cols = Object.keys(items[0]);
    const esc = v => (v==null ? "" : String(v).replace(/"/g,'""'));
    const header = cols.join(",");
    const rows = items.map(r => cols.map(c => `"${{esc(r[c])}}"`).join(","));
    return [header].concat(rows).join("\\n");
  }}

  function downloadCsv(filename, content) {{
    const blob = new Blob([content], {{type: "text/csv;charset=utf-8;"}});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = filename;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }}

  function removePointByRowId(rowId) {{
    var tr = gd.data[0]; // ein Trace
    if (!tr || !tr.customdata) return;
    var idx = tr.customdata.findIndex(cd => cd && cd[1] === rowId);
    if (idx < 0) return;

    // zentrale Arrays splicen
    ['x','y','text','customdata'].forEach(k => {{ if (Array.isArray(tr[k])) tr[k].splice(idx,1); }});
    if (tr.marker) {{
      if (Array.isArray(tr.marker.size)) tr.marker.size.splice(idx,1);
      if (Array.isArray(tr.marker.color)) tr.marker.color.splice(idx,1);
      if (tr.marker.line && Array.isArray(tr.marker.line.color)) tr.marker.line.color.splice(idx,1);
    }}
    Plotly.redraw(gd);
  }}

  // --- Utils ---
function toNum(v) {{ const n = parseFloat(v); return Number.isFinite(n) ? n : null; }}
function fmtVal(v, unit="") {{ return (v===null || v===undefined || v==="") ? "–" : (""+v + unit); }}
function fmtBool(b) {{ return b ? "Ja" : "Nein"; }}
function buildHoverText(rec) {{
  return `<b>${{rec.Name || ""}}</b><br>` +
         `Warmiete: €${{fmtVal(rec.Warmiete)}}<br>` +
         `Entfernung: ${{fmtVal(rec.Entfernung," km")}}<br>` +
         `Zimmer: ${{fmtVal(rec.Zimmer)}}<br>` +
         `Größe: ${{fmtVal(rec["Größe"]," m²")}}<br>` +
         `EBK: ${{fmtBool(!!rec.EBK)}}<br>` +
         `Möbliert: ${{fmtBool(!!rec["Möbliert"])}}<br>` +
         `Internet: ${{fmtVal(rec["Internetgeschw."]," Mbit/s")}}<br>` +
         `Besichtigung: ${{fmtVal(rec.Besichtigungsthermin)}}<br>` +
         `Link: ${{rec.Link || "–"}}`;
}}
function nextRowId() {{
  if (!tableData.length) return 0;
  return Math.max(...tableData.map(r => (typeof r.row_id==="number"? r.row_id : 0))) + 1;
}}

// Größen-Skalierung 14–42 px nach 'Größe'
function computeSizes(data) {{
  const vals = data
    .map(r => Number.parseFloat(r["Größe"]))
    .filter(Number.isFinite);
  if (!vals.length) return data.map(_ => 28);
  const mn = Math.min(...vals), mx = Math.max(...vals);
  if (mn === mx) return data.map(_ => 28);
  return data.map(r => {{
    const gRaw = Number.parseFloat(r["Größe"]);
    const g = Number.isFinite(gRaw) ? gRaw : (mn + mx) / 2;
    return 14 + ((g - mn) / (mx - mn)) * (42 - 14);
  }});
}}

// Plot vollständig aus tableData neu aufbauen (robust)
function syncPlotWithTable() {{
  if (!gd || !gd.data || !gd.data.length) return;
  const tr = gd.data[0];
  const sizes = computeSizes(tableData);
  const x = tableData.map(r => r.Entfernung ?? null);
  const y = tableData.map(r => r.Warmiete ?? null);
  const text = tableData.map(r => buildHoverText(r));
  const custom = tableData.map(r => [r.Link || "", r.row_id]);
  const colors = tableData.map(r => r.Zimmer ?? null);

  tr.x = x;
  tr.y = y;
  tr.text = text;
  tr.customdata = custom;
  if (!tr.marker) tr.marker = {{}};
  tr.marker.size = sizes;
  tr.marker.color = colors;

  Plotly.redraw(gd);
  rebuildList();
}}

// --- Einfügen: Formular -> tableData -> Plot/List ---
function addRecordFromForm() {{
  const rec = {{
    row_id: nextRowId(),
    Name: document.getElementById('fName').value.trim(),
    Link: document.getElementById('fLink').value.trim(),
    Warmiete: toNum(document.getElementById('fWarmiete').value),
    Entfernung: toNum(document.getElementById('fEntfernung').value),
    Zimmer: toNum(document.getElementById('fZimmer').value),
    "Größe": toNum(document.getElementById('fGroesse').value),
    EBK: document.getElementById('fEBK').checked,
    "Möbliert": document.getElementById('fMoebliert').checked,
    "Internetgeschw.": toNum(document.getElementById('fInternet').value),
    Besichtigungsthermin: document.getElementById('fTermin').value.trim()
  }};

  // Minimal-Validierung
  const required = ["Name","Warmiete","Entfernung","Zimmer","Größe"];
  const missing = required.filter(k => (rec[k]===null || rec[k]==="" || rec[k]===undefined));
  if (missing.length) {{
    alert("Bitte ausfüllen: " + missing.join(", "));
    return;
  }}

  tableData.push(rec);
  // Formular optional leeren:
  // document.getElementById('addForm').reset();

  syncPlotWithTable();
}}

document.getElementById('addBtn').addEventListener('click', function(ev){{
  ev.preventDefault();
  addRecordFromForm();
}});
    
  function rebuildList() {{
    const list = document.getElementById('list');
    list.innerHTML = "";
    document.getElementById('count').textContent = tableData.length + " Einträge";
    tableData.forEach(rec => {{
      const row = document.createElement('div');
      row.className = "item";
      const left = document.createElement('div');
      const a = document.createElement('a');
      a.href = rec.Link || "#";
      a.target = "_blank";
      a.textContent = rec.Name;
      left.appendChild(a);

      const x = document.createElement('button');
      x.className = "xbtn";
      x.textContent = "×";
      x.title = "Eintrag löschen";
      x.addEventListener('click', function (ev) {{
        ev.stopPropagation();
        const ok = confirm("Diesen Eintrag löschen?\\n\\n" + (rec.Name || ""));
        if (!ok) return;
        const i = tableData.findIndex(r => r.row_id === rec.row_id);
        if (i >= 0) tableData.splice(i, 1);
        syncPlotWithTable(); // Plot & Liste zentral aktualisieren
      }});

      row.appendChild(left);
      row.appendChild(x);
      list.appendChild(row);
    }});
  }}

  document.getElementById('saveCsv').addEventListener('click', function(){{
    const csv = jsonToCsv(tableData);
    downloadCsv("wohnungen_stuttgart.csv", csv);
  }});

  syncPlotWithTable(); // baut Plot aus tableData und ruft rebuildList()
</script>
</body>
</html>
"""

# schreiben & öffnen
out_path = "wohnungen.html"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

webbrowser.open_new_tab('file://' + os.path.abspath(out_path))
