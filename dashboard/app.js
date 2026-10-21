"use strict";

const DATA_URL = "../data/output/bmw_m_catalogo_completo.json";
const $ = (id) => document.getElementById(id);
const number = (value, digits = 0) => Number.isFinite(value)
  ? new Intl.NumberFormat("pt-PT", { minimumFractionDigits: digits, maximumFractionDigits: digits }).format(value)
  : "—";
const hasNhtsa = (vehicle) => Number.isInteger(vehicle.nhtsa_recalls_count) && vehicle.nhtsa_recalls_count >= 0;
const normalize = (value) => String(value ?? "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("pt-PT");
const seriesLabel = (series) => series.replace(/^Série (\d+) M$/, "M$1");
let vehicles = [];

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function parseCatalogue(data) {
  if (!data || !Array.isArray(data.catalogo_bmw_m)) throw new Error("Estrutura JSON inesperada: falta catalogo_bmw_m.");
  for (const vehicle of data.catalogo_bmw_m) {
    if (!vehicle || typeof vehicle.model !== "string" || !vehicle.model.trim() ||
        typeof vehicle.series !== "string" || !vehicle.series.trim() ||
        !(vehicle.nhtsa_recalls_count === null || hasNhtsa(vehicle))) {
      throw new Error("Registo inválido: verifique modelo, série e contagem NHTSA (inteiro não negativo ou null).");
    }
  }
  return data.catalogo_bmw_m;
}

function summarize(rows) {
  const series = new Map();
  for (const vehicle of rows) series.set(vehicle.series, (series.get(vehicle.series) || 0) + 1);
  const valid = rows.filter(hasNhtsa).length;
  return { total: rows.length, series: [...series].sort(([a], [b]) => a.localeCompare(b, "pt-PT", { numeric: true })), valid, unknown: rows.length - valid };
}

function renderOverview() {
  const summary = summarize(vehicles);
  $("total").textContent = number(summary.total);
  $("series-count").textContent = number(summary.series.length);
  $("valid-count").textContent = number(summary.valid);
  $("unknown-count").textContent = number(summary.unknown);
  const years = vehicles.map((vehicle) => vehicle.year).filter(Number.isFinite);
  $("years").textContent = years.length ? `${Math.min(...years)}–${Math.max(...years)} · anos no catálogo` : "Sem anos disponíveis";

  const selected = $("series-filter").value;
  $("series-filter").replaceChildren(element("option", "", "Todas as séries"));
  $("series-filter").firstElementChild.value = "";
  $("series-chart").replaceChildren();
  const maxCount = Math.max(1, ...summary.series.map(([, count]) => count));
  for (const [series, count] of summary.series) {
    const option = element("option", "", seriesLabel(series));
    option.value = series;
    $("series-filter").append(option);
    const row = element("div", "bar-row");
    row.setAttribute("role", "listitem");
    const track = element("div", "bar-track");
    track.setAttribute("aria-hidden", "true");
    const fill = element("div", "bar-fill");
    fill.style.width = `${count / maxCount * 100}%`;
    track.append(fill);
    row.append(element("span", "", seriesLabel(series)), track, element("strong", "", number(count)));
    $("series-chart").append(row);
  }
  if (summary.series.some(([series]) => series === selected)) $("series-filter").value = selected;
  if (!summary.total) $("series-chart").append(element("p", "chart-note", "Catálogo sem veículos."));
  const percent = summary.total ? summary.valid / summary.total * 100 : 0;
  $("coverage-ring").style.strokeDasharray = `${percent} ${100 - percent}`;
  $("coverage-percent").textContent = summary.total ? `${number(percent, 1)}%` : "—";
  $("legend-valid").textContent = number(summary.valid);
  $("legend-unknown").textContent = number(summary.unknown);
  $("coverage-chart").setAttribute("aria-label", `${summary.valid} veículos com resposta NHTSA; ${summary.unknown} sem dados; ${summary.total} no total.`);
}

function filterVehicles(rows, series, query) {
  const term = normalize(query.trim());
  return rows.filter((vehicle) => (!series || vehicle.series === series) &&
    normalize(`${vehicle.model} ${vehicle.versao ?? ""} ${vehicle.year ?? ""}`).includes(term));
}

function renderTable() {
  const rows = filterVehicles(vehicles, $("series-filter").value, $("search").value);
  $("row-count").textContent = `${number(rows.length)} de ${number(vehicles.length)} veículos`;
  $("empty").hidden = rows.length !== 0;
  $("vehicles").replaceChildren();
  for (const vehicle of rows) {
    const row = element("tr");
    const model = element("td", "", vehicle.model);
    model.append(element("small", "", vehicle.versao || "Versão não indicada"));
    const nhtsa = element("td");
    nhtsa.append(element("span", `badge ${hasNhtsa(vehicle) ? "known" : "missing"}`, hasNhtsa(vehicle) ? "Com resposta" : "Sem dados · NULL"));
    row.append(model, element("td", "", seriesLabel(vehicle.series)), element("td", "", vehicle.year ?? "—"),
      element("td", "numeric", number(vehicle.engine_hp)), element("td", "numeric", number(vehicle.weight_kg)),
      element("td", "numeric", number(vehicle.hp_por_tonelada, 2)), element("td", "numeric", number(vehicle.zero_to_sixty_mph, 1)), nhtsa);
    $("vehicles").append(row);
  }
}

async function loadCatalogue() {
  $("reload").disabled = true;
  $("status").className = "status";
  $("status").textContent = "A carregar o catálogo local…";
  $("content").hidden = true;
  try {
    if (location.protocol === "file:") throw new Error("Abra http://localhost:8000/dashboard/ após iniciar o servidor Python na raiz do repositório.");
    const response = await fetch(DATA_URL, { cache: "no-store" });
    if (!response.ok) throw new Error(`Não foi possível ler o catálogo (HTTP ${response.status}).`);
    vehicles = parseCatalogue(await response.json());
    renderOverview();
    renderTable();
    $("content").hidden = false;
    $("status").textContent = `Leitura local: ${new Date().toLocaleString("pt-PT")} · JSON exportado pelo ETL · Atualizar dados relê o ficheiro, sem executar o ETL.`;
  } catch (error) {
    $("status").className = "status error";
    $("status").textContent = `Erro ao carregar os dados. ${error.message} Confirme o servidor e o ficheiro data/output/bmw_m_catalogo_completo.json; depois tente Atualizar dados.`;
  } finally {
    $("reload").disabled = false;
  }
}

$("series-filter").addEventListener("change", renderTable);
$("search").addEventListener("input", renderTable);
$("clear").addEventListener("click", () => {
  $("series-filter").value = "";
  $("search").value = "";
  renderTable();
});
$("reload").addEventListener("click", loadCatalogue);
loadCatalogue();