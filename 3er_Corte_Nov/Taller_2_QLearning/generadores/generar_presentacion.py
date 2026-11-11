# -*- coding: utf-8 -*-
"""Genera Taller2_C3_presentacion.pptx (y su PDF) desde cifras.json y figuras/.

Uso (desde la carpeta del taller):
    C:\\Users\\pipel\\venvs\\ml\\Scripts\\python.exe generadores\\generar_presentacion.py
"""
import re
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Cm, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import RAIZ, F, exportar_pdf  # noqa: E402

SALIDA = RAIZ / "Taller2_C3_presentacion.pptx"
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
    _texto(pie.text_frame, ["Shiro Twin · Taller 2, 3.er corte · Aprendizaje de Máquina 26-2 · Universidad Sergio Arboleda"],
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


# 1 · Portada -----------------------------------------------------------------------------------------------
s = prs.slides.add_slide(VACIA)
fondo = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, H); fondo.fill.solid(); fondo.fill.fore_color.rgb = _rgb(AZUL)
fondo.line.fill.background()
tb = s.shapes.add_textbox(Cm(2), Cm(4.2), W - Cm(4), Cm(8))
_texto(tb.text_frame, ["Shiro Twin", "El agente que aprende a aplazar cargas sin conocer el modelo"], tam=40, color=BLANCO, viñetas=False)
tb.text_frame.paragraphs[1].runs[0].font.size = Pt(24)
tb2 = s.shapes.add_textbox(Cm(2), Cm(11.5), W - Cm(4), Cm(5))
_texto(tb2.text_frame, ["Taller 2 · 3.er corte (Q-learning) · Aprendizaje de Máquina 26-2",
                        "Grupo Shiro: Jose Leonardo Diazgranados · Sofía Londoño · Andrés Felipe Céspedes Rondón · Alex Duran",
                        "Docente: Hernán Darío Cruz Bueno · Universidad Sergio Arboleda · 11 de noviembre de 2026"],
       tam=15, color="D9E1F2", viñetas=False)
s.notes_slide.notes_text_frame.text = "En el Taller 1 Shiro resolvió su MDP con el modelo. Hoy aprende sin modelo, como tendría que hacerlo en una casa nueva."

# 2 · Qué se construye ---------------------------------------------------------------------------------------
s = diapositiva("Qué le falta a Shiro: aprender sin conocer el modelo",
                "Q-learning es el agente que llegaría a una casa nueva: no tiene la tabla P, aprende probando.")
caja(s, Cm(1.2), Cm(3.2), Cm(15.3), Cm(13.8), [
    "Taller 1: el MDP de **{n_estados_umbral} estados** se resolvió con iteración de valor → **π***.",
    "Eso exigía la tabla P contada con 4 meses de datos de **esta** casa.",
    "En Shiro Home esa tabla no existe: el agente debe **aprender jugando**.",
    "Tenemos la respuesta correcta (π*) para medir si aprende bien.",
], color=GRIS, tam=17, titulo="Del modelo al aprendizaje")
caja(s, Cm(17.3), Cm(3.2), Cm(15.3), Cm(13.8), [
    "¿Recupera π*? ¿Con **cuántos días** de experiencia? (arranque en frío)",
    "¿Qué **α, γ, ε** para un agente que se reentrena cada mes?",
    "¿**Cuantiles o K-Means** para definir el estado?",
    "¿Qué **recompensas** rompen a Shiro?",
], color=VERDE, tam=17, titulo="Decisiones que dependen de este taller")

# 3 · Por qué nuestros datos ---------------------------------------------------------------------------------
s = diapositiva("Por qué nuestros datos y nuestra π*, y no el ejemplo de las fresas",
                "Se conservan los pasos, la regla, los hiperparámetros de partida y las gráficas del profesor; cambia lo que el agente decide.")
tabla(s, Cm(1.2), Cm(3.1), Cm(31.4), ["Aspecto", "Ejemplo de las fresas", "Shiro", "Por qué"], [
    ["Acción", "Cubeta del precio observado", "No actuar · aplazar · ejecutar", "El agente debe controlar la acción"],
    ["Episodio", "Un paso al azar", "Un día de 24 h, sin reiniciar", "Sin secuencia, γ no propaga y la curva sigue a ε"],
    ["Combinación no vista", "−100", "Acciones válidas por reglas", "−100 enseña a evitar lo no visto, no lo malo"],
    ["¿Aprendió?", "La curva sube", "Coincidencia con π* y ahorro real", "Tenemos la respuesta correcta del mismo MDP"],
    ["Datos", "Fresas", "Consumo del hogar (UCI n.º 374)", "Principio Shiro primero, aceptado desde el 1.er corte"],
], [4.6, 6.2, 8.0, 12.6], tam=14)

# 4 · Diseño ---------------------------------------------------------------------------------------------------
s = diapositiva("Dos entornos, un agente y tres medidas",
                "La brecha entre acciones es de centésimas: por eso se pondera la coincidencia y se mide el ahorro real.")
caja(s, Cm(1.2), Cm(3.2), Cm(15.3), Cm(7.0), [
    "**Réplica**: los {dias_ep} días reales, hora a hora, sin reiniciar a medianoche.",
    "**Modelo contado**: el MDP exacto del Taller 1 (control).",
    "{n_semillas} semillas por configuración; curvas con banda.",
], color=GRIS, tam=15, titulo="Entornos")
caja(s, Cm(1.2), Cm(10.6), Cm(15.3), Cm(6.4), [
    "Reiniciar a las 00:00 dejaba Q = 0 en «madrugada con carga pendiente».",
    "El agente aprendió a arrastrar la carga y ejecutarla en punta: **ahorro nulo**.",
], color=NARANJA, tam=14, titulo="Error corregido antes de reportar")
caja(s, Cm(17.3), Cm(3.2), Cm(15.3), Cm(13.8), [
    "**Coincidencia simple** con π* en {n_decision_umbral} estados con decisión.",
    "**Coincidencia ponderada** por la brecha de π*: mediana **{brecha_med}** (de {brecha_min} a {brecha_max}).",
    "**Ahorro capturado**: % del ahorro de π* en mayo, con la cuenta real.",
    "Curva = recompensa del día − la de no actuar ese día (sin eso solo se ve qué día gastó más la casa).",
], color=VERDE, tam=15, titulo="Cómo se sabe si aprendió")

# 5 · Problema base --------------------------------------------------------------------------------------------
s = diapositiva("Problema base: α fijo no converge; α decreciente sí se acerca",
                "El error de los Q es diez veces mayor que la brecha que deben distinguir.")
imagen(s, "Q1_base_aprendizaje.png", Cm(0.8), Cm(2.9), w=Cm(32.2))
tabla(s, Cm(1.2), Cm(13.2), Cm(31.4), ["Agente (réplica)", "Ponderada", "Llegan al 90 %", "Ahorro mayo", "Capturado de π*", "Error |Q − Q*|"], [
    ["Profesor: α 0,1 · {n_ep} días", "{prof_acierto_w}", "{prof_alcanzan}", "{prof_ahorro}", "{prof_captura}", "{prof_errq}"],
    ["Recomendado: 1/N^0,6 · {n_ep_rec} días", "{base_acierto_w}", "{base_alcanzan}", "{base_ahorro}", "{base_captura}", "{base_errq}"],
], [9.0, 4.0, 4.4, 4.0, 4.6, 5.4], tam=13)

# 6 · Arranque en frío ----------------------------------------------------------------------------------------
s = diapositiva("El hallazgo para Shiro: el arranque en frío es inviable",
                "Ni {n_ep_rec} días simulados bastan. En una casa real son décadas: el agente se pre-entrena en el gemelo.")
imagen(s, "Q2_base_heatmap.png", Cm(0.6), Cm(2.8), h=Cm(14.6))
caja(s, Cm(21.2), Cm(3.0), Cm(11.4), Cm(14.2), [
    "**Ninguna semilla** llega al 90 % ponderado en {n_ep_rec} días ≈ **{anos_rec}** de experiencia real.",
    "Falla en {base_n_difs} decisiones de brecha pequeña: las «por milésimas» del Taller 1.",
    "Aun así, en mayo **no se distingue de π*** ({boot_ql_pi}).",
    "→ **Twin → Home** deja de ser preferencia: es una necesidad medida.",
], color=VERDE, tam=14)

# 7 · Parte 1 ---------------------------------------------------------------------------------------------------
s = diapositiva("Parte 1: ¿la política es la misma en otra estación?",
                "La π* óptima es la misma en invierno y en mayo; lo que no alcanza es aprenderla con un solo mes.")
tabla(s, Cm(1.2), Cm(3.1), Cm(31.4), ["Periodo", "Horas con nivel alto", "Energía media", "Horas al valle desde la tarde", "Estados vistos"], [
    ["Enero–abril (A)", "{pers_alto_A}", "{pers_kwh_A}", "{pers_valle_tarde_A}", "{pers_estados_A}"],
    ["Mayo (B)", "{pers_alto_B}", "{pers_kwh_B}", "{pers_valle_tarde_B}", "{pers_estados_B}"],
], [6.0, 6.0, 6.4, 7.0, 6.0], tam=14)
caja(s, Cm(1.2), Cm(7.4), Cm(15.3), Cm(9.8), [
    "π* de mayo = π* de invierno en **{p1_iguales_vi} de {p1_decision_comunes}** decisiones.",
    "La «personalidad» de este hogar es estable: el valle queda igual de lejos.",
], color=GRIS, tam=16, titulo="La política óptima")
caja(s, Cm(17.3), Cm(7.4), Cm(15.3), Cm(9.8), [
    "Agente de invierno: {tr_ql_inv_tr} en su periodo y **{tr_ql_inv_te} en mayo** (se transfiere).",
    "Agente de solo mayo: {p1_B_acierto_w} ponderado, pero ahorro **{tr_ql_mayo_te}**.",
    "→ Shiro hereda la política de la estación anterior.",
], color=VERDE, tam=16, titulo="Lo que aprende el agente")

# 8 · Parte 2 ---------------------------------------------------------------------------------------------------
s = diapositiva("Parte 2: γ y α cambian cuánto cuesta aprender, no la estrategia",
                "Miope aprende mejor (Q pequeños, menos ruido); ningún α fijo resuelve el ruido.")
tabla(s, Cm(1.2), Cm(3.1), Cm(15.6), ["γ", "Ponderada", "Capturado", "Q mínimo"], [
    ["0,5 (miope)", "{g0p5_acierto_w}", "{g0p5_captura}", "{g0p5_qmin}"],
    ["0,9 (profesor)", "{g0p9_acierto_w}", "{g0p9_captura}", "—"],
    ["0,95 (base)", "{base_acierto_w}", "{base_captura}", "{g0p95_qmin}"],
    ["0,99 (paciente)", "{g0p99_acierto_w}", "{g0p99_captura}", "{g0p99_qmin}"],
], [4.6, 3.6, 3.6, 3.8], tam=13)
tabla(s, Cm(17.2), Cm(3.1), Cm(15.4), ["α ({n_ep_rec} días)", "Ponderada", "Capturado", "Oscilación"], [
    ["0,01 (lento)", "{a0p01_acierto_w}", "{a0p01_captura}", "{a0p01_disp}"],
    ["0,1 (profesor)", "{a0p1_acierto_w}", "{a0p1_captura}", "{a0p1_disp}"],
    ["0,9 (impulsivo)", "{a0p9_acierto_w}", "{a0p9_captura}", "{a0p9_disp}"],
    ["1/N^0,6", "{base_acierto_w}", "{base_captura}", "{arec_disp}"],
], [4.6, 3.4, 3.4, 4.0], tam=13)
caja(s, Cm(1.2), Cm(10.4), Cm(31.4), Cm(6.8), [
    "π* casi no cambia con γ (la contabilidad corregida cobra el beneficio de aplazar en el momento): el miope también lo ve.",
    "γ = 0,99 acumula Q enormes y su ruido supera las brechas: en mayo ahorra **{g0p99_ahorro}**.",
    "α = 0,9 es el que más oscila; α = 0,01 sigue cambiando de opinión; α = 0,1 no mejora con más días. **α decreciente**.",
], color=VERDE, tam=14)

# 9 · Parte 3 ---------------------------------------------------------------------------------------------------
s = diapositiva("Parte 3: K-Means le gana a los cuantiles; el umbral del proyecto, a los dos",
                "La mejor definición de estado es la anclada en lo que la acción puede mover.")
imagen(s, "Q8_cortes_estados.png", Cm(0.8), Cm(2.9), w=Cm(19.0))
tabla(s, Cm(1.2), Cm(10.6), Cm(31.4), ["Definición", "Horas «alto»", "ΔE", "π*: ahorro mayo", "Q-learning: ahorro mayo"], [
    ["Cuantiles (qcut)", "{pct_alto_qcut}", "{DE_qcut}", "{p3vi_qcut_ahorro}", "{p3_qcut_ahorro}"],
    ["K-Means", "{pct_alto_kmeans}", "{DE_kmeans}", "{p3vi_kmeans_ahorro}", "{p3_kmeans_ahorro}"],
    ["Umbral 200 Wh (base)", "{pct_alto_umbral}", "{DE_umbral}", "{p3vi_umbral_ahorro}", "{base_ahorro}"],
], [9.0, 5.0, 4.4, 6.4, 6.6], tam=13)
caja(s, Cm(20.2), Cm(3.0), Cm(12.4), Cm(7.2), [
    "Tercil «alto» desde {corte_q2}: el **{p3_qcut_sin_exceso}** de esas horas no tiene nada que aplazar.",
    "K-Means corta donde el consumo se separa ({corte_k1} y {corte_k2}).",
], color=GRIS, tam=13)

# 10 · Parte 4 ---------------------------------------------------------------------------------------------------
s = diapositiva("Parte 4: el agente optimiza exactamente lo que se le pide",
                "Tres recompensas quedan prohibidas en el entorno de Shiro.")
imagen(s, "Q12_parte4_recompensas.png", Cm(0.8), Cm(2.9), w=Cm(32.2))
caja(s, Cm(1.2), Cm(10.8), Cm(10.2), Cm(6.4), [
    "**+1 por transacción** → Shiro nervioso: {p4_trans_aplaz} aplazamientos/día, ahorro **{p4_trans_ahorro}**.",
], color=NARANJA, tam=14)
caja(s, Cm(11.8), Cm(10.8), Cm(10.2), Cm(6.4), [
    "**−1000 si pierde** → Shiro miedoso: {p4_miedo_aplaz} aplazamientos/día; nunca propone.",
], color=NARANJA, tam=14)
caja(s, Cm(22.4), Cm(10.8), Cm(10.2), Cm(6.4), [
    "**Contabilidad ingenua** → espera {p4_ing_espera} (base {base_espera}) y ahorra {p4_ing_ahorro}.",
], color=NARANJA, tam=14)

# 11 · Batalla y qué cambia en Shiro ---------------------------------------------------------------------------
s = diapositiva("La batalla en mayo y qué cambia en Shiro",
                "Cierre: decisiones para Shiro Home y el Taller 3 (DQN).")
imagen(s, "Q14_batalla_mayo.png", Cm(0.6), Cm(4.0), w=Cm(17.6))
caja(s, Cm(18.6), Cm(3.0), Cm(14.0), Cm(14.2), [
    "**Pre-entrenar en el gemelo**; en la casa solo ajustar.",
    "**α decreciente**; horizonte corto para el agente tabular.",
    "**Estado del proyecto** (umbral 200 Wh) se mantiene.",
    "**Recompensa del Taller 1 fija**: sin pago por actuar ni castigo de −1000.",
    "Política de invierno sirve en mayo.",
    "Límites: {n_semillas} semillas, aproximación de Markov, ε sin sintonizar, sobreestimación de Q.",
], color=VERDE, tam=14)


def main():
    prs.save(SALIDA)
    print(f"Presentación: {SALIDA.name} ({len(prs.slides)} diapositivas)")
    pdf = exportar_pdf(SALIDA, SALIDA.with_suffix(".pdf"))
    print(f"PDF: {pdf.name}")


if __name__ == "__main__":
    main()
