# -*- coding: utf-8 -*-
"""Genera Taller1_C3_Diseno_MDP_RESUELTO.docx (y su PDF) desde cifras.json y figuras/.

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

SALIDA = RAIZ / "Taller1_C3_Diseno_MDP_RESUELTO.docx"
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
    r = p.add_run(" " + texto)
    r.bold = True; r.font.size = Pt(13); r.font.color.rgb = RGBColor(255, 255, 255)
    p.paragraph_format.space_before = Pt(12); p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True


def H2(texto):
    p = doc.add_paragraph()
    r = p.add_run(texto)
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
r = p.add_run("APRENDIZAJE DE MÁQUINA — TALLER 1 · 3.er CORTE (APRENDIZAJE POR REFUERZO)")
r.bold = True; r.font.size = Pt(10); r.font.color.rgb = RGBColor.from_string(AZUL)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Shiro Twin: el MDP que decide cuándo aplazar una carga"); r.bold = True; r.font.size = Pt(18)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Documento de diseño, adaptación del código y batalla de las políticas"); r.italic = True; r.font.size = Pt(11.5)

tabla(["Campo", "Valor"], [
    ["Universidad", "Universidad Sergio Arboleda · Aprendizaje de Máquina · semestre 26-2"],
    ["Docente", "Hernán Darío Cruz Bueno"],
    ["Grupo Shiro", "Jose Leonardo Diazgranados · Sofía Londoño · Andrés Felipe Céspedes Rondón · Alex Duran"],
    ["Sector", "Energía y Medio Ambiente / IoT"],
    ["Dataset", "Appliances Energy Prediction (UCI n.º 374): {n_dias} días completos, serie horaria"],
    ["Fecha", "4 de noviembre de 2026"],
], [4, 12.5])

recuadro("Resumen", [
    "Shiro necesitaba **la pieza que decide**. Este taller formaliza su MDP: **{n_estados} estados** (tipo de día de K-Means, "
    "franja, nivel de demanda y carga pendiente), 3 acciones (no actuar, aplazar, ejecutar lo pendiente) y una transición "
    "contada con `shift(-1)` sobre enero–abril. Lo resuelve con la iteración de valor del curso, en **{iteraciones} iteraciones**.",
    "**El estado «carga pendiente» es indispensable.** Sin él, aplazar equivaldría a borrar consumo. Y con la contabilidad "
    "ingenua el agente aplaza y nunca ejecuta: deja la carga esperando **{cordura_ingenua_1p0_espera}**, aunque la tarifa sea plana.",
    "**Con una persona paciente (λ = 0,005) la política óptima coincide con la codiciosa en los {n_estados} estados:** aplaza "
    "todo pico en punta y lo ejecuta en la madrugada. En mayo ahorra **{ahorro_opt_te}** del costo con **{espera_opt_te}** "
    "de espera, y no se distingue de no actuar ({boot_no_te}).",
    "**Con una persona exigente (λ = 0,02) aparecen las reglas de oro:** π* difiere de la codiciosa en **{ex_n_difs} estados**. "
    "Deja de aplazar en la mañana, guarda el cupo en la tarde de un día de carga alta y rescata la carga pendiente. "
    "En mayo baja la espera de {ex_espera_cod_te} a **{ex_espera_opt_te}** con un ahorro de {ex_ahorro_opt_te}.",
    "**Qué cambia en Shiro:** λ es el control de la persona y la política se recalcula para cada valor. Las decisiones con "
    "margen de milésimas se muestran como dudosas. Aplazar por tarifa no es donde está el ahorro de este hogar.",
])

# =====================================================================================
H1("1. Qué se construye y qué decisiones dependen de este taller")
P("Shiro Twin ya tiene un **simulador** de consumo (regresión lineal con retardos), un **anticipador** de picos "
  "(Guardian, modelo G0 del Parcial 2) y un **detector de tipos de día** (K-Means del 2.º corte). Le falta la pieza que "
  "**decide**: el proceso de decisión de Markov sobre el que el agente aprenderá a operar el hogar. Es un criterio de "
  "cierre del proyecto todavía abierto («MDP formalizado por escrito») y es el entorno que usará el Taller 2 del corte "
  "(Q-learning). Cuatro decisiones de arquitectura dependen de lo que salga aquí:", alin="j")
N_([
    "**Espacio de estados:** ¿cabe el tipo de día? ¿Necesita la probabilidad de pico de Guardian una variable propia?",
    "**Si la transición depende de la acción.** En el ejemplo de las fresas no depende. En Shiro, aplazar deja una carga "
    "pendiente que habrá que ejecutar después.",
    "**Cuánto vale una hora de espera (λ):** el parámetro que decide si aplazar compensa y que la persona ajustaría.",
    "**Qué hace el agente cuando una decisión está en el límite** o cuando el estado casi no tiene historia.",
])

# =====================================================================================
H1("2. Parte 1 — Documento de diseño: las cinco preguntas")
H2("2.1 Objetivo y agente")
P("**Agente: Shiro**, que propone y deja que la persona apruebe, como en el resto del proyecto. En el gemelo se supone "
  "la aprobación. **Decisión única: cada hora, ¿dejo correr la carga desplazable del hogar o la aplazo, y cuándo ejecuto "
  "la que quedó esperando?** El objetivo es minimizar el costo de la energía ponderado por la tarifa **sin imponer esperas "
  "largas**.", alin="j")
P("**¿Hay algo que mover?** La figura 1 responde lo mismo que la gráfica de precios de las fresas. El "
  "{pct_horas_alto_tr} de las horas de enero–abril tiene demanda alta (media de lecturas > 200 Wh), y **el "
  "{pct_alto_en_valle} de ellas cae en la madrugada**: el valle de tarifa está vacío y hay espacio para mover cargas hacia "
  "él.", alin="j")
figura("R1_justificacion.png", "Energía media por hora y porcentaje de horas con nivel alto (enero–abril). En verde, la "
       "madrugada, con tarifa de valle.")

H2("2.2 Acciones (A)")
tabla(["Acción", "Cuándo es válida", "Qué hace"], [
    ["**No actuar**", "Siempre", "El hogar consume lo que demanda."],
    ["**Aplazar**", "Nivel alto y sin otra carga pendiente (hay un solo cupo)",
     "Saca ΔE = {DE} de esta hora y deja la carga pendiente."],
    ["**Ejecutar**", "Hay una carga pendiente", "Consume ΔE en esta hora y libera el cupo."],
], [3, 6, 7.5])
P("Se deja fuera a propósito la acción «ajustar la consigna ±1 °C» de la propuesta del proyecto. El dataset no trae un "
  "actuador térmico ni un dato que mida su efecto, y modelarla sería inventar la física del hogar.", alin="j")

H2("2.3 Estados (S): aquí entra el aprendizaje no supervisado")
tabla(["Variable", "Valores", "De dónde sale"], [
    ["**Tipo de día estimado**", "normal / carga alta",
     "**K-Means k = 2** del 2.º corte, ajustado solo con los {n_dias_tr} días de entrenamiento (centroides de "
     "{km_kwh_normal} y {km_kwh_alto}; {n_alto_tr} días de carga alta). Se asigna con `.predict` restringido a las "
     "horas ya vistas del día. Antes de las 8 h es «normal»; con la curva hasta las 12 h reconoce el {obs_rec_12} de "
     "los días de carga alta."],
    ["**Franja**", "madrugada · mañana · tarde · noche", "Bloques de 6 h; define la tarifa."],
    ["**Nivel de demanda**", "bajo (< 60 Wh) · medio · alto (> 200 Wh)",
     "Media de lecturas de la hora en curso. 200 Wh es el umbral de anomalía del proyecto (percentil 90 de entrenamiento)."],
    ["**Carga pendiente**", "no / sí", "No sale del dataset: la crea la acción «Aplazar»."],
], [3.6, 3.9, 9])
P("**Por qué estas variables y no veinte.** Con tres variables exógenas hay 24 combinaciones, y en entrenamiento aparecen "
  "**{n_x_vistos}**, con una mediana de **{vis_med} visitas** y un mínimo de {vis_min} ({estado_min}). De las que "
  "faltan, tres son imposibles (no hay «carga alta» de madrugada, porque antes de las 8 h el tipo no es observable) y la "
  "otra no ocurrió nunca (en enero–abril ninguna hora de madrugada tuvo demanda alta). **Mayo no trae ningún estado "
  "nuevo.** Con la hora (24 valores) en "
  "lugar de la franja serían 288 combinaciones y las transiciones no se podrían estimar con {n_dias_tr} días.", alin="j")
P("La probabilidad de pico de Guardian **no necesita variable propia**: sus dos entradas, consumo actual y hora × "
  "laborable, ya son *nivel* y *franja*. Así, la tabla P contada generaliza a G0. El paso de decisión es de **una hora**: "
  "a 10 minutos la probabilidad de quedarse en el mismo estado es {autolazo_10}, frente a {autolazo_h} por hora (la "
  "autocorrelación que el proyecto ya documentó), y aplazar una lavadora se decide a escala de horas.", alin="j")
figura("R2_cobertura.png", "Cobertura del espacio de estados: horas de entrenamiento en cada combinación de tipo de día, "
       "franja y nivel.", ancho=10.5)

H2("2.4 Recompensa (R)")
P("**r(s, a) = −tarifa(franja) · energía consumida(s, a) − λ · [queda una carga pendiente]**, en kWh-equivalentes de "
  "valle.", alin="j")
V_([
    "**Energía:** la demanda media del estado (un `groupby` como el del ejemplo), menos ΔE si se aplaza, más ΔE si se "
    "ejecuta.",
    "**ΔE = {DE}**: el 40 % del exceso medio sobre 200 Wh en las horas de nivel alto ({exceso_alto}). El 40 % sale del "
    "Parcial 2, donde solo el 39,7 % del exceso del mes estaba en picos que se podían avisar a tiempo.",
    "**Tarifa:** valle (madrugada) = 1,0; punta (resto del día) = 1,5. Es relativa a propósito: el dato no trae precios y "
    "se barre de 1,0 a 2,0.",
    "**λ:** costo de cada hora con una carga esperando. No se puede medir, así que se trata como un parámetro de la persona "
    "con dos perfiles: **paciente (λ = 0,005)** y **exigente (λ = 0,02)**. Aplazar evita un sobrecosto de "
    "{ganancia_aplazar}, que compensa esperas de hasta {horas_eq_paciente} en el perfil paciente y de "
    "{horas_eq_exigente} en el exigente.",
])
recuadro("Decisión de diseño: la contabilidad de la carga aplazada", [
    "Con descuento γ < 1, pagar después *parece* más barato que pagar ahora. Si la energía aplazada se cobrara completa "
    "cuando se ejecuta, el agente aplazaría aunque la tarifa fuera plana: aprovecharía el descuento, no la tarifa.",
    "Por eso, **al aplazar se cobra enseguida la parte inevitable** (ΔE a precio de valle) y **al ejecutar solo el "
    "sobrecosto frente al valle**. La suma sin descontar es la misma; lo único que cambia es que postergar deja de "
    "parecer un ahorro.",
    "Comprobación: con tarifa plana, la contabilidad corregida aplaza en **{cordura_corregida_1p0_nap} estados**. La ingenua "
    "aplaza en **{cordura_ingenua_1p0_nap}** y **nunca ejecuta**: en mayo la carga queda esperando "
    "**{cordura_ingenua_1p0_espera}**. Es el «ahorro simulado que no existe» que el proyecto venía advirtiendo, ahora "
    "dentro del propio MDP.",
], color=NARANJA)

H2("2.5 Transición (P)")
P("**P(s′ | s, a) = P_datos(tipo′, franja′, nivel′ | tipo, franja, nivel) · P_acción(pendiente′ | pendiente, a).**", alin="j")
V_([
    "**Opción A (implementada, como en el ejemplo):** se cuentan con `shift(-1)` las horas consecutivas de entrenamiento "
    "({n_horas_tr} horas, {n_pares_P} pares (s, s′) distintos). Supuesto declarado: lo que el hogar *demanda* no depende de "
    "que Shiro aplace.",
    "**Parte de la acción (determinista):** aplazar deja la carga pendiente, ejecutar la libera y no actuar la mantiene. "
    "**Esto hace que P dependa de la acción**, que es justo lo que le falta al ejemplo de las fresas.",
    "**Opción B (cómo se llenaría con el modelo supervisado).** El simulador elegido en el proyecto es la regresión lineal "
    "con retardos. Se consultaría cientos de veces por estado: (1) muestrear lecturas reales de ese estado; (2) predecir la "
    "hora siguiente; (3) sumar un residuo tomado de la misma franja y tipo de día; (4) discretizar el resultado y contar a "
    "qué estado cae. G0 aportaría directamente la probabilidad de pasar a nivel alto. Ese es el entorno del Taller 2 "
    "(Q-learning), donde el estado podrá ser continuo.",
])
H2("2.6 Descuento y convergencia")
P("**γ = 0,95 por hora**, una vida media de unas 13,5 h: más o menos lo que dura una espera hasta el valle. Se barre de 0 "
  "a 0,99; con γ = 0 se obtiene exactamente la política codiciosa. **θ = 10⁻⁶**, muy por debajo del sobrecosto que se "
  "juega en cada decisión ({ganancia_aplazar}).", alin="j")

# =====================================================================================
H1("3. Parte 2 — Adaptación del código de las fresas")
tabla(["Paso del ejemplo", "Qué cambió", "Por qué"], [
    ["1 · Limpieza", "{n_dias} días completos agregados a 24 horas; entrenamiento hasta el 30-abr ({n_dias_tr} días), "
     "mayo para evaluar ({n_dias_te} días).", "Shiro decide por hora; la partición temporal es la regla del proyecto."],
    ["2 · Estados", "**Se eliminó** `pd.qcut`. Tipo de día con K-Means (`.predict` sobre la curva parcial), franja, nivel "
     "y carga pendiente.", "Información mínima para decidir; cobertura medida (sección 2.3)."],
    ["3a · Recompensa", "Ya no es `atlantaretail − farmprice`: tarifa × energía, ΔE, λ y contabilidad corregida.",
     "Reglas de negocio del hogar."],
    ["3b · Transición", "`P_dict[s][a][s′]`: conteo `shift(-1)` por la parte de la acción.", "P depende de a."],
    ["4 · Iteración de valor", "`expected_future_value` se calcula **dentro** del bucle de acciones; las acciones no "
     "válidas no se evalúan.", "Sin esto, el término futuro sería igual para todas las acciones."],
    ["5 · Política", "π*, CSV con V* y Q de cada acción, y la política codiciosa (γ = 0) al lado.", "Para la batalla."],
], [3.2, 7.3, 6])
P("El único cambio de fondo a los pasos 4 y 5 es dónde se calcula el valor futuro:", alin="j")
codigo([
    "for a in R_dict[s]:                                   # solo acciones válidas en s",
    "    reward = R_dict[s][a]",
    "    expected_future_value = 0                         # ← ahora depende de la acción",
    "    for next_s, prob in P_dict[s][a].items():",
    "        expected_future_value += prob * V[next_s]",
    "    q_sa[a] = reward + GAMMA * expected_future_value",
])
recuadro("Observación sobre el ejemplo de las fresas", [
    "En el ejemplo, P(s′ | s) no depende de la acción: es la simplificación deliberada del distribuidor pequeño que no "
    "mueve el mercado. Por eso el valor futuro es el mismo para las cuatro ciudades, se cancela al comparar, y **π\* = "
    "argmax R(s, a): la política óptima es la codiciosa**. El «dilema NY contra Chicago» necesita que la acción cambie el "
    "estado siguiente. En Shiro sí lo cambia (la carga pendiente), y por eso aquí las dos políticas pueden separarse.",
], color=GRIS)
P("El cuaderno corre de principio a fin y converge en {iteraciones} iteraciones. La política completa queda en "
  "`politica_optima_shiro.csv`, con V*(s) y Q(s, a) de cada estado.", alin="j")

# =====================================================================================
H1("4. Parte 3 — La batalla de las políticas")
H2("4.1 Interpretar la política (perfil paciente, λ = 0,005)")
figura("R3_distribucion_politica.png", "Distribución de la política sobre los {n_estados} estados: óptima (γ = 0,95) frente "
       "a codiciosa (γ = 0).", ancho=12.5)
P("**El agente aplaza en los {n_opt_Aplazar} estados donde puede hacerlo** (pico en punta y sin carga pendiente), "
  "**ejecuta en los {n_opt_Ejecutar} estados de madrugada con carga pendiente** y no actúa en los {n_opt_No actuar} restantes. "
  "**Tiene sentido:** un aplazamiento ahorra {ganancia_aplazar}, que en este perfil compensa esperas de hasta "
  "{horas_eq_paciente}. La espera esperada más larga, desde la mañana, es de {horas_valle_1}. Por eso mirar "
  "al futuro no cambia ninguna decisión: **π\* coincide con la codiciosa en los {n_estados} estados** (diferencias: "
  "{n_difs}) y también con la regla fija «aplazar todo pico en punta, ejecutar en la madrugada».", alin="j")
figura("R5_mapa_politica.png", "Mapa de la política óptima del perfil paciente. Color: acción; número: V*(s) en "
       "kWh-eq (negativo = costo esperado).")

H2("4.2 Las reglas de oro (perfil exigente, λ = 0,02)")
P("Cuando la persona valora su tiempo cuatro veces más, π* y la codiciosa discrepan en **{ex_n_difs} de los "
  "{n_estados} estados**. π* aplaza en {ex_n_aplaza} estados y la codiciosa en {ex_n_aplaza_cod}. La tabla descompone cada "
  "regla en recompensa inmediata y valor futuro (Q = R + γ·ΣP·V*):", alin="j")
tabla(["Estado", "π*", "Codiciosa", "Lo que gana hoy la codiciosa", "Lo que cuesta después (γΣPV)", "Dato que lo explica"], [
    ["{regla_0-1-2-0_desc}", "No actuar", "Aplazar", "+{regla_0-1-2-0_ganancia_inm}", "{regla_0-1-2-0_costo_fut}",
     "Valle a {regla_0-1-2-0_horas}"],
    ["{regla_1-2-2-0_desc}", "No actuar", "Aplazar", "+{regla_1-2-2-0_ganancia_inm}", "{regla_1-2-2-0_costo_fut}",
     "Valle a {regla_1-2-2-0_horas}; otro pico antes del valle: {p_otro_pico_1-2-2}"],
    ["{regla_0-1-0-1_desc}", "Ejecutar", "No actuar", "+{regla_0-1-0-1_costo_inm_ej} (no paga el sobrecosto hoy)",
     "{regla_0-1-0-1_ganancia_fut_ej}", "Valle a {regla_0-1-0-1_horas}"],
], [3.6, 1.8, 1.8, 2.9, 2.9, 3.5], tam=8.5)
figura("R8_mapa_politica_exigente.png", "Mapa de la política óptima del perfil exigente (λ = 0,02).")
P("**Regla 1 — Por la mañana no aplaza, aunque la tarifa sea punta.** La codiciosa ve que aplazar gana "
  "{regla_0-1-2-0_ganancia_inm} kWh-eq ahora: el sobrecosto de punta evitado, menos la primera hora de espera. π* mira "
  "lo que viene: el valle está a {regla_0-1-2-0_horas} esperadas, y cargar con la espera todo ese tiempo cuesta "
  "{regla_0-1-2-0_costo_fut} en valor futuro, más de lo que se gana. En este perfil una espera compensa solo si dura "
  "menos de {horas_eq_exigente}. Es el mismo tipo de dilema que el de NY contra Chicago: la ganancia de hoy es real, pero "
  "deja al agente en un estado peor.", alin="j")
P("**Regla 2 — En un día de carga alta guarda el cupo de la tarde.** Con un pico en la tarde, en un día normal π* "
  "aplaza (ΔQ = {ex_dQ_0-2-2-0}) y en un día de carga alta no (ΔQ = {ex_dQ_1-2-2-0}). Dos cosas del día de carga alta "
  "explican la diferencia: el valle queda más lejos ({horas_valle_x_1-2-2} frente a {horas_valle_x_0-2-2}) y es más "
  "probable que llegue otro pico en punta antes del valle ({p_otro_pico_1-2-2} frente a {p_otro_pico_0-2-2}), cuando el "
  "cupo ya estaría ocupado. *Probablemente* el agente reserva el cupo para la noche, donde aplazar sí compensa "
  "(ΔQ = {ex_dQ_1-3-2-0}, valle a {horas_valle_x_1-3-2}). **Ojo: la decisión se juega por milésimas de kWh-eq.**", alin="j")
P("**Regla 3 — Rescata la carga pendiente.** Con una carga esperando en la mañana y demanda baja, la codiciosa sigue "
  "esperando: una hora más (−0,02) parece más barata que el sobrecosto de punta. π* suma las {regla_0-1-0-1_horas} que "
  "faltan hasta el valle y prefiere ejecutar ya. En la tarde el detalle es más fino: con demanda media π* elige "
  "«{ex_pol_0-2-1-1}» y con demanda alta «{ex_pol_0-2-2-1}», es decir, espera. Probablemente porque un nivel alto en la tarde "
  "delata la joroba de las 17 h, cuando el valle está más cerca ({horas_valle_x_0-2-2} frente a {regla_0-2-1-1_horas}).",
  alin="j")

H2("4.3 La batalla fuera de muestra: mayo, el mes que el modelo nunca vio")
P("Se recorre mayo hora por hora con la demanda real. Cada política decide, y sus acciones mueven ΔE y abren o cierran "
  "la carga pendiente. El costo se cobra en la hora en que se consume la energía y a la tarifa de esa hora (la cuenta "
  "real, sin descuento). Al lado va el mismo cálculo en enero–abril, dentro de la muestra.", alin="j")
tabla(["Perfil · política", "Ahorro mayo", "Espera mayo", "Aplazamientos/día mayo", "Ahorro ene–abr", "Espera ene–abr"], [
    ["Paciente · regla fija = codiciosa = **π\***", "{ahorro_opt_te}", "{espera_opt_te}", "{aplaz_opt_te}",
     "{ahorro_opt_tr}", "{espera_opt_tr}"],
    ["Exigente · regla fija = codiciosa", "{ex_ahorro_cod_te}", "{ex_espera_cod_te}", "{ex_aplaz_cod_te}",
     "{ex_ahorro_cod_tr}", "{ex_espera_cod_tr}"],
    ["Exigente · **π\***", "{ex_ahorro_opt_te}", "{ex_espera_opt_te}", "{ex_aplaz_opt_te}", "{ex_ahorro_opt_tr}",
     "{ex_espera_opt_tr}"],
], [5.2, 2.2, 2.2, 2.6, 2.2, 2.2], tam=9)
figura("R6_batalla.png", "Batalla de las políticas en el perfil paciente: ahorro de costo frente a no actuar y horas con una "
       "carga esperando, en enero–abril y en mayo.")
P("Las diferencias se miden en el objetivo del MDP (costo + λ · espera) con **bootstrap pareado por día** (2.000 réplicas, "
  "semilla 42):", alin="j")
V_([
    "**Paciente, π* frente a no actuar:** mayo {boot_no_te} → *no se distingue*; enero–abril {boot_no_tr} → sí.",
    "**Exigente, π* frente a la codiciosa:** mayo {ex_boot_cod_te} → *no se distingue*; enero–abril {ex_boot_cod_tr} → "
    "sí. En la práctica, π* resigna algo de ahorro (de {ex_ahorro_cod_te} a {ex_ahorro_opt_te}) a cambio de esperar "
    "menos (de {ex_espera_cod_te} a {ex_espera_opt_te}).",
])
P("**Lectura honesta:** con esta tarifa y este hogar, aplazar mueve el {ahorro_opt_te} del costo, y con {n_dias_te} "
  "días de mayo ese efecto no se separa del ruido. La política es sensata y se comporta igual dentro y fuera de muestra; "
  "lo que el gemelo no puede prometer es un ahorro grande por tarifa.", alin="j")

H2("4.4 Sensibilidad: tarifa y precio de la espera")
figura("R7_sensibilidad.png", "Estados que aplazan y ahorro en mayo para cada combinación de λ y tarifa de punta (el MDP se "
       "resuelve de nuevo en cada celda).")
P("Con tarifa plana ninguna combinación aplaza: la prueba de cordura se cumple en toda la columna. Con la tarifa de "
  "punta en 1,5, los estados que aplazan pasan de {sens_nap_0p005_1p5} a {sens_nap_0p01_1p5} y a {sens_nap_0p02_1p5} "
  "cuando λ sube de 0,005 a 0,01 y a 0,02. En el perfil exigente se conservan los aplazamientos de la noche (valle a "
  "{horas_valle_3} en promedio) y el de la tarde de un día normal. Con γ = 0,99 aplaza en {gamma_0p99_nap} de los 6 "
  "estados posibles; con γ ≤ 0,95, en {gamma_0p95_nap}.", alin="j")

# =====================================================================================
H1("5. Qué cambia en el diseño de Shiro por estos números")
recuadro("Decisiones que quedan tomadas", [
    "**El estado del agente de Q-learning (Taller 2) lleva la carga pendiente.** Sin ella, aplazar borraría consumo. La "
    "**contabilidad corregida** se conserva en el entorno: la ingenua produce un agente que nunca ejecuta.",
    "**λ es un control de la persona, no una constante del modelo.** Resolver el MDP tarda décimas de segundo, así que la "
    "política se recalcula con cada valor. La interfaz debe mostrar el par «cuánto ahorra / cuánto espera», igual que "
    "Guardian muestra el tiempo en alerta.",
    "**Las decisiones con margen de milésimas (regla 2) se presentan como dudosas** y quedan a criterio de la persona: "
    "el margen entre Q(aplazar) y Q(no actuar) funciona como confianza, igual que el margen al centroide en el tipo de día.",
    "**El tipo de día sí entra al estado:** cambia la decisión de la tarde en el perfil exigente.",
    "**La hora dentro de la franja importa (regla 3).** En el Taller 2 se probarán bloques de 3 h si la cobertura alcanza.",
    "**Expectativa de ahorro:** aplazar por tarifa mueve un {ahorro_opt_te} en mayo, sin separarse del ruido. El techo "
    "sigue siendo saber qué aparato se enciende (hallazgos 4 y 31). Todo ahorro se reporta como simulado.",
])
recuadro("Límites que se declaran", [
    "ΔE (40 % del exceso) y la tarifa relativa son supuestos; se barren, pero no se miden.",
    "La demanda se supone independiente de la acción, con un solo cupo de carga pendiente.",
    "El nivel es el de la hora en curso: Shiro *ve arrancar* la carga y aplaza el resto, no la anticipa (ver Parcial 2).",
    "Solo {n_dias_te} días de prueba. En mayo los días de carga alta bajan del {pct_alto_tr} al {pct_alto_te}.",
    "Hay estados con pocas visitas (mínimo {vis_min}), y no hay acción térmica: el confort entra como costo de espera, no "
    "como temperatura.",
], color=NARANJA)

H1("6. Reproducibilidad")
V_([
    "`Taller1_C3_MDP_Shiro.ipynb`: pasos 1–5 del ejemplo adaptados y la Parte 3 completa. Corre de principio a fin y "
    "escribe `cifras.json`, la política en CSV y las figuras R1–R8.",
    "`generadores/`: construye y ejecuta el cuaderno, este documento y la presentación. Todas las cifras de este documento "
    "salen de `cifras.json`.",
    "Datos: `data set/energydata_complete.csv` (UCI n.º 374). Semilla 42 en todo.",
])


def main():
    doc.save(SALIDA)
    print(f"Documento: {SALIDA.name}")
    pdf = exportar_pdf(SALIDA, SALIDA.with_suffix(".pdf"))
    print(f"PDF: {pdf.name}")


if __name__ == "__main__":
    main()
