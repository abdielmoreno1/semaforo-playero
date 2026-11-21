const API = location.origin;
const COLOR = { verde: "#16a34a", amarillo: "#d97706", rojo: "#dc2626" };
const NOMBRE = { verde: "En buen estado", amarillo: "Con precaución", rojo: "Evitar esta playa" };
const DIA = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];
let ubicacion = null; // { lat, lng } si el usuario da permiso
let cacheTodas = []; // la última respuesta de /api/playas
let cacheImpacto = null; // la última respuesta de /api/impacto
let modoActual = null; // "todas" o "ideal"
let mapa = null; // el mapa de Leaflet
let capaPlayas = null; // los puntos de colores
let capaYo = null; // el punto azul de tu ubicación
let marcadores = {}; // id de playa -> marcador del mapa
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;",
">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
function momentoActual() {
const inputF = $("sp-fecha"), inputH = $("sp-hora"), inputFest = $("sp-festivo");
if (inputF && inputF.value && inputH && inputH.value !== "") {
const fecha = inputF.value;
const hora = Number(inputH.value);
const festivo = Boolean(inputFest && inputFest.checked);
const [y, m, day] = fecha.split("-").map(Number);
const dt = new Date(y, (m || 1) - 1, day || 1);
const dia = DIA[dt.getDay()] || fecha;
return {
fecha,
hora,
festivo,
etiqueta: `${dia} ${fecha} · ${String(hora).padStart(2, "0")}:00${festivo ? " (Festivo)" : ""}`,
};
}
const q = new URLSearchParams(location.search);
const f = q.get("fecha"), h = q.get("hora");
const festParam = q.get("festivo") === "true";
if (f && h !== null) {
const horaNum = Math.min(20, Math.max(6, Number(h) || 13));
if (inputF) inputF.value = f;
if (inputH) inputH.value = String(horaNum);
if (inputFest) inputFest.checked = festParam;
if ($("sp-hora-txt")) $("sp-hora-txt").textContent = `${String(horaNum).padStart(2, "0")}:00`;
return { fecha: f, hora: horaNum, festivo: festParam, etiqueta: `${f} · ${horaNum}:00` };
}
const d = new Date();
let hora = d.getHours();
if (hora >= 20) {
d.setDate(d.getDate() + 1);
hora = 13;
} else if (hora < 6) {
hora = 13;
}
const fecha = [
d.getFullYear(),
String(d.getMonth() + 1).padStart(2, "0"),
String(d.getDate()).padStart(2, "0"),
].join("-");
if (inputF) inputF.value = fecha;
if (inputH) inputH.value = String(hora);
if (inputFest) inputFest.checked = festParam;
if ($("sp-hora-txt")) $("sp-hora-txt").textContent = `${String(hora).padStart(2, "0")}:00`;
const dia = DIA[d.getDay()];
return { fecha, hora, festivo: festParam, etiqueta: `${dia} · ${String(hora).padStart(2, "0")}:00` };
}
function pedirUbicacion() {
return new Promise((resolve) => {
ubicacion = null;
const q = new URLSearchParams(location.search);
const lngParam = q.get("lng") ?? q.get("lon");
if (q.get("lat") && lngParam) {
const lat = Number(q.get("lat"));
const lng = Number(lngParam);
if (Number.isFinite(lat) && Number.isFinite(lng)) {
ubicacion = { lat, lng };
return resolve(ubicacion);
}
}
if (!navigator.geolocation) return resolve(null);
navigator.geolocation.getCurrentPosition(
(pos) => { ubicacion = { lat: pos.coords.latitude, lng: pos.coords.longitude };
resolve(ubicacion); },
() => resolve(null),
{ timeout: 4000, maximumAge: 300000 }
);
});
}

function adaptarPlaya(playa) {
return {
...playa,
estado: playa.semaforo,
ocupacion_pct: playa.ocupacion,
lon: playa.lng,
};
}

async function cargarDatos() {
const m = momentoActual();
const params = new URLSearchParams({
fecha: m.fecha,
hora: String(m.hora),
festivo: String(Boolean(m.festivo)),
});
if (ubicacion && Number.isFinite(ubicacion.lat) && Number.isFinite(ubicacion.lng)) {
params.set("lat", String(ubicacion.lat));
params.set("lng", String(ubicacion.lng));
}
const paramsImpacto = new URLSearchParams({
fecha: m.fecha,
hora: String(m.hora),
festivo: String(Boolean(m.festivo)),
});
const [resTodas, resImpacto] = await Promise.all([
fetch(`${API}/api/playas?${params}`),
fetch(`${API}/api/impacto?${paramsImpacto}`),
]);
if (!resTodas.ok) throw new Error(`HTTP ${resTodas.status}`);
const dTodas = await resTodas.json();
if (!Array.isArray(dTodas)) throw new Error("La API devolvió un formato de playas inesperado.");
cacheTodas = dTodas.map(adaptarPlaya);
cacheImpacto = resImpacto && resImpacto.ok ? await resImpacto.json() : null;
if (!cacheTodas.length) throw new Error("No pudimos cargar las playas. Intenta de nuevo en un momento.");
return m;
}

function urlGoogleMaps(playa) {
const destino = `${playa.lat},${playa.lng}`;
if (!ubicacion) {
return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(destino)}`;
}
const params = new URLSearchParams({
api: "1",
origin: `${ubicacion.lat},${ubicacion.lng}`,
destination: destino,
});
return `https://www.google.com/maps/dir/?${params}`;
}

function tarjetaHtml(p, { etiquetaExtra = "" } = {}) {
const estado = (p.estado || "verde").toLowerCase();
const dist = p.distancia_km != null ? `${esc(p.distancia_km)} km de ti` : "";
const urlMaps = urlGoogleMaps(p);
const motivos = Array.isArray(p.motivos) ? p.motivos : [];
const alternativas = Array.isArray(p.alternativas)
? p.alternativas.map((alt) =>
typeof alt === "string"
? alt
: `${alt.nombre} (${alt.ocupacion}% ocup · estrés ${alt.estres}% · ${alt.transporte})`
).filter(Boolean)
: [];
const subtitulo = p.transporte ? esc(p.transporte) : (p.municipio ? esc(p.municipio) : "");
const detalle = [
etiquetaExtra ? `<p><strong>${esc(etiquetaExtra)}</strong></p>` : "",
`<p><strong>Pronóstico (+2 h):</strong> ${esc(p.ocupacion_2h ?? p.ocupacion_pct)}% de ocupación · <strong>Estrés ecológico:</strong> ${esc(p.estres)}/100</p>`,
p.transporte ? `<p><strong>Transporte público:</strong> ${esc(p.transporte)}</p>` : "",
motivos.length ? `<p><strong>Por qué:</strong> ${esc(motivos.join(". "))}</p>` : "",
alternativas.length ? `<p><strong>Alternativas recomendadas:</strong> ${esc(alternativas.join(" | "))}</p>` : "",
`<p><a href="${esc(urlMaps)}" target="_blank" rel="noopener">Abrir en Google Maps</a></p>`,
].join("");
return `
<article class="sp-card sp-card--${esc(estado)}">
<div class="sp-card-top">
<div class="sp-card-heading">
${subtitulo ? `<p class="sp-card-lugar">${subtitulo}</p>` : ""}
<h4>${esc(p.nombre)}</h4>
</div>
<span class="sp-badge sp-badge--${esc(estado)}">${esc(NOMBRE[estado] || estado)}
</span>
</div>
<div class="sp-card-datos">
<div class="sp-ocupacion"><strong>${esc(p.ocupacion_pct)}%</strong><span>ocupación</span></div>
<div class="sp-metricas-sec">
<span>En 2h: <strong>${esc(p.ocupacion_2h ?? p.ocupacion_pct)}%</strong></span>
<span>Estrés: <strong>${esc(p.estres)}%</strong></span>
</div>
${dist ? `<p class="sp-distancia">${dist}</p>` : ""}
</div>
<div class="sp-acciones">
<button type="button" class="sp-btn" data-ver-mapa="${esc(p.id)}">Ver en el mapa</button>
<button type="button" class="sp-btn" data-toggle-detalle aria-expanded="false">Ver por qué</button>
</div>
<div class="sp-detalle" hidden>${detalle}</div>
</article>`;
}

function iniciarMapa() {
if (mapa) return;
mapa = L.map("sp-mapa", { scrollWheelZoom: false }).setView([20.95, -87.0], 8);
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
maxZoom: 18,
attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(mapa);
capaPlayas = L.layerGroup().addTo(mapa);
capaYo = L.layerGroup().addTo(mapa);
}
function globoHtml(p) {
const est = (p.estado || "verde").toLowerCase();
const dist = p.distancia_km != null ? ` · <strong>a ${esc(p.distancia_km)} km de
ti</strong>` : "";
const bus = p.transporte ? `<br><small>${esc(p.transporte)}</small>` : "";
const urlMaps = urlGoogleMaps(p);
return `
<strong>${esc(p.nombre)}</strong><br>
${esc(NOMBRE[est] || est)} · Ocupación ${esc(p.ocupacion_pct)}% · Estrés ${esc(p.estres)}%${dist}${bus}<br>
<a href="${esc(urlMaps)}" target="_blank" rel="noopener">Cómo llegar</a>`;
}
function pintarMapa(playas) {
iniciarMapa();
capaPlayas.clearLayers();
marcadores = {};
const puntos = [];
for (const p of playas) {
if (p.lat == null || p.lon == null) continue;
const est = (p.estado || "verde").toLowerCase();
const icono = L.divIcon({
className: "",
html: `<div class="sp-puntito" style="background:${COLOR[est] || COLOR.verde}">
</div>`,
iconSize: [16, 16], iconAnchor: [8, 8]
});
const m = L.marker([p.lat, p.lon], { icon: icono }).bindPopup(globoHtml(p));
m.addTo(capaPlayas);
marcadores[String(p.id)] = m;
puntos.push([p.lat, p.lon]);
}
capaYo.clearLayers();
if (ubicacion) {
const yo = L.divIcon({ className: "", html: `<div class="sp-yo"></div>`, iconSize: [14,
14], iconAnchor: [7, 7] });
L.marker([ubicacion.lat, ubicacion.lng], { icon: yo }).bindPopup("Estás aquí").addTo(capaYo);
puntos.push([ubicacion.lat, ubicacion.lng]);
}
if (puntos.length && !mapa._encuadrado) {
mapa.fitBounds(puntos, { padding: [30, 30], maxZoom: 12 });
mapa._encuadrado = true;
}
}

function puntaje(p) { return 0.6 * p.ocupacion_pct + 0.4 * p.estres; }
function elegirIdeal(playas) {
const verdes = playas.filter((p) => p.estado === "verde");
const amarillas = playas.filter((p) => p.estado === "amarillo");
const grupo = verdes.length ? verdes : amarillas;
if (!grupo.length) return null;
return [...grupo].sort((a, b) => puntaje(a) - puntaje(b))[0];
}
function textoImpacto(ideal) {
const detalle = (cacheImpacto?.detalle || [])
.filter((item) => item.alternativa_id === ideal?.id)
.sort((a, b) => b.reduccion_estres_pct - a.reduccion_estres_pct)[0];
const extraQr = cacheImpacto?.reportes_ciudadanos_activos > 0
? ` · Validado con ${cacheImpacto.reportes_ciudadanos_activos} reportes ciudadanos (QR).`
: "";
if (detalle && ideal) {
return `Al elegir ${ideal.nombre} en vez de ${detalle.nombre}, el estrés ecológico baja ${detalle.reduccion_estres_pct}% (de ${detalle.estres} a ${detalle.estres_alternativa} puntos)${extraQr}`;
}
return resumenImpacto(ideal);
}
function resumenImpacto(ideal = null) {
const extraQr = cacheImpacto?.reportes_ciudadanos_activos > 0
? ` (${cacheImpacto.reportes_ciudadanos_activos} reportes ciudadanos QR activos)`
: "";
if (cacheImpacto?.playas_en_riesgo > 0) {
return `Impacto Ambiental Colectivo: hay ${cacheImpacto.playas_en_riesgo} de ${cacheImpacto.playas_evaluadas} playas con presión alta. Al elegir alternativas en verde, la reducción promedio de estrés ecológico es de ${cacheImpacto.reduccion_promedio_pct}%${extraQr}.`;
}
if (ideal) {
return `No se detectan playas en riesgo crítico en este horario. ${ideal.nombre} tiene solo ${ideal.estres} puntos de estrés ecológico estimado${extraQr}.`;
}
return `Ecosistema costero en buen estado: 0 playas en riesgo crítico en este horario${extraQr}.`;
}
function pintarIdeal(playas, m) {
const box = $("sp-ideal");
const ideal = elegirIdeal(playas);
if (!ideal) {
box.hidden = false;
box.className = "sp-ideal sp-ideal--amarillo";
box.innerHTML = `<h3>Todas las playas están en rojo</h3><p>Revisa las opciones con menor estrés que aparecen abajo.</p><div class="sp-impacto">${esc(resumenImpacto())}</div>`;
return;
}
const est = (ideal.estado || "verde").toLowerCase();
const dist = ideal.distancia_km != null ? ` · <strong>a ${esc(ideal.distancia_km)} km de
ti</strong>` : "";
const urlMaps = urlGoogleMaps(ideal);
const transporte = ideal.transporte ? ` · ${esc(ideal.transporte)}` : "";
const impacto = textoImpacto(ideal);
box.hidden = false;
box.className = est === "amarillo" ? "sp-ideal sp-ideal--amarillo" : "sp-ideal";
box.innerHTML = `
<p class="sp-ideal-etiqueta">Playa recomendada · ${esc(m.etiqueta)}</p>
<h3>${esc(ideal.nombre)} (${esc(NOMBRE[est] || est)})</h3>
<p class="sp-meta">Ocupación ${esc(ideal.ocupacion_pct)}% (en 2h: ${esc(ideal.ocupacion_2h ?? ideal.ocupacion_pct)}%) · Estrés ecológico ${esc(ideal.estres)}/100${transporte}${dist}</p>
<p>${esc((ideal.motivos || []).join(". ") || "Es la opción más tranquila en este horario.")}</p>
${impacto ? `<div class="sp-impacto">${esc(impacto)}</div>` : ""}
<div class="sp-ideal-acciones">
<a class="sp-btn sp-btn--primario" href="${esc(urlMaps)}" target="_blank"
rel="noopener">Cómo llegar</a>
<button type="button" class="sp-btn" data-ver-mapa="${esc(ideal.id)}">Ver en el mapa</button>
</div>`;
setTimeout(() => enfocarPlaya(ideal.id), 120);
}

function mostrarEstado(texto, esError = false) {
const el = $("sp-estado");
el.hidden = !texto;
el.textContent = texto;
el.className = esError ? "sp-estado sp-estado--error" : "sp-estado";
}
function pintarTodo(m) {
const playas = [...cacheTodas];
if (ubicacion) {
playas.sort((a, b) => (a.distancia_km ?? Infinity) - (b.distancia_km ?? Infinity));
}
$("sp-ubicacion-txt").textContent = ubicacion
? "Ordenadas por cercanía a tu ubicación"
: "Sin acceso a tu ubicación (activa el permiso para ver distancias)";
const bannerImpacto = $("sp-resumen-impacto");
pintarMapa(playas);
if (modoActual === "ideal") {
if (bannerImpacto) bannerImpacto.hidden = true;
pintarIdeal(playas, m);
const ideal = elegirIdeal(playas);
const candidatas = playas.filter((p) => p.id !== ideal?.id);
const recomendables = candidatas.filter((p) => p.estado !== "rojo");
const otras = (recomendables.length ? recomendables : candidatas)
.sort((a, b) => puntaje(a) - puntaje(b))
.slice(0, 2);
$("sp-lista-titulo").textContent = recomendables.length
? "Otras opciones recomendables"
: "Otras opciones con menor estrés (todas en rojo)";
$("sp-lista").innerHTML = otras.map((p) => tarjetaHtml(p)).join("");
} else {
$("sp-ideal").hidden = true;
if (bannerImpacto && cacheImpacto) {
bannerImpacto.hidden = false;
bannerImpacto.textContent = resumenImpacto();
}
$("sp-lista-titulo").textContent = `Todas las playas (${playas.length}) · ${m.etiqueta}`;
$("sp-lista").innerHTML = playas.map((p) => tarjetaHtml(p)).join("");
}
}
async function abrirSeccion(modo) {
const cambioDeVista = modo !== modoActual;
modoActual = modo;
const sec = $("sp-resultados");
sec.hidden = false;
const header = document.querySelector("[data-sp-header]");
const offset = header ? header.offsetHeight + 12 : 12;
const top = sec.getBoundingClientRect().top + window.scrollY - offset;
window.scrollTo({ top, behavior: "smooth" });
if (mapa) {
mapa.invalidateSize();
if (cambioDeVista) {
mapa.closePopup();
mapa._encuadrado = false;
}
}
mostrarEstado("Consultando el estado de las playas...");
try {
await pedirUbicacion();
const m = await cargarDatos(modo);
mostrarEstado("");
pintarTodo(m);
} catch (err) {
mostrarEstado(err.message || "No pudimos cargar las playas. Intenta de nuevo.", true);
}
}

function enfocarPlaya(id) {
const marcador = marcadores[String(id)];
if (!mapa || !marcador) {
mostrarEstado("No se encontró la playa en el mapa. Vuelve a cargar los resultados.", true);
return;
}
mapa.invalidateSize();
mapa.setView(marcador.getLatLng(), Math.max(mapa.getZoom(), 12), { animate: true });
marcador.openPopup();
}

document.addEventListener("click", (e) => {
const target = e.target instanceof Element ? e.target : null;
if (!target) return;

const modo = target.closest("[data-modo]");
if (modo) {
void abrirSeccion(modo.dataset.modo);
return;
}

if (target.closest("#sp-ver-todas")) {
void abrirSeccion("todas");
return;
}

if (target.closest("#sp-ver-ideal")) {
void abrirSeccion("ideal");
return;
}

const botonDetalle = target.closest("[data-toggle-detalle]");
if (botonDetalle) {
const detalle = botonDetalle.closest(".sp-card")?.querySelector(".sp-detalle");
if (detalle) {
detalle.hidden = !detalle.hidden;
botonDetalle.textContent = detalle.hidden ? "Ver por qué" : "Ocultar detalles";
botonDetalle.setAttribute("aria-expanded", String(!detalle.hidden));
}
return;
}

const btn = target.closest("[data-ver-mapa]");
if (btn) {
const id = btn.dataset.verMapa;
enfocarPlaya(id);
}
});

async function refrescarPorFiltro() {
if (!modoActual) modoActual = "todas";
const hInput = $("sp-hora");
if (hInput && $("sp-hora-txt")) {
$("sp-hora-txt").textContent = `${String(hInput.value).padStart(2, "0")}:00`;
}
try {
const m = await cargarDatos(modoActual);
mostrarEstado("");
pintarTodo(m);
} catch (err) {
mostrarEstado(err.message || "Error al actualizar los filtros.", true);
}
}

$("sp-fecha")?.addEventListener("change", () => void refrescarPorFiltro());
$("sp-hora")?.addEventListener("input", () => void refrescarPorFiltro());
$("sp-festivo")?.addEventListener("change", () => void refrescarPorFiltro());
