# -*- coding: utf-8 -*-
r"""Verificación previa a la entrega del Parcial 3 (C3). Debe terminar con código 0.

1. Datos: consola.json, cifras_c2.json (con sus anclas) y cifras_p3.json existen y son coherentes.
2. Consola: Edge headless abre Consola_Shiro.html#prueba y la propia página confirma que su iteración de valor, su red
   DQN y su K-Means calculan lo mismo que Python (35/35 políticas, Q < 1e-6, red < 1e-6, margen < 1e-4).
3. Consola: sin residuos ([[clave]], {p2:…}, undefined, NaN, TODO…) y todo decimal del texto fijo sale de las cifras del
   semestre o es un parámetro declarado. El fragmento para publicar existe y no trae <html>/<head>/<body>.
4. Artículo: sin residuos, decimales trazables, 5–7 páginas en el PDF, y la regla de las dos particiones (un párrafo o
   una tabla que cita la partición aleatoria cita también la temporal).
5. Capturas de la consola para el artículo.

Uso (desde la carpeta del parcial):
    C:\Users\pipel\venvs\ml\Scripts\python.exe -X utf8 generadores\verificar.py
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import RAIZ, cargar  # noqa: E402

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
fallos = []


def falla(msg):
    fallos.append(msg)
    print("  ✗", msg)


def ok(msg):
    print("  ✓", msg)


DEC = re.compile(r"−?\d[\d.]*,\d+")
TODAS = cargar()
NUMEROS = set()
for v in TODAS.values():
    NUMEROS |= set(DEC.findall(str(v.get("texto", ""))))
# Parámetros de diseño declarados (no son resultados)
PERMITIDOS = {"0,005", "0,02", "0,01", "0,95", "0,99", "0,05", "1,0", "1,5", "2,0", "3,0", "0,001", "0,6", "0,5", "0,1",
              "3.er", "2.º", "1.er", "2.ª", "26-2", "0,40", "1,2", "0,03", "0,002", "0,0"}


def huérfanos(texto):
    return sorted({n for n in DEC.findall(texto) if n not in NUMEROS and n not in PERMITIDOS and n.lstrip("−") not in NUMEROS})


RESIDUOS = [r"\[\[[^\]]*\]\]", r"\{(p2|t1|t2|t3|c2|p3):[^}]*\}", r"\bundefined\b", r"\bNaN\b", r"\bnan\b", r"\bTODO\b",
            r"\bNone\b", r"CLAUDE\.md", r"PLAN_PARCIAL", r"lorem"]

print("1. Datos")
for f in ("consola.json", "cifras_c2.json", "cifras_p3.json", "dbscan_mayo.json"):
    (ok(f"datos/{f}") if (RAIZ / "datos" / f).exists() else falla(f"falta datos/{f}"))
c2 = json.loads((RAIZ / "datos" / "cifras_c2.json").read_text(encoding="utf-8"))
anc = c2["meta"].get("anclas")
n_anc = len(anc) if isinstance(anc, (list, dict)) else anc
ok(f"cifras_c2.json: {len(c2['cifras'])} cifras, anclas registradas: {n_anc}")
p3 = json.loads((RAIZ / "datos" / "cifras_p3.json").read_text(encoding="utf-8"))["cifras"]
ok(f"exportar_datos.py: {p3['n_anclas_exportador']['valor']} anclas superadas")

print("2. Consola: autoprueba en Edge headless")
CONS = RAIZ / "Consola_Shiro.html"
if not CONS.exists():
    falla("falta Consola_Shiro.html")
else:
    url = CONS.resolve().as_uri() + "#prueba"
    r = subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-first-run", "--virtual-time-budget=15000",
                        "--dump-dom", url], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
    m = re.search(r'<pre[^>]*id="resultado-pruebas"[^>]*>(.*?)</pre>', r.stdout, re.S)
    if not m:
        falla("Edge no devolvió #resultado-pruebas (¿la página falló al cargar?)")
    else:
        res = json.loads(html.unescape(m.group(1)))
        print("    ", json.dumps(res, ensure_ascii=False)[:400])
        txt = json.dumps(res).lower()
        vi_ok = res.get("vi_identicas", res.get("politicas_identicas"))
        vi_tot = res.get("vi_total", res.get("politicas_total"))
        (ok(f"VI en la página: {vi_ok}/{vi_tot} políticas idénticas a Python") if vi_ok is not None and vi_ok == vi_tot == 35
         else falla(f"VI en la página: {vi_ok}/{vi_tot}"))
        for clave, tope in (("vi_error_q", 1e-6), ("red_error", 1e-6), ("margen_error", 1e-4)):
            v = res.get(clave)
            (ok(f"{clave} = {v:.2e} < {tope}") if isinstance(v, (int, float)) and v < tope else falla(f"{clave} = {v}"))
    sin_js = re.sub(r"<script.*?</script>|<style.*?</style>", " ", CONS.read_text(encoding="utf-8"), flags=re.S)
    visible = html.unescape(re.sub(r"<[^>]+>", " ", sin_js))
    for patron in RESIDUOS:
        for x in set(re.findall(patron, visible)):
            falla(f"consola: residuo «{x}»")
    h = huérfanos(visible)
    (falla(f"consola: decimales que no salen de las cifras: {h}") if h else ok("consola: todos los decimales del texto fijo son trazables"))
    frag = RAIZ / "datos" / "consola_artifact.html"
    if not frag.exists():
        falla("falta datos/consola_artifact.html (fragmento para publicar)")
    else:
        t = frag.read_text(encoding="utf-8")[:20000].lower()
        (falla("el fragmento trae <html>/<head>/<body> o doctype") if re.search(r"<!doctype|<html[\s>]|<head[\s>]|<body[\s>]", t)
         else ok("fragmento para publicar sin esqueleto propio"))
        (ok("fragmento con <title>") if "<title>" in t[:8000] else falla("el fragmento no tiene <title> en los primeros 8 KB"))
    kb = CONS.stat().st_size / 1024
    ok(f"tamaño de la consola: {kb:,.0f} KB")

print("3. Artículo")
DOCX = RAIZ / "Articulo_IEEE_Shiro_Twin.docx"
PDF = DOCX.with_suffix(".pdf")
if not DOCX.exists():
    falla("falta Articulo_IEEE_Shiro_Twin.docx")
else:
    from docx import Document
    d = Document(DOCX)
    bloques = [p.text for p in d.paragraphs]
    for t in d.tables:
        bloques.append(" | ".join(c.text for fila in t.rows for c in fila.cells))
    todo = "\n".join(bloques)
    for patron in RESIDUOS:
        for x in set(re.findall(patron, todo)):
            falla(f"artículo: residuo «{x}»")
    h = huérfanos(todo)
    (falla(f"artículo: decimales que no salen de las cifras: {h}") if h else ok("artículo: todos los decimales son trazables"))
    malos = [b[:90] for b in bloques if re.search(r"\baleatori[ao]s?\b", b, re.I) and re.search(r"R²|F1|R2", b)
             and not re.search(r"\btemporal", b, re.I)]
    (falla(f"artículo: cita la partición aleatoria sin la temporal en {len(malos)} bloque(s): {malos[:3]}") if malos
     else ok("artículo: regla de las dos particiones"))
    if PDF.exists():
        import pymupdf
        n = len(pymupdf.open(PDF))
        (ok(f"PDF del artículo: {n} páginas") if 5 <= n <= 7 else falla(f"PDF del artículo: {n} páginas (se esperaban 5–7)"))
    else:
        falla("falta el PDF del artículo")

print("4. Capturas")
caps = sorted(p.name for p in (RAIZ / "figuras").glob("consola_*.png"))
(ok(f"{len(caps)} capturas: {caps}") if "consola_captura.png" in caps else falla(f"falta figuras/consola_captura.png ({caps})"))

print("\nRESULTADO:", "OK" if not fallos else f"{len(fallos)} fallo(s)")
sys.exit(1 if fallos else 0)
