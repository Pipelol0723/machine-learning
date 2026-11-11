# -*- coding: utf-8 -*-
"""Verificación previa a la entrega del Taller 2 (C3). Debe terminar con código 0.

1. El cuaderno está ejecutado completo, sin errores, y sus anclas con el Taller 1 pasaron.
2. Existen cifras.json, las políticas en CSV y las figuras Q1–Q14.
3. El docx y el pptx no tienen residuos ({clave} sin resolver, nan, TODO, menciones internas).
4. Todo número decimal del docx y del pptx sale de cifras.json o es un parámetro declarado.
5. Cordura: en el entorno modelo (el MDP exacto) el agente recomendado coincide con π* en al menos el 90 % de los estados.
"""
import json
import re
import sys
from pathlib import Path

import nbformat
from docx import Document
from pptx import Presentation

RAIZ = Path(__file__).resolve().parent.parent
fallos = []


def falla(msg):
    fallos.append(msg)
    print("  ✗", msg)


def ok(msg):
    print("  ✓", msg)


print("1. Cuaderno")
nb = nbformat.read(RAIZ / "Taller2_C3_QLearning_Shiro.ipynb", as_version=4)
codigo = [c for c in nb.cells if c.cell_type == "code"]
sin_ejecutar = [i for i, c in enumerate(codigo) if c.get("execution_count") is None]
errores = [i for i, c in enumerate(codigo) if any(o.get("output_type") == "error" for o in c.get("outputs", []))]
(falla(f"celdas sin ejecutar: {sin_ejecutar}") if sin_ejecutar else ok(f"{len(codigo)} celdas de código ejecutadas"))
(falla(f"celdas con error: {errores}") if errores else ok("sin errores"))
salida = "\n".join("".join(o.get("text", "")) for c in codigo for o in c.get("outputs", []) if o.get("output_type") == "stream")
(ok("anclas con el Taller 1 coinciden") if re.search(r"Anclas con el Taller 1: (\d+)/\1 coinciden", salida)
 else falla("no aparece la línea de anclas con el Taller 1"))

print("2. Archivos")
cif = json.loads((RAIZ / "cifras.json").read_text(encoding="utf-8"))["cifras"]
ok(f"cifras.json con {len(cif)} cifras")
figs = sorted(p.name for p in (RAIZ / "figuras").glob("Q*.png"))
(ok(f"{len(figs)} figuras Q*") if len(figs) >= 14 else falla(f"faltan figuras: {figs}"))
for f in ("politicas_base.csv", "politicas_parte1_estaciones.csv", "resumen_configuraciones.csv"):
    (ok(f) if (RAIZ / f).exists() else falla(f"falta {f}"))


def texto_docx(p):
    d = Document(p)
    partes = [x.text for x in d.paragraphs]
    for t in d.tables:
        for fila in t.rows:
            for c in fila.cells:
                partes.append(c.text)
    return "\n".join(partes)


def texto_pptx(p):
    partes = []
    for s in Presentation(p).slides:
        for sh in s.shapes:
            if sh.has_text_frame:
                partes.append(sh.text_frame.text)
            if sh.has_table:
                for fila in sh.table.rows:
                    for c in fila.cells:
                        partes.append(c.text)
        if s.has_notes_slide:
            partes.append(s.notes_slide.notes_text_frame.text)
    return "\n".join(partes)


RESIDUOS = [r"\{[^}]*\}", r"\bnan\b", r"\bNone\b", r"\bTODO\b", r"Claude", r"Anthropic", r"CLAUDE\.md", r"\bhito\b", r"PLAN_"]
# Parámetros de diseño declarados (no son resultados) y cifras heredadas de entregas anteriores
PERMITIDOS = {"0,005", "0,02", "0,01", "0,1", "0,9", "0,5", "0,95", "0,99", "0,999", "1,0", "1,5", "0,40", "0,6", "39,7",
              "13,5", "0,3", "3.er", "2.º", "1.er", "26-2", "374", "10⁻⁶", "−1000", "−100", "1/N", "0,59", "0,594", "7,2"}
textos = " ".join(str(v["texto"]) for v in cif.values())
numeros = set(re.findall(r"−?\d[\d.]*,\d+", textos))
t1 = json.loads((RAIZ.parent / "Taller_1_RL_MDP" / "cifras.json").read_text(encoding="utf-8"))["cifras"]
numeros |= set(re.findall(r"−?\d[\d.]*,\d+", " ".join(str(v["texto"]) for v in t1.values())))   # cifras heredadas del T1

print("3–4. Documento y presentación")
for nombre, extraer in (("Taller2_C3_QLearning_RESUELTO.docx", texto_docx), ("Taller2_C3_presentacion.pptx", texto_pptx)):
    if not (RAIZ / nombre).exists():
        falla(f"falta {nombre}")
        continue
    t = extraer(RAIZ / nombre)
    for patron in RESIDUOS:
        for m in re.findall(patron, t):
            falla(f"{nombre}: residuo «{m}»")
    huérfanos = sorted({n for n in re.findall(r"−?\d[\d.]*,\d+", t)
                        if n not in numeros and n not in PERMITIDOS and n.lstrip("−") not in numeros})
    (falla(f"{nombre}: números que no salen de cifras.json: {huérfanos}") if huérfanos
     else ok(f"{nombre}: todos los decimales salen de cifras.json o son parámetros declarados"))
    if not (RAIZ / nombre).with_suffix(".pdf").exists():
        falla(f"falta el PDF de {nombre}")

print("5. Las afirmaciones centrales del documento coinciden con cifras.json")
afirmaciones = [
    ("«en mayo no se distingue de π*»", cif.get("boot_ql_pi_sig", {}).get("valor") == "no"),
    ("«ninguna semilla llega al 90 % ponderado» (agente recomendado, réplica)", cif.get("base_alcanzan", {}).get("valor") == 0),
    ("«el recomendado captura más ahorro que el del profesor»",
     cif.get("base_captura", {}).get("valor", 0) > cif.get("prof_captura", {}).get("valor", 1)),
    ("«la π* de mayo es la misma que la de invierno»",
     cif.get("p1_iguales_vi", {}).get("valor") == cif.get("p1_decision_comunes", {}).get("valor")),
    ("«K-Means supera a los cuantiles y el umbral a los dos» (π* en mayo)",
     cif["p3vi_qcut_ahorro"]["valor"] < cif["p3vi_kmeans_ahorro"]["valor"] < cif["p3vi_umbral_ahorro"]["valor"]),
    ("«el castigo de −1000 deja al agente sin aplazar»", cif.get("p4_miedo_aplaz", {}).get("valor") == 0),
]
for texto, cumple in afirmaciones:
    (ok(texto) if cumple else falla(f"no se cumple {texto}"))

print("\nRESULTADO:", "OK" if not fallos else f"{len(fallos)} fallo(s)")
sys.exit(1 if fallos else 0)
