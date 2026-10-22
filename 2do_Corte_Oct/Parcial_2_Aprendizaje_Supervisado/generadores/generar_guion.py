# -*- coding: utf-8 -*-
"""Guion de la sustentación de Shiro Guardian (10 minutos, cuatro expositores).

Salida: ../Guion_Sustentacion_Shiro_Guardian.docx y ../Guion_Sustentacion_Shiro_Guardian.pdf
Estilo del guion del video del 2.º corte (Presentacion_Talleres_C2/Guion_Video_Talleres_C2.docx): carta, Calibri,
cabeceras 1F3864, tablas con encabezado azul y recuadro FDF2E3.

Las cifras salen de ../cifras.json (campo "texto") y de ../mockup/datos_mockup.json. El recorrido de la demo se
comprobó ejecutando la maqueta (Mockup_Shiro_Guardian.html) en Edge sin interfaz.

Cifras del deslizador (12 % y 5 %): las exporta el cuaderno (claves demo_r12_* y demo_r05_*) con la misma lógica que
la página (cortes de la calma de validación aplicados a la prueba).

Uso:  C:\\Users\\pipel\\venvs\\ml\\Scripts\\python.exe generar_guion.py [--sin-pdf]
"""
import datetime as dt
import re
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from comun_office import RAIZ, Cifras, buscar_residuos, datos_mockup, en_palabras, exportar_pdf, num_es

C = Cifras()
T, N = C.T, C.N
DM = datos_mockup()
SALIDA = RAIZ / "Guion_Sustentacion_Shiro_Guardian.docx"
AZUL, GRIS, NEGRO = "1F3864", "555555", "000000"

# Deslizador de rojo de la página a 12 % y a 5 % (claves demo_* del cuaderno)
R12 = {k: (N(k) if k in ("demo_r12_n20", "demo_r12_min_dia", "demo_r12_avisos_dia") else T(k))
       for k in ("demo_r12_n20", "demo_r12_p20", "demo_r12_avisos_dia", "demo_r12_min_dia", "demo_r12_falsos", "demo_r12_r")}
R05 = {k: (N(k) if k in ("demo_r05_n20", "demo_r05_min_dia", "demo_r05_avisos_dia") else T(k))
       for k in ("demo_r05_n20", "demo_r05_p20", "demo_r05_avisos_dia", "demo_r05_min_dia", "demo_r05_rojo_pct", "demo_r05_r")}

# ---------------------------------------------------------------------------------------------------------------
# Cifras (todas de cifras.json o datos_mockup.json)
picos = N("def_picos_prueba")
n20, p20 = N("titular_n20"), T("titular_p20")
min_dia, avisos_dia, falsos = T("titular_min_dia"), T("titular_avisos_dia"), T("titular_falsos")
m20, m20_pct = N("titular_m20"), T("titular_m20_pct")
azar = T("azar_p20_desplegado")
d_regla, ic_inf, ic_sup = N("titular_d_regla"), N("titular_d_regla_ic_inf"), N("titular_d_regla_ic_sup")
p20_ic_inf, p20_ic_sup = N("fig2_elegido_desp_p20_ic_inf"), T("fig2_elegido_desp_p20_ic_sup")
utiles = T("g0_desp_utiles")
rojo_pct, r_def = T("titular_rojo_pct"), T("def_tasa_base_r")
umbral = T("part_umbral_wh")
n_lect, dias = T("datos_n_lecturas"), T("datos_dias")
fit_fin, val_ini, val_fin = T("part_fit_fin"), T("part_val_inicio"), T("part_val_fin")
prueba_ini, prueba_fin = T("part_prueba_inicio"), T("part_prueba_fin")
val_n, val_picos, prueba_n = T("part_val_n"), T("def_picos_validacion"), T("part_prueba_n")
val_p20, prueba_p20 = T("g0_val_p20"), T("g0_prueba_p20")
p1_det, p1_dur, p1_calma, p1_mismo = (T("ancla_det_detectados"), T("ancla_det_duracion"),
                                      T("n1c_alerta_calma_pct"), T("n1c_det_mismo_r_p20"))
caso_d, caso_ic_inf, caso_ic_sup = N("caso_otro_d"), N("caso_otro_ic_inf"), N("caso_otro_ic_sup")
g1_min, g4_min, presup_min = T("g1_desp_min_dia"), T("g4_desp_min_dia"), T("fig3_presupuesto_min_dia")
sens05 = T("sens_05_elegido_p20")
c1_ini, c1_wh, c1_color = T("caso1_inicio"), T("caso1_energia_wh"), T("caso1_color")
c2_ini, c2_dur = T("caso2_inicio"), T("caso2_duracion_min")
no_fuga_n, no_fuga_dif, purga = T("vec_no_fuga_instantes"), T("vec_no_fuga_dif_max"), T("def_purga_lecturas")
ej_dia, ej_ini_rojo, ej_min = T("ejemplo_dia"), T("ejemplo_dia_inicio_rojo"), T("ejemplo_dia_min_desde_inicio_rojo")
ej_pico, ej_ant, ej_picos = T("ejemplo_dia_pico"), T("ejemplo_dia_antelacion_min"), N("ejemplo_dia_picos")
e_ant, e_tot, e_pct = T("energia_exceso_anticipado_kwh"), T("energia_exceso_kwh"), T("energia_exceso_anticipado_pct")
sim_m_kwh, sim_m_ev, sim_m_ac = T("sim_medio_kwh"), T("sim_medio_evitable_pct"), T("sim_medio_aceptadas_pct")
cal_val, cal_prueba = T("cal_decil10_tasa_mdp"), T("cal_decil10_tasa_prueba")
nvars = N("sel_nvars")
presup_pct = T("g0_prueba_rojo_pct")          # 7,66 % de la calma: rojo del presupuesto (101 min/día)

# Momentos de la tarjeta 1 (datos_mockup.json) y sus textos tal como los muestra la página
MOM = DM["momentos_tarjeta1"]
m_rojo = next(m for m in MOM if m["rotulo"].startswith("primer rojo del aviso útil"))
m_verde = next(m for m in MOM if m["color_esperado"] == "verde")
boton = lambda m: f"{m['fecha_es']} · {m['rotulo_llano']}"
sit = next((s for s in DM["situaciones_tarjeta4"] if s["fecha"] == m_rojo["fecha"]), None)
hasta_pico = f"{sit['min_hasta_pico']} min" if sit else None
redondeo_pagina = lambda x: num_es(x, 1 if abs(x) < 10 else 0)        # misma regla que la página (n1)
G3C = DM["g3c"]
franja_m = next(k for k, (a, b) in G3C["franjas"].items() if k != "nota" and a <= m_rojo["entradas"]["hora"] < b)
pron_rojo = num_es(max(0, m_rojo["pronostico_g3c"]), 0)
pron_err = num_es(G3C["mae_por_franja"][franja_m], 0)
DA = DM["dia_antes_despues"]
kwh = lambda wh: num_es(wh / 1000, 2)
pf = DA["pico_frase"]
mayor = max(DA["picos"], key=lambda q: q["energia_wh"])
sin_aviso = [q for q in DA["picos"] if not q["antelacion_min"]]
con20 = [q for q in DA["picos"] if q["antelacion_min"] >= 20]
con10 = [q for q in DA["picos"] if 0 < q["antelacion_min"] < 20]
hh = lambda s: s[11:16]
dia_tipo = "fin de semana" if m_rojo["entradas"]["es_fin_semana"] else "día laborable"
CAL = DM["calibracion"]
rango_rojo = CAL["mostrar_rango"][m_rojo["decil_calibracion"]] or [CAL["tasa_mdp"][m_rojo["decil_calibracion"]]] * 2

# ---------------------------------------------------------------------------------------------------------------
doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.59), Cm(27.94)
sec.left_margin = sec.right_margin = Cm(2.2)
sec.top_margin = sec.bottom_margin = Cm(2.0)
st = doc.styles["Normal"]
st.font.name, st.font.size = "Calibri", Pt(9.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
ANCHO = 21.59 - 4.4


def color(r, h):
    r.font.color.rgb = RGBColor.from_string(h)


def runs(p, texto, size=9.5, col=NEGRO, bold=False):
    """**negrita** dentro del texto; «comillas» se dejan tal cual."""
    for parte in re.split(r"(\*\*.+?\*\*)", texto):
        if not parte:
            continue
        parte = parte.replace(" %", chr(160) + "%")          # espacio duro: el % no queda solo en otra línea
        r = p.add_run(parte[2:-2] if parte.startswith("**") else parte)
        r.bold = True if parte.startswith("**") else bold
        r.font.size = Pt(size)
        r.font.name = "Calibri"
        color(r, col)
    return p


def parrafo(texto, size=9.5, col=NEGRO, bold=False, after=5, align=None, estilo=None):
    p = doc.add_paragraph(style=estilo) if estilo else doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after)
    if align is not None:
        p.alignment = align
    return runs(p, texto, size, col, bold)


def titulo(texto, size=14, after=7, before=10):
    p = parrafo(texto, size, AZUL, True, after)
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.keep_with_next = True
    return p


def sombrear(celda, hexcol):
    tcPr = celda._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hexcol)
    tcPr.append(shd)


def bordes_tabla(tabla, col="BFBFBF"):
    tblPr = tabla._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{lado}")
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), "4")
        e.set(qn("w:color"), col)
        b.append(e)
    tblPr.append(b)


def tabla(encab, filas, anchos, size=9.5):
    t = doc.add_table(rows=1 + len(filas), cols=len(encab))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    bordes_tabla(t)
    for i, fila in enumerate([encab] + filas):
        tr = t.rows[i]._tr
        trPr = tr.get_or_add_trPr()
        cant = OxmlElement("w:cantSplit")
        trPr.append(cant)
        if i == 0:
            th = OxmlElement("w:tblHeader")
            trPr.append(th)
        for j, val in enumerate(fila):
            cel = t.cell(i, j)
            cel.width = Cm(anchos[j])
            p = cel.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            if i == 0:
                sombrear(cel, AZUL)
                runs(p, val, size, "FFFFFF", True)
            else:
                partes = val if isinstance(val, list) else [val]
                for k, parte in enumerate(partes):
                    pp = p if k == 0 else cel.add_paragraph()
                    pp.paragraph_format.space_after = Pt(2)
                    runs(pp, parte, size, NEGRO, j == 0 and len(encab) > 2 and False)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def recuadro(texto, fondo="FDF2E3"):
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    cel = t.cell(0, 0)
    cel.width = Cm(ANCHO)
    sombrear(cel, fondo)
    partes = texto if isinstance(texto, list) else [texto]
    for k, parte in enumerate(partes):
        p = cel.paragraphs[0] if k == 0 else cel.add_paragraph()
        p.paragraph_format.space_after = Pt(3)
        runs(p, parte, 9.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def viñetas(items):
    for it in items:
        parrafo(it, after=3, estilo="List Bullet")


HABLADO = []          # texto que se dice en voz alta (para contar palabras)


def bloque(enc, filas, anchos=(4.3, ANCHO - 4.3)):
    titulo(enc, 11.5, 4, 8)
    for f in filas:
        HABLADO.append(f[-1] if isinstance(f[-1], str) else " ".join(f[-1]))
    tabla(["Qué se muestra", "Qué decir"], filas, anchos)


# ---------------------------------------------------------------------------------------------------------------
# Contenido hablado por bloque
B1 = [
    ("Póster · título y autores",
     "Buenos días; somos Jose, Sofía, Andrés y Alex, del grupo Shiro. Shiro es el asistente personal en el que "
     "trabajamos; en esta materia construimos su módulo de energía, y **Shiro Guardian** cuida el consumo de la casa. "
     "Nuestra pregunta: ¿cuánto antes se puede avisar de un pico de consumo?"),
    ("Póster · «Problema y contexto» (el día con el semáforo)",
     f"Un pico es pasar de {umbral} en una lectura de diez minutos. Hoy el hogar se entera cuando ya empezó: tarde. "
     "Guardian tiene que avisar **antes**, con margen para aplazar una carga, y de ese aviso depende qué "
     "probabilidad entra al estado del agente del tercer corte."),
    ("Póster · resultado en una frase",
     f"La respuesta corta: en el mes que el modelo nunca vio, Guardian avisó **{n20} de {picos} picos** con al menos "
     f"dos lecturas de antelación, con el semáforo en rojo {min_dia}. Y el {falsos} de sus avisos no tuvo pico "
     "detrás. **Sofía cuenta cómo llegamos a ese modelo.**"),
]
B2 = [
    ("Póster · «Dataset y características»",
     f"Usamos Appliances Energy Prediction, de UCI: {n_lect} de una vivienda en Bélgica, una cada diez minutos, "
     f"durante {dias}, sin datos faltantes. Lo decimos de entrada: es una sola casa, de invierno y primavera, sin "
     "verano. Excluimos rv1 y rv2, dos variables aleatorias que el dataset trae como control."),
    ("Póster · «Modelos aplicados y evolución»",
     f"Partimos el tiempo en tres tramos. Con los datos hasta el {fit_fin.split(' ')[0]} se entrenan los modelos. "
     f"Del {val_ini.split(' ')[0]} al {val_fin.split(' ')[0]}, la validación, se elige el modelo y se fijan los "
     f"colores del semáforo. Y del {prueba_ini.split(' ')[0]} al {prueba_fin.split(' ')[0]} es el examen: un mes que "
     "el modelo nunca vio y que se usa una sola vez."),
    ("Póster · «Modelos aplicados y evolución» (sigue)",
     f"Probamos {en_palabras(C.V('sel_n_candidatos'))} candidatos supervisados: desde un **modelo mínimo de "
     f"{en_palabras(C.V('sel_nvars'))} variables** —el consumo actual y qué tan "
     f"seguido hubo picos a esa hora— hasta bosques aleatorios y regresiones logísticas de {N('part_n_variables')} "
     "variables, y el gemelo. "
     "La regla para elegir se aplica solo en validación: avisar más picos que la regla del medidor, al menos 1 de "
     "cada 4 con margen y 1 aviso útil de cada 3; entre los que pasan, el más simple que quede a menos de 10 puntos "
     "del mejor. Esos umbrales los fijamos después de ver cálculos preliminares del mes de prueba, y lo declaramos "
     "como limitación."),
    ("Póster · «Modelo final y resultados» (la cifra del parcial 1 con el presupuesto se dice de palabra: no está "
     "en el póster)",
     "Ganó el modelo mínimo. Lo comparamos con dos listones: la regla del medidor —avisar cuando el consumo ya es "
     "alto— y el azar. Y corregimos al parcial 1: su "
     f"{p1_det} contaba avisos que tocaban picos ya empezados; con el rojo del presupuesto, {presup_min}, anticipa "
     f"{p1_mismo}, casi lo mismo que nuestro modelo con ese rojo, {prueba_p20}. **Andrés lo muestra funcionando.**"),
]
B3 = [
    ("Póster · «Modelo final y resultados» (picos avisados frente a la regla)",
     f"Con los mismos {min_dia} en rojo, Guardian avisa {n20} de {picos}, el {p20}; la regla del medidor, {m20}; el azar, "
     f"{azar}. Frente al azar se distingue. Frente a la regla son {d_regla} puntos más, con un rango plausible de "
     f"{ic_inf} a {ic_sup}: con {picos} picos no es concluyente, y así lo decimos. Ahora, la maqueta."),
]
B4 = [
    ("Póster · «Errores y reflexiones éticas» (casos críticos)",
     f"Dos casos críticos. El pico sin aviso más costoso, el {c1_ini}, de {c1_wh}: veinte minutos antes el semáforo "
     f"estaba en ámbar, no en rojo. Y la falsa alarma más larga, el {c2_ini}: {c2_dur} en rojo sin pico. ¿Quién paga "
     "cada error? Un pico no avisado lo paga la factura, como hoy; una falsa alarma la paga la confianza. Por eso el "
     "titular decide cuánto rojo tolera y Shiro nunca actúa solo."),
    ("Póster: «Errores y reflexiones éticas» (solo los 2 riesgos); lo demás se dice de palabra",
     f"Límites: una sola vivienda; la deriva —con los cortes de abril, en mayo el rojo subió a {min_dia} frente a "
     f"{presup_min} previstos—; la validación fue optimista ({val_p20} frente a {prueba_p20} en el examen, con el "
     "mismo rojo del presupuesto); y la "
     "variable que falta es qué aparato se enciende. Privacidad: el consumo revela cuándo hay gente en casa; por eso "
     "todo se procesa en el hogar, bajo la Ley 1581 de 2012."),
    ("Diapositivas de implementación 2 y 3",
     "¿Cómo se implementaría? Shiro es nuestro producto. Guardian no es una aplicación aparte: entra por iot-bridge, "
     "calcula en un servicio local como el de Whisper y la propuesta pasa por ApprovalGate, el mismo permiso que Shiro "
     "ya pide antes de tocar un archivo. Solo necesita el medidor y la hora, y nada sale de la casa sin autorización."),
    ("Diapositivas 4 a 7",
     "El titular aprueba; cada mes se recalibra en la casa, porque medimos la deriva, y el equipo de Shiro audita. "
     "Cada hogar nuevo empieza en gris, sin notificaciones, hasta reunir datos suficientes; calculamos un mes, pero "
     "es una hipótesis del piloto. Capacitación: recorrido con esta "
     "maqueta, guía de una página y preguntas frecuentes. Y la ruta es Twin, Guardian y Home, sin fechas y con "
     "criterios de salida. **Jose cierra.**"),
]
B5 = [
    ("Póster · «Conclusión y futuro»",
     "¿Qué cambia en Shiro? La probabilidad calibrada —de cada 100 momentos así, cuántos precedieron un pico— entra "
     "al estado del agente; Guardian notifica con una propuesta que la persona aprueba; el gemelo sigue siendo la "
     "función de transición, pero no el semáforo; y se recalibra cada mes. Aprendimos que el criterio de validación "
     "pesa más que el algoritmo. Falta saber qué aparato se enciende y probar en otra casa. Gracias; quedamos atentos "
     "a sus preguntas."),
]

DEMO = [
    ("1", f"Botón «{boton(m_rojo)}» (ya viene cargado al abrir la página)",
     [f"Píldora **ROJO**. «De cada 100 momentos así, **entre {redondeo_pagina(min(rango_rojo))} y "
      f"{redondeo_pagina(max(rango_rojo))}** precedieron un pico» (validación {redondeo_pagina(rango_rojo[1])}; "
      f"mes nunca visto {redondeo_pagina(rango_rojo[0])}: la página muestra el rango porque la validación fue "
      "optimista con puntajes así).",
      "«Qué propone Shiro»: «no encender cargas grandes en los próximos 30 min» con Aprobar · Ajustar · Rechazar.",
      f"Pronóstico: «≈ {pron_rojo} Wh ± {pron_err} Wh»."],
     f"Es el {m_rojo['fecha_es']}, un {dia_tipo}. El consumo es {num_es(m_rojo['wh'], 0)} Wh: todavía no es pico, "
     "pero a esta hora los picos son frecuentes, y el semáforo pasa a rojo. Shiro propone; la persona decide"
     + (f". El pico llegó {hasta_pico} después." if hasta_pico else ".")),
    ("2", "Clic en «Ajustar»",
     ["Aparece «Plazo: 15 / 30 / 60 min» y la nota «Propuesta ajustada a 30 min. Registrado solo en esta maqueta "
      "(no se guarda); Shiro no ejecuta nada por su cuenta.»"],
     "Ajustar cambia el plazo. Ni aprobando Shiro enciende o apaga nada: solo registra la decisión."),
    ("3", f"Botón «{boton(m_verde)}»",
     [f"Píldora **VERDE**; «De cada 100 momentos así, {redondeo_pagina(m_verde['tasa_mdp'])} precedieron un pico»; "
      "«Nada. Shiro solo registra el momento.»"],
     f"Otro momento: {num_es(m_verde['wh'], 0)} Wh a las {hh(m_verde['fecha'])} de un "
     f"{'fin de semana' if m_verde['entradas']['es_fin_semana'] else 'día laborable'}. Verde: Shiro no molesta."),
    ("4", f"Volver a «{m_rojo['fecha_es']}…». En «Consumo actual (Wh)», triple clic para seleccionar el valor y "
          "escribir 60; repetir (triple clic y escribir) con 120 y con 250",
     ["60 → **VERDE** · 120 → **ROJO** con propuesta · 250 → **ROJO · EN CURSO**: «El consumo ya pasa de "
      f"{umbral}: el pico está en curso y lo dice el medidor, no el modelo.» Debajo de los momentos: «Valores "
      "editados a mano.»"],
     "A la misma hora, el color depende del consumo actual: con poco consumo, verde; con 120, rojo. Y por encima de "
     f"{umbral} ya no es un aviso: el pico está en curso, lo ve el medidor y Shiro no repite la notificación."),
    ("5", "Clic en «2 · El semáforo del mes nunca visto» (barra de arriba)",
     [f"Indicadores: «**{n20} de {picos}** picos avisados con al menos 20 min ({p20}…)», «{N('titular_avisos_dia')} "
      f"avisos al día», «{utiles} de los avisos precedieron un pico ({falsos} falsos)», «{N('titular_min_dia')} min al "
      f"día en rojo ({rojo_pct}…)».",
      f"Nota: «rango plausible de {p20_ic_inf} a {p20_ic_sup}; marcar al azar … avisaría el {azar}».",
      f"Tabla: Guardian {n20} ({p20}) · avisar cuando el consumo ya es alto {m20} ({m20_pct}) · azar {azar}."],
     f"Este es el mes completo que el modelo nunca vio, con el rojo que de verdad hubo, {min_dia}: {n20} de {picos} picos con al menos dos lecturas de "
     f"antelación, {avisos_dia}, y el {falsos} de los avisos sin pico detrás. Ese costo está a la vista."),
    ("6", f"Deslizador «Rojo en abril (validación)»: de {r_def} hasta cerca de 12 % y afinar con las flechas ← → "
          f"del teclado (pasos de 0,01) hasta que la etiqueta diga {R12['demo_r12_r']} (con otro valor las cifras "
          "cambian un poco). Después, «Restablecer rojo y ámbar por defecto»",
     [f"«**{R12['demo_r12_n20']} de {picos}** picos avisados con al menos 20 min ({R12['demo_r12_p20']})», "
      f"«{R12['demo_r12_avisos_dia']} avisos al día», «{R12['demo_r12_min_dia']} min al día en rojo», "
      f"{R12['demo_r12_falsos']} falsos; el rango plausible desaparece (solo existe con el valor por defecto).",
      f"Al restablecer, vuelve a «{n20} de {picos}»."],
     "Más rojo, más picos avisados y más avisos al día. Es el control que tendría el titular: él decide cuánta "
     "interrupción tolera."),
    ("7", f"Bajar a «Antes y después · día del ejemplo: {ej_dia}»",
     [f"«el semáforo estaba en rojo desde las **{ej_ini_rojo}**, **{ej_min} antes** del pico de las {ej_pico} "
      f"({kwh(pf['energia_wh'])} kWh); las cifras del mes cuentan como máximo {ej_ant}».",
      f"«De los {ej_picos} picos de ese día: {len(con20)} con al menos 20 min de aviso, {len(con10)} con solo 10 min, "
      f"{len(sin_aviso)} sin aviso (el de las {hh(mayor['inicio'])}, {kwh(mayor['energia_wh'])} kWh, el mayor del "
      "día)»."],
     f"Antes, el hogar se enteraba por la factura. Después: el {ej_dia}, el semáforo estaba en rojo desde las "
     f"{ej_ini_rojo}, {ej_min} antes del pico, y Shiro propuso no encender cargas grandes. Y no lo maquillamos: el "
     "pico más grande de ese día llegó sin aviso."),
    ("8", f"Clic en «Escenario medio ({sim_m_ev} · {sim_m_ac})»",
     [f"«Medido: … **{e_ant}** por encima de {umbral}, de {e_tot} de exceso en todo el mes ({e_pct})» y, en el "
      f"recuadro **SIMULADO**, «{sim_m_kwh} en el mes»."],
     f"Lo medido: {e_ant} de exceso estaban en picos avisados con margen; no es ahorro, es lo que estaba en juego. Si "
     f"se pudiera correr de hora un {sim_m_ev} y la persona aceptara el {sim_m_ac} de las propuestas, serían "
     f"{sim_m_kwh}: es una simulación con supuestos."),
    ("9", "Bajar al pie de la página",
     ["«**Verificación: OK** — compara con el cuaderno los cortes, las métricas de la tarjeta 2, el azar, la energía "
      "medida, los escenarios simulados, la frase del antes y después… y, en los 5 momentos reales, color, puntaje, "
      "calibración, regla del explicador y pronóstico.»"],
     "La página se verifica sola contra el cuaderno cada vez que se abre: si algo no coincide, lo dice. "
     "**Alex sigue con lo que puede salir mal y con la implementación.**"),
]

PREGUNTAS = [
    ("¿Por qué el modelo más simple y no Random Forest?",
     "Porque se eligió en validación con preferencia por lo simple: entre los que pasan el piso y quedan a menos de 10 "
     f"puntos del mejor, el más simple. En el examen, con el rojo del presupuesto ({presup_min}), el mejor complejo (la logística "
     f"entrenada para anticipar) avisó {caso_d} puntos más, con un rango de {caso_ic_inf} a {caso_ic_sup}: no se "
     f"distinguen. Y los bosques derivan: con los cortes de abril, en mayo estuvieron en rojo {g1_min} y {g4_min}, "
     f"frente a {min_dia} del modelo mínimo."),
    ("¿33 % es bueno?",
     f"Es {n20} de {picos} con al menos dos lecturas de antelación, con {min_dia} en rojo. El azar con ese mismo rojo da {azar} y la regla del "
     f"medidor {m20} de {picos}. Frente al azar, sí; frente a la regla, {d_regla} puntos más con un rango de {ic_inf} a "
     f"{ic_sup}: no es concluyente con {picos} picos. Por eso lo presentamos como «unos {T('titular_p20_fraccion')}», no más."),
    ("¿Por qué tantas falsas alarmas?",
     f"El {falsos} de los avisos no tuvo pico detrás: es el costo de avisar con margen sin saber qué aparato se va a "
     f"encender. Se controla con el deslizador: con menos rojo hay menos avisos, pero también menos picos avisados. "
     f"En el estudio de sensibilidad, si en el mes de prueba se marcara en rojo exactamente el 5 % de los momentos "
     f"tranquilos, Guardian avisaría el {sens05} de los picos con margen. Ojo si lo prueban en la página: el "
     f"deslizador fija el corte con abril, así que con {R05['demo_r05_r']} el rojo realizado del mes es "
     f"{R05['demo_r05_rojo_pct']} y la página muestra {R05['demo_r05_n20']} de {picos} ({R05['demo_r05_p20']}), con "
     f"{R05['demo_r05_min_dia']} min al día en rojo y {R05['demo_r05_avisos_dia']} avisos al día."),
    ("¿Qué diferencia hay entre validación y prueba?",
     f"La validación ({val_ini.split(' ')[0]} a {val_fin.split(' ')[0]}, {val_n}, {val_picos}) sirve para elegir el "
     f"modelo y fijar los colores. La prueba ({prueba_n}, {picos} picos) se usa una sola vez, al final, y no elige "
     f"nada. La validación resultó optimista: {val_p20} frente a {prueba_p20}, ambos con el rojo del presupuesto "
     f"({presup_min}, {presup_pct} de los momentos tranquilos); el titular, {p20}, se mide con el rojo realizado del "
     f"mes ({min_dia}, {rojo_pct}). Una limitación que declaramos: los umbrales del piso (25 % y 33 %) y el margen "
     "de 10 puntos los escogimos tras ver cálculos preliminares del mes de prueba; por eso solo deciden en "
     "validación."),
    ("¿Por qué no usan el 86,9 % del parcial 1?",
     f"Porque contaba avisos que tocaban picos ya empezados: alertas de {p1_dur} de media que dejaban el {p1_calma} de "
     f"los momentos tranquilos en alerta, y su umbral de 0,40 se eligió mirando el mes de prueba. A {presup_min}, el "
     f"rojo del presupuesto, ese detector anticipa {p1_mismo} con al menos dos lecturas y nuestro modelo mínimo "
     f"{prueba_p20} ({N('n1c_det_mismo_r_n20')} contra {N('g0_prueba_n20')} picos): casi lo mismo. Lo que cambia es qué se mide: avisar con margen, no tocar un pico ya empezado."),
    ("¿Cómo saben que no hay fuga de información?",
     "Partición solo temporal; cada variable se construye con datos hasta el instante t; lo comprobamos en "
     f"{no_fuga_n} instantes al azar (diferencia máxima {no_fuga_dif}). Los cortes del semáforo salen de la "
     f"validación y se aplican al examen sin mirarlo, con {purga} purgadas en las fronteras. Lo que sí declaramos: "
     "los umbrales del piso (25 % y 33 %) y el margen de 10 puntos los escogimos tras ver cálculos preliminares del "
     "mes de prueba; por eso solo deciden en validación y la prueba no elige nada. Es una limitación."),
    ("¿Funcionaría en otra casa?",
     "No lo sabemos, y lo decimos: es una vivienda belga de invierno y primavera. Por eso, en la implementación, cada "
     "hogar nuevo empieza en gris, sin notificaciones, hasta reunir datos suficientes de esa casa (un mes es una "
     f"hipótesis: aquí el modelo se ajustó con {T('part_fit_dias')} de datos), y antes del piloto en hogares reales hay que "
     "revalidar con otra vivienda (UCI n.º 235)."),
    ("¿Qué pasa con la privacidad?",
     f"El modelo solo necesita el medidor y la hora ({nvars} variables). Todo se procesa y se guarda en el equipo del "
     "hogar, también el último mes de lecturas que pide la recalibración; solo salen los indicadores agregados del "
     "tablero mensual y con autorización del titular, como exige la Ley 1581 de 2012."),
    ("¿Qué haría falta para producción?",
     "Revalidar con otra vivienda; conectar el medidor real (MQTTTransport hacia Home Assistant, con su ADR); "
     "automatizar la recalibración mensual; y medir en un piloto si la gente responde las propuestas."),
    ("¿Dónde está el aprendizaje supervisado si gana un modelo de dos variables?",
     "El modelo mínimo es supervisado: aprende de ejemplos etiquetados qué tan seguido hubo picos a cada hora, en "
     "laborable y en fin de semana, y con etiquetas se fijan sus cortes y su calibración. Además entrenamos bosques, "
     "logísticas y el gemelo con las mismas reglas: el hallazgo es que, para anticipar, más variables no ayudaron."),
]

# ---------------------------------------------------------------------------------------------------------------
# Documento
parrafo("APRENDIZAJE DE MÁQUINA · PARCIAL 2 · SUSTENTACIÓN", 9.5, GRIS, True, 2)
parrafo("Guion de la sustentación — Shiro Guardian", 19, AZUL, True, 2)
parrafo("Para presentar el póster, la maqueta y la propuesta de implementación entre cuatro personas", 11, GRIS,
        after=8)

hablado_previo = [x[-1] for x in B1 + B2 + B3 + B4 + B5] + [x[-1] for x in DEMO]
_cuenta = lambda filas: sum(len(re.sub(r"\*\*", "", f[-1]).split()) for f in filas)
POR_BLOQUE = {"Jose (apertura)": _cuenta(B1), "Sofía": _cuenta(B2), "Andrés (con demo)": _cuenta(B3) + _cuenta(DEMO),
              "Alex": _cuenta(B4), "Jose (cierre)": _cuenta(B5)}
palabras = sum(len(re.sub(r"\*\*", "", s).split()) for s in hablado_previo)
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre"]
hoy = dt.date.today()
tabla(["Campo", "Valor"], [
    ["Grupo", "Shiro — Jose Leonardo Diazgranados, Sofía Londoño, Andrés Felipe Céspedes Rondón, Alex Duran"],
    ["Duración objetivo", "10 minutos de exposición, más las preguntas del profesor"],
    ["Material en pantalla", "Poster_Shiro_Guardian.pdf · Mockup_Shiro_Guardian.html (sin internet) · "
                             "Implementacion_Shiro_Guardian.pdf (7 diapositivas; las notas del orador están en el "
                             ".pptx)"],
    ["Texto hablado", f"≈ {num_es(palabras, 0)} palabras en total"],
    ["Fecha", f"{hoy.day} de {MESES[hoy.month - 1]} de {hoy.year}"],
], [4.0, ANCHO - 4.0])

titulo("Plan de la sustentación")
tabla(["Bloque", "Quién habla", "Qué se muestra", "Tiempo"], [
    ["Apertura: la necesidad de Shiro y la pregunta", "Jose", "Póster: título y «Problema y contexto»", "1:00"],
    ["Datos y cómo se eligió el modelo", "Sofía", "Póster: «Dataset», «Modelos aplicados y evolución», "
                                                  "«Modelo final»", "2:00"],
    ["Resultados y demo de la maqueta", "Andrés", "Póster (30 s) y Mockup_Shiro_Guardian.html", "3:50"],
    ["Ética, limitaciones e implementación", "Alex", "Póster: «Errores y reflexiones éticas»; diapositivas 2–7",
     "2:30"],
    ["Cierre", "Jose", "Póster: «Conclusión y futuro»", "0:40"],
    ["Total", "", "", "10:00"],
], [5.2, 2.3, ANCHO - 5.2 - 2.3 - 1.5, 1.5])

p = parrafo("", after=6, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
runs(p, "**Cómo usar este guion.** Es la versión corta para hablar. La versión larga de la implementación está en las "
        "**notas del orador** de Implementacion_Shiro_Guardian.pptx (Vista → Notas). No hay que leer palabra por "
        "palabra: lo importante es la idea de cada fila y las cifras exactas, que salen del cuaderno. El reparto es "
        "una propuesta y se puede cambiar.")
recuadro(["**Si hay que recortar a unos 8 minutos.** En la demo, salten los pasos 2 (Ajustar) y 8 (escenario "
          "simulado); en la implementación, pasen sin detenerse por las diapositivas 3 y 4. Nunca se recortan el "
          "titular con su costo, la comparación con la regla del medidor ni el antes y después.",
          "**El bloque más cuidado es la demo:** la maqueta vale la mitad de la nota. Andrés la ensaya dos veces con "
          "cronómetro."])

recuadro([f"**Dos tiempos en rojo: no los mezclen.** El **presupuesto** es el rojo fijado en abril con la "
          f"validación: {presup_min}, el {presup_pct} de los momentos tranquilos. El **realizado** es el que de "
          f"verdad hubo en el mes de prueba con esos cortes: {min_dia}, el {rojo_pct}.",
          f"Con el **realizado** se miden el titular ({n20} de {picos}, {p20}), la regla del medidor ({m20} de "
          f"{picos}) y el azar ({azar}). Con el **presupuesto** se miden {val_p20} (validación) y {prueba_p20} "
          f"(prueba) del modelo mínimo, el {p1_mismo} del detector del parcial 1 y los +{caso_d} puntos de la logística sobre el modelo mínimo. "
          "Cada vez que digan «el mismo tiempo en rojo», digan cuál."], "E8F3E8")

titulo("Antes de la sustentación")
viñetas([
    "Una sola persona comparte la pantalla y tiene abiertos, en este orden, el póster (PDF), la maqueta (HTML) y las "
    "diapositivas de implementación (PDF). Así no hay cortes al cambiar de expositor.",
    "Abrir Mockup_Shiro_Guardian.html con doble clic (funciona sin internet y sin instalar nada) y comprobar que el pie "
    "dice «Verificación: OK». Si dice «DIFIERE», ir al plan B.",
    "Recargar la página justo antes de la demo: así arranca con el momento rojo cargado y el deslizador en su valor "
    "por defecto.",
    "Frase de pase: cada expositor termina nombrando al siguiente («…Andrés lo muestra funcionando»).",
    "No improvisen cifras: si hay duda, la cifra exacta está en este guion, en el póster y en la página.",
])

titulo("El guion")
bloque("Apertura — Jose · póster · 1:00 min", B1)
bloque("Datos y cómo se eligió el modelo — Sofía · póster · 2:00 min", B2)
bloque("Resultados y demo — Andrés · póster y maqueta · 3:50 min", B3)

titulo("Recorrido de la demo (≈ 3:20 min)", 11.5, 4, 6)
parrafo("Cada paso dice dónde hacer clic, qué debe verse en la página (entre comillas, el texto tal como aparece) y "
        "qué decir. Comprobado ejecutando la página: los colores, textos y cifras de esta tabla son los que muestra.",
        after=5, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
tabla(["#", "Clic", "Qué debe verse", "Qué decir"], [list(f) for f in DEMO], [0.7, 3.6, 6.6, ANCHO - 0.7 - 3.6 - 6.6],
      size=9)
recuadro(f"**Si el deslizador no queda exactamente en {R12['demo_r12_r']}**, las cifras cambian un poco: lo que importa es la "
         "dirección (más rojo, más picos avisados y más avisos al día). Para volver al valor por defecto use siempre "
         "el botón «Restablecer».", "F2F2F2")

bloque("Ética, limitaciones e implementación — Alex · póster y diapositivas · 2:30 min", B4)
bloque("Cierre — Jose · póster · 0:40 min", B5)

titulo("Preguntas que podría hacer el profesor")
for i, (q, a) in enumerate(PREGUNTAS, 1):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(5)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run(f"{i}.  ")
    r.bold, r.font.size = True, Pt(9.5)
    color(r, AZUL)
    runs(p, f"**{q}** ", 9.5)
    runs(p, a, 9.5)

titulo("Plan B si falla la demo")
viñetas([
    "Si la página no abre, se queda en blanco o el pie dice «DIFIERE»: no se depura en vivo. Se muestran las capturas "
    "de la maqueta (carpeta figuras y póster): MG1 (página completa), MG2 (tarjeta 1: el momento rojo con la "
    "propuesta) y MG3 (tarjeta 2: el mes nunca visto con el antes y después). Se narran los mismos pasos con las "
    "cifras de la tabla de arriba.",
    "Llevar la carpeta del parcial en una memoria USB. La página es un solo archivo HTML sin dependencias: si Edge "
    "falla, se abre con otro navegador.",
    "Si falla el proyector o la pantalla compartida, el guion se puede seguir con el póster impreso y las capturas: "
    "las cifras de esta tabla no dependen de la página.",
])

# ---------------------------------------------------------------------------------------------------------------
# Comprobaciones
texto_total = "\n".join(p.text for p in doc.paragraphs) + "\n" + "\n".join(
    c.text for t in doc.tables for row in t.rows for c in row.cells)
texto_total = texto_total.replace(chr(160), " ")
res = buscar_residuos(texto_total)
assert not res, f"Residuos prohibidos: {res}"
for frase in (f"{n20} de {picos}", p20, min_dia, falsos, azar, f"{m20} de {picos}", ic_inf, ic_sup):
    assert frase in texto_total, f"Falta la cifra del relato común: {frase}"

cp = doc.core_properties
cp.author = cp.last_modified_by = "Grupo Shiro — Diazgranados, Londoño, Céspedes Rondón, Duran"
cp.title = "Guion de la sustentación — Shiro Guardian"
cp.subject = "Aprendizaje de Máquina · Universidad Sergio Arboleda · Parcial 2, 2.º corte, 2026-2"
cp.comments = "Guion de la sustentación de Shiro Guardian (10 minutos, cuatro expositores)"
cp.keywords = "Shiro Guardian; sustentación"
cp.category = ""
doc.save(SALIDA)
print(f"DOCX: {SALIDA.name} · ≈ {palabras} palabras habladas · {len(C.usadas)} cifras de cifras.json")
print("Palabras por bloque: " + " · ".join(f"{k} {v}" for k, v in POR_BLOQUE.items()))
if "--sin-pdf" not in sys.argv:
    pdf = exportar_pdf(SALIDA, SALIDA.with_suffix(".pdf"))
    print(f"PDF: {pdf.name}")
