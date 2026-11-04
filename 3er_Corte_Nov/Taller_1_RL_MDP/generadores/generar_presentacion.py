# -*- coding: utf-8 -*-
"""Genera Taller1_C3_presentacion.pptx (y su PDF) desde cifras.json y figuras/.

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

SALIDA = RAIZ / "Taller1_C3_presentacion.pptx"
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
    _texto(pie.text_frame, ["Shiro Twin · Taller 1, 3.er corte · Aprendizaje de Máquina 26-2 · Universidad Sergio Arboleda"],
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
tb = s.shapes.add_textbox(Cm(2), Cm(4.5), W - Cm(4), Cm(8))
_texto(tb.text_frame, ["Shiro Twin", "El MDP que decide cuándo aplazar una carga"], tam=40, color=BLANCO, viñetas=False)
tb.text_frame.paragraphs[1].runs[0].font.size = Pt(26)
tb2 = s.shapes.add_textbox(Cm(2), Cm(11.5), W - Cm(4), Cm(5))
_texto(tb2.text_frame, ["Taller 1 · 3.er corte (Aprendizaje por Refuerzo) · Aprendizaje de Máquina 26-2",
                        "Grupo Shiro: Jose Leonardo Diazgranados · Sofía Londoño · Andrés Felipe Céspedes Rondón · Alex Duran",
                        "Docente: Hernán Darío Cruz Bueno · Universidad Sergio Arboleda · 4 de noviembre de 2026"],
       tam=15, color="D9E1F2", viñetas=False)
s.notes_slide.notes_text_frame.text = "Presentamos la pieza que le faltaba al gemelo digital de Shiro: la que decide."

# 2 · Qué se construye -----------------------------------------------------------------------------------------
s = diapositiva("Qué le falta a Shiro: la pieza que decide",
                "Shiro ya predice, anticipa y agrupa. Este taller formaliza el MDP y deja listo el entorno del Taller 2.")
caja(s, Cm(1.2), Cm(3.2), Cm(15.3), Cm(13.8), [
    "**Simulador** de consumo: lineal con retardos (1.er corte).",
    "**Guardian**: anticipa picos con G0 (Parcial 2).",
    "**Tipos de día**: K-Means k = 2 (2.º corte).",
    "**Falta el MDP**: la pieza que decide. Es criterio de cierre del proyecto y el entorno del Taller 2 (Q-learning).",
], color=GRIS, tam=17, titulo="Lo que Shiro ya tiene")
caja(s, Cm(17.3), Cm(3.2), Cm(15.3), Cm(13.8), [
    "¿Cabe el **tipo de día** en el estado? ¿Hace falta la probabilidad de pico de Guardian?",
    "¿La **transición depende de la acción**? En las fresas, no.",
    "¿Cuánto vale **una hora de espera (λ)** para la persona?",
    "¿Qué hacer cuando la decisión está **en el límite**?",
], color=VERDE, tam=17, titulo="Decisiones que dependen de este taller")

# 3 · La traducción a MDP --------------------------------------------------------------------------------------
s = diapositiva("La traducción a MDP: las cinco preguntas",
                "Una sola decisión: cada hora, dejar correr o aplazar la carga desplazable. Tres acciones finitas.")
tabla(s, Cm(1.2), Cm(3.1), Cm(31.4), ["Pregunta", "Respuesta de Shiro"], [
    ["1 · Objetivo y agente", "Shiro (propone; la persona aprueba). Cada hora: ¿dejo correr la carga desplazable o la aplazo?"],
    ["2 · Acciones", "No actuar · Aplazar (pico y cupo libre) · Ejecutar lo pendiente"],
    ["3 · Estados ({n_estados})", "Tipo de día (K-Means) × franja × nivel de demanda × carga pendiente"],
    ["4 · Recompensa", "−tarifa(franja) · energía − λ · [carga esperando]   (kWh-eq; valle 1,0, punta 1,5)"],
    ["5 · Transición", "Conteo shift(−1) en enero–abril × efecto determinista de la acción → P depende de a"],
    ["γ, θ", "γ = 0,95 por hora (≈ una espera hasta el valle) · θ = 10⁻⁶"],
], [6.4, 25.0], tam=15)

# 4 · Estados ----------------------------------------------------------------------------------------------------
s = diapositiva("Estados: el clustering entra al MDP, y la cobertura alcanza",
                "La maldición de la dimensionalidad se controla con cuatro variables y una tabla de cobertura medida.")
imagen(s, "R2_cobertura.png", Cm(1.0), Cm(3.4), h=Cm(12.0))
caja(s, Cm(18.6), Cm(3.1), Cm(14.0), Cm(14.0), [
    "**Tipo de día**: K-Means del 2.º corte ajustado con {n_dias_tr} días; .predict sobre la curva vista hasta la hora "
    "anterior (a las 12 h reconoce el {obs_rec_12} de los días de carga alta).",
    "**{n_x_vistos} de 24** combinaciones vistas; mediana **{vis_med}** visitas, mínimo {vis_min}. Mayo: ningún estado nuevo.",
    "Con la hora en vez de la franja serían 288 combinaciones: P no se podría estimar.",
    "Paso de **1 hora**: repetir estado {autolazo_10} a 10 min frente a {autolazo_h} por hora.",
], color=GRIS, tam=14)

# 5 · Recompensa y trampa del descuento ---------------------------------------------------------------------------
s = diapositiva("Recompensa: la trampa del descuento",
                "Con descuento, pagar después parece más barato. Corregimos la contabilidad y lo comprobamos con tarifa plana.")
caja(s, Cm(1.2), Cm(3.2), Cm(15.3), Cm(13.8), [
    "**ΔE = {DE}** por aplazamiento: 40 % del exceso sobre 200 Wh (el 39,7 % avisable del Parcial 2).",
    "Aplazar evita un sobrecosto de **{ganancia_aplazar}**.",
    "λ = precio de una hora de espera. Dos perfiles: **paciente 0,005** y **exigente 0,02**.",
    "Contabilidad corregida: al aplazar se cobra ya la parte de valle; al ejecutar, solo el sobrecosto.",
], color=GRIS, tam=16, titulo="r = −tarifa · energía − λ · espera")
caja(s, Cm(17.3), Cm(3.2), Cm(15.3), Cm(13.8), [
    "Tarifa plana, contabilidad corregida: aplaza en **{cordura_corregida_1p0_nap}** estados. Bien.",
    "Tarifa plana, contabilidad ingenua: aplaza en **{cordura_ingenua_1p0_nap}** y **nunca ejecuta**: la carga espera "
    "**{cordura_ingenua_1p0_espera}**.",
    "Es el «ahorro simulado que no existe» que el proyecto venía advirtiendo, ahora dentro del propio MDP.",
], color=NARANJA, tam=16, titulo="Prueba de cordura")

# 6 · Código ------------------------------------------------------------------------------------------------------
s = diapositiva("Adaptación del código: un cambio de fondo",
                "En las fresas el valor futuro no depende de la ciudad: π* termina siendo la codiciosa. Aquí la acción cambia el futuro.")
caja(s, Cm(1.2), Cm(3.2), Cm(15.3), Cm(13.8), [
    "Paso 1: {n_dias} días → serie horaria; entrenamiento hasta el 30-abr, prueba en mayo.",
    "Paso 2: **se eliminó pd.qcut** → K-Means + franja + nivel + pendiente.",
    "Paso 3a: tarifa × energía, ΔE, λ.",
    "Paso 3b: P_dict[s][a][s′] = conteo × acción.",
    "Pasos 4–5: el valor futuro **dentro** del bucle de acciones; converge en {iteraciones} iteraciones.",
], color=GRIS, tam=16, titulo="Qué cambió")
caja(s, Cm(17.3), Cm(3.2), Cm(15.3), Cm(13.8), [
    "En el ejemplo, P(s′|s) no depende de la acción (el distribuidor no mueve el mercado).",
    "El término γ·ΣP·V es igual para las cuatro ciudades y se cancela → **π* = argmax R = política codiciosa**.",
    "El «dilema NY contra Chicago» necesita que la acción cambie el estado siguiente. En Shiro lo cambia: la carga pendiente.",
], color=VERDE, tam=16, titulo="Observación sobre las fresas")

# 7 · Política paciente --------------------------------------------------------------------------------------------
s = diapositiva("La política (persona paciente): coincide con la codiciosa",
                "Aplazar compensa esperas de hasta {horas_eq_paciente}; la espera esperada más larga es de {horas_valle_1}. Mirar al futuro no cambia nada.")
imagen(s, "R3_distribucion_politica.png", Cm(0.8), Cm(4.0), w=Cm(18.2))
caja(s, Cm(19.6), Cm(3.1), Cm(13.0), Cm(14.0), [
    "Aplaza en los **{n_opt_Aplazar}** estados donde puede (pico en punta, cupo libre).",
    "Ejecuta en los **{n_opt_Ejecutar}** estados de madrugada con carga pendiente.",
    "**π* = codiciosa = regla fija** en los {n_estados} estados.",
    "¿Tiene sentido? Sí: compensa esperar hasta **{horas_eq_paciente}** y la espera esperada más larga (desde la "
    "mañana) es de {horas_valle_1}.",
], color=GRIS, tam=15)

# 8 · Reglas de oro ------------------------------------------------------------------------------------------------
s = diapositiva("Reglas de oro (persona exigente, λ = 0,02)",
                "π* y la codiciosa discrepan en {ex_n_difs} de {n_estados} estados. La tabla descompone cada regla en el hoy y el después.")
tabla(s, Cm(1.2), Cm(3.0), Cm(31.4), ["Regla", "π*", "Codiciosa", "Gana hoy la codiciosa", "Cuesta después", "Por qué"], [
    ["1 · Mañana, pico", "No actuar", "Aplazar", "+{regla_0-1-2-0_ganancia_inm}", "{regla_0-1-2-0_costo_fut}",
     "Valle a {regla_0-1-2-0_horas}; solo compensa < {horas_eq_exigente}"],
    ["2 · Tarde, carga alta", "No actuar", "Aplazar", "+{regla_1-2-2-0_ganancia_inm}", "{regla_1-2-2-0_costo_fut}",
     "Otro pico antes del valle {p_otro_pico_1-2-2} (normal: {p_otro_pico_0-2-2}): guarda el cupo"],
    ["3 · Mañana, carga pendiente", "Ejecutar", "No actuar", "+{regla_0-1-0-1_costo_inm_ej}", "{regla_0-1-0-1_ganancia_fut_ej}",
     "Faltan {regla_0-1-0-1_horas} al valle: mejor pagar el sobrecosto ya"],
], [5.0, 2.8, 2.8, 4.2, 3.6, 13.0], tam=13)
caja(s, Cm(1.2), Cm(9.0), Cm(31.4), Cm(8.0), [
    "**Regla 1.** Aplazar gana {regla_0-1-2-0_ganancia_inm} hoy, pero cargar la espera {regla_0-1-2-0_horas} cuesta "
    "{regla_0-1-2-0_costo_fut}. Es el dilema NY contra Chicago: la ganancia de hoy deja al agente en un estado peor.",
    "**Regla 2.** En la tarde, un día normal aplaza (ΔQ {ex_dQ_0-2-2-0}) y uno de carga alta no (ΔQ {ex_dQ_1-2-2-0}). "
    "Probablemente guarda el cupo para la noche (ΔQ {ex_dQ_1-3-2-0}). Se decide por milésimas.",
    "**Regla 3.** La codiciosa ve una hora de espera (−0,02) más barata que el sobrecosto; π* suma las horas que faltan.",
], color=VERDE, tam=15)

# 9 · Batalla --------------------------------------------------------------------------------------------------------
s = diapositiva("La batalla en mayo (el mes que el modelo nunca vio)",
                "Ahorro pequeño y honesto: con {n_dias_te} días no se separa del ruido. π* exigente cambia ahorro por menos espera.")
imagen(s, "R6_batalla.png", Cm(1.0), Cm(2.9), w=Cm(19.5))
caja(s, Cm(21.0), Cm(3.1), Cm(11.6), Cm(14.0), [
    "**Paciente** (π* = codiciosa): ahorro {ahorro_opt_te}, espera {espera_opt_te}, {aplaz_opt_te} aplazamientos/día.",
    "Frente a no actuar: {boot_no_te} → no se distingue.",
    "**Exigente**: π* ahorra {ex_ahorro_opt_te} con {ex_espera_opt_te} de espera; la codiciosa, {ex_ahorro_cod_te} con "
    "{ex_espera_cod_te}.",
    "Enero–abril: π* le gana a la codiciosa ({ex_boot_cod_tr}); en mayo, no se distingue.",
], color=GRIS, tam=13)

# 10 · Sensibilidad ------------------------------------------------------------------------------------------------
s = diapositiva("Sensibilidad: el precio de esperar decide la política",
                "Tarifa plana: nunca aplaza. A más λ, el agente abandona la mañana y conserva la noche.")
imagen(s, "R7_sensibilidad.png", Cm(1.0), Cm(3.0), w=Cm(31.8))
caja(s, Cm(1.2), Cm(14.6), Cm(31.4), Cm(3.2), [
    "Con punta 1,5, los estados que aplazan pasan de {sens_nap_0p005_1p5} a {sens_nap_0p01_1p5} y a {sens_nap_0p02_1p5} "
    "cuando λ sube de 0,005 a 0,01 y a 0,02. Con tarifa plana, cero en toda la columna.",
], color=VERDE, tam=15, viñetas=False)

# 11 · Qué cambia en Shiro -----------------------------------------------------------------------------------------
s = diapositiva("Qué cambia en Shiro por estos números",
                "Cierre: decisiones de diseño para el agente de Q-learning y límites declarados.")
caja(s, Cm(1.2), Cm(3.2), Cm(19.0), Cm(13.8), [
    "El agente de Q-learning lleva **carga pendiente** en el estado y la **contabilidad corregida**.",
    "**λ es un control de la persona**: la política se recalcula en décimas de segundo; mostrar «ahorro / espera».",
    "Decisiones por **milésimas** → se muestran como dudosas (margen = confianza).",
    "El **tipo de día** sí cambia decisiones; la hora dentro de la franja también → probar bloques de 3 h.",
    "Aplazar por tarifa mueve un **{ahorro_opt_te}**: el ahorro real exige saber qué aparato se enciende.",
], color=VERDE, tam=15, titulo="Decisiones")
caja(s, Cm(21.0), Cm(3.2), Cm(11.6), Cm(13.8), [
    "ΔE y la tarifa son supuestos (se barren).",
    "La demanda no depende de la acción; un solo cupo.",
    "Shiro ve arrancar la carga, no la anticipa.",
    "{n_dias_te} días de prueba; carga alta {pct_alto_tr} → {pct_alto_te}.",
    "Sin acción térmica; ahorro siempre simulado.",
], color=NARANJA, tam=14, titulo="Límites")


def main():
    prs.save(SALIDA)
    print(f"Presentación: {SALIDA.name} ({len(prs.slides)} diapositivas)")
    pdf = exportar_pdf(SALIDA, SALIDA.with_suffix(".pdf"))
    print(f"PDF: {pdf.name}")


if __name__ == "__main__":
    main()
