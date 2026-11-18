# -*- coding: utf-8 -*-
r"""Genera Presentacion_Parcial3_Shiro.pptx (y su PDF): la presentación del Parcial 3 (≈ 15–20 min, 22 diapositivas).

Sigue el hilo del artículo (lo que Shiro necesita → el paradigma que lo resuelve → qué cambia en Shiro) con la paleta
oscura de la consola, para que presentación y demo se vean como una sola pieza. Toda cifra se escribe {prefijo:clave}
(comun.py); {prefijo:clave|n} deja solo el número. Las notas del orador no tienen reparto (decisión de Pipe).

Uso (desde la carpeta del parcial):
    C:\Users\pipel\venvs\ml\Scripts\python.exe -X utf8 generadores\generar_presentacion.py
"""
import re
import sys
from pathlib import Path

from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Cm, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402
from comun import PROY, RAIZ, exportar_pdf  # noqa: E402

SALIDA = RAIZ / "Presentacion_Parcial3_Shiro.pptx"
FIG = RAIZ / "figuras"
F_G2 = PROY / "2do_Corte_Oct" / "Parcial_2_Aprendizaje_Supervisado" / "figuras" / "POSTER_G2.png"
F_T4H = PROY / "3er_Corte_Nov" / "Taller_3_DQN" / "figuras" / "T4_mapa_horario.png"

# Paleta oscura de la consola (consola_plantilla.html)
BG, PANEL, PANEL2, LINEA = "0F151B", "17202A", "202C38", "31404E"
INK, INK2 = "E6EDF3", "A0B1C1"
AZUL, TEAL, ROSA, NARANJA, AMBAR, VERDE, ROJO = "7FB2FF", "5BB8CC", "E07FB0", "E79A4E", "E8B33A", "4FBF72", "F0685C"
T_TIT, T_TXT = "Bahnschrift SemiBold", "Segoe UI"

SEC = {  # sección → (rótulo, color)
    "problema": ("El problema", INK2), "metodo": ("Método", INK2),
    "sup": ("Supervisado · el gemelo", AZUL), "gua": ("Guardian · cuándo avisar", AMBAR),
    "nos": ("No supervisado · el contexto", TEAL), "ref": ("Refuerzo · la decisión", ROSA),
    "pro": ("Prototipo · la consola", NARANJA), "lim": ("Ética y límites", ROJO), "fin": ("Cierre", VERDE),
}

prs = Presentation()
prs.slide_width, prs.slide_height = Cm(33.867), Cm(19.05)
W, H = prs.slide_width, prs.slide_height
VACIA = prs.slide_layouts[6]
MX = Cm(1.5)                       # margen lateral
CW = W - 2 * MX                    # ancho útil
Y0 = Cm(4.1)                       # inicio del contenido
NOTAS = []


# =====================================================================================================================
# Cifras
# =====================================================================================================================
_NUM = re.compile(r"^[−+]?\d[\d.]*(?:,\d+)?")


def _cifra(clave, mod):
    t = comun.C(clave)
    t = re.sub(r"(?<![\w])-(?=\d)", "−", t)
    if mod == "n":
        m = _NUM.match(t)
        t = m.group(0) if m else t
    return t


_UNIDAD = re.compile(r"(?<=\d) (?=(%|Wh\b|kWh|h/día|h\b|min\b|°C|puntos\b|días\b|picos\b|avisos/día|min/día))")


def F(texto):
    t = re.sub(r"\{([a-z0-9]+:[^{}|]+)(?:\|([a-z]+))?\}", lambda m: _cifra(m.group(1), m.group(2)), texto)
    t = _UNIDAD.sub(" ", t).replace("≥ ", "≥ ")      # la cifra no se separa de su unidad
    return t.replace("π*", "π∗")


# =====================================================================================================================
# Primitivas
# =====================================================================================================================
def _rgb(h):
    return RGBColor.from_string(h)


def _rect(s, x, y, w, h, color, forma=MSO_SHAPE.RECTANGLE, radio=None):
    r = s.shapes.add_shape(forma, x, y, w, h)
    r.fill.solid(); r.fill.fore_color.rgb = _rgb(color); r.line.fill.background(); r.shadow.inherit = False
    if radio is not None:
        r.adjustments[0] = radio
    return r


def _run(p, texto, tam, color, fuente=T_TXT, negrita=False, espaciado=None):
    r = p.add_run(); r.text = texto
    f = r.font; f.size = Pt(tam); f.color.rgb = _rgb(color); f.name = fuente; f.bold = negrita
    if espaciado:
        r._r.get_or_add_rPr().set("spc", str(espaciado))
    return r


def _vineta(p, color, sangria=0.6):
    pPr = p._p.get_or_add_pPr()
    pPr.set("marL", str(int(Cm(sangria)))); pPr.set("indent", str(-int(Cm(sangria))))
    c = etree.SubElement(pPr, qn("a:buClr")); etree.SubElement(c, qn("a:srgbClr")).set("val", color)
    etree.SubElement(pPr, qn("a:buFont")).set("typeface", "Arial")
    etree.SubElement(pPr, qn("a:buChar")).set("char", "•")


def _marcado(p, linea, tam, color, acento, fuente=T_TXT):
    """**texto** = negrita blanca; ^^texto^^ = negrita del color de la sección."""
    for trozo in re.split(r"(\*\*[^*]+\*\*|\^\^[^^]+\^\^)", F(linea)):
        if not trozo:
            continue
        if trozo.startswith("**"):
            _run(p, trozo[2:-2], tam, INK, fuente, True)
        elif trozo.startswith("^^"):
            _run(p, trozo[2:-2], tam, acento, fuente, True)
        else:
            _run(p, trozo, tam, color, fuente)


def texto(s, x, y, w, h, lineas, tam=16, color=INK, acento=AZUL, vinetas=False, espacio=6, fuente=T_TXT,
          alin=PP_ALIGN.LEFT, ancla=MSO_ANCHOR.TOP, interlineado=1.08):
    tb = s.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame; tf.word_wrap = True; tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = ancla
    for i, ln in enumerate(lineas):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = alin; p.space_after = Pt(espacio); p.line_spacing = interlineado
        if vinetas:
            _vineta(p, acento)
        _marcado(p, ln, tam, color, acento, fuente)
    return tb


def _mayus(t):
    """Mayúsculas sin tocar las letras griegas (λ, π, γ, α no deben volverse Λ, Π…)."""
    return "".join(ch if ch in "λπγαεθ∗" else ch.upper() for ch in t)


def rotulo(s, x, y, w, txt, color, tam=11.5):
    tb = s.shapes.add_textbox(x, y, w, Cm(0.7))
    tf = tb.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.word_wrap = True
    _run(tf.paragraphs[0], _mayus(F(txt)), tam, color, T_TIT, False, 120)
    return tb


def tarjeta(s, x, y, w, h, titulo, lineas, color, tam=15, vinetas=True, fondo=PANEL, espacio=5):
    _rect(s, x, y, w, h, fondo)
    _rect(s, x, y, Cm(0.13), h, color)
    yy = y + Cm(0.45)
    if titulo:
        rotulo(s, x + Cm(0.6), yy, w - Cm(1.0), titulo, color)
        yy += Cm(0.85)
    texto(s, x + Cm(0.6), yy, w - Cm(1.1), y + h - yy - Cm(0.3), lineas, tam=tam, acento=color, vinetas=vinetas,
          espacio=espacio)


def decision(s, x, y, w, h, txt, tam=15):
    """Recuadro de cierre de cada bloque: qué cambia en Shiro por causa de estos números."""
    _rect(s, x, y, w, h, PANEL2)
    _rect(s, x, y, Cm(0.13), h, VERDE)
    rotulo(s, x + Cm(0.6), y + Cm(0.4), w - Cm(1.0), "→ Qué cambia en Shiro", VERDE)
    texto(s, x + Cm(0.6), y + Cm(1.15), w - Cm(1.1), h - Cm(1.35), [txt], tam=tam, acento=VERDE)


def kpi(s, x, y, w, valor, etiqueta, color, tam=40, tam_et=13.5, alto=Cm(3.6)):
    tb = s.shapes.add_textbox(x, y, w, alto)
    tf = tb.text_frame; tf.word_wrap = True; tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]; p.line_spacing = 0.95
    _run(p, F(valor), tam, color, T_TIT)
    p2 = tf.add_paragraph(); p2.space_before = Pt(2); p2.line_spacing = 1.05
    _marcado(p2, etiqueta, tam_et, INK2, color)
    return tb


def figura(s, ruta, x, y, w, h, fondo="FFFFFF", pad=0.3):
    _rect(s, x, y, w, h, fondo)
    iw, ih = Image.open(ruta).size
    aw, ah = w - 2 * Cm(pad), h - 2 * Cm(pad)
    esc = min(aw / iw, ah / ih)
    pw, ph = int(iw * esc), int(ih * esc)
    s.shapes.add_picture(str(ruta), x + (w - pw) // 2, y + (h - ph) // 2, width=pw, height=ph)


def tabla(s, x, y, w, enc, filas, anchos, tam=14, alto=0.95, acento=AZUL, resaltar=()):
    n, m = len(filas) + 1, len(enc)
    gs = s.shapes.add_table(n, m, x, y, w, Cm(alto * n))
    tblPr = gs._element.graphic.graphicData.tbl.tblPr
    tblPr.set("firstRow", "0"); tblPr.set("bandRow", "0")
    sid = tblPr.find(qn("a:tableStyleId"))
    if sid is not None:
        sid.text = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"      # sin estilo, sin rejilla
    t = gs.table
    for j, a in enumerate(anchos):
        t.columns[j].width = Cm(a)
    for i in range(n):
        t.rows[i].height = Cm(alto)
        for j in range(m):
            c = t.cell(i, j)
            c.fill.solid()
            c.fill.fore_color.rgb = _rgb(PANEL2 if i == 0 else (PANEL if i % 2 else BG))
            c.margin_left = c.margin_right = Cm(0.25); c.margin_top = c.margin_bottom = Cm(0.05)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = c.text_frame; tf.word_wrap = True
            p = tf.paragraphs[0]; p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.RIGHT
            if i == 0:
                _run(p, _mayus(F(enc[j])), tam - 3, INK2, T_TIT, False, 80)
            else:
                v = str(filas[i - 1][j])
                if i - 1 in resaltar:
                    _marcado(p, "^^" + v + "^^" if not v.startswith("^^") else v, tam, INK, acento)
                else:
                    _marcado(p, v, tam, INK, acento)
    return t


def diapositiva(sec, titulo, notas):
    s = prs.slides.add_slide(VACIA)
    s.background.fill.solid(); s.background.fill.fore_color.rgb = _rgb(BG)
    nombre, color = SEC[sec]
    _rect(s, MX, Cm(1.0), Cm(0.5), Cm(0.13), color)
    rotulo(s, MX + Cm(0.75), Cm(0.78), Cm(20), nombre, color, tam=12)
    texto(s, MX, Cm(1.45), CW, Cm(2.4), [titulo], tam=27, fuente=T_TIT, interlineado=0.98, espacio=0)
    NOTAS.append((s, notas))
    return s


def pies():
    total = len(prs.slides)
    for i, s in enumerate(prs.slides, start=1):
        if i == 1:
            continue
        texto(s, MX, H - Cm(0.95), Cm(20), Cm(0.6), ["Shiro Twin · Parcial 3 · Aprendizaje de Máquina 26-2"], tam=10,
              color="6B7D8E")
        texto(s, W - MX - Cm(4), H - Cm(0.95), Cm(4), Cm(0.6), [f"{i} / {total}"], tam=10, color="6B7D8E",
              alin=PP_ALIGN.RIGHT)
    for s, n in NOTAS:
        s.notes_slide.notes_text_frame.text = F(" ".join(n.split()))


C1, C2 = MX, MX + CW // 2 + Cm(0.35)      # dos columnas
CW2 = CW // 2 - Cm(0.35)
CW3 = (CW - Cm(1.2)) // 3                   # tres columnas
X3 = [MX + i * (CW3 + Cm(0.6)) for i in range(3)]

# =====================================================================================================================
# 1 · Portada
# =====================================================================================================================
s = prs.slides.add_slide(VACIA)
s.background.fill.solid(); s.background.fill.fore_color.rgb = _rgb(BG)
_rect(s, 0, 0, Cm(0.35), H, NARANJA)
rotulo(s, MX, Cm(2.0), Cm(15), "Parcial 3 · Aprendizaje de Máquina 26-2", NARANJA, tam=13)
texto(s, MX, Cm(2.9), Cm(15.6), Cm(3.0), ["Shiro Twin"], tam=60, fuente=T_TIT, espacio=0)
texto(s, MX, Cm(5.9), Cm(15.2), Cm(4.4),
      ["Un gemelo digital del hogar que predice el consumo, anticipa los picos y propone cuándo aplazar una carga"],
      tam=21, color=INK2, interlineado=1.1)
texto(s, MX, Cm(11.3), Cm(15.4), Cm(4.6),
      ["**Grupo Shiro**", "Jose Leonardo Diazgranados · Sofía Londoño", "Andrés Felipe Céspedes Rondón · Alex Duran",
       "Docente: Hernán Darío Cruz Bueno", "Universidad Sergio Arboleda · noviembre de 2026"],
      tam=14, color=INK2, espacio=3)
figura(s, FIG / "consola_captura.png", Cm(17.6), Cm(3.3), Cm(14.8), Cm(10.6), fondo=LINEA, pad=0.08)
texto(s, Cm(17.6), Cm(14.2), Cm(14.8), Cm(1.4),
      ["La consola de Shiro: los tres aprendizajes del semestre funcionando en una sola página."],
      tam=12, color=INK2)
NOTAS.append((s, "Durante el semestre construimos Shiro Twin, la primera fase de Shiro, un asistente de energía para "
                 "el hogar. Shiro Twin es un gemelo digital: simula la casa, avisa antes de un pico y propone cuándo "
                 "aplazar una carga, pero no actúa; la persona decide. En los próximos minutos vamos a recorrer qué "
                 "necesitaba Shiro, cómo lo resolvió cada paradigma del curso —supervisado, no supervisado y refuerzo—, "
                 "la consola que junta los tres y, al final, lo que todavía no sabemos. Todas las cifras de estas "
                 "diapositivas salen de los cuadernos verificados de cada taller."))

# =====================================================================================================================
# 2 · Qué necesita Shiro
# =====================================================================================================================
s = diapositiva("problema", "Qué necesita Shiro para ayudar con la energía de una casa",
                "Shiro se construye en tres fases. Shiro Twin simula y solo propone; Guardian avisa; Shiro Home actúa "
                "en la casa con aprobación. Este curso construyó Shiro Twin, y para eso el gemelo necesitaba cuatro "
                "piezas. Cada una se resolvió con un paradigma distinto: la función de transición y la señal de aviso "
                "con aprendizaje supervisado, el contexto con no supervisado y la decisión con refuerzo. La pregunta "
                "que atraviesa todo el semestre está abajo: qué necesita saber el gemelo de un solo hogar para "
                "proponer con honestidad, y cuánto ahorro real hay detrás. Esa segunda mitad es importante, porque la "
                "respuesta honesta resultó ser «poco», y lo vamos a mostrar.")
fases = [("Shiro Twin", "Simula la casa y propone. Lo que construyó este curso.", NARANJA),
         ("Guardian", "Avisa antes de que empiece un pico.", AMBAR),
         ("Shiro Home", "Actúa en la casa con la aprobación de la persona.", INK2)]
for i, (t_, d_, c_) in enumerate(fases):
    x = X3[i]
    _rect(s, x, Y0, CW3, Cm(2.6), PANEL)
    _rect(s, x, Y0, CW3, Cm(0.12), c_)
    texto(s, x + Cm(0.5), Y0 + Cm(0.45), CW3 - Cm(1), Cm(0.9), [t_], tam=19, fuente=T_TIT, color=c_)
    texto(s, x + Cm(0.5), Y0 + Cm(1.35), CW3 - Cm(1), Cm(1.2), [d_], tam=13.5, color=INK2)
    if i < 2:
        texto(s, x + CW3 + Cm(0.05), Y0 + Cm(0.75), Cm(0.6), Cm(1), ["→"], tam=20, color=INK2, alin=PP_ALIGN.CENTER)
rotulo(s, MX, Y0 + Cm(3.25), CW, "Shiro Twin necesita cuatro piezas, y cada una pide un paradigma", INK2)
CW4 = (CW - Cm(1.5)) // 4
piezas = [("Función de transición", "¿Cuánto consumirá la casa en el paso siguiente?", "Supervisado", AZUL),
          ("Contexto", "¿Qué tipo de día se está viviendo hoy?", "No supervisado", TEAL),
          ("Señal anticipada", "¿Empieza un pico en los próximos 30 min?", "Supervisado, por antelación", AMBAR),
          ("Agente", "¿Aplazo esta carga o no hago nada?", "Refuerzo", ROSA)]
for i, (t_, q_, p_, c_) in enumerate(piezas):
    x = MX + i * (CW4 + Cm(0.5))
    y = Y0 + Cm(4.05)
    _rect(s, x, y, CW4, Cm(4.6), PANEL)
    _rect(s, x, y, Cm(0.13), Cm(4.6), c_)
    texto(s, x + Cm(0.55), y + Cm(0.4), CW4 - Cm(0.9), Cm(0.9), [t_], tam=16.5, fuente=T_TIT)
    texto(s, x + Cm(0.55), y + Cm(1.35), CW4 - Cm(0.9), Cm(2.0), [q_], tam=14, color=INK2)
    rotulo(s, x + Cm(0.55), y + Cm(3.65), CW4 - Cm(0.9), p_, c_, tam=11)
_rect(s, MX, Y0 + Cm(9.15), CW, Cm(2.25), PANEL2)
texto(s, MX + Cm(0.6), Y0 + Cm(9.4), CW - Cm(1.2), Cm(1.9),
      ["**La pregunta del semestre:** ¿qué necesita saber el gemelo de un solo hogar para proponer, con honestidad, "
       "cuándo aplazar una carga, y cuánto ahorro real hay detrás de esa propuesta?"], tam=16.5, color=INK2,
      ancla=MSO_ANCHOR.MIDDLE)

# =====================================================================================================================
# 3 · Arquitectura
# =====================================================================================================================
s = diapositiva("problema", "Cómo encajan las piezas: Shiro propone, la persona decide",
                "Este es el esquema de Shiro Twin. Arriba, el gemelo lineal: es el simulador previsto para que el "
                "agente entrene en un entorno continuo. Ojo, eso todavía está pendiente: hoy los agentes se entrenan en "
                "una réplica de días reales de la casa, y lo decimos así en el artículo. El tipo de día y el aviso de "
                "Guardian entran al estado del agente. El agente propone y la persona aprueba o rechaza; en Shiro Home, "
                "la acción aprobada volvería a la casa. Todo lo que sigue está ordenado en ese mismo sentido: primero "
                "la transición, después el aviso, el contexto y por último la decisión.")
figura(s, FIG / "A1_arquitectura.png", MX, Y0 - Cm(0.2), Cm(14.6), Cm(13.6))
xr = MX + Cm(15.4)
wr = CW - Cm(15.4)
tarjeta(s, xr, Y0 - Cm(0.2), wr, Cm(4.2), "Supervisado", [
    "**Gemelo lineal**: el consumo del paso siguiente; será el simulador del entorno continuo.",
    "**Guardian (G0)**: probabilidad de que empiece un pico en 30 min."], AZUL, tam=14.5)
tarjeta(s, xr, Y0 + Cm(4.3), wr, Cm(2.9), "No supervisado", [
    "**Tipo de día** con su margen como confianza; DBSCAN marca lo que no encaja."], TEAL, tam=14.5)
tarjeta(s, xr, Y0 + Cm(7.5), wr, Cm(2.9), "Refuerzo", [
    "**Agente** que propone aplazar o no; la persona aprueba y fija su paciencia (λ)."], ROSA, tam=14.5)
_rect(s, xr, Y0 + Cm(10.7), wr, Cm(2.7), PANEL2)
texto(s, xr + Cm(0.5), Y0 + Cm(10.9), wr - Cm(1), Cm(2.4),
      ["**Pendiente y declarado:** hoy los agentes entrenan en una réplica de días reales, no sobre el gemelo "
       "(flecha discontinua)."], tam=14, color=INK2, ancla=MSO_ANCHOR.MIDDLE)

# =====================================================================================================================
# 4 · Datos y reglas
# =====================================================================================================================
s = diapositiva("metodo", "Una sola casa y dos particiones que se reportan siempre",
                "Todo Shiro hereda las virtudes y los sesgos de un solo conjunto de datos: una vivienda belga de bajo "
                "consumo, con lecturas cada diez minutos de enero a mayo de 2016. Se eligió porque es el único candidato "
                "con temperatura por habitación, que la recompensa necesita para el confort. La regla de método más "
                "importante del semestre es la de las dos particiones. La aleatoria es la del material del curso; la "
                "temporal entrena hasta abril y prueba en mayo. Reportamos siempre las dos, pero toda decisión de "
                "arquitectura se toma con la temporal, porque dos lecturas seguidas son casi idénticas y la aleatoria "
                "deja en el entrenamiento al vecino de cada lectura de prueba. En KNN eso se vio: K igual a uno daba el "
                "mejor F1, señal inequívoca de fuga.")
tarjeta(s, C1, Y0, CW2, Cm(8.0), "El hogar (UCI n.º 374)", [
    "**{p2:datos_n_lecturas}** cada 10 min, del 11-ene al 27-may-2016, sin faltantes.",
    "**{t1:n_dias} días completos**; objetivo: consumo de los aparatos en Wh.",
    "**{p2:part_n_exogenas} predictoras**: hora, luces, temperatura y humedad de 9 habitaciones, clima. Sin rv1/rv2 "
    "(ruido inyectado).",
    "Único candidato con **temperatura interior**: sin ella no hay penalización de confort."], NARANJA, tam=15)
tarjeta(s, C2, Y0, CW2, Cm(8.0), "Dos particiones, siempre", [
    "**Aleatoria 80/20** (semilla 42): dado el estado, ¿cuánto consume? Es la del curso.",
    "**Temporal**: entrena hasta el 30-abr y prueba en mayo ({t1:n_dias_tr} y {t1:n_dias_te} días): ¿generaliza a un "
    "mes que nunca vio?",
    "^^Decide la temporal^^: lecturas consecutivas casi idénticas filtran en la aleatoria (en KNN, K = 1 era el "
    "mejor)."], AZUL, tam=15)
tarjeta(s, MX, Y0 + Cm(8.5), CW, Cm(4.5), "Otras reglas fijas", [
    "Umbral de pico = percentil 90 del **entrenamiento** ({p2:part_umbral_wh}); calcularlo con todo filtraría mayo.",
    "Retardos (10, 20, 30 y 60 min antes) solo en la temporal; escalado e hiperparámetros solo con entrenamiento.",
    "Diferencias con **IC del 95 % por bootstrap pareado por día**: si incluye el cero, «no se distingue»."],
         INK2, tam=14.5)

# =====================================================================================================================
# 5 · Supervisado: el tablero se invierte
# =====================================================================================================================
s = diapositiva("sup", "El gemelo necesita una función de transición, y la partición temporal invierte el tablero",
                "La primera pieza es la función de transición: dado el estado de la casa ahora, cuánto consumirá en el "
                "paso siguiente. En la partición aleatoria gana la complejidad: LightGBM y Random Forest superan con "
                "amplitud a la regresión lineal. Pero en la temporal, la que decide, el orden se invierte por completo: "
                "la lineal es la única con R² positivo y Random Forest cae a menos cuatro, peor que un árbol solo. Con "
                "variables de retardo la lineal sube a {p2:her_bo_lineal_retardos_r2}. La lección es que precisión y "
                "robustez en el tiempo son ejes distintos, y a un gemelo que tiene que simular meses que no ha visto le "
                "importa el segundo.")
tabla(s, MX, Y0, Cm(19.4), ["Regresión del consumo (R²)", "Aleatoria", "Temporal", "Temporal + retardos"], [
    ["Regresión lineal", "{p2:her_reg_lineal_aleatoria_r2}", "^^{p2:her_reg_lineal_temporal_r2}^^",
     "^^{p2:her_bo_lineal_retardos_r2}^^"],
    ["Árbol de decisión", "{p2:her_reg_arbol_aleatoria_r2}", "{p2:her_reg_arbol_temporal_r2}", "—"],
    ["KNN (K = 5)", "{p2:her_reg_knn_aleatoria_r2}", "{p2:her_reg_knn_temporal_r2}", "—"],
    ["Random Forest", "{p2:her_reg_rf_aleatoria_r2}", "{p2:her_reg_rf_temporal_r2}", "{p2:her_bo_rf_retardos_r2}"],
    ["LightGBM", "**{p2:her_bo_lgbm_aleatoria_r2}**", "{p2:her_bo_lgbm_temporal_r2}", "{p2:her_bo_lgbm_retardos_r2}"],
    ["XGBoost", "{p2:her_bo_xgb_aleatoria_r2}", "{p2:her_bo_xgb_temporal_r2}", "{p2:her_bo_xgb_retardos_r2}"],
], [6.6, 3.8, 3.8, 5.2], tam=15, alto=1.25, acento=AZUL)
texto(s, MX, Y0 + Cm(9.0), Cm(19.4), Cm(1.4),
      ["Aleatoria: 80/20, semilla 42. Temporal: entrena hasta el 30-abr y prueba en mayo; los retardos solo se usan "
       "en ella."], tam=11.5, color=INK2)
xk = MX + Cm(20.4)
wk = CW - Cm(20.4)
_rect(s, xk, Y0, wk, Cm(9.0), PANEL)
kpi(s, xk + Cm(0.6), Y0 + Cm(0.5), wk - Cm(1.2), "{p2:her_reg_rf_aleatoria_r2} → {p2:her_reg_rf_temporal_r2}",
    "Random Forest: de la aleatoria a la temporal", ROJO, tam=34)
kpi(s, xk + Cm(0.6), Y0 + Cm(4.6), wk - Cm(1.2), "{p2:her_reg_lineal_temporal_r2} → {p2:her_bo_lineal_retardos_r2}",
    "Lineal en la temporal, sin y con retardos", AZUL, tam=34)
decision(s, MX, Y0 + Cm(10.5), CW, Cm(2.8),
         "Precisión y robustez temporal son ejes distintos. Al gemelo, que debe simular meses que no ha visto, le "
         "importa la segunda: ^^se decide con la partición temporal^^.")

# =====================================================================================================================
# 6 · Supervisado: por qué
# =====================================================================================================================
s = diapositiva("sup", "Los árboles no extrapolan: promedian el invierno y leen el calor como consumo",
                "¿Por qué colapsan los árboles? Primero, no extrapolan: Random Forest con retardos predice en mayo un "
                "consumo sostenidamente alto, con un sesgo medio de más de sesenta vatios hora, porque solo puede "
                "promediar lo que vio en invierno; la lineal, dominada por el consumo de hace diez minutos, predice el "
                "cambio y casi no tiene sesgo. Segundo, hay un confusor: en invierno las habitaciones más cálidas eran "
                "las de más consumo, porque parte de ese calor lo producen los aparatos. En mayo la casa está más "
                "cálida por dentro, y un árbol lee ese calor como consumo. Sin las temperaturas interiores, LightGBM "
                "pierde casi todo su sesgo; quitar el mes no lo arregla. Y el boosting, con retardos, solo iguala a la "
                "lineal con más error.")
tarjeta(s, X3[0], Y0, CW3, Cm(8.8), "Los retardos rinden", [
    "Lineal temporal: R² ^^{p2:her_reg_lineal_temporal_r2} → {p2:her_bo_lineal_retardos_r2}^^ con el consumo de 10–60 "
    "min antes.",
    "MAE {p2:her_bo_lineal_retardos_mae} · RMSE {p2:her_bo_lineal_retardos_rmse}.",
    "Ningún barrido de hiperparámetros se acercó."], AZUL, tam=15)
tarjeta(s, X3[1], Y0, CW3, Cm(8.8), "Los árboles no extrapolan", [
    "RF + retardos: R² **{p2:her_bo_rf_retardos_r2}**.",
    "Sesgo medio en mayo: **+{p2:her_reg_rf_retardos_sesgo}** frente a +{p2:her_reg_lineal_retardos_sesgo} de la "
    "lineal.",
    "Exterior: {p2:her_deriva_ene_tout} en enero, {p2:her_deriva_may_tout} en mayo."], ROJO, tam=15)
tarjeta(s, X3[2], Y0, CW3, Cm(8.8), "El confusor interior", [
    "En invierno, la habitación más cálida era la de **más consumo**: el calor lo ponían los aparatos.",
    "En mayo la casa está más cálida: el árbol **lee calor como consumo**.",
    "Sin temperaturas interiores, LightGBM pierde casi todo el sesgo; quitar el mes no basta."], AMBAR, tam=15)
decision(s, MX, Y0 + Cm(9.3), CW, Cm(4.0),
         "La función de transición es la ^^regresión lineal con retardos^^. La temperatura interior entra al MDP como "
         "variable de confort, no como predictor. LightGBM + retardos ({p2:her_bo_lgbm_retardos_r2}) iguala a la lineal "
         "({p2:her_bo_lineal_retardos_r2}) con más error ({p2:her_bo_lgbm_retardos_mae}): el boosting no la reemplaza.")

# =====================================================================================================================
# 7 · Supervisado: el gemelo no es un oráculo
# =====================================================================================================================
s = diapositiva("sup", "El gemelo no es un oráculo: frente a «repetir la última lectura»",
                "Antes de construir un agente encima, hay que saber cuánto vale el gemelo. Lo comparamos con lo más "
                "simple posible: repetir la última lectura. En error absoluto medio el gemelo pierde; en RMSE, que "
                "castiga los picos, gana. Y en las lecturas sobre el umbral los dos subestiman, el gemelo más. El "
                "error tampoco es parejo en el día: de madrugada es pequeño y en la mañana se multiplica. Eso tiene una "
                "consecuencia directa para Shiro: un agente entrenado sobre un simulador que abarata los picos "
                "aprendería a explotar un ahorro que no existe. Por eso el gemelo declara una incertidumbre que depende "
                "de la hora y se valida contra un mes reservado antes de que un agente entrene sobre él.")
tabla(s, MX, Y0, Cm(17.0), ["Mayo (partición temporal)", "Gemelo", "Repetir la última"], [
    ["MAE", "{p2:n1b_g3a_total_mae}", "**{p2:n1b_persistencia_total_mae}**"],
    ["RMSE", "**{p2:n1b_g3a_total_rmse}**", "{p2:n1b_persistencia_total_rmse}"],
    ["Sesgo en lecturas sobre el umbral", "{p2:n1b_g3a_altas_sesgo}", "{p2:n1b_persistencia_altas_sesgo}"],
], [8.4, 4.3, 4.3], tam=15, alto=1.3)
texto(s, MX, Y0 + Cm(5.5), Cm(17.0), Cm(2.6),
      ["En la consola corre una versión de **6 variables** (hora, luces, dos sensores, clima exterior y consumo "
       "actual): MAE {p3:sim6_mae_mayo} en mayo."], tam=14.5, color=INK2)
xk = MX + Cm(18.0)
wk = CW - Cm(18.0)
_rect(s, xk, Y0, wk, Cm(8.1), PANEL)
rotulo(s, xk + Cm(0.6), Y0 + Cm(0.45), wk - Cm(1), "MAE del gemelo por franja (mayo)", AZUL)
franjas = [("Madrugada", "{p2:n1b_g3a_madrugada_mae}"), ("Mañana", "{p2:n1b_g3a_manana_mae}"),
           ("Tarde", "{p2:n1b_g3a_tarde_mae}"), ("Noche", "{p2:n1b_g3a_noche_mae}")]
vmax = max(float(F(v).split()[0].replace(",", ".")) for _, v in franjas)
for i, (n_, v_) in enumerate(franjas):
    yb = Y0 + Cm(1.55) + i * Cm(1.6)
    val = float(F(v_).split()[0].replace(",", "."))
    texto(s, xk + Cm(0.6), yb + Cm(0.1), Cm(3.0), Cm(0.8), [n_], tam=14, color=INK2)
    largo = int((wk - Cm(7.6)) * val / vmax)
    _rect(s, xk + Cm(3.7), yb + Cm(0.1), largo, Cm(0.75), AZUL)
    texto(s, xk + Cm(3.9) + largo, yb + Cm(0.12), Cm(3.4), Cm(0.8), [v_], tam=14, color=INK)
decision(s, MX, Y0 + Cm(8.9), CW, Cm(3.3),
         "La incertidumbre del simulador es ^^función de la hora^^ y el gemelo se valida contra un mes reservado "
         "**antes** de que un agente entrene sobre él: un simulador que abarata los picos enseñaría a explotar un "
         "ahorro que no existe.")

# =====================================================================================================================
# 8 · Guardian: reconocer no es anticipar
# =====================================================================================================================
s = diapositiva("gua", "Guardian necesita avisar antes del pico: reconocer no es anticipar",
                "Aplazar una carga solo sirve si Guardian avisa antes de que el pico empiece. En el primer corte "
                "teníamos un detector que «detectaba» el {p2:ancla_det_detectados} de los picos. Al revisarlo vimos "
                "que contaba alertas que tocaban picos ya en curso: los avisos duraban más de una hora y media, en la "
                "mayoría de los picos con alerta previa la alerta ya venía encendida, y el umbral se había elegido "
                "mirando la prueba. Medido como lo que es, anticipar con al menos dos lecturas de antelación y con el "
                "mismo presupuesto de rojo, ese detector baja a {p2:n1c_det_mismo_r_p20}. A la derecha está el "
                "protocolo con el que se evaluó todo lo que sigue.")
_rect(s, MX, Y0, CW2, Cm(9.4), PANEL)
kpi(s, MX + Cm(0.7), Y0 + Cm(0.5), CW2 - Cm(1.4), "{p2:ancla_det_detectados}",
    "picos «detectados» por el detector del 1.er corte (Random Forest + retardos, umbral 0,40)", INK2, tam=44)
kpi(s, MX + Cm(0.7), Y0 + Cm(4.4), CW2 - Cm(1.4), "{p2:n1c_det_mismo_r_p20}",
    "los que de verdad **anticipa** con al menos dos lecturas (≥ 20 min), con el mismo tiempo en rojo que G0", AMBAR,
    tam=44)
tarjeta(s, C2, Y0, CW2, Cm(9.4), "Por qué la diferencia", [
    "Avisos de **{p2:her_det_duracion}** de media: tocaban picos ya en curso.",
    "En **{p2:n1c_antes_ya_encendida_n|n} de {p2:n1c_antes_n|n}** picos con alerta previa, la alerta ya venía "
    "encendida.",
    "Su umbral se eligió **mirando la prueba**."], AMBAR, tam=15)
tarjeta(s, MX, Y0 + Cm(9.9), CW, Cm(3.4), "Protocolo de Guardian", [
    "Pico: lecturas > {p2:part_umbral_wh} separadas por menos de 30 min. Ajuste en el 85 % inicial del entrenamiento; "
    "cortes en el 15 % final ({p2:def_picos_validacion}); se reporta mayo ({p2:def_picos_prueba}).",
    "Mismo **presupuesto** de rojo para todos ({p2:def_tasa_base_r} de la calma). Listones: la regla de nivel y el "
    "azar."], INK2, tam=13.5, espacio=3)

# =====================================================================================================================
# 9 · Guardian: G0
# =====================================================================================================================
s = diapositiva("gua", "Para anticipar basta lo simple: G0, un modelo de dos variables",
                "G0 tiene dos variables: el consumo actual y la frecuencia histórica de picos a esa hora, en día "
                "laborable o de fin de semana; son cuarenta y ocho celdas. Ganó la selección en validación, y en prueba "
                "ningún modelo de {p2:part_n_variables} variables se distingue de él: el mejor suma apenas un punto, con "
                "un intervalo que cruza el cero. Desplegado con los cortes de validación, avisa {p2:titular_n20|n} de "
                "los {p2:def_picos_prueba|n} picos de mayo con al menos dos lecturas de antelación. Con ese mismo tiempo "
                "en rojo, la regla de nivel avisa {p2:titular_m20|n}: la ventaja de G0 no es concluyente, y lo decimos. "
                "El costo es alto: cerca de dos horas al día en rojo y seis de cada diez avisos falsos.")
figura(s, F_G2, MX, Y0, Cm(16.2), Cm(11.9))
xr = MX + Cm(17.0)
wr = CW - Cm(17.0)
_rect(s, xr, Y0, wr, Cm(3.6), PANEL)
kpi(s, xr + Cm(0.6), Y0 + Cm(0.35), wr - Cm(1.2), "{p2:titular_n20|n} de {p2:def_picos_prueba|n} picos",
    "avisados con al menos dos lecturas (≥ 20 min) de antelación: **{p2:titular_p20}**", AMBAR, tam=36)
tarjeta(s, xr, Y0 + Cm(3.9), wr, Cm(5.2), "Desplegado en mayo", [
    "**{p2:titular_min_dia}** en rojo ({p2:titular_rojo_pct} de la calma) · {p2:titular_avisos_dia}.",
    "**{p2:titular_falsos}** de avisos falsos.",
    "Regla de nivel al mismo rojo: {p2:titular_m20|n} picos; ventaja +{p2:titular_d_regla} (IC "
    "{p2:titular_d_regla_ic_inf|n} a {p2:titular_d_regla_ic_sup|n}: no concluyente). Azar: {p2:azar_p20_desplegado}."],
         AMBAR, tam=13.5, espacio=3)
tarjeta(s, xr, Y0 + Cm(9.4), wr, Cm(2.6), "Selección", [
    "Gana en validación ({p2:g0_val_p20}); el mejor de {p2:part_n_variables} variables suma +{p2:caso_otro_d} (IC "
    "{p2:caso_otro_ic_inf|n} a {p2:caso_otro_ic_sup|n})."], INK2, tam=13.5)
texto(s, MX, Y0 + Cm(12.2), CW, Cm(1.0),
      ["G0 = consumo actual + frecuencia histórica de picos por hora, en laborable o fin de semana (48 celdas)."],
      tam=13, color=INK2)

# =====================================================================================================================
# 10 · Guardian: deriva y alcance
# =====================================================================================================================
s = diapositiva("gua", "Lo simple deriva menos, la validación es optimista y el aviso toca poco",
                "Tres matices antes de cerrar Guardian. Los bosques derivan más que lo simple: con los cortes de abril, "
                "en mayo quedan en rojo un tercio o más del tiempo en calma, frente a menos del diez por ciento de G0; "
                "sin las temperaturas de las habitaciones la deriva baja mucho, el mismo confusor de antes. La "
                "validación es optimista: G0 anticipa el {p2:g0_val_p20} en validación y el {p2:g0_prueba_p20} en "
                "prueba con el mismo presupuesto. Y lo que un aviso puede tocar es acotado: solo el "
                "{p2:energia_exceso_anticipado_pct} del exceso de mayo cae en picos avisados a tiempo. El resto exige "
                "saber qué aparato se enciende.")
tarjeta(s, X3[0], Y0, CW3, Cm(8.6), "Los bosques derivan", [
    "Rojo realizado en mayo con cortes de abril: bosque que reconoce **{p2:g1_desp_rojo_pct}**, que anticipa "
    "**{p2:g4_desp_rojo_pct}**; G0, ^^{p2:g0_desp_rojo_pct}^^.",
    "Sin temperaturas interiores: {p2:deriva_g1_sin_tint_rojo} y {p2:deriva_g4_sin_tint_rojo}."], AMBAR, tam=14.5)
tarjeta(s, X3[1], Y0, CW3, Cm(8.6), "La validación es optimista", [
    "G0: **{p2:g0_val_p20}** en validación y **{p2:g0_prueba_p20}** en prueba, con el mismo presupuesto.",
    "Decil más alto de la calibración: {p2:cal_decil10_tasa_val} frente a {p2:cal_decil10_tasa_prueba}."], AMBAR,
         tam=14.5)
tarjeta(s, X3[2], Y0, CW3, Cm(8.6), "El aviso toca poco", [
    "Solo el ^^{p2:energia_exceso_anticipado_pct}^^ del exceso de mayo ({p2:energia_exceso_anticipado_kwh} de "
    "{p2:energia_exceso_kwh}) cae en picos avisados con ≥ 20 min.",
    "El resto exige saber **qué aparato** se enciende."], AMBAR, tam=14.5)
decision(s, MX, Y0 + Cm(9.1), CW, Cm(4.2),
         "El anticipador de Guardian es ^^G0^^: exportable, explicable y capaz de correr en la página y en el hogar. Se "
         "evalúa por antelación y con el mismo tiempo en rojo, nunca por «evento tocado»; su probabilidad lleva rango y "
         "se recalibra cada mes.")

# =====================================================================================================================
# 11 · No supervisado: tipos de día
# =====================================================================================================================
s = diapositiva("nos", "El estado necesita contexto: K-Means encuentra dos tipos de día",
                "La tercera pieza es el contexto: ¿hoy es un día de mucho consumo? Representamos cada día por sus "
                "veinticuatro consumos medios horarios, sin estandarizar. Las tres métricas coinciden en k igual a dos: "
                "el codo, la silueta y el índice de Dunn. Aparecen un día normal y un día de carga alta, con un bloque "
                "diurno de consumo y jorobas a media mañana y en la tarde. Lo interesante es lo que no los explica: el "
                "fin de semana no tiene ninguna asociación y el mes tampoco. Las madrugadas son iguales; la diferencia "
                "aparece de día, y eso va a importar en la siguiente diapositiva.")
figura(s, FIG / "A2_tipos_dia.png", MX, Y0, Cm(18.8), Cm(11.8))
xr = MX + Cm(19.6)
wr = CW - Cm(19.6)
_rect(s, xr, Y0, wr, Cm(5.0), PANEL)
kpi(s, xr + Cm(0.6), Y0 + Cm(0.35), (wr - Cm(1.5)) // 2, "{c2:km_n_normal|n}", "días normales · {c2:km_kwh_normal}",
    TEAL, tam=40)
kpi(s, xr + Cm(0.6) + (wr - Cm(1.2)) // 2, Y0 + Cm(0.35), (wr - Cm(1.5)) // 2, "{c2:km_n_alta|n}",
    "días de carga alta · {c2:km_kwh_alta}", ROSA, tam=40)
tarjeta(s, xr, Y0 + Cm(5.3), wr, Cm(6.5), "Por qué k = 2", [
    "Codo: {c2:km_caida_inercia} menos de inercia de 1 a 2 grupos.",
    "Silueta **{c2:km_silueta}** (k = 3: {c2:km_silueta_k3}); Dunn {c2:km_dunn}, el máximo.",
    "^^El calendario no lo explica^^: V de Cramér con el fin de semana {c2:km_cramer_finde}; con el mes "
    "{c2:km_cramer_mes} (p = {c2:km_p_mes})."], TEAL, tam=14.5)

# =====================================================================================================================
# 12 · No supervisado: real y observable
# =====================================================================================================================
s = diapositiva("nos", "¿Es real o un artefacto de K-Means? ¿Y cuándo se sabe en el día?",
                "Antes de meter el tipo de día al estado había que saber si es real. El agrupamiento jerárquico con "
                "Ward coincide con K-Means en casi todos los días, y los desacuerdos están todos junto a la frontera: "
                "el tipo es real, pero de frontera difusa, así que el margen al centroide sirve como confianza. Hubo una "
                "trampa: el enlace promedio tiene la mejor silueta aislando un solo día; por eso k nunca se elige solo "
                "por la métrica. La estabilidad decidió los papeles: sin mayo, K-Means reproduce el mismo reparto y Ward "
                "no. Y lo más útil para Shiro: a las ocho de la mañana todavía no se sabe qué día es; hacia el mediodía "
                "sí, a tiempo para la joroba de la tarde.")
tarjeta(s, X3[0], Y0, CW3, Cm(8.8), "Real, de frontera difusa", [
    "Ward coincide con K-Means en **{c2:ward_coinciden}** días (ARI {c2:ward_ari_kmeans}).",
    "Los {c2:ward_cambian_kmeans|n} desacuerdos están junto a la frontera: el **margen** es la confianza.",
    "Trampa: el enlace promedio tiene la mejor silueta ({c2:avg_silueta}) aislando **un solo día**."], TEAL, tam=14.5)
tarjeta(s, X3[1], Y0, CW3, Cm(8.8), "Estable sin mayo", [
    "Ajustado sin mayo, K-Means da el mismo reparto (ARI ^^{c2:estab_ari_kmeans}^^); Ward no "
    "({c2:estab_ari_ward}).",
    "**K-Means asigna** en producción; el jerárquico audita en cada reentrenamiento."], TEAL, tam=14.5)
tarjeta(s, X3[2], Y0, CW3, Cm(8.8), "Se revela de día", [
    "A las 8 h la curva parcial acierta {c2:km_obs_8h_acierto}: menos que decir siempre «normal» "
    "({c2:km_obs_8h}).",
    "A las 12 h reconoce ^^{c2:km_obs_12h}^^ de los días de carga alta.",
    "Mayo: {c2:km_mayo_fuera_p95} días fuera del p95; carga alta {c2:km_alta_tr} → {c2:km_alta_te}."], TEAL,
         tam=14.5)
decision(s, MX, Y0 + Cm(9.3), CW, Cm(4.0),
         "El tipo de día entra al estado como ^^estimación que se actualiza durante el día^^, con su margen al centroide "
         "como confianza. K-Means lo asigna y Ward lo audita cada mes: si dejan de coincidir, la definición de día está "
         "cambiando.")

# =====================================================================================================================
# 13 · No supervisado: DBSCAN
# =====================================================================================================================
s = diapositiva("nos", "DBSCAN busca lo que no encaja: rareza en contexto, no magnitud",
                "DBSCAN mira lo que no encaja. Con un solo radio deja como ruido a todos los días de carga alta; "
                "separando por tipo se ve que un día de carga alta es más de dos veces más disperso que uno normal. Los "
                "días atípicos, muchos de enero, se marcan pero no se borran, y en mayo hay dos días sin vecinos en la "
                "historia: un día desconocido pide una política conservadora. Sobre lecturas, con un DBSCAN por franja, "
                "de madrugada ve consumos raros que están por debajo del umbral, como un aparato olvidado encendido; en "
                "la tarde casi no marca lo que el umbral marca por rutina. Ve rareza en contexto, no magnitud. Y "
                "ninguna definición de anomalía es inmune a la estación.")
tarjeta(s, C1, Y0, CW2, Cm(8.8), "Días", [
    "Carga alta: radio {c2:db_eps_alta}, ^^{c2:db_ratio_eps}^^ el del día normal ({c2:db_eps_normal}).",
    "**{c2:db_atipicos}** atípicos robustos ({c2:db_atipicos_pct}; {c2:db_atipicos_enero} de enero): se marcan, no "
    "se borran.",
    "Mayo: **{c2:db_mayo_desconocidos}** días sin vecinos densos → política conservadora."], TEAL, tam=15)
tarjeta(s, C2, Y0, CW2, Cm(8.8), "Lecturas, un DBSCAN por franja", [
    "De madrugada, el **{c2:db_madrugada_bajo200}** de su ruido está bajo {c2:db_umbral_wh}: ve lo que el umbral no "
    "ve.",
    "En la tarde solo marca el {c2:db_tarde_marca} de lo que supera el umbral.",
    "Mayo: DBSCAN marca {c2:db_mayo_caida} y el umbral fijo {c2:umbral_mayo_caida}: **nada es inmune a la "
    "estación**."], TEAL, tam=15)
decision(s, MX, Y0 + Cm(9.3), CW, Cm(4.0),
         "Guardian tendrá una ^^segunda alarma por rareza^^ (DBSCAN por franja, solo en subidas), pendiente de evaluar "
         "con el mismo protocolo que G0. La incertidumbre del simulador depende del tipo de día además de la franja, y "
         "todo umbral se recalibra cada mes.")

# =====================================================================================================================
# 14 · Refuerzo: el MDP
# =====================================================================================================================
s = diapositiva("ref", "La pieza que decide: el MDP de Shiro",
                "Con transición, contexto y aviso, falta la pieza que decide. El paso es de una hora. El estado "
                "combina el tipo de día estimado, la franja, el nivel de consumo y si hay una carga esperando: "
                "{t1:n_estados} estados. Las acciones son no actuar, aplazar parte del pico hasta el valle y ejecutar "
                "lo pendiente. La recompensa cobra la energía por la tarifa y penaliza la espera con lambda, que mide "
                "cuánto le cuesta esperar a la persona. Un detalle importante: en el código de ejemplo del curso la "
                "transición no dependía de la acción, así que la mejor política era simplemente la codiciosa. Para "
                "Shiro la acción tiene que cambiar el futuro, y por eso existe el estado «carga pendiente». La tarifa "
                "con punta uno coma cinco es un supuesto de diseño.")
tarjeta(s, MX, Y0, Cm(15.6), Cm(6.0), "Estado ({t1:n_estados} combinaciones)", [
    "**Tipo de día** estimado (K-Means sobre la curva parcial).",
    "**Franja** del día y **nivel** de consumo: bajo 60 Wh, medio o sobre el umbral.",
    "**Carga pendiente**: si hay algo aplazado esperando."], ROSA, tam=15)
tarjeta(s, MX, Y0 + Cm(6.4), Cm(15.6), Cm(6.0), "Acciones", [
    "**No actuar**.",
    "**Aplazar** el 40 % del exceso (ΔE = {t1:DE}) hasta el valle, si el nivel es alto y hay cupo.",
    "**Ejecutar** lo pendiente."], ROSA, tam=15)
xr = MX + Cm(16.3)
wr = CW - Cm(16.3)
_rect(s, xr, Y0, wr, Cm(4.3), PANEL2)
rotulo(s, xr + Cm(0.6), Y0 + Cm(0.45), wr - Cm(1), "Recompensa", ROSA)
texto(s, xr + Cm(0.6), Y0 + Cm(1.25), wr - Cm(1.2), Cm(1.4), ["r = −c(t)·E − λ·w"], tam=30, fuente=T_TIT)
texto(s, xr + Cm(0.6), Y0 + Cm(2.75), wr - Cm(1.2), Cm(1.4),
      ["c: tarifa (valle 1,0 · punta 1,5, supuesto) · E: energía cobrada · w = 1 si hay carga esperando · λ: cuánto "
       "le cuesta esperar a la persona"], tam=12.5, color=INK2)
tarjeta(s, xr, Y0 + Cm(4.6), wr, Cm(3.6), "Entorno", [
    "Réplica de días reales: transiciones contadas hasta el 30-abr y la acción mueve la carga; γ = 0,95."],
         INK2, tam=14)
tarjeta(s, xr, Y0 + Cm(8.5), wr, Cm(3.9), "Lo que corregimos del ejemplo", [
    "En el código del curso P(s′|s) no dependía de la acción → la «óptima» era la codiciosa. En Shiro la acción "
    "**cambia el futuro**."], AMBAR, tam=14)

# =====================================================================================================================
# 15 · Refuerzo: lo que enseñó el MDP
# =====================================================================================================================
s = diapositiva("ref", "Lo que enseñó el MDP: aplazar no es ahorrar, y λ decide la política",
                "Resolver el MDP con iteración de valor dejó tres lecciones. Primera: si la energía aplazada se cobra "
                "completa al ejecutarla, el descuento hace que aplazar un costo parezca ahorrarlo; con tarifa plana el "
                "agente aplazaba y nunca ejecutaba. Con la contabilidad corregida eso desaparece. Segunda: con una "
                "persona paciente la política óptima es una regla fija, aplazar en punta y ejecutar de madrugada, y en "
                "mayo ahorra el {t1:ahorro_opt_te} del costo, que no se distingue de no hacer nada. Tercera: con una "
                "persona exigente la política cambia en {t1:ex_n_difs} estados y cambia ahorro por espera. Lambda no es "
                "un hiperparámetro nuestro: es un control de la persona.")
tarjeta(s, X3[0], Y0, CW3, Cm(8.8), "Contabilidad corregida", [
    "Cobrar todo al ejecutar + descuento = aplazar **parece** ahorrar: con tarifa plana la carga espera "
    "**{t1:cordura_ingenua_1p0_espera}**.",
    "Corregida (valle al aplazar, sobrecosto al ejecutar): con tarifa plana aplaza en "
    "^^{t1:cordura_corregida_1p0_nap}^^ estados."], ROSA, tam=14.5)
tarjeta(s, X3[1], Y0, CW3, Cm(8.8), "Persona paciente · λ = 0,005", [
    "π* = la codiciosa = una regla fija: aplazar en punta, ejecutar de madrugada.",
    "Mayo: ahorra ^^{t1:ahorro_opt_te}^^ con **{t1:espera_opt_te}** de espera.",
    "Frente a no actuar: {t1:boot_no_te} → no se distingue."], ROSA, tam=14.5)
tarjeta(s, X3[2], Y0, CW3, Cm(8.8), "Persona exigente · λ = 0,02", [
    "π* cambia en **{t1:ex_n_difs} de {t1:n_estados}** estados: no aplaza en la mañana (valle a "
    "{t1:horas_valle_x_0-1-2}).",
    "Ahorro {t1:ex_ahorro_opt_te} con {t1:ex_espera_opt_te}.",
    "La tarde se decide por milésimas (ΔQ +{t1:ex_dQ_0-2-2-0} / {t1:ex_dQ_1-2-2-0}) → **dudosa**."], ROSA, tam=14.5)
decision(s, MX, Y0 + Cm(9.3), CW, Cm(4.0),
         "El entorno conserva la ^^contabilidad corregida^^ y el estado «carga pendiente». ^^λ es un control de la "
         "persona^^ y la política se recalcula para cada valor; las decisiones por milésimas se muestran como dudosas.")

# =====================================================================================================================
# 16 · Refuerzo: Q-learning
# =====================================================================================================================
s = diapositiva("ref", "Q-learning: en una casa nueva no hay modelo, hay que aprender probando",
                "En una casa real Shiro no tendrá la tabla de transiciones: tendrá que aprender de la experiencia. "
                "¿Cuánta necesita? Las diferencias entre acciones son de centésimas, mucho menores que el error de los "
                "valores Q con una tasa de aprendizaje fija. Con los hiperparámetros del ejemplo del curso, Q-learning "
                "captura solo el {t2:prof_captura} del ahorro posible. Con una tasa decreciente llega al "
                "{t2:base_captura}, pero necesita {t2:n_ep_rec} días: unos {t2:anos_rec} de experiencia real. Además, el "
                "agente miope aprende mejor que el paciente, la definición de estado del proyecto le gana a cuantiles y "
                "a K-Means, y tres recompensas quedan prohibidas: pagar por actuar crea un Shiro nervioso, castigar "
                "cualquier pérdida uno miedoso.")
tarjeta(s, C1, Y0, CW2, Cm(7.6), "¿Cuánta experiencia?", [
    "Brecha entre acciones: mediana **{t2:brecha_med}** (de {t2:brecha_min|n} a {t2:brecha_max}); error de Q con "
    "α = 0,1: **{t2:prof_errq}**.",
    "α fijo, {t2:n_ep} días: captura **{t2:prof_captura}** del ahorro de π*.",
    "α decreciente, {t2:n_ep_rec} días: ^^{t2:base_captura}^^, pero ≈ **{t2:anos_rec}** de casa real."], ROSA,
         tam=14.5)
tarjeta(s, C2, Y0, CW2, Cm(7.6), "Horizonte, estado y estación", [
    "Miope (γ = 0,5) captura **{t2:g0p5_captura}**; paciente (γ = 0,99) {t2:g0p99_captura}.",
    "Ahorro de π* según el estado: cuantiles {t2:p3vi_qcut_ahorro}, K-Means {t2:p3vi_kmeans_ahorro}, umbral "
    "^^{t2:p3vi_umbral_ahorro}^^.",
    "π* de invierno = π* de mayo en {t2:p1_iguales_vi|n} de {t2:p1_decision_comunes|n} decisiones: se transfiere."],
         ROSA, tam=14.5)
rotulo(s, MX, Y0 + Cm(8.0), CW, "Recompensas prohibidas", ROJO)
prohib = [("+1 por actuar → «Shiro nervioso»", "{t2:p4_trans_aplaz} aplazamientos al día, ahorro {t2:p4_trans_ahorro}."),
          ("−1000 si pierde → «Shiro miedoso»", "{t2:p4_miedo_aplaz} aplazamientos al día: nunca propone."),
          ("Contabilidad ingenua", "Espera {t2:p4_ing_espera} (base {t2:base_espera}), ahorro {t2:p4_ing_ahorro}.")]
for i, (t_, d_) in enumerate(prohib):
    x = X3[i]
    _rect(s, x, Y0 + Cm(8.8), CW3, Cm(4.5), PANEL)
    _rect(s, x, Y0 + Cm(8.8), Cm(0.13), Cm(4.5), ROJO)
    texto(s, x + Cm(0.6), Y0 + Cm(9.2), CW3 - Cm(1), Cm(1.9), [t_], tam=15.5, fuente=T_TIT)
    texto(s, x + Cm(0.6), Y0 + Cm(11.0), CW3 - Cm(1), Cm(2.1), [d_], tam=14, color=INK2)

# =====================================================================================================================
# 17 · Refuerzo: recompensa centrada
# =====================================================================================================================
s = diapositiva("ref", "La recompensa centrada: de {t3:ql_dias80} a {t3:qlc_dias80} de experiencia",
                "El arranque en frío no era culpa de la tabla: era ruido de la recompensa. El término de lo que la casa "
                "consume no depende de la acción y domina la señal. La recompensa centrada lo quita y deja solo lo que "
                "la acción cambia; como lo que se quita no depende de la acción, la política óptima es la misma. Con "
                "ella, el mismo Q-learning de tabla captura al menos el ochenta por ciento del ahorro desde el día "
                "{t3:qlc_dias80|n} de experiencia simulada, en las cinco semillas, y termina igualando a la política "
                "óptima. Con la recompensa original necesitaba {t3:ql_dias80}. Es el hallazgo más importante del "
                "refuerzo para Shiro: el arranque en una casa pasa de décadas a meses, aunque todavía sin medir en una "
                "casa real.")
figura(s, FIG / "A4_arranque_frio.png", MX, Y0, Cm(19.2), Cm(8.3))
xr = MX + Cm(20.0)
wr = CW - Cm(20.0)
_rect(s, xr, Y0, wr, Cm(8.3), PANEL2)
rotulo(s, xr + Cm(0.6), Y0 + Cm(0.45), wr - Cm(1), "Recompensa centrada", ROSA)
texto(s, xr + Cm(0.6), Y0 + Cm(1.25), wr - Cm(1.2), Cm(1.3), ["r̃ = r + c(t)·E casa"], tam=26, fuente=T_TIT)
texto(s, xr + Cm(0.6), Y0 + Cm(2.75), wr - Cm(1.2), Cm(5.4), [
    "Aplazar: (c − 1)·ΔE − λ",
    "Ejecutar: −(c − 1)·ΔE",
    "No actuar: −λ si hay carga esperando",
    "Lo quitado no depende de la acción: **π* no cambia**."], tam=14, color=INK2, vinetas=True, acento=ROSA, espacio=4)
tabla(s, MX, Y0 + Cm(8.7), CW, ["Agente (mayo, persona paciente)", "Ahorro (%)", "De π* (%)", "Espera (h/día)",
                                "Días hasta 80 %"], [
    ["π* (iteración de valor)", "{t3:vi_ahorro_te|n}", "ref.", "{t3:vi_espera_te|n}", "—"],
    ["Q-learning, recompensa original", "{t3:ql_ahorro|n}", "{t3:ql_captura|n}", "{t3:ql_espera|n}", "{t3:ql_dias80|n}"],
    ["Q-learning, recompensa centrada", "{t3:qlc_ahorro|n}", "{t3:qlc_captura|n}", "{t3:qlc_espera|n}",
     "{t3:qlc_dias80|n}"],
    ["DQN", "{t3:dqn_ahorro|n}", "{t3:dqn_captura|n}", "{t3:dqn_espera|n}", "{t3:dqn_dias80|n}"],
], [11.5, 4.5, 4.4, 5.0, 5.4], tam=13.5, alto=0.92, acento=ROSA, resaltar=(2,))

# =====================================================================================================================
# 18 · Refuerzo: DQN
# =====================================================================================================================
s = diapositiva("ref", "La red ve la hora exacta, y sin sus dos trucos no aprende",
                "La red DQN captura el {t3:dqn_captura} del ahorro posible y su semilla mediana decide igual que la "
                "política óptima en todo mayo; Double DQN no mejora. Lo nuevo es que ve la hora exacta, que la tabla "
                "agrupaba en franjas. Con una persona exigente la red aplaza solo desde las {t3:e4_ex_desde}: la teoría "
                "dice que aplazar compensa a partir de las {t3:e4_ex_hora_teorica}, y la red elige la primera hora "
                "entera después. Abajo, la ablación: sin memoria de experiencias o sin red objetivo aprende peor, y sin "
                "ninguna de las dos hay semillas que no ahorran nada. Para Shiro la conclusión es práctica: con "
                "cuarenta estados basta la tabla; la red se justifica por el estado que viene, con la hora exacta, la "
                "probabilidad de G0 y el clima.")
figura(s, F_T4H, MX, Y0, Cm(16.8), Cm(12.0))
xr = MX + Cm(17.6)
wr = CW - Cm(17.6)
tarjeta(s, xr, Y0, wr, Cm(4.4), "DQN · {t3:n_rasgos} rasgos → 64 → 64 → 3", [
    "Captura ^^{t3:dqn_captura}^^ del ahorro de π*; la semilla mediana decide igual en todo mayo.",
    "Double DQN: {t3:ddqn_captura}."], ROSA, tam=14)
tarjeta(s, xr, Y0 + Cm(4.7), wr, Cm(3.4), "La hora exacta (λ = 0,02)", [
    "Aplaza desde las **{t3:e4_ex_desde}**; teoría: {t3:sobrecosto_kwh} / λ = {t3:e4_ex_umbral_h} antes del valle → "
    "{t3:e4_ex_hora_teorica}."], ROSA, tam=14)
tarjeta(s, xr, Y0 + Cm(8.4), wr, Cm(3.6), "Ablación", [
    "Sin memoria: {t3:sinr_captura} (peor semilla {t3:sinr_ahorro_min}) · sin red objetivo: {t3:sint_captura}.",
    "Sin ninguno: **{t3:sina_captura}**, espera {t3:sina_espera}."], ROJO, tam=14)
texto(s, MX, Y0 + Cm(12.25), CW, Cm(1.0),
      ["→ En Shiro Twin propone **π***, exacta y explicable para cada λ; Q-learning y la red verifican."], tam=14,
      color=VERDE)

# =====================================================================================================================
# 19 · Prototipo: la consola
# =====================================================================================================================
s = diapositiva("pro", "La consola de Shiro: los tres aprendizajes en una sola página",
                "Faltaba un criterio de cierre del proyecto: ver el entorno funcionando de principio a fin. La consola "
                "es una página HTML que funciona sin internet y sin librerías, con los datos de mayo incluidos. Una sola "
                "elección de día y hora alimenta cinco pantallas, y todo se calcula en el navegador: la predicción "
                "lineal y el semáforo de G0, el tipo de día con K-Means, la política óptima recalculada con la paciencia "
                "y la tarifa que elija la persona, la red DQN ejecutándose en la página, preguntas respondidas con "
                "plantillas que citan cifras reales, y una ficha del modelo con sus límites. Nada se ejecuta sin que la "
                "persona lo apruebe.")
figura(s, FIG / "consola_captura.png", MX, Y0, Cm(17.8), Cm(12.4), fondo=LINEA, pad=0.08)
xr = MX + Cm(18.6)
wr = CW - Cm(18.6)
pantallas = [("Hoy en casa", "supervisado", "Curva del día, predicción a un paso, semáforo de G0 y «¿y si…?».", AZUL),
             ("¿Qué tipo de día es?", "no supervisado", "K-Means sobre la curva parcial, margen y bandera de DBSCAN.",
              TEAL),
             ("¿Qué haría Shiro?", "refuerzo", "π* recalculada con tu λ y tu tarifa; Q-learning y la red, al lado.",
              ROSA),
             ("Pregúntale a Shiro", "los tres", "Respuestas por plantilla con cifras reales, sin modelo de lenguaje.",
              NARANJA),
             ("Ficha del modelo", "límites", "Las dos particiones, intervalos y lo que no funciona.", INK2)]
for i, (t_, p_, d_, c_) in enumerate(pantallas):
    y = Y0 + i * Cm(2.5)
    _rect(s, xr, y, wr, Cm(2.25), PANEL)
    _rect(s, xr, y, Cm(0.13), Cm(2.25), c_)
    texto(s, xr + Cm(0.55), y + Cm(0.25), wr - Cm(0.9), Cm(0.8), [f"^^{t_}^^  ·  {p_}"], tam=14, acento=c_,
          color=INK2)
    texto(s, xr + Cm(0.55), y + Cm(1.0), wr - Cm(0.9), Cm(1.2), [d_], tam=12.5, color=INK2)

# =====================================================================================================================
# 20 · Prototipo: demo y verificación
# =====================================================================================================================
s = diapositiva("pro", "Demo en vivo, y cómo sabemos que la página calcula bien",
                "Para la demo abrimos Consola_Shiro.html; arranca el sábado veintiuno de mayo a las doce, una hora con "
                "pico. En «Hoy en casa» se ve el semáforo de G0 y la predicción; movemos las luces o la temperatura "
                "exterior en el «¿y si…?». En «¿Qué tipo de día es?» la curva de la mañana ya se parece a carga alta, "
                "con su margen. En «¿Qué haría Shiro?» los tres agentes coinciden en aplazar; movemos la paciencia y la "
                "tarifa y la política se recalcula en el momento. Cerramos preguntándole a Shiro por qué. ¿Cómo sabemos "
                "que la página no inventa? Un verificador compara la iteración de valor en JavaScript con la de Python en "
                "{p3:n_rejilla_vi} combinaciones, y la red y K-Means contra sus valores de referencia.")
pasos = [("1", "Abrir **Consola_Shiro.html**: arranca el sábado 21 de mayo a las 12:00, una hora con pico."),
         ("2", "**Hoy en casa**: semáforo de G0 y predicción a un paso; mover luces y temperatura en «¿y si…?»."),
         ("3", "**¿Qué tipo de día es?**: la mañana ya se parece a carga alta, con su margen."),
         ("4", "**¿Qué haría Shiro?**: los tres agentes proponen aplazar; mover λ y la tarifa y ver la política "
               "recalculada."),
         ("5", "**Pregúntale a Shiro** por qué aplaza; cerrar en la **Ficha del modelo**.")]
rotulo(s, MX, Y0, Cm(18), "Guion de la demo (≈ 3 min)", NARANJA)
for i, (n_, d_) in enumerate(pasos):
    y = Y0 + Cm(0.9) + i * Cm(2.35)
    _rect(s, MX, y, Cm(1.3), Cm(1.3), NARANJA, forma=MSO_SHAPE.OVAL)
    texto(s, MX, y + Cm(0.17), Cm(1.3), Cm(1.0), [n_], tam=17, fuente=T_TIT, color=BG, alin=PP_ALIGN.CENTER)
    texto(s, MX + Cm(1.8), y + Cm(0.05), Cm(16.6), Cm(2.2), [d_], tam=15, color=INK2)
xr = MX + Cm(19.2)
wr = CW - Cm(19.2)
tarjeta(s, xr, Y0, wr, Cm(7.4), "Verificación antes de publicar", [
    "La iteración de valor en JavaScript da la **misma política que Python** en las {p3:n_rejilla_vi} combinaciones "
    "de λ y tarifa.",
    "La red DQN y el margen de K-Means coinciden con sus valores de referencia.",
    "Se puede ver en la propia página: **#prueba**."], VERDE, tam=14.5)
tarjeta(s, xr, Y0 + Cm(7.8), wr, Cm(5.1), "Una sola fuente de cifras", [
    "Consola, artículo y estas diapositivas leen los mismos archivos de resultados de cada taller.",
    "Si una cifra no sale de ahí, la generación falla."], VERDE, tam=14.5)

# =====================================================================================================================
# 21 · Límites
# =====================================================================================================================
s = diapositiva("lim", "Lo que todavía no sabemos, dicho de frente",
                "Cuatro límites que preferimos decir nosotros. El ahorro es pequeño y simulado: el {t1:ahorro_opt_te} "
                "en mayo, que no se distingue de no hacer nada, medido en la réplica de días reales y no sobre el "
                "gemelo. Es una sola casa, en invierno y primavera: la definición misma de anomalía envejece de enero a "
                "mayo, así que todo se recalibra cada mes. Falta saber qué aparato se enciende: ese es el techo real, no "
                "los hiperparámetros. Y la tarifa con punta era un supuesto de diseño: en un hogar colombiano habría "
                "que partir de la tarifa real. Sobre la ética: Shiro solo propone, la persona fija su paciencia y ve "
                "cuánto tiempo pasa en alerta. Con seis de cada diez avisos falsos, el riesgo real es que la persona "
                "deje de mirar.")
lims = [("El ahorro es pequeño y simulado", "Aplazar ahorra **{t1:ahorro_opt_te}** en mayo y no se distingue de no "
         "actuar; se midió en la réplica, no sobre el gemelo.", ROJO),
        ("Una casa, sin verano", "El percentil 90 mensual cae de **{p2:her_deriva_ene_p90}** a "
         "**{p2:her_deriva_may_p90}**: umbral, cortes y tipos de día se recalibran cada mes; falta otra vivienda.", ROJO),
        ("Falta saber qué aparato", "Solo el **{p2:energia_exceso_anticipado_pct}** del exceso cae en picos avisados a "
         "tiempo: ningún sensor ambiental distingue «horno y secadora a la vez».", ROJO),
        ("La tarifa era un supuesto", "Punta ×1,5 y valle 1,0 son de diseño; en un hogar colombiano habría que partir "
         "de la tarifa real.", ROJO)]
for i, (t_, d_, c_) in enumerate(lims):
    x = C1 if i % 2 == 0 else C2
    y = Y0 + (i // 2) * Cm(4.1)
    tarjeta(s, x, y, CW2, Cm(3.8), t_, [d_], c_, tam=14.5, vinetas=False)
_rect(s, MX, Y0 + Cm(8.5), CW, Cm(4.8), PANEL2)
_rect(s, MX, Y0 + Cm(8.5), Cm(0.13), Cm(4.8), VERDE)
rotulo(s, MX + Cm(0.6), Y0 + Cm(8.9), CW, "Ética: la persona decide", VERDE)
texto(s, MX + Cm(0.6), Y0 + Cm(9.7), CW - Cm(1.2), Cm(3.4), [
    "Shiro Twin **solo propone**: la persona aprueba o rechaza cada aplazamiento, fija λ y ve cuánto tiempo pasa el "
    "sistema en alerta.",
    "Un pico no avisado es recuperable; con **{p2:titular_falsos}** de avisos falsos, el riesgo es que la persona deje "
    "de mirar.",
    "La explicación usa lo que la persona entiende (hora, consumo, luces), nunca la temperatura de una habitación."],
      tam=14.5, color=INK2, vinetas=True, acento=VERDE, espacio=4)

# =====================================================================================================================
# 22 · Cierre
# =====================================================================================================================
s = diapositiva("fin", "Qué queda listo para Shiro y cuál es el siguiente paso",
                "Para cerrar, lo que el semestre deja listo para Shiro: una función de transición que generaliza a un "
                "mes no visto; un contexto con confianza, que K-Means asigna y el jerárquico audita; un anticipador "
                "simple y exportable, G0; y un agente explicable con una recompensa centrada que aprende en cien días "
                "simulados. Lo que no queda listo también está escrito: el entorno continuo sobre el gemelo, un ahorro "
                "que se distinga de no actuar, datos por aparato, otra vivienda y el verano. El siguiente paso que "
                "proponemos es llevar a Shiro lo que ya es útil: G0 como un módulo de solo lectura, con un medidor real "
                "en la casa. La lección de método es la del comienzo: la partición temporal decide. Gracias.")
tarjeta(s, C1, Y0, CW2, Cm(7.6), "Listo", [
    "**Transición**: lineal con retardos (R² {p2:her_bo_lineal_retardos_r2} en la partición temporal).",
    "**Contexto con confianza**: dos tipos de día; K-Means asigna, el jerárquico audita.",
    "**Anticipador** simple y exportable: G0, {p2:titular_p20} de los picos con ≥ 20 min.",
    "**Agente explicable** con recompensa centrada: ≥ 80 % del ahorro de π* desde el día {t3:qlc_dias80|n}."],
         VERDE, tam=14.5)
tarjeta(s, C2, Y0, CW2, Cm(7.6), "No listo", [
    "Entorno continuo sobre el gemelo (hoy: réplica de días reales).",
    "Un ahorro que se distinga de no actuar.",
    "Datos por aparato, otra vivienda y el verano.",
    "Segunda alarma de Guardian (DBSCAN) evaluada."], ROJO, tam=14.5)
_rect(s, MX, Y0 + Cm(8.1), CW, Cm(5.2), PANEL2)
_rect(s, MX, Y0 + Cm(8.1), Cm(0.13), Cm(5.2), NARANJA)
rotulo(s, MX + Cm(0.6), Y0 + Cm(8.5), CW, "Siguiente paso propuesto para Shiro", NARANJA)
texto(s, MX + Cm(0.6), Y0 + Cm(9.3), CW - Cm(1.2), Cm(3.9), [
    "Llevar **G0** al asistente como un módulo de **solo lectura** («¿cómo está la casa?»), con un medidor real: la "
    "regla de nivel desde el primer día y G0 cuando haya picos suficientes, recalibrado cada mes.",
    "Del agente de refuerzo pasan las **reglas de diseño**: la persona fija λ, recompensa centrada, Shiro propone y no "
    "actúa sola."], tam=15, color=INK2, vinetas=True, acento=NARANJA, espacio=5)


def main():
    pies()
    prs.save(SALIDA)
    print(f"Presentación: {SALIDA.name} ({len(prs.slides)} diapositivas, {len(comun.USADAS)} cifras)")
    pdf = exportar_pdf(SALIDA, SALIDA.with_suffix(".pdf"))
    print(f"PDF: {pdf.name}")


if __name__ == "__main__":
    main()
