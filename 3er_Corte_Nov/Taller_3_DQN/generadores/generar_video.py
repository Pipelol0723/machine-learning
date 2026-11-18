# -*- coding: utf-8 -*-
r"""Genera el material del video del Taller 3 (C3): diapositivas, imágenes por diapositiva y guion con reparto.

Salidas (todas desde cifras.json y figuras/; ninguna cifra escrita a mano):
    Taller3_C3_video_diapositivas.pptx/.pdf   13 diapositivas 16:9, con la narración en las notas
    video/diapositivas_png/diapositiva_NN.png 1920 px de ancho, una por diapositiva
    video/textos/diapositiva_NN_<narrador>.txt el texto que se dice en cada diapositiva
    video/guion.json                          narrador, texto, palabras y segundos estimados por diapositiva
    Guion_Video_Taller3_C3.docx/.pdf          guion con reparto para el grupo

Uso (desde la carpeta del taller):
    C:\Users\pipel\venvs\ml\Scripts\python.exe generadores\generar_video.py
"""
import json
import re
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Cm, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import RAIZ, F, exportar_pdf  # noqa: E402

SALIDA = RAIZ / "Taller3_C3_video_diapositivas.pptx"
FIG = RAIZ / "figuras"
AZUL, VERDE, NARANJA, GRIS, BLANCO = "1F3864", "E8F3E8", "FDF2E3", "F2F2F2", "FFFFFF"

prs = Presentation()
prs.slide_width, prs.slide_height = Cm(33.867), Cm(19.05)
W, H = prs.slide_width, prs.slide_height
VACIA = prs.slide_layouts[6]


def _rgb(h):
    return RGBColor.from_string(h)


def _texto(tf, lineas, tam=16, color="000000", viñetas=True, espacio=6):
    tf.word_wrap = True
    for i, ln in enumerate(lineas):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(espacio)
        ln = F(ln).replace("π\\*", "π∗").replace("π*", "π∗").replace("V*", "V∗")
        if viñetas:
            ln = "• " + ln
        for trozo in re.split(r"(\*\*[^*]+\*\*)", ln):
            if not trozo:
                continue
            r = p.add_run()
            r.text = trozo[2:-2] if trozo.startswith("**") else trozo
            r.font.size = Pt(tam); r.font.bold = trozo.startswith("**"); r.font.color.rgb = _rgb(color)
            r.font.name = "Calibri"


def diapositiva(titulo, notas=""):
    s = prs.slides.add_slide(VACIA)
    barra = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, Cm(2.4))
    barra.fill.solid(); barra.fill.fore_color.rgb = _rgb(AZUL); barra.line.fill.background()
    tb = s.shapes.add_textbox(Cm(1.2), Cm(0.35), W - Cm(2.4), Cm(1.8))
    _texto(tb.text_frame, [titulo], tam=26, color=BLANCO, viñetas=False)
    tb.text_frame.paragraphs[0].runs[0].font.bold = True
    pie = s.shapes.add_textbox(Cm(1.2), H - Cm(1.0), W - Cm(2.4), Cm(0.8))
    _texto(pie.text_frame, ["Shiro Twin · Taller 3, 3.er corte (DQN) · Aprendizaje de Máquina 26-2 · Universidad Sergio Arboleda"],
           tam=9, color="7F7F7F", viñetas=False)
    if notas:
        s.notes_slide.notes_text_frame.text = F(notas)
    return s


def caja(s, x, y, w, h, lineas, color=None, tam=16, viñetas=True, titulo=None):
    if color:
        r = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
        r.fill.solid(); r.fill.fore_color.rgb = _rgb(color); r.line.fill.background()
        r.adjustments[0] = 0.05
    tb = s.shapes.add_textbox(x + Cm(0.4), y + Cm(0.3), w - Cm(0.8), h - Cm(0.6))
    if titulo:
        lineas = ["**" + titulo + "**"] + lineas
        _texto(tb.text_frame, lineas[:1], tam=tam + 1, viñetas=False)
        _texto_extra(tb.text_frame, lineas[1:], tam, viñetas)
    else:
        _texto(tb.text_frame, lineas, tam=tam, viñetas=viñetas)
    return tb


def _texto_extra(tf, lineas, tam, viñetas):
    for ln in lineas:
        p = tf.add_paragraph(); p.space_after = Pt(5)
        ln = F(ln).replace("π\\*", "π∗").replace("π*", "π∗").replace("V*", "V∗")
        if viñetas:
            ln = "• " + ln
        for trozo in re.split(r"(\*\*[^*]+\*\*)", ln):
            if not trozo:
                continue
            r = p.add_run(); r.text = trozo[2:-2] if trozo.startswith("**") else trozo
            r.font.size = Pt(tam); r.font.bold = trozo.startswith("**"); r.font.name = "Calibri"


def imagen(s, archivo, x, y, w=None, h=None):
    return s.shapes.add_picture(str(FIG / archivo), x, y, width=w, height=h)


def tabla(s, x, y, w, enc, filas, anchos, tam=12):
    t = s.shapes.add_table(len(filas) + 1, len(enc), x, y, w, Cm(1.0 * (len(filas) + 1))).table
    for j, e in enumerate(enc):
        c = t.cell(0, j); c.text = F(e)
        c.fill.solid(); c.fill.fore_color.rgb = _rgb(AZUL)
        for p in c.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(tam); r.font.bold = True; r.font.color.rgb = _rgb(BLANCO)
    for i, fila in enumerate(filas, start=1):
        for j, v in enumerate(fila):
            c = t.cell(i, j); c.text = F(str(v)).replace("π*", "π∗")
            c.fill.solid(); c.fill.fore_color.rgb = _rgb(GRIS if i % 2 else BLANCO)
            for p in c.text_frame.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(tam)
    for j, a in enumerate(anchos):
        t.columns[j].width = Cm(a)
    return t


# =====================================================================================
# Guion: una entrada por diapositiva (narrador y texto que se dice). La duración se estima a 2,4 palabras por segundo.
# =====================================================================================
GUION = []


def g(narrador, texto):
    GUION.append({"narrador": narrador, "texto": F(texto)})


# 1 · Portada ------------------------------------------------------------------------------------------------
s = prs.slides.add_slide(VACIA)
fondo = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, H); fondo.fill.solid(); fondo.fill.fore_color.rgb = _rgb(AZUL)
fondo.line.fill.background()
tb = s.shapes.add_textbox(Cm(2), Cm(4.2), W - Cm(4), Cm(8))
_texto(tb.text_frame, ["Shiro Twin", "De la Q-table a la red: el agente con estado continuo (DQN)"], tam=40, color=BLANCO, viñetas=False)
tb.text_frame.paragraphs[1].runs[0].font.size = Pt(24)
tb2 = s.shapes.add_textbox(Cm(2), Cm(11.5), W - Cm(4), Cm(5))
_texto(tb2.text_frame, ["Taller 3 · 3.er corte (Aprendizaje por Refuerzo) · Aprendizaje de Máquina 26-2",
                        "Grupo Shiro: Jose Leonardo Diazgranados · Sofía Londoño · Andrés Felipe Céspedes Rondón · Alex Duran",
                        "Docente: Hernán Darío Cruz Bueno · Universidad Sergio Arboleda · noviembre de 2026"], tam=15, color="D9E1F2", viñetas=False)
g("Jose", "Hola, somos el grupo Shiro: Jose, Sofía, Andrés y Alex. En este video presentamos el Taller 3 del tercer corte: "
  "de Q-learning a Deep Q-Networks, aplicado al agente de Shiro, que decide cada hora si conviene aplazar el consumo de un hogar.")

# 2 · Qué le falta a Shiro ----------------------------------------------------------------------------------
s = diapositiva("Qué le falta a Shiro: un agente que aprenda rápido y vea el estado completo")
caja(s, Cm(1.2), Cm(3.2), Cm(15.3), Cm(13.8), [
    "**Taller 1:** MDP de {n_estados} estados resuelto con iteración de valor → π* ahorra **{vi_ahorro_te}** en mayo.",
    "**Taller 2:** Q-learning aprende sin modelo, pero con **{n_ep_ql} días** (≈ {t2:anos_rec}) no llega al 90 %.",
    "La tabla solo ve la **franja** (bloques de 6 h), no la hora.",
], color=GRIS, tam=21, titulo="Lo que ya tenemos")
caja(s, Cm(17.3), Cm(3.2), Cm(15.3), Cm(13.8), [
    "¿Una **red** acorta el arranque en frío?",
    "¿La **hora exacta** cambia la decisión?",
    "¿Qué **trucos de estabilidad** son imprescindibles?",
    "¿Qué agente usará la **consola del parcial**?",
], color=VERDE, tam=21, titulo="Preguntas de este taller")
g("Jose", "Shiro es el gemelo digital de un hogar. En el Taller 1 resolvimos su problema de decisión con iteración de valor: "
  "cuarenta estados y una política óptima que en mayo ahorra el {vi_ahorro_te} del costo. En el Taller 2 el agente aprendió "
  "sin conocer el modelo, con Q-learning, pero necesitó {n_ep_ql} días simulados, unos {t2:anos_rec} de experiencia real, "
  "y aun así no llegó al noventa por ciento de acierto. Hoy preguntamos: ¿una red neuronal resuelve eso? ¿Y qué gana Shiro "
  "cuando ve la hora exacta en vez de la franja? Primero Sofía explica la investigación; después Alex muestra cómo se aplica "
  "a nuestro sector, y Andrés presenta el prototipo y sus resultados. Al final contamos qué cambia en Shiro.")

# 3 · Parte 1: por qué falla la tabla -------------------------------------------------------------------------
s = diapositiva("Parte 1 · ¿Por qué la Q-table no escala?")
caja(s, Cm(1.2), Cm(3.2), Cm(15.3), Cm(13.8), [
    "Una **celda por cada combinación** de estado y acción.",
    "No **generaliza**: las 17:00 y las 18:00 son celdas distintas aunque se parezcan.",
    "Cada variable nueva **multiplica** las celdas: con la hora (24) en vez de la franja, 40 estados pasan a cientos.",
], color=GRIS, tam=21, titulo="La tabla")
caja(s, Cm(17.3), Cm(3.2), Cm(15.3), Cm(13.8), [
    "Con **solo {n_estados} estados**, Q-learning necesitó **{n_ep_ql} días** sin llegar al 90 %.",
    "El estado real de Shiro es **continuo**: hora, consumo, confianza del tipo de día, probabilidad de pico.",
    "Ese estado no cabe en ninguna tabla.",
], color=NARANJA, tam=21, titulo="La evidencia de Shiro")
g("Sofía", "La Q-table guarda un valor por cada combinación de estado y acción. Eso tiene dos problemas. Primero, no generaliza: "
  "para la tabla, las cinco y las seis de la tarde son celdas distintas, aunque se parezcan. Segundo, cada variable nueva "
  "multiplica el número de celdas. Nosotros lo medimos: con solo cuarenta estados, Q-learning necesitó {n_ep_ql} días y no "
  "llegó al noventa por ciento. Y el estado real de Shiro es continuo: la hora, el consumo, la confianza en el tipo de día. "
  "Eso no cabe en ninguna tabla.")

# 4 · Parte 1: la red reemplaza a la tabla ---------------------------------------------------------------------
s = diapositiva("Parte 1 · La pieza central: una red en lugar de la tabla")
imagen(s, "T0_esquema_dqn.png", Cm(1.0), Cm(2.9), w=Cm(31.8))
g("Sofía", "La pieza central de DQN es una red neuronal que reemplaza a la tabla. Recibe el estado como un vector de "
  "{n_rasgos} números y devuelve, de una vez, el valor Q de cada acción: no actuar, aplazar y ejecutar. Su papel no es "
  "memorizar celdas sino generalizar: si aprende que a las cinco de la tarde conviene aplazar, lo extiende a las seis. "
  "¿Cómo aprende? Compara lo que predice con el objetivo de Bellman, que es la recompensa más el valor descontado del "
  "estado siguiente, y corrige sus pesos con descenso de gradiente. "
  "La escribimos en NumPy, sin librerías de aprendizaje profundo, para que sus pesos puedan correr en la consola del parcial.")

# 5 · Parte 1: los dos trucos ------------------------------------------------------------------------------------
s = diapositiva("Parte 1 · Los dos trucos que la hacen estable")
caja(s, Cm(1.2), Cm(3.2), Cm(15.3), Cm(13.8), [
    "Guarda las transiciones (estado, acción, recompensa, siguiente).",
    "Entrena con **lotes al azar**: rompe la correlación entre horas consecutivas, que son casi idénticas.",
    "**Reutiliza** cada día muchas veces: menos días de experiencia.",
], color=GRIS, tam=20, titulo="Memoria de experiencias (experience replay)")
caja(s, Cm(17.3), Cm(3.2), Cm(15.3), Cm(13.8), [
    "Una **copia congelada** de la red calcula el objetivo r + γ·max Q(s′).",
    "Se sincroniza cada 500 actualizaciones.",
    "Sin ella, el objetivo **se mueve** con cada paso: la red persigue su propia sombra.",
], color=VERDE, tam=20, titulo="Red objetivo fija")
g("Sofía", "Pero reemplazar la tabla por una red no basta: sin ayuda, el entrenamiento es inestable. El primer truco es la "
  "memoria de experiencias: guardamos veinte mil transiciones y entrenamos con lotes tomados al azar. Así se rompe la "
  "correlación entre horas consecutivas, que son casi idénticas, y cada día se reutiliza muchas veces. El segundo truco es "
  "la red objetivo: una copia congelada que calcula el objetivo y se actualiza cada quinientos pasos. Sin ella, el objetivo "
  "se mueve con cada actualización. Probamos además una variante, Double DQN, que separa quién elige la acción siguiente de "
  "quién la evalúa, para reducir la sobreestimación que medimos en el Taller 2. En la Parte 3 mostramos qué pasa si "
  "quitamos cada truco.")

# 6 · Parte 2: el problema --------------------------------------------------------------------------------------------
s = diapositiva("Parte 2 · Aplicación al sector: Shiro Home")
caja(s, Cm(1.2), Cm(3.2), Cm(12.6), Cm(13.8), [
    "Cada hora, decidir qué hacer con la **carga desplazable** del hogar (lavadora, secadora, horno).",
    "Minimizar el costo de la energía **sin imponer esperas largas**.",
    "Shiro propone; la persona aprueba.",
], color=GRIS, tam=19, titulo="El problema")
caja(s, Cm(14.4), Cm(3.2), Cm(9.4), Cm(13.8), [
    "Hora (seno y coseno)", "Consumo actual y anterior", "Margen de K-Means (¿día de carga alta?)", "Tarifa vigente",
    "Carga pendiente y horas de espera", "Nivel alto (> 200 Wh)",
], color=VERDE, tam=17, titulo="Estado: {n_rasgos} números")
caja(s, Cm(24.4), Cm(3.2), Cm(8.2), Cm(13.8), ["No actuar", "Aplazar el pico", "Ejecutar lo pendiente"], color=NARANJA, tam=19, titulo="Acciones")
g("Alex", "Ahora, el sector. El problema de Shiro Home es decidir cada hora qué hacer con la carga que se puede mover, como la "
  "lavadora o la secadora, para pagar menos energía sin obligar a la persona a esperar demasiado. El agente ve un vector de "
  "{n_rasgos} números: la hora como seno y coseno, el consumo de la hora actual y la anterior, qué tanto se parece el día a "
  "uno de carga alta según K-Means, la tarifa, si hay una carga esperando y desde hace cuánto, y si hay un pico. Y tiene tres "
  "acciones: no actuar, aplazar el pico o ejecutar lo pendiente.")

# 7 · Parte 2: recompensa y por qué DQN ---------------------------------------------------------------------------
s = diapositiva("Parte 2 · Recompensa y por qué DQN")
caja(s, Cm(1.2), Cm(3.2), Cm(15.3), Cm(13.8), [
    "Aplazar: + sobrecosto de punta evitado − λ por cada hora de espera.",
    "Ejecutar en punta: − el sobrecosto.",
    "**Centrada:** el costo de lo que consume la casa no depende de Shiro → se quita. **Misma política óptima, mucho menos ruido.**",
    "Prohibidas: pagar por actuar o castigar toda pérdida (Taller 2).",
], color=GRIS, tam=18, titulo="Recompensa")
caja(s, Cm(17.3), Cm(3.2), Cm(15.3), Cm(13.8), [
    "La tabla necesita demasiados días.",
    "No ve la hora exacta: decide igual a las 13:00 que a las 17:00.",
    "No transfiere lo aprendido entre estados parecidos ni entre casas.",
    "El estado que viene (probabilidad de pico, confianza, clima) es continuo.",
], color=VERDE, tam=18, titulo="¿Por qué DQN y no una tabla?")
g("Alex", "La recompensa premia el sobrecosto de punta que se evita al aplazar y castiga cada hora de espera. Aquí hicimos un "
  "cambio importante: el costo de lo que consume la casa no depende de lo que decida Shiro, así que lo quitamos de la "
  "recompensa. La política óptima es exactamente la misma, pero el agente deja de aprender ruido. Es una lección que se "
  "repite en todo el semestre: el agente optimiza exactamente lo que se le pide, así que la recompensa debe medir solo lo "
  "que su decisión puede cambiar. ¿Y por qué DQN? Porque la "
  "tabla necesita demasiados días, no ve la hora exacta, no transfiere lo aprendido, y el estado que viene es continuo.")

# 8 · Parte 3: del Taller 1 al 3 ---------------------------------------------------------------------------------------
s = diapositiva("Parte 3 · El prototipo evoluciona: Taller 1 → Taller 2 → Taller 3")
tabla(s, Cm(1.2), Cm(3.2), Cm(31.4), ["", "Taller 1", "Taller 2", "Taller 3"], [
    ["Agente", "Iteración de valor (con modelo)", "Q-learning (tabla)", "DQN (red, en NumPy)"],
    ["Estado", "{n_estados} estados discretos", "{n_estados} estados discretos", "{n_rasgos} números continuos"],
    ["Aprende con", "La tabla P contada", "{n_ep_ql} días simulados", "{n_ep_dqn} días simulados"],
    ["Datos", "Enero–abril aprende · mayo evalúa", "Igual", "Igual"],
], [5.0, 8.8, 8.8, 8.8], tam=15)
caja(s, Cm(1.2), Cm(10.6), Cm(31.4), Cm(6.4), [
    "Mismos datos, tarifa, ΔE ({DE}) y λ. **{n_anclas} anclas** comprueban que el entorno reproduce los talleres 1 y 2.",
    "{n_semillas} semillas por configuración; ahorro medido en mayo con la cuenta real.",
], color=VERDE, tam=18)
g("Andrés", "Pasamos al prototipo. Es la evolución de los dos talleres anteriores: mismos datos, misma tarifa y mismo costo de "
  "espera. El agente aprende con enero a abril y se evalúa en mayo, un mes que nunca vio. Antes de entrenar, {n_anclas} "
  "anclas comprueban que el entorno reproduce exactamente los resultados de los talleres 1 y 2. Todo está escrito en NumPy: "
  "la red, la retropropagación y el optimizador Adam. Y cada configuración se entrena con {n_semillas} semillas distintas, "
  "para no confundir un buen resultado con suerte.")

# 9 · E1 batalla --------------------------------------------------------------------------------------------------------
s = diapositiva("Parte 3 · E1: la red alcanza a la política óptima")
imagen(s, "T5_batalla_mayo.png", Cm(0.8), Cm(3.4), w=Cm(20.2))
caja(s, Cm(21.4), Cm(3.0), Cm(11.2), Cm(14.2), [
    "**DQN, {n_ep_dqn} días:** captura el **{dqn_captura}** del ahorro de π*.",
    "La semilla mediana decide **igual que π*** en todo mayo.",
    "Q-learning del Taller 2: {ql_captura} con {n_ep_ql} días.",
    "Double DQN: {ddqn_captura}; no mejora aquí.",
], color=GRIS, tam=16)
g("Andrés", "Primer experimento, la batalla en mayo. La red, con {n_ep_dqn} días de entrenamiento, consigue el {dqn_captura} "
  "del ahorro de la política óptima, y la semilla mediana toma exactamente las mismas decisiones que ella durante todo el "
  "mes: comparadas día por día con un bootstrap, la diferencia es cero. Q-learning del Taller 2 se quedaba en el "
  "{ql_captura} con diez veces más días. La variante Double DQN no mejora en este problema: una de sus semillas se queda "
  "atrás.")

# 10 · E2 arranque en frío ------------------------------------------------------------------------------------------------
s = diapositiva("Parte 3 · E2: el arranque en frío y la sorpresa")
imagen(s, "T2_arranque_frio.png", Cm(0.8), Cm(2.9), w=Cm(21.0))
caja(s, Cm(22.2), Cm(3.0), Cm(10.4), Cm(14.2), [
    "Días hasta el 80 % del ahorro de π* (las 5 semillas):",
    "Q-learning del Taller 2: **{ql_dias80}**.",
    "DQN: **{dqn_dias80}**.",
    "**Q-learning con recompensa centrada: {qlc_dias80}**, y llega al {qlc_captura}.",
    "→ El problema del Taller 2 era el **ruido** de la recompensa, no la tabla.",
], color=VERDE, tam=16)
g("Andrés", "Segundo experimento, el arranque en frío: cuántos días necesita cada agente para conseguir el ochenta por ciento "
  "del ahorro óptimo. Q-learning del Taller 2 necesitaba {ql_dias80}. La red, {dqn_dias80}. Y aquí viene la sorpresa: el "
  "mismo Q-learning de tabla, con la recompensa centrada, lo logra en {qlc_dias80} y termina en el {qlc_captura}. El "
  "problema del Taller 2 no era la tabla: era el ruido de la recompensa. Para Shiro Home eso significa pasar de décadas a "
  "unos meses de experiencia.")

# 11 · E3 ablación ----------------------------------------------------------------------------------------------------------
s = diapositiva("Parte 3 · E3: ¿qué se rompe si quitamos cada truco?")
imagen(s, "T3_ablacion.png", Cm(0.8), Cm(2.7), h=Cm(9.4))
tabla(s, Cm(1.2), Cm(12.4), Cm(31.4), ["Configuración", "Ahorro de π* capturado", "Ahorro en mayo, peor a mejor semilla",
                                         "Espera"], [
    ["Completo (memoria + red objetivo)", "{dqn_captura}", "{dqn_ahorro_min} a {dqn_ahorro_max}", "{dqn_espera}"],
    ["Sin memoria de experiencias", "{sinr_captura}", "{sinr_ahorro_min} a {sinr_ahorro_max}", "{sinr_espera}"],
    ["Sin red objetivo", "{sint_captura}", "{sint_ahorro_min} a {sint_ahorro_max}", "{sint_espera}"],
    ["Sin ninguno de los dos", "{sina_captura}", "{sina_ahorro_min} a {sina_ahorro_max}", "{sina_espera}"],
], [10.0, 6.6, 9.0, 5.8], tam=11)
g("Andrés", "Tercer experimento: quitamos los trucos. Sin la memoria de experiencias, la red baja al {sinr_captura} y se vuelve "
  "inestable entre semillas. Sin la red objetivo, al {sint_captura}. Y sin ninguno de los dos, al {sina_captura}, con "
  "semillas que no ahorran nada y una espera de {sina_espera}. A la derecha se ve por qué: el valor Q oscila mucho más. "
  "Los dos trucos no son adornos: son lo que hace que la red aprenda.")

# 12 · E4 hora por hora -------------------------------------------------------------------------------------------------------
s = diapositiva("Parte 3 · E4: lo que la tabla no veía, la decisión hora por hora")
imagen(s, "T4_mapa_horario.png", Cm(0.6), Cm(2.8), h=Cm(14.6))
caja(s, Cm(23.6), Cm(3.0), Cm(9.0), Cm(14.2), [
    "Persona exigente (λ = 0,02): aplaza picos **desde las {e4_ex_desde}**. La cuenta a mano pone el equilibrio a las "
    "**{e4_ex_hora_teorica}**: la red lo encontró sola.",
    "Con carga pendiente: la paciente espera a la madrugada; la exigente ejecuta también en la mañana ({e4_ex_ejec_rango}).",
    "De madrugada nunca hubo picos: ahí la red **extrapola**.",
], color=GRIS, tam=14)
g("Andrés", "Cuarto experimento: lo que la tabla no veía. La red decide hora por hora. Para una persona exigente, que valora "
  "más su tiempo, la red solo aplaza los picos desde las {e4_ex_desde}. Y no es casualidad: el sobrecosto que se evita paga "
  "como mucho {e4_ex_umbral_h} de espera, así que aplazar conviene desde las {e4_ex_hora_teorica}. La red lo descubrió sola; "
  "la tabla, que veía toda la tarde como una sola casilla, no podía. Con una carga pendiente, la persona paciente espera "
  "siempre a la madrugada, y la exigente la ejecuta también en la mañana, porque esperar quince horas le cuesta más que el "
  "sobrecosto. Una advertencia honesta: de madrugada nunca hubo picos en los datos, así que ahí la red extrapola.")

# 13 · Cierre -----------------------------------------------------------------------------------------------------------------------
s = diapositiva("Qué cambia en Shiro por estos resultados")
caja(s, Cm(1.2), Cm(3.2), Cm(31.4), Cm(13.8), [
    "**La recompensa centrada es obligatoria:** sin ella ningún agente aprende rápido.",
    "**Con {n_estados} estados basta la tabla** (con recompensa centrada): es lo más rápido y lo más explicable.",
    "**La red es para el estado que viene:** la hora exacta, la probabilidad de pico de Guardian, otras casas.",
    "**Memoria de experiencias y red objetivo son imprescindibles** en la red.",
    "La **consola del parcial** ejecutará esta red en la página, junto a la política óptima y a Q-learning.",
], color=VERDE, tam=21, titulo="Decisiones para Shiro")
g("Alex", "Para cerrar, lo que cambia en Shiro. Primero, la recompensa centrada es obligatoria: sin ella ningún agente aprende "
  "rápido. Segundo, con cuarenta estados basta la tabla, que es lo más rápido y lo más explicable. Tercero, la red se "
  "justifica por el estado que viene: la hora exacta, la probabilidad de pico de Guardian, otras casas. Y los dos trucos "
  "son imprescindibles. Y un límite que no escondemos: el ahorro es pequeño, el {vi_ahorro_te} en mayo, porque en esta casa "
  "aplazar mueve poco; el techo está en saber qué aparato se enciende. En el parcial, la consola de Shiro ejecutará esta red "
  "en la página, junto a la política óptima. Gracias.")


def main():
    assert len(GUION) == len(prs.slides), "Cada diapositiva debe tener su bloque de guion"
    for diap, e in zip(prs.slides, GUION):
        diap.notes_slide.notes_text_frame.text = f"[{e['narrador']}] {e['texto']}"
    prs.save(SALIDA)
    pdf = exportar_pdf(SALIDA, SALIDA.with_suffix(".pdf"))
    import pymupdf
    carpeta_png = RAIZ / "video" / "diapositivas_png"; carpeta_png.mkdir(parents=True, exist_ok=True)
    d = pymupdf.open(pdf); zoom = 1920 / d[0].rect.width
    for i, pg in enumerate(d):
        pg.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom)).save(carpeta_png / f"diapositiva_{i + 1:02d}.png")
    total = 0
    for i, e in enumerate(GUION):
        e["n"] = i + 1; e["palabras"] = len(e["texto"].split()); e["segundos"] = round(e["palabras"] / 2.4)
        e["png"] = f"diapositivas_png/diapositiva_{i + 1:02d}.png"; total += e["segundos"]
        (RAIZ / "video" / "textos").mkdir(exist_ok=True)
        (RAIZ / "video" / "textos" / f"diapositiva_{i + 1:02d}_{e['narrador']}.txt").write_text(e["texto"], encoding="utf-8")
    (RAIZ / "video" / "guion.json").write_text(json.dumps({"total_segundos": total, "diapositivas": GUION}, ensure_ascii=False, indent=1),
                                               encoding="utf-8")
    md = [f"# Guion del video · Taller 3 del 3.er corte (DQN) · Grupo Shiro", "",
          f"Duración estimada: {total // 60} min {total % 60} s (2,4 palabras por segundo). Una toma por diapositiva, "
          "nombrada NN_nombre (por ejemplo 03_sofia.m4a). Se lee solo el texto de cada bloque, sin el número ni el narrador.", ""]
    for nombre in ("Jose", "Sofía", "Alex", "Andrés"):
        bl = [e for e in GUION if e["narrador"] == nombre]
        md.append(f"- **{nombre}:** diapositivas {', '.join(str(e['n']) for e in bl)} · ≈ {sum(e['segundos'] for e in bl)} s")
    md.append("")
    for e in GUION:
        md += [f"## {e['n']:02d} · {e['narrador']} · ≈ {e['segundos']} s", "", e["texto"], ""]
    (RAIZ / "video" / "guion.md").write_text("\n".join(md), encoding="utf-8")
    print(f"Diapositivas: {SALIDA.name} ({len(prs.slides)}) · PNG 1920 px · guion.json y guion.md: {len(GUION)} bloques, ≈ {total // 60} min {total % 60} s")
    assert len(GUION) == len(prs.slides), "Cada diapositiva debe tener su bloque de guion"
    guion_docx(total)


def guion_docx(total):
    from docx import Document
    from docx.shared import Pt, Cm as DCm
    doc = Document()
    for sec in doc.sections:
        sec.left_margin = sec.right_margin = DCm(2.0); sec.top_margin = sec.bottom_margin = DCm(1.8)
    doc.styles["Normal"].font.name = "Calibri"; doc.styles["Normal"].font.size = Pt(11)
    doc.add_heading("Guion del video · Taller 3 del 3.er corte (DQN) · Grupo Shiro", level=1)
    doc.add_paragraph(F(f"Duración estimada: {total // 60} min {total % 60} s (a 2,4 palabras por segundo). Cada integrante graba sus "
                        "bloques en el orden indicado. Las diapositivas están en video/diapositivas_png/ y el texto de cada bloque en "
                        "video/textos/."))
    t = doc.add_table(rows=1, cols=4); t.style = "Table Grid"
    for j, e in enumerate(("#", "Narrador", "Duración", "Texto que se dice")):
        t.rows[0].cells[j].text = e
    for e in GUION:
        c = t.add_row().cells
        c[0].text = str(e["n"]); c[1].text = e["narrador"]; c[2].text = f"≈ {e['segundos']} s"; c[3].text = e["texto"]
    for fila in t.rows:
        for j, w in enumerate((1.0, 2.2, 2.0, 12.0)):
            fila.cells[j].width = DCm(w)
    doc.add_heading("Reparto por integrante", level=2)
    for nombre in ("Jose", "Sofía", "Alex", "Andrés"):
        bloques = [e for e in GUION if e["narrador"] == nombre]
        doc.add_paragraph(f"{nombre}: diapositivas {', '.join(str(e['n']) for e in bloques)} · ≈ {sum(e['segundos'] for e in bloques)} s")
    salida = RAIZ / "Guion_Video_Taller3_C3.docx"; doc.save(salida); exportar_pdf(salida, salida.with_suffix(".pdf"))
    print(f"Guion: {salida.name} y su PDF")


if __name__ == "__main__":
    main()
