# -*- coding: utf-8 -*-
"""Construye la Consola de Shiro (Parcial 3) a partir de generadores/consola_plantilla.html.

Salidas:
    Consola_Shiro.html            documento completo, autocontenido, para adjuntar y abrir sin internet
    datos/consola_artifact.html   la misma página como fragmento (sin doctype/html/head/body) para publicarla
    figuras/consola_*.png         capturas con Edge headless (se omiten con --sin-edge)

Cada [[prefijo:clave]] de la plantilla se sustituye con comun.C(clave); una clave que no existe detiene la
construcción. Las claves que usa el JavaScript están en <script id="cifras-claves"> y se incrustan como CIFRAS.
Uso:  python -X utf8 generadores/construir_consola.py [--sin-edge]
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402

RAIZ = comun.RAIZ
PLANTILLA = Path(__file__).resolve().parent / "consola_plantilla.html"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
VISTAS = ["hoy", "tipo", "shiro", "pregunta", "ficha"]
RESET = ("<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);"
         "padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif}"
         "img{max-width:100%}[hidden]{display:none!important}</style>")


def incrustar(ident, objeto):
    txt = json.dumps(objeto, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/json" id="{ident}">{txt}</script>'


def menos(texto):
    """Signo menos tipográfico: algunas fuentes escriben -2,891 y otras −0,078."""
    return re.sub(r"(?<![\w,.])-(?=\d)", "−", texto)


def construir():
    ruta_db = RAIZ / "datos" / "dbscan_mayo.json"
    ruta_datos = RAIZ / "datos" / "consola.json"
    for r, quien in ((ruta_datos, "exportar_datos.py"), (ruta_db, "exportar_c2.py")):
        if not r.exists():
            sys.exit(f"ERROR: falta {r.relative_to(RAIZ)}; lo genera {quien}. Vuelve a ejecutar cuando exista.")
    datos = json.loads(ruta_datos.read_text(encoding="utf-8"))
    dbscan = json.loads(ruta_db.read_text(encoding="utf-8"))
    fechas = [d["fecha"] for d in dbscan]
    if fechas != datos["dias"]:
        sys.exit("ERROR: dbscan_mayo.json no trae los mismos 26 días (y en el mismo orden) que consola.json.")
    for d in dbscan:
        if d["dbscan"] not in ("en grupo", "atípico", "desconocido"):
            sys.exit(f"ERROR: estado DBSCAN inesperado en {d['fecha']}: {d['dbscan']!r}")

    html = PLANTILLA.read_text(encoding="utf-8")
    comun.recargar()
    usadas = set()

    def sust(m):
        clave, entero = m.group(1), m.group(2)
        usadas.add(clave)
        if entero:                       # [[prefijo:clave|n]] → solo el número entero, sin unidad
            v = comun.V(clave)
            comun.C(clave)
            if float(v) != int(v):
                sys.exit(f"ERROR: [[{clave}|n]] pide un entero y la cifra vale {v}")
            return f"{int(v):,}".replace(",", ".")
        return menos(comun.C(clave))

    html = re.sub(r"\[\[([a-z0-9]+:[^\[\]\s|]+)(\|n)?\]\]", sust, html)
    if "[[" in html.split("<script>")[0]:
        sys.exit("ERROR: quedó un marcador [[…]] sin sustituir en el texto de la plantilla.")

    m = re.search(r'<script type="application/json" id="cifras-claves">(.*?)</script>', html, re.S)
    claves = json.loads(m.group(1))
    cifras = {k: {"valor": comun.V(k), "texto": menos(comun.C(k))} for k in claves}
    usadas.update(claves)
    cifras["_n"] = len(usadas)
    html = html.replace(m.group(0), "")
    bloque = incrustar("datos", datos) + "\n" + incrustar("dbscan", dbscan) + "\n" + incrustar("cifras", cifras)
    if "<!--DATOS-->" not in html or "<!--CUERPO-->" not in html:
        sys.exit("ERROR: la plantilla perdió el marcador <!--DATOS--> o <!--CUERPO-->.")
    html = html.replace("<!--DATOS-->", bloque)
    cabeza, cuerpo = html.split("<!--CUERPO-->")

    completo = ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                + RESET + "\n" + cabeza.strip() + "\n</head>\n<body>\n" + cuerpo.strip() + "\n</body>\n</html>\n")
    fragmento = cabeza.strip() + "\n" + cuerpo.strip() + "\n"
    assert fragmento.lstrip().startswith("<title>") and "<!doctype" not in fragmento.lower()
    (RAIZ / "Consola_Shiro.html").write_text(completo, encoding="utf-8", newline="\n")
    (RAIZ / "datos" / "consola_artifact.html").write_text(fragmento, encoding="utf-8", newline="\n")
    print(f"Consola_Shiro.html: {len(completo.encode('utf-8')) / 1024:.0f} KB · {len(usadas)} cifras "
          f"({len(claves)} también en JS)")
    return RAIZ / "Consola_Shiro.html"


def edge(args, url, espera=120):
    perfil = tempfile.mkdtemp(prefix="shiro_edge_")
    try:
        r = subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={perfil}",
                            "--virtual-time-budget=8000", *args, url],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=espera)
        return r.stdout or ""
    finally:
        shutil.rmtree(perfil, ignore_errors=True)


def probar(pagina):
    dom = edge(["--dump-dom"], pagina.as_uri() + "#prueba")
    m = re.search(r'<pre id="resultado-pruebas">(.*?)</pre>', dom, re.S)
    if not m:
        sys.exit("ERROR: Edge no devolvió la vista #prueba.")
    txt = m.group(1).replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    try:
        res = json.loads(txt)
    except ValueError:
        sys.exit(f"ERROR: #resultado-pruebas no es JSON: {txt[:300]}")
    print("#prueba:", json.dumps(res, ensure_ascii=False))
    pie = re.search(r'<span id="verif"[^>]*>(.*?)</span>', dom, re.S)
    print("pie:", pie.group(1) if pie else "?")
    bien = (res.get("ok") and res.get("vi_identicas") == res.get("vi_total") == 35 and res.get("vi_error_q", 1) < 1e-6
            and res.get("red_error", 1) < 1e-6 and res.get("margen_error", 1) < 1e-4 and res.get("cifras_ok"))
    if not bien:
        sys.exit("ERROR: la página no supera sus pruebas.")


def capturar(pagina):
    fig = RAIZ / "figuras"
    fig.mkdir(exist_ok=True)
    for v in VISTAS:
        destino = fig / f"consola_{v}.png"
        edge([f"--screenshot={destino}", "--window-size=1440,1000", "--hide-scrollbars",
              "--force-device-scale-factor=1"], pagina.as_uri() + "#" + v)
        if not destino.exists():
            sys.exit(f"ERROR: no se pudo capturar {destino.name}")
        print("captura:", destino.name, f"{destino.stat().st_size / 1024:.0f} KB")
    shutil.copyfile(fig / "consola_shiro.png", fig / "consola_captura.png")


if __name__ == "__main__":
    pagina = construir()
    if "--sin-edge" not in sys.argv:
        probar(pagina)
        capturar(pagina)
    print("OK")
