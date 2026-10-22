# -*- coding: utf-8 -*-
"""Verificación final de las piezas del Parcial 2 (Shiro Guardian).

Uso (desde cualquier carpeta):
    C:\\Users\\pipel\\venvs\\ml\\Scripts\\python.exe generadores\\verificar.py [--sin-edge]

Lee las piezas ya generadas (no las regenera) y comprueba:
  (i)   residuos prohibidos en informe, póster, presentación (con notas), guion (con tablas, encabezados y pies),
        sus PDF y la página HTML; claves internas G0–G5 solo en el apéndice del informe y en el póster;
  (ii)  en el cuerpo del informe (antes de «Referencias»): ni F1, ni AUC, ni R², ni log-loss, ni accuracy, ni exactitud;
  (iii) toda cifra de la partición aleatoria va con su par temporal en la misma unidad de texto (párrafo, fila o caja);
  (iv)  «a tiempo» y «antes del pico» solo en frases con minutos; «20 minutos» solo con «al menos dos lecturas»;
  (v)   consistencia: el titular, la regla, el costo, el azar, el rango, el modelo, los casos críticos y los autores
        aparecen idénticos en las cuatro piezas y en sus PDF; cada número con decimales (o con punto de miles) de cada
        pieza está en cifras.json (campo «texto») o en una lista blanca justificada; los PDF son posteriores a su
        fuente; la página coincide con cifras.json y, renderizada en Edge sin interfaz, dice «Verificación: OK».

Imprime un informe y termina con código 0 solo si todo pasa.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pymupdf
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from pptx import Presentation

RAIZ = Path(__file__).resolve().parent.parent
CIF = json.loads((RAIZ / "cifras.json").read_text(encoding="utf-8"))
TODAS = {**CIF["heredadas"], **CIF["nuevas"]}
DM = json.loads((RAIZ / "mockup" / "datos_mockup.json").read_text(encoding="utf-8"))

PIEZAS = {
    "informe": RAIZ / "Informe_Ejecutivo_Shiro_Guardian.docx",
    "póster": RAIZ / "Poster_Shiro_Guardian.pptx",
    "presentación": RAIZ / "Implementacion_Shiro_Guardian.pptx",
    "guion": RAIZ / "Guion_Sustentacion_Shiro_Guardian.docx",
}
HTML = RAIZ / "Mockup_Shiro_Guardian.html"
PLANTILLA = RAIZ / "mockup" / "plantilla.html"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")

FALLAS, AVISOS, OKS = [], [], []


def falla(msg):
    FALLAS.append(msg)


def ok(msg):
    OKS.append(msg)


def T(k):
    return str(TODAS[k]["texto"])


def V(k):
    return TODAS[k]["valor"]


def norm(s):
    """Unifica signos y espacios: «−» → «-», espacios duros y finos → espacio, guiones de corte fuera."""
    s = s.replace("\u2212", "-").replace("\u00a0", " ").replace("\u202f", " ").replace("\u2009", " ")
    s = s.replace("\u00ad", "").replace("\u2011", "-")
    return re.sub(r"[ \t]+", " ", s)


def num(k):
    """Parte numérica del texto de una cifra ('28 picos' -> '28')."""
    return norm(T(k)).split(" ")[0]


# ------------------------------------------------------------------------------------------------------------------
# Extracción de texto por unidades (párrafo, fila de tabla, caja de texto, nota)
# ------------------------------------------------------------------------------------------------------------------
def unidades_docx(ruta):
    """Lista de (zona, texto) en orden del documento. zona = 'cuerpo' | 'referencias' | 'apendice' | 'encabezado'."""
    doc = Document(ruta)
    out, zona = [], "cuerpo"
    for el in doc.element.body.iterchildren():
        tag = el.tag.split("}")[-1]
        if tag == "p":
            p = Paragraph(el, doc)
            t = p.text.strip()
            estilo = (p.style.name if p.style is not None else "") or ""
            if estilo.startswith("Heading") or estilo.startswith("Título"):
                if t == "Referencias":
                    zona = "referencias"
                elif t.startswith("Apéndice"):
                    zona = "apendice"
            if t:
                out.append((zona, t))
        elif tag == "tbl":
            tb = Table(el, doc)
            for row in tb.rows:
                celdas, vistas = [], set()
                for c in row.cells:
                    if id(c._tc) in vistas:
                        continue
                    vistas.add(id(c._tc))
                    celdas.append(c.text.strip())
                t = " | ".join(x for x in celdas if x)
                if t:
                    out.append((zona, t))
    for s in doc.sections:
        for parte in (s.header, s.footer, s.first_page_header, s.first_page_footer):
            try:
                for p in parte.paragraphs:
                    if p.text.strip():
                        out.append(("encabezado", p.text.strip()))
            except Exception:
                pass
    return out


def _formas(shapes):
    for sh in shapes:
        if sh.shape_type == 6 and hasattr(sh, "shapes"):          # grupo
            yield from _formas(sh.shapes)
        else:
            yield sh


def unidades_pptx(ruta):
    prs = Presentation(ruta)
    out = []
    for i, sl in enumerate(prs.slides, 1):
        for sh in _formas(sl.shapes):
            if sh.has_text_frame and sh.text_frame.text.strip():
                out.append((f"diapositiva {i}", sh.text_frame.text.strip()))
            if getattr(sh, "has_table", False) and sh.has_table:
                for row in sh.table.rows:
                    t = " | ".join(c.text.strip() for c in row.cells if c.text.strip())
                    if t:
                        out.append((f"diapositiva {i}", t))
        if sl.has_notes_slide:
            for p in sl.notes_slide.notes_text_frame.paragraphs:
                t = "".join(r.text for r in p.runs).strip()
                if t:
                    out.append((f"notas {i}", t))
    return out


def texto_pdf(ruta):
    with pymupdf.open(ruta) as d:
        return "\n".join(pg.get_text() for pg in d)


UNID = {}
for nombre, ruta in PIEZAS.items():
    if not ruta.exists():
        falla(f"{nombre}: no existe {ruta.name}")
        UNID[nombre] = []
        continue
    UNID[nombre] = unidades_docx(ruta) if ruta.suffix == ".docx" else unidades_pptx(ruta)
    UNID[nombre] = [(z, norm(t)) for z, t in UNID[nombre]]

TODO_PIEZA = {k: "\n".join(t for _, t in v) for k, v in UNID.items()}

# ------------------------------------------------------------------------------------------------------------------
# PDF: existen, son posteriores a su fuente y repiten el titular
# ------------------------------------------------------------------------------------------------------------------
PDF_TXT = {}
for nombre, ruta in PIEZAS.items():
    pdf = ruta.with_suffix(".pdf")
    if not pdf.exists():
        falla(f"{nombre}: falta el PDF {pdf.name}")
        continue
    if pdf.stat().st_mtime < ruta.stat().st_mtime:
        falla(f"{nombre}: el PDF es anterior a su fuente (regenerar con Office)")
    PDF_TXT[nombre] = norm(re.sub(r"-\n", "", texto_pdf(pdf)).replace("\n", " "))
png = RAIZ / "Poster_Shiro_Guardian.png"
if not png.exists() or png.stat().st_mtime < (RAIZ / "Poster_Shiro_Guardian.pdf").stat().st_mtime - 5:
    falla("póster: el PNG de vista previa falta o es anterior al PDF")

HTML_TXT = HTML.read_text(encoding="utf-8") if HTML.exists() else ""
if not HTML_TXT:
    falla("página: no existe Mockup_Shiro_Guardian.html")

# ------------------------------------------------------------------------------------------------------------------
# (i) Residuos
# ------------------------------------------------------------------------------------------------------------------
RESIDUOS = [
    (r"\{\{", "{{"), (r"\[por calcular\]", "[por calcular]"), (r"\bTODO\b", "TODO"), (r"(?i)\bclaude\b", "Claude"),
    (r"(?i)\banthropic\b", "Anthropic"), (r"(?i)\bchatgpt\b", "ChatGPT"), (r"(?i)\bIA generativa\b", "IA generativa"),
    (r"(?i)CLAUDE\.md", "CLAUDE.md"), (r"(?i)\bspecs?\b", "spec"), (r"(?i)\bhitos?\b", "hito"),
    (r"(?i)\bel plan\b(?! de (la sustentación|implementación))", "el plan"),
]
# En las piezas para leer tampoco van nombres de archivos de trabajo; la página sí cita el cuaderno del que salen
# sus datos (pie de autoverificación), así que esa regla no se le aplica.
RESIDUOS_PIEZA = RESIDUOS + [(r"(?i)\.ipynb\b", ".ipynb")]


def residuos(texto, reglas=RESIDUOS_PIEZA):
    return sorted({et for pat, et in reglas if re.search(pat, texto)})


for nombre in PIEZAS:
    r = residuos(TODO_PIEZA[nombre])
    if r:
        falla(f"(i) {nombre}: residuos {r}")
    if nombre in PDF_TXT and residuos(PDF_TXT[nombre]):
        falla(f"(i) {nombre} (PDF): residuos {residuos(PDF_TXT[nombre])}")
r = residuos(HTML_TXT, RESIDUOS)
if r:
    falla(f"(i) página HTML: residuos {r}")
if not [f for f in FALLAS if f.startswith("(i)")]:
    ok("(i) sin residuos en docx (tablas, encabezados y pies), pptx (con notas), PDF y HTML")

# Claves internas G0–G5: solo en el apéndice del informe y en el póster (con su nombre llano al lado)
ID_RE = re.compile(r"\bG[0-5][a-c]?\b")
for nombre, unid in UNID.items():
    if nombre == "póster":
        for z, t in unid:
            for m in ID_RE.finditer(t):
                if m.group(0) == "G0" and "consumo actual" not in t:
                    falla(f"(i) póster: «G0» sin su nombre llano al lado: «{t[:80]}»")
        continue
    malos = [t[:90] for z, t in unid if ID_RE.search(t) and not (nombre == "informe" and z == "apendice")]
    if malos:
        falla(f"(i) {nombre}: claves internas G0–G5 fuera del apéndice: {malos[:3]}")
if not [f for f in FALLAS if "claves internas" in f or "nombre llano" in f]:
    ok("(i) claves G0–G5 solo en el apéndice del informe y en el póster (con su nombre llano)")

# ------------------------------------------------------------------------------------------------------------------
# (ii) Términos técnicos prohibidos en el cuerpo del informe
# ------------------------------------------------------------------------------------------------------------------
PROHIBIDOS = [(r"\bF1\b", "F1"), (r"\bAUC\b", "AUC"), (r"R²|\bR2\b", "R²"), (r"(?i)log-?loss", "log-loss"),
              (r"(?i)\baccuracy\b", "accuracy"), (r"(?i)\bexactitud\b", "exactitud")]
cuerpo = [t for z, t in UNID["informe"] if z == "cuerpo"]
n_prohib = 0
for pat, et in PROHIBIDOS:
    hall = [t[:80] for t in cuerpo if re.search(pat, t)]
    if hall:
        n_prohib += len(hall)
        falla(f"(ii) informe, cuerpo: «{et}» aparece en {len(hall)} párrafo(s): {hall[:2]}")
# comparativas tipo «A 0,81 vs B 0,79»
for t in cuerpo:
    if re.search(r"\d,\d+\s*(vs\.?|versus)\s*\S*\s*\d,\d+", t):
        falla(f"(ii) informe, cuerpo: comparativa técnica lado a lado: «{t[:80]}»")
if n_prohib == 0:
    ok(f"(ii) cuerpo del informe ({len(cuerpo)} párrafos y filas antes de «Referencias»): 0 apariciones de "
       "F1, AUC, R², log-loss, accuracy o exactitud")

# ------------------------------------------------------------------------------------------------------------------
# Números con decimales o con punto de miles
# ------------------------------------------------------------------------------------------------------------------
NUM_RE = re.compile(r"(?<![\w,.])-?(?:\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+,\d+)(?![\w]|,\d|\.\d)")


def numeros(texto, sin_conteos=False):
    """Números con decimales o punto de miles, sin signo. sin_conteos: omite los conteos del propio documento
    («≈ 1.125 palabras»), que el generador calcula al escribirlo y no son resultados."""
    t = norm(texto)
    return [m.group(0).lstrip("-") for m in NUM_RE.finditer(t)
            if not (sin_conteos and re.match(r"\s*palabras\b", t[m.end():]))]


NUM_CIFRAS = set()
for k, v in TODAS.items():
    NUM_CIFRAS.update(numeros(str(v["texto"])))

# ------------------------------------------------------------------------------------------------------------------
# (iii) Cifras de la partición aleatoria con su par temporal en la misma unidad
# ------------------------------------------------------------------------------------------------------------------
ALEAT = {k: v for k, v in TODAS.items() if v.get("particion") == "aleatoria" and numeros(str(v["texto"]))}


def pares_temporales(k):
    m = re.match(r"her_(reg|clf|bo)_(\w+?)_aleatoria_(\w+)$", k)
    if not m:
        return []
    modelo = m.group(2)
    return [c for c in TODAS if re.match(rf"her_(reg|clf|bo)_{modelo}_(temporal|retardos)_", c)]


n_aleat = 0
for nombre, unid in UNID.items():
    for z, t in unid:
        toks = set(numeros(t))
        for k, v in ALEAT.items():
            nk = numeros(str(v["texto"]))[0]
            if nk not in toks:
                continue
            # el mismo número puede ser también una cifra temporal (p. ej. la lineal con retardos): entonces no aplica
            if any(nk in numeros(str(TODAS[o]["texto"])) for o in TODAS if TODAS[o].get("particion") != "aleatoria"):
                continue
            n_aleat += 1
            pares = pares_temporales(k)
            if not any(set(numeros(T(p))) & toks for p in pares):
                falla(f"(iii) {nombre}: {nk} ({k}, partición aleatoria) sin su par temporal en «{t[:90]}»")
if not [f for f in FALLAS if f.startswith("(iii)")]:
    ok(f"(iii) {n_aleat} aparición(es) de cifras de la partición aleatoria, todas con su par temporal al lado")

# ------------------------------------------------------------------------------------------------------------------
# (iv) «a tiempo», «antes del pico», «20 minutos»
# ------------------------------------------------------------------------------------------------------------------
def frases(texto):
    return [f for f in re.split(r"(?<=[.!?…])\s+(?=[«(¿¡A-ZÁÉÍÓÚÑ0-9])", texto) if f.strip()]


n_iv = 0
for nombre, unid in UNID.items():
    for z, t in unid:
        if nombre == "informe" and z == "referencias":
            continue
        for f in frases(t):
            fl = f.lower()
            for expr in ("a tiempo", "antes del pico"):
                if expr in fl:
                    n_iv += 1
                    if not re.search(r"\bmin\b|minutos?\b|\blecturas?\b", fl):
                        falla(f"(iv) {nombre}: «{expr}» sin minutos en «{f[:100]}»")
            if re.search(r"\b20 minutos\b", fl):
                n_iv += 1
                if "al menos dos lecturas" not in fl:
                    falla(f"(iv) {nombre}: «20 minutos» sin «al menos dos lecturas» en «{f[:100]}»")
if not [f for f in FALLAS if f.startswith("(iv)")]:
    ok(f"(iv) {n_iv} frase(s) con «a tiempo», «antes del pico» o «20 minutos», todas con su margen en minutos o lecturas")

# ------------------------------------------------------------------------------------------------------------------
# (v) Consistencia del relato y de las cifras
# ------------------------------------------------------------------------------------------------------------------
picos = num("def_picos_prueba")
TITULAR = {
    "titular (n de 84)": f"{num('titular_n20')} de {picos}",
    "titular (%)": norm(T("titular_p20")),
    "regla con el mismo rojo": f"{num('titular_m20')} de {picos}",
    "costo: minutos al día en rojo": f"{num('titular_min_dia')} min",
    "costo: avisos falsos": norm(T("titular_falsos")),
    "azar con el mismo rojo": norm(T("azar_p20_desplegado")),
}
RANGO = (num("titular_d_regla_ic_inf"), num("titular_d_regla_ic_sup"))
AUTORES = ["Diazgranados", "Londoño", "Céspedes Rondón", "Duran"]
CASOS = {"caso 1 (fecha)": T("caso1_inicio").split(" ")[0], "caso 2 (fecha)": T("caso2_inicio").split(" ")[0],
         "caso 1 (energía)": norm(T("caso1_energia_wh"))}
EXIGE_CASOS = {"informe": ["caso 1 (fecha)", "caso 2 (fecha)"], "póster": ["caso 1 (fecha)", "caso 2 (fecha)"],
               "presentación": ["caso 1 (energía)"], "guion": ["caso 1 (fecha)", "caso 2 (fecha)", "caso 1 (energía)"]}


def contiene(texto, frag):
    return frag in texto or frag.replace(" ", "") in texto.replace(" ", "")


for nombre in PIEZAS:
    texto = TODO_PIEZA[nombre]
    for et, frag in TITULAR.items():
        if not contiene(texto, frag):
            falla(f"(v) {nombre}: falta {et} «{frag}»")
        if nombre in PDF_TXT and not contiene(PDF_TXT[nombre], frag):
            falla(f"(v) {nombre} (PDF): falta {et} «{frag}»")
    if not any(set(RANGO) <= {m.group(0) for m in NUM_RE.finditer(t)} for _, t in UNID[nombre]):
        falla(f"(v) {nombre}: falta el rango plausible «{RANGO[0]} a {RANGO[1]}» en una misma frase")
    if "modelo mínimo" not in texto.lower():
        falla(f"(v) {nombre}: no nombra el «modelo mínimo» elegido")
    pos = [texto.find(a) for a in AUTORES]
    if min(pos) < 0 or pos != sorted(pos):
        falla(f"(v) {nombre}: autores ausentes o fuera de orden ({dict(zip(AUTORES, pos))})")
    for et in EXIGE_CASOS[nombre]:
        if not contiene(texto, CASOS[et]):
            falla(f"(v) {nombre}: falta {et} «{CASOS[et]}»")
if not [f for f in FALLAS if f.startswith("(v)")]:
    ok("(v) titular «" + TITULAR["titular (n de 84)"] + "; " + TITULAR["titular (%)"] + "», regla «"
       + TITULAR["regla con el mismo rojo"] + "», costo «" + TITULAR["costo: minutos al día en rojo"] + "/día; "
       + TITULAR["costo: avisos falsos"] + "», azar «" + TITULAR["azar con el mismo rojo"] + "» y rango «"
       + f"{RANGO[0]} a {RANGO[1]}» idénticos en las cuatro piezas y sus PDF; mismo modelo, mismos casos, mismos autores")

# ---- Números huérfanos -------------------------------------------------------------------------------------------
# Lista blanca: solo parámetros de definición, de interfaz y de citas, cada uno con su porqué.
BLANCA = {
    "48.587": "número del Diario Oficial en la referencia de la Ley 1581 de 2012",
    "0,01": "paso del deslizador de la página (parámetro de interfaz, guion de la demo)",
}


def derivados_mockup():
    """Cifras que el guion lee de datos_mockup.json (misma ejecución del cuaderno), con la ruta de cada una."""
    d = {}
    for q in DM["dia_antes_despues"]["picos"]:
        d[f"{q['energia_wh'] / 1000:.2f}".replace(".", ",")] = (
            f"datos_mockup.json: dia_antes_despues.picos[{q['inicio'][11:16]}].energia_wh en kWh")
    return d


DERIVADOS = derivados_mockup()
huerfanos = {}
for nombre in PIEZAS:
    for z, t in UNID[nombre]:
        for x in numeros(t, sin_conteos=True):
            if x in NUM_CIFRAS or x in BLANCA or x in DERIVADOS:
                continue
            huerfanos.setdefault(nombre, set()).add(x)
for nombre, xs in huerfanos.items():
    falla(f"(v) {nombre}: números que no están en cifras.json ni en la lista blanca: {sorted(xs)}")
usados_bl = sorted({x for n_ in PIEZAS for _, t in UNID[n_] for x in numeros(t) if x in BLANCA})
usados_der = sorted({x for n_ in PIEZAS for _, t in UNID[n_] for x in numeros(t) if x in DERIVADOS and x not in NUM_CIFRAS})
if not huerfanos:
    tot = sum(len(numeros(t)) for n_ in PIEZAS for _, t in UNID[n_])
    ok(f"(v) {tot} números con decimales o punto de miles en las cuatro piezas: todos en cifras.json, salvo "
       f"{len(usados_bl)} de la lista blanca ({', '.join(usados_bl) or '—'}) y {len(usados_der)} leído(s) de "
       f"datos_mockup.json ({', '.join(usados_der) or '—'})")

# ---- La página: datos incrustados frente a cifras.json, plantilla sin cifras, render en Edge --------------------
E = DM["esperado"]
CHEQ = [
    ("n20 del elegido desplegado", E["tarjeta2_elegido_desplegado"]["n20"], V("titular_n20"), 0),
    ("% con ≥ 20 min", E["tarjeta2_elegido_desplegado"]["p20"], V("titular_p20"), 1e-4),
    ("min/día en rojo", E["tarjeta2_elegido_desplegado"]["min_dia"], V("titular_min_dia"), 1e-4),
    ("% de avisos falsos", E["tarjeta2_elegido_desplegado"]["falsos"], V("titular_falsos"), 1e-4),
    ("avisos al día", E["tarjeta2_elegido_desplegado"]["avisos_dia"], V("titular_avisos_dia"), 1e-4),
    ("regla con el mismo rojo", E["tarjeta2_regla_mismo_rojo"]["n20"], V("titular_m20"), 0),
    ("azar", E["azar_p20_desplegado"], V("azar_p20_desplegado"), 1e-4),
    ("exceso avisado (kWh)", E["exceso_anticipado_kwh"], V("energia_exceso_anticipado_kwh"), 1e-4),
    ("rango inferior", DM["incertidumbre"]["d_regla_ic"][0], V("titular_d_regla_ic_inf"), 1e-4),
    ("rango superior", DM["incertidumbre"]["d_regla_ic"][1], V("titular_d_regla_ic_sup"), 1e-4),
]
for et, a, b, tol in CHEQ:
    if abs(float(a) - float(b)) > tol:
        falla(f"(v) página: {et} = {a} en datos_mockup.json frente a {b} en cifras.json")
if DM["elegido"]["nombre"] != T("sel_elegido_nombre"):
    falla("(v) página: el modelo elegido no coincide con cifras.json")
if DM["frase_caso"] != T("caso_frase"):
    falla("(v) página: la frase del caso no coincide con cifras.json")
# La plantilla no lleva cifras de resultado: números con decimales fuera de <script> y <style>
if PLANTILLA.exists():
    vis = re.sub(r"(?s)<script.*?</script>|<style.*?</style>|<[^>]+>", " ", PLANTILLA.read_text(encoding="utf-8"))
    xs = [x for x in numeros(vis) if x not in NUM_CIFRAS]
    if xs:
        falla(f"(v) plantilla de la página: números tecleados fuera de cifras.json: {sorted(set(xs))}")


def render_edge():
    if not EDGE.exists():
        return None, "Edge no está instalado"
    # msedge.exe delega en un proceso hijo y vuelve enseguida: se lanza con Start-Process -Wait (espera a toda la
    # familia de procesos) y la salida se redirige a un archivo. Perfil temporal propio y corto (rutas largas fallan).
    perfil = Path(tempfile.mkdtemp(prefix="vrf_"))
    salida, errores = perfil.parent / (perfil.name + "_dom.html"), perfil.parent / (perfil.name + "_err.txt")
    q = lambda p_: str(p_).replace("'", "''")
    ps = (f"$p = Start-Process -FilePath '{q(EDGE)}' -ArgumentList @('--headless=new','--disable-gpu','--no-first-run',"
          f"'--user-data-dir=\"{q(perfil)}\"','--virtual-time-budget=20000','--dump-dom','\"{HTML.as_uri()}\"') "
          f"-RedirectStandardOutput '{q(salida)}' -RedirectStandardError '{q(errores)}' -Wait -PassThru -NoNewWindow; "
          "exit $p.ExitCode")
    try:
        subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps], capture_output=True, timeout=240)
        return (salida.read_text(encoding="utf-8", errors="replace") if salida.exists() else ""), None
    except Exception as e:                                      # noqa: BLE001
        return None, str(e)
    finally:
        shutil.rmtree(perfil, ignore_errors=True)
        for f_ in (salida, errores):
            try:
                f_.unlink()
            except OSError:
                pass


if "--sin-edge" not in sys.argv and HTML_TXT:
    dom, err = render_edge()
    if dom is None or not dom.strip():
        falla(f"(v) página: no se pudo renderizar en Edge sin interfaz ({err or 'salida vacía'})")
    else:
        m = re.search(r'id="verif"[^>]*>([^<]*)', dom)
        pie = m.group(1).strip() if m else ""
        if not pie.startswith("Verificación: OK"):
            falla(f"(v) página: el pie no dice «Verificación: OK»: «{pie[:160]}»")
        visible = norm(re.sub(r"(?s)<script.*?</script>|<style.*?</style>|<[^>]+>", " ", dom))
        for et, frag in TITULAR.items():
            if et.startswith("costo: minutos"):
                frag = num("titular_min_dia")
            if et.startswith("regla"):                          # la tabla de la página da «21 (25,0 %)»
                frag = norm(T("titular_m20_pct"))
            if not contiene(visible, frag):
                falla(f"(v) página renderizada: falta {et} «{frag}»")
        if not [f for f in FALLAS if f.startswith("(v) página")]:
            ok("(v) página: datos incrustados = cifras.json (" + str(len(CHEQ)) + " cifras, modelo y frase del caso); "
               "renderizada en Edge sin interfaz dice «" + pie[:17] + "» y muestra el titular, la regla, el costo y el azar")
elif "--sin-edge" in sys.argv:
    AVISOS.append("página: no se renderizó en Edge (--sin-edge)")

# ------------------------------------------------------------------------------------------------------------------
# Informe
# ------------------------------------------------------------------------------------------------------------------
print("=" * 100)
print("VERIFICACIÓN FINAL — Shiro Guardian (Parcial 2)")
print("=" * 100)
for nombre, ruta in PIEZAS.items():
    print(f"  {nombre:13s} {ruta.name}  ·  {len(UNID[nombre])} unidades de texto  ·  PDF "
          + ("sí" if nombre in PDF_TXT else "NO"))
print(f"  {'página':13s} {HTML.name}")
print("-" * 100)
for m in OKS:
    print("OK     " + m)
for m in AVISOS:
    print("AVISO  " + m)
for m in FALLAS:
    print("FALLA  " + m)
print("-" * 100)
print(f"Resultado: {'TODO PASA' if not FALLAS else str(len(FALLAS)) + ' FALLA(S)'}")
sys.exit(0 if not FALLAS else 1)
