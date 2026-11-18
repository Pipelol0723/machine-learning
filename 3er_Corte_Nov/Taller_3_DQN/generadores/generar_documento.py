# -*- coding: utf-8 -*-
r"""Genera Taller3_C3_DQN_RESUELTO.docx (y su PDF) desde cifras.json (de este taller y de los talleres 1 y 2) y figuras/.

Uso (desde la carpeta del taller):
    C:\Users\pipel\venvs\ml\Scripts\python.exe generadores\generar_documento.py
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

SALIDA = RAIZ / "Taller3_C3_DQN_RESUELTO.docx"
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
r = p.add_run("APRENDIZAJE DE MÁQUINA — TALLER 3 · 3.er CORTE (DE Q-LEARNING A DEEP Q-NETWORKS)")
r.bold = True; r.font.size = Pt(10); r.font.color.rgb = RGBColor.from_string(AZUL)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Shiro Twin: de la Q-table a la red, el agente con estado continuo"); r.bold = True; r.font.size = Pt(17)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Investigación, aplicación al sector y prototipo DQN que evoluciona el MDP del Taller 1 y el Q-learning del Taller 2")
r.italic = True; r.font.size = Pt(11)

tabla(["Campo", "Valor"], [
    ["Universidad", "Universidad Sergio Arboleda · Aprendizaje de Máquina · semestre 26-2"],
    ["Docente", "Hernán Darío Cruz Bueno"],
    ["Grupo Shiro", "Jose Leonardo Diazgranados · Sofía Londoño · Andrés Felipe Céspedes Rondón · Alex Duran"],
    ["Sector", "Energía y Medio Ambiente / IoT"],
    ["Datos", "Appliances Energy Prediction (UCI n.º 374): {n_dias_tr} días de enero–abril para aprender, {n_dias_te} de mayo para evaluar"],
    ["Entrega", "Video (las tres partes) · este documento como respaldo escrito · cuaderno Taller3_C3_DQN_Shiro.ipynb"],
    ["Fecha", "13 de noviembre de 2026"],
], [4, 12.5])

recuadro("Resumen", [
    "Shiro decide cada hora si aplazar la carga desplazable del hogar. En el Taller 1 resolvió el problema con el modelo "
    "(π* ahorra el {vi_ahorro_te} en mayo) y en el Taller 2 lo aprendió sin modelo con una tabla, pero necesitó "
    "{n_ep_ql} días simulados. Este taller reemplaza la tabla por una **red neuronal (DQN, escrita en NumPy)** que ve un "
    "estado de {n_rasgos} números: la hora exacta, el consumo, la confianza en el tipo de día y la carga pendiente.",
    "**La red alcanza a la política óptima:** con {n_ep_dqn} días captura el **{dqn_captura}** del ahorro de π* y la "
    "semilla mediana toma las mismas decisiones que π* en todo mayo ({boot_dqn_pi}).",
    "**La sorpresa:** el arranque en frío del Taller 2 no era culpa de la tabla sino del **ruido de la recompensa**. Con la "
    "recompensa centrada (se quita el costo de lo que consume la casa, que no depende de Shiro) el mismo Q-learning de "
    "tabla captura el ≥ 80 % del ahorro desde los **{qlc_dias80}** y termina en el {qlc_captura}; la red, desde los "
    "{dqn_dias80}.",
    "**Los dos trucos son imprescindibles:** sin memoria de experiencias ni red objetivo la red captura el {sina_captura}, "
    "con semillas que no ahorran nada y {sina_espera} de espera.",
    "**Lo que cambia en Shiro:** la recompensa centrada es obligatoria; con los {n_estados} estados de hoy basta la tabla; "
    "la red se justifica por el estado que viene (hora exacta, probabilidad de pico de Guardian, otras casas) y su peso "
    "exportado corre en la consola del parcial.",
])

# =====================================================================================
H1("1. Qué se construye y qué decisiones dependen de este taller")
P("Shiro Twin ya tiene simulador, anticipador de picos (Guardian), tipos de día y un agente de decisión. Ese agente "
  "tiene dos límites que el Taller 2 midió: **aprende lento** (con {n_ep_ql} días simulados, unos {t2:anos_rec} de "
  "experiencia real, no llega al 90 % de acierto ponderado) y **ve el mundo en {n_estados} casillas**: la franja de seis "
  "horas y no la hora, tres niveles de consumo y no el consumo. El estado que Shiro Home necesitará (la probabilidad "
  "calibrada de pico de G0, la confianza del tipo de día, el clima) es continuo y no cabe en una tabla. Este taller "
  "construye el agente que sí lo puede recibir, y responde cuatro preguntas de arquitectura:", alin="j")
N_([
    "**¿Una red acorta el arranque en frío?** De eso depende cuánto pre-entrenamiento en el gemelo necesita Shiro Home.",
    "**¿La hora exacta cambia la decisión dentro de una franja?** Es lo que la tabla no podía ver (hallazgo 35).",
    "**¿Qué trucos de estabilidad son imprescindibles** con nuestros datos? Se quitan uno por vez.",
    "**¿Qué agente ejecuta la consola del parcial?** La tabla, la red o ambas, lado a lado.",
])

H1("2. Por qué partimos de nuestro prototipo y no de un ejemplo")
P("Para este taller no hay cuaderno del profesor: el enunciado pide **evolucionar el prototipo de los talleres 1 y 2**, y "
  "los dos adjuntos son trabajos de otros grupos (seguridad vial y banca) que responden la parte conceptual sin "
  "resultados propios. Por eso el prototipo conserva todo lo que ya estaba verificado (datos, MDP, tarifa, ΔE = {DE}, "
  "λ, contabilidad corregida y el entorno de réplica sin reinicio a medianoche) y cambia una sola cosa por vez: la tabla "
  "por la red. Así cada diferencia se puede atribuir, y la π* del Taller 1 sigue siendo la respuesta correcta contra la "
  "que se mide todo. Antes de entrenar, el cuaderno comprueba **{n_anclas} anclas**: cinco cifras del Taller 1 y el ahorro "
  "en mayo del Q-learning recomendado del Taller 2, que se reproducen exactamente.", alin="j")

# =====================================================================================
H1("3. Parte 1 · Investigación: de la Q-table a la red")
H2("3.1 ¿Por qué la Q-table no escala?")
P("La Q-table guarda un número por cada pareja (estado, acción) y lo actualiza solo cuando el agente visita **esa** "
  "pareja. De ahí sus dos límites:", alin="j")
V_([
    "**No generaliza.** Lo aprendido en una casilla no informa a las vecinas: para la tabla, las 17:00 y las 18:00 con un "
    "consumo parecido son celdas distintas, y cada una debe visitarse muchas veces para estimar su valor.",
    "**Crece de forma multiplicativa.** Cada variable nueva multiplica el número de celdas. Si Shiro pasara de la franja "
    "(4 valores) a la hora (24), de 3 niveles de consumo a 10 y añadiera la probabilidad de pico en 5 tramos, los "
    "{n_estados} estados pasarían a miles, cada uno con pocas visitas. Con variables continuas la tabla ni siquiera "
    "existe sin discretizar, y discretizar pierde información.",
])
P("**En Shiro ya se midió el costo:** con solo {n_estados} estados, Q-learning necesitó {n_ep_ql} días simulados para "
  "capturar el {ql_captura} del ahorro de π*, y sus valores Q quedaron con un error de {t2:base_errq} frente a brechas "
  "entre acciones de {t2:brecha_med} (mediana). La tabla no tiene cómo compartir lo aprendido entre estados parecidos.",
  alin="j")

H2("3.2 ¿Qué reemplaza a la tabla y cuál es su rol?")
P("En DQN (Mnih et al., 2015) una **red neuronal** Q(s, a; θ) recibe el estado como un vector de números y devuelve en "
  "una sola pasada el valor de **todas** las acciones. Ya no se guarda un número por casilla: se ajustan los pesos θ "
  "para que la red se acerque al objetivo de Bellman r + γ · max Q(s′, a′). Su rol es **aproximar y generalizar**: "
  "estados parecidos producen valores parecidos, así que cada experiencia mejora la estimación de muchos estados a la "
  "vez y la red puede responder ante estados que nunca vio (con el riesgo de extrapolar, que se mide en la Parte 3).",
  alin="j")
figura("T0_esquema_dqn.png", "El DQN de Shiro: el estado de la casa entra como {n_rasgos} números, la red devuelve el valor Q "
       "de cada acción y se elige la mayor entre las válidas. Abajo, los dos mecanismos que estabilizan el aprendizaje.",
       ancho=16)

H2("3.3 Memoria de experiencias (experience replay)")
P("El agente guarda cada transición (s, a, r, s′) en una memoria y entrena con **lotes tomados al azar** de ella (Lin, "
  "1992; Mnih et al., 2015). Resuelve dos problemas:", alin="j")
V_([
    "**Correlación.** Pasos consecutivos son casi idénticos (en nuestro dataset, dos lecturas seguidas difieren muy poco: "
    "es la advertencia de autocorrelación del proyecto). Entrenar en orden equivale a ajustar la red una y otra vez al "
    "mismo pedazo del día; el muestreo al azar mezcla horas, días y situaciones.",
    "**Eficiencia.** Cada transición se reutiliza muchas veces, así que se necesitan menos días de experiencia. Para Shiro "
    "Home, donde cada día real cuesta un día, esto es lo que importa.",
])
H2("3.4 Red objetivo fija")
P("El objetivo r + γ · max Q(s′) depende de la misma red que se está ajustando: cada actualización mueve también el "
  "blanco, y el entrenamiento puede oscilar o divergir. La solución es una **segunda red, copia congelada** de la "
  "principal, que calcula el objetivo y solo se sincroniza cada cierto número de actualizaciones (en Shiro, cada 500). "
  "Así el blanco queda quieto el tiempo suficiente para acercarse a él. **Double DQN** (van Hasselt et al., 2016) va un "
  "paso más allá: la red principal elige la mejor acción siguiente y la objetivo la evalúa, lo que reduce la "
  "sobreestimación que produce el máximo de valores con ruido (el Taller 2 midió un sesgo de {t2:base_sesgoq} en sus "
  "Q).", alin="j")
P("Los dos trucos no se dejan como teoría: en la Parte 3 (E3) se **quitan uno por vez** y se mide qué se rompe.",
  alin="j")

# =====================================================================================
H1("4. Parte 2 · Aplicación al sector: Shiro Home")
H2("4.1 El problema")
P("Cada hora, Shiro decide qué hacer con la **carga desplazable** del hogar (lavadora, secadora, horno: un bloque de "
  "ΔE = {DE}, el 40 % del exceso medio de un pico) para **pagar menos energía sin imponer esperas largas**. La tarifa "
  "tiene valle (madrugada, precio 1,0) y punta (resto del día, 1,5). Shiro propone y la persona aprueba; λ representa lo "
  "que a esa persona le cuesta esperar.", alin="j")
H2("4.2 Estado: {n_rasgos} números que Shiro conoce a esa hora")
tabla(["Variable", "Qué es", "Por qué la necesita Shiro"], [
    ["Hora (seno y coseno)", "La hora exacta, en un círculo: las 23:00 quedan junto a las 00:00",
     "Lo que la tabla no veía: la distancia al valle cambia dentro de una franja (hallazgo 35)."],
    ["Consumo actual y anterior", "log Wh de la hora en curso y de la anterior, estandarizados con enero–abril",
     "El nivel continuo, no tres tramos; el anterior indica si el pico está empezando o terminando."],
    ["Margen de K-Means", "Qué tan cerca está la curva parcial del día del centroide de carga alta (de −1 a 1)",
     "El tipo de día con su confianza (hallazgo 22), no una etiqueta."],
    ["Tarifa vigente", "1 en punta, 0 en valle", "Lo que cuesta consumir ahora."],
    ["Carga pendiente", "1 si hay un bloque aplazado esperando", "Sin ella, aplazar borraría consumo (hallazgo 32)."],
    ["Horas esperando", "Horas que lleva la carga aplazada, divididas entre 24", "La espera que paga la persona."],
    ["Nivel alto", "1 si el consumo supera 200 Wh (el umbral del proyecto)", "Solo un pico se puede aplazar."],
], [3.6, 6.0, 6.9], tam=8.5)
H2("4.3 Acciones")
V_([
    "**No actuar:** el consumo sigue como está.",
    "**Aplazar:** mueve ΔE de un pico a más tarde. Solo si hay un pico y no hay otra carga esperando (un cupo).",
    "**Ejecutar lo pendiente:** corre ahora la carga aplazada.",
])
H2("4.4 Recompensa: la misma del Taller 1, pero centrada")
P("La recompensa del Taller 1 es −tarifa · energía − λ · espera, con la **contabilidad corregida** (al aplazar se cobra "
  "la parte aplazada a precio de valle y al ejecutar solo el sobrecosto, hallazgo 32). Su primer término incluye el costo "
  "de **todo** lo que consume la casa en esa hora, que no depende de lo que decida Shiro y varía mucho de un día a otro. "
  "Para el agente es ruido puro. Por eso se usa la **recompensa centrada**, que conserva solo lo que la acción cambia:",
  alin="j")
codigo([
    "aplazar:     r = (tarifa − 1) · ΔE − λ        # sobrecosto de punta evitado menos la primera hora de espera",
    "ejecutar:    r = −(tarifa − 1) · ΔE           # sobrecosto si se ejecuta en punta (0 en el valle)",
    "no actuar:   r = −λ · pendiente               # cada hora que la carga sigue esperando",
])
P("**Por qué no cambia la política óptima:** en el entorno de réplica el consumo de la casa es el de los datos, sea cual "
  "sea la acción. El término quitado suma lo mismo para cualquier política, así que desplaza todos los valores Q de un "
  "estado en la misma cantidad y el argmax no cambia. Lo que sí cambia es la varianza: el agente deja de intentar "
  "explicar por qué un día la casa consumió más que otro. Siguen prohibidas las recompensas del hallazgo 40 (pagar por "
  "actuar, castigar toda pérdida y la contabilidad ingenua).", alin="j")
H2("4.5 ¿Por qué DQN y no Q-table?")
V_([
    "**La hora exacta y el consumo continuo** entran tal cual, sin discretizar.",
    "**Generaliza:** lo aprendido a las 17:00 informa a las 18:00, y lo aprendido en un día de carga alta a uno parecido.",
    "**Recibe el estado que viene:** la probabilidad calibrada de pico de G0, el tipo de día con su confianza y el clima "
    "son continuos; con una tabla cada uno multiplicaría las celdas.",
    "**Transfiere entre casas:** una red pre-entrenada en el gemelo se puede ajustar en Shiro Home; una tabla de "
    "{n_estados} casillas de este hogar no describe otro.",
    "**Corre en la página y en el hogar:** son unos cinco mil pesos; el cuaderno los exporta a `dqn_pesos.json` para "
    "la consola del parcial.",
])

# =====================================================================================
H1("5. Parte 3 · Prototipo: el DQN de Shiro")
H2("5.1 Entorno, red e hiperparámetros")
P("**Entorno:** el de réplica del Taller 2. Los {n_dias_tr} días de enero–abril se recorren en orden, hora por hora, sin "
  "reiniciar a medianoche (la carga pendiente pasa de un día al siguiente); cada episodio es un día. La política "
  "aprendida se evalúa en los {n_dias_te} días de mayo con la **cuenta real** (costo de toda la energía más λ por hora "
  "de espera), igual que π* y Q-learning.", alin="j")
tabla(["Componente", "Valor", "Por qué"], [
    ["Red", "9 → 64 → 64 → 3, ReLU", "Pequeña: el problema tiene pocas variables y debe correr en la página."],
    ["Pérdida y optimizador", "Huber · Adam (tasa 0,001) · recorte del gradiente en norma 10",
     "Huber y el recorte evitan saltos por recompensas grandes."],
    ["Memoria de experiencias", "20.000 transiciones · lote de 64 · empieza tras 500", "Guarda las últimas horas: más de la mitad del entrenamiento."],
    ["Red objetivo", "Se sincroniza cada 500 actualizaciones", "Blanco quieto unas tres semanas simuladas."],
    ["γ y λ", "0,95 y 0,005 (persona paciente); 0,02 como variante", "Los del Taller 1, para comparar con su π*."],
    ["Exploración", "ε de 1,0 a 0,05 en la primera mitad", "Explora al principio y luego explota."],
    ["Entrenamiento", "{n_ep_dqn} días · {n_semillas} semillas (42 a 46)", "Diez veces menos días que Q-learning."],
    ["Acciones inválidas", "Se enmascaran (Q = −∞)", "Aplazar sin pico o ejecutar sin pendiente no existen."],
], [3.8, 6.0, 6.7], tam=8.5)
P("La red está escrita **en NumPy** (propagación, retropropagación y Adam), sin librerías de aprendizaje profundo: no hubo "
  "que instalar nada, cada operación es visible en el cuaderno y los pesos se pueden ejecutar en JavaScript.", alin="j")

H2("5.2 E1 · La batalla: la red alcanza a la política óptima")
tabla(["Agente", "Días", "Ahorro en mayo", "% del ahorro de π*", "Peor a mejor semilla", "Espera"], [
    ["π* (Taller 1, con el modelo)", "—", "{vi_ahorro_te}", "100 %", "—", "{vi_espera_te}"],
    ["Q-learning recomendado (Taller 2)", "{n_ep_ql}", "{ql_ahorro}", "{ql_captura}", "{ql_ahorro_min} a {ql_ahorro_max}", "{ql_espera}"],
    ["**DQN**", "{n_ep_dqn}", "**{dqn_ahorro}**", "**{dqn_captura}**", "{dqn_ahorro_min} a {dqn_ahorro_max}", "{dqn_espera}"],
    ["Double DQN", "{n_ep_dqn}", "{ddqn_ahorro}", "{ddqn_captura}", "{ddqn_ahorro_min} a {ddqn_ahorro_max}", "{ddqn_espera}"],
    ["Q-learning con recompensa centrada", "{n_ep_ql}", "{qlc_ahorro}", "{qlc_captura}", "{qlc_ahorro_min} a {qlc_ahorro_max}", "{qlc_espera}"],
], [4.8, 1.6, 2.1, 2.4, 3.3, 2.3], tam=8.5)
figura("T5_batalla_mayo.png", "Ahorro de costo en mayo frente a no actuar (media de {n_semillas} semillas). Negro: π*; azul: "
       "redes; gris: Q-learning; naranja: redes sin alguno de sus trucos.", ancho=15)
P("Con {n_ep_dqn} días la red captura el **{dqn_captura}** del ahorro de π*, más que Q-learning con {n_ep_ql}. Su semilla "
  "mediana decide **igual que π*** en todo mayo: la diferencia diaria de su objetivo con el de π* es {boot_dqn_pi}. Frente "
  "a Q-learning tampoco se distingue ({boot_dqn_ql}). La red **no supera** a π* aunque ve la hora exacta: con la persona "
  "paciente aplazar todo pico en punta ya es lo óptimo (hallazgo 33), así que la información extra no tiene dónde rendir. "
  "Double DQN no mejora en este problema ({ddqn_captura}): su peor semilla queda en {ddqn_ahorro_min}.", alin="j")
figura("T1_aprendizaje_dqn.png", "Curva de aprendizaje con la recompensa centrada (media móvil de 50 días, banda entre "
       "semillas), pérdida de Huber y decaimiento de ε.", ancho=16)

H2("5.3 E2 · El arranque en frío, y la sorpresa")
figura("T2_arranque_frio.png", "Porcentaje del ahorro de π* que consigue en mayo cada agente según los días de experiencia "
       "(escala logarítmica; banda entre las {n_semillas} semillas).", ancho=15)
tabla(["Agente", "Días hasta que las 5 semillas capturan ≥ 80 % del ahorro de π* (y no vuelven a bajar)"], [
    ["Q-learning del Taller 2", "{ql_dias80}"],
    ["DQN", "{dqn_dias80}"],
    ["Double DQN", "{ddqn_dias80}"],
    ["**Q-learning con recompensa centrada**", "**{qlc_dias80}**"],
], [6.0, 10.5], tam=9)
P("La red acorta mucho el arranque en frío frente al Taller 2 ({dqn_dias80} frente a {ql_dias80}). Pero el experimento de "
  "control dice **por qué**: el mismo Q-learning de tabla, con la recompensa centrada, llega en **{qlc_dias80}** y "
  "termina en el {qlc_captura}. **El problema del Taller 2 no era la tabla sino el ruido de la recompensa:** el costo de "
  "lo que consume la casa variaba mucho más que las brechas entre acciones, y el agente pasaba miles de días "
  "promediándolo. Esto **corrige el hallazgo 36** del proyecto: el arranque en frío de Shiro Home no exige décadas de "
  "experiencia sino unos meses, siempre que la recompensa esté centrada. Pre-entrenar en el gemelo sigue siendo útil "
  "(evita meses de decisiones malas en una casa real), pero deja de ser una necesidad.", alin="j")

H2("5.4 E3 · Ablación: ¿qué se rompe sin cada truco?")
figura("T3_ablacion.png", "Izquierda: % del ahorro de π* según los días de experiencia, con y sin cada truco. Derecha: "
       "magnitud media de Q en seis estados de prueba durante el entrenamiento.", ancho=16)
tabla(["Configuración", "% del ahorro de π*", "Peor a mejor semilla", "Espera", "Oscilación de Q"], [
    ["Completo (memoria + red objetivo)", "{dqn_captura}", "{dqn_ahorro_min} a {dqn_ahorro_max}", "{dqn_espera}", "{osc_dqn}"],
    ["Sin memoria de experiencias", "{sinr_captura}", "{sinr_ahorro_min} a {sinr_ahorro_max}", "{sinr_espera}", "{osc_sinr}"],
    ["Sin red objetivo", "{sint_captura}", "{sint_ahorro_min} a {sint_ahorro_max}", "{sint_espera}", "{osc_sint}"],
    ["Sin ninguno de los dos", "{sina_captura}", "{sina_ahorro_min} a {sina_ahorro_max}", "{sina_espera}", "{osc_sina}"],
], [5.0, 2.6, 3.4, 2.3, 3.2], tam=8.5)
P("Sin la memoria de experiencias la red entrena con las últimas horas, consecutivas y casi iguales: el resultado depende "
  "de la semilla (su peor semilla ahorra {sinr_ahorro_min}). Sin la red objetivo el promedio cae menos ({sint_captura}) pero "
  "el valor Q oscila el doble. **Sin ninguno de los dos** la red captura el {sina_captura}, hay semillas que no ahorran "
  "nada ({sina_ahorro_min}), la espera sube a {sina_espera} y la oscilación de Q es más de cuatro veces la del agente "
  "completo. La oscilación es la desviación de los cambios día a día de |Q| en los últimos 300 días. Es la Parte 1 "
  "demostrada con los datos de Shiro.", alin="j")

H2("5.5 E4 · Lo que la tabla no veía: la decisión hora por hora")
figura("T4_mapa_horario.png", "Arriba: ventaja de aplazar frente a no actuar cuando hay un pico, por hora. Abajo: ventaja de "
       "ejecutar frente a esperar cuando hay una carga pendiente, por hora y horas de espera. Media de {n_semillas} "
       "semillas; franja verde = valle.", ancho=16)
P("La red, a diferencia de la tabla, puede decidir distinto **dentro de una misma franja**:", alin="j")
V_([
    "**Persona paciente (λ = 0,005):** aplaza un pico en las {e4_pac_punta_aplaza} horas de punta. Con una carga "
    "pendiente solo ejecuta en el valle ({e4_pac_ejec_rango}): esperar le cuesta poco.",
    "**Persona exigente (λ = 0,02):** aplaza un pico en {e4_ex_punta_aplaza} de las 18 horas de punta, solo desde las "
    "**{e4_ex_desde}**. La cuenta a mano lo confirma: aplazar evita un sobrecosto de {sobrecosto_kwh}, que paga como "
    "mucho {e4_ex_umbral_h} de espera a λ = 0,02; como el valle empieza a las 0:00, aplazar conviene desde las "
    "{e4_ex_hora_teorica}. **La red encontró ese punto sola, hora por hora.** La tabla no podía, porque veía toda la "
    "tarde (12:00 a 17:59) como una casilla. Con una carga pendiente ejecuta en {e4_ex_ejec_horas} horas "
    "({e4_ex_ejec_rango}): en la mañana esperar hasta la madrugada le cuesta más que el sobrecosto.",
    "**Advertencia honesta:** en la madrugada nunca hubo picos en enero–abril, así que la ventaja de aplazar a esas horas "
    "es una **extrapolación** de la red (y en el valle aplazar no ahorra nada). En la consola esas celdas se muestran "
    "como fuera de los datos.",
])
P("Con la persona exigente la red captura el {dqnx_captura} del ahorro de su propia π* (λ = 0,02), con {dqnx_espera} de "
  "espera frente a {vi_ex_espera_te} de π*.", alin="j")

# =====================================================================================
H1("6. Qué cambia en el diseño de Shiro por estos números")
recuadro("Decisiones que quedan tomadas", [
    "**La recompensa centrada es obligatoria** en todo agente de Shiro que aprenda: con ella la tabla pasa de {ql_dias80} "
    "a {qlc_dias80} para capturar el 80 % del ahorro. Corrige el hallazgo 36: el arranque en frío es de meses, no de "
    "décadas.",
    "**Para los {n_estados} estados de hoy basta la tabla:** es la más rápida ({qlc_dias80}), llega al {qlc_captura} y es "
    "la más explicable.",
    "**La red se justifica por el estado que viene:** la hora exacta (la persona exigente aplaza solo desde las "
    "{e4_ex_desde}), la probabilidad de pico de G0, el clima y otras casas. Ya alcanza a π* con {n_ep_dqn} días.",
    "**Memoria de experiencias y red objetivo son imprescindibles** en la red; Double DQN no aporta con estos datos.",
    "**Consola del parcial:** π* (exacta), Q-learning y la red DQN lado a lado; la red corre en la página con "
    "`dqn_pesos.json`, y las horas sin datos (madrugada con pico) se marcan como extrapolación.",
])
recuadro("Límites que se declaran", [
    "**Ahorro simulado y pequeño:** π* ahorra el {vi_ahorro_te} en mayo y no se distingue de no actuar (Taller 1). La red "
    "aprende bien una decisión que, con esta tarifa y este hogar, mueve poco (hallazgos 31 y 33).",
    "**El estado continuo convive con reglas discretas:** aplazar solo es válido con nivel alto (> 200 Wh), como en el "
    "MDP; la red decide cuándo, no redefine qué es un pico.",
    "ΔE constante y consumo independiente de la acción, como en los talleres 1 y 2. Una sola vivienda.",
    "{n_semillas} semillas por configuración; solo la batalla final lleva intervalo de confianza (bootstrap pareado por "
    "día, 2.000 réplicas).",
    "No se probó γ = 0,99 con la red (quedó como experimento opcional del plan); el Taller 2 mostró que con tabla se ahoga "
    "en ruido.",
    "Los pesos exportados son los de la semilla mediana; otra semilla puede decidir distinto en estados poco visitados.",
], color=NARANJA)

H1("7. Reproducibilidad")
V_([
    "`Taller3_C3_DQN_Shiro.ipynb`: entorno, anclas, red en NumPy y los experimentos E1–E4. Corre de principio a fin y "
    "escribe `cifras.json`, `dqn_pesos.json`, `resumen_agentes.csv` y las figuras T0–T5.",
    "`generadores/`: construye y ejecuta el cuaderno, este documento y el material del video (diapositivas y guion). "
    "Todas las cifras salen de `cifras.json` de este taller y de los talleres 1 y 2.",
    "Datos: `data set/energydata_complete.csv` (UCI n.º 374). Semillas 42 a 46.",
])

H1("Referencias")
for ref in [
    "Candanedo, L. M., Feldheim, V., y Deramaix, D. (2017). Data driven prediction models of energy use of appliances in a "
    "low-energy house. *Energy and Buildings, 140*, 81–97.",
    "Lin, L.-J. (1992). Self-improving reactive agents based on reinforcement learning, planning and teaching. *Machine "
    "Learning, 8*, 293–321.",
    "Mnih, V., Kavukcuoglu, K., Silver, D., et al. (2015). Human-level control through deep reinforcement learning. "
    "*Nature, 518*, 529–533.",
    "Sutton, R. S., y Barto, A. G. (2018). *Reinforcement learning: An introduction* (2.ª ed.). MIT Press.",
    "van Hasselt, H., Guez, A., y Silver, D. (2016). Deep reinforcement learning with double Q-learning. *Proceedings of "
    "the AAAI Conference on Artificial Intelligence, 30*(1).",
    "Watkins, C. J. C. H., y Dayan, P. (1992). Q-learning. *Machine Learning, 8*, 279–292.",
]:
    P(ref, tam=9.5, despues=3)


def main():
    doc.save(SALIDA)
    print(f"Documento: {SALIDA.name}")
    pdf = exportar_pdf(SALIDA, SALIDA.with_suffix(".pdf"))
    print(f"PDF: {pdf.name}")


if __name__ == "__main__":
    main()
