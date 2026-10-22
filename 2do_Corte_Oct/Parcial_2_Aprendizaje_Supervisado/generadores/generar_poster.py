# -*- coding: utf-8 -*-
"""Genera el póster académico del Parcial 2 (Parte 4): Shiro Guardian.

Uso (desde cualquier carpeta):
    C:\\Users\\pipel\\venvs\\ml\\Scripts\\python.exe generadores\\generar_poster.py [--sin-pdf] [--forzar]
    --sin-pdf  solo el .pptx (no abre PowerPoint); --forzar  emite aunque la maqueta no quepa (para mirarla)

Nota: G1, G2, G3 y G5 entran en sus versiones de póster (figuras/POSTER_G*.png), que el cuaderno dibuja
al tamaño físico de la caja de figura (ancho de columna menos el relleno, ~170 mm) con etiquetas de 18 pt
y cifras clave de 22 pt; aquí se comprueba que ese ancho coincide y se colocan a escala 1:1. Las capturas
del mockup (MG2, MG3_informe) siguen entrando como recortes por fracciones fijas (P4_*); si cambian,
revisar REC_MG2 y REC_MG3.

Salidas (en la carpeta del parcial):
    Poster_Shiro_Guardian.pptx  una sola diapositiva A1 vertical (594 x 841 mm), editable
    Poster_Shiro_Guardian.pdf   exportado por PowerPoint (COM vía PowerShell, con candado)
    Poster_Shiro_Guardian.png   vista previa (~2.400 px de alto) renderizada del PDF con pymupdf

Reglas:
- Toda cifra sale de cifras.json (campo "texto"); aquí solo se teclean parámetros de definición
  (200 Wh, 10 min, al menos dos lecturas), fechas del dataset y nombres.
- La maqueta se mide antes de dibujar: cada columna se apila con alturas calculadas con las
  métricas reales de Segoe UI (PIL). Si algo no cabe, el generador falla en vez de encimar.
- Las figuras auxiliares P4_* son recortes de capturas existentes (no se recalcula nada).
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageFont
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Mm, Pt

CARPETA = Path(__file__).resolve().parent.parent
FIG = CARPETA / "figuras"
CIFRAS = CARPETA / "cifras.json"
ESCUDO = CARPETA / "recursos" / "escudo_universidad_sergio_arboleda.png"
SALIDA = CARPETA / "Poster_Shiro_Guardian.pptx"
PDF = CARPETA / "Poster_Shiro_Guardian.pdf"
PNG = CARPETA / "Poster_Shiro_Guardian.png"
CANDADO = Path(r"C:\Users\pipel\AppData\Local\Temp\shiro_office.lock")

# ------------------------------------------------------------------------------------------
# Cifras
# ------------------------------------------------------------------------------------------
_DATOS = json.loads(CIFRAS.read_text(encoding="utf-8"))
_TODAS = {**_DATOS["heredadas"], **_DATOS["nuevas"]}
USADAS = set()


def T(clave):
    """Texto es-CO de una cifra, tal como lo exporta el cuaderno."""
    USADAS.add(clave)
    return _TODAS[clave]["texto"].replace(" %", " %")   # «100 %» no se parte entre líneas


def N(clave):
    """El texto sin la unidad (p. ej. '28 picos' -> '28')."""
    texto, unidad = T(clave), _TODAS[clave].get("unidad", "")
    if unidad and texto.endswith(" " + unidad):
        return texto[: -len(unidad) - 1]
    return texto


def SIN_SIGNO(clave):
    """Para frases del tipo 'se queda corto en X': quita el signo del texto exportado."""
    return T(clave).lstrip("-−")


def MENOS(texto):
    """Signo menos tipográfico (no deja que la línea se corte entre el signo y el número)."""
    return texto.replace("-", "−")


def FECHA(clave):
    """Solo la fecha de un texto 'd-mmm-aaaa hh:mm'."""
    return T(clave).split(" ")[0]


# ------------------------------------------------------------------------------------------
# Estilo
# ------------------------------------------------------------------------------------------
ANCHO, ALTO = 594.0, 841.0  # mm
MARGEN, CANAL = 14.0, 8.0
NCOL = 3
COLW = (ANCHO - 2 * MARGEN - (NCOL - 1) * CANAL) / NCOL
PAD = 6.5  # relleno interno de las tarjetas

FUENTE = "Segoe UI"
FUENTE_SB = "Segoe UI Semibold"
TTF = {
    (FUENTE, False): r"C:\Windows\Fonts\segoeui.ttf",
    (FUENTE, True): r"C:\Windows\Fonts\segoeuib.ttf",
    (FUENTE_SB, False): r"C:\Windows\Fonts\seguisb.ttf",
    (FUENTE_SB, True): r"C:\Windows\Fonts\seguisb.ttf",
}

C_FONDO = RGBColor(0xF3, 0xF4, 0xF1)
C_TARJETA = RGBColor(0xFF, 0xFF, 0xFF)
C_BORDE = RGBColor(0xDA, 0xDD, 0xE2)
C_TEXTO = RGBColor(0x1F, 0x23, 0x28)
C_SUAVE = RGBColor(0x55, 0x5D, 0x69)
C_TITULO = RGBColor(0x0B, 0x2E, 0x59)  # azul del escudo
C_VERDE = RGBColor(0x18, 0x80, 0x38)
C_AMBAR = RGBColor(0xE8, 0x71, 0x0A)
C_ROJO = RGBColor(0xD9, 0x30, 0x25)
C_RESALTE = RGBColor(0xEE, 0xF3, 0xF9)

LS = 1.17  # interlineado (múltiplo del tamaño)
PT_MM = 25.4 / 72.0

_CACHE = {}


def _fuente(nombre, negrita):
    clave = (nombre, negrita)
    if clave not in _CACHE:
        _CACHE[clave] = ImageFont.truetype(TTF[clave], 200)
    return _CACHE[clave]


def ancho_mm(texto, tam, nombre=FUENTE, negrita=False):
    return _fuente(nombre, negrita).getlength(texto) * tam / 200.0 * PT_MM


# ------------------------------------------------------------------------------------------
# Texto enriquecido: un párrafo es una lista de tramos (texto, negrita, color)
# ------------------------------------------------------------------------------------------
def tramos(*partes):
    """Admite str (normal) o tuplas (texto, 'b') / (texto, 'b', color) / (texto, '', color)."""
    salida = []
    for p in partes:
        if isinstance(p, str):
            salida.append((p, False, None))
        else:
            salida.append((p[0], "b" in p[1], p[2] if len(p) > 2 else None))
    return salida


def envolver(parrafo, tam, ancho, nombre=FUENTE):
    """Cuenta líneas como lo haría PowerPoint (corte por palabras, con un 2 % de holgura)."""
    util = ancho * 0.98
    palabras = []
    for texto, negrita, _ in parrafo:
        for trozo in re.split(r"([ \t\n]+)", texto):  # el espacio duro (U+00A0) no corta
            if trozo:
                palabras.append((trozo, negrita))
    lineas, actual = 1, 0.0
    for trozo, negrita in palabras:
        w = ancho_mm(trozo, tam, nombre, negrita)
        if trozo.strip(" \t\n") == "":
            actual += w
            continue
        if actual + w > util and actual > 0:
            lineas += 1
            actual = w
        else:
            actual += w
    return lineas


def alto_parrafos(parrafos, tam, ancho, nombre=FUENTE, espacio=0.35):
    lineas = sum(envolver(p, tam, ancho, nombre) for p in parrafos)
    return lineas * tam * LS * PT_MM + (len(parrafos) - 1) * espacio * tam * PT_MM


# ------------------------------------------------------------------------------------------
# Operaciones de dibujo (se calculan primero y se emiten después)
# ------------------------------------------------------------------------------------------
OPS = []
DESBORDES = []


def op_texto(x, y, w, parrafos, tam, color=C_TEXTO, nombre=FUENTE, alinear=PP_ALIGN.LEFT,
             espacio=0.35):
    h = alto_parrafos(parrafos, tam, w, nombre, espacio)
    OPS.append(dict(t="texto", x=x, y=y, w=w, h=h, parrafos=parrafos, tam=tam, color=color,
                    nombre=nombre, alinear=alinear, espacio=espacio))
    return h


def op_rect(x, y, w, h, relleno, borde=None, redondo=False, grosor=0.6):
    OPS.append(dict(t="rect", x=x, y=y, w=w, h=h, relleno=relleno, borde=borde,
                    redondo=redondo, grosor=grosor))
    return OPS[-1]


def op_imagen(ruta, x, y, w=None, h=None):
    with Image.open(ruta) as im:
        ancho_px, alto_px = im.size
    if w is not None and h is None:
        h = w * alto_px / ancho_px
    elif h is not None and w is None:
        w = h * ancho_px / alto_px
    OPS.append(dict(t="imagen", ruta=str(ruta), x=x, y=y, w=w, h=h))
    return w, h


# ------------------------------------------------------------------------------------------
# Figuras: versiones de póster del cuaderno (1:1) y recortes de las capturas del mockup
# ------------------------------------------------------------------------------------------
def recortar(origen, destino, fx0, fy0, fx1, fy1):
    with Image.open(FIG / origen) as im:
        w, h = im.size
        caja = (round(fx0 * w), round(fy0 * h), round(fx1 * w), round(fy1 * h))
        im.crop(caja).save(FIG / destino, dpi=(300, 300))
    return FIG / destino


# Tarjeta 2 del mockup: indicadores + tira del semáforo del día de ejemplo.
REC_MG3 = recortar("MG3_informe.png", "P4_MG3_recorte.png", 0.030, 0.236, 0.970, 0.622)
# Tarjeta 1 del mockup: color, porqué y propuesta aprobable.
REC_MG2 = recortar("MG2.png", "P4_MG2_recorte.png", 0.474, 0.108, 0.962, 0.684)


def figura_poster(nombre):
    """Versión de póster dibujada por el cuaderno al ancho de la caja: se coloca sin escalar (18 pt = 18 pt)."""
    ruta = FIG / f"POSTER_{nombre}.png"
    with Image.open(ruta) as im:
        ancho_mm = im.size[0] / im.info["dpi"][0] * 25.4
    if abs(ancho_mm - (COLW - 2 * PAD)) > 0.3:
        DESBORDES.append(f"{ruta.name} mide {ancho_mm:.1f} mm de ancho y la caja {COLW - 2 * PAD:.1f} mm: "
                         "las etiquetas no quedarían a 18 pt")
    return ruta


# G1: el día de ejemplo con la tira del semáforo, sin leyenda (los colores se explican en el texto de la sección 1).
REC_G1 = figura_poster("G1")
# G2: picos avisados con ≥ 10, ≥ 20 y ≥ 30 min frente a la regla de nivel y el azar.
REC_G2 = figura_poster("G2")
# G3: solo el acierto de cada color (el tiempo en rojo va en las fichas y en el riesgo 2).
REC_G3 = figura_poster("G3")
# G5: consumo + franja del semáforo de cada caso con su anotación; sin el panel del puntaje interno.
REC_G5 = figura_poster("G5")


# ------------------------------------------------------------------------------------------
# Secciones de columna
# ------------------------------------------------------------------------------------------
TAM_CUERPO = 24
TAM_SECCION = 40
TAM_TITULO = 76
HUECO_MAX = 7.0  # holgura máxima que se reparte en cada hueco al equilibrar las columnas


class Columna:
    def __init__(self, i, y0, y1):
        self.x = MARGEN + i * (COLW + CANAL)
        self.y = y0
        self.y1 = y1
        self.ix = self.x + PAD
        self.iw = COLW - 2 * PAD
        self.i0 = len(OPS)
        self.marcas = []     # índices de OPS donde empieza un bloque que no es el primero
        self.tarjetas = []   # (op de la tarjeta, índice inicial, índice final)
        self.primero = True

    def _bloque(self):
        if not self.primero:
            self.marcas.append(len(OPS))
        self.primero = False

    def seccion(self, numero, titulo):
        if self.y > self.y1 - 20:
            DESBORDES.append(f"Sin espacio para la sección {numero}")
        if self.tarjetas:
            self.marcas.append(len(OPS))
        self.ini_tarjeta = len(OPS)
        self.tarjeta = op_rect(self.x, self.y, COLW, 10, C_TARJETA, C_BORDE, redondo=True)
        self.y0_tarjeta = self.y
        self.y += PAD - 1.5
        h = op_texto(self.ix, self.y, self.iw, [tramos((f"{numero} · {titulo}", "b"))],
                     TAM_SECCION, C_TITULO, FUENTE_SB)
        self.y += h + 1.0
        op_rect(self.ix, self.y, 34, 1.6, C_TITULO)
        self.y += 5.5
        self.primero = True

    def texto(self, parrafos, tam=TAM_CUERPO, color=C_TEXTO, despues=4.0, nombre=FUENTE):
        self._bloque()
        h = op_texto(self.ix, self.y, self.iw, parrafos, tam, color, nombre)
        self.y += h + despues

    def imagen(self, ruta, ancho=None, despues=4.0):
        self._bloque()
        w = ancho or self.iw
        x = self.ix + (self.iw - w) / 2
        _, h = op_imagen(ruta, x, self.y, w=w)
        self.y += h + despues

    def imagen_y_texto(self, ruta, ancho, parrafos, despues=4.0):
        """Imagen a la izquierda y texto a la derecha, centrado en vertical."""
        self._bloque()
        _, h = op_imagen(ruta, self.ix, self.y, w=ancho)
        wt = self.iw - ancho - 5
        ht = alto_parrafos(parrafos, TAM_CUERPO, wt)
        op_texto(self.ix + ancho + 5, self.y + max(0.0, (h - ht) / 2), wt, parrafos, TAM_CUERPO)
        self.y += max(h, ht) + despues

    def shiro(self, texto):
        """Recuadro 'qué cambia en Shiro'."""
        self._bloque()
        par = [tramos(("→ En Shiro: ", "b", C_TITULO), texto)]
        h = alto_parrafos(par, TAM_CUERPO, self.iw - 8)
        op_rect(self.ix, self.y, self.iw, h + 7, C_RESALTE, None, redondo=True)
        op_rect(self.ix, self.y, 1.8, h + 7, C_TITULO)
        op_texto(self.ix + 5, self.y + 3.5, self.iw - 8, par, TAM_CUERPO)
        self.y += h + 7 + 4.0

    def ficha_ancha(self, num, etq, col, tam_num=44, despues=3.0):
        """Cifra titular a todo el ancho: número grande y etiqueta debajo."""
        self._bloque()
        w = self.iw
        hn = tam_num * LS * PT_MM
        he = alto_parrafos([etq], 24, w - 9)
        alto = 2.5 + hn + he + 3.5
        op_rect(self.ix, self.y, w, alto, RGBColor(0xF5, 0xF6, 0xF8), None, redondo=True)
        op_rect(self.ix, self.y, 2.2, alto, col)
        op_texto(self.ix + 6, self.y + 2.0, w - 9, [tramos((num, "b"))], tam_num, C_TEXTO, FUENTE_SB)
        op_texto(self.ix + 6, self.y + 2.5 + hn, w - 9, [etq], 24, C_SUAVE)
        self.y += alto + despues

    def fichas(self, lista, tam_num=36, despues=4.0):
        """Cifras en una fila de n tarjetas: (número, etiqueta, color del filete)."""
        self._bloque()
        n = len(lista)
        fw = (self.iw - 3 * (n - 1)) / n
        lineas = max(envolver(tramos(etq), 24, fw - 7) for _, etq, _ in lista)
        alto = 2.5 + tam_num * LS * PT_MM + lineas * 24 * LS * PT_MM + 3.0
        for i, (num, etq, col) in enumerate(lista):
            x = self.ix + i * (fw + 3)
            op_rect(x, self.y, fw, alto, RGBColor(0xF5, 0xF6, 0xF8), None, redondo=True)
            op_rect(x, self.y, 2.0, alto, col)
            op_texto(x + 5, self.y + 2.0, fw - 7, [tramos((num, "b"))], tam_num, C_TEXTO, FUENTE_SB)
            op_texto(x + 5, self.y + 2.5 + tam_num * LS * PT_MM, fw - 7, [tramos(etq)], 24, C_SUAVE)
            if envolver(tramos((num, "b")), tam_num, fw - 7, FUENTE_SB) > 1:
                DESBORDES.append(f"Cifra de ficha demasiado larga: {num}")
        self.y += alto + despues

    def metricas(self, filas, cab, tam=24, despues=3.0):
        """Filas (etiqueta, Guardian, base, cuál gana: 1 o 2). Solo el mejor de cada fila en negrita."""
        self._bloque()
        w0, w1 = self.iw * 0.50, self.iw * 0.25
        ws = [w0, w1, self.iw - w0 - w1]
        xs = [self.ix, self.ix + w0, self.ix + w0 + w1]
        hl = tam * LS * PT_MM
        op_rect(self.ix, self.y, self.iw, hl + 3, RGBColor(0xEE, 0xF1, 0xF5))
        for j, t in enumerate(cab):
            op_texto(xs[j] + 1.5, self.y + 1.5, ws[j] - 2, [tramos((t, "b", C_TITULO))], tam)
        self.y += hl + 3 + 1.5
        for *fila, mejor in filas:
            for j, t in enumerate(fila):
                if envolver(tramos(t), tam, ws[j] - 2) > 1:
                    DESBORDES.append(f"Celda en dos líneas: {t}")
                op_texto(xs[j] + 1.5, self.y, ws[j] - 2, [tramos((t, "b" if j == mejor else ""))], tam)
            self.y += hl + 1.5
            op_rect(self.ix, self.y, self.iw, 0.35, C_BORDE)
            self.y += 1.5
        self.y += despues

    def linea_tiempo(self, filas, despues=0.0):
        """Línea de tiempo nativa: (etiqueta en negrita, texto, destacada)."""
        self._bloque()
        xl = self.ix + 3.0
        xt = self.ix + 10.0
        wt = self.iw - 10.0
        y0 = self.y
        centros = []
        for k, (etq, texto, destacada) in enumerate(filas):
            par = [tramos((etq + ": ", "b", C_TITULO), *texto)]
            h = alto_parrafos(par, TAM_CUERPO, wt - (4 if destacada else 0))
            if destacada:
                op_rect(xt - 3, self.y - 2.0, wt + 3, h + 4.5, C_RESALTE, None, redondo=True)
                op_texto(xt, self.y, wt - 4, par, TAM_CUERPO)
            else:
                op_texto(xt, self.y, wt, par, TAM_CUERPO)
            centros.append((self.y + TAM_CUERPO * LS * PT_MM / 2, destacada))
            self.y += h + (4.5 if k < len(filas) - 1 else 0)
        op_rect(xl - 0.5, centros[0][0], 1.0, centros[-1][0] - centros[0][0], C_BORDE)
        for yc, destacada in centros:
            r = 2.6 if destacada else 1.9
            op_rect(xl - r, yc - r, 2 * r, 2 * r, C_TITULO if destacada else RGBColor(0x9A, 0xA3, 0xB2),
                    None, redondo=True)
        self.y += despues

    def cerrar(self):
        self.y += PAD - 1.5
        self.tarjeta["h"] = self.y - self.y0_tarjeta
        self.tarjetas.append((self.tarjeta, self.ini_tarjeta, len(OPS)))
        self.y += CANAL
        if self.y - CANAL > self.y1 + 0.01:
            DESBORDES.append(f"Desborde de columna en x={self.x:.0f}: {self.y - CANAL:.1f} > {self.y1:.1f} mm")

    def equilibrar(self):
        """Reparte la holgura de la columna entre los huecos para que todas acaben a la misma altura."""
        holgura = self.y1 - (self.y - CANAL)
        if holgura <= 0 or not self.marcas:
            return holgura
        paso = min(HUECO_MAX, holgura / len(self.marcas))

        def desplazamiento(i):
            return paso * sum(1 for m in self.marcas if m <= i)

        tarjetas = {id(t) for t, _, _ in self.tarjetas}
        for i in range(self.i0, self.tarjetas[-1][2]):  # solo las operaciones de esta columna
            if id(OPS[i]) not in tarjetas:
                OPS[i]["y"] += desplazamiento(i)
        for t, a, b in self.tarjetas:
            d0, d1 = desplazamiento(a), desplazamiento(b - 1)
            t["y"] += d0
            t["h"] += d1 - d0
        return holgura - paso * len(self.marcas)


# ==========================================================================================
# 1. Encabezado
# ==========================================================================================
y = MARGEN
ESC_H = 56.0
w_esc, _ = op_imagen(ESCUDO, MARGEN, y + 4, h=ESC_H)
tx = MARGEN + w_esc + 12
tw = ANCHO - MARGEN - tx
ty = y
h = op_texto(tx, ty, tw, [tramos(("¿Cuánto antes se puede avisar de un pico de consumo?", "b"))],
             TAM_TITULO, C_TITULO, FUENTE_SB)
ty += h + 1
h = op_texto(tx, ty, tw, [tramos("Modelos supervisados para Shiro Guardian")], 46, C_TEXTO, FUENTE_SB)
ty += h + 3.5
h = op_texto(tx, ty, tw, [tramos("Jose Leonardo Diazgranados · Sofía Londoño · Andrés Felipe Céspedes Rondón · Alex Duran")],
             28, C_TEXTO)
ty += h + 1
h = op_texto(tx, ty, tw, [tramos("Universidad Sergio Arboleda · Aprendizaje de Máquina · Docente: Hernán Darío Cruz Bueno · "
                                 "2.º corte, 2026-2")],
             24, C_SUAVE)
ty += h
y = max(ty, y + 4 + ESC_H) + 6

# Filete tricolor (los tres colores del semáforo)
tercio = (ANCHO - 2 * MARGEN) / 3
for i, c in enumerate([C_VERDE, C_AMBAR, C_ROJO]):
    op_rect(MARGEN + i * tercio, y, tercio, 3.2, c)
y += 3.2 + 6

Y_COLUMNAS = y

# ==========================================================================================
# Pie y conclusión (se reservan abajo)
# ==========================================================================================
PIE_TAM = 24
pie = [tramos("Datos: Candanedo et al. (2017), Energy and Buildings, 140, 81–97")]
h_pie = alto_parrafos(pie, PIE_TAM, ANCHO - 2 * MARGEN)
Y_PIE = ALTO - MARGEN + 2 - h_pie
op_texto(MARGEN, Y_PIE, ANCHO - 2 * MARGEN, pie, PIE_TAM, C_SUAVE, alinear=PP_ALIGN.CENTER)

conclusiones = [
    ("Qué aprendimos",
     [tramos(f"Medir con margen cambió al ganador: con {N('def_picos_prueba')} picos, {T('sel_nvars')} variables "
             f"no se distinguen de {T('part_n_variables')}; el ",
             (T("ancla_det_detectados"), "b"), " del parcial 1 no anticipaba.")]),
    ("Qué mejoraríamos",
     [tramos("Saber qué aparato se enciende; más hogares, verano y picos.")]),
    ("Para producción",
     [tramos("Recalibrar cada mes; primer mes sin avisos; proceso local; decide la persona.")]),
]
alto_conc = max(alto_parrafos(p, TAM_CUERPO, COLW - 2 * PAD) + alto_parrafos([tramos((t, "b"))], 28, COLW - 2 * PAD)
                for t, p in conclusiones)
h_tit_conc = alto_parrafos([tramos(("7 · Conclusión y futuro", "b"))], TAM_SECCION, 300, FUENTE_SB)
H_CONC = PAD - 1.5 + h_tit_conc + 1 + 5.5 + alto_conc + 2.5 + PAD - 2
Y_CONC = Y_PIE - 6 - H_CONC
op_rect(MARGEN, Y_CONC, ANCHO - 2 * MARGEN, H_CONC, C_TARJETA, C_BORDE, redondo=True)
yc = Y_CONC + PAD - 1.5
op_texto(MARGEN + PAD, yc, 300, [tramos(("7 · Conclusión y futuro", "b"))], TAM_SECCION, C_TITULO, FUENTE_SB)
yc += h_tit_conc + 1
op_rect(MARGEN + PAD, yc, 34, 1.6, C_TITULO)
yc += 5.5
for i, (t, p) in enumerate(conclusiones):
    x = MARGEN + i * (COLW + CANAL) + PAD
    w = COLW - 2 * PAD
    hh = op_texto(x, yc, w, [tramos((t, "b"))], 28, C_TITULO, FUENTE_SB)
    op_texto(x, yc + hh + 2.5, w, p, TAM_CUERPO)
    if i:
        op_rect(x - PAD - CANAL / 2 - 0.2, yc, 0.4, alto_conc + 2, C_BORDE)

Y_FIN_COLUMNAS = Y_CONC - CANAL

col1 = Columna(0, Y_COLUMNAS, Y_FIN_COLUMNAS)

# ==========================================================================================
# Columna 1: problema, dataset, modelos
# ==========================================================================================
c = col1
c.seccion(1, "Problema y contexto")
c.texto([tramos("Guardian debe avisar ", ("antes", "b"),
                " de un pico (>\u00a0200\u00a0Wh en 10\u00a0min), con al menos dos lecturas (≥\u00a020\u00a0min) de margen, "
                "para que la persona aplace una carga. ", ("Verde", "b", C_VERDE),
                " sin aviso, ", ("amarillo", "b", C_AMBAR), " atento, ", ("rojo", "b", C_ROJO),
                " Shiro propone aplazar; ", ("rayado", "b", C_ROJO), " pico en curso.")])
c.imagen(REC_G1, despues=0)
c.cerrar()

c.seccion(2, "Dataset y características")
c.texto([tramos((T("datos_n_lecturas"), "b"), " cada 10 min · ", (T("datos_dias"), "b"), " · ",
                (T("datos_faltantes"), "b"), " faltantes. ", (T("part_n_variables"), "b"),
                f" variables: {T('part_n_exogenas')} del hogar (temperatura y humedad por cuarto, clima, "
                f"calendario, luces) + {T('part_n_retardos')} retardos (consumo de la última hora). "
                "Prueba: último mes.")])
c.texto([tramos(("Calidad: ", "b", C_TITULO),
                f"una vivienda belga, sin verano; {T('datos_appliances_multiplo10_pct')} en pasos de 10 Wh; "
                f"rv1/rv2 fuera; T6/RH_6 afuera; {T('datos_dias_incompletos')} días incompletos.")], despues=0)
c.cerrar()

c.seccion(3, "Modelos aplicados y evolución")
c.linea_tiempo([
    ("Taller 2 · árbol y KNN", ["la hora ordena el consumo."], False),
    ("Taller 3 · bosque", [f"R² {T('her_reg_rf_aleatoria_r2')} aleatoria y {MENOS(T('her_reg_rf_temporal_r2'))} temporal: "
                           "siempre ambas."], False),
    ("Parcial 1 · retardos", ["gemelo lineal; su detector reconocía picos ya empezados."], False),
    ("2.º corte · boosting", ["no extrapola a un mes más cálido."], False),
    ("Parcial 2 · Guardian", [f"avisar antes. De {T('sel_n_candidatos')} candidatos ({T('sel_nvars')} a "
                              f"{T('part_n_variables')} variables) gana el más simple que "
                              "pasa el mínimo de validación (fijado tras cálculos preliminares de la prueba): ",
                              ("modelo mínimo (G0) = consumo actual + frecuencia de picos a esa hora.", "b")], True),
])
c.cerrar()
col1_fin = c

# ------------------------------------------------------------------------------------------
col2 = Columna(1, Y_COLUMNAS, Y_FIN_COLUMNAS)
c = col2
c.seccion(4, "Modelo final y resultados")
c.ficha_ancha(f"{N('titular_n20')} de {N('def_picos_prueba')} picos",
              tramos(("avisados con al menos dos lecturas (≥\u00a020\u00a0min) de antelación: ", ""),
                     (T("titular_p20"), "b", C_TEXTO)), C_VERDE)
c.fichas([
    (N("titular_min_dia"), "min/día en rojo", C_ROJO),
    (N("titular_avisos_dia"), "avisos al día", C_AMBAR),
    (T("titular_falsos"), "avisos sin pico", C_ROJO),
], tam_num=36)
c.texto([tramos("Regla de nivel (avisar si el consumo ya es alto), mismo rojo: ",
                (f"{N('titular_m20')} de {N('def_picos_prueba')}", "b"),
                f" (+{T('titular_d_regla')}; rango plausible al 95 %: "
                f"{MENOS(N('titular_d_regla_ic_inf'))} a {N('titular_d_regla_ic_sup')} puntos: no concluyente)."),
         tramos(f"Azar: {T('azar_p20_desplegado')}.")])
c.metricas([
    ("Gemelo · MAE", T("n1b_g3a_total_mae"), T("n1b_persistencia_total_mae"), 2),
    ("Gemelo · RMSE", T("n1b_g3a_total_rmse"), T("n1b_persistencia_total_rmse"), 1),
    ("Semáforo · exactitud", T("lect_elegido_exactitud"), T("lect_todo_verde_exactitud"), 2),
    ("Semáforo · F1", T("lect_elegido_f1"), T("lect_todo_verde_f1"), 1),
], ("", "Guardian", "Base"), despues=2.0)
c.texto([tramos(("Gemelo", "b"), " (pronostica 10 min): pierde en MAE con repetir la última lectura; gana en "
                "RMSE (picos), y aun así queda ", (SIN_SIGNO("n1b_g3a_altas_sesgo"), "b"), " corto."),
         tramos(("Semáforo: ", "b"), "«todo verde» acierta más, pero no avisa ninguno.")])
c.imagen(REC_G2, despues=3)
c.imagen(REC_G3, despues=3)
c.shiro("la probabilidad del semáforo entra al estado del MDP; el gemelo solo simula.")
c.cerrar()

# ------------------------------------------------------------------------------------------
col3 = Columna(2, Y_COLUMNAS, Y_FIN_COLUMNAS)
c = col3
c.seccion(5, "Errores y reflexiones éticas")
c.imagen(REC_G5, despues=3)
c.texto([tramos((f"Caso 1 · {FECHA('caso1_inicio')}", "b"),
                f": de {T('caso1_wh_previo')} a {T('caso1_max_wh')}, {T('caso1_duracion_min')} de pico "
                "sin rojo previo."),
         tramos((f"Caso 2 · {FECHA('caso2_inicio')}", "b"),
                f": {T('caso2_duracion_min')} en rojo sin pico.")])
c.texto([tramos(("Riesgo 1 · falsas alarmas", "b", C_ROJO),
                f": actuando solo, Shiro habría aplazado cargas {T('caso2_duracion_min')} sin motivo (caso 2). "
                "→ Shiro solo propone."),
         tramos(("Riesgo 2 · deriva", "b", C_AMBAR),
                f": {T('fig3_min_dia_rojo')} en rojo frente a {T('fig3_presupuesto_min_dia')} previstos. "
                "→ Recalibrar cada mes.")], despues=0)
c.cerrar()

c.seccion(6, "Mockup de Guardian")
c.imagen(REC_MG3, despues=3)
c.imagen_y_texto(REC_MG2, 106, [tramos("Color, porqué y propuesta aprobable de un momento real.")], despues=0)
c.cerrar()

for nombre, col in (("1", col1), ("2", col2), ("3", col3)):
    resto = col.equilibrar()
    print(f"Columna {nombre}: holgura {col.y1 - (col.y - CANAL):.1f} mm; sin repartir {resto:.1f} mm")



# ==========================================================================================
# Emisión
# ==========================================================================================
def emitir():
    prs = Presentation()
    prs.slide_width = Mm(ANCHO)
    prs.slide_height = Mm(ALTO)
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fondo = diapo.background.fill
    fondo.solid()
    fondo.fore_color.rgb = C_FONDO
    for o in OPS:
        if o["t"] == "rect":
            forma = MSO_SHAPE.ROUNDED_RECTANGLE if o["redondo"] else MSO_SHAPE.RECTANGLE
            s = diapo.shapes.add_shape(forma, Mm(o["x"]), Mm(o["y"]), Mm(o["w"]), Mm(o["h"]))
            if o["redondo"]:
                s.adjustments[0] = min(0.5, 4.0 / max(1.0, min(o["w"], o["h"])))
            s.fill.solid()
            s.fill.fore_color.rgb = o["relleno"]
            if o["borde"] is None:
                s.line.fill.background()
            else:
                s.line.color.rgb = o["borde"]
                s.line.width = Pt(o["grosor"])
            s.shadow.inherit = False
            if s.has_text_frame:
                s.text_frame.text = ""
        elif o["t"] == "imagen":
            diapo.shapes.add_picture(o["ruta"], Mm(o["x"]), Mm(o["y"]), Mm(o["w"]), Mm(o["h"]))
        elif o["t"] == "texto":
            caja = diapo.shapes.add_textbox(Mm(o["x"]), Mm(o["y"]), Mm(o["w"]), Mm(o["h"] + 1))
            tf = caja.text_frame
            tf.word_wrap = True
            tf.auto_size = None
            tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
            tf.vertical_anchor = MSO_ANCHOR.TOP
            for k, par in enumerate(o["parrafos"]):
                p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
                p.alignment = o["alinear"]
                p.line_spacing = Pt(o["tam"] * LS)
                if k:
                    p.space_before = Pt(o["espacio"] * o["tam"])
                for texto, negrita, color in par:
                    r = p.add_run()
                    r.text = texto
                    f = r.font
                    f.name = o["nombre"]
                    f.size = Pt(o["tam"])
                    f.bold = negrita if o["nombre"] == FUENTE else False
                    f.color.rgb = color or o["color"]
    prs.core_properties.title = "¿Cuánto antes se puede avisar de un pico de consumo? Modelos supervisados para Shiro Guardian"
    prs.core_properties.author = "Jose Leonardo Diazgranados, Sofía Londoño, Andrés Felipe Céspedes Rondón, Alex Duran"
    prs.core_properties.subject = "Póster académico, Parcial 2 de Aprendizaje de Máquina"
    prs.save(SALIDA)
    return prs


def contar_palabras():
    palabras = 0
    for o in OPS:
        if o["t"] == "texto":
            for par in o["parrafos"]:
                texto = "".join(t for t, _, _ in par)
                palabras += len([w for w in re.split(r"\s+", texto) if re.search(r"\w", w)])
    return palabras


def a_pdf():
    espera = time.time()
    while True:
        try:
            fd = os.open(str(CANDADO), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, f"generar_poster.py pid {os.getpid()}".encode())
            os.close(fd)
            break
        except FileExistsError:
            if time.time() - espera > 20 * 60:
                raise SystemExit("El candado de Office sigue ocupado tras 20 min")
            print("Office ocupado por otra pieza; reintento en 15 s")
            time.sleep(15)
    try:
        if PDF.exists():
            PDF.unlink()
        ps = (
            "$ErrorActionPreference = 'Stop'\n"
            "$app = New-Object -ComObject PowerPoint.Application\n"
            "try {\n"
            f"  $p = $app.Presentations.Open('{SALIDA}', $true, $false, $false)\n"
            f"  $p.SaveAs('{PDF}', 32)\n"
            "  $p.Close()\n"
            "} finally { $app.Quit(); [System.Runtime.InteropServices.Marshal]::ReleaseComObject($app) | Out-Null }\n"
        )
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                           capture_output=True, text=True, timeout=600)
        if r.returncode != 0 or not PDF.exists():
            raise SystemExit("PowerPoint no exportó el PDF:\n" + r.stdout + r.stderr)
    finally:
        try:
            CANDADO.unlink()
        except FileNotFoundError:
            pass


def a_png():
    import pymupdf
    doc = pymupdf.open(PDF)
    pagina = doc[0]
    zoom = 2400 / pagina.rect.height
    pagina.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom)).save(PNG)
    doc.close()


if __name__ == "__main__":
    if DESBORDES and "--forzar" not in sys.argv:
        raise SystemExit(" | ".join(DESBORDES))
    emitir()
    n = contar_palabras()
    print(f"Palabras en el póster (sin contar las figuras): {n}")
    if n > 500:
        raise SystemExit("Más de 500 palabras")
    tams = sorted({o["tam"] for o in OPS if o["t"] == "texto"})
    print("Tamaños de letra usados (pt):", tams)
    print("Cifras usadas:", len(USADAS))
    if "--sin-pdf" not in sys.argv:
        a_pdf()
        a_png()
        print("PDF y PNG listos")
    print(SALIDA)
