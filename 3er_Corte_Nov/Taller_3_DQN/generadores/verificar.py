# -*- coding: utf-8 -*-
"""Verificación previa a la entrega del Taller 3 (C3). Debe terminar con código 0.

1. El cuaderno está ejecutado completo, sin errores, y sus anclas con los talleres 1 y 2 pasaron.
2. Existen cifras.json, dqn_pesos.json (red ejecutable: misma salida que en el cuaderno), resumen_agentes.csv y las
   figuras T0–T5.
3. El documento, las diapositivas del video y el guion no tienen residuos ({clave} sin resolver, nan, TODO, menciones
   internas).
4. Todo número decimal de esas piezas sale de los cifras.json (de este taller o de los talleres 1 y 2) o es un parámetro
   declarado.
5. Las afirmaciones centrales coinciden con cifras.json.
6. El material del video está completo: un PNG y un texto por diapositiva, y la duración estimada entre 8 y 10 minutos.
"""
import json
import re
import sys
from pathlib import Path

import nbformat
import numpy as np
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
nb = nbformat.read(RAIZ / "Taller3_C3_DQN_Shiro.ipynb", as_version=4)
codigo = [c for c in nb.cells if c.cell_type == "code"]
sin_ejecutar = [i for i, c in enumerate(codigo) if c.get("execution_count") is None]
errores = [i for i, c in enumerate(codigo) if any(o.get("output_type") == "error" for o in c.get("outputs", []))]
(falla(f"celdas sin ejecutar: {sin_ejecutar}") if sin_ejecutar else ok(f"{len(codigo)} celdas de código ejecutadas"))
(falla(f"celdas con error: {errores}") if errores else ok("sin errores"))
salida = "\n".join("".join(o.get("text", "")) for c in codigo for o in c.get("outputs", []) if o.get("output_type") == "stream")
(ok("anclas con el Taller 1 coinciden") if re.search(r"Anclas con el Taller 1: (\d+)/\1 coinciden", salida)
 else falla("no aparece la línea de anclas con el Taller 1"))
(ok("ancla con el Taller 2 coincide") if "Ancla con el Taller 2" in salida else falla("no aparece el ancla con el Taller 2"))

print("2. Archivos")
cif = json.loads((RAIZ / "cifras.json").read_text(encoding="utf-8"))["cifras"]
ok(f"cifras.json con {len(cif)} cifras")
figs = sorted(p.name for p in (RAIZ / "figuras").glob("T[0-5]_*.png"))
(ok(f"{len(figs)} figuras T0–T5") if len(figs) == 6 else falla(f"faltan figuras: {figs}"))
(ok("resumen_agentes.csv") if (RAIZ / "resumen_agentes.csv").exists() else falla("falta resumen_agentes.csv"))
pesos = json.loads((RAIZ / "dqn_pesos.json").read_text(encoding="utf-8"))
P_ = {k: np.array(v) for k, v in pesos["capas"].items()}
forma = (P_["W1"].shape, P_["W2"].shape, P_["W3"].shape)
(ok(f"dqn_pesos.json: red {forma[0][0]} → {forma[0][1]} → {forma[1][1]} → {forma[2][1]}, {len(pesos['rasgos'])} rasgos")
 if forma == ((9, 64), (64, 64), (64, 3)) and len(pesos["rasgos"]) == 9 else falla(f"forma inesperada de la red: {forma}"))
# La red exportada debe aplazar un pico a las 18:00 sin carga pendiente (lo que hace π* para la persona paciente)
h = 18; w = (np.log(1400) - pesos["mu_logw"]) / pesos["sd_logw"]
x = np.array([np.sin(2 * np.pi * h / 24), np.cos(2 * np.pi * h / 24), w, w, 0.0, 1.0, 0.0, 0.0, 1.0])
a1 = np.maximum(0, x @ P_["W1"] + P_["b1"]); a2 = np.maximum(0, a1 @ P_["W2"] + P_["b2"]); q = a2 @ P_["W3"] + P_["b3"]
(ok("la red exportada aplaza un pico a las 18:00 (como π*)") if q[1] > q[0] else falla(f"la red exportada no aplaza a las 18:00: {q}"))


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


RESIDUOS = [r"\{[^}]*\}", r"\bnan\b", r"\bNone\b", r"\bTODO\b", r"Claude", r"Anthropic", r"CLAUDE\.md", r"\bhito\b", r"PLAN_",
            r"\bt[12]:"]
# Parámetros de diseño declarados (no son resultados)
PERMITIDOS = {"0,005", "0,02", "0,95", "0,99", "0,05", "1,0", "1,5", "0,001", "0,6", "2,4", "3.er", "2.º", "1.er", "2.ª", "26-2", "374"}
numeros = set()
for ruta in (RAIZ / "cifras.json", RAIZ.parent / "Taller_1_RL_MDP" / "cifras.json", RAIZ.parent / "Taller_2_QLearning" / "cifras.json"):
    c_ = json.loads(ruta.read_text(encoding="utf-8"))["cifras"]
    numeros |= set(re.findall(r"−?\d[\d.]*,\d+", " ".join(str(v["texto"]) for v in c_.values())))

print("3–4. Documento, diapositivas del video y guion")
for nombre, extraer in (("Taller3_C3_DQN_RESUELTO.docx", texto_docx), ("Taller3_C3_video_diapositivas.pptx", texto_pptx),
                        ("Guion_Video_Taller3_C3.docx", texto_docx)):
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

print("5. Las afirmaciones centrales coinciden con cifras.json")
V = lambda k: cif[k]["valor"]
afirmaciones = [
    ("«la semilla mediana de la red no se distingue de π* en mayo»", V("boot_dqn_pi_sig") == "no"),
    ("«la red captura más ahorro de π* que Q-learning del Taller 2»", V("dqn_captura") > V("ql_captura")),
    ("«la red no supera a π*»", V("dqn_ahorro_max") <= V("vi_ahorro_te") + 1e-9),
    ("«Q-learning con recompensa centrada llega al 80 % antes que la red, y la red antes que el Taller 2»",
     V("qlc_dias80") is not None and V("dqn_dias80") is not None and V("qlc_dias80") < V("dqn_dias80") < V("ql_dias80")),
    ("«Double DQN no mejora en este problema»", V("ddqn_captura") <= V("dqn_captura")),
    ("«sin ninguno de los dos trucos la red captura menos y hay semillas que no ahorran nada»",
     V("sina_captura") < min(V("sinr_captura"), V("sint_captura"), V("dqn_captura")) and V("sina_ahorro_min") <= 1e-9),
    ("«sin memoria de experiencias el resultado depende de la semilla» (peor semilla bajo la del completo)",
     V("sinr_ahorro_min") < V("dqn_ahorro_min")),
    ("«sin red objetivo el valor Q oscila el doble»", 1.7 <= V("osc_sint") / V("osc_dqn") <= 2.3),
    ("«sin ninguno, la oscilación es más de cuatro veces la del completo»", V("osc_sina") / V("osc_dqn") > 4),
    ("«la persona exigente aplaza de forma continua desde una hora más tardía que la paciente»",
     V("e4_ex_desde") is not None and (V("e4_pac_desde") is None or V("e4_ex_desde") > V("e4_pac_desde"))),
    ("«la red con la persona exigente espera menos que su π*»", V("dqnx_espera") < V("vi_ex_espera_te")),
    ("«la red encontró sola el punto de equilibrio de la persona exigente» (primera hora entera tras el teórico)",
     V("e4_ex_desde") == int(np.ceil(V("e4_ex_hora_teorica")))),
    ("«la persona paciente aplaza en las 18 horas de punta y solo ejecuta en el valle»",
     V("e4_pac_punta_aplaza") == 18 and max(V("e4_pac_ejec_rango")) <= 5),
]
for texto, cumple in afirmaciones:
    (ok(texto) if cumple else falla(f"no se cumple {texto}"))

print("6. Material del video")
guion = json.loads((RAIZ / "video" / "guion.json").read_text(encoding="utf-8"))
n_diap = len(Presentation(RAIZ / "Taller3_C3_video_diapositivas.pptx").slides)
pngs = sorted((RAIZ / "video" / "diapositivas_png").glob("diapositiva_*.png"))
txts = sorted((RAIZ / "video" / "textos").glob("diapositiva_*.txt"))
(ok(f"{n_diap} diapositivas, {len(pngs)} PNG, {len(txts)} textos") if n_diap == len(pngs) == len(txts) == len(guion["diapositivas"])
 else falla(f"material incompleto: {n_diap} diapositivas, {len(pngs)} PNG, {len(txts)} textos, {len(guion['diapositivas'])} bloques"))
seg = guion["total_segundos"]
(ok(f"duración estimada {seg // 60} min {seg % 60} s") if 8 * 60 <= seg <= 10 * 60 else falla(f"duración estimada fuera de 8–10 min: {seg} s"))
narradores = {e["narrador"] for e in guion["diapositivas"]}
(ok(f"narradores: {sorted(narradores)}") if narradores == {"Jose", "Sofía", "Andrés", "Alex"} else falla(f"narradores: {narradores}"))

print("\nRESULTADO:", "OK" if not fallos else f"{len(fallos)} fallo(s)")
sys.exit(1 if fallos else 0)
