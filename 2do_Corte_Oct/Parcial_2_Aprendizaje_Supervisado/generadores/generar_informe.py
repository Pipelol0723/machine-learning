# -*- coding: utf-8 -*-
"""Genera el informe ejecutivo APA 7 (Parte 1) del Parcial 2: Shiro Guardian.

Salidas (en la raíz del parcial):
  Informe_Ejecutivo_Shiro_Guardian.docx
  Informe_Ejecutivo_Shiro_Guardian.pdf   (Word por COM desde PowerShell, con candado)

Toda cifra sale de cifras.json (campo "texto"). Solo se teclean parámetros de definición
(200 Wh, 10/20/30 min, 48 casillas, 10 puntos) y fechas del dataset.

Uso:  python generar_informe.py [--sin-pdf]
"""
import json
import os
import subprocess
import sys
import time
from datetime import date, datetime
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

RAIZ = Path(__file__).resolve().parent.parent
FIG = RAIZ / "figuras"
SALIDA_DOCX = RAIZ / "Informe_Ejecutivo_Shiro_Guardian.docx"
SALIDA_PDF = RAIZ / "Informe_Ejecutivo_Shiro_Guardian.pdf"
CANDADO = Path(r"C:\Users\pipel\AppData\Local\Temp\shiro_office.lock")

# --------------------------------------------------------------------------------------
# Cifras
# --------------------------------------------------------------------------------------
_CIF = json.loads((RAIZ / "cifras.json").read_text(encoding="utf-8"))
_TODAS = {**_CIF["heredadas"], **_CIF["nuevas"]}


def c(clave):
    """Texto es-CO de una cifra de cifras.json; falla si no existe."""
    if clave not in _TODAS:
        raise KeyError(f"Cifra ausente en cifras.json: {clave}")
    return str(_TODAS[clave]["texto"])


def n(clave):
    """Solo el número (sin unidad) del texto de una cifra: '28 picos' -> '28'."""
    return c(clave).split(" ")[0]


_PALABRAS = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez"]


def palabra(clave):
    """Entero pequeño de cifras.json dicho con letra: sel_n_candidatos (6) -> 'seis'."""
    v = int(_TODAS[clave]["valor"])
    return _PALABRAS[v] if 0 <= v < len(_PALABRAS) else str(v)


def pts(clave):
    """'8,3 puntos' -> '8,3'; '-1,2 puntos' -> '−1,2' (signo tipográfico)."""
    return n(clave).replace("-", "−")


# Comprobación del caso: el texto del informe está escrito para el caso B con G0 elegido.
assert c("caso_letra") == "B", "El texto está escrito para el caso B: revisar narrativa"
assert c("sel_elegido") == "G0", "El texto está escrito para el modelo mínimo (G0)"

# --------------------------------------------------------------------------------------
# Utilidades de formato APA
# --------------------------------------------------------------------------------------
NEGRO = RGBColor(0, 0, 0)
SANGRIA = Cm(1.27)


def _fuente(run_or_style, tam=11, negrita=None, cursiva=None):
    f = run_or_style.font
    f.name = "Calibri"
    f.size = Pt(tam)
    f.color.rgb = NEGRO
    if negrita is not None:
        f.bold = negrita
    if cursiva is not None:
        f.italic = cursiva
    rpr = run_or_style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(a), "Calibri")
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        if rfonts.get(qn(a)) is not None:
            del rfonts.attrib[qn(a)]


def _pf(p, alin=None, sangria=None, interlineado="doble", antes=0, despues=0, sigue=None):
    pf = p.paragraph_format
    if alin is not None:
        pf.alignment = alin
    if sangria is not None:
        pf.first_line_indent = sangria
    pf.line_spacing_rule = WD_LINE_SPACING.DOUBLE if interlineado == "doble" else WD_LINE_SPACING.SINGLE
    pf.space_before = Pt(antes)
    pf.space_after = Pt(despues)
    if sigue is not None:
        pf.keep_with_next = sigue
    return p


def configurar_estilos(doc):
    st = doc.styles["Normal"]
    _fuente(st, 11)
    pf = st.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.first_line_indent = SANGRIA
    pf.widow_control = True
    # Idioma español (Colombia) para corrector y guiones
    rpr = st.element.get_or_add_rPr()
    lang = OxmlElement("w:lang")
    lang.set(qn("w:val"), "es-CO")
    rpr.append(lang)

    formato = {
        "Heading 1": dict(alin=WD_ALIGN_PARAGRAPH.CENTER, cursiva=False),
        "Heading 2": dict(alin=WD_ALIGN_PARAGRAPH.LEFT, cursiva=False),
        "Heading 3": dict(alin=WD_ALIGN_PARAGRAPH.LEFT, cursiva=True),
    }
    for nombre, f in formato.items():
        s = doc.styles[nombre]
        _fuente(s, 11, negrita=True, cursiva=f["cursiva"])
        p = s.paragraph_format
        p.alignment = f["alin"]
        p.first_line_indent = Cm(0)
        p.left_indent = Cm(0)
        p.space_before = Pt(0)
        p.space_after = Pt(0)
        p.line_spacing_rule = WD_LINE_SPACING.DOUBLE
        p.keep_with_next = True
    for s in doc.styles:
        if s.name in ("Title", "Subtitle"):
            _fuente(s, 11)


def campo_pagina(parrafo):
    run = parrafo.add_run()
    _fuente(run, 11)
    for tipo, texto in (("begin", None), (None, " PAGE "), ("separate", None), (None, "1"), ("end", None)):
        if tipo:
            e = OxmlElement("w:fldChar")
            e.set(qn("w:fldCharType"), tipo)
            run._r.append(e)
        elif texto == " PAGE ":
            e = OxmlElement("w:instrText")
            e.set(qn("xml:space"), "preserve")
            e.text = texto
            run._r.append(e)
        else:
            e = OxmlElement("w:t")
            e.text = texto
            run._r.append(e)


import re as _re

_NBSP_RE = _re.compile(r"(\d) (%|Wh|kWh|min|picos|lecturas|días|avisos|puntos)")
_FECHA_RE = _re.compile(r"\b(\d{1,2})-([a-záéíóú]{3})-(\d{4})\b")


def tipografia(texto):
    """Espacio no separable entre cifra y unidad (evita «86,9 / %» partido), guion no separable en
    las fechas (evita «27-/may-2016») y menos tipográfico."""
    texto = _NBSP_RE.sub(lambda m: m.group(1) + chr(160) + m.group(2), texto)
    texto = _FECHA_RE.sub(lambda m: m.group(1) + "‑" + m.group(2) + "‑" + m.group(3), texto)
    return _re.sub(r"(?<![\w-])-(?=\d)", chr(8722), texto)


def parrafo(doc, partes, sangria=SANGRIA, alin=WD_ALIGN_PARAGRAPH.LEFT, interlineado="doble", sigue=None):
    """partes: str o lista de (texto, estilo) con estilo en {'', 'n', 'c', 'nc'}."""
    p = doc.add_paragraph()
    _pf(p, alin=alin, sangria=sangria, interlineado=interlineado, sigue=sigue)
    _aplicar_salto(p)
    if isinstance(partes, str):
        partes = [(partes, "")]
    for texto, est in partes:
        r = p.add_run(tipografia(texto))
        _fuente(r, 11, negrita="n" in est, cursiva="c" in est)
    return p


def titulo(doc, texto, nivel):
    h = doc.add_heading(level=nivel)
    _aplicar_salto(h)
    r = h.add_run(texto)
    _fuente(r, 11, negrita=True, cursiva=(nivel == 3))
    return h


_SALTO = {"pendiente": False}


def salto_pagina(doc):
    """El siguiente párrafo o título empieza página nueva (salto «antes», sin párrafo vacío que pueda quedar
    solo en una página en blanco)."""
    _SALTO["pendiente"] = True


def _aplicar_salto(p):
    if _SALTO["pendiente"]:
        p.paragraph_format.page_break_before = True
        _SALTO["pendiente"] = False


def que_cambia(doc, texto):
    """Cierre de sección: qué cambia en Shiro (encabezado APA de nivel 4, en línea)."""
    return parrafo(doc, [("Qué cambia en Shiro. ", "n"), (texto, "")])


CONT = {"fig": 0, "tab": 0}


def figura(doc, archivo, titulo_fig, nota, ancho_cm, alt=None):
    CONT["fig"] += 1
    p = parrafo(doc, [(f"Figura {CONT['fig']}", "n")], sangria=Cm(0), sigue=True)
    p = parrafo(doc, [(titulo_fig, "c")], sangria=Cm(0), sigue=True)
    p = doc.add_paragraph()
    _pf(p, alin=WD_ALIGN_PARAGRAPH.CENTER, sangria=Cm(0), interlineado="simple", sigue=True)
    forma = p.add_run().add_picture(str(FIG / archivo), width=Cm(ancho_cm))
    # Texto alternativo (accesibilidad): título de la figura más la descripción dada
    docpr = forma._inline.docPr
    docpr.set("title", f"Figura {CONT['fig']}")
    docpr.set("descr", f"{titulo_fig}. {alt}" if alt else titulo_fig)
    parrafo(doc, [("Nota. ", "c"), (nota, "")], sangria=Cm(0))
    return CONT["fig"]


def _bordes_tabla(tabla):
    tbl = tabla._tbl
    tblPr = tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for lado, val in (("top", "single"), ("left", "nil"), ("bottom", "single"), ("right", "nil"),
                      ("insideH", "nil"), ("insideV", "nil")):
        e = OxmlElement(f"w:{lado}")
        e.set(qn("w:val"), val)
        if val == "single":
            e.set(qn("w:sz"), "8")
            e.set(qn("w:space"), "0")
            e.set(qn("w:color"), "000000")
        b.append(e)
    tblPr.append(b)


def _borde_inferior_celda(celda):
    tcPr = celda._tc.get_or_add_tcPr()
    bs = OxmlElement("w:tcBorders")
    e = OxmlElement("w:bottom")
    e.set(qn("w:val"), "single")
    e.set(qn("w:sz"), "6")
    e.set(qn("w:space"), "0")
    e.set(qn("w:color"), "000000")
    bs.append(e)
    tcPr.append(bs)


def _no_partir_fila(fila):
    trPr = fila._tr.get_or_add_trPr()
    e = OxmlElement("w:cantSplit")
    trPr.append(e)


def _celda_texto(celda, contenido, negrita=False, tam=10):
    celda.text = ""
    p = celda.paragraphs[0]
    _pf(p, sangria=Cm(0), interlineado="simple", antes=1, despues=1)
    partes = contenido if isinstance(contenido, list) else [(contenido, "n" if negrita else "")]
    for texto, est in partes:
        r = p.add_run(tipografia(texto))
        _fuente(r, tam, negrita="n" in est, cursiva="c" in est)


def tabla(doc, titulo_tab, encabezado, filas, anchos_cm, nota, tam=10):
    CONT["tab"] += 1
    parrafo(doc, [(f"Tabla {CONT['tab']}", "n")], sangria=Cm(0), sigue=True)
    parrafo(doc, [(titulo_tab, "c")], sangria=Cm(0), sigue=True)
    t = doc.add_table(rows=1 + len(filas), cols=len(encabezado))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    _bordes_tabla(t)
    for j, h in enumerate(encabezado):
        _celda_texto(t.rows[0].cells[j], h, negrita=True, tam=tam)
        _borde_inferior_celda(t.rows[0].cells[j])
    # repetir encabezado si la tabla cruza de página
    trPr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader")
    trPr.append(th)
    for i, fila in enumerate(filas, start=1):
        for j, v in enumerate(fila):
            _celda_texto(t.rows[i].cells[j], v, tam=tam)
        _no_partir_fila(t.rows[i])
    for fila in t.rows:
        for j, w in enumerate(anchos_cm):
            fila.cells[j].width = Cm(w)
    # mantener el título con el encabezado y la primera fila (la tabla puede partirse después)
    for fila in t.rows[:min(2, len(t.rows) - 1)]:
        for celda in fila.cells:
            for p in celda.paragraphs:
                p.paragraph_format.keep_with_next = True
    parrafo(doc, [("Nota. ", "c"), (nota, "")], sangria=Cm(0))
    return CONT["tab"]


def referencia(doc, partes):
    p = doc.add_paragraph()
    _pf(p, sangria=Cm(-1.27))
    p.paragraph_format.left_indent = Cm(1.27)
    for texto, est in partes:
        r = p.add_run(texto)
        _fuente(r, 11, negrita="n" in est, cursiva="c" in est)
    return p


# --------------------------------------------------------------------------------------
# Textos que se repiten
# --------------------------------------------------------------------------------------
TITULO = ("¿Cuánto antes se puede avisar de un pico de consumo? "
          "Modelos supervisados para Shiro Guardian")
AUTORES = "Jose Leonardo Diazgranados, Sofía Londoño, Andrés Felipe Céspedes Rondón y Alex Duran"
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
         "octubre", "noviembre", "diciembre"]


def fecha_es(d):
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


# Fechas del mes de prueba y de los tramos (texto de cifras.json)
PRUEBA_INI = c("part_prueba_inicio").split(" ")[0]   # 30-abr-2016
PRUEBA_FIN = c("part_prueba_fin").split(" ")[0]      # 27-may-2016
FIT_FIN = c("part_fit_fin").split(" ")[0]            # 13-abr-2016
VAL_FIN = c("part_val_fin").split(" ")[0]            # 30-abr-2016

ESCENARIO = (
    f"Si Shiro Guardian hubiera funcionado en el mes que el modelo nunca vio ({PRUEBA_INI} a "
    f"{PRUEBA_FIN}), con el semáforo en rojo {n('titular_min_dia')} minutos al día, habría avisado "
    f"con al menos dos lecturas de antelación (entre 10 y 20 minutos o más) {n('titular_n20')} de "
    f"los {n('def_picos_prueba')} picos; con el mismo tiempo en rojo, avisar cuando el consumo ya "
    f"es alto habría avisado {n('titular_m20')}."
)


# --------------------------------------------------------------------------------------
# Documento
# --------------------------------------------------------------------------------------
def construir():
    doc = Document()
    configurar_estilos(doc)
    sec = doc.sections[0]
    sec.page_height = Cm(27.94)
    sec.page_width = Cm(21.59)
    for lado in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
        setattr(sec, lado, Cm(2.54))
    sec.header_distance = Cm(1.27)
    sec.footer_distance = Cm(1.27)
    cab = sec.header.paragraphs[0]
    _pf(cab, alin=WD_ALIGN_PARAGRAPH.RIGHT, sangria=Cm(0), interlineado="simple")
    campo_pagina(cab)
    cp = doc.core_properties
    ahora = datetime.now().replace(microsecond=0)
    cp.title = TITULO
    cp.author = AUTORES
    cp.last_modified_by = AUTORES
    cp.subject = "Informe ejecutivo del Parcial 2: Shiro Guardian"
    cp.keywords = "Shiro Guardian; anticipación de picos; aprendizaje supervisado; validación temporal"
    cp.comments = ""
    cp.category = ""
    cp.language = "es-CO"
    cp.created = ahora
    cp.modified = ahora
    cp.last_printed = ahora
    cp.revision = 1

    # ---------------- Portada de estudiante (APA 7) ----------------
    for _ in range(3):
        parrafo(doc, "", sangria=Cm(0))
    parrafo(doc, [(TITULO, "n")], sangria=Cm(0), alin=WD_ALIGN_PARAGRAPH.CENTER)
    parrafo(doc, "", sangria=Cm(0))
    for linea in (AUTORES,
                  "Universidad Sergio Arboleda",
                  "Aprendizaje de Máquina (2.º corte, 2026-2)",
                  "Hernán Darío Cruz Bueno",
                  fecha_es(date.today())):
        parrafo(doc, linea, sangria=Cm(0), alin=WD_ALIGN_PARAGRAPH.CENTER)
    salto_pagina(doc)

    # ---------------- Resumen ----------------
    titulo(doc, "Resumen", 1)
    parrafo(doc, (
        f"Shiro Guardian es la parte de Shiro que vigila el consumo eléctrico del hogar y debe avisar "
        f"antes de un pico (más de 200 Wh en una lectura de 10 min) para que la persona alcance a "
        f"aplazar una carga grande. Este informe mide cuánta anticipación se logra y cuántas falsas "
        f"alarmas cuesta, con los datos públicos de una vivienda (Candanedo et al., 2017) y un mes que "
        f"los modelos nunca vieron. Se compararon {palabra('sel_n_candidatos')} modelos supervisados, elegidos en un periodo de "
        f"validación y evaluados en el mes de prueba sin reentrenar; el piso de selección se fijó tras "
        f"ver cálculos preliminares de ese mes, así que solo decide dentro de la validación. Quedó el "
        f"modelo mínimo de dos variables (consumo actual y "
        f"frecuencia histórica de picos a esa hora): avisó {n('titular_n20')} de los "
        f"{n('def_picos_prueba')} picos del mes ({c('titular_p20')}) con al menos dos lecturas de "
        f"antelación, con el semáforo en rojo {c('titular_min_dia')}, {c('titular_avisos_dia')} y "
        f"{c('titular_falsos')} de avisos sin pico detrás. Avisar cuando el consumo ya es alto, con el "
        f"mismo tiempo en rojo, logra {n('titular_m20')} de {n('def_picos_prueba')}; la diferencia "
        f"({pts('titular_d_regla')} puntos; rango plausible de {pts('titular_d_regla_ic_inf')} a "
        f"{pts('titular_d_regla_ic_sup')}) no es concluyente con {n('def_picos_prueba')} picos: podría "
        f"deberse al azar del muestreo. Marcar al azar el mismo tiempo avisaría el "
        f"{c('azar_p20_desplegado')}, y ningún modelo complejo se distingue del mínimo. Decisión para "
        f"Shiro: Guardian usa el modelo mínimo, notifica con una propuesta que la persona aprueba, ajusta "
        f"o rechaza, entrega su probabilidad calibrada a la siguiente fase de Shiro (el agente que "
        f"aprende qué hacer) y recalibra sus cortes cada mes."
    ), sangria=Cm(0))
    parrafo(doc, [("Palabras clave: ", "c"),
                  ("gestión de la demanda en el hogar, aprendizaje supervisado, anticipación de picos, "
                   "semáforo de riesgo, validación temporal", "")])
    salto_pagina(doc)

    # ---------------- Cuerpo ----------------
    parrafo(doc, [(TITULO, "n")], sangria=Cm(0), alin=WD_ALIGN_PARAGRAPH.CENTER)

    # 1. Problema real del sector
    titulo(doc, "Problema real del sector", 1)
    parrafo(doc, (
        "Shiro es un proyecto de hogar inteligente por fases: un gemelo digital del consumo (Shiro "
        "Twin), una capa de vigilancia (Shiro Guardian) y un sistema que actúa en la casa (Shiro Home). "
        "Este trabajo construye Guardian, la capa que clasifica el riesgo de la próxima media hora y "
        "notifica. De su resultado dependen dos decisiones de arquitectura: qué probabilidad de pico "
        "entra al estado del agente de la siguiente fase (un proceso de decisión de Markov, MDP: el "
        "entorno donde el agente aprende qué hacer) y si Guardian notifica o solo colorea el tablero."
    ))
    parrafo(doc, (
        f"El problema es que el hogar no sabe que viene un pico. En la vivienda estudiada, el mes de "
        f"prueba tuvo {c('def_picos_prueba')} ({c('def_picos_por_dia_prueba')}) y "
        f"{c('energia_exceso_kwh')} por encima de los 200 Wh, de {c('energia_prueba_kwh')} en total. La "
        f"persona se entera por la factura o, con un medidor, cuando el pico ya empezó: tarde para "
        f"aplazar la lavadora o el horno. Un aviso solo sirve con margen; por eso se cuentan los picos "
        f"avisados con al menos dos lecturas de antelación (20 minutos o más en el reloj de las "
        f"lecturas, que se toman cada 10 min). La Figura 1 muestra un día del mes de prueba."
    ))
    que_cambia(doc, (
        "La pregunta de Guardian deja de ser «¿la lectura actual supera 200 Wh?», que el medidor ya "
        "responde, y pasa a ser «¿empieza un pico en la próxima media hora?», la señal que el agente "
        "necesita para aprender a aplazar."
    ))

    # 2. Modelo elegido y justificación
    titulo(doc, "Modelo elegido y justificación", 1)
    parrafo(doc, (
        f"Guardian necesitaba un modelo que diga, cada 10 min, qué tan probable es un pico en la "
        f"próxima media hora y que siga sirviendo en un mes que no conoce. Los datos (Candanedo, 2017; "
        f"Candanedo et al., 2017) "
        f"son {c('datos_n_lecturas')} cada 10 min de una vivienda belga durante {c('datos_dias')} de "
        f"invierno y primavera de 2016, con {c('datos_n_columnas')} columnas y {c('datos_faltantes')} "
        f"faltantes. Problemas declarados: una sola vivienda sin verano; dos columnas de ruido puestas "
        f"como control (se excluyen); consumo siempre en múltiplos de 10 Wh "
        f"({c('datos_appliances_multiplo10_pct')} de las lecturas); dos sensores «interiores» que miden "
        f"fuera, y {palabra('datos_dias_incompletos')} días incompletos (el primero y el último)."
    ))
    figura(doc, "INF_G1_dia_con_guardian.png",
           f"Un día del mes que el modelo nunca vio ({c('ejemplo_dia')}), sin y con Guardian",
           "Franjas rosadas: picos. La tira es el color del semáforo con los cortes de abril; el rojo "
           "rayado lo da el medidor y no es un aviso.", 15.0)
    parrafo(doc, (
        f"La validación es temporal, un examen con un mes que nunca se vio: los modelos aprenden hasta "
        f"el {FIT_FIN}; los días siguientes, hasta el {VAL_FIN} ({c('def_picos_validacion')}), sirven "
        f"para elegir y fijar los colores, y en el mes de prueba se evalúa sin reentrenar. Compitieron "
        f"{palabra('sel_n_candidatos')} candidatos supervisados hechos con scikit-learn (Pedregosa et al., 2011): el modelo mínimo de "
        f"dos variables; un bosque aleatorio (un comité de árboles que votan; Breiman, 2001) y una "
        f"regresión logística entrenados para reconocer el pico en curso; el gemelo digital, que parte "
        f"de lo gastado hace 10 min y lo corrige por hora, luz y clima, usado como puntaje, y otro "
        f"bosque y otra logística entrenados para anticipar. Los listones: avisar cuando el consumo ya "
        f"es alto (la regla de nivel, que el medidor da gratis) y el azar."
    ))
    parrafo(doc, (
        f"En validación se exigió un piso: más picos avisados que la regla, al menos uno de cada cuatro "
        f"picos y que uno de cada tres avisos preceda un pico. Lo pasaron {palabra('sel_n_pasan_piso')} de los "
        f"{palabra('sel_n_candidatos')}. Entre "
        f"ellos se prefirió el más simple a menos de 10 puntos del mejor, lo mínimo que justifica "
        f"{c('part_n_variables')} variables frente a {palabra('sel_nvars')}. Ese piso se fijó tras ver cálculos preliminares "
        f"de la prueba (ver Limitaciones). Quedó el "
        f"modelo mínimo, que mira el consumo actual y la frecuencia histórica "
        f"de picos a esa hora en día laborable o de fin de semana. Los bosques, además, se desajustan en "
        f"mayo: con los cortes de abril pintan de rojo el {c('g1_desp_rojo_pct')} y el "
        f"{c('g4_desp_rojo_pct')} de los momentos tranquilos, frente al {c('titular_rojo_pct')} del "
        f"mínimo. La Tabla 1 resume el camino."
    ))
    tabla(doc, "Decisiones que llevaron al modelo de Guardian",
          ["Entrega", "Qué se probó", "Qué se aprendió", "Decisión para Shiro"],
          [
              ["Taller 2", "Árbol de decisión y vecinos cercanos",
               "La hora a la que despierta el hogar ordena el consumo", "La hora entra al estado"],
              ["Taller 3", "Bosque aleatorio y máquinas de soporte vectorial",
               "El que mejor ajusta con lecturas mezcladas es el que más falla en un mes nuevo",
               "Decide la partición temporal"],
              ["Parcial 1", "Consumo de los últimos minutos (retardos)",
               "Los retardos rescatan el mes nuevo; el detector reconocía el pico en curso",
               "El gemelo es la regresión lineal con retardos"],
              ["Taller de boosting", "LightGBM, XGBoost y CatBoost",
               "No extrapola a un mes más cálido", "No reemplaza al gemelo"],
              ["Parcial 2", f"{palabra('sel_n_candidatos').capitalize()} candidatos para anticipar",
               "Con diferencias indistinguibles, conviene lo más simple",
               "Guardian usa el modelo mínimo"],
          ],
          [2.9, 4.3, 5.0, 4.3],
          "Cifras de cada modelo en el Apéndice A.")
    que_cambia(doc, (
        "El servicio de modelos cabe en el propio hogar: dos tablas de percentiles y una frecuencia "
        "por cada una de las 48 casillas de hora y tipo de día. El gemelo sigue siendo la regresión "
        "lineal con retardos y no decide el color."
    ))

    # 3. Resultados clave y visualizaciones
    titulo(doc, "Resultados clave y visualizaciones", 1)
    parrafo(doc, (
        "Antes de notificar, Guardian necesita saber cuánto avisa, cuánto molesta, por qué y qué está en juego."
    ))
    titulo(doc, "Escenario de uso", 2)
    parrafo(doc, ESCENARIO + (
        f" Ese tiempo en rojo es el realizado en mayo, el {c('titular_rojo_pct')} de los momentos "
        f"tranquilos; el azar, con ese mismo tiempo, avisaría el {c('azar_p20_desplegado')} (Figura 2). "
        f"La ventaja sobre la regla, {pts('titular_d_regla')} puntos, tiene un rango plausible de "
        f"{pts('titular_d_regla_ic_inf')} a {pts('titular_d_regla_ic_sup')} (remuestreo por días; Efron "
        f"y Tibshirani, 1993): con {n('def_picos_prueba')} picos no es concluyente. Con una sola lectura "
        f"de margen la regla avisa {n('titular_m10_n')} ({c('titular_m10_pct')}) y el modelo "
        f"{n('titular_n10')} ({c('titular_p10')}): lo que aporta está en el margen. Con el presupuesto de abril, igual para "
        f"todos los candidatos ({c('def_tasa_base_r')} de los momentos tranquilos), ningún modelo complejo se "
        f"distingue del mínimo (el mejor avisa {pts('caso_otro_d')} puntos más, rango {pts('caso_otro_ic_inf')} "
        f"a {pts('caso_otro_ic_sup')}; Apéndice A). El costo del modelo desplegado: "
        f"{c('titular_avisos_dia')} de {c('g0_desp_duracion')} y {c('titular_falsos')} sin pico detrás."
    ))
    titulo(doc, "Antes y después", 2)
    parrafo(doc, (
        f"Antes: el hogar se entera por la factura o cuando el pico ya empezó. Después: el "
        f"{c('ejemplo_dia')} el semáforo estaba en rojo desde las {c('ejemplo_dia_inicio_rojo')}, "
        f"{c('ejemplo_dia_min_desde_inicio_rojo')} antes del pico de las {c('ejemplo_dia_pico')} (el mes "
        f"cuenta como máximo {c('ejemplo_dia_antelacion_min')}), y Shiro propuso no encender cargas "
        f"grandes; la persona decide. De los {c('ejemplo_dia_picos')} del día, "
        f"{palabra('ejemplo_dia_n20')} llegó con al menos "
        f"dos lecturas de margen ({c('ejemplo_dia_pct')}), como en el mes (Figura 1). No se dibuja un "
        f"consumo «con Shiro»: no hay un modelo del efecto de la propuesta."
    ))

    figura(doc, "INF_G2_picos_avisados_sin_leyenda.png",
           "Picos avisados con margen en el mes nunca visto, frente a la regla de nivel y al azar",
           f"Barras oscuras: modelo mínimo de dos variables, desplegado. Barras claras: regla de nivel "
           f"(consumo actual). Línea discontinua: azar. Las tres señales con el mismo tiempo en rojo, el "
           f"realizado en mayo ({c('titular_rojo_pct')} de los momentos tranquilos); la comparación entre "
           f"candidatos del Apéndice A usa el presupuesto de abril ({c('def_tasa_base_r')}). Barras de "
           f"error: rango plausible del 95 %.", 14.0,
           alt=(f"Gráfico de barras. Con al menos dos lecturas de antelación, el modelo mínimo avisa "
                f"{c('titular_p20')} de los picos, la regla de nivel {c('titular_m20_pct')} y el azar "
                f"{c('azar_p20_desplegado')}.") if "titular_m20_pct" in _TODAS else None)

    titulo(doc, "Reglas y patrones convertidos en acción", 2)
    parrafo(doc, (
        f"Un árbol de decisión de tres niveles imita al semáforo y lo traduce en reglas (Figura 3): "
        f"coincide con él en el {c('expl_fidelidad')} de los momentos tranquilos del mes de prueba (uno "
        f"que nunca dijera rojo coincidiría en el {c('expl_base_nunca_rojo')}) y reproduce el "
        f"{c('expl_cobertura')} de sus rojos. Hay rojo cuando a esa hora suele haber picos (laborables "
        f"{c('fig4_horas_laborables')}; fines de semana {c('fig4_horas_fin_semana')}) y el consumo ya "
        f"está por encima de lo habitual. La regla describe lo que mira el modelo, no la causa del pico. "
        f"La Tabla 2 lleva cada color a una acción."
    ))
    tabla(doc, "Del color del semáforo a la acción",
          ["Color", "Cuándo aparece", "Qué hace Shiro", "Qué hace la persona"],
          [
              [[("Verde", "n")], "Momento tranquilo, puntaje bajo el corte amarillo",
               "Registra; no muestra nada", "Nada"],
              [[("Amarillo", "n")], "Momento tranquilo, puntaje entre los dos cortes",
               "Pinta ámbar con la regla que lo explica; no notifica", "Puede mirar"],
              [[("Rojo anticipado", "n")],
               "Hora con picos frecuentes y consumo por encima de lo habitual",
               "Notifica y propone no encender cargas grandes en los próximos 30 min",
               "Aprueba, ajusta o rechaza; la propuesta vence a los 30 min"],
              [[("Rojo en curso", "n")], "La lectura supera 200 Wh o el pico ya empezó",
               "Lo marca el medidor; no repite la notificación", "Ve el pico, como hoy"],
              [[("Gris", "n")], "Más de 30 días sin recalibrar los cortes",
               "Muestra «baja confianza» y no propone", "Sabe que el aviso no es fiable"],
          ],
          [2.7, 4.6, 4.8, 4.4],
          "Donde la regla y el modelo no coinciden, manda el modelo.")

    figura(doc, "INF_G4_regla_explica_rojo.png",
           "Las dos reglas que explican el rojo de Guardian y la acción que proponen",
           "«Frecuencia histórica»: proporción de veces que a esa hora empezó un pico en la media hora "
           "siguiente. Las demás hojas del árbol dan «no rojo».", 15.5)
    titulo(doc, "Semáforo y tablero", 2)
    parrafo(doc, (
        f"En el mes de prueba el semáforo estuvo en verde {c('fig3_min_dia_verde')}, en amarillo "
        f"{c('fig3_min_dia_amarillo')} y en rojo anticipado {c('fig3_min_dia_rojo')}; los "
        f"{c('fig3_min_dia_en_curso')} restantes fueron rojo en curso, que marca el medidor (Figura 4). "
        f"Los tres primeros colores se reparten los momentos tranquilos. De cada 100 "
        f"momentos en rojo, {n('g0_desp_acierto_rojo')} precedieron un pico; en amarillo, "
        f"{n('g0_desp_acierto_amarillo')}, y en verde, {n('g0_desp_acierto_verde')}, con una tasa base "
        f"de {c('def_tasa_base_prueba')}: el color ordena el riesgo, aunque el rojo falla más de lo que "
        f"acierta. El rojo se fijó en abril para ocupar el {c('def_tasa_base_r')} de los momentos "
        f"tranquilos y en mayo ocupó el {c('titular_rojo_pct')}: es deriva, y por eso el tablero de la "
        f"Tabla 3 se revisa cada mes. La Figura 5 muestra cómo lo ve la persona en la maqueta."
    ))
    figura(doc, "INF_G3_tiempo_y_acierto_por_color.png",
           "Cuánto tiempo pasa el semáforo en cada color y cuánto acierta cada uno",
           "Acierto: lecturas de cada color que precedieron un pico en los 30 min siguientes; línea "
           "punteada: tasa base del mes.", 13.2)
    tabla(doc, "Tablero mensual de Guardian",
          ["Indicador", "Mes de prueba", "Qué revisar si cambia"],
          [
              ["Picos avisados con al menos dos lecturas de margen",
               f"{n('titular_n20')} de {n('def_picos_prueba')} ({c('titular_p20')}; rango "
               f"{n('fig2_elegido_desp_p20_ic_inf')}–{c('fig2_elegido_desp_p20_ic_sup')})",
               "Si baja, recalibrar o revisar el modelo"],
              ["Avisos al día", f"{n('titular_avisos_dia')}, de {c('g0_desp_duracion')}",
               "Si sube, el hogar dejará de atender"],
              ["Avisos que precedieron un pico", f"{c('g0_desp_utiles')} ({c('titular_falsos')} sin pico)",
               "Si baja, ajustar el presupuesto de rojo"],
              ["Minutos al día en rojo",
               f"{n('titular_min_dia')} (presupuesto: {n('fig3_presupuesto_min_dia')})",
               "Si se aparta, hay deriva: recalibrar"],
              ["Más uno: nivel que solo supera el 10 % de las lecturas (percentil 90)",
               f"{c('her_deriva_may_p90')} en mayo (enero: {c('her_deriva_ene_p90')})",
               "Si se aleja de 200 Wh, la definición de pico envejece"],
          ],
          [5.6, 5.4, 5.5],
          "Cada indicador se compara con el del mes anterior; el último vigila la definición de pico.")
    figura(doc, "INF_MG2_tarjeta1.png",
           "Tarjeta «¿Y si…?» de la maqueta funcional de Guardian",
           f"Momento real del {PRUEBA_INI} a las 09:10. La frecuencia se muestra como rango porque la "
           f"validación resultó optimista. Recorte: se omite el pronóstico de consumo.", 14.0)

    titulo(doc, "Impacto: medido y simulado", 2)
    parrafo(doc, (
        f"El indicador que Guardian toca es la energía por encima de 200 Wh, la que se podría correr de "
        f"hora. Medido: los {n('titular_n20')} picos avisados con margen tuvieron "
        f"{c('energia_exceso_anticipado_kwh')} por encima de 200 Wh, el "
        f"{c('energia_exceso_anticipado_pct')} de los {c('energia_exceso_kwh')} de exceso del mes. No es "
        f"ahorro: es la energía en juego. Cuánto se habría evitado depende de qué parte de la carga se "
        f"puede aplazar y de cuántas propuestas se aceptan, que aquí no se miden; la Tabla 4 los trata "
        f"como supuestos. Con tarifa plana aplazar no ahorra dinero; por eso no hay cifras en pesos."
    ))
    esc = []
    for nivel, rot in (("bajo", "Bajo"), ("medio", "Medio"), ("alto", "Alto")):
        esc.append([rot, c(f"sim_{nivel}_evitable_pct"), c(f"sim_{nivel}_aceptadas_pct"),
                    c(f"sim_{nivel}_kwh"), c(f"sim_{nivel}_pct_exceso")])
    tabla(doc, "Impacto SIMULADO en el mes de prueba",
          ["Escenario", "Parte aplazable (supuesto)", "Propuestas aceptadas (supuesto)",
           "kWh corridos de hora (SIMULADO)", "% del exceso del mes (SIMULADO)"],
          esc, [2.6, 3.4, 3.6, 3.4, 3.5],
          f"{c('sim_nota').replace('con al menos 20 min', 'con al menos dos lecturas de antelación (20 min o más)')} Cálculo: {c('energia_exceso_anticipado_kwh')} × parte aplazable × "
          f"propuestas aceptadas.")
    que_cambia(doc, (
        "Guardian notifica solo el rojo anticipado, siempre como propuesta aprobable; el tablero "
        "se revisa cada mes, y la recompensa del agente trata el ahorro como simulado hasta medir "
        "cuántas propuestas acepta un hogar real."
    ))

    # 4. Conclusiones
    titulo(doc, "Conclusiones y decisiones que permite tomar", 1)
    parrafo(doc, [("Para el hogar. ", "n"), (
        f"Tendrá aviso con margen en cerca de {c('titular_p20_fraccion')} picos, a cambio de unos "
        f"{n('titular_avisos_dia')} avisos al día, {c('titular_falsos_fraccion')} sin pico detrás. Con el control de rojo "
        f"decide: más rojo avisa más y molesta más.", "")])
    parrafo(doc, [("Para el equipo de Shiro. ", "n"), (
        "Desplegar el modelo mínimo, recalibrar cada mes, no prometer el " + c("ancla_det_detectados") +
        " del parcial 1 y revalidar con otra vivienda antes de llevarlo a otro hogar.", "")])
    parrafo(doc, [("Para el diseño de Shiro. ", "n"), (
        "La probabilidad calibrada (de cada 100 momentos parecidos, cuántos precedieron un pico), con "
        "su rango, entra al estado del agente; Guardian "
        "notifica por la pantalla de aprobación (ApprovalGate); el gemelo es la función de transición, "
        "no el semáforo, y la recompensa debe corregir que se queda corto en los picos.", "")])

    # 5. Limitaciones y ética
    titulo(doc, "Limitaciones y consideraciones éticas", 1)
    parrafo(doc, (
        f"Guardian le hablará a una persona en su casa: sus errores tienen quién los pague. Los datos "
        f"son de una vivienda belga sin verano y el mes de prueba tiene {c('def_picos_prueba')}, así que "
        f"los rangos son amplios. Los hábitos cambian con la estación: el nivel que solo supera el 10 % "
        f"de las lecturas bajó de {c('her_deriva_ene_p90')} en enero a {c('her_deriva_may_p90')} en "
        f"mayo. La validación fue optimista: con el presupuesto de abril ({c('def_tasa_base_r')} de los "
        f"momentos tranquilos), el modelo avisó con margen el {c('g0_val_p20')} de los picos de "
        f"validación y el {c('g0_prueba_p20')} de los de prueba. El piso de selección y el margen de "
        f"10 puntos se fijaron tras ver cálculos preliminares del mes de prueba; por eso solo deciden "
        f"dentro de la validación y no cuentan como confirmación independiente. El "
        f"gemelo se equivoca casi lo mismo que repetir la última lectura ({c('n1b_g3a_total_mae')} "
        f"frente a {c('n1b_persistencia_total_mae')} de error medio) y sobre 200 Wh se queda corto en "
        f"promedio {c('n1b_g3a_altas_sesgo').lstrip('-')}. Falta saber qué aparato se enciende."
    ))
    titulo(doc, "Corrección del parcial 1", 2)
    parrafo(doc, (
        f"El parcial 1 reportó {c('ancla_det_detectados')} de picos detectados, pero contaba avisos que "
        f"tocaban picos ya en curso: sus alertas duraban {c('ancla_det_duracion')}, cubrían el "
        f"{c('n1c_alerta_calma_pct')} de los momentos tranquilos y su umbral se eligió mirando el mes de "
        f"prueba. Se encendía antes del inicio en {n('n1c_antes_n')} de {n('def_picos_prueba')} picos, "
        f"pero en {n('n1c_antes_ya_encendida_n')} ya venía encendida. Con el mismo presupuesto de rojo "
        f"({c('def_tasa_base_r')} de los momentos tranquilos, {c('fig3_presupuesto_min_dia')}), el "
        f"detector del parcial 1 avisa con al menos dos lecturas de antelación el "
        f"{c('n1c_det_mismo_r_p20')} de los picos, frente al {c('g0_prueba_p20')} del modelo mínimo: "
        f"con la misma base, la ventaja de Guardian sobre el parcial 1 es pequeña. Lo que sí cambia es "
        f"que ahora se mide la antelación y no si la alerta toca el pico."
    ))
    titulo(doc, "Quién paga cada error", 2)
    parrafo(doc, (
        f"Dos casos críticos lo ilustran (Figura 6). El {c('caso1_inicio').split(' ')[0]}, 20 min antes "
        f"del pico, el consumo era de {c('caso1_consumo_wh')} y el semáforo estaba en "
        f"{c('caso1_color')}; vino un pico de {c('caso1_duracion_min')} con lecturas de hasta "
        f"{c('caso1_max_wh')} que nada anunciaba. El {c('caso2_inicio').split(' ')[0]} el semáforo "
        f"estuvo {c('caso2_duracion_min')} en rojo sin pico detrás. La Tabla 5 resume quién paga cada "
        f"error y su mitigación."
    ))
    figura(doc, "INF_G5_casos_criticos.png",
           "Dos casos críticos: el pico sin aviso con más energía y la falsa alarma más larga",
           "Consumo y color del semáforo; se omite el panel con el puntaje del modelo frente a sus cortes.", 13.2)
    tabla(doc, "Quién paga cada error de Guardian y cómo se mitiga",
          ["Error", "Quién lo paga", "Mitigación"],
          [
              [[("Pico no avisado", "n")],
               "El hogar, con energía y factura, como hoy; puede creer que estaba protegido",
               "No prometer más de lo medido; el medidor sigue marcando el rojo en curso"],
              [[("Falsa alarma", "n")],
               f"La persona, con atención y confianza ({c('titular_falsos')} de los avisos)",
               "Control de cuánto rojo tolera; la propuesta vence a los 30 min; se muestra cuánto "
               "acierta cada color"],
              [[("Deriva", "n")],
               "El hogar, sin saberlo: el semáforo molesta más o avisa menos",
               "Recalibración mensual; gris si pasan más de 30 días"],
              [[("Privacidad", "n")],
               "El titular y quienes conviven: el consumo revela cuándo hay gente en casa",
               "Proceso y datos en el equipo del hogar (tablas del modelo y último mes de lecturas); solo "
               "salen indicadores agregados, con autorización"],
              [[("Automatizar mal", "n")],
               "La persona, si se aplaza algo que necesitaba",
               "Shiro propone y la persona decide; nada se ejecuta sin aprobación"],
          ],
          [3.0, 6.3, 7.2],
          "Mes de prueba, modelo mínimo de dos variables.")
    parrafo(doc, (
        "El consumo cada 10 min revela rutinas: cuándo se despierta el hogar o cuándo no hay nadie. "
        "Es un dato personal, y la Ley 1581 de 2012 exige autorización previa e informada del "
        "titular (art. 9) y uso limitado a la finalidad informada (art. 4; Congreso de la República de "
        "Colombia, 2012). El modelo elegido solo necesita el medidor y la hora, y Shiro propone pero la "
        "persona decide: toda acción pasa por la pantalla de aprobación."
    ))
    que_cambia(doc, (
        "La privacidad y la aprobación humana son requisitos de diseño de Guardian, no opciones."
    ))

    # 6. Recomendaciones
    titulo(doc, "Recomendaciones finales", 1)
    recs = [
        ("Desplegar el modelo mínimo con propuesta aprobable, no con automatización: ",
         "avisa tanto como los complejos, se explica en una línea y deja la decisión en la persona."),
        ("Recalibrar los cortes cada mes y pasar a gris si no se hace: ",
         f"la deriva movió el rojo de {c('fig3_presupuesto_min_dia')} a {c('titular_min_dia')} en un solo mes."),
        ("Mostrar el costo junto al beneficio: ",
         "los picos avisados sin los avisos al día y los avisos sin pico detrás dan una imagen engañosa."),
        ("Medir qué aparato se enciende: ",
         "es la variable que faltó en los casos críticos y puede aportar más que cualquier algoritmo."),
        ("Revalidar con otra vivienda y empezar cada hogar con un mes en gris: ",
         "el modelo viene de una sola casa y su validación resultó optimista."),
    ]
    for i, (a, b) in enumerate(recs, start=1):
        parrafo(doc, [(f"{i}. ", ""), (a, "n"), (b, "")])
    que_cambia(doc, (
        "Con estas cinco acciones Guardian entra a la hoja de ruta de Shiro como un aviso honesto: su "
        "probabilidad alimenta al agente de la siguiente fase y la última palabra es de la persona."
    ))

    # ---------------- Referencias ----------------
    salto_pagina(doc)
    titulo(doc, "Referencias", 1)
    refs = [
        [("American Psychological Association. (2020). ", ""),
         ("Publication manual of the American Psychological Association", "c"),
         (" (7.ª ed.). https://doi.org/10.1037/0000165-000", "")],
        [("Breiman, L. (2001). Random forests. ", ""), ("Machine Learning, 45", "c"),
         ("(1), 5–32. https://doi.org/10.1023/A:1010933404324", "")],
        [("Candanedo, L. (2017). ", ""), ("Appliances energy prediction", "c"),
         (" [Conjunto de datos]. UCI Machine Learning Repository. https://doi.org/10.24432/C5VC8G", "")],
        [("Candanedo, L. M., Feldheim, V. y Deramaix, D. (2017). Data driven prediction models of "
          "energy use of appliances in a low-energy house. ", ""), ("Energy and Buildings, 140", "c"),
         (", 81–97. https://doi.org/10.1016/j.enbuild.2017.01.083", "")],
        [("Congreso de la República de Colombia. (2012, 17 de octubre). ", ""),
         ("Ley Estatutaria 1581 de 2012, por la cual se dictan disposiciones generales para la "
          "protección de datos personales", "c"),
         (". Diario Oficial n.º 48.587. "
          "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981", "")],
        [("Efron, B. y Tibshirani, R. J. (1993). ", ""), ("An introduction to the bootstrap", "c"),
         (". Chapman & Hall. https://doi.org/10.1007/978-1-4899-4541-9", "")],
        [("Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, "
          "M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., "
          "Brucher, M., Perrot, M. y Duchesnay, É. (2011). Scikit-learn: Machine learning in Python. ",
          ""), ("Journal of Machine Learning Research, 12", "c"),
         (", 2825–2830. https://jmlr.org/papers/v12/pedregosa11a.html", "")],
    ]
    for r in refs:
        referencia(doc, r)

    # ---------------- Apéndice A ----------------
    salto_pagina(doc)
    titulo(doc, "Apéndice A", 1)
    titulo(doc, "Ficha técnica", 1)
    parrafo(doc, (
        "Este apéndice reúne las métricas técnicas que el cuerpo traduce a lenguaje del hogar. El "
        "documento sigue el formato de trabajos de estudiante de la American Psychological Association "
        "(2020). Nombres internos de los candidatos: G0, modelo mínimo de dos variables; G1 y G2, "
        "bosque aleatorio y regresión logística entrenados para reconocer el pico en curso; G3b, "
        "gemelo de 36 variables usado como puntaje; G4 y G5, bosque y logística entrenados para "
        "anticipar. Todas las cifras son de la partición temporal salvo donde se indica el par."
    ))
    CONT["tab"] = 0

    def tabla_apendice(titulo_tab, enc, filas, anchos, nota):
        CONT["tab"] += 1
        parrafo(doc, [(f"Tabla A{CONT['tab']}", "n")], sangria=Cm(0), sigue=True)
        parrafo(doc, [(titulo_tab, "c")], sangria=Cm(0), sigue=True)
        t = doc.add_table(rows=1 + len(filas), cols=len(enc))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        _bordes_tabla(t)
        for j, h in enumerate(enc):
            _celda_texto(t.rows[0].cells[j], h, negrita=True, tam=9)
            _borde_inferior_celda(t.rows[0].cells[j])
        trPr = t.rows[0]._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:tblHeader"))
        for i, fila in enumerate(filas, start=1):
            for j, v in enumerate(fila):
                _celda_texto(t.rows[i].cells[j], v, tam=9)
            _no_partir_fila(t.rows[i])
        for fila in t.rows:
            for j, w in enumerate(anchos):
                fila.cells[j].width = Cm(w)
        # tablas cortas del apéndice: no partirlas entre páginas (todas las filas menos la última, con la siguiente)
        for fila in t.rows[:-1]:
            for celda in fila.cells:
                for p_ in celda.paragraphs:
                    p_.paragraph_format.keep_with_next = True
        parrafo(doc, [("Nota. ", "c"), (nota, "")], sangria=Cm(0))

    cand = [("G0", "Modelo mínimo de dos variables"), ("G1", "Bosque que reconoce"),
            ("G2", "Logística que reconoce"), ("G3b", "Gemelo como puntaje"),
            ("G4", "Bosque que anticipa"), ("G5", "Logística que anticipa")]
    filas = [["—", "Regla de nivel (listón)", c("regla_val_p20"), c("regla_prueba_p20"),
              c("regla_prueba_avisos_dia").split(" ")[0], "—"]]
    for k, nom in cand:
        filas.append([k, nom, c(f"{k.lower()}_val_p20"), c(f"{k.lower()}_prueba_p20"),
                      n(f"{k.lower()}_prueba_avisos_dia"),
                      "Sí" if c(f"piso_{k.lower()}_pasa") == "1" else "No"])
    tabla_apendice("Candidatos: picos avisados con al menos dos lecturas de margen",
                   ["Clave", "Candidato", "Validación", "Prueba", "Avisos/día (prueba)", "Pasa el piso"],
                   filas, [1.3, 4.6, 2.4, 2.2, 3.0, 2.3],
                   f"Mismo presupuesto de rojo para todos, el fijado en abril ({c('def_tasa_base_r')} de "
                   f"los momentos tranquilos). Azar con ese presupuesto: {c('azar_p20_teorico')}. "
                   f"{c('caso_frase').split('→')[0].strip()} El {c('titular_p20')} del cuerpo del "
                   f"informe es otra base: el modelo desplegado con el rojo realizado en mayo "
                   f"({c('titular_rojo_pct')}), frente al {c('titular_m20_pct')} de la regla y el "
                   f"{c('azar_p20_desplegado')} del azar con ese mismo rojo.")
    tabla_apendice(
        "Métricas por lectura del modelo elegido y del gemelo",
        ["Métrica", "Valor", "Línea base", "Cómo se lee"],
        [
            ["Exactitud del semáforo (rojo vs. no rojo)", c("lect_elegido_exactitud"),
             f"Todo verde: {c('lect_todo_verde_exactitud')}",
             "Como un vigilante que siempre dice «todo bien»: acierta casi siempre y nunca avisa. El "
             "semáforo cede exactitud a propósito para avisar con margen"],
            ["Precisión del rojo", c("lect_elegido_precision"), f"Tasa base: {c('def_tasa_base_prueba')}",
             "De cada 100 lecturas rojas, cuántas preceden un pico"],
            ["Sensibilidad", c("lect_elegido_sensibilidad"), "—",
             "De cada 100 lecturas previas a un pico, cuántas se pintan de rojo"],
            ["F1 por lectura", c("lect_elegido_f1"), "Todo verde: 0",
             "Como una nota que solo es alta si el rojo acierta y además cubre los picos: si una de "
             "las dos falla, baja"],
            ["AUC", c("lect_elegido_auc"), f"Regla de nivel: {c('lect_regla_auc')}",
             f"Si se saca al azar un momento previo a un pico y otro tranquilo, el semáforo da más "
             f"alarma al primero {round(_TODAS['lect_elegido_auc']['valor'] * 100)} de cada 100 "
             f"veces (50 sería lanzar una moneda)"],
            ["Gemelo: error medio (MAE)", c("n1b_g3a_total_mae"),
             f"Repetir la última lectura: {c('n1b_persistencia_total_mae')}", "Pierde en el error típico"],
            ["Gemelo: error cuadrático (RMSE)", c("n1b_g3a_total_rmse"),
             f"Repetir la última lectura: {c('n1b_persistencia_total_rmse')}", "Gana en los errores grandes"],
            ["Gemelo: R²", c("ancla_g3a_r2"), "Predecir la media: 0",
             "Qué parte de las subidas y bajadas del consumo anticipa el gemelo; 0 es no mejorar a "
             "decir siempre el promedio"],
            ["Detector del parcial 1: F1 por lectura a 0,40", c("her_det040_f1"), "—",
             "Reconocía la lectura actual; no anticipaba"],
        ],
        [4.6, 2.0, 4.0, 5.9],
        "Mes de prueba, momentos tranquilos, cortes fijados en validación. El gemelo es la regresión "
        "lineal de 36 variables con retardos.")
    tabla_apendice(
        "Modelos heredados: partición aleatoria frente a temporal",
        ["Modelo", "R² aleatoria", "R² temporal", "F1 aleatoria (reconocer)", "F1 temporal (reconocer)"],
        [
            ["Regresión lineal", c("her_reg_lineal_aleatoria_r2"), c("her_reg_lineal_temporal_r2"), "—", "—"],
            ["Árbol de decisión", c("her_reg_arbol_aleatoria_r2"), c("her_reg_arbol_temporal_r2"),
             c("her_clf_arbol_aleatoria_f1"), c("her_clf_arbol_temporal_f1")],
            ["Vecinos cercanos (KNN)", c("her_reg_knn_aleatoria_r2"), c("her_reg_knn_temporal_r2"),
             c("her_clf_knn_aleatoria_f1"), c("her_clf_knn_temporal_f1")],
            ["Bosque aleatorio", c("her_reg_rf_aleatoria_r2"), c("her_reg_rf_temporal_r2"),
             c("her_clf_rf_aleatoria_f1"), c("her_clf_rf_temporal_f1")],
            ["SVM (rbf, C = 10)", "—", "—", c("her_clf_svm_aleatoria_f1"), c("her_clf_svm_temporal_f1")],
            ["LightGBM", c("her_bo_lgbm_aleatoria_r2"), c("her_bo_lgbm_temporal_r2"), "—", "—"],
            ["Lineal con retardos (gemelo)", "no aplica", c("her_bo_lineal_retardos_r2"), "—", "—"],
        ],
        [4.6, 2.6, 2.6, 3.3, 3.4],
        "Cifras de los talleres y del parcial 1, sin retardos salvo la última fila. En la partición "
        "aleatoria los retardos no se usan porque filtran la lectura vecina. Todas las decisiones de "
        "Shiro se toman con la partición temporal.")

    # ---------------- Apéndice B ----------------
    salto_pagina(doc)
    titulo(doc, "Apéndice B", 1)
    titulo(doc, "Glosario en lenguaje llano", 1)
    glosario = [
        ("Pico", "lectura de más de 200 Wh en 10 min; las lecturas altas separadas por menos de 30 min "
                 "forman un solo pico."),
        ("Momento tranquilo", "lectura fuera de cualquier pico; sobre ellos se cuenta el tiempo en rojo."),
        ("Aviso", "racha de lecturas en rojo; es útil si un pico empieza en los 30 min siguientes."),
        ("Al menos dos lecturas de antelación", "el primer rojo llegó 20 min o más antes del inicio "
                                                "del pico en el reloj de las lecturas."),
        ("Regla de nivel", "avisar cuando el consumo actual ya es alto, sin aprender de ejemplos."),
        ("Modelo mínimo", "modelo entrenado con dos variables: consumo actual y frecuencia histórica de "
                          "picos a esa hora en día laborable o de fin de semana."),
        ("Puntaje", "número que el modelo da a cada momento; cuanto más alto, más riesgo de que venga "
                    "un pico."),
        ("Corte", "valor del puntaje a partir del cual cambia el color del semáforo; se fija en "
                  "validación y se recalibra cada mes."),
        ("Presupuesto de rojo", f"parte de los momentos tranquilos que se permite pintar de rojo; se "
                                f"fijó en abril en {c('def_tasa_base_r')} (unos "
                                f"{n('fig3_presupuesto_min_dia')} minutos al día), y es la base con la "
                                f"que se comparan todos los candidatos."),
        ("Percentil", "posición de un valor entre todos los observados: el percentil 90 es el valor que "
                      "solo supera el 10 % de las lecturas."),
        ("Probabilidad calibrada", "el puntaje traducido a «de cada 100 momentos parecidos, cuántos "
                                   "precedieron un pico», medido en validación agrupando los puntajes "
                                   "en diez tramos (deciles)."),
        ("Bosque aleatorio", "comité de árboles de decisión que votan."),
        ("Gemelo digital", "pronóstico del consumo siguiente que parte de lo gastado hace 10 min y lo "
                           "corrige por hora, luz y clima."),
        ("Validación temporal", "examen con un periodo posterior que el modelo nunca vio."),
        ("Rango plausible", "intervalo del 95 % obtenido al remuestrear los días del mes."),
        ("Deriva", "cambio de los hábitos o del clima que hace que los cortes de un mes no sirvan "
                   "igual al siguiente."),
        ("MDP", "proceso de decisión de Markov: el entorno donde el agente de Shiro aprenderá qué hacer "
                "en la siguiente fase del proyecto."),
        ("ApprovalGate", "pantalla donde la persona aprueba, ajusta o rechaza cada propuesta de Shiro."),
    ]
    for termino, defin in glosario:
        parrafo(doc, [(f"{termino}: ", "n"), (defin, "")])

    doc.save(SALIDA_DOCX)
    return SALIDA_DOCX


# --------------------------------------------------------------------------------------
# PDF por Word (COM vía PowerShell) con candado exclusivo
# --------------------------------------------------------------------------------------
PS_WORD = r"""
$ErrorActionPreference = 'Stop'
$w = $null
try {
  $w = New-Object -ComObject Word.Application
  $w.Visible = $false
  $w.DisplayAlerts = 0
  $d = $w.Documents.Open('__DOCX__', $false, $true)
  $d.Fields.Update() | Out-Null
  $d.ExportAsFixedFormat('__PDF__', 17)
  $d.Close(0)
  Write-Output 'PDF_OK'
} catch {
  Write-Output ('PDF_ERROR ' + $_.Exception.Message)
  exit 1
} finally {
  if ($w -ne $null) { $w.Quit() | Out-Null; [System.Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null }
}
"""


def exportar_pdf(docx, pdf):
    inicio = time.time()
    while True:
        try:
            fd = os.open(str(CANDADO), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, f"generar_informe.py {os.getpid()}".encode())
            os.close(fd)
            break
        except FileExistsError:
            if time.time() - inicio > 20 * 60:
                raise TimeoutError("Candado de Office ocupado más de 20 min")
            time.sleep(15)
    # Se exporta a una ruta temporal fuera de OneDrive y luego se copia: así se comprueba que el
    # PDF entregado es el recién exportado (no uno anterior retenido por la sincronización).
    import shutil
    import tempfile
    tmp_pdf = Path(tempfile.gettempdir()) / f"informe_shiro_{os.getpid()}.pdf"
    try:
        if tmp_pdf.exists():
            tmp_pdf.unlink()
        script = PS_WORD.replace("__DOCX__", str(docx)).replace("__PDF__", str(tmp_pdf))
        r = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=600)
        print(r.stdout.strip())
        if r.returncode != 0 or "PDF_OK" not in r.stdout:
            print(r.stderr.strip())
            raise RuntimeError("Falló la exportación a PDF")
        if not tmp_pdf.exists() or tmp_pdf.stat().st_size == 0:
            raise RuntimeError("Word no escribió el PDF")
        # Metadatos del PDF (Word no los copia por defecto): título, autor, asunto e idioma
        import pymupdf as fitz
        tmp2 = tmp_pdf.with_name(tmp_pdf.stem + "_meta.pdf")
        with fitz.open(tmp_pdf) as d:
            meta = dict(d.metadata or {})
            meta.update(title=TITULO, author=AUTORES,
                        subject="Informe ejecutivo del Parcial 2: Shiro Guardian",
                        keywords="Shiro Guardian; anticipación de picos; aprendizaje supervisado",
                        creator="Microsoft Word", producer=meta.get("producer") or "")
            d.set_metadata(meta)
            try:
                d.set_language("es-CO")
            except Exception:
                pass
            d.save(tmp2, garbage=3, deflate=True)
        shutil.copyfile(tmp2, pdf)
        tmp2.unlink()
        tmp_pdf.unlink()
    finally:
        try:
            CANDADO.unlink()
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    ruta = construir()
    print("DOCX:", ruta)
    if "--sin-pdf" not in sys.argv:
        exportar_pdf(SALIDA_DOCX, SALIDA_PDF)
        print("PDF:", SALIDA_PDF)
