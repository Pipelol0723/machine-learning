# -*- coding: utf-8 -*-
r"""Artículo IEEE del semestre (Parcial 3, parte 2): Articulo_IEEE_Shiro_Twin.docx y su PDF.

Toda cifra de resultado entra como {prefijo:clave} y se resuelve con comun.C (fuente única: cifras de P2, T1, T2, T3,
C2 y P3). {prefijo:clave|n} deja solo el número, sin su unidad. Las citas se escriben [[clave]] y se numeran en orden
de aparición, al estilo IEEE. Marcado en línea: [b]negrita[/b] e [i]cursiva[/i].

Figuras propias (prefijo A, se regeneran en cada corrida):
    figuras/A1_arquitectura.png   arquitectura de Shiro Twin
    figuras/A2_tipos_dia.png      los dos tipos de día (K-Means k = 2 recalculado y anclado contra cifras_c2.json)
    figuras/A4_arranque_frio.png  T2_arranque_frio (C3-T3) sin su título interno, a doble columna
Figuras reutilizadas: POSTER_G2 (Parcial 2) y, si existe, figuras/consola_captura.png (captura de la consola; si falta
se avisa y la Fig. 5 se omite).

Uso (desde la carpeta del parcial):
    C:\Users\pipel\venvs\ml\Scripts\python.exe -X utf8 generadores\generar_articulo.py
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402
from docx import Document  # noqa: E402
from docx.enum.section import WD_SECTION  # noqa: E402
from docx.enum.table import WD_TABLE_ALIGNMENT  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT  # noqa: E402
from docx.oxml import OxmlElement  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.shared import Inches, Pt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402

RAIZ, PROY = comun.RAIZ, comun.PROY
FIG = RAIZ / "figuras"
DOCX = RAIZ / "Articulo_IEEE_Shiro_Twin.docx"
PDF = DOCX.with_suffix(".pdf")
CSV = PROY / "data set" / "energydata_complete.csv"
F_G2 = PROY / "2do_Corte_Oct" / "Parcial_2_Aprendizaje_Supervisado" / "figuras" / "POSTER_G2.png"
F_T2 = PROY / "3er_Corte_Nov" / "Taller_3_DQN" / "figuras" / "T2_arranque_frio.png"
F_CONSOLA = FIG / "consola_captura.png"
F_T4 = FIG / "A4_arranque_frio.png"     # T2_arranque_frio sin su título interno (el pie lo reemplaza)

COL_IN = 3.5          # ancho de columna IEEE (pulgadas)
TEXTO_IN = 7.25       # ancho del texto a dos columnas
SEP_IN = 0.25         # separación entre columnas
FUENTE = "Times New Roman"

# =====================================================================================================================
# Cifras, citas y marcado
# =====================================================================================================================
_NUM = re.compile(r"^[−+]?\d[\d.]*(?:,\d+)?")


def _cifra(clave, mod):
    t = comun.C(clave)
    t = re.sub(r"(?<![\w])-(?=\d)", "−", t)            # signo menos tipográfico
    if mod == "n":
        m = _NUM.match(t)
        t = m.group(0) if m else t
    return t


def F(texto):
    return re.sub(r"\{([a-z0-9]+:[^{}|]+)(?:\|([a-z]+))?\}", lambda m: _cifra(m.group(1), m.group(2)), texto)


def V(clave):
    return comun.V(clave)


REFS = {
    "candanedo": 'L. M. Candanedo, V. Feldheim y D. Deramaix, "Data driven prediction models of energy use of appliances '
                 'in a low-energy house," [i]Energy and Buildings[/i], vol. 140, pp. 81–97, 2017.',
    "efron": "B. Efron y R. J. Tibshirani, [i]An Introduction to the Bootstrap[/i]. New York, NY, USA: Chapman & Hall, 1993.",
    "breiman": 'L. Breiman, "Random forests," [i]Machine Learning[/i], vol. 45, no. 1, pp. 5–32, 2001.',
    "ke": 'G. Ke [i]et al.[/i], "LightGBM: A highly efficient gradient boosting decision tree," en [i]Advances in Neural '
          'Information Processing Systems 30[/i], 2017, pp. 3146–3154.',
    "lloyd": 'S. P. Lloyd, "Least squares quantization in PCM," [i]IEEE Trans. Inf. Theory[/i], vol. 28, no. 2, '
             'pp. 129–137, 1982.',
    "rousseeuw": 'P. J. Rousseeuw, "Silhouettes: A graphical aid to the interpretation and validation of cluster '
                 'analysis," [i]J. Comput. Appl. Math.[/i], vol. 20, pp. 53–65, 1987.',
    "dunn": 'J. C. Dunn, "Well-separated clusters and optimal fuzzy partitions," [i]J. Cybernetics[/i], vol. 4, no. 1, '
            'pp. 95–104, 1974.',
    "ward": 'J. H. Ward, "Hierarchical grouping to optimize an objective function," [i]J. Amer. Statist. Assoc.[/i], '
            'vol. 58, no. 301, pp. 236–244, 1963.',
    "hubert": 'L. Hubert y P. Arabie, "Comparing partitions," [i]J. Classification[/i], vol. 2, no. 1, pp. 193–218, 1985.',
    "ester": 'M. Ester, H.-P. Kriegel, J. Sander y X. Xu, "A density-based algorithm for discovering clusters in large '
             'spatial databases with noise," en [i]Proc. 2nd Int. Conf. Knowledge Discovery and Data Mining (KDD-96)[/i], '
             '1996, pp. 226–231.',
    "sutton": "R. S. Sutton y A. G. Barto, [i]Reinforcement Learning: An Introduction[/i], 2.ª ed. Cambridge, MA, USA: "
              "MIT Press, 2018.",
    "watkins": 'C. J. C. H. Watkins y P. Dayan, "Q-learning," [i]Machine Learning[/i], vol. 8, no. 3–4, pp. 279–292, 1992.',
    "evendar": 'E. Even-Dar e Y. Mansour, "Learning rates for Q-learning," [i]J. Mach. Learn. Res.[/i], vol. 5, '
               'pp. 1–25, 2003.',
    "mnih": 'V. Mnih [i]et al.[/i], "Human-level control through deep reinforcement learning," [i]Nature[/i], vol. 518, '
            'no. 7540, pp. 529–533, 2015.',
    "lin": 'L.-J. Lin, "Self-improving reactive agents based on reinforcement learning, planning and teaching," '
           '[i]Machine Learning[/i], vol. 8, no. 3–4, pp. 293–321, 1992.',
    "hasselt": 'H. van Hasselt, A. Guez y D. Silver, "Deep reinforcement learning with double Q-learning," en '
               '[i]Proc. AAAI Conf. Artificial Intelligence[/i], vol. 30, 2016, pp. 2094–2100.',
}
ORDEN_CITAS = []


def _citas(texto):
    def rep(m):
        out = []
        for c in [x.strip() for x in m.group(1).split(",")]:
            if c not in REFS:
                raise KeyError(f"Cita desconocida: {c}")
            if c not in ORDEN_CITAS:
                ORDEN_CITAS.append(c)
            out.append(f"[{ORDEN_CITAS.index(c) + 1}]")
        return ", ".join(out)
    return re.sub(r"\[\[([a-z, ]+)\]\]", rep, texto)


_UNIDAD = re.compile(r"(?<=\d) (?=(%|Wh\b|kWh|h/día|h\b|min\b|°C|puntos\b|días\b|picos\b|avisos/día|min/día|semillas\b))")


def prep(texto):
    t = _UNIDAD.sub("\u00a0", _citas(F(texto)))
    return t.replace("≥ ", "≥\u00a0")


# =====================================================================================================================
# Figuras propias
# =====================================================================================================================
def fig_arquitectura(ruta):
    plt.rcParams.update({"font.family": "DejaVu Sans"})
    fig, ax = plt.subplots(figsize=(3.45, 3.3), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10.2)
    ax.axis("off")
    GRIS, BORDE, TINTA, SUAVE = "#f3f3f3", "#4d4d4d", "#1a1a1a", "#6b6b6b"
    ACENTO, ACENTO_F = "#1f4e79", "#e3ebf4"

    def caja(x0, y0, x1, y1, titulo, sub, etiqueta=None, fc=GRIS, ec=BORDE, lw=0.7):
        ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0,rounding_size=0.22",
                                    fc=fc, ec=ec, lw=lw))
        cx = (x0 + x1) / 2
        ax.text(cx, y1 - 0.42, titulo, ha="center", va="center", fontsize=6.8, fontweight="bold", color=TINTA)
        ax.text(cx, (y0 + y1) / 2 - (0.05 if etiqueta else 0.2), sub, ha="center", va="center", fontsize=5.9, color=TINTA)
        if etiqueta:
            ax.text(cx, y0 + 0.33, etiqueta, ha="center", va="center", fontsize=5.3, color=ec if ec != BORDE else SUAVE,
                    fontweight="bold")

    def flecha(x0, y0, x1, y1, estilo="-|>", ls="-", color=BORDE):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle=estilo, lw=0.75, color=color, ls=ls, shrinkA=0, shrinkB=0,
                                    mutation_scale=7))

    X0, X1 = 0.15, 9.05
    caja(X0, 8.75, X1, 10.05, "Hogar · UCI n.º 374", "consumo, luces, 9 habitaciones y clima, cada 10 min", "DATOS")
    filas = [(0.15, 2.95, "Gemelo digital", "lineal + retardos", "SUPERVISADO", "transición (prevista)", True),
             (3.2, 6.0, "Tipo de día", "K-Means · DBSCAN", "NO SUPERVISADO", "contexto", False),
             (6.25, 9.05, "Guardian (G0)", "¿pico en 30 min?", "SUPERVISADO", "aviso", False)]
    for x0, x1, t, s, e, rot, prevista in filas:
        caja(x0, 5.95, x1, 7.9, t, s, e)
        cx = (x0 + x1) / 2
        flecha(cx, 8.75, cx, 7.9)
        # el gemelo será el entorno continuo del agente: hoy el agente se entrena en una réplica de días reales
        flecha(cx, 5.95, cx, 5.05, ls=(0, (3, 2)) if prevista else "-", color=SUAVE if prevista else BORDE)
        ax.text(cx + 0.12, 5.5, rot, ha="left", va="center", fontsize=5.6, style="italic", color=SUAVE)
    caja(X0, 3.2, X1, 5.05, "Agente: π*, Q-learning, DQN", "estado: tipo de día, franja, nivel, carga pendiente",
         "REFUERZO", fc=ACENTO_F, ec=ACENTO, lw=1.0)
    caja(1.9, 0.25, 7.3, 2.0, "Persona", "aprueba o rechaza · fija λ")
    flecha(4.6, 3.2, 4.6, 2.0)
    ax.text(4.72, 2.6, "propuesta", ha="left", va="center", fontsize=5.6, style="italic", color=SUAVE)
    # lazo de vuelta: la acción aprobada llega a la casa (Shiro Home)
    ax.plot([7.3, 9.55, 9.55], [1.125, 1.125, 9.4], color=SUAVE, lw=0.75, ls=(0, (3, 2)))
    flecha(9.55, 9.4, X1, 9.4, color=SUAVE)
    ax.text(9.8, 5.2, "acción aprobada (Shiro Home)", rotation=90, ha="center", va="center", fontsize=5.6,
            style="italic", color=SUAVE)
    fig.subplots_adjust(0, 0, 1, 1)
    fig.savefig(ruta, dpi=300)
    plt.close(fig)


def fig_arranque_sin_titulo(origen, ruta):
    """Recorta el título interno de T2_arranque_frio.png (la figura no se puede redibujar: no se guardaron sus curvas)."""
    from PIL import Image
    im = Image.open(origen).convert("RGB")
    g = np.asarray(im.convert("L"))
    tinta = (g < 200).any(axis=1)
    filas = np.flatnonzero(tinta)
    a = filas[0]
    b = a
    while b + 1 < len(tinta) and tinta[b + 1]:
        b += 1                                  # fin de la banda del título
    c = b + 1
    while c < len(tinta) and not tinta[c]:
        c += 1                                  # comienzo del gráfico
    assert b < 0.12 * g.shape[0] and c < 0.2 * g.shape[0], (a, b, c)
    im.crop((0, max(b + 1, c - 6), im.width, im.height)).save(ruta, dpi=im.info.get("dpi", (150, 150)))


def fig_tipos_dia(ruta):
    """Los dos tipos de día del C2-T2, redibujados a ancho de columna (mismo K-Means: k = 2, n_init = 10, semilla 42)."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    df = pd.read_csv(CSV, parse_dates=["date"])
    df["dia"] = df["date"].dt.normalize()
    df["hora"] = df["date"].dt.hour
    n = df.groupby("dia").size()
    d = df[df["dia"].isin(n[n == 144].index)]
    nivel = d.groupby(["dia", "hora"])["Appliances"].mean().unstack()
    X = nivel.values
    lab = KMeans(n_clusters=2, n_init=10, random_state=42).fit_predict(X)
    alta = int(np.argmax([X[lab == c].sum(1).mean() for c in (0, 1)]))
    n_alta, n_norm = int((lab == alta).sum()), int((lab != alta).sum())
    sil = silhouette_score(X, lab)
    # anclas contra la fuente única (cifras_c2.json)
    assert n_norm == V("c2:km_n_normal") and n_alta == V("c2:km_n_alta"), (n_norm, n_alta)
    assert abs(sil - V("c2:km_silueta")) < 5e-4, sil
    plt.rcParams.update({"font.family": "DejaVu Sans"})
    fig, ax = plt.subplots(figsize=(3.45, 2.15), dpi=300)
    h = np.arange(24)
    for es_alta, color, nombre in ((False, "#1f4e79", "día normal"), (True, "#c55a11", "día de carga alta")):
        M = X[(lab == alta) == es_alta]
        ax.fill_between(h, np.percentile(M, 10, axis=0), np.percentile(M, 90, axis=0), color=color, alpha=0.16, lw=0)
        ax.plot(h, M.mean(0), color=color, lw=1.6,
                label=f"{nombre} ({comun.C('c2:km_n_alta' if es_alta else 'c2:km_n_normal')})")
    ax.set_xlim(0, 23)
    ax.set_ylim(0, None)
    ax.set_xticks(range(0, 24, 3))
    ax.set_xlabel("Hora del día", fontsize=7)
    ax.set_ylabel("Consumo medio por hora (Wh)", fontsize=7)
    ax.tick_params(labelsize=6.5, length=2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color="#dddddd", lw=0.5)
    ax.legend(frameon=False, fontsize=6.5, loc="upper left")
    fig.tight_layout(pad=0.3)
    fig.savefig(ruta, dpi=300)
    plt.close(fig)


# =====================================================================================================================
# Utilidades de Word
# =====================================================================================================================
doc = Document()


def _fuente_run(r, size, bold=False, italic=False, smallcaps=False):
    r.font.name = FUENTE
    r._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), FUENTE)
    r.font.size = Pt(size)
    r.bold = bold or None
    r.italic = italic or None
    if smallcaps:
        r.font.small_caps = True


def escribir(p, texto, size=10, bold=False, italic=False, smallcaps=False):
    """Escribe texto con marcado [b]..[/b], [i]..[/i], [s]..[/s] (subíndice) y [p]..[/p] (superíndice)."""
    b, i, sub, sup = bold, italic, False, False
    for tok in re.split(r"(\[/?[bisp]\])", texto):
        if tok in ("[b]", "[/b]"):
            b = True if tok == "[b]" else bold
        elif tok in ("[i]", "[/i]"):
            i = True if tok == "[i]" else italic
        elif tok in ("[s]", "[/s]"):
            sub = tok == "[s]"
        elif tok in ("[p]", "[/p]"):
            sup = tok == "[p]"
        elif tok:
            r = p.add_run(tok)
            _fuente_run(r, size, b, i or sub, smallcaps)
            if sub:
                r.font.subscript = True
            if sup:
                r.font.superscript = True
    return p


def _formato(p, alin=WD_ALIGN_PARAGRAPH.JUSTIFY, sangria=0.0, antes=0, despues=0, juntar=False, izq=0.0):
    pf = p.paragraph_format
    p.alignment = alin
    pf.first_line_indent = Inches(sangria) if sangria else None
    pf.left_indent = Inches(izq) if izq else None
    pf.space_before = Pt(antes)
    pf.space_after = Pt(despues)
    pf.line_spacing = 1.0
    pf.keep_with_next = juntar or None
    return p


def parrafo(texto, sangria=True):
    p = _formato(doc.add_paragraph(), sangria=0.15 if sangria else 0)
    return escribir(p, prep(texto))


def decision(texto):
    """Cierre de cada sección: la decisión de arquitectura que se tomó."""
    return parrafo("[b][i]Decisión para Shiro.[/i][/b] " + texto)


def h1(texto):
    p = _formato(doc.add_paragraph(), alin=WD_ALIGN_PARAGRAPH.CENTER, antes=7, despues=3, juntar=True)
    return escribir(p, texto, smallcaps=True)


def h2(texto):
    p = _formato(doc.add_paragraph(), alin=WD_ALIGN_PARAGRAPH.LEFT, antes=4, despues=1, juntar=True)
    return escribir(p, texto, italic=True)


def lista(items):
    for k, it in enumerate(items, 1):
        p = _formato(doc.add_paragraph(), izq=0.22, sangria=-0.17)
        escribir(p, f"{k})\u00a0" + prep(it))


def ecuacion(texto, n):
    p = _formato(doc.add_paragraph(), alin=WD_ALIGN_PARAGRAPH.LEFT, antes=3, despues=3)
    ts = p.paragraph_format.tab_stops
    ts.add_tab_stop(Inches(COL_IN / 2), WD_TAB_ALIGNMENT.CENTER)
    ts.add_tab_stop(Inches(COL_IN), WD_TAB_ALIGNMENT.RIGHT)
    escribir(p, "\t" + prep(texto) + f"\t({n})")


N_FIG = [0]


def figura(ruta, ancho, pie):
    N_FIG[0] += 1
    p = _formato(doc.add_paragraph(), alin=WD_ALIGN_PARAGRAPH.CENTER, antes=4, despues=2, juntar=True)
    p.add_run().add_picture(str(ruta), width=Inches(ancho))
    c = _formato(doc.add_paragraph(), antes=0, despues=6)
    escribir(c, f"Fig. {N_FIG[0]}.\u2002" + prep(pie), size=8)
    return N_FIG[0]


def _sectpr_columnas(sec, n):
    sp = sec._sectPr
    cols = sp.find(qn("w:cols"))
    if cols is None:
        cols = OxmlElement("w:cols")
        sp.append(cols)
    cols.set(qn("w:num"), str(n))
    cols.set(qn("w:space"), str(int(SEP_IN * 1440)))


def nueva_seccion(columnas):
    """Salto de sección continuo; el párrafo que guarda el salto se reduce a 1 pt para no dejar un hueco."""
    doc.add_section(WD_SECTION.CONTINUOUS)
    marca = doc.paragraphs[-1]
    marca.paragraph_format.space_before = Pt(0)
    marca.paragraph_format.space_after = Pt(0)
    marca.paragraph_format.line_spacing = Pt(1)
    ppr = marca._p.get_or_add_pPr()
    mrpr = OxmlElement("w:rPr")
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), "2")
    mrpr.append(sz)
    sp = ppr.find(qn("w:sectPr"))
    (sp.addprevious(mrpr) if sp is not None else ppr.append(mrpr))
    _sectpr_columnas(doc.sections[-1], columnas)


def figura_ancha(ruta, pie):
    """Figura a doble columna: sección continua de una columna entre dos de dos columnas."""
    nueva_seccion(1)
    n = figura(ruta, TEXTO_IN - 0.1, pie)
    nueva_seccion(2)
    return n


def _borde(el, lado, val="single", sz=8):
    b = OxmlElement(f"w:{lado}")
    b.set(qn("w:val"), val)
    b.set(qn("w:sz"), str(sz))
    b.set(qn("w:space"), "0")
    b.set(qn("w:color"), "000000")
    el.append(b)


N_TAB = [0]
ROMANOS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


def tabla(titulo, encabezado, filas, anchos, nota=None):
    """Tabla IEEE: «TABLA I» y título encima, filetes arriba, bajo el encabezado y abajo. Una fila que es un str es un
    subtítulo que ocupa todo el ancho."""
    N_TAB[0] += 1
    c1 = _formato(doc.add_paragraph(), alin=WD_ALIGN_PARAGRAPH.CENTER, antes=6, despues=0, juntar=True)
    escribir(c1, f"Tabla {ROMANOS[N_TAB[0] - 1]}", size=8, smallcaps=True)
    c2 = _formato(doc.add_paragraph(), alin=WD_ALIGN_PARAGRAPH.CENTER, antes=0, despues=3, juntar=True)
    escribir(c2, prep(titulo), size=8, smallcaps=True)
    t = doc.add_table(rows=1 + len(filas), cols=len(encabezado))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    tblPr = t._tbl.tblPr
    lay = OxmlElement("w:tblLayout")
    lay.set(qn("w:type"), "fixed")
    tblPr.append(lay)
    bordes = OxmlElement("w:tblBorders")
    _borde(bordes, "top", sz=8)
    _borde(bordes, "left", "nil")
    _borde(bordes, "bottom", sz=8)
    _borde(bordes, "right", "nil")
    _borde(bordes, "insideH", "nil")
    _borde(bordes, "insideV", "nil")
    tblPr.append(bordes)
    mar = OxmlElement("w:tblCellMar")
    for lado, v in (("left", 50), ("right", 50), ("top", 10), ("bottom", 10)):
        e = OxmlElement(f"w:{lado}")
        e.set(qn("w:w"), str(v))
        e.set(qn("w:type"), "dxa")
        mar.append(e)
    tblPr.append(mar)

    def celda(c, texto, ancho, alin, bold=False, italic=False, borde_abajo=False):
        c.width = Inches(ancho)
        p = c.paragraphs[0]
        _formato(p, alin=alin)
        escribir(p, prep(texto), size=8, bold=bold, italic=italic)
        if borde_abajo:
            tcb = OxmlElement("w:tcBorders")
            _borde(tcb, "bottom", sz=4)
            c._tc.get_or_add_tcPr().append(tcb)

    for j, e in enumerate(encabezado):
        celda(t.rows[0].cells[j], e, anchos[j], WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER,
              borde_abajo=True)
    for fila_t in t.rows:
        trpr = fila_t._tr.get_or_add_trPr()
        cs = OxmlElement("w:cantSplit")
        trpr.append(cs)
    for i, fila in enumerate(filas, 1):
        cells = t.rows[i].cells
        if isinstance(fila, str):
            m = cells[0].merge(cells[-1])
            celda(m, fila, sum(anchos), WD_ALIGN_PARAGRAPH.LEFT, italic=True)
            continue
        for j, v in enumerate(fila):
            celda(cells[j], v, anchos[j], WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER)
    for fila_t in t.rows[:-1]:
        for c in fila_t.cells:
            for pp in c.paragraphs:
                pp.paragraph_format.keep_with_next = True
    if nota:
        p = _formato(doc.add_paragraph(), antes=2, despues=8)
        escribir(p, prep(nota), size=7)
    else:
        _formato(doc.add_paragraph(), despues=4)


# =====================================================================================================================
# Documento
# =====================================================================================================================
def configurar():
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    sec.top_margin, sec.bottom_margin = Inches(0.75), Inches(1.0)
    sec.left_margin = sec.right_margin = Inches(0.625)
    sec.header_distance, sec.footer_distance = Inches(0.4), Inches(0.4)
    _sectpr_columnas(sec, 1)
    st = doc.styles["Normal"]
    st.font.name = FUENTE
    st.font.size = Pt(10)
    rpr = st.element.get_or_add_rPr()
    rf = rpr.get_or_add_rFonts()
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(a), FUENTE)
    lang = OxmlElement("w:lang")
    lang.set(qn("w:val"), "es-CO")
    lang.set(qn("w:eastAsia"), "es-CO")
    lang.set(qn("w:bidi"), "ar-SA")
    rpr.append(lang)
    pf = st.paragraph_format
    pf.space_before, pf.space_after, pf.line_spacing = Pt(0), Pt(0), 1.0
    pf.widow_control = True
    # separación silábica automática (mejora el justificado en columnas estrechas)
    s = doc.settings.element
    ancla = s.find(qn("w:defaultTabStop"))
    hy = OxmlElement("w:autoHyphenation")
    hy.set(qn("w:val"), "true")
    (ancla.addnext(hy) if ancla is not None else s.append(hy))
    core = doc.core_properties
    core.title = "Shiro Twin: un gemelo digital del hogar que predice, anticipa picos y propone cuándo aplazar cargas"
    core.author = "Jose Leonardo Diazgranados, Sofía Londoño, Andrés Felipe Céspedes Rondón, Alex Duran"
    core.language = "es-CO"


def construir():
    configurar()
    FIG.mkdir(exist_ok=True)
    fa1, fa2 = FIG / "A1_arquitectura.png", FIG / "A2_tipos_dia.png"
    fig_arquitectura(fa1)
    fig_tipos_dia(fa2)
    fig_arranque_sin_titulo(F_T2, F_T4)

    # ---------------------------------------------------------------- título y autores (una columna)
    p = _formato(doc.add_paragraph(), alin=WD_ALIGN_PARAGRAPH.CENTER, antes=6, despues=10)
    escribir(p, "Shiro Twin: un gemelo digital del hogar que predice, anticipa picos y propone cuándo aplazar cargas",
             size=24)
    p = _formato(doc.add_paragraph(), alin=WD_ALIGN_PARAGRAPH.CENTER, despues=2)
    escribir(p, "Jose Leonardo Diazgranados, Sofía Londoño, Andrés Felipe Céspedes Rondón y Alex Duran", size=11)
    p = _formato(doc.add_paragraph(), alin=WD_ALIGN_PARAGRAPH.CENTER, despues=1)
    escribir(p, "Aprendizaje de Máquina 26-2", size=10, italic=True)
    p = _formato(doc.add_paragraph(), alin=WD_ALIGN_PARAGRAPH.CENTER, despues=12)
    escribir(p, "Universidad Sergio Arboleda, Colombia", size=10, italic=True)
    nueva_seccion(2)

    # ---------------------------------------------------------------- resumen
    p = _formato(doc.add_paragraph(), sangria=0.15, despues=4)
    escribir(p, "[i]Resumen[/i]—" + prep(
        "Shiro es un asistente de energía para el hogar que se construye en tres fases: Shiro Twin, un gemelo digital "
        "que solo propone; Guardian, que avisa; y Home, que actúa en la casa con aprobación de la persona. Sobre una "
        "vivienda belga (UCI n.º 374, {p2:datos_n_lecturas} cada 10 min), el artículo ordena el trabajo del semestre "
        "según lo que el gemelo necesitaba. Para la "
        "función de transición, la partición temporal invirtió el tablero supervisado: Random Forest pasa de R² "
        "{p2:her_reg_rf_aleatoria_r2} en la partición aleatoria a {p2:her_reg_rf_temporal_r2} en la temporal; con "
        "variables de retardo, la regresión lineal sube de {p2:her_reg_lineal_temporal_r2} a "
        "{p2:her_bo_lineal_retardos_r2} en la partición temporal, mientras Random Forest con retardos sigue en "
        "{p2:her_bo_rf_retardos_r2}. Para el contexto, K-Means encontró dos tipos de día que el calendario no explica. "
        "Para avisar, un modelo de dos variables anticipa {p2:titular_n20|n} de {p2:def_picos_prueba|n} picos de mayo "
        "con al menos dos lecturas (≥ 20 min) de antelación, y ningún modelo de {p2:part_n_variables} variables se "
        "distingue de él. Para decidir, un MDP de {t1:n_estados} estados con contabilidad corregida muestra que "
        "aplazar por tarifa ahorra apenas el {t1:ahorro_opt_te} del costo de mayo; con una recompensa centrada, "
        "Q-learning tabular captura al menos el 80 % de ese ahorro desde el día {t3:qlc_dias80|n} de experiencia "
        "simulada y una DQN llega al {t3:dqn_captura}. Una consola web ejecuta los tres paradigmas en el navegador. "
        "Límites: una sola vivienda, sin verano y sin saber qué aparato se enciende."),
             size=9, bold=True)
    p = _formato(doc.add_paragraph(), sangria=0.15, despues=6)
    escribir(p, "[i]Palabras clave[/i]—gemelo digital, consumo eléctrico residencial, partición temporal, agrupamiento "
                "de días, anticipación de picos, proceso de decisión de Markov, Q-learning, DQN.", size=9, bold=True)

    # ---------------------------------------------------------------- I
    h1("I. Introducción")
    parrafo("Un hogar paga por la energía que consume y por la hora en que la consume: los picos en horas de punta "
            "cuestan más y son lo que una persona podría correr de hora si supiera a tiempo que vienen. Shiro es el "
            "asistente que el grupo diseña para eso, en tres fases: [b]Shiro Twin[/b], un gemelo digital que simula el "
            "hogar y solo propone; [b]Guardian[/b], que avisa antes de un pico; y [b]Shiro Home[/b], que actúa en la "
            "casa con la aprobación de la persona. Este curso construyó Shiro Twin (Fig. 1).")
    pie_fig1 = ("Arquitectura de Shiro Twin. El gemelo lineal (supervisado) es el simulador previsto para el entorno "
                "continuo del agente (flecha discontinua; hoy el agente se entrena en una réplica de días reales); el "
                "tipo de día (no supervisado) y el aviso de Guardian entran a su estado. El agente propone y la persona "
                "decide; en Shiro Home, la acción aprobada vuelve a la casa.")
    parrafo("El gemelo necesita cuatro piezas y cada una se construyó con un paradigma distinto: una [i]función de "
            "transición[/i] que diga cuánto consumirá la casa en el paso siguiente (supervisado), un [i]contexto[/i] "
            "que diga qué tipo de día se está viviendo (no supervisado), una [i]señal anticipada[/i] de pico para "
            "Guardian (supervisado, evaluado por antelación) y un [i]agente[/i] que decida si aplazar una carga "
            "(refuerzo). La pregunta que atraviesa el semestre es qué necesita saber el gemelo digital de un solo hogar "
            "para proponer, con honestidad, cuándo aplazar una carga, y cuánto ahorro real hay detrás de esa propuesta. "
            "Las contribuciones son cinco: 1) una evaluación con dos particiones que invierte el tablero supervisado "
            "(Sec. III); 2) el tipo de día como estimación con confianza, auditada con tres algoritmos (Sec. IV); 3) una "
            "evaluación de Guardian por antelación, que separa reconocer un pico de anticiparlo (Sec. V); 4) una "
            "contabilidad corregida y una recompensa centrada que vuelven aprendible la decisión de aplazar (Sec. VI), y "
            "5) una consola que ejecuta los tres paradigmas con cifras verificadas (Sec. VII).")
    figura(fa1, 2.95, pie_fig1)

    # ---------------------------------------------------------------- II
    h1("II. Datos y método")
    parrafo("Todo componente de Shiro hereda las virtudes y los sesgos de un único conjunto de datos, así que las reglas "
            "de evaluación se fijaron antes que los modelos.")
    h2("A. El hogar")
    parrafo("Appliances Energy Prediction [[candanedo]] registra una vivienda de bajo consumo en Bélgica entre el 11 de "
            "enero y el 27 de mayo de 2016: {p2:datos_n_lecturas} cada 10 min, sin faltantes ({t1:n_dias} días "
            "completos). El objetivo es [i]Appliances[/i], el consumo de los aparatos en Wh. Hay {p2:part_n_exogenas} "
            "predictoras: cuatro temporales, el consumo de luces, la temperatura y la humedad de nueve habitaciones y "
            "seis variables del clima; se excluyen [i]rv1[/i] y [i]rv2[/i], ruido que los autores inyectaron como "
            "control. Se eligió este conjunto, frente a otros dos candidatos, porque es el único con temperatura "
            "interior por habitación, sin la cual no se puede calcular la penalización de confort de la recompensa.")
    h2("B. Dos particiones, siempre")
    parrafo("La partición aleatoria 80/20 (semilla 42), la del material del curso y la de [[candanedo]], responde "
            "«dado el estado observado, ¿cuánto consume?». La partición temporal entrena hasta el 30 de abril y prueba "
            "en mayo ({t1:n_dias_tr} y {t1:n_dias_te} días completos) y responde «¿generaliza a un mes que nunca "
            "vio?». Se reportan siempre las dos, pero toda decisión de arquitectura se toma con la temporal. La razón "
            "es la autocorrelación: dos lecturas consecutivas son casi idénticas, así que la partición aleatoria deja "
            "en el entrenamiento al vecino de 10 min de cada lectura de prueba; en KNN, K = 1 dio el mejor F1 de todos "
            "los K probados, la señal inequívoca de esa fuga.")
    h2("C. Retardos y convenciones")
    parrafo("El consumo de 10, 20, 30 y 60 min antes y la media, el máximo y la desviación de la última hora, siempre "
            "desplazados un paso para no mirar el presente, llevan el vector a {p2:part_n_variables} variables; solo se "
            "usan en la partición temporal, porque en la aleatoria filtrarían el valor que se quiere predecir. El umbral "
            "de anomalía es el percentil 90 del consumo de entrenamiento ({p2:part_umbral_wh}); calcularlo "
            "sobre todo el conjunto filtraría el mes de prueba. El escalado y los hiperparámetros se ajustan solo con el "
            "entrenamiento, por validación cruzada. En regresión manda el RMSE, que castiga los picos; en "
            "clasificación, el recall y el F1, porque decir siempre «normal» logra una exactitud de "
            "{p2:her_clf_base_aleatoria_accuracy} en la partición aleatoria con F1 nulo, y en el mes temporal de prueba, "
            "con solo el {p2:her_deriva_may_tasa} de lecturas sobre el umbral, esa exactitud engañosa sería aún mayor. "
            "Las diferencias "
            "entre señales o políticas llevan un intervalo de confianza (IC) del 95 % por bootstrap pareado por día "
            "[[efron]] (2.000 réplicas, semilla 42): si el IC incluye el cero, se dice que no se distinguen.")

    # ---------------------------------------------------------------- III
    h1("III. Qué consume la casa: aprendizaje supervisado")
    parrafo("El gemelo necesita una función de transición: dado el estado del hogar en [i]t[/i], el consumo en "
            "[i]t[/i] + 1. Es el simulador previsto para el entorno continuo en el que entrenará el agente de Shiro Home "
            "(hoy los agentes se entrenan en una réplica de días reales, Sec. VI), y de ella depende la incertidumbre "
            "que ese simulador declarará.")
    h2("A. El tablero se invierte")
    parrafo("La Tabla I resume los modelos de la primera mitad del curso. En la partición aleatoria gana la "
            "complejidad: LightGBM [[ke]] ({p2:her_bo_lgbm_aleatoria_r2}) y Random Forest [[breiman]] "
            "({p2:her_reg_rf_aleatoria_r2}) superan con amplitud a la regresión lineal "
            "({p2:her_reg_lineal_aleatoria_r2}). En la temporal el orden se invierte: la lineal es la única con R² "
            "positivo ({p2:her_reg_lineal_temporal_r2}) y Random Forest cae a {p2:her_reg_rf_temporal_r2}, peor que un "
            "árbol individual ({p2:her_reg_arbol_temporal_r2}). En clasificación ocurre lo mismo: el F1 de Random "
            "Forest para reconocer una lectura sobre el umbral baja de {p2:her_clf_rf_aleatoria_f1} a "
            "{p2:her_clf_rf_temporal_f1}, y el de SVM, de {p2:her_clf_svm_aleatoria_f1} a "
            "{p2:her_clf_svm_temporal_f1}. Precisión y robustez temporal son ejes distintos, y a un gemelo que debe "
            "simular meses futuros le importa el segundo.")
    tabla("Tablero supervisado con las dos particiones",
          ["Modelo", "Aleatoria", "Temporal", "Temporal + retardos"],
          ["Regresión del consumo (R²)",
           ["Regresión lineal", "{p2:her_reg_lineal_aleatoria_r2}", "[b]{p2:her_reg_lineal_temporal_r2}[/b]",
            "[b]{p2:her_bo_lineal_retardos_r2}[/b]"],
           ["Árbol de decisión", "{p2:her_reg_arbol_aleatoria_r2}", "{p2:her_reg_arbol_temporal_r2}", "—"],
           ["KNN (K = 5)", "{p2:her_reg_knn_aleatoria_r2}", "{p2:her_reg_knn_temporal_r2}", "—"],
           ["Random Forest", "{p2:her_reg_rf_aleatoria_r2}", "{p2:her_reg_rf_temporal_r2}", "{p2:her_bo_rf_retardos_r2}"],
           ["LightGBM", "[b]{p2:her_bo_lgbm_aleatoria_r2}[/b]", "{p2:her_bo_lgbm_temporal_r2}",
            "{p2:her_bo_lgbm_retardos_r2}"],
           ["XGBoost", "{p2:her_bo_xgb_aleatoria_r2}", "{p2:her_bo_xgb_temporal_r2}", "{p2:her_bo_xgb_retardos_r2}"],
           ["CatBoost", "{p2:her_bo_catboost_aleatoria_r2}", "{p2:her_bo_catboost_temporal_r2}",
            "{p2:her_bo_catboost_retardos_r2}"],
           "Clasificación: lectura sobre el umbral (F1)",
           ["Árbol de decisión", "{p2:her_clf_arbol_aleatoria_f1}", "{p2:her_clf_arbol_temporal_f1}", "—"],
           ["KNN (K = 3)", "{p2:her_clf_knn_aleatoria_f1}", "{p2:her_clf_knn_temporal_f1}", "—"],
           ["Random Forest", "[b]{p2:her_clf_rf_aleatoria_f1}[/b]", "[b]{p2:her_clf_rf_temporal_f1}[/b]",
            "[b]{p2:her_det050_f1}[/b]"],
           ["SVM (rbf, C = 10)", "{p2:her_clf_svm_aleatoria_f1}", "{p2:her_clf_svm_temporal_f1}", "—"]],
          [1.08, 0.62, 0.66, 1.14],
          nota="Aleatoria: 80/20, semilla 42. Temporal: entrena hasta el 30-abr-2016 y prueba en mayo; los retardos "
               "solo se usan en ella (en la aleatoria filtran). En negrita, el mejor de cada columna en cada bloque.")
    h2("B. Los retardos, y por qué los árboles no extrapolan")
    parrafo("Ningún barrido de hiperparámetros se acercó a lo que aportaron los retardos: en la partición temporal la "
            "lineal pasa de R² {p2:her_reg_lineal_temporal_r2} a {p2:her_bo_lineal_retardos_r2} (MAE "
            "{p2:her_bo_lineal_retardos_mae}, RMSE {p2:her_bo_lineal_retardos_rmse}). Con los mismos retardos, Random "
            "Forest se queda en {p2:her_bo_rf_retardos_r2}: predice en mayo un consumo sostenidamente alto, con un sesgo "
            "medio de +{p2:her_reg_rf_retardos_sesgo} frente a +{p2:her_reg_lineal_retardos_sesgo} de la lineal. Un "
            "árbol solo puede promediar valores vistos en invierno; la lineal, dominada por el consumo de hace 10 min, "
            "predice el cambio respecto del nivel actual. Mayo es otra estación (la temperatura exterior media pasa de "
            "{p2:her_deriva_ene_tout} en enero a {p2:her_deriva_may_tout}), pero la causa de fondo es un confusor de "
            "la temperatura [i]interior[/i]: en invierno las habitaciones más cálidas eran las de más consumo, porque "
            "parte de ese calor lo producen los propios aparatos, y en mayo la casa está por dentro más cálida que en "
            "casi todo el entrenamiento, así que un árbol lee ese calor como consumo. Reentrenado sin las temperaturas "
            "interiores, LightGBM pierde casi todo su sesgo de mayo; quitar el mes no lo arregla.")
    h2("C. El boosting no reemplaza a la lineal")
    parrafo("Con retardos, LightGBM iguala a la lineal en R² ({p2:her_bo_lgbm_retardos_r2} frente a "
            "{p2:her_bo_lineal_retardos_r2}) con más error absoluto ({p2:her_bo_lgbm_retardos_mae} frente a "
            "{p2:her_bo_lineal_retardos_mae}), y lo poco que aprende de más viene de los sensores interiores, que son "
            "justo los que traen el sesgo estacional. El gemelo tampoco es un oráculo: en MAE pierde frente a repetir "
            "la última lectura ({p2:n1b_g3a_total_mae} frente a {p2:n1b_persistencia_total_mae}), en RMSE gana "
            "({p2:n1b_g3a_total_rmse} frente a {p2:n1b_persistencia_total_rmse}) y en las lecturas sobre el umbral "
            "ambos subestiman (sesgo de {p2:n1b_g3a_altas_sesgo} frente a {p2:n1b_persistencia_altas_sesgo}). Su error "
            "tampoco es uniforme: MAE de {p2:n1b_g3a_madrugada_mae} de madrugada frente a {p2:n1b_g3a_manana_mae} en la "
            "mañana.")
    decision("La función de transición del gemelo es la regresión lineal con retardos. La temperatura interior entra "
             "al MDP como variable de confort, no como predictor del consumo; la incertidumbre del simulador es función "
             "de la hora, y el gemelo se valida contra un mes reservado antes de que un agente entrene sobre él. Como "
             "subestima los picos, queda una advertencia para el entorno continuo: un agente entrenado sobre un "
             "simulador que abarata los picos aprendería a explotar un ahorro que no existe.")

    # ---------------------------------------------------------------- IV
    h1("IV. Qué tipo de día es: aprendizaje no supervisado")
    parrafo("El estado del MDP necesita un contexto que el calendario no da: ¿hoy es un día de mucho consumo? Está en "
            "juego si el tipo de día entra al estado, con qué algoritmo se asigna en producción y con qué confianza.")
    h2("A. Dos tipos de día con K-Means")
    parrafo("Cada día se representa por sus 24 consumos medios horarios en Wh, sin estandarizar. Con K-Means "
            "[[lloyd]] las tres "
            "métricas coinciden en k = 2: el codo ({c2:km_caida_inercia} menos de inercia de k = 1 a k = 2), la "
            "silueta [[rousseeuw]] ({c2:km_silueta}, frente a {c2:km_silueta_k3} con k = 3) y el índice de Dunn "
            "[[dunn]] ({c2:km_dunn}, el máximo del barrido). Aparecen un [i]día normal[/i] ({c2:km_n_normal}, "
            "{c2:km_kwh_normal} en promedio) y un [i]día de carga alta[/i] ({c2:km_n_alta}, {c2:km_kwh_alta}) con un "
            "bloque diurno de consumo (Fig. 2). El calendario no los explica: la V de Cramér con el fin de semana es "
            "{c2:km_cramer_finde} y con el mes, {c2:km_cramer_mes} (p = {c2:km_p_mes}). El tipo tampoco se ve al "
            "amanecer: hasta las 8 h, asignar con la curva parcial acierta el {c2:km_obs_8h_acierto} de los días, menos "
            "que decir siempre «normal» ({c2:km_obs_8h}); con la curva hasta las 12 h se reconoce el {c2:km_obs_12h} de "
            "los días de carga alta, a tiempo para actuar sobre la joroba de la tarde. Mayo no trae tipos nuevos "
            "({c2:km_mayo_fuera_p95} días fuera del percentil 95 del entrenamiento), pero los días de carga alta bajan "
            "de {c2:km_alta_tr} a {c2:km_alta_te}.")
    figura(fa2, 3.0, "Los dos tipos de día que encuentra K-Means (k = 2) sobre los {t1:n_dias} días completos: media "
                     "por hora y banda entre los percentiles 10 y 90. La madrugada es igual en ambos; el día de carga "
                     "alta se separa con un bloque diurno que solo se hace visible hacia media mañana.")
    h2("B. ¿Real o artefacto? El agrupamiento jerárquico")
    parrafo("El agrupamiento jerárquico con enlace de Ward [[ward]] y con enlace completo elige también k = 2 y "
            "coincide con K-Means en {c2:ward_coinciden} días (ARI [[hubert]] {c2:ward_ari_kmeans}); los "
            "{c2:ward_cambian_kmeans|n} desacuerdos están todos entre el 20 % de días más cercanos a la frontera. El "
            "tipo de día es real, pero de frontera difusa. El enlace promedio logra la mejor silueta ({c2:avg_silueta}) y "
            "el mejor Dunn ({c2:avg_dunn}) aislando un solo día: por eso k nunca se elige solo por la métrica, sino con "
            "un tamaño mínimo de clúster del 5 %. La estabilidad decidió el papel de cada "
            "método: ajustado sin mayo, K-Means reproduce el mismo reparto (ARI {c2:estab_ari_kmeans}) y Ward no "
            "({c2:estab_ari_ward}).")
    h2("C. DBSCAN: lo que no encaja")
    parrafo("Con un solo radio, DBSCAN [[ester]] forma un único grupo y deja como ruido a los días de carga alta; "
            "separando por tipo, el radio del día de "
            "carga alta ({c2:db_eps_alta}) es {c2:db_ratio_eps} el del día normal ({c2:db_eps_normal}): un día de carga "
            "alta es más disperso. Los {c2:db_atipicos} atípicos robustos ({c2:db_atipicos_pct}; "
            "{c2:db_atipicos_enero|n} de ellos en enero) se marcan, no se borran, y en mayo {c2:db_mayo_desconocidos} "
            "días no tienen vecinos densos en la historia. Sobre lecturas, con un DBSCAN por franja, de madrugada el "
            "{c2:db_madrugada_bajo200} del ruido está bajo el umbral de {c2:db_umbral_wh}, mientras en la tarde DBSCAN "
            "solo marca el {c2:db_tarde_marca} de las lecturas que lo superan: ve rareza en contexto, no magnitud. "
            "Ninguna definición de anomalía es inmune a la estación: en mayo la fracción marcada por DBSCAN cambia "
            "{c2:db_mayo_caida} y la que supera el umbral fijo, {c2:umbral_mayo_caida}.")
    decision("El tipo de día entra al estado como estimación que se actualiza durante el día, con su margen al "
             "centroide como confianza; K-Means lo asigna en producción y Ward y el enlace completo lo auditan en cada "
             "reentrenamiento mensual. Un día «desconocido» pide una política conservadora, la incertidumbre del "
             "simulador depende del tipo de día además de la franja, y Guardian tendrá una segunda alarma por rareza "
             "(DBSCAN por franja, solo en subidas), pendiente de evaluar.")

    # ---------------------------------------------------------------- V
    h1("V. Cuándo avisar: Guardian")
    parrafo("Aplazar una carga solo es posible si Guardian avisa antes de que el pico empiece. Está en juego qué señal "
            "alimenta su semáforo y qué probabilidad de pico entra al estado del agente.")
    h2("A. Reconocer no es anticipar")
    parrafo("El detector de la primera etapa del curso (Random Forest con retardos, umbral 0,40) «detectaba» el "
            "{p2:ancla_det_detectados} de los picos, pero contaba alertas que tocaban picos ya en curso: sus avisos "
            "duraban {p2:her_det_duracion} de media; en {p2:n1c_antes_ya_encendida_n|n} de los "
            "{p2:n1c_antes_n|n} picos con alerta previa la alerta ya venía encendida, y el umbral se había elegido "
            "mirando la prueba. Con el mismo presupuesto de rojo que G0, ese detector anticipa solo el "
            "{p2:n1c_det_mismo_r_p20} de los picos con al menos dos lecturas (≥ 20 min) de antelación.")
    figura(F_G2, 2.85, "Picos de mayo avisados con antelación por G0 desplegado, frente a la regla de nivel y al azar "
                      "(línea discontinua) con el mismo rojo realizado ({p2:titular_rojo_pct} de la calma); barras: IC "
                      "del 95 % por bootstrap pareado por día. «≥ 20 min» equivale a al menos dos lecturas.")
    h2("B. Protocolo")
    parrafo("Un pico agrupa las lecturas sobre {p2:part_umbral_wh} separadas por menos de 30 min; la etiqueta marca "
            "las lecturas en calma tras las que empieza uno en los 30 min siguientes. Las señales se ajustan con el 85 % "
            "inicial del entrenamiento temporal, sus cortes se fijan en el 15 % final ({p2:def_picos_validacion}) y se "
            "reportan en mayo ({p2:def_picos_prueba}). Se seleccionan y comparan con un mismo [i]presupuesto[/i] de "
            "rojo, el {p2:def_tasa_base_r} de la calma (la tasa base de la etiqueta); el rojo que una señal desplegada "
            "[i]realiza[/i] se reporta aparte, sin mezclarlo. Los listones son la regla de nivel (solo el consumo "
            "actual) y el azar; gana el modelo más simple a menos de 10 puntos del mejor en validación.")
    h2("C. Para anticipar basta lo simple")
    parrafo("El modelo mínimo de dos variables, G0 (consumo actual y frecuencia histórica de picos por hora, en "
            "laborable o fin de semana: 48 celdas), gana la selección en validación ({p2:g0_val_p20}). En prueba y con "
            "el mismo presupuesto, ningún modelo de {p2:part_n_variables} variables se distingue de él: el mejor, una "
            "regresión logística que anticipa, suma +{p2:caso_otro_d} (IC de {p2:caso_otro_ic_inf|n} a "
            "{p2:caso_otro_ic_sup|n}). Desplegado con los cortes de validación, G0 realiza en mayo un rojo del "
            "{p2:titular_rojo_pct} de la calma ({p2:titular_min_dia}), y con ese rojo se reporta el titular (Fig. 3): "
            "avisa {p2:titular_n20|n} de los {p2:def_picos_prueba|n} picos ({p2:titular_p20}) con al menos dos lecturas "
            "(≥ 20 min) de antelación, con {p2:titular_avisos_dia} y un {p2:titular_falsos} de avisos falsos. La regla "
            "y el azar se miden con ese mismo rojo realizado: la regla avisa {p2:titular_m20|n} (ventaja de G0, "
            "+{p2:titular_d_regla}, IC de {p2:titular_d_regla_ic_inf|n} a {p2:titular_d_regla_ic_sup|n}: no "
            "concluyente) y el azar llegaría al {p2:azar_p20_desplegado}.")
    h2("D. Deriva, calibración y alcance")
    parrafo("Los bosques derivan más que lo simple: con los cortes de abril, en mayo el bosque que reconoce realiza un "
            "rojo del {p2:g1_desp_rojo_pct} de la calma y el que anticipa, del {p2:g4_desp_rojo_pct}, frente al "
            "{p2:g0_desp_rojo_pct} de G0; reentrenados sin las temperaturas de las habitaciones bajan a "
            "{p2:deriva_g1_sin_tint_rojo} y {p2:deriva_g4_sin_tint_rojo}, el mismo confusor de la Sec. III. La "
            "validación, además, es optimista: G0 anticipa el {p2:g0_val_p20} de los picos en validación y el "
            "{p2:g0_prueba_p20} en prueba con el mismo presupuesto, y en el decil más alto de su calibración precedieron "
            "un pico el {p2:cal_decil10_tasa_val} de los momentos en validación frente al {p2:cal_decil10_tasa_prueba} "
            "en prueba. Y lo que un aviso puede tocar es acotado: solo el {p2:energia_exceso_anticipado_pct} del exceso "
            "sobre el umbral en mayo ({p2:energia_exceso_anticipado_kwh} de {p2:energia_exceso_kwh}) cae en picos "
            "avisados con al menos dos lecturas de antelación.")
    decision("El anticipador de Guardian es G0: exportable, explicable con una regla de dos variables y capaz de correr "
             "en la página y en el hogar; la complejidad queda para el gemelo. Guardian se evalúa por antelación y con "
             "el mismo tiempo en rojo, nunca por «evento tocado», y la probabilidad de pico que entra al estado lleva su "
             "rango y se recalibra cada mes.")

    # ---------------------------------------------------------------- VI
    h1("VI. Qué decidir: aprendizaje por refuerzo")
    parrafo("Con transición, contexto y aviso, falta la pieza que decide. Están en juego cómo se contabiliza el costo "
            "de aplazar, quién fija la paciencia y qué agente propone en Shiro Twin. El proyecto la construyó por "
            "etapas del curso: un MDP resuelto con iteración de valor (π*), Q-learning con la recompensa original y, "
            "por último, una DQN con la recompensa centrada de la Sec. VI-E.")
    h2("A. El MDP de Shiro")
    parrafo("El paso es de una hora. El estado combina el tipo de día estimado (K-Means ajustado con los "
            "{t1:n_dias_tr} días de entrenamiento y asignado sobre la curva parcial), la franja, el nivel de consumo "
            "(bajo 60 Wh, medio o sobre el umbral) y si hay una carga pendiente: {t1:n_estados} estados. Las acciones "
            "son no actuar, aplazar (con nivel alto y cupo libre) y ejecutar lo pendiente; aplazar mueve el 40 % del "
            "exceso, Δ[i]E[/i] = {t1:DE}. La tarifa vale 1,0 en valle y 1,5 en punta; las transiciones se estiman por "
            "conteo hasta el 30 de abril y la acción las modifica de forma determinista, con γ = 0,95 [[sutton]]. Ese "
            "es el entorno de todos los agentes: una [i]réplica de días reales[/i] en la que el consumo sigue la serie "
            "observada y la acción solo mueve la carga; el entorno continuo con el gemelo lineal de la Sec. III sigue "
            "pendiente. En el código de ejemplo del curso [i]P[/i]([i]s[/i]′|[i]s[/i]) no dependía de la acción, de "
            "modo que π* era simplemente la política codiciosa; para Shiro la acción debe cambiar el futuro, y de ahí "
            "el estado «carga pendiente». La recompensa es")
    ecuacion("[i]r[/i] = −[i]c[/i]([i]t[/i])·[i]E[/i] − λ·[i]w[/i]", 1)
    parrafo("donde [i]c[/i] es la tarifa, [i]E[/i] la energía cobrada en el paso, [i]w[/i] vale 1 si en ese paso hay "
            "una carga esperando y λ mide cuánto le cuesta esperar a la persona.", sangria=False)
    h2("B. Contabilidad corregida")
    parrafo("Si la energía aplazada se cobra completa al ejecutarla, el descuento hace que aplazar un costo parezca "
            "ahorrarlo: con tarifa plana el agente aplaza y nunca ejecuta, y la carga espera "
            "{t1:cordura_ingenua_1p0_espera} en mayo. La contabilidad corregida cobra al aplazar la parte a precio de "
            "valle y al ejecutar solo el sobrecosto; con tarifa plana, el agente aplaza en "
            "{t1:cordura_corregida_1p0_nap} estados, como debe ser. Resuelto por iteración de valor, con una persona "
            "paciente (λ = 0,005) π* coincide con la política codiciosa y con una regla fija en los {t1:n_estados} "
            "estados: aplazar todo pico en punta y ejecutar de madrugada. En mayo ahorra el {t1:ahorro_opt_te} del "
            "costo con {t1:espera_opt_te} de espera, y no se distingue de no actuar: la diferencia es de {t1:boot_no_te}.")
    h2("C. λ es un control de la persona")
    parrafo("Con una persona exigente (λ = 0,02), π* se aparta de la política codiciosa en {t1:ex_n_difs} de los "
            "{t1:n_estados} estados: no "
            "aplaza en la mañana, porque el valle queda a {t1:horas_valle_x_0-1-2}; en la tarde de un día de carga alta "
            "guarda el cupo, porque otro pico antes del valle es más probable ({t1:p_otro_pico_1-2-2} frente a "
            "{t1:p_otro_pico_0-2-2} en un día normal), y rescata la carga pendiente. Cambia ahorro por espera: "
            "{t1:ex_ahorro_opt_te} con {t1:ex_espera_opt_te}. Las decisiones de la tarde se juegan por diferencias de "
            "milésimas de kWh-eq (Δ[i]Q[/i] = +{t1:ex_dQ_0-2-2-0} en un día normal frente a {t1:ex_dQ_1-2-2-0} en uno "
            "de carga alta), así que la consola las muestra como dudosas.")
    h2("D. Q-learning: ¿cuánta experiencia pide?")
    parrafo("En una casa real el agente de Shiro no conocerá [i]P[/i] y tendrá que aprender de la experiencia: ¿cuánta "
            "necesita? Las brechas entre acciones de π* son pequeñas (mediana {t2:brecha_med}, de {t2:brecha_min|n} a "
            "{t2:brecha_max}) frente al error de los Q con α fijo ({t2:prof_errq} con α = 0,1): con los "
            "hiperparámetros del código de ejemplo del curso y {t2:n_ep} días, Q-learning [[watkins]] captura solo el "
            "{t2:prof_captura} del ahorro de π*, y Shiro descarta el α fijo. Con α decreciente "
            "(1/[i]N[/i][p]0,6[/p] [[evendar]]) y {t2:n_ep_rec} días captura el {t2:base_captura} y en mayo no se "
            "distingue de π* —diferencia de {t2:boot_ql_pi}—, pero eso equivale a unos {t2:anos_rec}: con esta "
            "recompensa, arrancar en frío en una casa sería inviable. El agente miope aprende mejor que el paciente "
            "(γ = 0,5: {t2:g0p5_captura}; γ = 0,99: {t2:g0p99_captura}), así que el agente tabular usa horizonte "
            "corto. El estado del proyecto le ganó a terciles de consumo y a niveles de K-Means (π* ahorraría el "
            "{t2:p3vi_qcut_ahorro} y el {t2:p3vi_kmeans_ahorro}, frente al {t2:p3vi_umbral_ahorro}): el estado se "
            "ancla en lo que la acción puede mover. Las recompensas de +1 por acción (un agente «nervioso», "
            "{t2:p4_trans_aplaz|n} aplazamientos al día sin ahorro) y de −1000 por cualquier pérdida (uno «miedoso» "
            "que nunca aplaza) quedan prohibidas. Y como π* es la misma en invierno y en mayo "
            "({t2:p1_iguales_vi|n} de {t2:p1_decision_comunes|n} decisiones) mientras que aprender desde cero con los "
            "{t1:n_dias_te} días de mayo no ahorra nada, una política de invierno se transfiere a la primavera.")
    h2("E. Recompensa centrada y DQN")
    parrafo("El arranque en frío no era culpa de la tabla sino del ruido de la recompensa: el término "
            "−[i]c[/i]([i]t[/i])·[i]E[/i] de la casa no depende de la acción y domina la señal. La recompensa centrada "
            "lo quita y deja solo lo que la acción cambia:")
    ecuacion("[i]r̃[/i] = [i]r[/i] + [i]c[/i]([i]t[/i])·[i]E[/i][s]casa[/s]", 2)
    parrafo("donde [i]E[/i][s]casa[/s] es la energía que la casa consume en el paso sin contar la acción. Aplazar vale "
            "([i]c[/i] − 1)·Δ[i]E[/i] − λ; ejecutar, −([i]c[/i] − 1)·Δ[i]E[/i], y no actuar, −λ si hay carga pendiente. "
            "Como lo quitado no depende de la acción, π* no cambia. Con ella, el mismo Q-learning tabular captura al "
            "menos el 80 % del ahorro de π* desde el día {t3:qlc_dias80|n} en las {t3:n_semillas} semillas y termina "
            "en el {t3:qlc_captura}; con la recompensa original necesitaba {t3:ql_dias80}, y la DQN, {t3:dqn_dias80} "
            "(Tabla II, Fig. 4). "
            "La DQN [[mnih]] ({t3:n_rasgos} rasgos → 64 → 64 → 3 neuronas, con memoria de experiencias [[lin]] y red "
            "objetivo, {t3:n_ep_dqn} días) captura el {t3:dqn_captura}, y su semilla mediana decide igual que π* en "
            "todo mayo, con una diferencia de {t3:boot_dqn_pi}; Double DQN [[hasselt]] no mejora ({t3:ddqn_captura}; su peor semilla ahorra "
            "el {t3:ddqn_ahorro_min}). Los dos trucos son imprescindibles: sin memoria de experiencias la captura cae "
            "al {t3:sinr_captura} (la peor semilla ahorra el {t3:sinr_ahorro_min}); sin red objetivo, al "
            "{t3:sint_captura}, con los Q oscilando el doble; sin ninguno, al {t3:sina_captura}, con semillas que no "
            "ahorran ({t3:sina_ahorro_min}) y {t3:sina_espera} de espera.", sangria=False)
    parrafo("La red ve algo que la tabla no veía: la hora exacta. Con λ = 0,02 aplaza solo desde las "
            "{t3:e4_ex_desde}, la primera hora entera después del equilibrio teórico (un sobrecosto de "
            "{t3:sobrecosto_kwh} dividido por λ da {t3:e4_ex_umbral_h} antes del valle, es decir, las "
            "{t3:e4_ex_hora_teorica}). De madrugada nunca hubo picos, así que ahí la red extrapola y la consola lo "
            "marca.")
    decision("En Shiro Twin propone π*, exacta y explicable para cada λ, y Q-learning y DQN se muestran como "
             "verificación. La recompensa centrada es obligatoria en todo agente de Shiro: en el entorno de réplica baja "
             "la experiencia necesaria de {t3:ql_dias80} a {t3:qlc_dias80}, lo que hace plausible, aunque aún sin medir "
             "en una casa real, un arranque en frío de meses para Shiro Home. La red se justifica por el estado que "
             "viene (hora exacta, probabilidad de G0, clima), no por los {t1:n_estados} estados actuales, donde basta "
             "la tabla.")
    tabla("Agentes de refuerzo en mayo (persona paciente, media de {t3:n_semillas} semillas)",
          ["Agente", "Ahorro (%)", "De π* (%)", "Espera (h/día)", "Días hasta 80 %"],
          [["π* (iteración de valor)", "{t3:vi_ahorro_te|n}", "ref.", "{t3:vi_espera_te|n}", "n. a."],
           ["Q-learning (original)", "{t3:ql_ahorro|n}", "{t3:ql_captura|n}", "{t3:ql_espera|n}",
            "{t3:ql_dias80|n}"],
           ["[b]Q-learning (centrada)[/b]", "[b]{t3:qlc_ahorro|n}[/b]", "[b]{t3:qlc_captura|n}[/b]",
            "[b]{t3:qlc_espera|n}[/b]", "[b]{t3:qlc_dias80|n}[/b]"],
           ["DQN", "{t3:dqn_ahorro|n}", "{t3:dqn_captura|n}", "{t3:dqn_espera|n}", "{t3:dqn_dias80|n}"],
           ["Double DQN", "{t3:ddqn_ahorro|n}", "{t3:ddqn_captura|n}", "{t3:ddqn_espera|n}", "{t3:ddqn_dias80}"]],
          [1.26, 0.5, 0.5, 0.5, 0.74],
          nota="Entorno de réplica de días reales; ahorro frente a no actuar. Q-learning (original): α decreciente y "
               "recompensa de la ec. (1); (centrada): ec. (2). «Días hasta 80 %»: desde cuándo todas las semillas "
               "capturan al menos el 80 % del ahorro de π* (que resuelve el modelo: n. a.). En negrita, el único agente "
               "que iguala a π* y el que menos experiencia necesita.")
    figura_ancha(F_T4, "Arranque en frío en el entorno de réplica: porcentaje del ahorro de π* que logra en mayo cada "
                       "agente según los días de experiencia simulada (media y rango de {t3:n_semillas} semillas; eje "
                       "logarítmico). En la leyenda, «Q-learning (Taller 2)» es el Q-learning con la recompensa original "
                       "y «π* (Taller 1)», la política óptima por iteración de valor.")

    # ---------------------------------------------------------------- VII
    h1("VII. Prototipo: la consola de Shiro")
    hay_consola = F_CONSOLA.exists()
    parrafo("Faltaba un criterio de cierre: ver el entorno funcionando de principio a fin. La consola de Shiro es una "
            "página HTML autocontenida, sin red ni librerías, con los datos de mayo incrustados; una sola elección de "
            "contexto (día y hora) alimenta cinco pantallas y todo se calcula en el navegador"
            + (" (Fig. 5):" if hay_consola else ":"))
    lista(["[i]Hoy en casa[/i] (supervisado): curva del día, predicción lineal a un paso y semáforo de G0, con un "
           "«¿y si…?» de luces y temperatura exterior.",
           "[i]¿Qué tipo de día es?[/i] (no supervisado): K-Means sobre la curva parcial, con su margen y la bandera "
           "de DBSCAN.",
           "[i]¿Qué haría Shiro?[/i] (refuerzo): π* recalculada con el λ y la tarifa que elija la persona, junto a "
           "Q-learning y la DQN ejecutada en la página; marca decisiones dudosas y fuera de los datos.",
           "[i]Pregúntale a Shiro[/i]: respuestas por plantilla que citan cifras reales, sin modelo de lenguaje.",
           "[i]Ficha del modelo[/i]: las dos particiones, tipos de día, G0, agentes con sus intervalos y límites."])
    parrafo("Las cifras de la consola y del artículo salen de una única fuente, y antes de publicar un verificador "
            "comprueba que la iteración de valor en JavaScript reproduce la de Python en {p3:n_rejilla_vi} "
            "combinaciones de λ y tarifa, y que la red y K-Means coinciden.")
    if hay_consola:
        from PIL import Image
        w, h = Image.open(F_CONSOLA).size
        # si la captura es una de las pantallas guardadas por la consola, el pie dice cuál
        pantallas = {"consola_hoy.png": "Hoy en casa", "consola_tipo.png": "¿Qué tipo de día es?",
                     "consola_shiro.png": "¿Qué haría Shiro?", "consola_pregunta.png": "Pregúntale a Shiro",
                     "consola_ficha.png": "Ficha del modelo"}
        cual = next((v for k, v in pantallas.items()
                     if (FIG / k).exists() and (FIG / k).read_bytes() == F_CONSOLA.read_bytes()), None)
        pie5 = ("La consola de Shiro" + (f", pantalla «{cual}»" if cual else "") +
                ": una sola elección de día y hora alimenta las cinco pantallas.")
        if w / h > 2.2:
            figura_ancha(F_CONSOLA, pie5)
        else:
            figura(F_CONSOLA, 2.7, pie5)
    else:
        print("ADVERTENCIA: falta figuras/consola_captura.png; la Fig. 5 se omite. Vuelve a correr este generador "
              "cuando exista la captura.")

    # ---------------------------------------------------------------- VIII
    h1("VIII. Discusión, ética y límites")
    parrafo("[i]El ahorro es pequeño y simulado.[/i] Con esta casa y esta tarifa, aplazar ahorra el "
            "{t1:ahorro_opt_te} del costo de mayo y no se distingue de no hacer nada. La causa medida no es el "
            "algoritmo sino que aplazar por tarifa mueve poco: con la contabilidad corregida, cada aplazamiento solo "
            "gana la diferencia entre punta y valle sobre Δ[i]E[/i], menos la espera. Que apenas el "
            "{p2:energia_exceso_anticipado_pct} del exceso ocurra en picos que Guardian avisa con al menos dos lecturas de antelación refuerza que un "
            "ahorro mayor exigiría saber qué aparato se enciende. Y ese ahorro se midió en la réplica de días reales: "
            "en el entorno continuo valdrá la advertencia de la Sec. III.")
    parrafo("[i]Una sola vivienda y sin verano.[/i] Todo sale de una casa de bajo consumo en Bélgica, en invierno y "
            "primavera, y la definición misma de anomalía envejece: el percentil 90 mensual cae de "
            "{p2:her_deriva_ene_p90} en enero a {p2:her_deriva_may_p90} en mayo. Por eso el umbral, los cortes y los "
            "tipos de día se recalibran cada mes y el sistema declara baja confianza mientras tanto; medir la caída al "
            "cambiar de vivienda (UCI n.º 235) sigue pendiente.")
    parrafo("[i]Falta saber qué aparato se enciende.[/i] Ningún sensor ambiental distingue «horno y secadora a la vez» "
            "de un pico cualquiera: ese es el techo real, no los hiperparámetros.")
    parrafo("[i]La persona decide.[/i] Shiro Twin solo propone: la persona aprueba o rechaza cada aplazamiento, fija λ "
            "y ve cuánto tiempo pasa el sistema en alerta. Los errores no cuestan lo mismo: un pico no avisado es "
            "recuperable, pero con un {p2:titular_falsos} de avisos falsos el riesgo real es que la persona deje de "
            "mirar. La explicación usa variables que la persona entiende (hora, consumo actual, luces), nunca la "
            "temperatura de una habitación: los nueve sensores están correlacionados y su orden de importancia no "
            "significa nada.")

    # ---------------------------------------------------------------- IX
    h1("IX. Conclusiones")
    parrafo("El semestre respondió qué necesita saber el gemelo de un solo hogar para proponer con honestidad. Quedan "
            "listos para Shiro Home una función de transición que generaliza a un mes no visto (lineal con retardos, R² "
            "{p2:her_bo_lineal_retardos_r2} en la partición temporal), un contexto con confianza (dos tipos de día que "
            "K-Means asigna y el agrupamiento jerárquico audita), un anticipador simple y exportable (G0, "
            "{p2:titular_p20} de los picos con al menos dos lecturas de antelación) y un agente explicable con una "
            "recompensa centrada con la que, en el entorno de réplica, Q-learning supera el 80 % del ahorro de π* desde "
            "el día {t3:qlc_dias80|n} de experiencia simulada. No quedan listos el entorno continuo sobre el gemelo, la "
            "evidencia de un ahorro que se distinga de no actuar, los datos por aparato, una segunda vivienda y el "
            "verano. La lección de método es la del comienzo "
            "el semestre: la partición temporal decide, y cada número de la aleatoria necesita su par temporal para no "
            "prometer lo que el gemelo no puede cumplir.")

    # ---------------------------------------------------------------- agradecimientos y referencias
    p = _formato(doc.add_paragraph(), alin=WD_ALIGN_PARAGRAPH.CENTER, antes=7, despues=3, juntar=True)
    escribir(p, "Agradecimientos", smallcaps=True)
    parrafo("Los autores agradecen al profesor Hernán Darío Cruz Bueno, docente de Aprendizaje de Máquina (26-2) en "
            "la Universidad Sergio Arboleda, su orientación.")
    p = _formato(doc.add_paragraph(), alin=WD_ALIGN_PARAGRAPH.CENTER, antes=7, despues=3, juntar=True)
    escribir(p, "Referencias", smallcaps=True)
    for k, clave in enumerate(ORDEN_CITAS, 1):
        p = _formato(doc.add_paragraph(), izq=0.3, sangria=-0.3, despues=0)
        p.paragraph_format.tab_stops.add_tab_stop(Inches(0.3))
        escribir(p, f"[{k}]\t" + re.sub(r'"([^"]*)"', "“\\1”", REFS[clave]), size=8)
    sobran = sorted(set(REFS) - set(ORDEN_CITAS))
    if sobran:
        raise RuntimeError(f"Referencias sin citar: {sobran}")
    # salto final continuo: Word equilibra las dos columnas de la última página
    nueva_seccion(1)


# =====================================================================================================================
# Autocomprobación
# =====================================================================================================================
def comprobar():
    errores = []
    d = Document(DOCX)
    bloques = [p.text for p in d.paragraphs] + [c.text for t in d.tables for f in t.rows for c in f.cells]
    todo = "\n".join(bloques)
    for patron in (r"\{[^}]*\}", r"\bnan\b", r"\bNaN\b", r"\bTODO\b", r"\bNone\b", r"\[/?[bisp]\]", r"\[\[", r"⟨"):
        for x in set(re.findall(patron, todo)):
            errores.append(f"residuo «{x}»")
    import pymupdf
    doc_pdf = pymupdf.open(PDF)
    n = len(doc_pdf)
    texto_pdf = "".join(pg.get_text() for pg in doc_pdf)
    print(f"PDF: {n} páginas · {len(texto_pdf.split())} palabras · {len(comun.USADAS)} cifras citadas · "
          f"{len(ORDEN_CITAS)} referencias · {N_FIG[0]} figuras · {N_TAB[0]} tablas")
    if not 5 <= n <= 7:
        errores.append(f"el PDF tiene {n} páginas (se esperaban 5–7)")
    for e in errores:
        print("  ✗", e)
    return errores


if __name__ == "__main__":
    construir()
    doc.save(DOCX)
    print(f"DOCX: {DOCX}")
    import os
    import shutil
    import tempfile
    tmp = Path(tempfile.gettempdir()) / f"articulo_shiro_{os.getpid()}.pdf"
    comun.exportar_pdf(DOCX, tmp)
    shutil.copyfile(tmp, PDF)
    tmp.unlink()
    print(f"PDF:  {PDF}")
    sys.exit(1 if comprobar() else 0)
