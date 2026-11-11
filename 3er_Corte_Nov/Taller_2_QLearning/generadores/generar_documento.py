# -*- coding: utf-8 -*-
"""Genera Taller2_C3_QLearning_RESUELTO.docx (y su PDF) desde cifras.json y figuras/.

Uso (desde la carpeta del taller):
    C:\\Users\\pipel\\venvs\\ml\\Scripts\\python.exe generadores\\generar_documento.py
"""
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import RAIZ, C, F, exportar_pdf  # noqa: E402

SALIDA = RAIZ / "Taller2_C3_QLearning_RESUELTO.docx"
FIG = RAIZ / "figuras"
AZUL = "1F3864"
VERDE, NARANJA, GRIS = "E8F3E8", "FDF2E3", "F2F2F2"

doc = Document()
for s in doc.sections:
    s.left_margin = s.right_margin = Cm(2.2)
    s.top_margin = s.bottom_margin = Cm(2.0)
st = doc.styles["Normal"]
st.font.name = "Calibri"
st.font.size = Pt(11)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
st.paragraph_format.space_after = Pt(6)
st.paragraph_format.line_spacing = 1.12


def _sombra(elemento_pr, color):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    elemento_pr.append(shd)


def _runs(p, texto, tam=None, color=None, fuente=None):
    """Texto con **negrita** y *cursiva* simples. Sustituye {clave} por cifras."""
    texto = F(texto).replace("π\\*", "π∗").replace("π*", "π∗").replace("V*", "V∗")
    for trozo in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)", texto):
        if not trozo:
            continue
        if trozo.startswith("**"):
            r = p.add_run(trozo[2:-2]); r.bold = True
        elif trozo.startswith("*"):
            r = p.add_run(trozo[1:-1]); r.italic = True
        elif trozo.startswith("`"):
            r = p.add_run(trozo[1:-1]); r.font.name = "Consolas"
            r._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), "Consolas")
        else:
            r = p.add_run(trozo)
        if tam:
            r.font.size = Pt(tam)
        if color:
            r.font.color.rgb = RGBColor.from_string(color)
        if fuente:
            r.font.name = fuente
            r._element.rPr.rFonts.set(qn("w:eastAsia"), fuente)
    return p


def P(texto, alin=None, tam=None, despues=None):
    p = doc.add_paragraph()
    _runs(p, texto, tam=tam)
    if alin == "j":
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if despues is not None:
        p.paragraph_format.space_after = Pt(despues)
    return p


def V_(items, tam=None):
    for it in items:
        p = doc.add_paragraph(style="List Bullet")
        _runs(p, it, tam=tam)
        p.paragraph_format.space_after = Pt(3)


def N_(items):
    for it in items:
        p = doc.add_paragraph(style="List Number")
        _runs(p, it)
        p.paragraph_format.space_after = Pt(3)


def H1(texto):
    p = doc.add_paragraph()
    _sombra(p._p.get_or_add_pPr(), AZUL)
    r = p.add_run(" " + F(texto))
    r.bold = True; r.font.size = Pt(13); r.font.color.rgb = RGBColor(255, 255, 255)
    p.paragraph_format.space_before = Pt(12); p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True


def H2(texto):
    p = doc.add_paragraph()
    r = p.add_run(F(texto))
    r.bold = True; r.font.size = Pt(11.5); r.font.color.rgb = RGBColor.from_string(AZUL)
    p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True


def recuadro(titulo, lineas, color=VERDE, viñetas=True):
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = t.cell(0, 0)
    _sombra(c._tc.get_or_add_tcPr(), color)
    p = c.paragraphs[0]
    r = p.add_run(titulo); r.bold = True; r.font.size = Pt(10.5)
    for ln in lineas:
        q = c.add_paragraph(style="List Bullet" if viñetas else None)
        _runs(q, ln, tam=10)
        q.paragraph_format.space_after = Pt(2)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def codigo(lineas):
    t = doc.add_table(rows=1, cols=1)
    c = t.cell(0, 0)
    _sombra(c._tc.get_or_add_tcPr(), GRIS)
    c.paragraphs[0].text = ""
    for i, ln in enumerate(lineas):
        p = c.paragraphs[0] if i == 0 else c.add_paragraph()
        r = p.add_run(ln); r.font.name = "Consolas"; r.font.size = Pt(8.5)
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
        p.paragraph_format.space_after = Pt(0)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def tabla(enc, filas, anchos, tam=9.5):
    t = doc.add_table(rows=1, cols=len(enc))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, e in enumerate(enc):
        c = t.rows[0].cells[j]
        _sombra(c._tc.get_or_add_tcPr(), AZUL)
        r = c.paragraphs[0].add_run(e); r.bold = True; r.font.size = Pt(tam); r.font.color.rgb = RGBColor(255, 255, 255)
    for fila in filas:
        cells = t.add_row().cells
        for j, v in enumerate(fila):
            _runs(cells[j].paragraphs[0], str(v), tam=tam)
    for fila in t.rows:
        for j, w in enumerate(anchos):
            fila.cells[j].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


NFIG = [0]


def figura(archivo, pie, ancho=15.5):
    NFIG[0] += 1
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(FIG / archivo), width=Cm(ancho))
    p.paragraph_format.keep_with_next = True
    q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _runs(q, f"**Figura {NFIG[0]}.** " + pie, tam=9)


# =====================================================================================
# Portada
# =====================================================================================
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("APRENDIZAJE DE MÁQUINA — TALLER 2 · 3.er CORTE (APRENDIZAJE POR REFUERZO: Q-LEARNING)")
r.bold = True; r.font.size = Pt(10); r.font.color.rgb = RGBColor.from_string(AZUL)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Shiro Twin: el agente que aprende a aplazar cargas sin conocer el modelo"); r.bold = True; r.font.size = Pt(17)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Q-learning sobre el MDP del Taller 1: entornos, hiperparámetros, definición de estados y diseño de recompensas")
r.italic = True; r.font.size = Pt(11)

tabla(["Campo", "Valor"], [
    ["Universidad", "Universidad Sergio Arboleda · Aprendizaje de Máquina · semestre 26-2"],
    ["Docente", "Hernán Darío Cruz Bueno"],
    ["Grupo Shiro", "Jose Leonardo Diazgranados · Sofía Londoño · Andrés Felipe Céspedes Rondón · Alex Duran"],
    ["Sector", "Energía y Medio Ambiente / IoT"],
    ["Datos", "Appliances Energy Prediction (UCI n.º 374): {n_dias_tr} días de enero–abril para aprender, {n_dias_te} de mayo para evaluar"],
    ["Fecha", "11 de noviembre de 2026"],
], [4, 12.5])

recuadro("Resumen", [
    "En el Taller 1 Shiro **resolvió** su MDP porque tenía la tabla de transiciones de este hogar. En una casa nueva esa "
    "tabla no existe: el agente debe **aprender jugando**. Este taller construye ese agente con Q-learning y lo mide contra "
    "la respuesta correcta que ya conocemos, la π* del Taller 1.",
    "**Con los hiperparámetros del profesor** (α = 0,1 fijo, {n_ep} días simulados) el agente acierta el {prof_acierto_w} "
    "de las decisiones (ponderadas por lo que vale cada una) y consigue solo el **{prof_captura} del ahorro de π*** en "
    "mayo.",
    "**El agente recomendado para Shiro** (α decreciente 1/N^0,6, {n_ep_rec} días) acierta el **{base_acierto_w}**, "
    "consigue el **{base_captura}** del ahorro de π* y en mayo no se distingue de π* ({boot_ql_pi}).",
    "**El arranque en frío es inviable en una casa real:** ninguna de las {n_semillas} semillas llega al 90 % de acierto "
    "ponderado ni con {n_ep_rec} días simulados, unos {anos_rec} de experiencia. Las decisiones que falla son las de brecha "
    "pequeña (mediana {brecha_med}) frente a un error de sus valores Q de {base_errq}.",
    "**Lo que cambia en Shiro:** el agente se pre-entrena en el gemelo y en la casa solo se ajusta; α decreciente; la "
    "definición de estado del proyecto (umbral de 200 Wh) supera a cuantiles y a K-Means; y quedan prohibidas tres "
    "recompensas que producen un Shiro nervioso, uno miedoso o uno que no ejecuta.",
])

# =====================================================================================
H1("1. Qué se construye y qué decisiones dependen de este taller")
P("Shiro Twin ya tiene un simulador, un anticipador de picos (Guardian), un detector de tipos de día y, desde el Taller 1, "
  "el **MDP** del hogar resuelto con iteración de valor. Esa solución usaba algo que en una casa nueva no existe: la "
  "tabla P contada con cuatro meses de datos de *esa* casa. **Q-learning es la pieza que aprende sin modelo** (*model-free*), "
  "solo probando acciones y mirando lo que pasa. Es el agente que tendría que llegar a Shiro Home y el puente al DQN del "
  "Taller 3. Cuatro decisiones de arquitectura dependen de este taller:", alin="j")
N_([
    "**¿Q-learning recupera π*, y con cuántos días de experiencia?** Es el arranque en frío de Shiro en un hogar nuevo.",
    "**Qué α, γ y ε** sirven a un agente que se reentrena cada mes.",
    "**Si la definición del estado** (cuantiles frente a K-Means) cambia lo que el agente aprende.",
    "**Qué recompensas rompen a Shiro**: el agente optimiza exactamente lo que se le pide.",
])

# =====================================================================================
H1("2. Por qué usamos nuestros datos, nuestro MDP y nuestra π*, y no el ejemplo del profesor")
P("El enunciado pide correr el script del profesor (las fresas de `ProductPriceIndex.csv`) y modificarlo. Se conservó "
  "todo lo que lo hace reconocible: los pasos 1 a 5 con sus nombres, la regla de actualización, el ε-greedy, sus "
  "hiperparámetros de partida (α = 0,1; ε de 1,0 a 0,01 con decaimiento 0,999) y sus tres gráficas (curva de "
  "aprendizaje, decaimiento de ε y heatmap de la Q-table). Lo que se cambió, y por qué:", alin="j")
tabla(["Aspecto", "Ejemplo de las fresas", "Shiro", "Por qué"], [
    ["Datos y problema", "Precios de fresas", "Consumo del hogar (UCI n.º 374) y la decisión de aplazar cargas",
     "Principio del proyecto: cada taller construye una pieza de Shiro, aceptado por el docente desde el 1.er corte."],
    ["Acción", "Cubeta del precio de venta observado en Atlanta", "No actuar · aplazar · ejecutar lo pendiente",
     "El agente debe **controlar** la acción. Con un precio observado aprende qué combinaciones se dieron con más "
     "ganancia, no qué decisión conviene."],
    ["Episodio", "Un solo paso desde un estado al azar", "Un día de 24 horas, sin reiniciar a medianoche",
     "Con un solo paso no hay secuencia: γ casi no propaga valor y la curva sube sobre todo porque baja ε (menos "
     "castigos de −100), no porque el agente aprenda."],
    ["Combinación no vista", "−100", "No existe: las acciones válidas están definidas por reglas",
     "El −100 enseña a evitar lo que no está en los datos, no lo que es malo."],
    ["Cómo se sabe si aprendió", "La curva sube", "Coincidencia con **π* del Taller 1** y ahorro real en mayo",
     "Tenemos la respuesta correcta del mismo MDP: se puede medir el acierto, no solo la forma de la curva."],
    ["γ base", "0,9", "0,95, con 0,9 como variante", "Es el del Taller 1: permite comparar con su π* sin mezclar cambios."],
], [2.6, 3.4, 4.2, 6.3], tam=8.5)
P("Así, cada pregunta del taller se responde sobre el agente que de verdad usaría Shiro, y cada resultado se puede "
  "contrastar con una respuesta conocida.", alin="j")

# =====================================================================================
H1("3. Diseño: MDP, entornos, agente y cómo se mide")
H2("3.1 El MDP es el del Taller 1, sin cambios")
P("**{n_estados_umbral} estados**: tipo de día estimado con K-Means sobre la curva parcial, franja, nivel de demanda "
  "(< 60 / 60–200 / > 200 Wh) y carga pendiente; {n_decision_umbral} de ellos tienen algo que decidir. **Acciones:** no "
  "actuar, aplazar (pico y cupo libre) y ejecutar lo pendiente. **Recompensa:** −tarifa · energía − λ · espera, con la "
  "contabilidad corregida del Taller 1; tarifa de valle 1,0 y de punta 1,5; ΔE = {DE_umbral}; λ = 0,005. La iteración de "
  "valor da π*, y repetirla en mayo reproduce el Taller 1 al decimal (**{n_anclas} anclas de {n_anclas}**: ahorro "
  "{vi_ahorro_te}, espera {vi_espera_te}).", alin="j")
H2("3.2 Dos entornos de simulación (Paso 3)")
V_([
    "**Réplica de días reales** (principal, «el dataset como simulador»): recorre los {dias_ep} días de enero–abril hora a "
    "hora con su energía real. La acción solo mueve la energía aplazable y la carga pendiente. **No se reinicia a "
    "medianoche**: la carga pendiente cruza a la mañana siguiente, como en la vida real.",
    "**Modelo contado** (control): sortea la hora siguiente de la tabla P del Taller 1 y usa sus recompensas medias. Es "
    "*exactamente* el MDP que resolvió la iteración de valor.",
])
recuadro("Un error de diseño que se corrigió antes de reportar", [
    "La primera versión reiniciaba cada día a las 00:00 sin carga pendiente. Los estados «madrugada con carga pendiente» "
    "nunca se visitaban y conservaban su valor inicial Q = 0, que parece un premio frente a valores cercanos a −20.",
    "El agente aprendió a arrastrar la carga hasta la medianoche y ejecutarla la mañana siguiente en punta: ahorro nulo. "
    "Es la misma lección del Taller 1: **el agente explota cualquier defecto del entorno**. El entorno final no reinicia.",
], color=NARANJA)
H2("3.3 El agente (Paso 4) y las tres medidas")
P("La regla es la del profesor: Q(s,a) ← Q(s,a) + α·[r + γ·max Q(s′,·) − Q(s,a)], con ε-greedy y ε de 1,0 a 0,01 "
  "(decaimiento 0,999 por día). Cada configuración se entrena con **{n_semillas} semillas**: las curvas van con su banda. "
  "Para saber si aprendió se usan tres medidas:", alin="j")
V_([
    "**Coincidencia simple:** % de los {n_decision_umbral} estados con decisión en que su acción coincide con π*.",
    "**Coincidencia ponderada:** cada estado pesa lo que vale acertar en él, es decir, la **brecha** entre la mejor y la "
    "segunda acción según la iteración de valor. Esa brecha es pequeña: mediana {brecha_med}, de {brecha_min} a "
    "{brecha_max}. Equivocarse en una decisión casi empatada cuesta casi nada.",
    "**Ahorro capturado:** qué % del ahorro de π* consigue la política aprendida en mayo, con la cuenta real.",
])
P("La curva de aprendizaje se dibuja como **la recompensa del día menos la que habría tenido no actuar ese mismo día**. "
  "Lo que consume la casa cambia varios kWh de un día a otro, y el efecto de las decisiones es de décimas: sin restar ese "
  "día de referencia, la curva solo mostraría qué días gastó más el hogar.", alin="j")

# =====================================================================================
H1("4. Problema base: ¿Q-learning recupera la π* del Taller 1?")
tabla(["Agente · entorno", "Coincidencia", "Ponderada", "Llegan al 90 %", "Ahorro mayo", "Capturado de π*"], [
    ["Profesor (α 0,1 · {n_ep} días) · réplica", "{prof_acierto}", "{prof_acierto_w}", "{prof_alcanzan}", "{prof_ahorro}", "{prof_captura}"],
    ["Profesor · modelo contado", "{prof_modelo_acierto}", "{prof_modelo_acierto_w}", "{prof_modelo_alcanzan}", "{prof_modelo_ahorro}", "{prof_modelo_captura}"],
    ["**Recomendado (1/N^0,6 · {n_ep_rec} días) · réplica**", "{base_acierto}", "**{base_acierto_w}**", "{base_alcanzan}", "**{base_ahorro}**", "**{base_captura}**"],
    ["Recomendado · modelo contado", "{rec_modelo_acierto}", "{rec_modelo_acierto_w}", "{rec_modelo_alcanzan}", "{rec_modelo_ahorro}", "{rec_modelo_captura}"],
    ["π* (iteración de valor, Taller 1)", "100 %", "100 %", "—", "{vi_ahorro_te}", "100 %"],
], [5.6, 2.0, 2.0, 2.2, 2.1, 2.6], tam=8.5)
figura("Q1_base_aprendizaje.png", "Curva de aprendizaje, coincidencia ponderada con π* y decaimiento de ε del problema base "
       "(bandas: {n_semillas} semillas).")
P("**Lectura.** Con α = 0,1 fijo el agente no converge: su error medio en los valores Q es de {prof_errq}, cuando la "
  "brecha que tiene que distinguir es de {brecha_med}. Cada día raro mueve los Q más de lo que separa una acción de "
  "otra. Con **α decreciente** (1/N^0,6: rápido al principio y después promedio) el error baja a {base_errq} y el "
  "acierto ponderado sube a {base_acierto_w} (de {base_acierto_w_min} a {base_acierto_w_max} según la semilla). Lo que "
  "le queda es un **sesgo de sobreestimación** de {base_sesgoq}, el clásico de tomar el máximo de valores con ruido.", alin="j")
P("**Dónde falla.** El consenso de las cinco semillas difiere de π* en {base_n_difs} de {n_decision_umbral} estados. "
  "Son decisiones de brecha pequeña: si aplazar un pico de la mañana (el valle queda lejos) y qué hacer con una "
  "carga pendiente en la madrugada, la mañana o la tarde. **Son las mismas decisiones «por milésimas» que el Taller 1 "
  "marcó como dudosas.** Aun así, en mayo la política aprendida **no se distingue de π*** ({boot_ql_pi}).", alin="j")
P("**El modelo contado resulta más difícil que la réplica** (ponderada {rec_modelo_acierto_w} frente a "
  "{base_acierto_w}). En el modelo, la hora dentro de la franja se sortea en cada paso; en la réplica avanza como en la "
  "realidad. Por eso, *probablemente*, el valor futuro tiene más ruido en el modelo que en los días reales.", alin="j")
figura("Q2_base_heatmap.png", "Heatmap de la Q-table final: π* (iteración de valor), agente con hiperparámetros del "
       "profesor y agente recomendado. Número: valor Q; color: ventaja frente a la mejor acción del estado.", ancho=16)
recuadro("El hallazgo para Shiro: el arranque en frío es inviable", [
    "Ninguna semilla del agente recomendado llega al 90 % de acierto ponderado en {n_ep_rec} días simulados (en el "
    "modelo contado: {rec_modelo_alcanzan}). En una casa real la experiencia llega a un día por día: {n_ep_rec} días son "
    "unos **{anos_rec}**.",
    "→ El agente de Shiro Home **no puede aprender desde cero en la casa**. Se pre-entrena en el gemelo (Shiro Twin) y en "
    "el hogar solo se ajusta. Esto justifica con números el orden Twin → Home del proyecto y el Taller 3 (DQN sobre el "
    "simulador).",
])

# =====================================================================================
H1("5. Parte 1 — El explorador de entornos: ¿la política es la misma en otra estación?")
P("**Problema A:** el agente aprende con enero–abril (invierno). **Problema B:** aprende solo con mayo (primavera, "
  "{n_dias_te} días). La «personalidad» de cada periodo:", alin="j")
tabla(["Periodo", "Horas con nivel alto", "Energía media", "Horas al valle desde la tarde", "Horas al valle desde la noche", "Estados vistos"], [
    ["Enero–abril (A)", "{pers_alto_A}", "{pers_kwh_A}", "{pers_valle_tarde_A}", "{pers_valle_noche_A}", "{pers_estados_A}"],
    ["Mayo (B)", "{pers_alto_B}", "{pers_kwh_B}", "{pers_valle_tarde_B}", "{pers_valle_noche_B}", "{pers_estados_B}"],
], [3.2, 2.6, 2.6, 2.8, 2.8, 2.4], tam=9)
P("**¿Es la misma política óptima?** Sí. La iteración de valor con los datos de mayo da **la misma acción en los "
  "{p1_iguales_vi} de {p1_decision_comunes}** estados con decisión que existen en ambos periodos. Mayo tiene menos picos y "
  "algo menos de energía, pero la geometría del problema (qué tan lejos queda el valle desde cada franja) casi no cambia. "
  "La «personalidad» de este hogar es estable entre estaciones.", alin="j")
tabla(["Política", "Aplicada en enero–abril", "Aplicada en mayo"], [
    ["π* de invierno", "{tr_vi_inv_tr}", "{tr_vi_inv_te}"],
    ["π* de mayo", "{tr_vi_mayo_tr}", "{tr_vi_mayo_te}"],
    ["Q-learning aprendido en invierno", "{tr_ql_inv_tr}", "{tr_ql_inv_te}"],
    ["Q-learning aprendido solo en mayo", "{tr_ql_mayo_tr}", "{tr_ql_mayo_te}"],
], [6, 4, 4], tam=9)
P("**Lo que sí cambia es lo que el agente alcanza a aprender.** Con solo {n_dias_te} días, aun repetidos miles de veces, "
  "el agente de mayo acierta el {p1_B_acierto_w} ponderado pero su política no ahorra nada: aplaza y vuelve a ejecutar en "
  "punta. El agente de invierno, en cambio, **se transfiere a mayo sin perder ahorro** ({tr_ql_inv_tr} en su periodo, "
  "{tr_ql_inv_te} en mayo). → Para Shiro, una política aprendida con una estación larga sirve para la siguiente; "
  "aprender desde cero con un mes no.", alin="j")
figura("Q3_parte1_aprendizaje.png", "Parte 1: curva de aprendizaje, coincidencia con la π* de cada periodo y ε.")
figura("Q4_parte1_heatmap.png", "Parte 1: Q-table final de cada estación.", ancho=12)

# =====================================================================================
H1("6. Parte 2 — El sintonizador de hiperparámetros")
H2("6.1 Experimento 1: miope (γ = 0,5) frente a paciente (γ = 0,99)")
tabla(["γ", "π* (iteración de valor)", "Q-learning: ponderada", "Ahorro capturado", "Ahorro mayo", "Espera mayo", "Q mínimo"], [
    ["0,5 (miope)", "aplaza en {vi_aplaza_g0p5}, ejecuta en {g0p5_vi_ejecuta}", "{g0p5_acierto_w}", "{g0p5_captura}", "{g0p5_ahorro}", "{g0p5_espera}", "{g0p5_qmin}"],
    ["0,9 (profesor)", "aplaza en {vi_aplaza_g0p9}", "{g0p9_acierto_w}", "{g0p9_captura}", "{g0p9_ahorro}", "{g0p9_espera}", "—"],
    ["0,95 (base)", "aplaza en {vi_aplaza_umbral}, ejecuta en {g0p95_vi_ejecuta}", "{base_acierto_w}", "{base_captura}", "{base_ahorro}", "{base_espera}", "{g0p95_qmin}"],
    ["0,99 (paciente)", "aplaza en {vi_aplaza_g0p99}, ejecuta en {g0p99_vi_ejecuta}", "{g0p99_acierto_w}", "{g0p99_captura}", "{g0p99_ahorro}", "{g0p99_espera}", "{g0p99_qmin}"],
], [2.3, 3.6, 2.2, 2.0, 1.9, 2.0, 1.6], tam=8.5)
P("**¿Cambia la estrategia?** La óptima casi no cambia: con γ = 0,5 π* aplaza en los {vi_aplaza_g0p5} picos "
  "posibles y ejecuta en {g0p5_vi_ejecuta} estados, igual que con 0,95. La razón es la contabilidad corregida, que cobra el beneficio de aplazar en el mismo momento, así "
  "que hasta un agente miope lo ve. Con γ = 0,99 deja de aplazar en un estado y ejecuta en más.", alin="j")
P("**Lo que sí cambia, y mucho, es cuánto le cuesta aprenderla.** El agente miope tiene valores Q pequeños (mínimo "
  "{g0p5_qmin}) y poco ruido: aprende mejor que el base y captura el {g0p5_captura}. El paciente acumula valores "
  "enormes (mínimo {g0p99_qmin}); su ruido supera las brechas, y en mayo su política no ahorra ({g0p99_ahorro}) con "
  "{g0p99_espera} de espera. → Para un agente tabular conviene un horizonte corto; un γ alto solo vale la pena con más "
  "datos o con una red que generalice (Taller 3).", alin="j")
figura("Q5_parte2_gamma.png", "Parte 2 · Experimento 1: curvas, coincidencia con π*(γ) y ε para cuatro valores de γ.")
figura("Q6_parte2_gamma_heatmap.png", "Parte 2 · Experimento 1: Q-table final según γ (escalas muy distintas).", ancho=14)
H2("6.2 Experimento 2: lento (α = 0,01) frente a impulsivo (α = 0,9), todos con {n_ep_rec} días")
tabla(["α", "Ponderada", "Ahorro capturado", "Oscilación final de la curva", "Salto medio de la coincidencia"], [
    ["0,01 (lento)", "{a0p01_acierto_w}", "{a0p01_captura}", "{a0p01_disp}", "{a0p01_salto}"],
    ["0,1 (profesor)", "{a0p1_acierto_w}", "{a0p1_captura}", "{a0p1_disp}", "{a0p1_salto}"],
    ["0,9 (impulsivo)", "{a0p9_acierto_w}", "{a0p9_captura}", "{a0p9_disp}", "{a0p9_salto}"],
    ["**1/N^0,6 (recomendado)**", "**{base_acierto_w}**", "**{base_captura}**", "{arec_disp}", "{arec_salto}"],
], [4, 2.4, 2.6, 3.4, 3.6], tam=9)
P("**¿Cuál es más estable?** El impulsivo (α = 0,9) tiene la curva que más oscila: cada día reemplaza casi por completo "
  "lo aprendido. El lento (α = 0,01) aprende tan despacio que, a los {n_ep_rec} días, su política todavía cambia de "
  "opinión entre mediciones. **Ningún α fijo resuelve el problema:** con α = 0,1 entrenar más días no mejora (el ruido "
  "pone un piso). El α decreciente combina las dos virtudes: aprende rápido al principio y después promedia, y es el "
  "único que captura casi todo el ahorro de π*.", alin="j")
figura("Q7_parte2_alpha.png", "Parte 2 · Experimento 2: curvas, coincidencia con π* y ε para cuatro esquemas de α.")
figura("Q9_parte2_alpha_heatmap.png", "Parte 2 · Experimento 2: Q-table final según α.", ancho=14)

# =====================================================================================
H1("7. Parte 3 — El arquitecto del mundo: cuantiles frente a K-Means")
P("Se eliminó `pd.qcut` y se probaron tres formas de definir el nivel de demanda. Cada una tiene su propia π* y su "
  "propio ΔE (el 40 % del exceso medio de las horas que llama «alto»):", alin="j")
figura("Q8_cortes_estados.png", "Dónde corta cada definición el nivel de demanda sobre la distribución de la media horaria.")
tabla(["Definición", "Cortes", "Horas «alto»", "ΔE", "π*: ahorro mayo", "Q-learning: ponderada", "Q-learning: ahorro mayo"], [
    ["Cuantiles (qcut), sin tipo de día", "{corte_q1} y {corte_q2}", "{pct_alto_qcut}", "{DE_qcut}", "{p3vi_qcut_ahorro}", "{p3_qcut_acierto_w}", "{p3_qcut_ahorro}"],
    ["K-Means (días k = 2; nivel k = 3)", "{corte_k1} y {corte_k2}", "{pct_alto_kmeans}", "{DE_kmeans}", "{p3vi_kmeans_ahorro}", "{p3_kmeans_acierto_w}", "{p3_kmeans_ahorro}"],
    ["**Umbral del proyecto (base)**", "60 y 200 Wh", "{pct_alto_umbral}", "{DE_umbral}", "**{p3vi_umbral_ahorro}**", "**{base_acierto_w}**", "**{base_ahorro}**"],
], [4.2, 2.4, 1.8, 1.6, 2.2, 2.2, 2.2], tam=8.5)
P("**¿Es diferente la política? ¿Es mejor?** Con cuantiles, π* solo aplaza en **{vi_aplaza_qcut} estado**: el tercil "
  "«alto» arranca en {corte_q2} y mezcla picos reales con horas comunes. El {p3_qcut_sin_exceso} de esas horas no tiene "
  "ni una lectura sobre 200 Wh, así que no hay nada que aplazar y el ΔE medio se encoge a {DE_qcut}. K-Means encuentra "
  "cortes «naturales» más arriba ({corte_k1} y {corte_k2}) y **supera a los cuantiles** tanto con π* como con el agente "
  "que aprende.", alin="j")
P("**¿Por qué K-Means es más realista que Bajo/Medio/Alto?** Los terciles reparten las horas en tres grupos del mismo "
  "tamaño aunque el consumo no tenga esa forma (cola larga a la derecha). K-Means separa por distancia: el grupo alto son "
  "las horas que de verdad se alejan del resto. Pero el **umbral del proyecto** (200 Wh, el percentil 90 de "
  "entrenamiento) gana a los dos: K-Means deja «alto» solo al {pct_alto_kmeans} de las horas y pierde oportunidades de "
  "aplazar. La mejor definición de estado no la da un algoritmo de agrupamiento por sí solo, sino uno anclado en lo que "
  "la acción puede mover.", alin="j")
figura("Q10_parte3_aprendizaje.png", "Parte 3: el mismo agente con tres definiciones de estado.")
figura("Q11_parte3_heatmap.png", "Parte 3: Q-table final según la definición de estado.", ancho=16)

# =====================================================================================
H1("8. Parte 4 — El ingeniero de recompensas")
tabla(["Recompensa", "Qué aprendió (consenso)", "Aplazamientos/día", "Espera", "Ahorro real mayo"], [
    ["Base: costo + λ·espera, contabilidad corregida", "aplaza en {base_aplaza_est} estados, ejecuta en {base_ejecuta_est}", "{base_aplaz}", "{base_espera}", "{base_ahorro}"],
    ["**+1 por transacción**", "aplaza en {p4_trans_aplaza_est}, ejecuta en {p4_trans_ejecuta_est}", "{p4_trans_aplaz}", "{p4_trans_espera}", "{p4_trans_ahorro}"],
    ["**Castigo −1000 si la ganancia del paso es negativa**", "aplaza en {p4_miedo_aplaza_est}", "{p4_miedo_aplaz}", "{p4_miedo_espera}", "{p4_miedo_ahorro}"],
    ["Extra: contabilidad ingenua (Taller 1)", "aplaza en {p4_ing_aplaza_est}, ejecuta en {p4_ing_ejecuta_est}", "{p4_ing_aplaz}", "{p4_ing_espera}", "{p4_ing_ahorro}"],
], [5.6, 3.8, 2.2, 2.0, 2.2], tam=8.5)
V_([
    "**+1 por transacción → el Shiro nervioso.** Aprende a aplazar todo pico y ejecutarlo a la hora siguiente: "
    "{p4_trans_aplaz} aplazamientos al día, una hora de espera cada uno y **ahorro {p4_trans_ahorro}**. Mueve energía de "
    "una hora de punta a otra de punta y cobra su recompensa por moverse. Es la fatiga de alertas del parcial 1 (avisos "
    "que no sirven), ahora como recompensa.",
    "**Castigo de −1000 → el Shiro miedoso.** Esperar con una carga pendiente cuesta λ, una ganancia negativa que se "
    "convierte en −1000, así que el agente **nunca aplaza** ({p4_miedo_aplaz} aplazamientos al día): elige siempre «no "
    "actuar», el *Hold* del ejemplo financiero.",
    "**Contabilidad ingenua.** Q-learning no alcanzó a caer del todo en la trampa que la iteración de valor sí mostró en el "
    "Taller 1 (allí la carga esperaba 23,4 h/día), pero ya espera {p4_ing_espera} frente a {base_espera} del base y "
    "consigue menos ahorro ({p4_ing_ahorro}).",
])
figura("Q12_parte4_recompensas.png", "Parte 4: curva de aprendizaje (recompensa propia normalizada), ahorro real, "
       "aplazamientos por día y ε.")
figura("Q13_parte4_heatmap.png", "Parte 4: Q-table final según la recompensa.", ancho=14)

# =====================================================================================
H1("9. La batalla en mayo")
figura("Q14_batalla_mayo.png", "Ahorro de costo en mayo, frente a no actuar, de cada configuración con su política final "
       "(media de {n_semillas} semillas). Línea punteada: π* del Taller 1.")
P("Las dos configuraciones que más se acercan a π* son el agente recomendado y su variante con γ = 0,5. Su consenso ahorra {ql_cons_ahorro} con "
  "{ql_cons_espera} de espera. Con bootstrap pareado por día (2.000 réplicas) **no se distingue de π*** ({boot_ql_pi}). "
  "Tampoco se distingue de no actuar ({boot_ql_no}), igual que π* en el Taller 1: con esta tarifa y este hogar aplazar "
  "mueve poco.", alin="j")

# =====================================================================================
H1("10. Qué cambia en el diseño de Shiro por estos números")
recuadro("Decisiones que quedan tomadas", [
    "**El agente se pre-entrena en el gemelo y en la casa solo se ajusta.** Ni {n_ep_rec} días simulados ({anos_rec} de "
    "experiencia real) bastan para el 90 % ponderado. El orden Twin → Home del proyecto deja de ser una preferencia y pasa "
    "a ser una necesidad medida.",
    "**α decreciente (1/N^0,6), no fijo.** Con el α del profesor el agente captura el {prof_captura} del ahorro de π*; con "
    "el decreciente, el {base_captura}.",
    "**Horizonte corto para el agente tabular.** γ = 0,5 llega a la misma estrategia con menos ruido; γ = 0,99 se ahoga en "
    "su propio ruido. El γ alto queda para el DQN del Taller 3.",
    "**La definición de estado del proyecto se mantiene** (umbral de 200 Wh, percentil 90). Supera a cuantiles y a "
    "K-Means: lo que importa es lo que la acción puede mover.",
    "**Recompensas prohibidas en el entorno de Q-learning/DQN:** pagar por actuar (Shiro nervioso), castigar toda pérdida "
    "(Shiro miedoso) y la contabilidad ingenua. Queda fija la recompensa del Taller 1.",
    "**Una política de invierno sirve en primavera** (la π* es la misma en las dos estaciones); aprender desde cero con un "
    "mes no sirve.",
    "**Las decisiones con brecha pequeña** son las que Q-learning no distingue: se muestran como dudosas (hallazgo 35 del "
    "proyecto).",
])
recuadro("Límites que se declaran", [
    "Solo {n_semillas} semillas por configuración; las bandas lo muestran, pero no hay intervalos formales entre "
    "configuraciones salvo en la batalla final.",
    "ΔE constante y la demanda independiente de la acción, como en el Taller 1. El MDP es una aproximación de Markov: la "
    "hora dentro de la franja no está en el estado.",
    "El calendario de ε es el del profesor en todos los casos; no se sintonizó.",
    "Q-learning sobreestima sus valores (sesgo {base_sesgoq}); variantes como Double Q-learning quedan para el Taller 3.",
    "Mayo son {n_dias_te} días: el problema B de la Parte 1 aprende y se evalúa con los mismos días.",
], color=NARANJA)

H1("11. Reproducibilidad")
V_([
    "`Taller2_C3_QLearning_Shiro.ipynb`: pasos 1–5 adaptados, las cuatro partes y la batalla. Corre de principio a fin, "
    "verifica sus {n_anclas} anclas con el Taller 1 y escribe `cifras.json`, las políticas en CSV y las figuras Q1–Q14.",
    "`generadores/`: construye y ejecuta el cuaderno, este documento y la presentación. Todas las cifras de este documento "
    "salen de `cifras.json`.",
    "Datos: `data set/energydata_complete.csv` (UCI n.º 374). Semillas 42 a 46.",
])


def main():
    doc.save(SALIDA)
    print(f"Documento: {SALIDA.name}")
    pdf = exportar_pdf(SALIDA, SALIDA.with_suffix(".pdf"))
    print(f"PDF: {pdf.name}")


if __name__ == "__main__":
    main()
