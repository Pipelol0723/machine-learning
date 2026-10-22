# -*- coding: utf-8 -*-
"""Parte 3 del parcial: propuesta de implementación de Shiro Guardian (7 diapositivas con notas del orador).

Salida: ../Implementacion_Shiro_Guardian.pptx y ../Implementacion_Shiro_Guardian.pdf
Estética de la consola del deck del 2.º corte (fondo #0D0F13, tarjetas #151920/#232833, Segoe UI y Consolas).
Toda cifra sale de ../cifras.json (campo "texto"). Los componentes de Shiro nombrados aquí son solo los que
aparecen en 02_Propuesta_Shiro_IoT.docx y 03_Plan_Unificado_Shiro_Twin_a_Home.docx.

Uso:  C:\\Users\\pipel\\venvs\\ml\\Scripts\\python.exe generar_presentacion.py [--sin-pdf]
"""
import re
import sys

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

from comun_office import RAIZ, Cifras, buscar_residuos, exportar_pdf

C = Cifras()
T, N = C.T, C.N

SALIDA = RAIZ / "Implementacion_Shiro_Guardian.pptx"
ESCUDO = RAIZ / "recursos" / "escudo_universidad_sergio_arboleda.png"
CAPTURA = RAIZ / "figuras" / "IMP_MG2_recorte.png"     # recorte de MG2: semáforo, porqué y propuesta

# Paleta de la consola (deck del 2.º corte)
BG, CARD, LINEA = "0D0F13", "151920", "232833"
TX, TX2, MUT, MUT2 = "E6E9EF", "C9D1DE", "9AA3B2", "6F7787"
VERDE_CLARO, VERDE, AMBAR, ROJO = "7BD992", "188038", "E8710A", "D93025"
F_TXT, F_TIT, F_MONO = "Segoe UI", "Segoe UI Semibold", "Consolas"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
TOTAL = 7


def rgb(h):
    return RGBColor.from_string(h)


def caja(sl, x, y, w, h, fill=CARD, line=LINEA, forma=MSO_SHAPE.RECTANGLE):
    s = sl.shapes.add_shape(forma, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = rgb(fill)
    if line:
        s.line.color.rgb = rgb(line)
        s.line.width = Pt(0.75)
    else:
        s.line.fill.background()
    s.shadow.inherit = False
    if forma == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = 0.06
    return s


def _runs(p, texto, size, color, font, bold):
    """Marcado mínimo: **negrita** y `código` (Consolas, verde claro)."""
    for parte in re.split(r"(\*\*.+?\*\*|`.+?`)", texto):
        if not parte:
            continue
        r = p.add_run()
        if parte.startswith("**"):
            r.text, b, f, c = parte[2:-2], True, font, TX
        elif parte.startswith("`"):
            r.text, b, f, c = parte[1:-1], False, F_MONO, VERDE_CLARO
        else:
            r.text, b, f, c = parte, bold, font, color
        r.font.name, r.font.size, r.font.bold = f, Pt(size), b
        r.font.color.rgb = rgb(c)


def texto(sl, x, y, w, h, contenido, size=13, color=MUT, font=F_TXT, bold=False, align=None,
          anchor=MSO_ANCHOR.TOP, esp=4, vineta=False):
    tb = sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0)
    tf.margin_top = tf.margin_bottom = Inches(0)
    tf.vertical_anchor = anchor
    parrafos = contenido if isinstance(contenido, list) else [contenido]
    for i, par in enumerate(parrafos):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        if align:
            p.alignment = align
        p.space_after = Pt(esp)
        _runs(p, ("•  " if vineta else "") + par, size, color, font, bold)
    return tb


def base(sl, n, kicker=None, titulo=None):
    sl.background.fill.solid()
    sl.background.fill.fore_color.rgb = rgb(BG)
    texto(sl, 0.75, 7.05, 8.0, 0.3, "Shiro Guardian · Parcial 2 · Parte 3 — implementación", 9, MUT2, F_MONO)
    texto(sl, 11.58, 7.05, 1.0, 0.3, f"{n:02d}", 9, MUT2, F_MONO, align=PP_ALIGN.RIGHT)
    if kicker:
        texto(sl, 0.75, 0.5, 11.5, 0.3, kicker, 10.5, VERDE_CLARO, F_MONO)
    if titulo:
        texto(sl, 0.75, 0.82, 11.8, 0.8, titulo, 26, TX, F_TIT)


def barra(sl, y, h, contenido, acento=VERDE, size=13):
    caja(sl, 0.75, y, 11.83, h)
    caja(sl, 0.75, y, 0.06, h, fill=acento, line=None)
    texto(sl, 1.03, y + 0.14, 11.35, h - 0.2, contenido, size, TX2, anchor=MSO_ANCHOR.MIDDLE)


def bordes(cel, color="2C323E", ancho=9525):
    """Bordes finos del color de la consola (la tabla por defecto de PowerPoint los pinta blancos)."""
    from pptx.oxml.ns import qn
    from lxml import etree
    tcPr = cel._tc.get_or_add_tcPr()
    for lado in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        for viejo in tcPr.findall(qn(lado)):
            tcPr.remove(viejo)
        ln = etree.SubElement(tcPr, qn(lado), w=str(ancho), cap="flat", cmpd="sng", algn="ctr")
        sf = etree.SubElement(ln, qn("a:solidFill"))
        etree.SubElement(sf, qn("a:srgbClr"), val=color)
        etree.SubElement(ln, qn("a:prstDash"), val="solid")
    # lnL.. deben ir antes del relleno en el esquema: se reordenan
    hijos = list(tcPr)
    lineas = [h for h in hijos if h.tag in {qn(x) for x in ("a:lnL", "a:lnR", "a:lnT", "a:lnB")}]
    for h in lineas:
        tcPr.remove(h)
    for k, h in enumerate(lineas):
        tcPr.insert(k, h)


def notas(sl, txt):
    sl.notes_slide.notes_text_frame.text = txt


# ---------------------------------------------------------------------------------------------------------------
# Cifras que usa el deck (todas de cifras.json)
picos = N("def_picos_prueba")                          # 84
n20, p20 = N("titular_n20"), T("titular_p20")         # 28 · 33,3 %
min_dia, avisos_dia, falsos = T("titular_min_dia"), T("titular_avisos_dia"), T("titular_falsos")
m20 = N("titular_m20")                                 # regla del medidor, mismo rojo
azar = T("azar_p20_desplegado")
d_regla, ic_inf, ic_sup = N("titular_d_regla"), N("titular_d_regla_ic_inf"), N("titular_d_regla_ic_sup")
utiles = T("g0_desp_utiles")
presup_min = T("fig3_presupuesto_min_dia")
rojo_pct, r_def = T("titular_rojo_pct"), T("def_tasa_base_r")
g1_min, g4_min = T("g1_desp_min_dia"), T("g4_desp_min_dia")
p90_ene, p90_may = T("her_deriva_ene_p90"), T("her_deriva_may_p90")
val_p20, prueba_p20 = T("g0_val_p20"), T("g0_prueba_p20")
presup_pct = T("g0_prueba_rojo_pct")                   # 7,66 % de la calma = 101 min/día (presupuesto)
umbral = T("part_umbral_wh")
cal_val, cal_prueba = T("cal_decil10_tasa_mdp"), T("cal_decil10_tasa_prueba")
caso1_wh, caso1_ini = T("caso1_energia_wh"), T("caso1_inicio")
prueba_ini, prueba_fin = T("part_prueba_inicio"), T("part_prueba_fin")
expl_fid = T("expl_fidelidad")

# ---------------------------------------------------------------------------------------------------------------
# 1 · Portada
sl = prs.slides.add_slide(BLANK)
base(sl, 1)
caja(sl, 0.75, 0.6, 0.34, 0.34, fill=VERDE, line=None, forma=MSO_SHAPE.ROUNDED_RECTANGLE)
texto(sl, 0.75, 0.6, 0.34, 0.34, "S", 13, "FFFFFF", F_MONO, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
texto(sl, 1.23, 0.62, 2.4, 0.3, "Shiro Guardian", 13, TX, F_TIT)
texto(sl, 3.2, 0.66, 6.2, 0.3, "Aprendizaje de Máquina · Parcial 2 · Parte 3", 10, MUT2, F_MONO)
caja(sl, 9.95, 0.42, 2.63, 1.5, fill="FFFFFF", line=None, forma=MSO_SHAPE.ROUNDED_RECTANGLE)
sl.shapes.add_picture(str(ESCUDO), Inches(10.07), Inches(0.53), width=Inches(2.39))
texto(sl, 0.75, 2.2, 10.0, 0.3, "PROPUESTA DE IMPLEMENTACIÓN · SHIRO COMO PRODUCTO PROPIO", 11, AMBAR, F_MONO)
texto(sl, 0.75, 2.6, 11.8, 1.6, ["Shiro Guardian en un hogar real:", "quién lo opera, cómo se cuida y cómo se usa."],
      34, TX, F_TIT, esp=0)
texto(sl, 0.75, 4.15, 11.0, 1.2,
      f"Guardian es la parte de Shiro que avisa antes de un pico de consumo (más de {umbral} en 10 min) para que la "
      f"persona alcance a aplazar una carga grande. Esta propuesta lleva al hogar el modelo elegido en el parcial —el "
      f"modelo mínimo de dos variables— con su costo a la vista: {n20} de {picos} picos avisados con margen y "
      f"{falsos} de avisos sin pico detrás.", 15, MUT)
caja(sl, 0.75, 5.75, 11.83, 0.01, fill=LINEA, line=None)
texto(sl, 0.75, 5.95, 8.4, 0.3,
      "Jose Leonardo Diazgranados · Sofía Londoño · Andrés Felipe Céspedes Rondón · Alex Duran", 11, TX2, F_TIT)
texto(sl, 0.75, 6.28, 8.4, 0.3,
      "Universidad Sergio Arboleda · Docente: Hernán Darío Cruz Bueno · 2.º corte, 2026-2", 10, MUT2, F_MONO)
texto(sl, 9.2, 5.95, 3.38, 0.6, ["Appliances Energy Prediction · UCI n.º 374", f"mes de prueba: {prueba_ini.split(' ')[0]} a {prueba_fin.split(' ')[0]}"],
      10, MUT2, F_MONO, align=PP_ALIGN.RIGHT, esp=0)
notas(sl, (
    "Esta es la Parte 3 del parcial: cómo pondríamos Shiro Guardian a funcionar en una casa de verdad. La organización "
    "es la nuestra: Shiro es nuestro producto y el equipo de Shiro sería quien lo instala y lo mantiene. "
    "Guardian tiene una tarea concreta: avisar antes de un pico de consumo —más de 200 Wh en una lectura de diez "
    "minutos— para que la persona alcance a aplazar una carga grande, como la secadora o el horno. "
    f"No vendemos más de lo que medimos: en el mes que el modelo nunca vio, Guardian avisó {n20} de {picos} picos con al "
    f"menos dos lecturas de antelación, y el {falsos} de sus avisos no tuvo un pico detrás. Toda la propuesta está "
    "pensada alrededor de ese costo: quién decide, cómo se recalibra cada mes y cómo se enseña a leer el semáforo para "
    "que no se termine ignorando."))

# ---------------------------------------------------------------------------------------------------------------
# 2 · Producto y arquitectura
sl = prs.slides.add_slide(BLANK)
base(sl, 2, "PRODUCTO Y ARQUITECTURA", "Guardian es una capa de Shiro, no una aplicación aparte")
etapas = [
    ("Medidor y sensores", "Una lectura de consumo cada 10 min. En la maqueta, datos históricos de una vivienda; en el "
                           "piloto (Fase 3), el medidor del hogar."),
    ("`iot-bridge`", "`IDeviceModule` por dispositivo y `DeviceRegistry` (ADR 0003). Hoy `InProcessTransport`; "
                     "luego `MQTTTransport` / Home Assistant."),
    ("Servicio Python de modelos", "Local, como el de Whisper (ADR 0020): puntaje del modelo mínimo, probabilidad "
                                   "calibrada y pronóstico del gemelo (lineal + retardos)."),
    ("Semáforo + `ApprovalGate`", "Verde, ámbar o rojo para la próxima media hora. En rojo, una propuesta que la "
                                  "persona aprueba, ajusta o rechaza (ADR 0022); vence en 30 min."),
    ("App de Shiro", "El modal de aprobación que ya existe en el cliente; Shiro lo dice con su voz y su avatar."),
]
w, gap, x0, y0, h = 2.13, 0.295, 0.75, 1.8, 2.6
for i, (tit, cuerpo) in enumerate(etapas):
    x = x0 + i * (w + gap)
    caja(sl, x, y0, w, h)
    caja(sl, x, y0, w, 0.06, fill=[MUT2, VERDE, VERDE, AMBAR, VERDE][i], line=None)
    texto(sl, x + 0.16, y0 + 0.22, w - 0.32, 0.55, tit, 14, TX, F_TIT)
    texto(sl, x + 0.16, y0 + 0.74, w - 0.32, h - 0.8, cuerpo, 12, MUT)
    if i < 4:
        a = sl.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + w + 0.03), Inches(y0 + 1.1), Inches(gap - 0.06),
                                Inches(0.3))
        a.fill.solid()
        a.fill.fore_color.rgb = rgb(MUT2)
        a.line.fill.background()
caja(sl, 0.75, 4.6, 5.8, 2.3, forma=MSO_SHAPE.ROUNDED_RECTANGLE)
texto(sl, 0.98, 4.72, 5.4, 0.3, "QUÉ PROMETE", 10.5, VERDE_CLARO, F_MONO)
texto(sl, 0.98, 5.04, 5.4, 1.8,
      f"≈ {T('titular_p20_fraccion')} picos avisados con al menos dos lecturas de antelación: **{n20} de {picos} ({p20})** en el "
      f"mes que el modelo nunca vio, con el semáforo en rojo {min_dia} y {avisos_dia}. Con esos mismos "
      f"{N('titular_min_dia')} min en rojo, el azar avisa el {azar} y la regla del medidor {m20} de {picos} "
      f"(+{d_regla} puntos, rango {ic_inf} a {ic_sup}: no concluyente).", 13, TX2)
caja(sl, 6.78, 4.6, 5.8, 2.3, forma=MSO_SHAPE.ROUNDED_RECTANGLE)
texto(sl, 7.01, 4.72, 5.4, 0.3, "QUÉ NO PROMETE", 10.5, AMBAR, F_MONO)
texto(sl, 7.01, 5.04, 5.4, 1.8,
      f"**No actúa:** su catálogo es de solo lectura y notificación; nada se enciende ni se apaga solo. "
      f"**No ahorra solo:** el {falsos} de los avisos no tuvo pico detrás, y aplazar depende de la persona. "
      "**No sabe qué aparato** se va a encender.", 13, TX2)
notas(sl, (
    "Guardian no es una aplicación nueva: es una capa que se monta sobre piezas que la arquitectura de Shiro ya "
    "reservó. De izquierda a derecha: el medidor entrega una lectura cada diez minutos. Entra por iot-bridge, el "
    "paquete que la arquitectura de Shiro dejó previsto para IoT, con las interfaces IDeviceModule y DeviceRegistry "
    "del ADR 0003; hoy el transporte es en proceso y más adelante sería MQTT hacia Home Assistant, sin tocar el resto. "
    "El cálculo vive en un servicio Python local, igual que hoy vive Whisper: ahí está el modelo mínimo de dos "
    "variables, su probabilidad calibrada y el pronóstico del gemelo. El semáforo pinta la próxima media hora; si "
    "sale rojo, la propuesta pasa por ApprovalGate, el mismo mecanismo con el que Shiro ya pide permiso antes de "
    "escribir un archivo. Y la persona la ve en la aplicación, con la voz y el avatar de Shiro. "
    "Al bus de Shiro van cuatro eventos, con la convención módulo:verbo: iot:reading en cada lectura; "
    "iot:anomaly-detected cuando el pico ya está en curso, que lo dice el medidor; iot:action-suggested cuando el "
    "semáforo anticipa un rojo con su propuesta; e iot:action-approved, que solo registra la decisión de la persona. "
    f"Lo que prometemos es concreto: unos {T('titular_p20_fraccion')} picos con margen, {n20} de {picos} en el mes de prueba, con "
    f"{min_dia} en rojo, que es el rojo realizado en ese mes con los cortes fijados en abril. Con esos mismos "
    f"minutos en rojo, la regla del medidor avisa {m20} y el azar el {azar}: frente al "
    f"azar Guardian se distingue; frente a la regla son {d_regla} puntos más, con un rango de {ic_inf} a {ic_sup}, que "
    f"con {picos} picos no es concluyente. Lo que no prometemos también: Guardian no actúa, no ahorra por sí mismo, y el {falsos} de sus "
    "avisos son falsas alarmas. La probabilidad calibrada que viaja en iot:action-suggested es la que entra al estado "
    "del MDP del agente; el gemelo sigue siendo la función de transición, no el semáforo."))

# ---------------------------------------------------------------------------------------------------------------
# 3 · Datos y privacidad
sl = prs.slides.add_slide(BLANK)
base(sl, 3, "DATOS Y PRIVACIDAD", "Lo que Guardian necesita sale del medidor y se queda en casa")
filas = [
    ("Qué entra", "Una lectura de consumo cada 10 min, la hora y si es laborable o fin de semana. El modelo elegido usa "
                  "**solo dos variables**: el consumo actual y qué tan seguido hubo picos a esa hora."),
    ("Qué se guarda", "Solo en el equipo del hogar: las tablas del modelo (una celda por hora y tipo de día) y el "
                      "último mes de lecturas para recalibrar. La ventana de 1 h (6 lecturas) es para el pronóstico."),
    ("Dónde se procesa", "En el equipo del hogar: el servicio de modelos corre local y la recalibración mensual usa los "
                         "puntajes del último mes sin sacarlos de la casa."),
    ("Qué sale", "Solo los indicadores agregados del tablero mensual (4 + 1), y solo si el titular lo consiente. "
                 "Nunca la serie de consumo."),
]
y = 1.95
for tit, cuerpo in filas:
    caja(sl, 0.75, y, 7.25, 0.92, forma=MSO_SHAPE.ROUNDED_RECTANGLE)
    texto(sl, 0.98, y + 0.12, 1.85, 0.7, tit, 13.5, TX, F_TIT)
    texto(sl, 2.85, y + 0.1, 4.95, 0.8, cuerpo, 12, MUT)
    y += 1.0
caja(sl, 8.25, 1.95, 4.33, 3.92)
caja(sl, 8.25, 1.95, 4.33, 0.06, fill=AMBAR, line=None)
texto(sl, 8.5, 2.15, 3.9, 0.3, "POR QUÉ IMPORTA", 10, AMBAR, F_MONO)
texto(sl, 8.5, 2.5, 3.9, 3.7, [
    "El consumo cada 10 minutos revela la ocupación: cuándo hay alguien en casa, cuándo se cocina, cuándo se lava.",
    "En Colombia es un dato personal bajo la **Ley 1581 de 2012**: autorización previa e informada del titular, "
    "finalidad declarada (avisar picos, nada más) y derecho a conocer, rectificar y pedir la supresión.",
    "Los convivientes también son titulares de sus datos: se les informa y pueden pedir que Guardian se apague.",
], 12, TX2, esp=8)
barra(sl, 6.05, 0.8, "**Qué cambia en Shiro:** el semáforo funciona sin nube. Si mañana no hay conexión, Guardian sigue "
                     "pintando la próxima media hora; lo único que se pierde es el tablero agregado.", size=12.5)
notas(sl, (
    "Una ventaja del modelo que elegimos es que pide muy poco. Para el color solo necesita dos cosas: el consumo de "
    "ahora y qué tan seguido hubo picos a esa misma hora en días parecidos. Eso sale del medidor y del reloj. "
    "Los sensores de temperatura y humedad por habitación no son obligatorios: solo afinan el pronóstico de consumo, "
    "que es la otra pieza, el gemelo. Lo que se guarda, y solo en el equipo de la casa: las tablas del modelo, una "
    "celda por hora y por tipo de día, y el último mes de lecturas, que hace falta para recalibrar; el pronóstico usa "
    "además una ventana de una hora, seis lecturas, en memoria. "
    "Todo se procesa en el equipo de la casa, como ya hace Shiro con el reconocimiento de voz. Incluso la "
    "recalibración mensual se hace allí. Al equipo de Shiro solo le llegarían los indicadores agregados del tablero "
    "mensual, cuatro más el percentil 90 del consumo, y solo si el titular lo autoriza. ¿Por qué tanto cuidado? Porque el consumo cada diez minutos dice cuándo hay gente "
    "en casa. En Colombia eso es un dato personal bajo la Ley 1581 de 2012: hace falta autorización previa, una "
    "finalidad declarada y el derecho a conocer y suprimir los datos. Y los convivientes también cuentan."))

# ---------------------------------------------------------------------------------------------------------------
# 4 · Roles (RACI)
sl = prs.slides.add_slide(BLANK)
base(sl, 4, "ROLES · MATRIZ RACI", "Quién decide, quién opera y quién responde")
cols = ["Actividad", "Titular del hogar", "Convivientes", "Ciencia de datos", "Plataforma", "Soporte", "Privacidad"]
filas = [
    ("Aprobar, ajustar o rechazar una propuesta", "R · A", "I", "—", "—", "—", "—"),
    ("Elegir cuánto rojo se tolera (deslizador)", "R · A", "C", "C", "—", "I", "—"),
    ("Recalibrar cada mes (servicio local, en casa)", "I", "—", "A", "R", "I", "—"),
    ("Definir la recalibración y auditar agregados", "I", "—", "R · A", "C", "—", "C"),
    ("Mantener iot-bridge y el servicio de modelos", "I", "—", "C", "R · A", "C", "—"),
    ("Modo aprendizaje (gris) en hogar nuevo", "I", "I", "R · A", "C", "C", "—"),
    ("Atender dudas, fallas y falsas alarmas", "C", "C", "C", "C", "R · A", "—"),
    ("Autorización de datos y envío de agregados", "A", "C", "I", "C", "—", "R"),
]
anchos = [4.1, 1.35, 1.25, 1.35, 1.25, 1.15, 1.38]
tabla_sh = sl.shapes.add_table(len(filas) + 1, len(cols), Inches(0.75), Inches(1.75), Inches(sum(anchos)),
                          Inches(0.44 * (len(filas) + 1)))
tabla_sh.table.first_row = False
tabla_sh.table.horz_banding = False
tab = tabla_sh.table
for j, a in enumerate(anchos):
    tab.columns[j].width = Inches(a)
for i in range(len(filas) + 1):
    tab.rows[i].height = Inches(0.44)
    for j in range(len(cols)):
        cel = tab.cell(i, j)
        cel.fill.solid()
        cel.fill.fore_color.rgb = rgb(LINEA if i == 0 else (CARD if i % 2 else "11151B"))
        cel.margin_left = cel.margin_right = Inches(0.08)
        cel.vertical_anchor = MSO_ANCHOR.MIDDLE
        bordes(cel)
        val = cols[j] if i == 0 else filas[i - 1][j]
        p = cel.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
        r = p.add_run()
        r.text = val
        if i == 0:
            r.font.name, r.font.size, r.font.color.rgb = F_MONO, Pt(10), rgb(MUT)
        elif j == 0:
            r.font.name, r.font.size, r.font.color.rgb = F_TXT, Pt(12), rgb(TX2)
        else:
            fuerte = "A" in val or "R" in val
            r.font.name, r.font.size = F_MONO, Pt(12)
            r.font.bold = fuerte
            r.font.color.rgb = rgb(VERDE_CLARO if fuerte else MUT)
texto(sl, 0.75, 6.0, 11.83, 0.3, "R = lo hace · A = responde por el resultado · C = se le consulta · I = se le informa. "
      "Hogar: titular y convivientes. Equipo de Shiro: ciencia de datos, plataforma, soporte y privacidad.", 10.5, MUT2)
barra(sl, 6.33, 0.6, "**Shiro propone, la persona decide:** ninguna fila pone a Shiro como responsable de una acción "
                     "dentro de la casa.", size=12.5)
notas(sl, (
    "Esta matriz responde quién hace qué. En la casa hay dos papeles: el titular, que es quien autorizó Guardian y quien "
    "aprueba, ajusta o rechaza cada propuesta, y los convivientes, que ven el semáforo y a quienes se consulta cuando "
    "se decide cuánto rojo tolerar. En el equipo de Shiro hay cuatro: ciencia de datos define cómo se recalibra y "
    "audita los indicadores agregados, pero la recalibración la ejecuta el servicio local dentro de la casa, porque "
    "los datos no salen de ahí; plataforma instala y mantiene iot-bridge y ese servicio; soporte atiende dudas y, "
    "sobre todo, las quejas por falsas alarmas; y privacidad responde por la autorización y por lo único que sale de "
    "la casa, los indicadores agregados. Fíjense en lo que no aparece: Shiro no es responsable de ninguna acción dentro "
    "del hogar. Propone y la persona decide, igual que hoy Shiro pide permiso antes de tocar un archivo."))

# ---------------------------------------------------------------------------------------------------------------
# 5 · Ciclo mensual y hogar nuevo
sl = prs.slides.add_slide(BLANK)
base(sl, 5, "CICLO MENSUAL Y HOGAR NUEVO", "Cada mes se recalibra; cada hogar nuevo empieza en gris")
pasos = [
    ("INSTALACIÓN", "Autorización del titular, conexión del medidor y guía de una página."),
    ("MODO APRENDIZAJE · HIPÓTESIS: ≈ 1 MES",
     "Gris y sin notificaciones: Guardian calcula y registra. Sale del gris por datos, no por calendario: cuando "
     "cada celda hora × tipo de día tenga ejemplos y picos suficientes (el mínimo se fija en el piloto)."),
    ("SEMÁFORO ACTIVO", "Propuestas en rojo. Cada mes: recalibrar cortes y revisar el tablero. Con más de 30 días "
                        "sin recalibrar vuelve el gris: baja confianza, no propone."),
]
y = 1.8
for i, (tit, cuerpo) in enumerate(pasos):
    caja(sl, 0.75, y, 5.55, 1.36, forma=MSO_SHAPE.ROUNDED_RECTANGLE)
    caja(sl, 0.75, y, 0.06, 1.36, fill=[MUT2, MUT2, VERDE][i], line=None)
    texto(sl, 1.0, y + 0.12, 5.1, 0.3, tit, 11, VERDE_CLARO if i == 2 else TX2, F_MONO)
    texto(sl, 1.0, y + 0.44, 5.15, 0.88, cuerpo, 12, MUT)
    y += 1.44
texto(sl, 6.6, 1.8, 6.0, 0.3, "TABLERO MENSUAL · 4 + 1 INDICADORES (MES DE PRUEBA)", 10.5, VERDE_CLARO, F_MONO)
kpis = [
    (f"{n20} de {picos}", f"picos avisados con al menos dos lecturas de antelación ({p20})"),
    (N("titular_avisos_dia"), "avisos al día"),
    (utiles, "de los avisos precedieron un pico"),
    (f"{N('titular_min_dia')} min", f"al día en rojo, frente a {presup_min} del presupuesto"),
]
for i, (big, sub) in enumerate(kpis):
    x, yk = 6.6 + (i % 2) * 3.03, 2.15 + (i // 2) * 1.2
    caja(sl, x, yk, 2.9, 1.1, forma=MSO_SHAPE.ROUNDED_RECTANGLE)
    texto(sl, x + 0.18, yk + 0.1, 2.6, 0.4, big, 20, TX, F_TIT)
    texto(sl, x + 0.18, yk + 0.52, 2.6, 0.55, sub, 12, MUT)
texto(sl, 6.6, 4.6, 5.98, 0.5,
      f"**+1, señal de deriva:** percentil 90 del consumo del mes, {p90_may} (enero: {p90_ene}; el pico se define "
      f"en {umbral}).", 12, MUT)
texto(sl, 6.6, 5.18, 5.98, 0.85,
      f"Dos rojos: el **presupuesto** fijado en abril ({presup_min}, {presup_pct} de la calma) y el **realizado** en "
      f"el mes ({min_dia}, {rojo_pct}). Con el presupuesto, la validación fue optimista: {val_p20} frente a "
      f"{prueba_p20} en prueba. El titular, {p20}, es con el realizado.", 12, MUT)
barra(sl, 6.12, 0.78, f"**Por qué cada mes:** con los cortes de abril, en mayo el modelo mínimo quedó en rojo "
                      f"{min_dia} frente a {presup_min} previstos, y los bosques {g1_min} y {g4_min}. Ninguna definición "
                      "de pico es inmune a la estación.", acento=AMBAR, size=12)
notas(sl, (
    "Dos ideas en esta diapositiva. La primera: un hogar nuevo no empieza con alarmas. El modelo se aprendió en una sola "
    "vivienda belga de invierno y primavera; en otra casa no sabemos qué tan bien funciona. Por eso arranca en modo "
    "aprendizaje: semáforo gris, sin notificaciones; Guardian solo calcula y registra. ¿Cuánto dura? Un mes es una "
    f"hipótesis que hay que validar en el piloto, no algo medido: en el parcial el modelo se ajustó con "
    f"{T('part_fit_dias')} de datos y los cortes con {T('part_val_dias')} de validación, y con un solo mes cada celda "
    "de hora por tipo de día tendría pocos ejemplos. Por eso la salida del gris se define por datos —ejemplos y "
    "picos suficientes en cada celda— y no por calendario. La segunda idea: cada mes se recalibra, porque lo medimos. "
    "Aquí conviene distinguir dos rojos. El presupuesto es el que se fija en abril, con la validación: "
    f"{presup_min}, el {presup_pct} de los momentos tranquilos. El realizado es el que de verdad hubo en el mes de "
    f"prueba con esos cortes: {min_dia}, el {rojo_pct}. Con el presupuesto, el modelo mínimo avisó {val_p20} de los "
    f"picos en validación y {prueba_p20} en prueba: la validación fue optimista. El titular de {n20} de {picos}, "
    f"{p20}, se mide con el rojo realizado, que fue mayor. "
    f"Los bosques se dispararon a {g1_min} y {g4_min}. El percentil 90 del consumo cayó de {p90_ene} en enero a "
    f"{p90_may} en mayo. Si pasan más de treinta días sin recalibrar, el semáforo vuelve a gris y deja de proponer. "
    "El tablero tiene cuatro indicadores, los mismos del informe: picos avisados con margen, avisos al día, avisos "
    "que precedieron un pico y minutos en rojo frente al presupuesto; más uno, el percentil 90 del consumo, que "
    "avisa si la propia definición de pico se está quedando vieja. Se lee mes contra mes, no contra la validación."))

# ---------------------------------------------------------------------------------------------------------------
# 6 · Capacitación
sl = prs.slides.add_slide(BLANK)
base(sl, 6, "CAPACITACIÓN AL USUARIO", "Enseñar a leer el semáforo antes de que llegue el primer rojo")
from PIL import Image as _Img
alto = 4.55
with _Img.open(CAPTURA) as _im:
    ancho = alto * _im.width / _im.height
caja(sl, 0.75, 1.8, ancho + 0.16, alto + 0.16, fill=LINEA, line=None, forma=MSO_SHAPE.ROUNDED_RECTANGLE)
sl.shapes.add_picture(str(CAPTURA), Inches(0.83), Inches(1.88), height=Inches(alto))
texto(sl, 0.75, 6.6, ancho + 0.16, 0.3, "Maqueta · tarjeta 1 (recorte)", 10, MUT2, F_MONO)
xr = 0.75 + ancho + 0.45
wr = 12.58 - xr
items = [
    ("Recorrido guiado de 10 min con la maqueta",
     "Un momento verde, un rojo con su propuesta y un rojo que fue falsa alarma; aprobar, ajustar y rechazar."),
    ("Guía de una página del semáforo",
     "Verde: nada. Ámbar: revisar antes de encender cargas grandes. Rojo: propuesta por 30 min. "
     "Rojo en curso: el medidor ya lo ve. Gris: baja confianza."),
    ("Video corto y preguntas frecuentes",
     f"«¿Por qué sonó y no hubo pico?» (el {falsos} de los avisos no tuvo pico detrás) · «¿Shiro apaga algo?» (no) · "
     "«¿Qué datos salen de la casa?»"),
]
y = 1.8
for tit, cuerpo in items:
    texto(sl, xr, y, wr, 0.32, tit, 15, TX, F_TIT)
    texto(sl, xr, y + 0.38, wr, 0.75, cuerpo, 13, MUT)
    y += 1.2
caja(sl, xr, 5.5, wr, 1.2, forma=MSO_SHAPE.ROUNDED_RECTANGLE)
caja(sl, xr, 5.5, 0.06, 1.2, fill=VERDE, line=None)
texto(sl, xr + 0.25, 5.6, wr - 0.4, 1.05,
      ["**Cómo se mide el éxito:** % de propuestas respondidas (aprobar, ajustar o rechazar) y cuántas veces se mueve "
       "el deslizador de rojo. Si las propuestas dejan de responderse, el semáforo se está ignorando. Se mide en el "
       "piloto (Fase 3): hoy no hay cifra."], 12.5, TX2)
notas(sl, (
    "Un semáforo que nadie entiende se apaga a la semana. La capacitación tiene tres piezas. Primero, un recorrido "
    "guiado de diez minutos con la misma maqueta que mostramos en la sustentación: cargar un momento verde, uno rojo con "
    "su propuesta y uno rojo que terminó en falsa alarma, y practicar aprobar, ajustar y rechazar. Segundo, una guía de "
    "una página con lo que significa cada color y lo que hace Shiro en cada uno. Tercero, un video corto y preguntas "
    f"frecuentes; la primera siempre será «¿por qué sonó si no pasó nada?», y la respuesta honesta es que el {falsos} "
    "de los avisos no tiene un pico detrás: es el precio de avisar con margen sin saber qué aparato se va a encender. "
    "¿Cómo sabremos si funcionó? Con dos señales del piloto, que es la Fase 3, en hogares reales: qué porcentaje de propuestas responde la persona y cuántas "
    "veces ajusta el deslizador. Hoy no tenemos esa cifra y no la inventamos."))

# ---------------------------------------------------------------------------------------------------------------
# 7 · Piloto y riesgos
sl = prs.slides.add_slide(BLANK)
base(sl, 7, "PILOTO Y RIESGOS", "De Twin a Home, sin fechas y con criterios de salida")
fases = [
    ("FASE 1 · SHIRO TWIN", "Objetivo formal del curso",
     "Gemelo y agente sobre datos reales. El MDP y el agente siguen pendientes (3.er corte).",
     "Sale con: MDP formalizado y agente evaluado dentro del gemelo."),
    ("FASE 2 · SHIRO GUARDIAN", "Solo lectura y notificación",
     f"Se adelantó en el parcial 2 sobre los datos y el gemelo de Twin ({n20} de {picos} con margen); su fase formal "
     "sigue siendo esta.",
     "Sale con: revalidación en otra vivienda (UCI n.º 235) que supere a la regla y al azar."),
    ("FASE 3 · SHIRO HOME", "Piloto en hogares reales",
     "ADR formal, `MQTTTransport` hacia Home Assistant, `DeviceRegistry` real y `ApprovalGate` para aparatos.",
     "Sale con: propuestas respondidas y tablero estable entre recalibraciones."),
]
for i, (k, sub, cuerpo, salida) in enumerate(fases):
    x = 0.75 + i * 3.98
    caja(sl, x, 1.75, 3.85, 2.55)
    caja(sl, x, 1.75, 3.85, 0.06, fill=[MUT2, VERDE, AMBAR][i], line=None)
    texto(sl, x + 0.2, 1.88, 3.45, 0.28, k, 10.5, VERDE_CLARO if i == 1 else MUT, F_MONO)
    texto(sl, x + 0.2, 2.15, 3.45, 0.34, sub, 14, TX, F_TIT)
    texto(sl, x + 0.2, 2.55, 3.45, 0.9, cuerpo, 12, MUT)
    texto(sl, x + 0.2, 3.5, 3.45, 0.75, salida, 12, TX2)
riesgos = [
    ("Fatiga de alarmas", f"{falsos} de avisos sin pico", "Deslizador del titular; el ámbar no notifica."),
    ("Deriva estacional", f"{min_dia} en rojo frente a {presup_min}", "Recalibración mensual; gris tras 30 días sin ella."),
    ("Una sola vivienda", "invierno y primavera, sin verano", "Modo aprendizaje; otra vivienda antes del piloto."),
    ("Pico no avisado", f"el más costoso ({caso1_wh}) en ámbar", "La guía explica el ámbar; no se prometen todos."),
    ("Privacidad", "el consumo revela ocupación", "Proceso local; agregados con autorización (Ley 1581)."),
]
texto(sl, 0.75, 4.45, 2.5, 0.28, "RIESGO", 10, MUT2, F_MONO)
texto(sl, 3.0, 4.45, 3.6, 0.28, "EVIDENCIA", 10, MUT2, F_MONO)
texto(sl, 6.75, 4.45, 5.85, 0.28, "MITIGACIÓN", 10, MUT2, F_MONO)
caja(sl, 0.75, 4.75, 11.83, 0.01, fill="2C323E", line=None)
y = 4.84
for r_, ev, mit in riesgos:
    texto(sl, 0.75, y, 2.2, 0.4, r_, 12.5, TX, F_TIT)
    texto(sl, 3.0, y, 3.6, 0.4, ev, 12, AMBAR)
    texto(sl, 6.75, y, 5.85, 0.4, mit, 12, MUT)
    y += 0.42
notas(sl, (
    "Cerramos con la ruta. Guardian se monta sobre la hoja de ruta del proyecto, en tres fases, sin fechas, porque cada una se "
    "abre solo cuando la anterior cumple su criterio de salida. Shiro Twin es el objetivo formal del curso: el gemelo y "
    "el agente; el MDP y el agente de Q-learning siguen pendientes para el tercer corte. Shiro Guardian es formalmente "
    "la Fase 2, la que la hoja de ruta del proyecto deja para cuando Twin cierre con margen; en este parcial la adelantamos "
    "sobre los datos y el gemelo de Twin, pero su fase sigue siendo la 2. Es software puro, sin ADR ni hardware, y "
    "su criterio de salida es repetir la prueba en otra vivienda y seguir superando a la regla del medidor y al azar "
    "con el mismo tiempo en rojo. Shiro Home, la Fase 3, es el piloto en hogares reales: exige el ADR formal, MQTT "
    "hacia Home Assistant, dispositivos registrados y extender ApprovalGate a aparatos físicos. Cuando en estas "
    "diapositivas decimos «el piloto», es esa fase. "
    f"Los riesgos están medidos, no imaginados: fatiga de alarmas, porque el {falsos} de los avisos no tiene pico "
    f"detrás; deriva, porque en mayo el rojo subió a {min_dia}; una sola vivienda; el pico no avisado más costoso, de "
    f"{caso1_wh}, que se quedó en ámbar; y la privacidad. Cada uno tiene su mitigación en las diapositivas anteriores."))

assert len(prs.slides) == TOTAL

# Comprobaciones: notas en todas y sin residuos prohibidos
todo_texto = []
for i, s in enumerate(prs.slides, 1):
    nt = s.notes_slide.notes_text_frame.text if s.has_notes_slide else ""
    assert len(nt) > 200, f"Diapositiva {i} sin notas suficientes"
    todo_texto.append(nt)
    for sh in s.shapes:
        if sh.has_text_frame:
            todo_texto.append(sh.text_frame.text)
        if sh.has_table:
            todo_texto += [c.text for row in sh.table.rows for c in row.cells]
res = buscar_residuos("\n".join(todo_texto))
assert not res, f"Residuos prohibidos: {res}"

cp = prs.core_properties
cp.author = cp.last_modified_by = "Grupo Shiro — Diazgranados, Londoño, Céspedes Rondón, Duran"
cp.title = "Shiro Guardian — propuesta de implementación (Parcial 2, Parte 3)"
cp.subject = "Aprendizaje de Máquina · Universidad Sergio Arboleda · 2.º corte, 2026-2"
cp.comments = "Propuesta de implementación de Shiro Guardian"
cp.keywords = "Shiro Guardian; implementación; semáforo de picos"
cp.category = ""
prs.save(SALIDA)
print(f"PPTX: {SALIDA.name} · {len(prs.slides)} diapositivas · {len(C.usadas)} cifras de cifras.json")
if "--sin-pdf" not in sys.argv:
    pdf = exportar_pdf(SALIDA, SALIDA.with_suffix(".pdf"))
    print(f"PDF: {pdf.name}")
