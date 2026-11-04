# -*- coding: utf-8 -*-
"""Verificación previa a la entrega del Taller 1 (C3). Debe terminar con código 0.

1. El cuaderno está ejecutado completo y sin errores.
2. Existen cifras.json, la política en CSV y las figuras R1–R8.
3. El docx y el pptx no tienen residuos ({clave} sin resolver, nan, TODO, menciones internas).
4. Todo número decimal del docx y del pptx sale de cifras.json o es un parámetro declarado.
5. La prueba de cordura se cumple (tarifa plana → 0 estados aplazan) y la política del CSV coincide con cifras.json.
"""
import csv
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
nb = nbformat.read(RAIZ / "Taller1_C3_MDP_Shiro.ipynb", as_version=4)
codigo = [c for c in nb.cells if c.cell_type == "code"]
sin_ejecutar = [i for i, c in enumerate(codigo) if c.get("execution_count") is None]
errores = [i for i, c in enumerate(codigo) if any(o.get("output_type") == "error" for o in c.get("outputs", []))]
(falla(f"celdas sin ejecutar: {sin_ejecutar}") if sin_ejecutar else ok(f"{len(codigo)} celdas de código ejecutadas"))
(falla(f"celdas con error: {errores}") if errores else ok("sin errores"))

print("2. Archivos")
cif = json.loads((RAIZ / "cifras.json").read_text(encoding="utf-8"))["cifras"]
ok(f"cifras.json con {len(cif)} cifras")
for f in ["politica_optima_shiro.csv"] + [f"figuras/{n}" for n in (
        "R1_justificacion.png", "R2_cobertura.png", "R3_distribucion_politica.png", "R4_valores.png",
        "R5_mapa_politica.png", "R6_batalla.png", "R7_sensibilidad.png", "R8_mapa_politica_exigente.png")]:
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


RESIDUOS = [r"\{[^}]*\}", r"\bnan\b", r"\bTODO\b", r"Claude", r"Anthropic", r"CLAUDE\.md", r"\bhito\b", r"PLAN_"]
# Parámetros de diseño declarados (no son resultados) y cifras heredadas de entregas anteriores
PERMITIDOS = {"0,005", "0,02", "0,01", "0,002", "1,0", "1,5", "2,0", "1,25", "0,95", "0,99", "0,5", "0,9", "13,5", "39,7",
              "3.er", "2.º", "1.er", "26-2", "374", "10⁻⁶", "−0,02"}
textos_cifras = " ".join(str(v["texto"]) for v in cif.values())
numeros_cifras = set(re.findall(r"−?\d[\d.]*,\d+", textos_cifras))

print("3–4. Documento y presentación")
for nombre, extraer in (("Taller1_C3_Diseno_MDP_RESUELTO.docx", texto_docx), ("Taller1_C3_presentacion.pptx", texto_pptx)):
    t = extraer(RAIZ / nombre)
    for patron in RESIDUOS:
        for m in re.findall(patron, t):
            falla(f"{nombre}: residuo «{m}»")
    huérfanos = sorted({n for n in re.findall(r"−?\d[\d.]*,\d+", t) if n not in numeros_cifras and n not in PERMITIDOS
                        and n.lstrip("−") not in numeros_cifras})
    (falla(f"{nombre}: números que no salen de cifras.json: {huérfanos}") if huérfanos
     else ok(f"{nombre}: todos los decimales salen de cifras.json o son parámetros declarados"))
    if not (RAIZ / nombre).with_suffix(".pdf").exists():
        falla(f"falta el PDF de {nombre}")

print("5. Coherencia")
(ok("cordura: con tarifa plana aplazan 0 estados") if cif["cordura_corregida_1p0_nap"]["valor"] == 0
 else falla("con tarifa plana el MDP aplaza"))
filas = list(csv.DictReader(open(RAIZ / "politica_optima_shiro.csv", encoding="utf-8")))
n_ap = sum(f["Acción óptima (a)"] == "Aplazar" for f in filas)
(ok(f"CSV: {len(filas)} estados, {n_ap} aplazan (= cifras.json)") if (n_ap == cif["n_opt_Aplazar"]["valor"]
                                                                     and len(filas) == cif["n_estados"]["valor"])
 else falla("la política del CSV no coincide con cifras.json"))

print("\nRESULTADO:", "OK" if not fallos else f"{len(fallos)} fallo(s)")
sys.exit(1 if fallos else 0)
