# -*- coding: utf-8 -*-
"""Genera y ejecuta Parcial2_Guardian.ipynb (hito H1a del Parcial 2).

Uso (desde la carpeta del parcial):
    C:\\Users\\pipel\\venvs\\ml\\Scripts\\python.exe generadores\\construir_cuaderno.py

1. Construye el cuaderno con nbformat (celdas markdown + código).
2. Lo ejecuta con nbclient (kernel python3, cwd = carpeta del cuaderno, timeout 900 s por celda).
3. Lo guarda CON salidas. El cuaderno escribe cifras.json y mockup/datos_mockup.json.
4. Si ya existía un cifras.json, compara sus bloques "nuevas" y "heredadas" con los nuevos
   (sin "meta") e informa si la ejecución es determinista.
"""
import json
import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient

CARPETA = Path(__file__).resolve().parent.parent
CUADERNO = CARPETA / "Parcial2_Guardian.ipynb"
CIFRAS = CARPETA / "cifras.json"

CELDAS = []


def md(texto):
    CELDAS.append(nbformat.v4.new_markdown_cell(texto.strip("\n")))


def code(texto):
    CELDAS.append(nbformat.v4.new_code_cell(texto.strip("\n")))


# =====================================================================================
# 0. Portada
# =====================================================================================
md(r'''
# Shiro Guardian: ¿cuánto antes puede avisar de un pico de consumo, y con qué modelo?

**Parcial 2 — Aprendizaje Supervisado (2.º corte, 26-2) · Grupo Shiro** · Universidad Sergio Arboleda

## La necesidad de Shiro que abre este cuaderno
**Shiro Guardian** es la capa del gemelo digital que vigila el consumo del hogar y pinta un **semáforo de la próxima
media hora**. El medidor ya sabe cuándo un pico está en curso; lo único que Guardian puede añadir es **margen**: un
aviso que llegue *antes* del pico deja tiempo para la acción que aprenderá el agente del tercer corte, **aplazar una
carga grande**. Un aviso que llega con el pico ya empezado no deja hacer nada.

## La decisión de arquitectura que depende de la respuesta
1. **Qué probabilidad de pico entra al estado del MDP**, con qué modelo y con qué calibración.
2. **Si Guardian notifica** (propuesta en `ApprovalGate`, que la persona aprueba, ajusta o rechaza) **o solo colorea**.
3. **Si lo complejo se justifica**: un modelo mínimo de dos variables frente a modelos de todo el vector de retardos.

## Reglas del juego (fijadas antes de calcular)
- Solo partición **temporal**: el modelo se ajusta con datos hasta mediados de abril (*fit*), se elige y se calibra en
  el resto de abril (*validación*) y se juzga **una sola vez** en el mes que nunca vio (*prueba*); la sección 1 imprime
  las fechas y la extensión de cada tramo.
- Toda comparación entre señales se hace con el **mismo tiempo en rojo**; el criterio es el **% de picos avisados con
  al menos dos lecturas de antelación** (antelación nominal de 20 minutos o más).
- Ninguna cifra está escrita a mano: todas se imprimen desde el código y se guardan en `cifras.json`, la única fuente
  de cifras del informe, el póster, la presentación y el mockup.

## Mapa
1. Datos y particiones · 2. Anclas (el entorno reproduce lo publicado) · 3. Definiciones operativas ·
4. Lo que Guardian sabe en cada instante (vector desplazado y prueba de no fuga) · 5. El gemelo frente a repetir la
última lectura (N1b) · 6. ¿Avisaba antes el detector del parcial 1? (N1c) · 7. Señales candidatas ·
8. Anticipación (N1d) · 9. Piso y selección · 10. Caso, titular y rango plausible (10.1 ruido de semilla de los
bosques) · 11. Calibración ·
12. Explicador (N1e) · 13. Energía y casos críticos (N1f) · 14. Ejemplos para el mockup · 15. Deriva y sensibilidad ·
16. Cifras heredadas · 17. Figuras para el informe y el póster · 18. Exportación · 19. Verificación, resumen de
resultados y página del mockup
''')

code(r'''
import json, re, time, sys, platform, datetime, warnings
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn, nbformat
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (r2_score, mean_absolute_error, mean_squared_error, f1_score, accuracy_score,
                             precision_score, recall_score, roc_auc_score)
warnings.filterwarnings("ignore")

T0 = time.time()
RS = 42
pd.set_option("display.width", 170)
pd.set_option("display.max_columns", 40)

# ---------- Formato es-CO y registro de cifras (única fuente: cifras.json) ----------
CIFRAS = {"meta": {}, "nuevas": {}, "heredadas": {}}
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

def num_es(x, dec=1):
    x = float(x)
    if round(x, dec) == 0:
        x = 0.0                                        # sin "-0,000"
    s = f"{x:,.{dec}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")

def pct_es(x, dec=1):
    return num_es(x, dec) + " %"

def sig_es(x, dec=1):
    return ("+" if x > 0 else "") + num_es(x, dec)

def fecha_es(ts):
    ts = pd.Timestamp(ts)
    return f"{ts.day}-{MESES[ts.month - 1]}-{ts.year} {ts:%H:%M}"

SUFIJO = {"%": " %", "Wh": " Wh", "kWh": " kWh", "min": " min", "min/día": " min/día", "avisos/día": " avisos/día",
          "días": " días", "puntos": " puntos", "°C": " °C", "s": " s", "picos": " picos", "lecturas": " lecturas",
          "picos/día": " picos/día"}

def registrar(clave, valor, unidad="", dec=1, fuente="", desc="", bloque="nuevas", particion="temporal"):
    """Guarda una cifra con su texto es-CO. Los valores no numéricos (caso, modelo, frases) van como texto.
    Fechas: 'valor' guarda ISO y 'texto' la forma es-CO (con hora si el ISO la trae)."""
    if isinstance(valor, (bool, np.bool_)):
        valor = int(valor)
    if isinstance(valor, np.integer):
        valor = int(valor)
    if isinstance(valor, (float, np.floating)):
        valor = float(valor)
        assert np.isfinite(valor), f"{clave}: valor no finito"
        texto = num_es(valor, dec) + SUFIJO.get(unidad, "")
        valor = round(valor, 6) + 0.0                  # + 0.0 normaliza el cero negativo
    elif isinstance(valor, int):
        texto = num_es(valor, 0) + SUFIJO.get(unidad, "")
    else:
        valor = str(valor)
        if unidad == "fecha" and re.match(r"\d{4}-\d{2}-\d{2}T", valor):
            texto = fecha_es(valor)
        elif unidad == "fecha" and re.fullmatch(r"\d{4}-\d{2}-\d{2}", valor):
            texto = fecha_es(valor).split(" ")[0]
        elif unidad == "hora" and re.match(r"\d{4}-\d{2}-\d{2}T", valor):
            texto = f"{pd.Timestamp(valor):%H:%M}"
        else:
            texto = valor
    assert clave not in CIFRAS[bloque], f"clave repetida: {clave}"
    CIFRAS[bloque][clave] = {"valor": valor, "texto": texto, "unidad": unidad, "particion": particion,
                             "fuente": fuente, "descripcion": desc}
    return valor

def tabla_es(df_, dec=1):
    return df_.to_string(float_format=lambda x: num_es(x, dec))

def que_cambia(texto):
    print("\n→ Qué cambia en Shiro: " + texto)

print(f"Python {platform.python_version()} · scikit-learn {sklearn.__version__} · pandas {pd.__version__} · "
      f"numpy {np.__version__}")
''')

# =====================================================================================
# 1. Datos y particiones
# =====================================================================================
md(r'''
---
## 1. Datos y particiones
**Necesidad de Guardian.** Para prometer un margen de aviso, Guardian tiene que haberse juzgado en un periodo que no vio
ni para ajustar el modelo ni para fijar los colores del semáforo. Por eso se separan tres tramos cronológicos: *fit*
(ajuste de modelos), *validación* (elección del modelo y cortes de color) y *prueba* (el mes nunca visto, exactamente
las mismas lecturas del parcial 1 y del C2-T1).

La carga y las variables son idénticas a `Parcial_Corte1.ipynb` (c.3 y c.22): mismas 29 exógenas, mismos retardos con
`shift(1)` y el umbral de pico como percentil 90 del entrenamiento de la partición aleatoria (se verifica con `assert`).

**Limitación declarada del umbral.** Ese entrenamiento aleatorio contiene lecturas del mes de prueba, así que el umbral
de pico no es del todo ajeno a la prueba (la celda imprime cuántas lecturas y cuál sería el percentil 90 del
entrenamiento temporal). Se conserva por comparabilidad con las cifras publicadas (anclas de la sección 2). Solo afecta a
la **definición** de pico; ningún modelo, corte ni calibración de Guardian se ajusta con la prueba.
''')

code(r'''
CSV = "../../data set/energydata_complete.csv"
df = pd.read_csv(CSV, parse_dates=["date"])
DATOS = {"n": len(df), "columnas": df.shape[1], "faltantes": int(df.isna().sum().sum()),
         "dias": (df["date"].max() - df["date"].min()).total_seconds() / 86400}

df["hora"]         = df["date"].dt.hour
df["dia_semana"]    = df["date"].dt.dayofweek
df["es_fin_semana"] = (df["dia_semana"] >= 5).astype(int)
df["mes"]           = df["date"].dt.month

def franja(h):
    if h < 6:  return "Madrugada (00-06)"
    if h < 12: return "Mañana (06-12)"
    if h < 18: return "Tarde (12-18)"
    return "Noche (18-24)"
df["franja"] = df["hora"].apply(franja)

TEMPORALES = ["hora", "dia_semana", "es_fin_semana", "mes"]
INTERIOR   = [c for c in df.columns
              if c.startswith(("T", "RH_")) and c not in ("T_out", "RH_out", "Tdewpoint")]
CLIMA      = ["T_out", "RH_out", "Press_mm_hg", "Windspeed", "Visibility", "Tdewpoint"]
FEATURES   = TEMPORALES + ["lights"] + INTERIOR + CLIMA
TARGET     = "Appliances"
assert len(FEATURES) == 29

# Umbral de pico: percentil 90 del entrenamiento ALEATORIO (convención del proyecto)
X_tr, X_te, y_tr, y_te = train_test_split(df[FEATURES], df[TARGET], test_size=.2, random_state=RS)
UMBRAL = np.percentile(y_tr, 90)
assert UMBRAL == 200, UMBRAL

# Serie ordenada y retardos EXACTAMENTE como Parcial_Corte1.ipynb c.22
dfo = df.sort_values("date").reset_index(drop=True)
dl = dfo.copy()
for k in (1, 2, 3, 6):
    dl[f"lag{k}"] = dl[TARGET].shift(k)
dl["media_1h"] = dl[TARGET].shift(1).rolling(6).mean()
dl["max_1h"]   = dl[TARGET].shift(1).rolling(6).max()
dl["std_1h"]   = dl[TARGET].shift(1).rolling(6).std()
dl = dl.dropna().reset_index(drop=True)
cl = int(len(dl) * .8)
RETARDOS = ["lag1", "lag2", "lag3", "lag6", "media_1h", "max_1h", "std_1h"]
COLS = FEATURES + RETARDOS
assert cl == 15783 and len(dl) - cl == 3946

N = len(dl)
n_fit = int(0.85 * cl)
FECHA = dl["date"]
A = dl[TARGET].to_numpy(dtype=float)
IDX = np.arange(N)
fit_m  = IDX < n_fit
val_m  = (IDX >= n_fit) & (IDX < cl)
test_m = IDX >= cl
SEG = {"fit": (0, n_fit), "validación": (n_fit, cl), "prueba": (cl, N)}

def dias_seg(a, b):
    return (FECHA.iloc[b - 1] - FECHA.iloc[a]).total_seconds() / 86400

F1 = "§1 Datos y particiones"
registrar("datos_n_lecturas", DATOS["n"], "lecturas", 0, F1, "Lecturas del dataset completo (CSV)")
registrar("datos_n_columnas", DATOS["columnas"], "", 0, F1, "Columnas del CSV (fecha, objetivo, luces, sensores, clima, rv1, rv2)")
registrar("datos_faltantes", DATOS["faltantes"], "", 0, F1, "Valores faltantes en el CSV")
registrar("datos_dias", DATOS["dias"], "días", 0, F1, "Extensión del dataset (última − primera fecha)")
registrar("part_umbral_wh", float(UMBRAL), "Wh", 0, F1, "Umbral de pico: percentil 90 del entrenamiento aleatorio")
# Limitación: el entrenamiento aleatorio incluye lecturas del mes de prueba
n_tr_prueba = int((df.loc[X_tr.index, "date"] >= FECHA.iloc[cl]).sum())
p90_temporal = float(np.percentile(A[:cl], 90))
p90_fit = float(np.percentile(A[:n_fit], 90))
registrar("part_umbral_lecturas_prueba", n_tr_prueba, "lecturas", 0, F1,
          "Lecturas del entrenamiento aleatorio que caen en el mes de prueba (limitación del umbral de 200 Wh)")
registrar("part_umbral_p90_temporal", p90_temporal, "Wh", 0, F1, "Percentil 90 del consumo en el entrenamiento temporal (dl[:cl])")
registrar("part_umbral_p90_fit", p90_fit, "Wh", 0, F1, "Percentil 90 del consumo en fit")
registrar("part_n_variables", len(COLS), "", 0, F1, "Variables del vector con retardos (29 exógenas + 7 retardos)")
registrar("part_n_exogenas", len(FEATURES), "", 0, F1, "Variables exógenas (sin rv1/rv2)")
registrar("part_n_lecturas_dl", N, "lecturas", 0, F1, "Lecturas de la serie con retardos")
for nombre, (a, b) in SEG.items():
    clave = {"fit": "fit", "validación": "val", "prueba": "prueba"}[nombre]
    registrar(f"part_{clave}_n", b - a, "lecturas", 0, F1, f"Lecturas del tramo {nombre}")
    registrar(f"part_{clave}_inicio", FECHA.iloc[a].isoformat(), "fecha", 0, F1, f"Primera lectura del tramo {nombre}")
    registrar(f"part_{clave}_fin", FECHA.iloc[b - 1].isoformat(), "fecha", 0, F1, f"Última lectura del tramo {nombre}")
    registrar(f"part_{clave}_dias", dias_seg(a, b), "días", 1, F1, f"Días del tramo {nombre} (última − primera fecha)")
    print(f"{nombre:12s} {num_es(b - a, 0):>6s} lecturas · {fecha_es(FECHA.iloc[a])} → {fecha_es(FECHA.iloc[b - 1])} "
          f"({num_es(dias_seg(a, b))} días)")
print(f"Dataset: {num_es(DATOS['n'], 0)} lecturas, {DATOS['columnas']} columnas, {DATOS['faltantes']} faltantes, "
      f"{num_es(DATOS['dias'], 0)} días")
print(f"Umbral de pico: {UMBRAL:.0f} Wh · {len(COLS)} variables ({len(FEATURES)} exógenas + {len(RETARDOS)} retardos)")
print(f"Limitación: el entrenamiento aleatorio que fija los {UMBRAL:.0f} Wh incluye {num_es(n_tr_prueba, 0)} lecturas del mes "
      f"de prueba; el percentil 90 del entrenamiento temporal sería {num_es(p90_temporal, 0)} Wh (en fit, "
      f"{num_es(p90_fit, 0)} Wh). Se conserva {UMBRAL:.0f} Wh por comparabilidad con las anclas; solo define qué es un pico.")
que_cambia(f"Guardian se ajusta con {num_es(n_fit, 0)} lecturas (hasta el {fecha_es(FECHA.iloc[n_fit - 1])}), "
           f"elige modelo y colores con {num_es(cl - n_fit, 0)} de validación y se juzga en {num_es(N - cl, 0)} lecturas "
           f"que nunca vio; un pico sigue siendo una lectura de más de {UMBRAL:.0f} Wh.")
''')

# =====================================================================================
# 2. Anclas
# =====================================================================================
md(r'''
---
## 2. Anclas (N1a): el entorno reproduce lo publicado
**Necesidad de Guardian.** Este parcial corrige el relato del parcial 1 ("detectar" no es "avisar antes"). Esa
corrección solo es creíble si el mismo entorno reproduce primero, al decimal, las cifras publicadas: el gemelo lineal de
36 variables (G3a, `Parcial_Corte1.ipynb` c.25), el de 6 variables (G3c, c.33) y el detector del parcial 1 (bosque
aleatorio que reconoce la lectura actual, umbral 0,40, c.38) evaluado con las funciones de `Taller1_Boosting.ipynb` c.17.
Si un ancla falla, el cuaderno se detiene.
''')

code(r'''
XO = dl[COLS]                         # vector ORIGINAL: exógenas en t y retardos hasta t-1 (predice A(t))
Xa, Xb = XO.iloc[:cl], XO.iloc[cl:]
ya, yb = A[:cl], A[cl:]

# G3a: gemelo lineal de 36 variables en todo el entrenamiento (c.25)
G3A = LinearRegression().fit(Xa, ya)
p3a = G3A.predict(Xb)
# G3c: gemelo de 6 variables (c.33)
SEIS = ["hora", "lights", "T2", "RH_2", "T_out", "lag1"]
G3C = LinearRegression().fit(XO.iloc[:cl][SEIS], ya)
p3c = G3C.predict(XO.iloc[cl:][SEIS])
# Detector del parcial 1: RF 200 árboles, etiqueta "la lectura actual supera 200 Wh" (c.38)
DET = RandomForestClassifier(n_estimators=200, random_state=RS, n_jobs=-1).fit(Xa, (ya > UMBRAL).astype(int))
proba_det = DET.predict_proba(Xb)[:, 1]

# ---- Funciones de evaluación por episodio, copiadas de Taller1_Boosting.ipynb c.17 ----
def episodios(b, gap=3):
    idx = np.where(b == 1)[0]
    if len(idx) == 0: return []
    return np.split(idx, np.where(np.diff(idx) > gap)[0] + 1)

fechas_t = dl.iloc[cl:]["date"].values
DIAS_T = (pd.Timestamp(fechas_t[-1]) - pd.Timestamp(fechas_t[0])).total_seconds() / 86400

def evaluar_alertas(b, cte):
    cb = np.asarray(cte); ep_r = episodios(cb); ix_r = set(np.concatenate(ep_r)); ea = episodios(b)
    return {"avisos/día": len(ea) / DIAS_T,
            "eventos detectados %": sum(1 for e in ep_r if any(len(set(e) & set(a)) > 0 for a in ea)) / len(ep_r) * 100,
            "avisos falsos %": (len(ea) - sum(1 for a in ea if ix_r & set(a))) / max(len(ea), 1) * 100,
            "duración media (min)": float(np.mean([len(a) for a in ea]) * 10) if ea else 0.0,
            "tiempo en alerta %": b.mean() * 100}

CTE_T = (yb > UMBRAL).astype(int)
alerta_det = (proba_det >= .40).astype(int)
OP = evaluar_alertas(alerta_det, CTE_T)

ANCLAS = []
def ancla(clave, desc, valor, esperado, tol, unidad="", dec=3):
    ok = abs(valor - esperado) <= tol + 1e-12
    ANCLAS.append({"clave": clave, "valor": valor, "esperado": esperado, "tol": tol, "ok": ok})
    print(f"{'OK   ' if ok else 'FALLA'} {desc:52s} {valor:12.4f}   esperado {esperado} ± {tol}")
    registrar(f"ancla_{clave}", valor, unidad, dec, "§2 Anclas", desc)
    return ok

ancla("g3a_r2", "G3a · R² en prueba", r2_score(yb, p3a), 0.557, 0.001, "", 3)
ancla("g3a_mae", "G3a · MAE (Wh)", mean_absolute_error(yb, p3a), 28.17, 0.01, "Wh", 2)
ancla("g3a_rmse", "G3a · RMSE (Wh)", float(np.sqrt(mean_squared_error(yb, p3a))), 60.54, 0.01, "Wh", 2)
ancla("g3a_sesgo", "G3a · sesgo medio (Wh)", float((p3a - yb).mean()), 0.457, 0.01, "Wh", 3)
ancla("g3c_mae", "G3c · MAE (Wh)", mean_absolute_error(yb, p3c), 28.85, 0.01, "Wh", 2)
ancla("g3c_r2", "G3c · R² en prueba", r2_score(yb, p3c), 0.5358, 0.001, "", 4)
for var, ref in zip(SEIS, [0.3772, 0.7726, -0.1388, -0.8008, 0.7555, 0.7343]):
    ancla(f"g3c_coef_{var.lower()}", f"G3c · coeficiente de {var}", float(G3C.coef_[SEIS.index(var)]), ref, 0.0001, "", 4)
ancla("g3c_intercepto", "G3c · intercepto", float(G3C.intercept_), 49.1819, 0.0001, "", 4)
ancla("det_picos", "Detector P1 · picos del mes de prueba", float(len(episodios(CTE_T))), 84, 0, "picos", 0)
ancla("det_dias", "Detector P1 · días de prueba", DIAS_T, 27.4, 0.05, "días", 1)
ancla("det_detectados", "Detector P1 · picos tocados por alguna alerta (%)", OP["eventos detectados %"], 86.9, 0.05, "%", 1)
ancla("det_avisos_dia", "Detector P1 · avisos por día", OP["avisos/día"], 3.03, 0.005, "avisos/día", 2)
ancla("det_falsos", "Detector P1 · avisos falsos (%)", OP["avisos falsos %"], 37.3, 0.05, "%", 1)
ancla("det_f1", "Detector P1 · F1 por lectura a 0,40", f1_score(CTE_T, alerta_det), 0.47, 0.005, "", 2)
ancla("det_tiempo_alerta", "Detector P1 · tiempo en alerta (%)", OP["tiempo en alerta %"], 21.1, 0.05, "%", 1)
ancla("det_duracion", "Detector P1 · duración media del aviso (min)", OP["duración media (min)"], 100.5, 0.05, "min", 1)

assert all(a["ok"] for a in ANCLAS), "Un ancla falló: el cuaderno se detiene"
registrar("ancla_n_ok", sum(a["ok"] for a in ANCLAS), "", 0, "§2 Anclas", "Anclas que pasan")
que_cambia(f"{sum(a['ok'] for a in ANCLAS)} de {len(ANCLAS)} anclas en verde: cada cifra nueva de Guardian es comparable "
           f"punto a punto con el parcial 1 y el C2-T1, incluido el F1 por lectura del detector a 0,40, que es "
           f"{num_es(f1_score(CTE_T, alerta_det), 2)} y no el 0,580 que anotaba la tabla de resultados del proyecto "
           f"(ese es a 0,5; ver sección 16).")
''')

# =====================================================================================
# 3. Definiciones
# =====================================================================================
md(r'''
---
## 3. Definiciones operativas
**Necesidad de Guardian.** "Avisar a tiempo" tiene que poder contarse. Se fijan antes de calcular:

- **Pico (episodio):** lecturas de más de 200 Wh agrupadas con `gap=3` (la función `episodios` de C2-T1), calculados
  sobre la serie completa. Inicio *s*, fin *e*.
- **En calma:** lectura fuera de todo tramo [*s*, *e*]. Dentro de un tramo, el color es **rojo en curso**: lo da el
  medidor, sin modelo. Fijar *e* obliga a mirar hasta tres lecturas adelante (para saber si el pico sigue); se cuenta
  cuántas lecturas de prueba quedan afectadas por ese vistazo.
- **Etiqueta de anticipación** `y_ant(t) = 1` si *t* está en calma y un pico empieza en las próximas una a tres
  lecturas (*t* ∈ [*s*−3, *s*−1]).
- **Presupuesto de rojo r:** la tasa base de `y_ant` en la calma del entrenamiento; el semáforo marca en rojo tantos
  momentos tranquilos como los que de verdad preceden un pico. Se decide sin mirar la prueba.
- **Purga:** todo lo que se estima con `y_ant` excluye las tres últimas lecturas de *fit* y de validación (su etiqueta
  mira al tramo siguiente).
''')

code(r'''
alta = (A > UMBRAL).astype(int)
EP = episodios(alta)                                   # picos sobre la serie completa
S = np.array([e[0] for e in EP]); E = np.array([e[-1] for e in EP])
en_pico = np.zeros(N, bool)
for s, e in zip(S, E):
    en_pico[s:e + 1] = True
calma = ~en_pico

y_ant = np.zeros(N, int)
ventana_de = np.full(N, -1)                            # a qué pico precede cada lectura de ventana
for p, s in enumerate(S):
    for j in range(max(s - 3, 0), s):
        assert calma[j]                                # los picos están separados por ≥ 3 lecturas en calma
        y_ant[j] = 1; ventana_de[j] = p

def picos_seg(a, b):
    """Picos con alguna lectura en [a, b)."""
    return np.where((E >= a) & (S < b))[0]

ids_val, ids_te = picos_seg(n_fit, cl), picos_seg(cl, N)
assert len(ids_te) == 84 and abs(dias_seg(cl, N) - 27.4) < 0.05

purga = np.ones(N, bool); purga[n_fit - 3:n_fit] = False; purga[cl - 3:cl] = False
M_FIT = calma & fit_m & purga                          # filas de ajuste para lo que usa y_ant

afectadas = int((en_pico & (A <= UMBRAL) & test_m).sum())
r = float(y_ant[:cl][calma[:cl]].mean())               # presupuesto de rojo (tasa base del entrenamiento)
r_te = float(y_ant[test_m & calma].mean())
anticipables_20 = int(sum(1 for p in ids_te if S[p] - 2 >= cl))
anticipables_10 = int(sum(1 for p in ids_te if S[p] - 1 >= cl))
primero = ids_te[0]

F3 = "§3 Definiciones"
registrar("def_picos_prueba", len(ids_te), "picos", 0, F3, "Picos con alguna lectura en el mes de prueba")
registrar("def_picos_validacion", len(ids_val), "picos", 0, F3, "Picos con alguna lectura en validación")
registrar("def_picos_fit", len(picos_seg(0, n_fit)), "picos", 0, F3, "Picos con alguna lectura en fit")
registrar("def_dias_prueba", dias_seg(cl, N), "días", 1, F3, "Días del mes de prueba (como c.38)")
registrar("def_picos_por_dia_prueba", len(ids_te) / dias_seg(cl, N), "picos/día", 1, F3, "Picos por día en prueba")
registrar("def_lecturas_altas_prueba", int((A[cl:] > UMBRAL).sum()), "lecturas", 0, F3, "Lecturas > 200 Wh en prueba")
registrar("def_lecturas_altas_prueba_pct", (A[cl:] > UMBRAL).mean() * 100, "%", 1, F3, "% de lecturas > 200 Wh en prueba")
registrar("def_lecturas_afectadas_fin", afectadas, "lecturas", 0, F3,
          "Lecturas de prueba ≤ 200 Wh dentro de un pico: su estado depende de mirar hasta 3 lecturas adelante")
registrar("def_lecturas_afectadas_fin_pct", afectadas / (N - cl) * 100, "%", 2, F3, "Ídem, % de las lecturas de prueba")
registrar("def_tasa_base_r", r * 100, "%", 2, F3, "Tasa base de y_ant en la calma del entrenamiento = presupuesto de rojo r")
registrar("def_tasa_base_prueba", r_te * 100, "%", 2, F3, "Tasa base de y_ant en la calma de prueba")
registrar("def_calma_prueba_pct", calma[cl:].mean() * 100, "%", 1, F3, "% de lecturas de prueba en calma")
registrar("def_picos_anticipables_20", anticipables_20, "picos", 0, F3, "Picos de prueba cuya ventana de 20 min cae en prueba")
registrar("def_primer_pico_inicio", FECHA.iloc[S[primero]].isoformat(), "fecha", 0, F3,
          "Inicio del primer pico de prueba (empezó en el entrenamiento)")
registrar("def_purga_lecturas", int((~purga).sum()), "lecturas", 0, F3, "Lecturas purgadas en las fronteras")

dur_picos = (E[ids_te] - S[ids_te] + 1) * 10
print(f"Picos: {len(ids_te)} en prueba ({num_es(dias_seg(cl, N))} días), {len(ids_val)} en validación, "
      f"{len(picos_seg(0, n_fit))} en fit")
print(f"Duración de los picos de prueba: mediana {num_es(np.median(dur_picos), 0)} min · media {num_es(dur_picos.mean())} min")
print(f"El primer pico de prueba empezó el {fecha_es(FECHA.iloc[S[primero]])} (en el entrenamiento): "
      f"solo {anticipables_20} de {len(ids_te)} picos pueden avisarse con 20 min dentro de la prueba "
      f"({anticipables_10} con 10 min).")
print(f"Vistazo al futuro para fijar el fin del pico: {afectadas} lecturas de prueba "
      f"({num_es(afectadas / (N - cl) * 100, 2)} %) — se declara como limitación.")
print(f"Tasa base de y_ant en calma: entrenamiento {num_es(r * 100, 2)} % · prueba {num_es(r_te * 100, 2)} %")
que_cambia(f"el semáforo pintará de rojo el {num_es(r * 100, 2)} % de los momentos tranquilos (≈ "
           f"{num_es(r * 144 * calma[cl:].mean(), 0)} lecturas, {num_es(r * 1440 * calma[cl:].mean(), 0)} min al día); "
           f"ese es el valor por defecto del deslizador del mockup.")
''')

# =====================================================================================
# 4. Vector desplazado
# =====================================================================================
md(r'''
---
## 4. Lo que Guardian sabe en cada instante: el vector "un paso adelante"
**Necesidad de Guardian.** En el instante *t* Guardian ya leyó el consumo de *t* y tiene que decidir el color de la
próxima media hora. Los modelos del parcial 1 se entrenaron para la lectura *t* con retardos hasta *t*−1; aplicarlos
un paso adelante exige construir, columna por columna, lo que de verdad se conoce en *t*:

| Columna | Valor en *t* |
|---|---|
| 29 exógenas | las de la fila *t* |
| `lag1`, `lag2`, `lag3`, `lag6` | consumo en *t*, *t*−1, *t*−2 y *t*−5 |
| `media_1h`, `max_1h`, `std_1h` | sobre el consumo de *t*−5 a *t* (misma `std` de pandas) |

Se construye con `shift(k−1)` y `rolling(6)` sin desplazar, y se comprueba que no hay fuga: en instantes al azar el
vector recalculado solo con la historia hasta *t* es idéntico al de la tabla.
''')

code(r'''
A_dfo = dfo[TARGET]
desp = pd.DataFrame({"lag1": A_dfo.shift(0), "lag2": A_dfo.shift(1), "lag3": A_dfo.shift(2), "lag6": A_dfo.shift(5),
                     "media_1h": A_dfo.rolling(6).mean(), "max_1h": A_dfo.rolling(6).max(),
                     "std_1h": A_dfo.rolling(6).std()})
off = len(dfo) - N
assert (dfo["date"].iloc[off:].reset_index(drop=True) == FECHA).all()
desp = desp.iloc[off:].reset_index(drop=True)
XS = pd.concat([dl[FEATURES], desp], axis=1)[COLS]     # vector DESPLAZADO: lo que se conoce en t
assert XS.notna().all().all()
# Coherencia: los retardos desplazados en t son los originales de t+1
assert np.allclose(XS[RETARDOS].iloc[:-1].to_numpy(), XO[RETARDOS].iloc[1:].to_numpy(), rtol=0, atol=1e-9)

# assert de no fuga: 200 instantes al azar, recalculados solo con dl.loc[:t]
rng = np.random.RandomState(RS)
instantes = rng.choice(np.arange(5, N), size=200, replace=False)
dif_max = 0.0
for t in instantes:
    h = dl.loc[:t]
    a_ = h[TARGET].to_numpy(dtype=float)
    v = np.r_[h[FEATURES].iloc[-1].to_numpy(dtype=float), a_[-1], a_[-2], a_[-3], a_[-6],
              a_[-6:].mean(), a_[-6:].max(), a_[-6:].std(ddof=1)]
    dif_max = max(dif_max, float(np.abs(v - XS.iloc[t].to_numpy(dtype=float)).max()))
# Tolerancia 1e-4 Wh: pandas calcula rolling() con un algoritmo acumulado (suma móvil) que arrastra error de
# redondeo del orden de 1e-5 Wh frente al cálculo directo; una fuga se vería como decenas de Wh.
assert dif_max < 1e-4, dif_max
registrar("vec_no_fuga_instantes", len(instantes), "", 0, "§4 Vector desplazado", "Instantes verificados sin fuga")
registrar("vec_no_fuga_dif_max", dif_max, "Wh", 6, "§4 Vector desplazado", "Diferencia máxima (redondeo de rolling de pandas)")
print(f"No fuga: {len(instantes)} instantes al azar (semilla {RS}) idénticos al recalcular solo con el pasado, salvo "
      f"redondeo numérico del rolling de pandas (diferencia máxima {dif_max:.1e} Wh; tolerancia 1e-4 Wh).")
que_cambia("todo lo que entra a Guardian en t ya existe en t; el iot-bridge solo necesita guardar la última hora de "
           "consumo en memoria para construirlo.")
''')

# =====================================================================================
# 5. N1b Persistencia
# =====================================================================================
md(r'''
---
## 5. El gemelo frente a repetir la última lectura (N1b)
**Necesidad de Shiro.** El gemelo lineal + retardos es la función de transición del MDP (decisión del parcial 1 y del
C2-T1). Antes de que el
agente aprenda dentro de él hay que saber cuánto aporta frente a la referencia más fuerte con los mismos insumos:
**repetir la última lectura** (persistencia, ŷ = `lag1`). Se mide en total, por franja y en las lecturas de más de
200 Wh, que es donde el agente puede explotar errores del entorno. También se mide el gemelo "un paso adelante"
(exógenas de *t* para predecir *t*+1), que es como lo usará la tarjeta 1 del mockup.
''')

code(r'''
pers = Xb["lag1"].to_numpy()                            # persistencia: A(t-1) como predicción de A(t)
fr_te = dl["franja"].iloc[cl:].to_numpy()
grupos = {"total": np.ones(N - cl, bool)}
CL_FR = {"Madrugada (00-06)": "madrugada", "Mañana (06-12)": "manana", "Tarde (12-18)": "tarde", "Noche (18-24)": "noche"}
for f_, k_ in CL_FR.items():
    grupos[k_] = fr_te == f_
grupos["altas"] = yb > UMBRAL

def errores(y_, p_):
    return {"MAE": mean_absolute_error(y_, p_), "RMSE": float(np.sqrt(mean_squared_error(y_, p_))),
            "sesgo": float((p_ - y_).mean())}

PRED_N1B = {"persistencia": pers, "g3a": p3a, "g3c": p3c}
filas = []
for g, m_ in grupos.items():
    for mod, p_ in PRED_N1B.items():
        e_ = errores(yb[m_], p_[m_])
        filas.append({"grupo": g, "modelo": mod, "n": int(m_.sum()), **e_})
        for met, v_ in e_.items():
            registrar(f"n1b_{mod}_{g}_{met.lower()}", v_, "Wh", 2, "§5 N1b", f"{met} de {mod} en {g} (prueba)")
N1B = pd.DataFrame(filas)
print(tabla_es(N1B.pivot(index="grupo", columns="modelo", values="MAE").loc[list(grupos)], 2).replace("modelo", "MAE (Wh)"))
print()
print(tabla_es(N1B.pivot(index="grupo", columns="modelo", values="RMSE").loc[list(grupos)], 2).replace("modelo", "RMSE (Wh)"))
print()
print(tabla_es(N1B.pivot(index="grupo", columns="modelo", values="sesgo").loc[list(grupos)], 2).replace("modelo", "sesgo (Wh)"))
registrar("n1b_n_altas", int(grupos["altas"].sum()), "lecturas", 0, "§5 N1b", "Lecturas > 200 Wh en prueba")

# Un paso adelante: exógenas de t para predecir A(t+1)
p3a_pa = G3A.predict(XS.iloc[cl - 1:N - 1]); p3c_pa = G3C.predict(XS.iloc[cl - 1:N - 1][SEIS])
d3a = mean_absolute_error(yb, p3a_pa) - mean_absolute_error(yb, p3a)
d3c = mean_absolute_error(yb, p3c_pa) - mean_absolute_error(yb, p3c)
registrar("n1b_g3a_unpaso_mae", mean_absolute_error(yb, p3a_pa), "Wh", 2, "§5 N1b", "MAE de G3a con exógenas de t (un paso adelante)")
registrar("n1b_g3c_unpaso_mae", mean_absolute_error(yb, p3c_pa), "Wh", 2, "§5 N1b", "MAE de G3c con exógenas de t (un paso adelante)")
print(f"\nUn paso adelante (exógenas de t): MAE de G3a cambia {sig_es(d3a, 3)} Wh, el de G3c {sig_es(d3c, 3)} Wh.")
pg = lambda mod, g, met: N1B.query("modelo == @mod and grupo == @g")[met].iloc[0]
d_mae = (pg("g3a", "total", "MAE") / pg("persistencia", "total", "MAE") - 1) * 100
d_rmse = (pg("g3a", "total", "RMSE") / pg("persistencia", "total", "RMSE") - 1) * 100
registrar("n1b_g3a_vs_pers_mae_pct", d_mae, "%", 1, "§5 N1b", "Diferencia relativa de MAE de G3a frente a persistencia")
registrar("n1b_g3a_vs_pers_rmse_pct", d_rmse, "%", 1, "§5 N1b", "Diferencia relativa de RMSE de G3a frente a persistencia")
que_cambia(f"el gemelo se equivoca {num_es(pg('g3a', 'total', 'MAE'), 2)} Wh por lectura frente a "
           f"{num_es(pg('persistencia', 'total', 'MAE'), 2)} Wh de repetir la última lectura ({sig_es(d_mae)} % de MAE, "
           f"{sig_es(d_rmse)} % de RMSE); en las {int(grupos['altas'].sum())} lecturas de más de 200 Wh su sesgo es "
           f"{num_es(pg('g3a', 'altas', 'sesgo'), 1)} Wh (persistencia {num_es(pg('persistencia', 'altas', 'sesgo'), 1)}): "
           f"el gemelo subestima los picos y la recompensa del MDP debe corregirlo. "
           + ("Frente a repetir la última lectura pierde en el error típico (MAE) y gana en los errores grandes (RMSE): "
              "su aporte como función de transición está en las desviaciones grandes, no en el paso a paso."
              if (d_mae > 0 and d_rmse < 0) else
              ("Gana a la persistencia en MAE y en RMSE." if (d_mae < 0 and d_rmse < 0) else
               "No gana a la persistencia en RMSE: su papel como función de transición queda en duda.")))
''')

# =====================================================================================
# 6. N1c Latencia
# =====================================================================================
md(r'''
---
## 6. ¿Avisaba antes el detector del parcial 1? (N1c)
**Necesidad de Guardian.** El parcial 1 reportó el porcentaje de picos "detectados": picos tocados por *alguna* alerta,
aunque llegara con el pico ya empezado. Para Guardian importa **cuándo** llega la primera alerta. Para cada pico de
prueba se busca la primera lectura en alerta del detector a 0,40 dentro de [*s*−3, *e*] y se clasifica: antes del
inicio (con sus minutos), en el inicio, después del inicio o nunca. Además, qué parte de la energía del pico (Wh de
[*s*, *e*]) quedaba todavía por delante en esa primera alerta (convención: la lectura de la alerta cuenta como "por
delante"; una alerta anterior al inicio deja el 100 %).
''')

code(r'''
lat = []
for p in ids_te:
    s, e = S[p], E[p]
    w = np.arange(max(s - 3, cl), e + 1)
    al = w[alerta_det[w - cl] == 1]
    en_total = A[s:e + 1].sum()
    if len(al) == 0:
        lat.append({"pico": p, "cat": "nunca", "min": np.nan, "resta": np.nan}); continue
    j = al[0]
    cat = "antes" if j < s else ("en el inicio" if j == s else "después")
    resta = 100.0 if j <= s else A[j:e + 1].sum() / en_total * 100
    lat.append({"pico": p, "cat": cat, "min": 10 * (s - j), "resta": resta})
LAT = pd.DataFrame(lat)
cnt = LAT["cat"].value_counts().reindex(["antes", "en el inicio", "después", "nunca"], fill_value=0)
F6 = "§6 N1c"
for c_, n_ in cnt.items():
    k_ = {"antes": "antes", "en el inicio": "inicio", "después": "despues", "nunca": "nunca"}[c_]
    registrar(f"n1c_{k_}_n", int(n_), "picos", 0, F6, f"Picos cuya primera alerta del detector P1 llega: {c_}")
    registrar(f"n1c_{k_}_pct", n_ / len(LAT) * 100, "%", 1, F6, f"% de picos con primera alerta: {c_}")
antes = LAT[LAT.cat == "antes"]
con_al = LAT[LAT.cat != "nunca"]
registrar("n1c_antes_20_n", int((antes["min"] >= 20).sum()), "picos", 0, F6, "Picos con primera alerta ≥ 20 min antes")
registrar("n1c_resta_mediana", float(con_al["resta"].median()), "%", 1, F6,
          "Mediana del % de energía del pico aún por delante en la primera alerta (picos con alerta)")
registrar("n1c_resta_media", float(con_al["resta"].mean()), "%", 1, F6,
          "Media del % de energía del pico aún por delante en la primera alerta (picos con alerta)")
tarde = LAT[LAT.cat == "después"]
registrar("n1c_despues_min_mediana", float(-tarde["min"].median()) if len(tarde) else 0.0, "min", 0, F6,
          "Mediana de minutos de retraso cuando la alerta llega después del inicio")
print("Primera alerta del detector del parcial 1 (umbral 0,40) frente al inicio de cada pico de prueba:")
for c_, n_ in cnt.items():
    print(f"  {c_:13s} {n_:3d} picos ({pct_es(n_ / len(LAT) * 100)})")
print(f"  de los que llegan antes: " + ", ".join(f"{int(m)} min: {int((antes['min'] == m).sum())}" for m in (10, 20, 30)))
print(f"Energía del pico aún por delante en la primera alerta: mediana {pct_es(con_al['resta'].median())} · "
      f"media {pct_es(con_al['resta'].mean())}")

# Contexto para leer el "antes": cuánto tiempo tranquilo pasaba el detector en alerta, y qué antelación
# lograría con el mismo tiempo en rojo que Guardian (definiciones de la sección 8, que aquí se adelantan).
calma_te = calma[cl:]
alerta_calma_pct = alerta_det[calma_te].mean() * 100
ids_tmp = ids_te
def antel_simple(rojo_full):
    out = []
    for p in ids_tmp:
        s = S[p]; a_ = 0
        for j in range(max(s - 3, cl), s):
            if rojo_full[j]: a_ = 10 * (s - j); break
        out.append(a_)
    return np.array(out)
rojo_det = np.zeros(N, bool); rojo_det[cl:] = (alerta_det == 1) & calma_te
ant_det = antel_simple(rojo_det)
score_det = np.full(N, -np.inf); score_det[cl:] = proba_det
idx_c_ = np.where(calma & test_m)[0]
k_ = int(round(r * len(idx_c_)))
orden_ = np.lexsort((idx_c_, -score_det[idx_c_]))
rojo_det_r = np.zeros(N, bool); rojo_det_r[idx_c_[orden_[:k_]]] = True
ant_det_r = antel_simple(rojo_det_r)
registrar("n1c_alerta_calma_pct", alerta_calma_pct, "%", 1, F6, "% de la calma de prueba en alerta del detector P1 a 0,40")
registrar("n1c_det040_p20", (ant_det >= 20).mean() * 100, "%", 1, F6,
          "% de picos con ≥ 20 min del detector P1 a 0,40 contado como semáforo (solo lecturas en calma)")
registrar("n1c_det_mismo_r_p20", (ant_det_r >= 20).mean() * 100, "%", 1, F6,
          "% de picos con ≥ 20 min del detector P1 con el mismo tiempo en rojo que Guardian (top-r de su probabilidad)")
print(f"Contexto: a 0,40 el detector estaba en alerta el {pct_es(alerta_calma_pct)} del tiempo tranquilo de prueba "
      f"(presupuesto de Guardian: {pct_es(r * 100, 2)}). Contado como semáforo: {pct_es((ant_det >= 20).mean() * 100)} de "
      f"picos con ≥ 20 min; con el mismo tiempo en rojo que Guardian: {pct_es((ant_det_r >= 20).mean() * 100)}.")
# ¿Las alertas "antes" son avisos dirigidos al pico o la cola de una alerta larga que ya estaba encendida?
def racha_previa(j):
    """Lecturas consecutivas en alerta inmediatamente antes de j (en el mes de prueba)."""
    n_ = 0
    while j - 1 - n_ >= cl and alerta_det[j - 1 - n_ - cl] == 1:
        n_ += 1
    return n_
ya_enc, racha60 = 0, 0
for p in ids_te:
    s = S[p]
    w = np.arange(max(s - 3, cl), s)
    al = w[alerta_det[w - cl] == 1]
    if len(al):
        rp = racha_previa(al[0])
        ya_enc += rp > 0
        racha60 += rp >= 6
n_antes = int(cnt["antes"])
registrar("n1c_antes_ya_encendida_n", int(ya_enc), "picos", 0, F6,
          "Picos con primera alerta 'antes' cuya alerta ya estaba encendida en la lectura anterior a la ventana [s−3, s−1]")
registrar("n1c_antes_racha60_n", int(racha60), "picos", 0, F6,
          "Ídem, con la alerta encendida desde hacía ≥ 60 min al llegar a la ventana")
print(f"De los {n_antes} picos con alerta 'antes', en {ya_enc} la alerta ya estaba encendida en la lectura anterior a la "
      f"ventana de 30 min (en {racha60}, desde hacía ≥ 60 min); los avisos del detector duran "
      f"{num_es(OP['duración media (min)'])} min de media.")
if ya_enc > n_antes / 2:
    print("Lectura: la mayoría de las alertas 'antes' son la cola de alertas largas que ya estaban encendidas, no un "
          "aviso que se enciende para el pico que viene.")
else:
    print("Lectura: la mayoría de las alertas 'antes' se encienden dentro de la ventana de 30 min previa al pico.")
print("Hipótesis previa ('casi nunca avisa antes'): " +
      ("no se sostiene" if n_antes / len(LAT) >= 0.2 else "se sostiene") +
      f" — {pct_es(n_antes / len(LAT) * 100)} de los picos tienen la primera alerta antes del inicio.")
que_cambia(f"el {pct_es(OP['eventos detectados %'])} del parcial 1 no es una promesa de aviso anticipado: "
           f"{cnt['antes']} de {len(LAT)} picos ({pct_es(cnt['antes'] / len(LAT) * 100)}) recibieron la primera alerta "
           f"antes de empezar ({int((antes['min'] >= 20).sum())} con 20 min o más), pero a costa de tener en alerta el "
           f"{pct_es(alerta_calma_pct)} del tiempo tranquilo; con el presupuesto de Guardian ese detector avisaría con "
           f"≥ 20 min el {pct_es((ant_det_r >= 20).mean() * 100)} de los picos. Guardian se juzga por antelación con "
           f"tiempo en rojo fijo, no por si toca el pico.")
''')

# =====================================================================================
# 7. Señales candidatas
# =====================================================================================
md(r'''
---
## 7. Señales candidatas
**Necesidad de Guardian.** El semáforo necesita un **puntaje** por momento tranquilo: cuanto más alto, más probable que
un pico empiece en la próxima media hora. Todas las señales se aplican sobre el vector desplazado y se ajustan solo con
*fit* (percentiles, frecuencias, escalado y modelos).

| Señal | Qué es | Simplicidad |
|---|---|---|
| **Regla de nivel** | puntaje = consumo actual; sin etiquetas (listón, no candidata) | — |
| **G0** modelo mínimo de 2 variables | percentil del consumo actual + percentil de la frecuencia de `y_ant` por hora × laborable/fin de semana (48 celdas), estimados en *fit* | 0 |
| **G3b** gemelo de 36 variables | pronóstico lineal del consumo en *t*+1 | 1 |
| **G2** logística que reconoce | entrenada para "la lectura actual supera 200 Wh" | 1 |
| **G5** logística que anticipa | entrenada con `y_ant` en la calma de *fit* (purgada) | 1 |
| **G1** bosque que reconoce | 200 árboles, etiqueta "la lectura actual supera 200 Wh" | 2 |
| **G4** bosque que anticipa | 200 árboles, entrenado con `y_ant` | 2 |

El escalador de G2 se ajusta con todo *fit* (las filas con que se entrena G2); el de G5, con las filas con que se entrena
G5 (calma de *fit* purgada). La sección 8 mide la variante de G5 con el escalador ajustado en todo *fit*.
''')

code(r'''
t_mod = time.time()
SCORE = {"regla": A.copy()}

# G0: modelo mínimo entrenado de dos variables
ref_nivel = np.sort(A[M_FIT])
def ecdf(ref, x):
    return np.searchsorted(ref, x, side="right") / len(ref)
celda = (dl["hora"] * 2 + dl["es_fin_semana"]).to_numpy()
freq = pd.Series(y_ant[M_FIT]).groupby(celda[M_FIT]).mean().reindex(range(48))
assert freq.notna().all()
freq_t = freq.to_numpy()[celda]
ref_hora = np.sort(freq_t[M_FIT])
p_nivel, p_hora = ecdf(ref_nivel, A), ecdf(ref_hora, freq_t)
SCORE["G0"] = p_nivel + p_hora

# G1 y G2: entrenados para RECONOCER (A(t) > 200 con el vector original), puntaje sobre el vector desplazado
G1 = RandomForestClassifier(n_estimators=200, random_state=RS, n_jobs=-1).fit(XO[fit_m], alta[fit_m])
SCORE["G1"] = G1.predict_proba(XS)[:, 1]
SC2 = StandardScaler().fit(XO[fit_m])
G2 = LogisticRegression(max_iter=2000).fit(SC2.transform(XO[fit_m]), alta[fit_m])
SCORE["G2"] = G2.predict_proba(SC2.transform(XS))[:, 1]
# G3b: gemelo de 36 variables en fit; su pronóstico de t+1 es el puntaje
G3B = LinearRegression().fit(XO[fit_m], A[fit_m])
SCORE["G3b"] = G3B.predict(XS)
# G4 y G5: entrenados para ANTICIPAR (y_ant en la calma de fit, purgada), entradas = vector desplazado
G4 = RandomForestClassifier(n_estimators=200, random_state=RS, n_jobs=-1).fit(XS[M_FIT], y_ant[M_FIT])
SCORE["G4"] = G4.predict_proba(XS)[:, 1]
SC5 = StandardScaler().fit(XS[M_FIT])
G5 = LogisticRegression(max_iter=2000).fit(SC5.transform(XS[M_FIT]), y_ant[M_FIT])
SCORE["G5"] = G5.predict_proba(SC5.transform(XS))[:, 1]

SENALES = ["regla", "G0", "G1", "G2", "G3b", "G4", "G5"]
CANDIDATOS = ["G0", "G3b", "G2", "G5", "G1", "G4"]
NIVEL = {"G0": 0, "G3b": 1, "G2": 1, "G5": 1, "G1": 2, "G4": 2}
NVARS = {"G0": 2, "G1": len(COLS), "G2": len(COLS), "G3b": len(COLS), "G4": len(COLS), "G5": len(COLS)}
NOMBRE = {"regla": "regla de nivel", "G0": "modelo mínimo de dos variables (G0)",
          "G1": "bosque aleatorio que reconoce (G1)", "G2": "regresión logística que reconoce (G2)",
          "G3b": "gemelo de 36 variables como puntaje (G3b)", "G4": "bosque aleatorio que anticipa (G4)",
          "G5": "regresión logística que anticipa (G5)"}
CLAVE = {s_: s_.lower() for s_ in SENALES}
print(f"Filas de ajuste: {num_es(fit_m.sum(), 0)} (G1, G2, G3b) · {num_es(M_FIT.sum(), 0)} en calma purgada (G0, G4, G5) · "
      f"tasa de y_ant en ellas {pct_es(y_ant[M_FIT].mean() * 100, 2)}")
print(f"Señales listas en {num_es(time.time() - t_mod)} s")
registrar("sen_filas_fit_calma", int(M_FIT.sum()), "lecturas", 0, "§7 Señales", "Filas de ajuste de G0, G4 y G5")
que_cambia("Guardian tiene seis candidatos supervisados y un listón sin etiquetas; todos producen un puntaje por "
           "momento tranquilo que el semáforo convierte en color con cortes fijados en validación.")
''')

# =====================================================================================
# 8. N1d Anticipación
# =====================================================================================
md(r'''
---
## 8. Anticipación (N1d)
**Necesidad de Guardian.** Elegir la señal del semáforo exige compararlas en igualdad de condiciones y medir lo que la
persona vive. Definiciones de esta sección:

- **Mismo tiempo en rojo (comparación):** cada señal marca en rojo el top-*r* de su puntaje en la calma del tramo
  (empates: la lectura más temprana primero; *k* = round(*r* × lecturas en calma)).
- **Desplegado:** los cortes se fijan en la calma de validación (rojo: cuantil 1−*r*; amarillo: cuantil 1−2*r*) y se
  aplican tal cual a la prueba. Así funcionaría Guardian de verdad.
- **Antelación de un pico:** 10 × (*s* − primera lectura en rojo de [*s*−3, *s*−1]) minutos, nominal (la real es de 0 a
  10 min menor). Se reporta el % de picos con ≥ 10, ≥ 20 y ≥ 30 min sobre todos los picos del tramo.
- **Aviso:** lecturas en calma en rojo agrupadas con `gap=3`; **útil** si toca la ventana de un pico; avisos por día,
  duración media y % de útiles. **Acierto de un color:** % de sus lecturas con `y_ant = 1`.
''')

code(r'''
def marcar_top(score, a, b, frac):
    idx = np.where(calma[a:b])[0] + a
    k = int(round(frac * len(idx)))
    orden = np.lexsort((idx, -score[idx]))            # puntaje descendente; empate → más temprano
    rojo = np.zeros(N, bool); rojo[idx[orden[:k]]] = True
    return rojo

def cortes_val(score, frac):
    v = score[calma & val_m]
    return float(np.quantile(v, 1 - frac)), float(np.quantile(v, 1 - 2 * frac))

def antelaciones(rojo, a, b):
    ids = picos_seg(a, b); out = np.zeros(len(ids), int)
    for i, p in enumerate(ids):
        s = S[p]
        for j in range(max(s - 3, a), s):
            if rojo[j]:
                out[i] = 10 * (s - j); break
    return ids, out

def evaluar(rojo, a, b, amarillo=None):
    seg = (IDX >= a) & (IDX < b)
    rojo = rojo & calma & seg
    ids, ant = antelaciones(rojo, a, b)
    dias = dias_seg(a, b)
    av = [x + a for x in episodios(rojo[a:b].astype(int))]
    util = np.array([bool(y_ant[x].any()) for x in av])
    nc = int((calma & seg).sum())
    m = {"p10": (ant >= 10).mean() * 100, "p20": (ant >= 20).mean() * 100, "p30": (ant >= 30).mean() * 100,
         "n10": int((ant >= 10).sum()), "n20": int((ant >= 20).sum()), "n30": int((ant >= 30).sum()),
         "picos": len(ids), "avisos": len(av), "avisos_dia": len(av) / dias,
         "duracion": float(np.mean([len(x) for x in av]) * 10) if av else 0.0,
         "utiles": float(util.mean() * 100) if av else 0.0,
         "acierto_rojo": float(y_ant[rojo].mean() * 100) if rojo.any() else 0.0,
         "rojo_pct": rojo.sum() / nc * 100, "min_dia": rojo.sum() * 10 / dias}
    m["falsos"] = 100 - m["utiles"]
    if amarillo is not None:
        am = amarillo & calma & seg & ~rojo
        verde = calma & seg & ~rojo & ~am
        m.update({"amarillo_pct": am.sum() / nc * 100, "acierto_amarillo": float(y_ant[am].mean() * 100) if am.any() else 0.0,
                  "acierto_verde": float(y_ant[verde].mean() * 100), "min_dia_fuera_verde": (rojo.sum() + am.sum()) * 10 / dias})
    return m, {"ids": ids, "ant": ant, "avisos": av, "util": util, "rojo": rojo}

RES, DET_, CORTES = {}, {}, {}
for sg in SENALES:
    RES[("val", sg)], DET_[("val", sg)] = evaluar(marcar_top(SCORE[sg], n_fit, cl, r), n_fit, cl)
    RES[("prueba", sg)], DET_[("prueba", sg)] = evaluar(marcar_top(SCORE[sg], cl, N, r), cl, N)
    cr, ca_ = cortes_val(SCORE[sg], r)
    CORTES[sg] = (cr, ca_)
    rojo_d = calma & (SCORE[sg] >= cr); am_d = calma & (SCORE[sg] >= ca_) & ~rojo_d
    RES[("desp", sg)], DET_[("desp", sg)] = evaluar(rojo_d, cl, N, am_d)

METRICAS = {"p10": ("%", 1, "% de picos con antelación ≥ 10 min"), "p20": ("%", 1, "% de picos con antelación ≥ 20 min"),
            "p30": ("%", 1, "% de picos con antelación ≥ 30 min"), "n10": ("picos", 0, "Picos con antelación ≥ 10 min"),
            "n20": ("picos", 0, "Picos con antelación ≥ 20 min"), "n30": ("picos", 0, "Picos con antelación ≥ 30 min"),
            "avisos_dia": ("avisos/día", 2, "Avisos por día"), "duracion": ("min", 1, "Duración media del aviso"),
            "utiles": ("%", 1, "% de avisos útiles (preceden un pico)"), "falsos": ("%", 1, "% de avisos falsos"),
            "acierto_rojo": ("%", 1, "Acierto del rojo (% de lecturas rojas con y_ant = 1)"),
            "rojo_pct": ("%", 2, "% de la calma en rojo"), "min_dia": ("min/día", 0, "Minutos al día en rojo"),
            "amarillo_pct": ("%", 2, "% de la calma en amarillo"), "acierto_amarillo": ("%", 1, "Acierto del amarillo"),
            "acierto_verde": ("%", 1, "Acierto del verde (% de lecturas verdes que preceden un pico)"),
            "min_dia_fuera_verde": ("min/día", 0, "Minutos al día fuera de verde")}
TRAMO = {"val": "validación, mismo tiempo en rojo", "prueba": "prueba, mismo tiempo en rojo",
         "desp": "prueba, desplegado con cortes de validación"}
for (tr, sg), m in RES.items():
    for met, v_ in m.items():
        if met in METRICAS:
            u_, d_, desc_ = METRICAS[met]
            nota_ = ""
            if tr == "desp":
                nota_ = (f" · rojo realizado {pct_es(m['rojo_pct'], 2)} de la calma: no comparable entre señales "
                         f"(para comparar, usar las claves *_prueba_*, mismo tiempo en rojo)")
            registrar(f"{CLAVE[sg]}_{tr}_{met}", v_, u_, d_, "§8 N1d", f"{desc_} · {NOMBRE[sg]} · {TRAMO[tr]}{nota_}")
for sg in SENALES:
    registrar(f"{CLAVE[sg]}_corte_rojo", CORTES[sg][0], "", 4, "§8 N1d", f"Corte rojo (validación) · {NOMBRE[sg]}")
    registrar(f"{CLAVE[sg]}_corte_amarillo", CORTES[sg][1], "", 4, "§8 N1d", f"Corte amarillo (validación) · {NOMBRE[sg]}")

COLS_T = ["p10", "p20", "p30", "n20", "avisos_dia", "duracion", "utiles", "acierto_rojo", "rojo_pct"]
for tr in ("val", "prueba", "desp"):
    t_ = pd.DataFrame({sg: RES[(tr, sg)] for sg in SENALES}).T[COLS_T + (["min_dia"] if tr == "desp" else [])]
    print(f"\n=== {TRAMO[tr]} · {RES[(tr, 'regla')]['picos']} picos ===")
    print(tabla_es(t_.astype(float), 1))
# Variante de G5 con el escalador ajustado en todo fit (elección no fijada de antemano: se declara su efecto)
SC5b = StandardScaler().fit(XS[fit_m])
G5b = LogisticRegression(max_iter=2000).fit(SC5b.transform(XS[M_FIT]), y_ant[M_FIT])
sc5b = G5b.predict_proba(SC5b.transform(XS))[:, 1]
m5b_v, _ = evaluar(marcar_top(sc5b, n_fit, cl, r), n_fit, cl)
m5b_t, _ = evaluar(marcar_top(sc5b, cl, N, r), cl, N)
registrar("g5_alt_escalador_val_p20", m5b_v["p20"], "%", 1, "§8 N1d",
          "G5 con el escalador ajustado en todo fit: % de picos con ≥ 20 min en validación (mismo tiempo en rojo)")
registrar("g5_alt_escalador_prueba_p20", m5b_t["p20"], "%", 1, "§8 N1d",
          "G5 con el escalador ajustado en todo fit: % de picos con ≥ 20 min en prueba (mismo tiempo en rojo)")
print(f"\nG5 con el escalador ajustado en todo fit (en vez de la calma purgada): validación {pct_es(m5b_v['p20'])} "
      f"(frente a {pct_es(RES[('val', 'G5')]['p20'])}), prueba {pct_es(m5b_t['p20'])} "
      f"(frente a {pct_es(RES[('prueba', 'G5')]['p20'])}).")
mejor_val = max(CANDIDATOS, key=lambda g: RES[("val", g)]["p20"])
que_cambia(f"en validación la mejor señal a ≥ 20 min es {NOMBRE[mejor_val]} con {pct_es(RES[('val', mejor_val)]['p20'])}; "
           f"la regla de nivel logra {pct_es(RES[('val', 'regla')]['p20'])}. La elección formal sale de la sección 9.")
''')

# =====================================================================================
# 9. Piso y selección
# =====================================================================================
md(r'''
---
## 9. Piso y selección (solo en validación)
**Necesidad de Guardian.** Un semáforo que avisa poco o que se equivoca demasiado se termina ignorando (hallazgo 9 del
proyecto). Antes de elegir, cada candidato debe superar un **piso** en validación: más picos con ≥ 20 min que la regla
de nivel, un mínimo de picos con ese margen y un mínimo de avisos útiles (los dos mínimos, fijados de antemano, se
imprimen abajo).

**Regla de selección**, fijada de antemano: entre los que pasan el piso, el **más simple** de los que quedan a menos de
10 puntos del mejor (≥ 20 min); dentro de un nivel, el de mayor %. Si ninguno pasa, la misma regla sin piso (caso C1).
El gemelo es siempre el segundo modelo elegido: la función de transición del MDP.
''')

code(r'''
PISO_P20, PISO_UTILES, MARGEN = 25.0, 33.0, 10.0
reg_val = RES[("val", "regla")]["p20"]
PISO = {}
for g in CANDIDATOS:
    m = RES[("val", g)]
    c1, c2, c3 = m["p20"] > reg_val, m["p20"] >= PISO_P20, m["utiles"] >= PISO_UTILES
    PISO[g] = {"supera_regla": c1, "p20_25": c2, "utiles_33": c3, "pasa": c1 and c2 and c3}
    registrar(f"piso_{CLAVE[g]}_pasa", int(PISO[g]["pasa"]), "", 0, "§9 Selección", f"1 si {NOMBRE[g]} pasa el piso en validación")
TP = pd.DataFrame(PISO).T.map(lambda b_: "sí" if b_ else "no")
TP.insert(0, "útiles val %", [RES[("val", g)]["utiles"] for g in CANDIDATOS])
TP.insert(0, "≥ 20 min val %", [RES[("val", g)]["p20"] for g in CANDIDATOS])
TP.insert(0, "nivel", [NIVEL[g] for g in CANDIDATOS])
print(f"Piso: ≥ 20 min > regla ({pct_es(reg_val)}), ≥ {num_es(PISO_P20, 0)} % de picos y ≥ {num_es(PISO_UTILES, 0)} % de avisos útiles")
print(tabla_es(TP, 1))

def seleccionar(pool):
    mejor = max(RES[("val", g)]["p20"] for g in pool)
    cerca = [g for g in pool if mejor - RES[("val", g)]["p20"] < MARGEN]
    nmin = min(NIVEL[g] for g in cerca)
    return max([g for g in cerca if NIVEL[g] == nmin], key=lambda g: (RES[("val", g)]["p20"], -CANDIDATOS.index(g))), mejor, cerca

pasan = [g for g in CANDIDATOS if PISO[g]["pasa"]]
hay_piso = len(pasan) > 0
ELEG, mejor_p20_val, cerca = seleccionar(pasan if hay_piso else CANDIDATOS)
F9 = "§9 Selección"
registrar("sel_elegido", ELEG, "", 0, F9, "Modelo elegido para el semáforo de Guardian (validación)")
registrar("sel_elegido_nombre", NOMBRE[ELEG], "", 0, F9, "Nombre llano del modelo elegido")
registrar("sel_nivel", NIVEL[ELEG], "", 0, F9, "Nivel de simplicidad del elegido (0 = mínimo)")
registrar("sel_nvars", NVARS[ELEG], "", 0, F9, "Variables que usa el elegido")
registrar("sel_n_pasan_piso", len(pasan), "", 0, F9, "Candidatos que pasan el piso en validación")
registrar("sel_pasan_piso", ", ".join(pasan) if pasan else "ninguno", "", 0, F9, "Candidatos que pasan el piso")
registrar("sel_mejor_p20_val", mejor_p20_val, "%", 1, F9, "Mejor % de picos con ≥ 20 min en validación")
registrar("sel_cerca", ", ".join(cerca), "", 0, F9, "Candidatos a menos de 10 puntos del mejor")
registrar("sel_gemelo", "G3a (36 variables) para el pronóstico; G3c (6 variables) en la tarjeta 1", "", 0, F9,
          "Segundo modelo elegido: el gemelo (función de transición)")
print(f"\nPasan el piso: {', '.join(pasan) if pasan else 'ninguno'} · mejor en validación {pct_es(mejor_p20_val)} · "
      f"a menos de {MARGEN:.0f} puntos: {', '.join(cerca)}")
print(f"ELEGIDO: {NOMBRE[ELEG]} (nivel {NIVEL[ELEG]}, {NVARS[ELEG]} variables)")
que_cambia(f"el semáforo de Guardian lo maneja {NOMBRE[ELEG]}; el gemelo lineal + retardos sigue siendo la función de "
           f"transición del MDP." + ("" if hay_piso else " Ningún candidato pasó el piso: Guardian colorea sin notificar."))
''')

# =====================================================================================
# 10. Casos, titular y rango plausible
# =====================================================================================
md(r'''
---
## 10. Caso, titular y rango plausible
**Necesidad de Shiro.** La prueba se mira una sola vez para decidir qué entra al MDP. Los casos, en orden:

- **C1:** ningún candidato pasó el piso → el elegido colorea sin notificar.
- **A:** elegido ≠ G0 y, en prueba, elegido − G0 ≥ 10 puntos con rango plausible (IC 95 %) > 0 → su probabilidad
  calibrada entra al MDP y dispara `ApprovalGate`.
- **C2:** elegido = G0 y G0 − complejo ≥ 10 puntos con IC > 0 (complejo = el mejor de los demás en validación) →
  Guardian despliega G0; lo complejo queda para el gemelo.
- **B:** cualquier otro → Guardian usa el elegido y se declara si la prueba favorece a otro.

**Rango plausible:** bootstrap pareado por día (2.000 réplicas, semilla 42): se remuestrean con reemplazo los días
calendario de la prueba (día del inicio de cada pico) y se recalcula la diferencia en % de picos con ≥ 20 min con el
marcado fijo de cada señal. **Titular:** el elegido desplegado (cortes de validación) y la regla de nivel con el mismo
tiempo en rojo realizado.
''')

code(r'''
DIAS_TEST = np.array(sorted(FECHA.iloc[cl:].dt.normalize().unique()))
def bootstrap_dif(ind1, ind2, ids, B=2000):
    dia_p = FECHA.iloc[S[ids]].dt.normalize().to_numpy()
    pos = np.searchsorted(DIAS_TEST, dia_p)
    assert (DIAS_TEST[pos] == dia_p).all()
    D = len(DIAS_TEST)
    n_d = np.bincount(pos, minlength=D)
    x1 = np.bincount(pos, weights=ind1.astype(float), minlength=D)
    x2 = np.bincount(pos, weights=ind2.astype(float), minlength=D)
    smp = np.random.RandomState(RS).randint(0, D, size=(B, D))
    d = (x1[smp].sum(1) - x2[smp].sum(1)) / n_d[smp].sum(1) * 100
    obs = (ind1.sum() - ind2.sum()) / len(ids) * 100
    lo, hi = np.percentile(d, [2.5, 97.5])
    return float(obs), float(lo), float(hi)

ind_te = {g: DET_[("prueba", g)]["ant"] >= 20 for g in SENALES}
p_te = {g: RES[("prueba", g)]["p20"] for g in CANDIDATOS}
# complejo = el mejor de los demás candidatos en validación; empate → el más simple (orden de CANDIDATOS)
COMPLEJO = max([g for g in CANDIDATOS if g != "G0"], key=lambda g: (RES[("val", g)]["p20"], -NIVEL[g], -CANDIDATOS.index(g)))
_emp = [g for g in CANDIDATOS if g not in ("G0", COMPLEJO) and RES[("val", g)]["p20"] == RES[("val", COMPLEJO)]["p20"]]
if _emp:
    print(f"Empate en validación entre {COMPLEJO} y {', '.join(_emp)} como 'complejo': se toma el más simple ({COMPLEJO}).")
    _alt = [bootstrap_dif(ind_te["G0"], ind_te[g], ids_te) if ELEG == "G0" else None for g in _emp]
    for g, a_ in zip(_emp, _alt):
        if a_ is not None:
            print(f"   con {g} como complejo la diferencia sería {num_es(a_[0])} puntos (IC {num_es(a_[1])} a {num_es(a_[2])})")
            registrar(f"caso_d_alt_{CLAVE[g]}", a_[0], "puntos", 1, "§10 Casos", f"Diferencia G0 − {g} (complejo alternativo por empate)")
if ELEG != "G0":
    par = (ELEG, "G0")
else:
    par = ("G0", COMPLEJO)
d_caso, lo_caso, hi_caso = bootstrap_dif(ind_te[par[0]], ind_te[par[1]], ids_te)
if not hay_piso:
    CASO = "C1"
elif ELEG != "G0":
    CASO = "A" if (d_caso >= MARGEN and lo_caso > 0) else "B"
else:
    CASO = "C2" if (d_caso >= MARGEN and lo_caso > 0) else "B"

# ¿La prueba favorece a otro candidato?
mejor_te = max(CANDIDATOS, key=lambda g: (p_te[g], -CANDIDATOS.index(g)))
otro = None
if mejor_te != ELEG and p_te[mejor_te] > p_te[ELEG]:
    otro = (mejor_te,) + bootstrap_dif(ind_te[mejor_te], ind_te[ELEG], ids_te)

# Titular: elegido desplegado y regla con el mismo tiempo en rojo realizado
MD = RES[("desp", ELEG)]
r_real = MD["rojo_pct"] / 100
M_REGLA, D_REGLA = evaluar(marcar_top(SCORE["regla"], cl, N, r_real), cl, N)
ind_desp = DET_[("desp", ELEG)]["ant"] >= 20
d_tit, lo_tit, hi_tit = bootstrap_dif(ind_desp, D_REGLA["ant"] >= 20, ids_te)
d_er, lo_er, hi_er = bootstrap_dif(ind_te[ELEG], ind_te["regla"], ids_te)   # mismo r en prueba

# Azar: marcar al azar una fracción f de la calma. Con f = r se compara con las señales al mismo r;
# con f = rojo realizado del elegido desplegado, con el titular y la regla al mismo rojo realizado.
idx_c = np.where(calma & test_m)[0]
def azar(frac):
    teo = (1 - (1 - frac) ** 2) * 100
    k_az = int(round(frac * len(idx_c)))
    rng_ = np.random.RandomState(RS); sims_ = []
    for _ in range(2000):
        rojo_az = np.zeros(N, bool); rojo_az[rng_.choice(idx_c, k_az, replace=False)] = True
        sims_.append((antelaciones(rojo_az, cl, N)[1] >= 20).mean() * 100)
    return teo, float(np.mean(sims_))
azar_teo, azar_sim = azar(r)
azar_teo_d, azar_sim_d = azar(r_real)

# Por lectura (para el póster y el Apéndice A): rojo del elegido desplegado frente a y_ant en la calma de prueba
mt_ = test_m & calma
y_l, rojo_l = y_ant[mt_], DET_[("desp", ELEG)]["rojo"][mt_]
LECT = {"exactitud": accuracy_score(y_l, rojo_l) * 100, "precision": precision_score(y_l, rojo_l, zero_division=0) * 100,
        "sensibilidad": recall_score(y_l, rojo_l) * 100, "f1": f1_score(y_l, rojo_l),
        "todo_verde_exactitud": (1 - y_l.mean()) * 100, "auc": roc_auc_score(y_l, SCORE[ELEG][mt_]),
        "auc_regla": roc_auc_score(y_l, SCORE["regla"][mt_])}

# Rango plausible por barra (Fig. 2): % de picos con ≥ 10/20/30 min, bootstrap por día
def bootstrap_prop(ind, ids, B=2000):
    obs, lo, hi = bootstrap_dif(ind, np.zeros(len(ind), bool), ids, B)
    return obs, lo, hi
FIG2 = {}
for et_, ant_ in (("elegido_desp", DET_[("desp", ELEG)]["ant"]), ("regla_mismo_rojo", D_REGLA["ant"])):
    for mm in (10, 20, 30):
        FIG2[(et_, mm)] = bootstrap_prop(ant_ >= mm, ids_te)

F10 = "§10 Casos"
k_el = NVARS[ELEG]
if CASO == "C1":
    solo_regla = all((not PISO[g]["supera_regla"]) and PISO[g]["p20_25"] and PISO[g]["utiles_33"] for g in CANDIDATOS)
    cond = ("ningún modelo superó a la regla de nivel" if solo_regla else
            f"ningún modelo reunió a la vez más picos que la regla, al menos el {num_es(PISO_P20, 0)} % de picos con "
            f"margen y al menos el {num_es(PISO_UTILES, 0)} % de avisos útiles")
    concl = "Los modelos no mejoran lo que el medidor ya da" if solo_regla else "Con estos sensores anticipar es difícil"
    FRASE = (f"En validación ningún modelo cumplió el piso ({cond}): el semáforo informa sin notificar; en prueba el "
             f"elegido avisó {MD['n20']} de {len(ids_te)}. → {concl}; falta saber qué aparato se enciende.")
elif CASO == "A":
    FRASE = (f"El {NOMBRE[ELEG]} avisa {num_es(d_caso)} picos más de cada 100 que el de dos variables. → Guardian puede "
             f"ser proactivo: su aviso entra al estado del MDP.")
elif CASO == "C2":
    FRASE = (f"El de dos variables avisa {num_es(d_caso)} picos más de cada 100 que el de {NVARS[COMPLEJO]} variables "
             f"({NOMBRE[COMPLEJO]}). → Más variables no ayudan a anticipar; la complejidad queda para el gemelo.")
else:
    if otro is not None and otro[2] > 0:   # la prueba favorece a otro candidato con IC > 0
        pre = (f"La prueba favorece al {NOMBRE[otro[0]]} por {num_es(otro[1])} de cada 100 picos, al revés que la validación")
    elif ELEG == "G0":
        pre = f"Con {len(ids_te)} picos, el de dos variables y el de {NVARS[COMPLEJO]} no se distinguen"
    else:
        pre = f"Con {len(ids_te)} picos, el de {k_el} variables y el de dos no se distinguen"
    FRASE = (f"{pre}: Guardian usa el {NOMBRE[ELEG]}, elegido en validación. → Avisar con margen es posible en "
             f"{pct_es(MD['p20'])} de los picos; el modelo se revalida con otra vivienda.")

registrar("caso_letra", CASO, "", 0, F10, "Caso del parcial (A, B, C1 o C2)")
registrar("caso_frase", FRASE, "", 0, F10, "Frase del caso (plantilla escrita de antemano, con cifras)")
registrar("caso_par", f"{par[0]} − {par[1]}", "", 0, F10, "Señales que compara la diferencia del caso")
registrar("caso_complejo", COMPLEJO, "", 0, F10, "Mejor candidato distinto de G0 en validación")
registrar("caso_d", d_caso, "puntos", 1, F10, "Diferencia del caso en % de picos con ≥ 20 min (prueba, mismo rojo)")
registrar("caso_ic_inf", lo_caso, "puntos", 1, F10, "Límite inferior del IC 95 % de la diferencia del caso")
registrar("caso_ic_sup", hi_caso, "puntos", 1, F10, "Límite superior del IC 95 % de la diferencia del caso")
registrar("caso_mejor_prueba", mejor_te, "", 0, F10, "Candidato con más picos a ≥ 20 min en prueba (mismo rojo)")
if otro is not None:
    registrar("caso_otro_d", otro[1], "puntos", 1, F10, f"Diferencia en prueba de {otro[0]} sobre el elegido (solo «favorece» si el IC 95 % inferior es > 0)")
    registrar("caso_otro_ic_inf", otro[2], "puntos", 1, F10, "IC 95 % inferior de esa ventaja")
    registrar("caso_otro_ic_sup", otro[3], "puntos", 1, F10, "IC 95 % superior de esa ventaja")
registrar("titular_n20", MD["n20"], "picos", 0, F10, "Picos avisados con ≥ 20 min por el elegido desplegado (de 84)")
registrar("titular_p20", MD["p20"], "%", 1, F10, "% de picos avisados con ≥ 20 min por el elegido desplegado")
registrar("titular_n10", MD["n10"], "picos", 0, F10, "Picos avisados con ≥ 10 min por el elegido desplegado")
registrar("titular_n30", MD["n30"], "picos", 0, F10, "Picos avisados con ≥ 30 min por el elegido desplegado")
registrar("titular_min_dia", MD["min_dia"], "min/día", 0, F10, "Minutos al día en rojo del elegido desplegado")
registrar("titular_rojo_pct", MD["rojo_pct"], "%", 2, F10, "% de la calma de prueba en rojo (realizado)")
registrar("titular_falsos", MD["falsos"], "%", 1, F10, "% de avisos falsos del elegido desplegado")
registrar("titular_avisos_dia", MD["avisos_dia"], "avisos/día", 2, F10, "Avisos por día del elegido desplegado")
registrar("titular_m20", M_REGLA["n20"], "picos", 0, F10, "Picos con ≥ 20 min de la regla de nivel al mismo rojo realizado")
registrar("titular_m20_pct", M_REGLA["p20"], "%", 1, F10, "% de picos con ≥ 20 min de la regla al mismo rojo realizado")
registrar("titular_m20_avisos_dia", M_REGLA["avisos_dia"], "avisos/día", 2, F10, "Avisos/día de la regla al mismo rojo realizado")
registrar("titular_m20_utiles", M_REGLA["utiles"], "%", 1, F10, "% de avisos útiles de la regla al mismo rojo realizado")
registrar("titular_d_regla", d_tit, "puntos", 1, F10, "Elegido desplegado − regla al mismo rojo (puntos, ≥ 20 min)")
registrar("titular_d_regla_ic_inf", lo_tit, "puntos", 1, F10, "IC 95 % inferior de esa diferencia")
registrar("titular_d_regla_ic_sup", hi_tit, "puntos", 1, F10, "IC 95 % superior de esa diferencia")
registrar("caso_d_regla_mismo_r", d_er, "puntos", 1, F10, "Elegido − regla en prueba con el mismo r (puntos)")
registrar("caso_d_regla_mismo_r_ic_inf", lo_er, "puntos", 1, F10, "IC 95 % inferior")
registrar("caso_d_regla_mismo_r_ic_sup", hi_er, "puntos", 1, F10, "IC 95 % superior")
registrar("titular_m10_pct", M_REGLA["p10"], "%", 1, F10, "% de picos con ≥ 10 min de la regla al mismo rojo realizado")
registrar("titular_m30_pct", M_REGLA["p30"], "%", 1, F10, "% de picos con ≥ 30 min de la regla al mismo rojo realizado")
registrar("titular_p10", MD["p10"], "%", 1, F10, "% de picos avisados con ≥ 10 min por el elegido desplegado")
registrar("titular_p30", MD["p30"], "%", 1, F10, "% de picos avisados con ≥ 30 min por el elegido desplegado")
registrar("azar_p20_teorico", azar_teo, "%", 1, F10,
          "% esperado de picos con ≥ 20 min marcando al azar el r de la calma (comparar con señales al mismo r)")
registrar("azar_p20_sim", azar_sim, "%", 1, F10,
          "Ídem por simulación (2.000 réplicas, semilla 42; incluye el pico no anticipable)")
registrar("azar_p20_desplegado", azar_teo_d, "%", 1, F10,
          "% esperado de picos con ≥ 20 min marcando al azar el rojo realizado del elegido desplegado "
          "(comparar con el titular y con la regla al mismo rojo realizado)")
registrar("azar_p20_desplegado_sim", azar_sim_d, "%", 1, F10, "Ídem por simulación (2.000 réplicas, semilla 42)")
FL = "§10 Por lectura"
registrar("lect_elegido_exactitud", LECT["exactitud"], "%", 1, FL,
          "Exactitud por lectura del elegido desplegado (rojo frente a 'precede un pico', calma de prueba)")
registrar("lect_elegido_precision", LECT["precision"], "%", 1, FL, "Precisión por lectura del rojo del elegido desplegado")
registrar("lect_elegido_sensibilidad", LECT["sensibilidad"], "%", 1, FL,
          "Sensibilidad por lectura: % de lecturas previas a un pico que el elegido desplegado pinta de rojo")
registrar("lect_elegido_f1", LECT["f1"], "", 2, FL, "F1 por lectura del elegido desplegado (etiqueta: precede un pico)")
registrar("lect_todo_verde_exactitud", LECT["todo_verde_exactitud"], "%", 1, FL,
          "Exactitud de pintar todo de verde (F1 = 0) en la calma de prueba")
registrar("lect_elegido_auc", LECT["auc"], "", 3, FL,
          "Probabilidad de que un momento previo a un pico puntúe más que uno tranquilo (AUC del elegido, calma de prueba)")
registrar("lect_regla_auc", LECT["auc_regla"], "", 3, FL, "Ídem para la regla de nivel")
for (et_, mm), (o_, lo_, hi_) in FIG2.items():
    registrar(f"fig2_{et_}_p{mm}", o_, "%", 1, F10, f"% de picos con ≥ {mm} min · {et_.replace('_', ' ')}")
    registrar(f"fig2_{et_}_p{mm}_ic_inf", lo_, "%", 1, F10, f"IC 95 % inferior (bootstrap por día) · ≥ {mm} min · {et_.replace('_', ' ')}")
    registrar(f"fig2_{et_}_p{mm}_ic_sup", hi_, "%", 1, F10, f"IC 95 % superior (bootstrap por día) · ≥ {mm} min · {et_.replace('_', ' ')}")

print(f"Caso {CASO} · diferencia {par[0]} − {par[1]} = {num_es(d_caso)} puntos (IC 95 % {num_es(lo_caso)} a {num_es(hi_caso)})")
if otro is not None:
    if otro[2] > 0:
        print(f"La prueba favorece a {otro[0]}: +{num_es(otro[1])} puntos sobre {ELEG} (IC {num_es(otro[2])} a {num_es(otro[3])})")
    else:
        print(f"En prueba {otro[0]} queda {num_es(otro[1])} puntos por encima de {ELEG}, sin distinguirse "
              f"(IC {num_es(otro[2])} a {num_es(otro[3])})")
print(f"Titular: {MD['n20']} de {len(ids_te)} picos ({pct_es(MD['p20'])}) con ≥ 20 min, {num_es(MD['min_dia'], 0)} min/día en rojo, "
      f"{pct_es(MD['falsos'])} de avisos falsos · regla al mismo rojo: {M_REGLA['n20']} ({pct_es(M_REGLA['p20'])}); "
      f"diferencia {num_es(d_tit)} (IC {num_es(lo_tit)} a {num_es(hi_tit)})")
print(f"{ELEG} − regla con el mismo r en prueba: {num_es(d_er)} puntos (IC {num_es(lo_er)} a {num_es(hi_er)})")
print(f"Azar al mismo r ({pct_es(r * 100, 2)}): {pct_es(azar_teo)} teórico · {pct_es(azar_sim)} simulado · "
      f"al rojo realizado del titular ({pct_es(r_real * 100, 2)}): {pct_es(azar_teo_d)} teórico · {pct_es(azar_sim_d)} simulado")
print(f"Por lectura (calma de prueba, etiqueta 'precede un pico'): exactitud {pct_es(LECT['exactitud'])} frente a "
      f"{pct_es(LECT['todo_verde_exactitud'])} de 'todo verde'; precisión {pct_es(LECT['precision'])}, sensibilidad "
      f"{pct_es(LECT['sensibilidad'])}, F1 {num_es(LECT['f1'], 2)}; AUC {num_es(LECT['auc'], 3)} (regla {num_es(LECT['auc_regla'], 3)}).")
print("Rango plausible por umbral de antelación (bootstrap por día): " + " · ".join(
    f"≥ {mm} min: elegido {pct_es(FIG2[('elegido_desp', mm)][0])} ({num_es(FIG2[('elegido_desp', mm)][1])}–"
    f"{num_es(FIG2[('elegido_desp', mm)][2])}), regla {pct_es(FIG2[('regla_mismo_rojo', mm)][0])} "
    f"({num_es(FIG2[('regla_mismo_rojo', mm)][1])}–{num_es(FIG2[('regla_mismo_rojo', mm)][2])})" for mm in (10, 20, 30)))
print("Regla de redacción del caso B: se usa la variante 'la prueba favorece a …' solo si la ventaja de otro candidato "
      "en prueba tiene IC 95 % por encima de 0; si no, 'no se distinguen'.")
print(FRASE)
if CASO == "C1":
    efecto = f"Guardian colorea con {ELEG} sin notificar; 'aplazar' solo se evalúa en los picos avisados."
else:
    efecto = (f"Guardian despliega {ELEG}: su probabilidad calibrada (sección 11) entra al estado del MDP y, como pasó el "
              f"piso, el rojo dispara la propuesta en ApprovalGate. ")
que_cambia(efecto + FRASE.split("→")[-1].strip())
''')

md(r'''
### 10.1 Ruido de semilla de los bosques
**Necesidad de Guardian.** G1 y G4 son bosques: su puntaje depende de la semilla. La decisión se tomó con la semilla 42,
fijada de antemano; aquí se mide cuánto se mueve su % de picos con ≥ 20 min en validación (mismo tiempo en rojo) con las
semillas 42 a 46 y si alguna cambiaría el elegido o el "complejo" contra el que se mide G0. La decisión no se rehace:
si una semilla la cambiara, se reporta.
''')

code(r'''
SEMILLAS = [42, 43, 44, 45, 46]
RUIDO = {"G1": [], "G4": []}
RUIDO_TE = {"G1": [], "G4": []}
CAMBIOS = []
for sem in SEMILLAS:
    if sem == RS:
        sc_sem = {"G1": SCORE["G1"], "G4": SCORE["G4"]}
    else:
        g1_ = RandomForestClassifier(n_estimators=200, random_state=sem, n_jobs=-1).fit(XO[fit_m], alta[fit_m])
        g4_ = RandomForestClassifier(n_estimators=200, random_state=sem, n_jobs=-1).fit(XS[M_FIT], y_ant[M_FIT])
        sc_sem = {"G1": g1_.predict_proba(XS)[:, 1], "G4": g4_.predict_proba(XS)[:, 1]}
    val_sem = {g: RES[("val", g)] for g in CANDIDATOS}
    det_te_sem = {}
    for g in ("G1", "G4"):
        m_v, _ = evaluar(marcar_top(sc_sem[g], n_fit, cl, r), n_fit, cl)
        m_t, d_t = evaluar(marcar_top(sc_sem[g], cl, N, r), cl, N)
        val_sem[g] = m_v; det_te_sem[g] = d_t
        RUIDO[g].append(m_v["p20"]); RUIDO_TE[g].append(m_t["p20"])
    # selección y complejo con esta semilla (mismas reglas que las secciones 9 y 10)
    pasa_ = [g for g in CANDIDATOS if val_sem[g]["p20"] > reg_val and val_sem[g]["p20"] >= PISO_P20
             and val_sem[g]["utiles"] >= PISO_UTILES]
    pool_ = pasa_ if pasa_ else CANDIDATOS
    mejor_ = max(val_sem[g]["p20"] for g in pool_)
    cerca_ = [g for g in pool_ if mejor_ - val_sem[g]["p20"] < MARGEN]
    nmin_ = min(NIVEL[g] for g in cerca_)
    eleg_ = max([g for g in cerca_ if NIVEL[g] == nmin_], key=lambda g: (val_sem[g]["p20"], -CANDIDATOS.index(g)))
    comp_ = max([g for g in CANDIDATOS if g != "G0"], key=lambda g: (val_sem[g]["p20"], -NIVEL[g], -CANDIDATOS.index(g)))
    fila_ = {"semilla": sem, "G1 val": val_sem["G1"]["p20"], "G4 val": val_sem["G4"]["p20"],
             "G1 prueba": RUIDO_TE["G1"][-1], "G4 prueba": RUIDO_TE["G4"][-1], "pasan el piso": " ".join(pasa_),
             "elegido": eleg_, "complejo": comp_}
    if comp_ in ("G1", "G4") and eleg_ == "G0":
        d_, lo_, hi_ = bootstrap_dif(ind_te["G0"], det_te_sem[comp_]["ant"] >= 20, ids_te)
        fila_.update({"d G0 − complejo": d_, "IC inf": lo_, "IC sup": hi_})
    CAMBIOS.append(fila_)
TR = pd.DataFrame(CAMBIOS).set_index("semilla")
print(tabla_es(TR, 1))
F101 = "§10.1 Ruido de semilla"
for g in ("G1", "G4"):
    for et_, lst_ in (("val", RUIDO[g]), ("prueba", RUIDO_TE[g])):
        registrar(f"semillas_{CLAVE[g]}_{et_}_p20_media", float(np.mean(lst_)), "%", 1, F101,
                  f"Media del % de picos con ≥ 20 min ({'validación' if et_ == 'val' else 'prueba'}, mismo rojo) de {NOMBRE[g]}, semillas 42–46")
        registrar(f"semillas_{CLAVE[g]}_{et_}_p20_min", float(np.min(lst_)), "%", 1, F101, f"Mínimo de lo anterior · {NOMBRE[g]}")
        registrar(f"semillas_{CLAVE[g]}_{et_}_p20_max", float(np.max(lst_)), "%", 1, F101, f"Máximo de lo anterior · {NOMBRE[g]}")
n_eleg_cambia = int((TR["elegido"] != ELEG).sum())
n_comp_cambia = int((TR["complejo"] != COMPLEJO).sum())
registrar("semillas_n", len(SEMILLAS), "", 0, F101, "Semillas probadas para los bosques (42–46)")
registrar("semillas_elegido_cambia_n", n_eleg_cambia, "", 0, F101, "Semillas con las que cambiaría el modelo elegido")
registrar("semillas_complejo_cambia_n", n_comp_cambia, "", 0, F101, "Semillas con las que cambiaría el 'complejo' del caso")
n_piso_cambia = int((TR["pasan el piso"] != " ".join(pasan)).sum())
registrar("semillas_piso_cambia_n", n_piso_cambia, "", 0, F101,
          "Semillas con las que cambiaría el conjunto de candidatos que pasan el piso (sin cambiar el elegido)")
alt_ = TR[TR["complejo"] != COMPLEJO]
if len(alt_) and "d G0 − complejo" in alt_:
    alt_ = alt_.dropna(subset=["d G0 − complejo"])
    registrar("semillas_d_alt_min", float(alt_["d G0 − complejo"].min()), "puntos", 1, F101,
              "Con las semillas que cambian el complejo a un bosque: mínima diferencia G0 − complejo en prueba")
    registrar("semillas_d_alt_max", float(alt_["d G0 − complejo"].max()), "puntos", 1, F101,
              "Ídem, máxima diferencia")
    registrar("semillas_ic_alt_inf_min", float(alt_["IC inf"].min()), "puntos", 1, F101,
              "Ídem, menor límite inferior del IC 95 % de esa diferencia")
    registrar("semillas_ic_alt_sup_max", float(alt_["IC sup"].max()), "puntos", 1, F101,
              "Ídem, mayor límite superior del IC 95 % de esa diferencia")
    casos_alt = ["C2" if (row["d G0 − complejo"] >= MARGEN and row["IC inf"] > 0) else "B" for _, row in alt_.iterrows()]
    registrar("semillas_caso_alt", ", ".join(sorted(set(casos_alt))), "", 0, F101,
              "Caso que saldría con las semillas que cambian el complejo")
else:
    casos_alt = []
LINEA_SEMILLAS = (
    f"Con las semillas 42–46, G1 logra en validación entre {num_es(min(RUIDO['G1']))} y {num_es(max(RUIDO['G1']))} % de "
    f"picos con ≥ 20 min (media {num_es(np.mean(RUIDO['G1']))}) y G4 entre {num_es(min(RUIDO['G4']))} y "
    f"{num_es(max(RUIDO['G4']))} % (media {num_es(np.mean(RUIDO['G4']))}); el elegido "
    + ("no cambia con ninguna semilla" if n_eleg_cambia == 0 else f"CAMBIARÍA con {n_eleg_cambia} de {len(SEMILLAS)} semillas")
    + ("" if n_piso_cambia == 0 else
       f" (con {n_piso_cambia} de {len(SEMILLAS)} semillas cambia quién pasa el piso: " +
       "; ".join(f"semilla {i_}: {v_}" for i_, v_ in TR["pasan el piso"].items() if v_ != " ".join(pasan)) + ")")
    + "; el complejo del caso "
    + ("tampoco cambia." if n_comp_cambia == 0 else
       f"pasaría de {COMPLEJO} a un bosque con {n_comp_cambia} de {len(SEMILLAS)} semillas"
       + (f" y el caso seguiría siendo {', '.join(sorted(set(casos_alt)))}" if casos_alt else "") + "."))
print("\n" + LINEA_SEMILLAS)
registrar("semillas_linea", LINEA_SEMILLAS, "", 0, F101, "Declaración del ruido de semilla de los bosques")
que_cambia(f"la decisión tomada con la semilla 42 se mantiene: Guardian sigue con {NOMBRE[ELEG]} y la variación de los "
           f"bosques se declara junto a sus cifras." if n_eleg_cambia == 0 else
           "la elección depende de la semilla de los bosques; se reporta sin rehacer la decisión tomada con la semilla 42.")
''')

# =====================================================================================
# 11. Calibración
# =====================================================================================
md(r'''
---
## 11. Calibración del elegido
**Necesidad de Shiro.** El MDP no puede recibir un puntaje arbitrario: necesita algo con significado, "de cada 100
momentos así, X precedieron un pico". Se calcula por deciles del puntaje en la calma de validación (purgada) y se
contrasta con lo que pasó en prueba con los mismos bordes.

**Empates.** Si el puntaje es discreto (G0 suma dos percentiles de tablas con muchos valores repetidos), los "deciles"
no tienen el mismo tamaño y su tasa depende de la convención de empates (aquí: decil = número de bordes ≤ puntaje). Por
eso se muestra el *n* de cada tramo junto a su tasa y, para el MDP, se usa la versión **monótona** de las tasas de
validación (tramos contiguos que violan el orden se fusionan, ponderando por *n*: regresión isotónica sobre los
tramos). La tasa de prueba es solo contraste: Guardian, al desplegarse, solo conoce la de validación.
''')

code(r'''
val_p = val_m & calma & purga
sc_v, ya_v = SCORE[ELEG][val_p], y_ant[val_p]
BORDES = np.unique(np.quantile(sc_v, np.linspace(.1, .9, 9)))
dec_v = np.searchsorted(BORDES, sc_v, side="right")
sc_t, ya_t = SCORE[ELEG][test_m & calma], y_ant[test_m & calma]
dec_t = np.searchsorted(BORDES, sc_t, side="right")
CAL = pd.DataFrame({"n_val": np.bincount(dec_v, minlength=len(BORDES) + 1),
                    "tasa_val": [ya_v[dec_v == k].mean() * 100 if (dec_v == k).any() else 0.0 for k in range(len(BORDES) + 1)],
                    "n_prueba": np.bincount(dec_t, minlength=len(BORDES) + 1),
                    "tasa_prueba": [ya_t[dec_t == k].mean() * 100 if (dec_t == k).any() else 0.0 for k in range(len(BORDES) + 1)]})
CAL.index = [f"decil {k + 1}" for k in range(len(CAL))]

def pav(tasas, pesos):
    """Regresión isotónica (no decreciente) sobre tramos: fusiona contiguos que violan el orden, ponderando por n."""
    bloques = []                                      # [suma ponderada, peso, n_tramos]
    for t_, w_ in zip(tasas, pesos):
        bloques.append([t_ * w_, w_, 1])
        while len(bloques) > 1 and bloques[-2][0] / bloques[-2][1] > bloques[-1][0] / bloques[-1][1]:
            b2 = bloques.pop(); bloques[-1] = [bloques[-1][0] + b2[0], bloques[-1][1] + b2[1], bloques[-1][2] + b2[2]]
    out = []
    for s_, w_, k_ in bloques:
        out += [s_ / w_] * k_
    return np.array(out)
CAL["tasa_mdp"] = pav(CAL["tasa_val"].to_numpy(), CAL["n_val"].to_numpy().astype(float))
print(f"Bordes (puntaje de {ELEG}): " + " · ".join(num_es(b_, 3) for b_ in BORDES))
print(tabla_es(CAL, 1))
print(f"Tamaño de los tramos en validación: de {CAL['n_val'].min()} a {CAL['n_val'].max()} lecturas (empates del puntaje). "
      f"Tramos con tasa de validación no monótona: {int((np.diff(CAL['tasa_val'].to_numpy()) < 0).sum())}; "
      f"la columna tasa_mdp los fusiona.")
for k in range(len(CAL)):
    registrar(f"cal_decil{k + 1}_tasa_val", CAL["tasa_val"].iloc[k], "%", 1, "§11 Calibración",
              f"De cada 100 momentos del decil {k + 1} (validación), cuántos precedieron un pico")
    registrar(f"cal_decil{k + 1}_tasa_prueba", CAL["tasa_prueba"].iloc[k], "%", 1, "§11 Calibración",
              f"Ídem en prueba con los bordes de validación (contraste)")
    registrar(f"cal_decil{k + 1}_tasa_mdp", CAL["tasa_mdp"].iloc[k], "%", 1, "§11 Calibración",
              f"Tasa monótona (isotónica por tramos, validación) del decil {k + 1}: la que entra al MDP")
    registrar(f"cal_decil{k + 1}_n_val", int(CAL["n_val"].iloc[k]), "lecturas", 0, "§11 Calibración",
              f"Lecturas de validación en el decil {k + 1}")
    registrar(f"cal_decil{k + 1}_n_prueba", int(CAL["n_prueba"].iloc[k]), "lecturas", 0, "§11 Calibración",
              f"Lecturas de prueba en el decil {k + 1}")
# Optimismo de la validación: en los deciles donde la tasa que se muestra (tasa_mdp) y la de prueba difieren más de
# UMBRAL_RANGO puntos, la página muestra el rango [prueba, validación] en vez de una sola cifra.
UMBRAL_RANGO = 5.0
CAL["dif_mdp_prueba"] = CAL["tasa_mdp"] - CAL["tasa_prueba"]
RANGO_CAL = [[float(CAL["tasa_prueba"].iloc[k]), float(CAL["tasa_mdp"].iloc[k])]
             if abs(CAL["dif_mdp_prueba"].iloc[k]) > UMBRAL_RANGO else None for k in range(len(CAL))]
dec_rango = [k + 1 for k, x in enumerate(RANGO_CAL) if x is not None]
k_opt = int(np.argmax(CAL["dif_mdp_prueba"].to_numpy()))
print(f"Deciles con más de {num_es(UMBRAL_RANGO, 0)} puntos entre validación (monótona) y prueba: "
      + (", ".join(f"decil {k} ({num_es(CAL['tasa_prueba'].iloc[k - 1], 1)} en prueba frente a "
                   f"{num_es(CAL['tasa_mdp'].iloc[k - 1], 1)} en validación)" for k in dec_rango) if dec_rango else "ninguno")
      + f". Mayor optimismo: decil {k_opt + 1}, {num_es(CAL['dif_mdp_prueba'].iloc[k_opt], 1)} puntos.")
for k in range(len(CAL)):
    registrar(f"cal_decil{k + 1}_dif_mdp_prueba", float(CAL["dif_mdp_prueba"].iloc[k]), "puntos", 1, "§11 Calibración",
              f"Tasa monótona de validación − tasa de prueba en el decil {k + 1} (positivo = la validación es optimista)")
registrar("cal_umbral_rango", UMBRAL_RANGO, "puntos", 0, "§11 Calibración",
          "Diferencia validación − prueba a partir de la cual la página muestra el rango [prueba, validación]")
registrar("cal_deciles_con_rango", ", ".join(str(k) for k in dec_rango) if dec_rango else "ninguno", "", 0, "§11 Calibración",
          "Deciles donde la página muestra el rango [prueba, validación] (diferencia mayor que el umbral)")
registrar("cal_optimismo_max", float(CAL["dif_mdp_prueba"].iloc[k_opt]), "puntos", 1, "§11 Calibración",
          "Mayor optimismo de la validación (tasa monótona − tasa de prueba) entre deciles")
registrar("cal_optimismo_max_decil", k_opt + 1, "", 0, "§11 Calibración", "Decil con el mayor optimismo de la validación")
registrar("cal_n_bins", len(CAL), "", 0, "§11 Calibración", "Número de deciles distintos (bordes únicos)")
registrar("cal_para_mdp", "validación, versión monótona (tasa_mdp)", "", 0, "§11 Calibración",
          "Qué tasa usar como 'de cada 100 momentos así': la de validación hecha monótona; la de prueba es contraste")
que_cambia(f"en el decil más alto de {ELEG}, de cada 100 momentos {num_es(CAL['tasa_mdp'].iloc[-1], 0)} precedieron un pico "
           f"en validación ({num_es(CAL['tasa_prueba'].iloc[-1], 0)} en prueba"
           f"{': la validación es optimista' if CAL['tasa_prueba'].iloc[-1] < CAL['tasa_mdp'].iloc[-1] else ''}), frente a "
           f"{num_es(CAL['tasa_mdp'].iloc[0], 0)} en el más bajo: esa tasa monótona, no el puntaje crudo, es la "
           f"probabilidad que entra al estado del MDP, y se recalibra cada mes.")
''')

# =====================================================================================
# 12. Explicador
# =====================================================================================
md(r'''
---
## 12. Explicador (N1e): reglas que la persona puede leer
**Necesidad de Guardian.** Cuando el semáforo se pone en rojo, la capa de explicación tiene que decir *por qué* en
términos del hogar. Un árbol de profundidad 3 imita el rojo del elegido (puntaje ≥ corte rojo) en la calma de *fit*
(purgada), con variables en lenguaje llano. Si el elegido fuera un bosque, se imitarían sus puntajes fuera de bolsa
para no copiar su sobreajuste. Se mide la **fidelidad** en prueba: cuánto coincide el árbol con el rojo real del
elegido y qué precisión tiene su rojo.
''')

code(r'''
LLANO = {"lag1": "consumo actual (Wh)", "lag2": "consumo de hace 10 min (Wh)", "lag3": "consumo de hace 20 min (Wh)",
         "lag6": "consumo de hace 50 min (Wh)", "media_1h": "consumo medio de la última hora (Wh)",
         "max_1h": "consumo máximo de la última hora (Wh)", "std_1h": "variabilidad del consumo en la última hora (Wh)",
         "hora": "hora del día", "dia_semana": "día de la semana (0 = lunes)", "es_fin_semana": "fin de semana (1 = sí)",
         "mes": "mes", "lights": "consumo de luces (Wh)", "T1": "temperatura de la cocina (°C)",
         "T2": "temperatura de la sala (°C)", "T3": "temperatura del lavadero (°C)", "T4": "temperatura de la oficina (°C)",
         "T5": "temperatura del baño (°C)", "T6": "temperatura exterior del edificio (°C)",
         "T7": "temperatura del cuarto de planchar (°C)", "T8": "temperatura del cuarto del adolescente (°C)",
         "T9": "temperatura del cuarto de los padres (°C)", "RH_1": "humedad de la cocina (%)", "RH_2": "humedad de la sala (%)",
         "RH_3": "humedad del lavadero (%)", "RH_4": "humedad de la oficina (%)", "RH_5": "humedad del baño (%)",
         "RH_6": "humedad exterior del edificio (%)", "RH_7": "humedad del cuarto de planchar (%)",
         "RH_8": "humedad del cuarto del adolescente (%)", "RH_9": "humedad del cuarto de los padres (%)",
         "T_out": "temperatura exterior (°C)", "RH_out": "humedad exterior (%)", "Press_mm_hg": "presión (mm Hg)",
         "Windspeed": "viento (m/s)", "Visibility": "visibilidad (km)", "Tdewpoint": "punto de rocío (°C)",
         "freq_hora_pct": "frecuencia histórica de picos a esta hora (en laborable o en fin de semana, según el día) (%)"}
XE = XS.copy()
if ELEG == "G0":
    XE["freq_hora_pct"] = freq_t * 100      # en %: "de cada 100 momentos así, cuántos precedieron un pico"
cr_el, ca_el = CORTES[ELEG]
if ELEG in ("G1", "G4"):
    gem = RandomForestClassifier(n_estimators=200, random_state=RS, n_jobs=-1, oob_score=True)
    if ELEG == "G4":
        gem.fit(XS[M_FIT], y_ant[M_FIT]); punt_fit = gem.oob_decision_function_[:, 1]
    else:
        gem.fit(XO[fit_m], alta[fit_m]); punt_fit = gem.oob_decision_function_[:, 1][M_FIT[fit_m]]
        print("Aviso: G1 se entrena con el vector original; sus puntajes OOB son de la lectura t, no de t+1.")
    punt_fit = np.nan_to_num(punt_fit)
else:
    punt_fit = SCORE[ELEG][M_FIT]
rojo_fit = punt_fit >= cr_el
ARB = DecisionTreeClassifier(max_depth=3, random_state=RS).fit(XE[M_FIT], rojo_fit)
nombres_e = list(XE.columns)

def reglas_arbol(arb, nombres):
    t_ = arb.tree_; out = []
    def rec(nodo, conds):
        if t_.children_left[nodo] == -1:
            v_ = t_.value[nodo][0]; prop = float(v_[1] / v_.sum()) if len(v_) > 1 else 0.0
            out.append({"hoja": int(nodo), "condiciones": conds, "n": int(t_.n_node_samples[nodo]),
                        "prop_rojo": prop, "rojo": bool(arb.classes_[int(np.argmax(v_))])})
            return
        f_ = nombres[t_.feature[nodo]]; u_ = float(t_.threshold[nodo])
        rec(t_.children_left[nodo], conds + [(f_, "≤", u_)])
        rec(t_.children_right[nodo], conds + [(f_, ">", u_)])
    rec(0, [])
    return out

def condicion_llana(f_, op, u_):
    if f_ == "es_fin_semana":
        return "es fin de semana" if op == ">" else "es día laborable"
    nombre = LLANO.get(f_, f_)
    unidad = ""
    m_ = re.match(r"(.*) \(([^)]*)\)$", nombre)
    if m_ and "=" not in m_.group(2):
        nombre, unidad = m_.group(1), " " + m_.group(2)
    elif m_:
        nombre = m_.group(1)
    dec = 3 if abs(u_) < 1 else 1
    return f"{nombre} {op} {num_es(u_, dec)}{unidad}"

def texto_regla(rg):
    # Une las condiciones repetidas de una misma variable en su intervalo más estrecho
    lim = {}
    for f_, op, u_ in rg["condiciones"]:
        lo_, hi_ = lim.get(f_, (-np.inf, np.inf))
        lim[f_] = (max(lo_, u_), hi_) if op == ">" else (lo_, min(hi_, u_))
    partes = []
    for f_, (lo_, hi_) in lim.items():
        if np.isfinite(lo_) and np.isfinite(hi_):
            a_, b_ = condicion_llana(f_, ">", lo_), condicion_llana(f_, "≤", hi_)
            partes.append(a_ + " y ≤ " + b_.split(" ≤ ")[1])
        elif np.isfinite(lo_):
            partes.append(condicion_llana(f_, ">", lo_))
        else:
            partes.append(condicion_llana(f_, "≤", hi_))
    color = "ROJO" if rg["rojo"] else "no rojo"
    return (f"SI {' y '.join(partes)} → {color} (en el entrenamiento, {num_es(rg['prop_rojo'] * 100, 0)} de cada 100 momentos "
            f"así estaban en rojo; {num_es(rg['n'], 0)} momentos)")

REGLAS = reglas_arbol(ARB, nombres_e)
for rg in REGLAS:
    rg["texto"] = texto_regla(rg)
HOJA_TXT = {rg["hoja"]: rg["texto"] for rg in REGLAS}
# coherencia del extractor con predict
assert (np.array([{rg["hoja"]: rg["rojo"] for rg in REGLAS}[h] for h in ARB.apply(XE[M_FIT])]) == ARB.predict(XE[M_FIT])).all()

mt = test_m & calma
pred_arb_t = ARB.predict(XE[mt]).astype(bool)
rojo_el_t = DET_[("desp", ELEG)]["rojo"][mt]
fid = (pred_arb_t == rojo_el_t).mean() * 100
prec_arb = rojo_el_t[pred_arb_t].mean() * 100 if pred_arb_t.any() else 0.0
acierto_arb = y_ant[mt][pred_arb_t].mean() * 100 if pred_arb_t.any() else 0.0
recall_arb = pred_arb_t[rojo_el_t].mean() * 100 if rojo_el_t.any() else 0.0
fid_fit = (ARB.predict(XE[M_FIT]) == rojo_fit).mean() * 100
F12 = "§12 Explicador"
registrar("expl_fidelidad", fid, "%", 1, F12, "Coincidencia rojo/no rojo del árbol con el elegido desplegado (calma de prueba)")
registrar("expl_precision", prec_arb, "%", 1, F12, "% del rojo del árbol que también es rojo del elegido (prueba)")
registrar("expl_cobertura", recall_arb, "%", 1, F12, "% del rojo del elegido que el árbol reproduce (prueba)")
registrar("expl_acierto", acierto_arb, "%", 1, F12, "% del rojo del árbol que precede un pico (prueba)")
registrar("expl_fidelidad_fit", fid_fit, "%", 1, F12, "Coincidencia del explicador con el rojo del elegido en los datos de entrenamiento de Guardian")
base_nunca = (~rojo_el_t).mean() * 100
registrar("expl_base_nunca_rojo", base_nunca, "%", 1, F12,
          "Coincidencia que lograría un explicador que nunca pinta rojo (línea base de la fidelidad, calma de prueba)")
registrar("expl_n_reglas_rojas", sum(rg["rojo"] for rg in REGLAS), "", 0, F12, "Hojas del árbol que dicen ROJO")
print("Reglas del explicador (profundidad 3):")
for rg in REGLAS:
    print("  " + rg["texto"])
print(f"\nFidelidad en la calma de prueba: {pct_es(fid)} de coincidencia (un explicador que nunca pinta rojo lograría "
      f"{pct_es(base_nunca)}) · precisión del rojo del árbol {pct_es(prec_arb)} · reproduce el {pct_es(recall_arb)} del "
      f"rojo del elegido · su rojo precede un pico el {pct_es(acierto_arb)} de las veces")
if ELEG == "G0":
    print("Nota: la variable de frecuencia del explicador está en % (0–100), igual que entradas.freq_hora_pct del mockup.")
que_cambia(f"la capa de explicación de Guardian puede mostrar {sum(rg['rojo'] for rg in REGLAS)} regla(s) de rojo en "
           f"lenguaje del hogar que reproducen el {pct_es(recall_arb)} del rojo real (coincidencia global "
           f"{pct_es(fid)}, frente a {pct_es(base_nunca)} de no pintar nunca rojo); donde no coinciden, manda el modelo y "
           f"la regla se rotula como aproximación.")
''')

# =====================================================================================
# 13. Energía y casos críticos
# =====================================================================================
md(r'''
---
## 13. Energía y casos críticos (N1f)
**Necesidad de Shiro.** La acción "aplazar" solo puede actuar sobre la energía de los picos que se avisaron con margen.
Se mide la energía del mes de prueba, la que cae dentro de picos y el **exceso sobre 200 Wh**, y cuánto de ese exceso
corresponde a picos avisados con ≥ 20 min por el elegido desplegado. Después, dos **casos críticos** elegidos por regla
(no a mano): el pico no anticipado con más energía y el aviso falso más largo.
''')

code(r'''
kwh_total = A[cl:].sum() / 1000
kwh_picos = A[cl:][en_pico[cl:]].sum() / 1000
exc_a = np.maximum(A[cl:] - UMBRAL, 0).sum() / 1000          # Σ max(A − 200, 0)
exc_b = A[cl:][A[cl:] > UMBRAL].sum() / 1000                 # Σ A[A > 200]
print(f"Energía de prueba {num_es(kwh_total)} kWh · dentro de los tramos de pico [s, e] {num_es(kwh_picos)} kWh "
      f"(incluye las lecturas ≤ 200 Wh entre lecturas altas de un mismo pico)")
print(f"Exceso: Σ max(A − 200, 0) = {num_es(exc_a)} kWh · Σ A[A > 200] = {num_es(exc_b)} kWh "
      f"→ el 'exceso sobre 200 Wh' es Σ max(A − 200, 0) y es el que se usa. "
      f"La 'energía de las lecturas altas' es Σ A[A > 200]; con los tramos [s, e] de la definición de pico son "
      f"{num_es(kwh_picos)} kWh.")
dd = DET_[("desp", ELEG)]
ids_d, ant_d = dd["ids"], dd["ant"]
ANT_DE = dict(zip(ids_d.tolist(), ant_d.tolist()))
def energia_pico(p):  # Wh del pico dentro de la prueba
    s, e = max(S[p], cl), E[p]
    return A[s:e + 1].sum()
def exceso_pico(p):
    s, e = max(S[p], cl), E[p]
    return np.maximum(A[s:e + 1] - UMBRAL, 0).sum()
exc_ant = sum(exceso_pico(p) for p in ids_d if ANT_DE[p] >= 20) / 1000
kwh_ant = sum(energia_pico(p) for p in ids_d if ANT_DE[p] >= 20) / 1000
F13 = "§13 Energía"
registrar("energia_prueba_kwh", kwh_total, "kWh", 1, F13, "Energía del mes de prueba (Σ A / 1000)")
registrar("energia_picos_kwh", kwh_picos, "kWh", 1, F13, "Energía dentro de picos en prueba")
registrar("energia_exceso_kwh", exc_a, "kWh", 1, F13, "Exceso sobre 200 Wh en prueba: Σ max(A − 200, 0) / 1000")
registrar("energia_sobre200_total_kwh", exc_b, "kWh", 1, F13, "Energía de las lecturas > 200 Wh: Σ A[A > 200] / 1000 (referencia)")
registrar("energia_exceso_anticipado_kwh", exc_ant, "kWh", 2, F13, "Exceso de los picos avisados con ≥ 20 min (elegido desplegado)")
registrar("energia_exceso_anticipado_pct", exc_ant / exc_a * 100, "%", 1, F13, "% del exceso que cae en picos avisados con ≥ 20 min")
registrar("energia_picos_anticipados_kwh", kwh_ant, "kWh", 1, F13, "Energía de los picos avisados con ≥ 20 min")
print(f"Exceso en picos avisados con ≥ 20 min: {num_es(exc_ant, 2)} kWh ({pct_es(exc_ant / exc_a * 100)} del exceso)")

# Colores desplegados del elegido en prueba
rojo_d = dd["rojo"]; am_d = calma & (SCORE[ELEG] >= CORTES[ELEG][1]) & ~rojo_d
COLOR = np.where(~calma, "rojo en curso", np.where(rojo_d, "rojo", np.where(am_d, "amarillo", "verde")))

def entradas(t):
    d_ = {c: float(XS.iloc[t][c]) for c in COLS}
    d_["freq_hora"] = float(freq_t[t]); d_["freq_hora_pct"] = float(freq_t[t] * 100); d_["celda"] = int(celda[t])
    if ELEG == "G0":
        d_["p_nivel"] = float(p_nivel[t]); d_["p_hora"] = float(p_hora[t])
    return d_

def momento(t, rotulo):
    expl_rojo = bool(ARB.predict(XE.iloc[[t]])[0])
    en_calma_ = bool(calma[t])
    coincide = (expl_rojo == (COLOR[t] == "rojo")) if en_calma_ else None
    return {"rotulo": rotulo, "indice_prueba": int(t - cl), "fecha": FECHA.iloc[t].isoformat(), "fecha_es": fecha_es(FECHA.iloc[t]),
            "wh": float(A[t]), "puntaje_elegido": float(SCORE[ELEG][t]), "puntaje_regla": float(SCORE["regla"][t]),
            "margen_corte_rojo": float(SCORE[ELEG][t] - CORTES[ELEG][0]),
            "margen_corte_amarillo": float(SCORE[ELEG][t] - CORTES[ELEG][1]),
            "color_esperado": str(COLOR[t]), "regla_explicador": HOJA_TXT[int(ARB.apply(XE.iloc[[t]])[0])],
            "explicador_rojo": expl_rojo, "explicador_coincide": coincide,
            "explicador_nota": ("pico en curso: el color lo da el medidor, el explicador no aplica" if not en_calma_ else
                                ("la regla coincide con el semáforo" if coincide else
                                 "aproximación: aquí el modelo manda (la regla del explicador no coincide con el color)")),
            "pronostico_g3c": float(G3C.predict(XS.iloc[[t]][SEIS])[0]),
            "decil_calibracion": int(np.searchsorted(BORDES, SCORE[ELEG][t], side="right")),
            "tasa_mdp": float(CAL["tasa_mdp"].iloc[int(np.searchsorted(BORDES, SCORE[ELEG][t], side="right"))]),
            "entradas": entradas(t)}

# Caso 1: pico NO anticipado (ninguna lectura en rojo en su ventana) con más energía, entre los anticipables
no_ant = [p for p in ids_d if ANT_DE[p] == 0 and S[p] - 3 >= cl]
p_c1 = sorted(no_ant, key=lambda p: (-energia_pico(p), S[p]))[0]
# Caso 2: aviso falso más largo (empate → el más temprano)
falsos = [x for x, u in zip(dd["avisos"], dd["util"]) if not u]
a_c2 = sorted(falsos, key=lambda x: (-len(x), x[0]))[0]
VENT_C1 = list(range(S[p_c1] - 3, S[p_c1]))
MARG_AM_C1 = [float(SCORE[ELEG][j] - CORTES[ELEG][1]) for j in VENT_C1]
FRAGIL_C1 = bool(min(abs(x) for x in MARG_AM_C1) < 0.01)
CASOS = {"pico_no_anticipado": {"inicio": FECHA.iloc[S[p_c1]].isoformat(), "fin": FECHA.iloc[E[p_c1]].isoformat(),
                                "energia_wh": float(energia_pico(p_c1)), "exceso_wh": float(exceso_pico(p_c1)),
                                "duracion_min": int((E[p_c1] - S[p_c1] + 1) * 10), "max_wh": float(A[S[p_c1]:E[p_c1] + 1].max()),
                                "puntajes_ventana": [float(SCORE[ELEG][j]) for j in VENT_C1],
                                "colores_ventana": [str(COLOR[j]) for j in VENT_C1],
                                "fechas_ventana": [FECHA.iloc[j].isoformat() for j in VENT_C1],
                                "margen_corte_amarillo": MARG_AM_C1, "margen_corte_rojo": [float(SCORE[ELEG][j] - CORTES[ELEG][0]) for j in VENT_C1],
                                "ventana_fragil": FRAGIL_C1,
                                "momento_narrativa": "s−2 (20 min antes del inicio)",
                                "nota_ventana": ("ventana [s−3, s−1]; margen = puntaje − corte. ventana_fragil = algún margen sobre el "
                                                 "corte amarillo menor que 0,01 en valor absoluto: ese color depende de un solo escalón "
                                                 "de las tablas de percentiles y no se narra como 'casi rojo'; la narrativa se ancla en s−2"),
                                "momento_20min_antes": momento(S[p_c1] - 2, "20 min antes del pico no anticipado")},
         "aviso_falso_largo": {"inicio": FECHA.iloc[a_c2[0]].isoformat(), "fin": FECHA.iloc[a_c2[-1]].isoformat(),
                               "lecturas_rojas": int(len(a_c2)), "duracion_min": int(len(a_c2) * 10),
                               "wh_max_durante": float(A[a_c2[0]:a_c2[-1] + 1].max()),
                               "momento_inicio": momento(a_c2[0], "primer rojo del aviso falso más largo")}}
c1_, c2_ = CASOS["pico_no_anticipado"], CASOS["aviso_falso_largo"]
registrar("caso1_inicio", c1_["inicio"], "fecha", 0, F13, "Caso crítico 1: inicio del pico no anticipado con más energía")
m1_ = c1_["momento_20min_antes"]
registrar("caso1_momento", m1_["fecha"], "fecha", 0, F13, "Caso crítico 1: momento descrito (20 min antes del inicio)")
registrar("caso1_puntaje", m1_["puntaje_elegido"], "", 3, F13, "Caso crítico 1: puntaje del elegido 20 min antes")
registrar("caso1_margen_amarillo", m1_["margen_corte_amarillo"], "", 3, F13, "Caso crítico 1: puntaje − corte amarillo, 20 min antes")
registrar("caso1_margen_rojo", m1_["margen_corte_rojo"], "", 3, F13, "Caso crítico 1: puntaje − corte rojo, 20 min antes")
registrar("caso1_color", m1_["color_esperado"], "", 0, F13, "Caso crítico 1: color del semáforo 20 min antes")
registrar("caso1_consumo_wh", m1_["entradas"]["lag1"], "Wh", 0, F13, "Caso crítico 1: consumo 20 min antes del inicio")
registrar("caso1_hora", int(m1_["entradas"]["hora"]), "", 0, F13, "Caso crítico 1: hora del día 20 min antes")
registrar("caso1_luces_wh", m1_["entradas"]["lights"], "Wh", 0, F13, "Caso crítico 1: consumo de luces 20 min antes")
for i_, (j_, mg_) in enumerate(zip(VENT_C1, MARG_AM_C1)):
    registrar(f"caso1_margen_amarillo_s{3 - i_}", mg_, "", 4, F13,
              f"Caso crítico 1: puntaje − corte amarillo en s−{3 - i_} ({FECHA.iloc[j_]:%H:%M})")
registrar("caso1_ventana_fragil", int(FRAGIL_C1), "", 0, F13,
          "Caso crítico 1: 1 si algún margen sobre el corte amarillo en [s−3, s−1] es menor que 0,01 (color frágil)")
registrar("caso1_narrativa_en", "s−2", "", 0, F13, "Caso crítico 1: momento en que se ancla la narrativa (20 min antes)")
registrar("caso1_energia_wh", c1_["energia_wh"], "Wh", 0, F13, "Caso crítico 1: energía del pico")
registrar("caso1_duracion_min", c1_["duracion_min"], "min", 0, F13, "Caso crítico 1: duración del pico")
registrar("caso1_max_wh", c1_["max_wh"], "Wh", 0, F13, "Caso crítico 1: lectura máxima")
registrar("caso1_wh_previo", float(A[S[p_c1] - 1]), "Wh", 0, F13, "Caso crítico 1: consumo 10 min antes del inicio")
registrar("caso2_inicio", c2_["inicio"], "fecha", 0, F13, "Caso crítico 2: inicio del aviso falso más largo")
m2_ = c2_["momento_inicio"]
registrar("caso2_puntaje", m2_["puntaje_elegido"], "", 3, F13, "Caso crítico 2: puntaje del elegido en el primer rojo")
registrar("caso2_margen_rojo", m2_["margen_corte_rojo"], "", 3, F13, "Caso crítico 2: puntaje − corte rojo en el primer rojo")
registrar("caso2_consumo_wh", m2_["entradas"]["lag1"], "Wh", 0, F13, "Caso crítico 2: consumo en el primer rojo")
registrar("caso2_hora", int(m2_["entradas"]["hora"]), "", 0, F13, "Caso crítico 2: hora del día en el primer rojo")
registrar("caso2_luces_wh", m2_["entradas"]["lights"], "Wh", 0, F13, "Caso crítico 2: consumo de luces en el primer rojo")
registrar("caso2_duracion_min", c2_["duracion_min"], "min", 0, F13, "Caso crítico 2: duración del aviso falso")
registrar("caso2_wh_max", c2_["wh_max_durante"], "Wh", 0, F13, "Caso crítico 2: consumo máximo durante el aviso")
print(f"\nCaso crítico 1 — pico no anticipado con más energía: {fecha_es(c1_['inicio'])} → {fecha_es(c1_['fin'])}, "
      f"{num_es(c1_['energia_wh'], 0)} Wh en {c1_['duracion_min']} min (máx. {num_es(c1_['max_wh'], 0)} Wh); "
      f"10 min antes el consumo era {num_es(A[S[p_c1] - 1], 0)} Wh; colores de la ventana: {', '.join(c1_['colores_ventana'])}")
m_ = c1_["momento_20min_antes"]["entradas"]
print(f"   entradas 20 min antes: consumo {num_es(m_['lag1'], 0)} Wh, hora {int(m_['hora'])}, luces {num_es(m_['lights'], 0)} Wh, "
      f"fin de semana {int(m_['es_fin_semana'])}, puntaje {num_es(c1_['momento_20min_antes']['puntaje_elegido'], 3)} "
      f"(margen sobre el corte amarillo {sig_es(m1_['margen_corte_amarillo'], 3)}; colores de la ventana por puntaje: "
      + ", ".join(f"{num_es(sc_, 4)} → {co_}" for sc_, co_ in zip(c1_["puntajes_ventana"], c1_["colores_ventana"]))
      + f"; corte amarillo {num_es(CORTES[ELEG][1], 4)})")
print("   Márgenes sobre el corte amarillo en la ventana: " + ", ".join(
    f"s−{3 - i_} ({FECHA.iloc[j_]:%H:%M}) {sig_es(mg_, 4)}" for i_, (j_, mg_) in enumerate(zip(VENT_C1, MARG_AM_C1))))
if FRAGIL_C1:
    print("   Ventana frágil: algún momento queda a menos de 0,01 del corte amarillo; su color depende de un solo escalón "
          "de la tabla de percentiles y no debe narrarse como 'casi rojo'. La narrativa del caso se ancla en s−2 "
          f"({FECHA.iloc[S[p_c1] - 2]:%H:%M}, margen {sig_es(MARG_AM_C1[1], 3)}).")
print(f"Caso crítico 2 — aviso falso más largo: {fecha_es(c2_['inicio'])} → {fecha_es(c2_['fin'])}, {c2_['duracion_min']} min en rojo "
      f"sin pico detrás (máx. {num_es(c2_['wh_max_durante'], 0)} Wh); puntaje inicial "
      f"{num_es(c2_['momento_inicio']['puntaje_elegido'], 3)}")
que_cambia(f"aplazar solo alcanza el exceso de los picos avisados con margen: {num_es(exc_ant, 2)} de {num_es(exc_a)} kWh "
           f"({pct_es(exc_ant / exc_a * 100)}) del mes; el resto del exceso llega sin aviso y el MDP no debe contar ese "
           f"ahorro. Los picos abruptos (como el caso 1) piden la variable que falta: qué aparato se enciende.")
''')

# =====================================================================================
# 14. Ejemplos para el mockup
# =====================================================================================
md(r'''
---
## 14. Ejemplos para el mockup (elegidos por regla)
**Necesidad de Guardian.** La página tiene que mostrar momentos reales, no escogidos a dedo. Reglas fijadas de antemano
(prueba; empate → el más temprano; "mediana" = mediana inferior):

- **Tarjeta 1 (5 momentos):** calma verde de puntaje mediano; primer rojo del aviso útil de antelación mediana; primer
  rojo del aviso falso más largo; 20 min antes del pico no anticipado con más energía; inicio del pico de energía mediana.
- **Tarjeta 4 (4 situaciones):** avisos útiles de mayor y de mediana antelación, falso más largo, no anticipado con más
  energía.
- **Día del antes/después:** entre los días con al menos tres picos, el de mediana en % de picos avisados con ≥ 20 min;
  la frase usa el pico de ese día con más antelación (empate → el más temprano).

**Dos medidas de tiempo en los avisos útiles.** La *antelación* se cuenta desde el primer rojo dentro de la ventana
[*s*−3, *s*−1] (como en la sección 8: nunca pasa de 30 min). Un aviso puede haber empezado antes de esa ventana; por eso
cada situación lleva también los minutos desde su primer rojo hasta el pico. La página no debe mostrar una cifra sin la
otra. En la situación del pico no anticipado se muestra el momento de 20 min antes del inicio (el mismo de la tarjeta 1),
con su puntaje y su margen sobre los cortes de color.
''')

code(r'''
def mediana_inf(valores):
    v_ = sorted(valores)
    return v_[(len(v_) - 1) // 2]

# 1) calma verde de puntaje mediano
verdes = np.where(test_m & (COLOR == "verde"))[0]
v_med = mediana_inf(SCORE[ELEG][verdes].tolist())
t1 = int(verdes[SCORE[ELEG][verdes] == v_med][0])
# Avisos útiles con su antelación
utiles = []
for x, u in zip(dd["avisos"], dd["util"]):
    if u:
        p_ = ventana_de[x][ventana_de[x] >= 0][0]
        utiles.append({"aviso": x, "pico": int(p_), "ant": int(ANT_DE[int(p_)])})
a_med = mediana_inf([u["ant"] for u in utiles])
u_med = sorted([u for u in utiles if u["ant"] == a_med], key=lambda u: u["aviso"][0])[0]
a_max = max(u["ant"] for u in utiles)
u_max = sorted([u for u in utiles if u["ant"] == a_max], key=lambda u: u["aviso"][0])[0]
# 5) inicio del pico de energía mediana (picos que empiezan en prueba)
ids_in = [p for p in ids_d if S[p] >= cl]
e_med = mediana_inf([energia_pico(p) for p in ids_in])
p_med = sorted([p for p in ids_in if energia_pico(p) == e_med], key=lambda p: S[p])[0]

MOMENTOS = [momento(t1, "calma verde de puntaje mediano"),
            momento(int(u_med["aviso"][0]), "primer rojo del aviso útil de antelación mediana"),
            momento(int(a_c2[0]), "primer rojo del aviso falso más largo"),
            momento(int(S[p_c1] - 2), "20 min antes del pico no anticipado con más energía"),
            momento(int(S[p_med]), "inicio del pico de energía mediana")]
# Rótulos para la página, en lenguaje llano (la franja sale de la hora de cada momento)
FRANJA_LLANA = lambda h_: franja(h_).split(" (")[0]
for m_, txt_ in zip(MOMENTOS, ["momento tranquilo (verde)", "primer rojo de un aviso útil", "rojo que resultó falsa alarma",
                               "20 min antes de un pico que nadie avisó", "pico ya en marcha (lo ve el medidor)"]):
    m_["rotulo_llano"] = f"{FRANJA_LLANA(int(m_['entradas']['hora']))}: {txt_}"

def tiempos_aviso(d_, x, p):
    """Las dos medidas de tiempo de un aviso útil (ver el texto de la sección)."""
    w_ = [j for j in range(max(S[p] - 3, cl), S[p]) if DET_[("desp", ELEG)]["rojo"][j]]
    d_.update({"antelacion_min": int(ANT_DE[p]), "min_desde_primer_rojo": int(S[p] - x[0]) * 10,
               "min_hasta_pico": int(S[p] - x[0]) * 10, "inicio_pico": FECHA.iloc[S[p]].isoformat(),
               "primer_rojo_aviso": FECHA.iloc[x[0]].isoformat(),
               "primer_rojo_en_ventana": FECHA.iloc[w_[0]].isoformat() if w_ else None,
               "nota_antelacion": (f"rojo desde {FECHA.iloc[x[0]]:%H:%M}; antelación contada desde el primer rojo dentro "
                                   f"de los 30 min previos al pico: {int(ANT_DE[p])} min; el pico llegó "
                                   f"{int(S[p] - x[0]) * 10} min después del primer rojo del aviso")})
    return d_

def situacion(tipo, x=None, p=None):
    if x is not None:
        d_ = momento(int(x[0]), tipo)
        d_.update({"duracion_min": int(len(x) * 10), "fin_aviso": FECHA.iloc[x[-1]].isoformat()})
        if p is not None:
            d_.update({"desenlace": f"pico a los {int(S[p] - x[0]) * 10} min", "energia_pico_wh": float(energia_pico(p))})
            tiempos_aviso(d_, x, p)
        else:
            d_.update({"desenlace": "falso: ningún pico en los 30 min siguientes"})
        return d_
    d_ = momento(int(S[p] - 2), tipo + " (20 min antes del inicio)")
    d_.update({"desenlace": "pico sin aviso", "inicio_pico": FECHA.iloc[S[p]].isoformat(), "antelacion_min": 0,
               "min_hasta_pico": 20, "energia_pico_wh": float(energia_pico(p))})
    return d_

# Si la antelación mediana coincide con la mayor, la regla "empate → el más temprano" devolvería el mismo aviso
# dos veces; en la tarjeta 4 la situación de mediana pasa al siguiente aviso útil con esa antelación (orden cronológico).
u_med4 = u_med
if u_med["aviso"][0] == u_max["aviso"][0]:
    sig_ = sorted([u for u in utiles if u["ant"] == a_med and u["aviso"][0] != u_max["aviso"][0]], key=lambda u: u["aviso"][0])
    if sig_:
        u_med4 = sig_[0]
    print(f"Nota: la antelación mediana de los avisos útiles ({a_med} min) es también la mayor; la tarjeta 4 toma el "
          f"siguiente aviso con esa antelación para no repetir la situación.")
SITUACIONES = [situacion("aviso útil de mayor antelación", u_max["aviso"], u_max["pico"]),
               situacion("aviso útil de antelación mediana", u_med4["aviso"], u_med4["pico"]),
               situacion("aviso falso más largo", a_c2),
               situacion("pico no anticipado con más energía", p=p_c1)]
tiempos_aviso(MOMENTOS[1], u_med["aviso"], u_med["pico"])
discord = [e_["fecha_es"] + " (" + e_["rotulo"] + ")" for e_ in MOMENTOS + SITUACIONES if e_["explicador_coincide"] is False]
registrar("expl_ejemplos_discordantes", len(discord), "", 0, "§14 Ejemplos",
          "Ejemplos del mockup (5 momentos + 4 situaciones) en calma donde la regla del explicador no coincide con el color")

# Día del antes/después
dia_de = FECHA.iloc[S[ids_d]].dt.normalize().to_numpy()
tab_dia = pd.DataFrame({"dia": dia_de, "ant20": ant_d >= 20}).groupby("dia").agg(picos=("ant20", "size"), pct=("ant20", "mean"))
cand = tab_dia[tab_dia.picos >= 3]
pct_med = mediana_inf(cand["pct"].tolist())
DIA = pd.Timestamp(sorted(cand.index[cand["pct"] == pct_med])[0])
idx_dia = np.where(test_m & (FECHA.dt.normalize() == DIA).to_numpy())[0]
picos_dia = []
for p in ids_d:
    if pd.Timestamp(FECHA.iloc[S[p]]).normalize() == DIA:
        w = [j for j in range(max(S[p] - 3, cl), S[p]) if rojo_d[j]]
        j0 = w[0] if w else None
        while j0 is not None and j0 - 1 >= cl and rojo_d[j0 - 1]:   # inicio de la racha roja continua
            j0 -= 1
        picos_dia.append({"inicio": FECHA.iloc[S[p]].isoformat(), "fin": FECHA.iloc[E[p]].isoformat(),
                          "antelacion_min": int(ANT_DE[p]), "primer_rojo": FECHA.iloc[w[0]].isoformat() if w else None,
                          "inicio_rojo": FECHA.iloc[j0].isoformat() if w else None,
                          "min_desde_inicio_rojo": int(S[p] - j0) * 10 if w else 0,
                          "energia_wh": float(energia_pico(p)), "exceso_wh": float(exceso_pico(p))})
DIA_AD = {"dia": DIA.date().isoformat(), "indice_inicio": int(idx_dia[0] - cl), "indice_fin": int(idx_dia[-1] - cl),
          "picos": picos_dia, "pct_anticipados": float(pct_med * 100), "n_dias_candidatos": int(len(cand))}
registrar("ejemplo_dia", DIA.date().isoformat(), "fecha", 0, "§14 Ejemplos", "Día del antes/después")
registrar("ejemplo_dia_picos", len(picos_dia), "picos", 0, "§14 Ejemplos", "Picos del día del antes/después")
registrar("ejemplo_dia_pct", pct_med * 100, "%", 0, "§14 Ejemplos", "% de picos del día avisados con ≥ 20 min")
# Pico del día para la frase "a las {hh:mm} el semáforo pasó a rojo, {k} min antes del pico"
con_rojo = [q for q in picos_dia if q["primer_rojo"]]
if con_rojo:
    q_ = sorted(con_rojo, key=lambda q: (-q["antelacion_min"], q["inicio"]))[0]
    DIA_AD["pico_frase"] = q_
    registrar("ejemplo_dia_primer_rojo", q_["primer_rojo"], "hora", 0, "§14 Ejemplos",
              "Primera lectura en rojo dentro de los 30 min previos al pico de más antelación del día (desde ella se "
              "cuenta la antelación, que nunca pasa de 30 min)")
    registrar("ejemplo_dia_inicio_rojo", q_["inicio_rojo"], "hora", 0, "§14 Ejemplos",
              "Inicio de la racha roja continua que precede a ese pico (puede empezar antes de la ventana de 30 min)")
    registrar("ejemplo_dia_min_desde_inicio_rojo", q_["min_desde_inicio_rojo"], "min", 0, "§14 Ejemplos",
              "Minutos entre el inicio de la racha roja y el inicio de ese pico")
    registrar("ejemplo_dia_pico", q_["inicio"], "hora", 0, "§14 Ejemplos", "Hora de inicio de ese pico")
    registrar("ejemplo_dia_antelacion_min", q_["antelacion_min"], "min", 0, "§14 Ejemplos",
              "Minutos entre el primer rojo de la ventana y el inicio de ese pico")
print("Tarjeta 1 — cinco momentos:")
for m_ in MOMENTOS:
    print(f"  {m_['fecha_es']:18s} {m_['color_esperado']:14s} consumo {num_es(m_['wh'], 0):>4s} Wh · puntaje "
          f"{num_es(m_['puntaje_elegido'], 3)} · {m_['rotulo']}")
print("Tarjeta 4 — cuatro situaciones:")
for s_ in SITUACIONES:
    print(f"  {s_['fecha_es']:18s} {s_['rotulo']:36s} → {s_['desenlace']}"
          + (f" · antelación (ventana) {s_['antelacion_min']} min, desde el primer rojo {s_['min_desde_primer_rojo']} min"
             if "min_desde_primer_rojo" in s_ else "")
          + f" · puntaje {num_es(s_['puntaje_elegido'], 3)} (margen sobre amarillo {sig_es(s_['margen_corte_amarillo'], 3)})")
print(f"Ejemplos donde la regla del explicador no coincide con el color: {len(discord)} de "
      f"{sum(e_['explicador_coincide'] is not None for e_ in MOMENTOS + SITUACIONES)} en calma"
      + (": " + "; ".join(discord) + " → la página los rotula como aproximación." if discord else "."))
print(f"Día del antes/después: {fecha_es(DIA).split(' ')[0]} ({len(picos_dia)} picos, {pct_es(pct_med * 100, 0)} avisados "
      f"con ≥ 20 min; mediana entre {len(cand)} días con ≥ 3 picos)")
for pd_ in picos_dia:
    print(f"   pico {fecha_es(pd_['inicio'])[-5:]} · antelación {pd_['antelacion_min']} min · primer rojo en la ventana "
          f"{fecha_es(pd_['primer_rojo'])[-5:] if pd_['primer_rojo'] else '—'} · en rojo desde "
          f"{fecha_es(pd_['inicio_rojo'])[-5:] if pd_['inicio_rojo'] else '—'}")
if con_rojo:
    print(f"Frase antes/después: el semáforo estaba en rojo desde las {fecha_es(q_['inicio_rojo'])[-5:]}, "
          f"{q_['min_desde_inicio_rojo']} min antes del pico de las {fecha_es(q_['inicio'])[-5:]} (antelación contada "
          f"en la ventana de 30 min: {q_['antelacion_min']} min).")
que_cambia("la página mostrará momentos reales del mes nunca visto, elegidos por regla, con el mismo color que les da "
           "el semáforo central: ninguna tarjeta puede contradecir a otra.")
''')

# =====================================================================================
# 15. Deriva y sensibilidad
# =====================================================================================
md(r'''
---
## 15. Deriva de cortes y sensibilidad al presupuesto
**Necesidad de Shiro.** Los cortes se fijaron con datos de abril y se aplican en mayo. Si el rojo realizado se aparta
del presupuesto, el semáforo molesta más (o menos) de lo pactado con la persona: es la señal para recalibrar cada mes
(hallazgo 13 del proyecto). Para los bosques se pone a prueba una explicación concreta (hallazgo 18 del proyecto: la
temperatura interior sube en mayo por encima de todo lo visto y los árboles no extrapolan): se reentrenan G1 y G4 sin
las temperaturas de las habitaciones y se mide de nuevo su rojo realizado. Además, ¿cambia la conclusión si el
presupuesto fuera 5 % o 10 %?
''')

code(r'''
def rojo_realizado_val(sg):
    v_ = SCORE[sg][calma & val_m]
    return (v_ >= CORTES[sg][0]).mean() * 100
der = pd.DataFrame({sg: {"rojo en validación %": rojo_realizado_val(sg), "rojo realizado prueba %": RES[("desp", sg)]["rojo_pct"],
                         "min/día": RES[("desp", sg)]["min_dia"], "≥ 20 min %": RES[("desp", sg)]["p20"]} for sg in SENALES}).T
print(f"Rojo con los cortes de validación (presupuesto {pct_es(r * 100, 2)}). La primera columna aísla el efecto de los "
      f"empates (puntajes discretos: 'rojo si puntaje ≥ corte'); la diferencia con la segunda es deriva de abril a mayo.")
print(tabla_es(der, 1))
for sg in SENALES:
    registrar(f"deriva_{CLAVE[sg]}_rojo_val", rojo_realizado_val(sg), "%", 2, "§15 Deriva",
              f"Rojo con su propio corte en la calma de validación (efecto de empates) · {NOMBRE[sg]}")
der = der.rename(columns={"rojo realizado prueba %": "rojo realizado %"})
peor = der["rojo realizado %"].idxmax()
registrar("deriva_rojo_min", der["rojo realizado %"].min(), "%", 1, "§15 Deriva", "Mínimo rojo realizado entre señales")
registrar("deriva_rojo_max", der["rojo realizado %"].max(), "%", 1, "§15 Deriva", "Máximo rojo realizado entre señales")

# ¿Explica la temperatura interior la deriva de los bosques? Reentrenar G1 y G4 sin T1–T9 (salvo T6, que mide fuera)
T_INT = [c for c in INTERIOR if c.startswith("T") and c != "T6"]
COLS_ST = [c for c in COLS if c not in T_INT]
SIN_T = {}
g1s = RandomForestClassifier(n_estimators=200, random_state=RS, n_jobs=-1).fit(XO[fit_m][COLS_ST], alta[fit_m])
g4s = RandomForestClassifier(n_estimators=200, random_state=RS, n_jobs=-1).fit(XS[M_FIT][COLS_ST], y_ant[M_FIT])
for sg, mod_ in (("G1", g1s), ("G4", g4s)):
    sc_ = mod_.predict_proba(XS[COLS_ST])[:, 1]
    cr_, _ = cortes_val(sc_, r)
    m_, _ = evaluar(calma & (sc_ >= cr_), cl, N)
    SIN_T[sg] = m_
    registrar(f"deriva_{CLAVE[sg]}_sin_tint_rojo", m_["rojo_pct"], "%", 1, "§15 Deriva",
              f"Rojo realizado en prueba de {NOMBRE[sg]} reentrenado sin las temperaturas de las habitaciones")
    registrar(f"deriva_{CLAVE[sg]}_sin_tint_p20", m_["p20"], "%", 1, "§15 Deriva",
              f"% de picos con ≥ 20 min (desplegado, no comparable) de {NOMBRE[sg]} sin temperaturas de las habitaciones")
print(f"\nSin las temperaturas de las habitaciones ({', '.join(T_INT)}): " + " · ".join(
    f"{sg} rojo realizado {pct_es(RES[('desp', sg)]['rojo_pct'])} → {pct_es(SIN_T[sg]['rojo_pct'])}" for sg in ("G1", "G4")))
baja_t = all(SIN_T[sg]["rojo_pct"] < RES[("desp", sg)]["rojo_pct"] / 2 for sg in ("G1", "G4"))
expl_bosques = ("al quitar las temperaturas de las habitaciones el rojo realizado de G1 baja de "
                f"{pct_es(RES[('desp', 'G1')]['rojo_pct'])} a {pct_es(SIN_T['G1']['rojo_pct'])} y el de G4 de "
                f"{pct_es(RES[('desp', 'G4')]['rojo_pct'])} a {pct_es(SIN_T['G4']['rojo_pct'])}, coherente con el "
                f"hallazgo 18 (temperatura interior fuera de rango y árboles que no extrapolan)" if baja_t else
                "quitar las temperaturas de las habitaciones no reduce a la mitad el rojo realizado de los bosques: la "
                "deriva no se explica solo por la temperatura interior")
SENS = {}
for frac in (0.05, 0.10):
    for sg in (ELEG, "regla"):
        m_, _ = evaluar(marcar_top(SCORE[sg], cl, N, frac), cl, N)
        SENS[(frac, sg)] = m_["p20"]
        registrar(f"sens_{int(frac * 100):02d}_{CLAVE[sg]}_p20" if sg == "regla" else f"sens_{int(frac * 100):02d}_elegido_p20",
                  m_["p20"], "%", 1, "§15 Sensibilidad", f"% de picos con ≥ 20 min con r = {int(frac * 100)} % · {NOMBRE[sg]}")
print("\nSensibilidad (prueba, mismo tiempo en rojo):")
for frac in (0.05, 0.10):
    print(f"  r = {int(frac * 100):2d} %: {ELEG} {pct_es(SENS[(frac, ELEG)])} · regla {pct_es(SENS[(frac, 'regla')])}")
que_cambia(f"con los cortes de abril el elegido pinta de rojo el {pct_es(RES[('desp', ELEG)]['rojo_pct'], 2)} de la calma de "
           f"mayo frente al {pct_es(r * 100, 2)} pactado (rango entre señales {pct_es(der['rojo realizado %'].min())} a "
           f"{pct_es(der['rojo realizado %'].max())}; el extremo es {NOMBRE[peor]}; {expl_bosques}): modelo y cortes se "
           f"recalibran juntos cada mes, y un bosque con temperaturas interiores no podría desplegarse con cortes fijos.")
''')

# =====================================================================================
# 16. Heredadas
# =====================================================================================
md(r'''
---
## 16. Cifras heredadas (leídas de las salidas guardadas)
**Necesidad de Shiro.** El póster cuenta la evolución de modelos del proyecto. Esas cifras no se recalculan: se leen con
`nbformat` de las salidas guardadas de los cuadernos fuente (celda fijada, expresión regular por celda) y se contrastan
con la tabla de resultados del proyecto. Si discrepan, manda la salida guardada, se anota la corrección y el cuaderno
sigue. Cada cifra de partición aleatoria se registra con su par temporal cuando la fuente lo guarda (la descripción
dice cuál es); el texto de cada cifra heredada conserva los decimales que imprimió la celda fuente, sin redondear dos
veces.
''')

code(r'''
P1 = nbformat.read("../../1er_Corte_Sept/Parcial_Corte1/Parcial_Corte1.ipynb", as_version=4)
BO = nbformat.read("../Taller_1_Boosting/Taller1_Boosting.ipynb", as_version=4)
def salida(nb_, i):
    return "\n".join(o.get("text", "") for o in nb_.cells[i].get("outputs", []) if o.get("output_type") == "stream")

class Num(float):
    """Número leído de una salida guardada; recuerda cuántos decimales imprimió la celda fuente."""
def a_num(s_):
    x_ = Num(float(s_))
    x_.dec = len(s_.split(".")[1]) if "." in s_ else 0
    return x_
NUM = r"(-?\d+(?:\.\d+)?|NaN)"
def filas_tabla(texto, nombres, ncols):
    out = {}
    for n_ in nombres:
        m_ = re.search(r"^" + re.escape(n_) + r"\s+" + r"\s+".join([NUM] * ncols) + r"\s*$", texto, re.M)
        assert m_, f"no se encontró la fila {n_}"
        out[n_] = [a_num(x) if x != "NaN" else float("nan") for x in m_.groups()]
    return out

FH = {}
# P1 c.7 — partición aleatoria
t7 = salida(P1, 7); reg7, clf7 = t7.split("CLASIFICACIÓN")
FH["p1c7_reg"] = filas_tabla(reg7, ["Regresión Lineal", "Árbol de Decisión", "KNN (K=5)", "Random Forest", "— Línea base (media)"], 3)
FH["p1c7_clf"] = filas_tabla(clf7, ["Árbol", "KNN (K=3)", "Random Forest", "SVM (rbf, C=10)", "SVM balanceado"], 5)
FH["p1c7_base_acc"] = a_num(re.search(r"accuracy ([\d.]+) · F1", t7).group(1))
# P1 c.8 — el contraste entre las dos particiones (pares temporales)
t8p = salida(P1, 8)
assert "EL CONTRASTE ENTRE LAS DOS PARTICIONES" in t8p
FH["p1c8"] = filas_tabla(t8p, ["Regresión Lineal", "Árbol", "KNN", "Random Forest", "SVM"], 4)
# P1 c.22 — F1 a 0,5 del RF con retardos (origen del 0,580)
FH["p1c22"] = filas_tabla(salida(P1, 22), ["+ retardos completos"], 5)
# P1 c.25 — temporal con retardos
FH["p1c25"] = filas_tabla(salida(P1, 25), ["Random Forest", "Regresión Lineal", "— Línea base (media)"], 5)
# P1 c.29 — deriva mensual
FH["p1c29"] = filas_tabla(salida(P1, 29), ["Enero", "Febrero", "Marzo", "Abril", "Mayo"], 6)
# P1 c.38 — detector y barrido (sobre la prueba)
t38 = salida(P1, 38)
FH["p1c38_dias"] = a_num(re.search(r"Simulación de despliegue: ([\d.]+) días", t38).group(1))
FH["p1c38_ep"] = int(re.search(r"Episodios reales de consumo alto: (\d+)", t38).group(1))
rf38, lg38 = t38.split("--- Regresión Logística")
FH["p1c38_rf"] = filas_tabla(rf38.split("--- Random Forest + retardos ---")[1], ["0.4", "0.5"], 5)
FH["p1c38_log"] = filas_tabla(lg38, ["0.2"], 5)
# Boosting c.8 — tablas de regresión de los tres escenarios
t8 = salida(BO, 8)
BOO = {}
for bloque in t8.split("=== ")[1:]:
    esc = bloque.split(" ·")[0].strip()
    BOO[esc] = filas_tabla(bloque, ["LightGBM", "Random Forest (ref.)", "Regresión Lineal (ref.)", "XGBoost", "CatBoost"], 6)
# Boosting c.22 — punto de operación del parcial
t22 = salida(BO, 22)
op_txt = re.search(r"Punto de operación del parcial \(RF, umbral 0,40\): (\{.*\})", t22).group(1)
FH["bo22"] = {k_: a_num(v_) for k_, v_ in re.findall(r"'([^']+)': (?:np\.float64\()?([\d.]+)", op_txt)}

# Coherencia interna: las columnas aleatorias de c.8 son las de c.7
for n7, n8 in [("Regresión Lineal", "Regresión Lineal"), ("Árbol de Decisión", "Árbol"), ("KNN (K=5)", "KNN"),
               ("Random Forest", "Random Forest")]:
    assert abs(FH["p1c7_reg"][n7][0] - FH["p1c8"][n8][0]) < 1e-9, n7
for n7, n8 in [("Árbol", "Árbol"), ("KNN (K=3)", "KNN"), ("Random Forest", "Random Forest"), ("SVM (rbf, C=10)", "SVM")]:
    assert abs(FH["p1c7_clf"][n7][3] - FH["p1c8"][n8][2]) < 1e-9, n7

# ---- Contraste con la tabla de resultados del proyecto (tolerancia de redondeo; no detiene el cuaderno) ----
def cerca(a_, b_, dec):
    return abs(a_ - b_) <= 0.5 * 10 ** (-dec) + 0.0005 + 1e-9
REF = [  # (descripción, valor guardado, valor de la tabla del proyecto, decimales en esa tabla)
    ("Lineal aleatoria R²", FH["p1c7_reg"]["Regresión Lineal"][0], 0.171, 3),
    ("Lineal aleatoria MAE", FH["p1c7_reg"]["Regresión Lineal"][1], 52.55, 2),
    ("Lineal aleatoria RMSE", FH["p1c7_reg"]["Regresión Lineal"][2], 91.07, 2),
    ("Lineal temporal R²", BOO["Temporal"]["Regresión Lineal (ref.)"][0], 0.106, 3),
    ("Lineal temporal R² (P1 c.8)", FH["p1c8"]["Regresión Lineal"][1], 0.106, 3),
    ("Árbol aleatoria R²", FH["p1c7_reg"]["Árbol de Decisión"][0], 0.325, 3),
    ("Árbol aleatoria MAE", FH["p1c7_reg"]["Árbol de Decisión"][1], 40.07, 2),
    ("Árbol aleatoria RMSE", FH["p1c7_reg"]["Árbol de Decisión"][2], 82.20, 2),
    ("Árbol temporal R²", FH["p1c8"]["Árbol"][1], -2.891, 3),
    ("KNN aleatoria R²", FH["p1c7_reg"]["KNN (K=5)"][0], 0.539, 3),
    ("KNN aleatoria MAE", FH["p1c7_reg"]["KNN (K=5)"][1], 30.90, 2),
    ("KNN aleatoria RMSE", FH["p1c7_reg"]["KNN (K=5)"][2], 67.89, 2),
    ("KNN temporal R²", FH["p1c8"]["KNN"][1], -0.602, 3),
    ("RF aleatoria R²", FH["p1c7_reg"]["Random Forest"][0], 0.567, 3),
    ("RF aleatoria MAE", FH["p1c7_reg"]["Random Forest"][1], 30.73, 2),
    ("RF aleatoria RMSE", FH["p1c7_reg"]["Random Forest"][2], 65.83, 2),
    ("RF temporal R²", BOO["Temporal"]["Random Forest (ref.)"][0], -4.459, 3),
    ("RF temporal R² (P1 c.8)", FH["p1c8"]["Random Forest"][1], -4.459, 3),
    ("Lineal + retardos R²", FH["p1c25"]["Regresión Lineal"][0], 0.557, 3),
    ("Lineal + retardos MAE", FH["p1c25"]["Regresión Lineal"][1], 28.17, 2),
    ("Lineal + retardos RMSE", FH["p1c25"]["Regresión Lineal"][2], 60.54, 2),
    ("RF + retardos R²", FH["p1c25"]["Random Forest"][0], -0.484, 3),
    ("RF + retardos MAE", FH["p1c25"]["Random Forest"][1], 76.20, 2),
    ("RF + retardos RMSE", FH["p1c25"]["Random Forest"][2], 110.80, 2),
    ("LightGBM aleatoria R²", BOO["Aleatoria"]["LightGBM"][0], 0.598, 3),
    ("LightGBM aleatoria MAE", BOO["Aleatoria"]["LightGBM"][1], 31.35, 2),
    ("LightGBM aleatoria RMSE", BOO["Aleatoria"]["LightGBM"][2], 63.45, 2),
    ("LightGBM temporal R²", BOO["Temporal"]["LightGBM"][0], -0.320, 3),
    ("LightGBM + retardos R²", BOO["Temporal + retardos"]["LightGBM"][0], 0.554, 3),
    ("LightGBM + retardos MAE", BOO["Temporal + retardos"]["LightGBM"][1], 30.34, 2),
    ("LightGBM + retardos RMSE", BOO["Temporal + retardos"]["LightGBM"][2], 60.74, 2),
    ("KNN F1 temporal", FH["p1c8"]["KNN"][3], 0.169, 3),
    ("RF F1 temporal", FH["p1c8"]["Random Forest"][3], 0.206, 3),
    ("SVM F1 temporal", FH["p1c8"]["SVM"][3], 0.024, 3),
]
for n_, (pr_, rc_, f1_, auc_) in {"Árbol": (0.580, 0.383, 0.461, 0.861), "KNN (K=3)": (0.727, 0.562, 0.634, 0.903),
                                  "Random Forest": (0.832, 0.522, 0.642, 0.951), "SVM (rbf, C=10)": (0.617, 0.285, 0.390, 0.832),
                                  "SVM balanceado": (0.367, 0.662, 0.472, 0.855)}.items():
    g_ = FH["p1c7_clf"][n_]
    REF += [(f"{n_} precisión", g_[1], pr_, 3), (f"{n_} recall", g_[2], rc_, 3), (f"{n_} F1", g_[3], f1_, 3), (f"{n_} AUC", g_[4], auc_, 3)]
REF += [("Detector 0,40 eventos %", FH["p1c38_rf"]["0.4"][1], 86.9, 1), ("Detector 0,40 alertas/día", FH["p1c38_rf"]["0.4"][0], 3.0, 1),
        ("Detector 0,40 falsos %", FH["p1c38_rf"]["0.4"][2], 37.3, 1), ("Detector tiempo en alerta %", FH["bo22"]["tiempo en alerta %"], 21.1, 1),
        ("Detector duración (min)", FH["bo22"]["duración media (min)"], 100.5, 1), ("Línea base accuracy", FH["p1c7_base_acc"], 0.904, 3)]
fallan = [c_ for c_ in REF if not cerca(c_[1], c_[2], c_[3])]
print(f"Contraste con la tabla de resultados del proyecto: {len(REF) - len(fallan)} de {len(REF)} cifras coinciden.")
for c_ in fallan:
    print(f"   DISCREPANCIA (manda la salida guardada): {c_[0]}: guardado {c_[1]} · tabla del proyecto {c_[2]}")
# Corrección conocida: F1 por lectura del detector a 0,40
f1_040, f1_050 = FH["p1c38_rf"]["0.4"][4], FH["p1c22"]["+ retardos completos"][4]
print(f"Corrección: la tabla de resultados del proyecto anota F1 por lectura 0,580 para el detector a 0,40; la salida "
      f"guardada (c.38) da {num_es(f1_040, 2)} a 0,40; el 0,580 es a 0,5 (c.22: {num_es(f1_050, 3)}). Manda la salida guardada.")

H = "heredadas"
OBJ_REG = "objetivo: consumo Appliances (Wh)"
OBJ_CLF = "objetivo: reconocer la lectura actual > 200 Wh"
def her(clave, valor, unidad, dec, fuente, desc, part):
    dec = getattr(valor, "dec", dec)               # los decimales que imprimió la celda fuente
    registrar(clave, valor, unidad, dec, fuente, desc, bloque=H, particion=part)
PAR_REG = {"lineal": "her_reg_lineal_temporal_r2", "arbol": "her_reg_arbol_temporal_r2", "knn": "her_reg_knn_temporal_r2",
           "rf": "her_reg_rf_temporal_r2", "media": "her_reg_media_retardos_mae / _rmse (temporal con retardos)"}
for n_, k_ in [("Regresión Lineal", "lineal"), ("Árbol de Decisión", "arbol"), ("KNN (K=5)", "knn"), ("Random Forest", "rf"), ("— Línea base (media)", "media")]:
    v_ = FH["p1c7_reg"][n_]
    par_ = f"; par temporal: {PAR_REG[k_]}" + ("" if k_ == "media" else " (la fuente solo guarda el R² temporal)")
    her(f"her_reg_{k_}_aleatoria_r2", v_[0], "", 3, "Parcial_Corte1.ipynb c.7", f"R² {n_}, partición aleatoria, {OBJ_REG}{par_}", "aleatoria")
    her(f"her_reg_{k_}_aleatoria_mae", v_[1], "Wh", 2, "Parcial_Corte1.ipynb c.7", f"MAE {n_}, partición aleatoria, {OBJ_REG}{par_}", "aleatoria")
    her(f"her_reg_{k_}_aleatoria_rmse", v_[2], "Wh", 2, "Parcial_Corte1.ipynb c.7", f"RMSE {n_}, partición aleatoria, {OBJ_REG}{par_}", "aleatoria")
for n8, k_ in [("Regresión Lineal", "lineal"), ("Árbol", "arbol"), ("KNN", "knn"), ("Random Forest", "rf")]:
    her(f"her_reg_{k_}_temporal_r2", FH["p1c8"][n8][1], "", 3, "Parcial_Corte1.ipynb c.8",
        f"R² {n8}, partición temporal sin retardos, {OBJ_REG}; par de her_reg_{k_}_aleatoria_r2", "temporal")
PAR_CLF = {"arbol": "Árbol", "knn": "KNN", "rf": "Random Forest", "svm": "SVM"}
for n_, k_ in [("Árbol", "arbol"), ("KNN (K=3)", "knn"), ("Random Forest", "rf"), ("SVM (rbf, C=10)", "svm"), ("SVM balanceado", "svm_bal")]:
    par_ = (f"; par temporal: her_clf_{k_}_temporal_f1 (la fuente solo guarda el F1 temporal)" if k_ in PAR_CLF else
            "; sin par temporal guardado (la fuente solo evalúa en temporal la SVM sin balancear)")
    for j_, met in enumerate(["accuracy", "precision", "recall", "f1", "auc"]):
        her(f"her_clf_{k_}_aleatoria_{met}", FH["p1c7_clf"][n_][j_], "", 3, "Parcial_Corte1.ipynb c.7",
            f"{met} {n_}, partición aleatoria, {OBJ_CLF}{par_}", "aleatoria")
for k_, n8 in PAR_CLF.items():
    her(f"her_clf_{k_}_temporal_f1", FH["p1c8"][n8][3], "", 3, "Parcial_Corte1.ipynb c.8",
        f"F1 {n8}, partición temporal sin retardos, {OBJ_CLF}; par de her_clf_{k_}_aleatoria_f1", "temporal")
her("her_clf_base_aleatoria_accuracy", FH["p1c7_base_acc"], "", 3, "Parcial_Corte1.ipynb c.7",
    f"Accuracy de 'todo normal', partición aleatoria, {OBJ_CLF}; sin par temporal guardado", "aleatoria")
for esc, k_ in [("Temporal", "temporal"), ("Temporal + retardos", "retardos"), ("Aleatoria", "aleatoria")]:
    for n_, kk in [("Regresión Lineal (ref.)", "lineal"), ("Random Forest (ref.)", "rf"), ("LightGBM", "lgbm"), ("XGBoost", "xgb"), ("CatBoost", "catboost")]:
        v_ = BOO[esc][n_]
        part = "aleatoria" if esc == "Aleatoria" else "temporal"
        par_ = f"; par temporal: her_bo_{kk}_temporal_* y her_bo_{kk}_retardos_*" if part == "aleatoria" else ""
        her(f"her_bo_{kk}_{k_}_r2", v_[0], "", 3, "Taller1_Boosting.ipynb c.8", f"R² {n_}, {esc}, {OBJ_REG}{par_}", part)
        her(f"her_bo_{kk}_{k_}_mae", v_[1], "Wh", 2, "Taller1_Boosting.ipynb c.8", f"MAE {n_}, {esc}, {OBJ_REG}{par_}", part)
        her(f"her_bo_{kk}_{k_}_rmse", v_[2], "Wh", 2, "Taller1_Boosting.ipynb c.8", f"RMSE {n_}, {esc}, {OBJ_REG}{par_}", part)
her("her_reg_lineal_retardos_sesgo", FH["p1c25"]["Regresión Lineal"][3], "Wh", 3, "Parcial_Corte1.ipynb c.25", f"Sesgo lineal + retardos, {OBJ_REG}", "temporal")
her("her_reg_rf_retardos_sesgo", FH["p1c25"]["Random Forest"][3], "Wh", 2, "Parcial_Corte1.ipynb c.25", f"Sesgo RF + retardos, {OBJ_REG}", "temporal")
her("her_reg_media_retardos_mae", FH["p1c25"]["— Línea base (media)"][1], "Wh", 2, "Parcial_Corte1.ipynb c.25", f"MAE de predecir la media (temporal), {OBJ_REG}", "temporal")
her("her_reg_media_retardos_rmse", FH["p1c25"]["— Línea base (media)"][2], "Wh", 2, "Parcial_Corte1.ipynb c.25", f"RMSE de predecir la media (temporal), {OBJ_REG}", "temporal")
for n_, k_ in zip(["Enero", "Febrero", "Marzo", "Abril", "Mayo"], ["ene", "feb", "mar", "abr", "may"]):
    her(f"her_deriva_{k_}_p90", FH["p1c29"][n_][3], "Wh", 0, "Parcial_Corte1.ipynb c.29", f"Percentil 90 del consumo en {n_}", "temporal")
    her(f"her_deriva_{k_}_tasa", FH["p1c29"][n_][4], "%", 2, "Parcial_Corte1.ipynb c.29", f"% de lecturas > 200 Wh en {n_}", "temporal")
    her(f"her_deriva_{k_}_tout", FH["p1c29"][n_][5], "°C", 2, "Parcial_Corte1.ipynb c.29", f"Temperatura exterior media en {n_}", "temporal")
DET_TXT = f"Detector RF + retardos a 0,40 ({OBJ_CLF}, evaluado por episodio)"
her("her_det040_eventos", FH["p1c38_rf"]["0.4"][1], "%", 1, "Parcial_Corte1.ipynb c.38", f"{DET_TXT}: picos tocados", "temporal")
her("her_det040_alertas_dia", FH["p1c38_rf"]["0.4"][0], "avisos/día", 2, "Parcial_Corte1.ipynb c.38", f"{DET_TXT}: alertas por día", "temporal")
her("her_det040_falsos", FH["p1c38_rf"]["0.4"][2], "%", 1, "Parcial_Corte1.ipynb c.38", f"{DET_TXT}: alertas falsas", "temporal")
her("her_det040_f1", f1_040, "", 2, "Parcial_Corte1.ipynb c.38",
    f"{DET_TXT}: F1 por lectura (corrige el 0,580 que anotaba la tabla de resultados del proyecto)", "temporal")
her("her_det050_f1", f1_050, "", 3, "Parcial_Corte1.ipynb c.22", f"RF + retardos a 0,5 ({OBJ_CLF}): F1 por lectura (origen del 0,580)", "temporal")
her("her_det_dias", FH["p1c38_dias"], "días", 1, "Parcial_Corte1.ipynb c.38", "Días del mes de prueba", "temporal")
her("her_det_episodios", FH["p1c38_ep"], "picos", 0, "Parcial_Corte1.ipynb c.38", "Episodios del mes de prueba", "temporal")
her("her_log020_eventos", FH["p1c38_log"]["0.2"][1], "%", 1, "Parcial_Corte1.ipynb c.38", f"Logística + retardos a 0,20 ({OBJ_CLF}): picos tocados", "temporal")
her("her_log020_alertas_dia", FH["p1c38_log"]["0.2"][0], "avisos/día", 2, "Parcial_Corte1.ipynb c.38", f"Logística a 0,20 ({OBJ_CLF}): alertas/día", "temporal")
her("her_log020_falsos", FH["p1c38_log"]["0.2"][2], "%", 1, "Parcial_Corte1.ipynb c.38", f"Logística a 0,20 ({OBJ_CLF}): alertas falsas", "temporal")
her("her_det_tiempo_alerta", FH["bo22"]["tiempo en alerta %"], "%", 1, "Taller1_Boosting.ipynb c.22", f"{DET_TXT}: tiempo en alerta", "temporal")
her("her_det_duracion", FH["bo22"]["duración media (min)"], "min", 1, "Taller1_Boosting.ipynb c.22", f"{DET_TXT}: duración media del aviso", "temporal")
her("her_correccion_f1", "La tabla de resultados del proyecto anota F1 0,580 a 0,40; la salida guardada da " + num_es(f1_040, 2) +
    " (0,580 es a 0,5, c.22). El umbral 0,40 se eligió barriendo la prueba (c.38–c.40).", "", 0,
    "Parcial_Corte1.ipynb c.22 y c.38", "Corrección a la tabla de resultados del proyecto", "temporal")
her("her_contraste_n_ok", len(REF) - len(fallan), "", 0, "§16 Heredadas", "Cifras heredadas que coinciden con la tabla del proyecto", "mixta")
her("her_contraste_n_total", len(REF), "", 0, "§16 Heredadas", "Cifras heredadas contrastadas con la tabla del proyecto", "mixta")
for i_, c_ in enumerate(fallan, 1):
    her(f"her_correccion_{i_}", f"{c_[0]}: la salida guardada da {num_es(c_[1], 3)}; la tabla del proyecto anota {num_es(c_[2], 3)}. Manda la salida guardada.",
        "", 0, "§16 Heredadas", "Discrepancia con la tabla de resultados del proyecto", "mixta")

# Coherencia entre heredadas del detector y las anclas recalculadas (mismo dato, dos fuentes)
for kh_, ka_ in [("her_det040_eventos", "ancla_det_detectados"), ("her_det040_alertas_dia", "ancla_det_avisos_dia"),
                 ("her_det040_falsos", "ancla_det_falsos"), ("her_det040_f1", "ancla_det_f1"),
                 ("her_det_tiempo_alerta", "ancla_det_tiempo_alerta"), ("her_det_duracion", "ancla_det_duracion"),
                 ("her_det_dias", "ancla_det_dias")]:
    vh_, va_ = CIFRAS[H][kh_]["valor"], CIFRAS["nuevas"][ka_]["valor"]
    dec_h = len(CIFRAS[H][kh_]["texto"].split(" ")[0].split(",")[1]) if "," in CIFRAS[H][kh_]["texto"] else 0
    assert abs(vh_ - va_) <= 0.5 * 10 ** (-dec_h) + 1e-9, (kh_, vh_, ka_, va_)
print(f"{len(CIFRAS['heredadas'])} cifras heredadas registradas; las del detector coinciden con las anclas recalculadas.")
que_cambia("la evolución de modelos del póster se cuenta con cifras trazables a una celda guardada, en pares aleatoria/temporal, "
           f"y con el F1 del detector corregido a {num_es(f1_040, 2)}.")
''')

# =====================================================================================
# 17. Figuras
# =====================================================================================
md(r'''
---
## 17. Figuras para el informe y el póster
**Necesidad de Shiro.** El informe y el póster tienen que mostrar lo mismo que dice el cuaderno, sin cifras tecleadas.
Cada figura sale de las variables de las secciones anteriores, se exporta una sola vez en PNG a 300 dpi en `figuras/`
(ancho de una columna de informe, unas 7,8 pulgadas, con texto de 10 pt o más: reducida a 16 cm el texto queda cerca de 8 pt, y la misma imagen se amplía sin pérdida al póster A1) y lleva en el subtítulo el componente de Shiro que
informa. Colores: verde, ámbar y rojo solo para el semáforo; gris para referencias; azul reservado al pronóstico del
gemelo (ninguna de estas figuras lo dibuja). Rutas y descripciones quedan en `cifras.json` (claves `fig_*`).
''')

code(r'''
import textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Patch, Rectangle, FancyBboxPatch
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.transforms import offset_copy

VERDE, AMBAR, ROJO, AZUL = "#188038", "#e8710a", "#d93025", "#1a73e8"
TINTA, GRIS_OSC, GRIS, GRIS_CLARO, GRIS_FONDO = "#202124", "#5f6368", "#9aa0a6", "#dadce0", "#f1f3f4"
ROJO_TENUE = "#f6cdc9"                       # rojo del semáforo al 25 % sobre blanco (rojo en curso y picos)
FUENTE = "Calibri" if any(f_.name == "Calibri" for f_ in fm.fontManager.ttflist) else "DejaVu Sans"
plt.rcParams.update({"font.family": FUENTE, "font.size": 11, "axes.titlesize": 12, "axes.labelsize": 11,
                     "xtick.labelsize": 10, "ytick.labelsize": 10, "legend.fontsize": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.edgecolor": GRIS, "axes.labelcolor": TINTA,
                     "xtick.color": GRIS_OSC, "ytick.color": GRIS_OSC, "text.color": TINTA, "figure.facecolor": "white",
                     "axes.facecolor": "white", "hatch.color": ROJO, "hatch.linewidth": 0.8, "legend.frameon": False})
Path("figuras").mkdir(exist_ok=True)
F17 = "§17 Figuras"
FIGS = {}
FMT_WH = FuncFormatter(lambda x_, _: num_es(x_, 0))
FMT_PCT = FuncFormatter(lambda x_, _: num_es(x_, 0) + " %")
COLOR_SEM = {"verde": VERDE, "amarillo": AMBAR, "rojo": ROJO}

ANCHO = 7.8          # pulgadas: una columna de informe (≈ 16 cm a 80 %) y ampliable sin pérdida al póster A1
LH = 13.0            # alto de línea (pt) para las figuras que se maquetan "como texto" (G4 y G6)

def titular(fig, titulo, subtitulo, sobre_ejes=22, ancho_car=96):
    """Título y subtítulo (componente de Shiro que informa) encima del eje más alto; el subtítulo se parte en líneas
    para que la figura no se ensanche más allá de ANCHO."""
    y_top = max(a_.get_position().y1 for a_ in fig.axes)
    sub_ = textwrap.fill(subtitulo, ancho_car)
    n_ = sub_.count("\n") + 1
    fig.text(0.0, y_top, sub_, transform=offset_copy(fig.transFigure, fig=fig, y=sobre_ejes, units="points"),
             ha="left", va="bottom", fontsize=10.5, color=GRIS_OSC, linespacing=1.25)
    fig.text(0.0, y_top, titulo, transform=offset_copy(fig.transFigure, fig=fig, y=sobre_ejes + 13.5 * n_ + 6, units="points"),
             ha="left", va="bottom", fontsize=14, fontweight="bold", color=TINTA)

def guardar(fig, clave, nombre, desc):
    ruta = f"figuras/{nombre}.png"
    fig.savefig(ruta, dpi=300, bbox_inches="tight", pad_inches=0.15, facecolor="white", metadata={"Software": None})
    plt.close(fig)
    FIGS[clave] = ruta
    registrar(f"fig_{clave}_ruta", ruta, "", 0, F17, desc)
    print(f"{ruta}: {desc}")

def tira(ax, xs, colores, ancho):
    """Tira del semáforo: un rectángulo por racha de color; el rojo en curso, rayado."""
    i_ = 0
    while i_ < len(xs):
        j_ = i_
        while j_ + 1 < len(xs) and colores[j_ + 1] == colores[i_]:
            j_ += 1
        x0, w_ = xs[i_], xs[j_] - xs[i_] + ancho
        if colores[i_] == "rojo en curso":
            ax.add_patch(Rectangle((x0, 0), w_, 1, facecolor=ROJO_TENUE, edgecolor=ROJO, hatch="////", linewidth=0))
        else:
            ax.add_patch(Rectangle((x0, 0), w_, 1, facecolor=COLOR_SEM[colores[i_]], linewidth=0))
        i_ = j_ + 1
    ax.set_ylim(0, 1); ax.set_yticks([])
    for lado_ in ("left", "top", "right"):
        ax.spines[lado_].set_visible(False)

LEYENDA_SEM = [Patch(facecolor=VERDE, label="verde: sin aviso"), Patch(facecolor=AMBAR, label="amarillo: atento"),
               Patch(facecolor=ROJO, label="rojo anticipado: Shiro propone aplazar"),
               Patch(facecolor=ROJO_TENUE, edgecolor=ROJO, hatch="////", linewidth=0, label="rojo en curso: lo da el medidor")]
hhmm = lambda j_: f"{FECHA.iloc[j_]:%H:%M}"

# ---------------------------------------------------------------- G1: un día con y sin Guardian
ix1 = idx_dia
hx = ((FECHA.iloc[ix1] - DIA).dt.total_seconds() / 3600).to_numpy()
fig = plt.figure(figsize=(ANCHO, 5.6))
gs = fig.add_gridspec(2, 1, height_ratios=[4, 0.55], hspace=0.12)
ax = fig.add_subplot(gs[0]); axs = fig.add_subplot(gs[1], sharex=ax)
for p in ids_d:
    if (E[p] >= ix1[0]) and (S[p] <= ix1[-1]):
        a_h = (FECHA.iloc[max(S[p], ix1[0])] - DIA).total_seconds() / 3600
        b_h = (FECHA.iloc[min(E[p], ix1[-1])] - DIA).total_seconds() / 3600 + 1 / 6
        ax.axvspan(a_h, b_h, color=ROJO_TENUE, alpha=0.6, lw=0, zorder=0)
ax.plot(hx + 1 / 12, A[ix1], color=TINTA, lw=1.6, zorder=3)
ax.axhline(UMBRAL, color=GRIS, ls="--", lw=1, zorder=1)
ymax1 = float(A[ix1].max()) * 1.6
ax.set_ylim(0, ymax1)
ax.text(0.2, UMBRAL + ymax1 * 0.012, f"umbral de pico: {num_es(UMBRAL, 0)} Wh", color=GRIS_OSC, fontsize=10, va="bottom")
ax.yaxis.set_major_formatter(FMT_WH); ax.set_ylabel("Consumo de los aparatos (Wh cada 10 min)")
niveles = [0.88, 0.62, 0.48]
for i_, q_ in enumerate(sorted(DIA_AD["picos"], key=lambda q: q["inicio"])):
    hs_ = (pd.Timestamp(q_["inicio"]) - DIA).total_seconds() / 3600
    y_ = ymax1 * niveles[i_ % 3]
    if q_["primer_rojo"]:
        # La barra va desde el inicio REAL de la racha roja; la antelación del proyecto se cuenta en [s−3, s−1]
        hr_ = (pd.Timestamp(q_["inicio_rojo"]) - DIA).total_seconds() / 3600
        t_r, t_p = f"{pd.Timestamp(q_['inicio_rojo']):%H:%M}", f"{pd.Timestamp(q_['inicio']):%H:%M}"
        if q_["min_desde_inicio_rojo"] > q_["antelacion_min"]:
            txt_ = (f"rojo desde {t_r} → pico {t_p}\n{q_['min_desde_inicio_rojo']} min en rojo antes del pico\n"
                    f"(antelación contada: {q_['antelacion_min']} min, el máximo)")
        else:
            txt_ = f"rojo desde {t_r} → pico {t_p}\n{q_['antelacion_min']} min de antelación"
        yb_ = y_ - ymax1 * 0.025
        ax.plot([hr_, hs_], [yb_, yb_], color=ROJO, lw=4, solid_capstyle="butt", zorder=4)
        ax.plot([hr_, hr_], [0, yb_], color=ROJO, lw=0.9, ls=":", zorder=2)
        ax.text(hr_, y_, txt_, color=TINTA, fontsize=10, ha="left" if hr_ < 12 else "right", va="bottom", linespacing=1.2)
    else:
        ax.text(hs_ - 0.15, y_, f"pico {pd.Timestamp(q_['inicio']):%H:%M}\nsin aviso previo", color=TINTA, fontsize=10,
                ha="left" if hs_ < 12 else "right", va="bottom", linespacing=1.2)
tira(axs, hx, [str(COLOR[j_]) for j_ in ix1], 1 / 6)
axs.set_xlim(0, 24); axs.set_xticks(range(0, 25, 3)); axs.set_xticklabels([f"{h_:02d}:00" for h_ in range(0, 25, 3)])
plt.setp(ax.get_xticklabels(), visible=False)
axs.set_ylabel("Guardian", rotation=0, ha="right", va="center", fontsize=10)
ax.set_title("Sin Guardian: solo el consumo (franjas rosadas = picos)", loc="left", fontsize=10.5, color=GRIS_OSC)
axs.legend(handles=LEYENDA_SEM, loc="upper center", bbox_to_anchor=(0.45, -0.95), ncol=2, fontsize=10)
n_pd = len(DIA_AD["picos"]); n_ad = sum(q["antelacion_min"] >= 20 for q in DIA_AD["picos"])
titular(fig, f"Un día del mes nunca visto ({fecha_es(DIA).split(' ')[0]}), sin y con Guardian",
        f"Informa: semáforo de Guardian y propuesta en ApprovalGate · día mediano entre {DIA_AD['n_dias_candidatos']} días "
        f"con ≥ 3 picos ({n_ad} de {n_pd} picos avisados con ≥ 20 min) · cortes de abril aplicados a mayo · la antelación "
        f"se cuenta en los 30 min previos al pico, aunque el rojo empiece antes")
guardar(fig, "g1", "G1_dia_con_guardian",
        f"Consumo cada 10 min del {fecha_es(DIA).split(' ')[0]} con picos sombreados y la tira del semáforo de {ELEG} "
        f"desplegado; inicio real del rojo y minutos de antelación (contados en los 30 min previos) anotados. Sin curva "
        f"'con Shiro' (no hay modelo del efecto)")

# ---------------------------------------------------------------- G2: picos avisados con margen
AZAR_UMB = {10: (1 - (1 - r_real) ** 3) * 100, 20: (1 - (1 - r_real) ** 2) * 100, 30: r_real * 100}
assert abs(AZAR_UMB[20] - azar_teo_d) < 1e-9
registrar("azar_p10_desplegado", AZAR_UMB[10], "%", 1, F17,
          "% esperado de picos con ≥ 10 min marcando al azar el rojo realizado del elegido (1 − (1 − f)³)")
registrar("azar_p30_desplegado", AZAR_UMB[30], "%", 1, F17,
          "% esperado de picos con ≥ 30 min marcando al azar el rojo realizado del elegido (f)")
fig, ax = plt.subplots(figsize=(ANCHO, 5.0))
xg = np.arange(3); wb = 0.36
SER2 = [("elegido_desp", f"{NOMBRE[ELEG]}, desplegado", "#3c4043", None, MD),
        ("regla_mismo_rojo", "regla de nivel (consumo actual) con el mismo tiempo en rojo", GRIS_CLARO, None, M_REGLA)]
for k_, (et_, lab_, col_, _, mm_) in enumerate(SER2):
    vals_ = [FIG2[(et_, m)][0] for m in (10, 20, 30)]
    los_ = [FIG2[(et_, m)][1] for m in (10, 20, 30)]; his_ = [FIG2[(et_, m)][2] for m in (10, 20, 30)]
    xs_ = xg + (k_ - 0.5) * (wb + 0.03)
    ax.bar(xs_, vals_, width=wb, color=col_, label=lab_, zorder=2)
    ax.errorbar(xs_, vals_, yerr=[np.array(vals_) - los_, np.array(his_) - vals_], fmt="none", ecolor=TINTA,
                elinewidth=1.1, capsize=4, zorder=3)
    for x_, v_, h_, m in zip(xs_, vals_, his_, (10, 20, 30)):
        ax.text(x_, h_ + 1.2, f"{pct_es(v_)}\n{mm_['n' + str(m)]} de {len(ids_te)}", ha="center", va="bottom",
                fontsize=10, color=TINTA)
for i_, m in enumerate((10, 20, 30)):
    ax.plot([i_ - 0.44, i_ + 0.44], [AZAR_UMB[m]] * 2, color=GRIS_OSC, ls=(0, (4, 3)), lw=1.4, zorder=4)
ax.plot([], [], color=GRIS_OSC, ls=(0, (4, 3)), lw=1.4, label="azar con el mismo tiempo en rojo")
ax.set_xticks(xg); ax.set_xticklabels(["≥ 10 min", "≥ 20 min\n(al menos dos lecturas)", "≥ 30 min"])
ax.set_xlabel("Antelación del primer rojo antes del inicio del pico")
ax.yaxis.set_major_formatter(FMT_PCT); ax.set_ylabel(f"Picos avisados (% de los {len(ids_te)} del mes)")
ax.set_ylim(0, max(FIG2[k][2] for k in FIG2) + 14)
h_, l_ = ax.get_legend_handles_labels()
ax.legend([h_[1], h_[2], h_[0]], [l_[1], l_[2], l_[0]], loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=1,
          fontsize=10)
titular(fig, "Picos avisados con margen en el mes nunca visto",
        f"Informa: si Guardian notifica en ApprovalGate · ambas señales con {pct_es(r_real * 100, 2)} de la calma en rojo "
        f"({num_es(MD['min_dia'], 0)} min/día) · barras: rango plausible del 95 % (bootstrap por día)")
guardar(fig, "g2", "G2_picos_avisados",
        f"% de los {len(ids_te)} picos con ≥ 10, ≥ 20 y ≥ 30 min de antelación: {ELEG} desplegado frente a la regla de nivel "
        f"con el mismo rojo realizado, IC 95 % bootstrap por día y línea de azar")

# ---------------------------------------------------------------- G3: cuánto molesta cada color
seg_te = test_m.copy()
dias_te = dias_seg(cl, N)
MIN_COLOR = {c_: float((COLOR[seg_te] == c_).sum() * 10 / dias_te) for c_ in ("verde", "amarillo", "rojo", "rojo en curso")}
assert abs(MIN_COLOR["rojo"] - MD["min_dia"]) < 1e-6
n_calma_te = int((calma & test_m).sum())
PRESUP_MIN = r * n_calma_te * 10 / dias_te
ACIERTO = {"verde": MD["acierto_verde"], "amarillo": MD["acierto_amarillo"], "rojo": MD["acierto_rojo"]}
for c_, k_ in (("verde", "verde"), ("amarillo", "amarillo"), ("rojo", "rojo"), ("rojo en curso", "en_curso")):
    registrar(f"fig3_min_dia_{k_}", MIN_COLOR[c_], "min/día", 0, F17, f"Minutos al día en {c_} ({ELEG} desplegado, prueba)")
registrar("fig3_presupuesto_min_dia", PRESUP_MIN, "min/día", 0, F17,
          "Minutos al día en rojo que corresponderían al presupuesto r sobre la calma de prueba")
fig, (axa, axb) = plt.subplots(2, 1, figsize=(ANCHO, 7.6), gridspec_kw={"height_ratios": [1.25, 1], "hspace": 0.5})
orden3 = ["verde", "amarillo", "rojo", "rojo en curso"]
yy = np.arange(len(orden3))[::-1]
for y_, c_ in zip(yy, orden3):
    if c_ == "rojo en curso":
        axa.barh(y_, MIN_COLOR[c_], height=0.6, color=ROJO_TENUE, edgecolor=ROJO, hatch="////", linewidth=0)
    else:
        axa.barh(y_, MIN_COLOR[c_], height=0.6, color=COLOR_SEM[c_])
    axa.text(MIN_COLOR[c_] + 12, y_, f"{num_es(MIN_COLOR[c_], 0)} min/día", va="center", fontsize=10)
y_r = yy[orden3.index("rojo")]
axa.plot([PRESUP_MIN] * 2, [y_r - 0.42, y_r + 0.42], color=TINTA, lw=2)
axa.annotate(textwrap.fill(f"marca negra = presupuesto: {pct_es(r * 100, 2)} de la calma = {num_es(PRESUP_MIN, 0)} min/día. "
                           f"Los cortes se fijaron en abril; en el mes nunca visto el rojo sube a "
                           f"{pct_es(r_real * 100, 2)} de la calma ({num_es(MIN_COLOR['rojo'], 0)} min/día): es deriva, "
                           f"y por eso se recalibra cada mes.", 52),
             xy=(PRESUP_MIN, y_r + 0.42), xytext=(MIN_COLOR["rojo"] + 230, y_r + 0.55), fontsize=10, color=TINTA,
             arrowprops=dict(arrowstyle="-", color=TINTA, lw=0.8), va="center", linespacing=1.2)
axa.set_yticks(yy); axa.set_yticklabels(orden3)
axa.set_xlim(0, max(MIN_COLOR.values()) * 1.2); axa.xaxis.set_major_formatter(FMT_WH)
axa.set_xlabel("Minutos al día"); axa.set_title("Tiempo en cada color", loc="left", fontsize=12)
orden3b = ["verde", "amarillo", "rojo"]
yb_ = np.arange(3)[::-1]
for y_, c_ in zip(yb_, orden3b):
    axb.barh(y_, ACIERTO[c_], height=0.6, color=COLOR_SEM[c_])
    axb.text(max(ACIERTO[c_], r_te * 100) + 0.5, y_, f"{num_es(ACIERTO[c_], 1)} de cada 100", va="center", fontsize=10)
axb.axvline(r_te * 100, color=GRIS_OSC, ls=(0, (4, 3)), lw=1.2)
axb.text(r_te * 100 + 0.4, -0.62, f"tasa base del mes: {pct_es(r_te * 100, 1)}", fontsize=10, color=GRIS_OSC, va="center")
axb.set_yticks(yb_); axb.set_yticklabels(orden3b)
axb.set_xlim(0, max(ACIERTO.values()) * 1.45); axb.set_ylim(-0.9, 2.5); axb.xaxis.set_major_formatter(FMT_PCT)
axb.set_xlabel("Lecturas que precedieron un pico en los 30 min siguientes")
axb.set_title("Acierto de cada color", loc="left", fontsize=12)
titular(fig, "Cuánto molesta cada color y cuánto acierta",
        f"Informa: el control de presupuesto del semáforo (tarjeta 2 de la página) · {NOMBRE[ELEG]}, mes nunca visto, "
        f"cortes fijados en validación")
guardar(fig, "g3", "G3_tiempo_y_acierto_por_color",
        f"Minutos al día en verde, amarillo, rojo y rojo en curso, con el presupuesto r marcado y la deriva del rojo "
        f"explicada; acierto por color (de cada 100 lecturas, cuántas precedieron un pico) frente a la tasa base del mes; "
        f"{ELEG} desplegado")

# ---------------------------------------------------------------- G4: la regla que explica el rojo
# Maquetada "como texto": las posiciones verticales van en líneas de LH pt, así ninguna caja se desborda.
rg_ord = sorted(REGLAS, key=lambda rg: (not rg["rojo"], -rg["n"]))
W_COND, W_NOTA, W_ACC, W_PIE = 58, 66, 34, 112
bloques4, y4 = [], 1.8
for rg in rg_ord:
    cond_ = textwrap.fill(rg["texto"].split(" → ")[0][3:], W_COND)
    nota_ = textwrap.fill(f"en el entrenamiento: {num_es(rg['prop_rojo'] * 100, 0)} de cada 100 de estos momentos estaban "
                          f"en rojo · {num_es(rg['n'], 0)} momentos", W_NOTA)
    acc_ = ("ROJO → propuesta: no encender cargas grandes en los próximos 30 min (la persona aprueba, ajusta o rechaza)"
            if rg["rojo"] else "no rojo → sin propuesta (verde o amarillo según el puntaje)")
    acc_ = textwrap.fill(acc_, W_ACC)
    nc_, nn_, na_ = cond_.count("\n") + 1, nota_.count("\n") + 1, acc_.count("\n") + 1
    alto_ = max(nc_ + 0.4 + nn_, na_) + 1.2
    bloques4.append((rg, y4, alto_, cond_, nota_, acc_, nc_))
    y4 += alto_ + 0.6
nota4 = (f"Fidelidad en la calma del mes nunca visto: coincide con el semáforo en el {pct_es(fid)} de los momentos (un "
         f"explicador que nunca dijera rojo coincidiría en el {pct_es(base_nunca)}); reproduce el {pct_es(recall_arb)} del "
         f"rojo y el {pct_es(prec_arb)} de su rojo es rojo del semáforo. Donde no coincide, manda el modelo y la regla se "
         f"rotula como aproximación.")
if ELEG == "G0":
    umb_f = [u_ for rg in REGLAS if rg["rojo"] for f_, op, u_ in rg["condiciones"] if f_ == "freq_hora_pct" and op == ">"]
    if umb_f:
        u_min = min(umb_f)
        def rangos_horas(hs):
            out_, ini_ = [], None
            for h_ in range(25):
                if h_ in hs and ini_ is None: ini_ = h_
                if h_ not in hs and ini_ is not None:
                    out_.append(f"{ini_}:00–{h_ - 1}:59"); ini_ = None
            return ", ".join(out_) if out_ else "ninguna"
        f_lab = {h_ for h_ in range(24) if freq.iloc[h_ * 2] * 100 > u_min}
        f_fin = {h_ for h_ in range(24) if freq.iloc[h_ * 2 + 1] * 100 > u_min}
        nota4 += (f" Horas con frecuencia de picos > {num_es(u_min, 1)} %: días laborables {rangos_horas(f_lab)}; "
                  f"fines de semana {rangos_horas(f_fin)}.")
        registrar("fig4_horas_laborables", rangos_horas(f_lab), "", 0, F17,
                  "Horas laborables cuya frecuencia histórica de picos supera el menor umbral de las reglas de rojo")
        registrar("fig4_horas_fin_semana", rangos_horas(f_fin), "", 0, F17, "Ídem, fin de semana")
pie4 = textwrap.fill(nota4, W_PIE)
y_tot4 = y4 + pie4.count("\n") + 1.5
fig, ax = plt.subplots(figsize=(ANCHO, y_tot4 * LH / 72 / 0.98))
fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
ax.set_xlim(0, 1); ax.set_ylim(y_tot4, 0); ax.axis("off")
ax.text(0.035, 0.6, "Si…", fontsize=11, fontweight="bold", color=GRIS_OSC, va="center")
ax.text(0.64, 0.6, "Entonces…", fontsize=11, fontweight="bold", color=GRIS_OSC, va="center")
for rg, y0_, alto_, cond_, nota_, acc_, nc_ in bloques4:
    ax.add_patch(Rectangle((0.0, y0_), 1.0, alto_, facecolor="#fdecea" if rg["rojo"] else GRIS_FONDO, linewidth=0))
    ax.add_patch(Rectangle((0.0, y0_), 0.012, alto_, facecolor=ROJO if rg["rojo"] else GRIS, linewidth=0))
    ax.text(0.035, y0_ + 0.6, cond_, fontsize=10.5, va="top", color=TINTA, linespacing=1.2)
    ax.text(0.035, y0_ + 0.6 + nc_ * 1.0 + 0.4, nota_, fontsize=10, va="top", color=GRIS_OSC, linespacing=1.2)
    ax.text(0.64, y0_ + alto_ / 2, acc_, fontsize=10.5, va="center", linespacing=1.2,
            color=ROJO if rg["rojo"] else GRIS_OSC, fontweight="bold" if rg["rojo"] else "normal")
ax.text(0.0, y4 + 0.2, pie4, fontsize=10, color=GRIS_OSC, va="top", linespacing=1.2)
titular(fig, "La regla que explica el rojo, y la acción que propone",
        f"Informa: la capa de explicación de Guardian · árbol de profundidad 3 que imita el rojo de {ELEG}, el "
        f"{NOMBRE[ELEG].split(' (')[0]}, ajustado con los datos de entrenamiento de Guardian (enero a mediados de abril) · "
        f"la frecuencia es la de esa hora en días laborables o de fin de semana, según el día", sobre_ejes=4)
guardar(fig, "g4", "G4_regla_explica_rojo",
        f"Reglas del árbol explicador de profundidad 3 en lenguaje del hogar con su acción y su fidelidad "
        f"({pct_es(fid)} de coincidencia, {pct_es(recall_arb)} del rojo reproducido)")

# ---------------------------------------------------------------- G5: dos casos críticos (un caso por fila)
w1 = np.arange(max(S[p_c1] - 12, cl), min(S[p_c1] + 13, N))
w2 = np.arange(max(a_c2[0] - 12, cl), min(a_c2[-1] + 13, N))
fig = plt.figure(figsize=(ANCHO, 11.2))
gs5 = fig.add_gridspec(7, 1, height_ratios=[3, 0.45, 2, 1.05, 3, 0.45, 2], hspace=0.16)
ejes5 = []
for fila_, (w_, tit_) in enumerate(((w1, f"Caso 1 · pico no anticipado con más energía · {fecha_es(FECHA.iloc[S[p_c1]]).split(' ')[0]}"),
                                    (w2, f"Caso 2 · aviso falso más largo · {fecha_es(FECHA.iloc[a_c2[0]]).split(' ')[0]}"))):
    g0_ = 4 * fila_
    a1 = fig.add_subplot(gs5[g0_]); a2 = fig.add_subplot(gs5[g0_ + 1], sharex=a1); a3 = fig.add_subplot(gs5[g0_ + 2], sharex=a1)
    xw = np.arange(len(w_))
    for p in range(len(S)):
        if E[p] >= w_[0] and S[p] <= w_[-1]:
            a1.axvspan(max(S[p], w_[0]) - w_[0], min(E[p], w_[-1]) - w_[0] + 1, color=ROJO_TENUE, alpha=0.6, lw=0, zorder=0)
    a1.plot(xw + 0.5, A[w_], color=TINTA, lw=1.6, zorder=3)
    a1.axhline(UMBRAL, color=GRIS, ls="--", lw=1)
    a1.yaxis.set_major_formatter(FMT_WH); a1.set_ylim(0, max(float(A[w_].max()), UMBRAL) * 1.75)
    a1.set_title(tit_, loc="left", fontsize=12, fontweight="bold")
    tira(a2, xw, [str(COLOR[j_]) for j_ in w_], 1)
    sc_w = np.where(calma[w_], SCORE[ELEG][w_], np.nan)
    a3.plot(xw + 0.5, sc_w, color=TINTA, lw=1.4, marker="o", ms=3.5)
    a3.axhline(CORTES[ELEG][0], color=ROJO, ls="--", lw=1.2); a3.axhline(CORTES[ELEG][1], color=AMBAR, ls="--", lw=1.2)
    x_lab, ha_lab = (len(w_) - 0.2, "right") if fila_ == 0 else (0.2, "left")   # rótulos donde no hay datos
    a3.text(x_lab, CORTES[ELEG][0] + 0.015, f"corte rojo {num_es(CORTES[ELEG][0], 3)}", color=ROJO, fontsize=10,
            va="bottom", ha=ha_lab)
    a3.text(x_lab, CORTES[ELEG][1] - 0.015, f"corte amarillo {num_es(CORTES[ELEG][1], 3)}", color=AMBAR,
            fontsize=10, va="top", ha=ha_lab)
    a3.yaxis.set_major_locator(MultipleLocator(0.2))
    a3.yaxis.set_major_formatter(FuncFormatter(lambda x_, _: num_es(x_, 1)))
    tk_ = [i_ for i_ in range(len(w_)) if FECHA.iloc[w_[i_]].minute == 0]
    a3.set_xticks(tk_); a3.set_xticklabels([hhmm(w_[i_]) for i_ in tk_]); a3.set_xlim(0, len(w_))
    plt.setp(a1.get_xticklabels(), visible=False); plt.setp(a2.get_xticklabels(), visible=False)
    a2.tick_params(axis="x", length=0)
    a1.set_ylabel("Consumo (Wh)"); a3.set_ylabel(f"Puntaje de {ELEG}")
    ejes5.append((a1, a2, a3, w_))
# Caso 1: narrativa anclada en s−2
a1, a2, a3, w_ = ejes5[0]
x_s2 = (S[p_c1] - 2) - w_[0]
a3.annotate(f"{hhmm(S[p_c1] - 2)}, 20 min antes: {num_es(A[S[p_c1] - 2], 0)} Wh,\n{COLOR[S[p_c1] - 2]} "
            f"(margen {sig_es(MARG_AM_C1[1], 3)} sobre el corte amarillo)",
            xy=(x_s2 + 0.5, SCORE[ELEG][S[p_c1] - 2]), xytext=(1, CORTES[ELEG][0] + 0.22), fontsize=10,
            arrowprops=dict(arrowstyle="->", color=TINTA, lw=0.8))
a3.set_ylim(min(np.nanmin(np.where(calma[w_], SCORE[ELEG][w_], np.nan)), CORTES[ELEG][1]) - 0.15, CORTES[ELEG][0] + 0.5)
min_vis_c1 = int(min(E[p_c1], w_[-1]) - S[p_c1] + 1) * 10
a1.text(0.015, 0.97, textwrap.fill(
        f"Qué faltó: de {num_es(A[S[p_c1] - 1], 0)} Wh saltó a un pico de hasta {num_es(c1_['max_wh'], 0)} Wh que duró "
        f"{c1_['duracion_min']} min (la figura muestra solo sus primeros {min_vis_c1} min): "
        f"{num_es(c1_['energia_wh'] / 1000, 1)} kWh en total, {num_es(c1_['exceso_wh'] / 1000, 2)} kWh por encima de "
        f"{num_es(UMBRAL, 0)} Wh. Ni el consumo ni la hora lo anunciaban: faltaba saber qué aparato se iba a encender.", 84),
        transform=a1.transAxes, fontsize=10, va="top", linespacing=1.2,
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=GRIS_CLARO))
if FRAGIL_C1:
    a3.text(0.98, 0.04, f"color frágil en {hhmm(VENT_C1[-1])}: margen {sig_es(MARG_AM_C1[-1], 4)}", transform=a3.transAxes,
            ha="right", fontsize=10, color=GRIS_OSC)
# Caso 2: costo del aviso falso
a1, a2, a3, w_ = ejes5[1]
a2.annotate("", xy=(a_c2[-1] - w_[0] + 1, 1.25), xytext=(a_c2[0] - w_[0], 1.25), annotation_clip=False,
            arrowprops=dict(arrowstyle="<->", color=ROJO, lw=1.4))
a1.text(0.015, 0.97, textwrap.fill(f"Qué costó: {c2_['duracion_min']} min en rojo ({hhmm(a_c2[0])}–{hhmm(a_c2[-1])}, "
        f"{c2_['lecturas_rojas']} lecturas) sin ningún pico detrás; el consumo no pasó de {num_es(c2_['wh_max_durante'], 0)} Wh. "
        f"La propuesta de aplazar habría sido inútil.", 84), transform=a1.transAxes, fontsize=10, va="top", linespacing=1.2,
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=GRIS_CLARO))
a3.set_ylim(min(np.nanmin(np.where(calma[w_], SCORE[ELEG][w_], np.nan)), CORTES[ELEG][1]) - 0.15, CORTES[ELEG][0] + 0.5)
fig.legend(handles=LEYENDA_SEM, loc="upper center", bbox_to_anchor=(0.5, 0.075), ncol=2, fontsize=10)
titular(fig, "Dos casos críticos del mes nunca visto",
        f"Informa: limitaciones de Guardian y la variable que falta (qué aparato se enciende) · consumo, semáforo y puntaje "
        f"de {ELEG} con los cortes de validación; franjas rosadas = picos")
guardar(fig, "g5", "G5_casos_criticos",
        f"Caso 1 (pico no anticipado con más energía, {fecha_es(c1_['inicio'])}) y caso 2 (aviso falso más largo, "
        f"{fecha_es(c2_['inicio'])}), uno por fila: consumo ±2 h, colores, puntaje y cortes; qué faltó y qué costó")

# ---------------------------------------------------------------- G6: evolución de modelos (póster), pila vertical
hz = lambda k_: CIFRAS["heredadas"][k_]["texto"].replace("-", "−")   # signo menos tipográfico
hv = lambda k_: CIFRAS["heredadas"][k_]["valor"]
nv = lambda k_: CIFRAS["nuevas"][k_]["valor"]
HITOS = [
    ("Taller 2", "1.er corte", "Árbol de decisión y KNN",
     "La raíz del árbol es la hora: el consumo se ordena por la hora a la que despierta el hogar.",
     [("R² árbol", f"{hz('her_reg_arbol_aleatoria_r2')} aleatoria · {hz('her_reg_arbol_temporal_r2')} temporal"),
      ("R² KNN", f"{hz('her_reg_knn_aleatoria_r2')} aleatoria · {hz('her_reg_knn_temporal_r2')} temporal")]),
    ("Taller 3", "1.er corte", "Bosque aleatorio y SVM",
     "El modelo más preciso es el menos robusto en el tiempo: se reportan siempre las dos particiones.",
     [("R² bosque", f"{hz('her_reg_rf_aleatoria_r2')} aleatoria · {hz('her_reg_rf_temporal_r2')} temporal"),
      ("F1 bosque", f"{hz('her_clf_rf_aleatoria_f1')} aleatoria · {hz('her_clf_rf_temporal_f1')} temporal")]),
    ("Parcial 1", "1.er corte", "Retardos: gemelo lineal y detector",
     "El gemelo (función de transición) es la lineal con retardos: los retardos rescatan la partición temporal. El "
     "detector reconoce la lectura actual.",
     [("R² lineal sin retardos", f"{hz('her_reg_lineal_aleatoria_r2')} aleatoria · {hz('her_reg_lineal_temporal_r2')} temporal"),
      ("R² lineal con retardos", f"{hz('her_bo_lineal_retardos_r2')} temporal (en la aleatoria no se usan: filtran)"),
      ("Detector a umbral 0,40 (temporal)", f"{pct_es(hv('her_det040_eventos'))} de picos tocados · F1 por lectura "
                                            f"{num_es(hv('her_det040_f1'), 2)}")]),
    ("Boosting", "2.º corte · Taller 1", "LightGBM, XGBoost y CatBoost",
     "El boosting no reemplaza al gemelo ni al detector: no extrapola a un mes más cálido.",
     [("R² LightGBM", f"{hz('her_bo_lgbm_aleatoria_r2')} aleatoria · {hz('her_bo_lgbm_temporal_r2')} temporal"),
      ("R² temporal con retardos", f"LightGBM {hz('her_bo_lgbm_retardos_r2')} · lineal {hz('her_bo_lineal_retardos_r2')}")]),
    ("Parcial 2", "2.º corte", f"Guardian: {NOMBRE[ELEG]}",
     "La pregunta cambia: avisar antes de que empiece el pico. Con márgenes indistinguibles, se queda lo más simple.",
     [("Picos con ≥ 20 min (solo temporal)", f"{nv('titular_n20')} de {len(ids_te)} ({pct_es(nv('titular_p20'))})"),
      ("Regla de nivel al mismo rojo", f"{nv('titular_m20')} de {len(ids_te)} ({pct_es(nv('titular_m20_pct'))})")]),
]
W_MOD, W_DEC, W_CIF = 24, 34, 40
X_IZQ, X_MED, X_DER = 0.075, 0.33, 0.645
filas6, y6 = [], 0.0
PREG_RECON = "Pregunta: reconocer (¿cuánto consume ahora?, ¿la lectura actual supera 200 Wh?)"
PREG_ANTIC = "Pregunta nueva: anticipar (¿empieza un pico en la próxima media hora?)"
y6 += 1.6                                             # rótulo de la primera pregunta
for i_, (hito_, corte_, mod_, dec_, cifs_) in enumerate(HITOS):
    if i_ == len(HITOS) - 1:
        y6 += 1.9                                     # rótulo de la pregunta nueva
    mod_w = textwrap.fill(mod_, W_MOD); dec_w = textwrap.fill(dec_, W_DEC)
    cif_w = [(lab_, textwrap.fill(val_.replace(" %", " %"), W_CIF)) for lab_, val_ in cifs_]
    n_izq = 1.3 + 1 + 0.3 + mod_w.count("\n") + 1
    n_dec = dec_w.count("\n") + 1
    n_cif = sum(1 + v_.count("\n") + 1 + 0.5 for _, v_ in cif_w) - 0.5
    alto_ = max(n_izq, n_dec, n_cif) + 1.2
    filas6.append((i_, y6, alto_, hito_, corte_, mod_w, dec_w, cif_w))
    y6 += alto_ + 0.7
fig, ax = plt.subplots(figsize=(ANCHO, y6 * LH / 72 / 0.98))
fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
ax.set_xlim(0, 1); ax.set_ylim(y6, 0); ax.axis("off")
ax.text(X_IZQ - 0.02, 0.5, PREG_RECON, fontsize=10.5, color=GRIS_OSC, va="top")
for i_, y0_, alto_, hito_, corte_, mod_w, dec_w, cif_w in filas6:
    ultimo = i_ == len(HITOS) - 1
    if ultimo:
        ax.text(X_IZQ - 0.02, y0_ - 1.6, PREG_ANTIC, fontsize=10.5, color=TINTA, fontweight="bold", va="top")
    ax.add_patch(FancyBboxPatch((X_IZQ - 0.02, y0_), 1 - X_IZQ + 0.01, alto_, boxstyle="round,pad=0,rounding_size=0.008",
                                facecolor="white", edgecolor=TINTA if ultimo else GRIS_CLARO,
                                linewidth=2.2 if ultimo else 1.2, mutation_aspect=ANCHO * 72 * 0.98 / LH))
    ax.scatter([0.022], [y0_ + 1.0], s=80 if ultimo else 55, color=TINTA if ultimo else GRIS, zorder=3, clip_on=False)
    ax.text(X_IZQ, y0_ + 0.6, hito_, fontsize=12, fontweight="bold", va="top")
    ax.text(X_IZQ, y0_ + 0.6 + 1.3, corte_, fontsize=10, va="top", color=GRIS_OSC)
    ax.text(X_IZQ, y0_ + 0.6 + 2.6, mod_w, fontsize=10, va="top", color=GRIS_OSC, linespacing=1.2)
    ax.text(X_MED, y0_ + 0.6, dec_w, fontsize=10.5, va="top", color=TINTA, linespacing=1.2)
    yc_ = y0_ + 0.6
    for lab_, val_ in cif_w:
        ax.text(X_DER, yc_, lab_, fontsize=10, va="top", color=GRIS_OSC)
        ax.text(X_DER, yc_ + 1.05, val_, fontsize=10.5, va="top", color=TINTA, linespacing=1.2,
                fontweight="bold" if ultimo else "normal")
        yc_ += 1.05 + val_.count("\n") + 1 + 0.5
y_l0, y_l1 = filas6[0][1] + 1.0, filas6[-1][1] + 1.0
ax.plot([0.022, 0.022], [y_l0, y_l1], color=GRIS, lw=2, zorder=1, clip_on=False)
titular(fig, "Evolución de los modelos de Shiro: de reconocer a anticipar",
        "Informa: qué decisión de arquitectura dejó cada entrega · cifras en par aleatoria / temporal leídas de las salidas "
        "guardadas de cada cuaderno · el F1 del detector es a umbral 0,40 (el 0,580 de la tabla del proyecto era a 0,5)",
        sobre_ejes=2)
guardar(fig, "g6", "G6_evolucion_modelos",
        "Línea de tiempo vertical Taller 2 → Taller 3 → Parcial 1 → Taller 1 del 2.º corte → Parcial 2 con la decisión de "
        "cada entrega, cifras en par aleatoria/temporal (heredadas; la lineal sin retardos con su par y aparte la temporal "
        "con retardos) y el cambio de pregunta: reconocer → anticipar")
registrar("fig_n", len(FIGS), "", 0, F17, "Figuras exportadas a 300 dpi")
que_cambia(f"informe y póster tienen {len(FIGS)} figuras a 300 dpi trazables a este cuaderno; ninguna dibuja una curva "
           f"'con Shiro', porque no hay modelo del efecto de la acción.")
''')

# =====================================================================================
# 18. Exportación
# =====================================================================================
md(r'''
---
## 18. Exportación: `cifras.json` y `mockup/datos_mockup.json`
**Necesidad de Shiro.** El informe, el póster, la presentación y la página tienen que decir lo mismo. Se exporta una sola
fuente de cifras (valor, texto es-CO, unidad, partición, fuente y descripción) y los datos que la página incrusta: la
serie del mes de prueba con los puntajes, los puntajes de validación para recalcular los cortes con los deslizadores,
los parámetros del elegido si corre en el navegador, la calibración, las reglas del explicador, el gemelo de seis
variables, los momentos de ejemplo y los valores esperados para la autoverificación de la página.
''')

code(r'''
# ---- parámetros del elegido (si es exportable) ----
if ELEG == "G0":
    vn, cn = np.unique(ref_nivel, return_counts=True)
    vh, ch = np.unique(ref_hora, return_counts=True)
    PARAMS = {"tipo": "G0", "exportable": True, "celda": "hora * 2 + es_fin_semana",
              "frecuencias": [float(x) for x in freq.to_numpy()],
              "ecdf_nivel": {"valores": vn.tolist(), "F": (np.cumsum(cn) / cn.sum()).tolist()},
              "ecdf_hora": {"valores": vh.tolist(), "F": (np.cumsum(ch) / ch.sum()).tolist()},
              "p_hora_por_celda": [float(x) for x in ecdf(ref_hora, freq.to_numpy())],
              "formula": "puntaje = F_nivel(consumo actual) + F_hora(frecuencia de la celda); F(x) = fracción de la referencia ≤ x"}
elif ELEG in ("G2", "G5"):
    sc_, lg_ = (SC2, G2) if ELEG == "G2" else (SC5, G5)
    PARAMS = {"tipo": ELEG, "exportable": True, "variables": COLS, "media": sc_.mean_.tolist(), "escala": sc_.scale_.tolist(),
              "coeficientes": lg_.coef_[0].tolist(), "intercepto": float(lg_.intercept_[0]),
              "formula": "p = 1 / (1 + exp(-(intercepto + Σ coef·(x − media)/escala)))"}
elif ELEG == "G3b":
    PARAMS = {"tipo": "G3b", "exportable": True, "variables": COLS, "coeficientes": G3B.coef_.tolist(),
              "intercepto": float(G3B.intercept_), "formula": "puntaje = intercepto + Σ coef·x"}
else:
    PARAMS = {"tipo": ELEG, "exportable": False, "nota": "bosque: solo puntajes precalculados"}

def metricas_card2(m_):
    return {k_: (float(v_) if isinstance(v_, (float, np.floating)) else int(v_)) for k_, v_ in m_.items()}

sel = slice(cl, N)
MOCK = {
    "version": 1, "generado": datetime.datetime.now().isoformat(timespec="seconds"),
    "elegido": {"id": ELEG, "nombre": NOMBRE[ELEG], "nivel": NIVEL[ELEG], "nvars": NVARS[ELEG]},
    "caso": CASO, "frase_caso": FRASE, "umbral_wh": float(UMBRAL), "r_defecto": r, "gap": 3,
    "mediana_wh": float(np.median(A[:cl])),
    "datos": {"nombre": "Appliances Energy Prediction, UCI", "desde": FECHA.iloc[0].isoformat(),
              "hasta": FECHA.iloc[N - 1].isoformat(), "nota": "una sola vivienda; mediana_wh = mediana del consumo antes de la prueba"},
    "incertidumbre": {"p20": float(MD["p20"]), "p20_ic": [float(CIFRAS["nuevas"]["fig2_elegido_desp_p20_ic_inf"]["valor"]),
                                                       float(CIFRAS["nuevas"]["fig2_elegido_desp_p20_ic_sup"]["valor"])],
                      "d_regla": float(CIFRAS["nuevas"]["titular_d_regla"]["valor"]),
                      "d_regla_ic": [float(CIFRAS["nuevas"]["titular_d_regla_ic_inf"]["valor"]),
                                     float(CIFRAS["nuevas"]["titular_d_regla_ic_sup"]["valor"])],
                      "azar_p20": float(azar_teo_d),
                      "nota": "IC 95 % bootstrap por día con el r por defecto; la página solo los muestra con ese r"},
    "cortes_defecto": {"elegido": {"rojo": CORTES[ELEG][0], "amarillo": CORTES[ELEG][1]},
                       "regla": {"rojo": CORTES["regla"][0], "amarillo": CORTES["regla"][1]}},
    "serie_prueba": {"fecha": [f.isoformat() for f in FECHA.iloc[sel]], "wh": A[sel].tolist(),
                     "en_calma": calma[sel].astype(int).tolist(), "rojo_en_curso": en_pico[sel].astype(int).tolist(),
                     "y_ant": y_ant[sel].tolist(), "puntaje_elegido": SCORE[ELEG][sel].tolist(),
                     "puntaje_regla": SCORE["regla"][sel].tolist(),
                     "pico": [int(next((i for i, p in enumerate(ids_te) if S[p] <= t <= E[p]), -1)) if en_pico[t] else -1 for t in range(cl, N)],
                     "ventana_de_pico": [int(np.where(ids_te == ventana_de[t])[0][0]) if ventana_de[t] >= 0 and ventana_de[t] in ids_te else -1 for t in range(cl, N)]},
    "picos_prueba": [{"id": i, "inicio": FECHA.iloc[S[p]].isoformat(), "fin": FECHA.iloc[E[p]].isoformat(),
                      "indice_inicio": int(S[p] - cl), "indice_fin": int(E[p] - cl), "energia_wh": float(energia_pico(p)),
                      "exceso_wh": float(exceso_pico(p)), "anticipable_20": bool(S[p] - 2 >= cl)} for i, p in enumerate(ids_te)],
    "validacion_calma": {"puntaje_elegido": SCORE[ELEG][calma & val_m].tolist(), "puntaje_regla": SCORE["regla"][calma & val_m].tolist(),
                         "desde": FECHA.iloc[n_fit].isoformat(), "hasta": FECHA.iloc[cl - 1].isoformat(),
                         "nota": "cortes = cuantil lineal (numpy) 1−r y 1−2r de estos puntajes"},
    "parametros_elegido": PARAMS,
    "calibracion": {"bordes": BORDES.tolist(), "tasa_validacion": CAL["tasa_val"].tolist(), "tasa_prueba": CAL["tasa_prueba"].tolist(),
                    "tasa_mdp": CAL["tasa_mdp"].tolist(),
                    "n_validacion": CAL["n_val"].astype(int).tolist(), "n_prueba": CAL["n_prueba"].astype(int).tolist(),
                    "regla": "decil = número de bordes ≤ puntaje",
                    "mostrar": "tasa_mdp",
                    "mostrar_rango": RANGO_CAL, "umbral_rango_puntos": UMBRAL_RANGO,
                    "optimismo_max_puntos": float(CAL["dif_mdp_prueba"].iloc[k_opt]), "optimismo_max_decil": k_opt + 1,
                    "nota": ("'De cada 100 momentos así' usa tasa_mdp (validación hecha monótona; es lo que Guardian conoce al "
                             "desplegarse). tasa_prueba es contraste y puede diferir. mostrar_rango[k] = [prueba, validación] "
                             f"en los deciles donde difieren más de {num_es(UMBRAL_RANGO, 0)} puntos (null en los demás): ahí "
                             "mostrar el rango, no una sola cifra. Mayor optimismo: decil "
                             f"{k_opt + 1}, {num_es(CAL['tasa_mdp'].iloc[k_opt], 1)} de cada 100 en validación frente a "
                             f"{num_es(CAL['tasa_prueba'].iloc[k_opt], 1)} en prueba ({num_es(CAL['dif_mdp_prueba'].iloc[k_opt], 1)} "
                             "puntos). Los tramos no tienen el mismo tamaño por empates del puntaje: mostrar n junto a la tasa.")},
    "explicador": {"reglas": [{"texto": rg["texto"], "rojo": rg["rojo"], "n": rg["n"], "prop_rojo": rg["prop_rojo"],
                               "condiciones": [{"variable": f_, "nombre": LLANO.get(f_, f_), "op": op, "umbral": u_} for f_, op, u_ in rg["condiciones"]]}
                              for rg in REGLAS],
                   "fidelidad_pct": fid, "precision_pct": prec_arb, "cobertura_pct": recall_arb, "base_nunca_rojo_pct": base_nunca,
                   "nota": ("Las condiciones se evalúan sobre momento.entradas[variable]; freq_hora_pct está en % (0–100), "
                            "entradas.freq_hora es la misma frecuencia en fracción (0–1) y no la usa el explicador. "
                            "Cada momento trae explicador_rojo y explicador_coincide: si no coinciden, rotular "
                            "'aproximación: aquí el modelo manda'.")},
    "g3c": {"variables": SEIS, "coeficientes": G3C.coef_.tolist(), "intercepto": float(G3C.intercept_),
            "mae_total": float(pg("g3c", "total", "MAE")), "mae_persistencia": float(pg("persistencia", "total", "MAE")),
            "mae_por_franja": {k_: float(pg("g3c", k_, "MAE")) for k_ in CL_FR.values()},
            "sesgo_por_franja": {k_: float(pg("g3c", k_, "sesgo")) for k_ in CL_FR.values()},
            "franjas": {"madrugada": [0, 6], "manana": [6, 12], "tarde": [12, 18], "noche": [18, 24],
                        "nota": "hora h pertenece a la franja [desde, hasta)"},
            "altas_mae": float(pg("g3c", "altas", "MAE")), "altas_sesgo": float(pg("g3c", "altas", "sesgo")),
            "altas_n": int(grupos["altas"].sum()),
            "nota": ("entrenado con todo el entrenamiento (vio la validación); un paso adelante usa lag1 = consumo actual; "
                     "en lecturas > 200 Wh subestima (altas_sesgo < 0): el pronóstico se queda corto en los picos")},
    "momentos_tarjeta1": MOMENTOS, "situaciones_tarjeta4": SITUACIONES, "dia_antes_despues": DIA_AD,
    "casos_criticos": CASOS,
    "esperado": {"tarjeta2_elegido_desplegado": metricas_card2(RES[("desp", ELEG)]),
                 "tarjeta2_regla_mismo_rojo": metricas_card2(M_REGLA),
                 "colores_momentos": [m_["color_esperado"] for m_ in MOMENTOS],
                 "azar_p20_desplegado": azar_teo_d,
                 "exceso_anticipado_kwh": float(exc_ant), "exceso_total_kwh": float(exc_a),
                 "por_lectura": {k_: float(v_) for k_, v_ in LECT.items()},
                 "nota": ("métricas con r por defecto y cortes de validación; antelación ≥ 20 min = rojo en s−3 o s−2; "
                          "tarjeta2_elegido_desplegado y tarjeta2_regla_mismo_rojo tienen el mismo rojo realizado")},
}
SEGUNDOS = time.time() - T0
CIFRAS["meta"] = {"fecha_ejecucion": datetime.datetime.now().isoformat(timespec="seconds"), "segundos": round(SEGUNDOS, 1),
                  "sklearn": sklearn.__version__, "pandas": pd.__version__, "numpy": np.__version__,
                  "python": platform.python_version(), "cuaderno": "Parcial2_Guardian.ipynb"}
Path("mockup").mkdir(exist_ok=True)
with open("cifras.json", "w", encoding="utf-8") as fh:
    json.dump(CIFRAS, fh, ensure_ascii=False, indent=1, allow_nan=False)
with open("mockup/datos_mockup.json", "w", encoding="utf-8") as fh:
    json.dump(MOCK, fh, ensure_ascii=False, allow_nan=False)
print(f"cifras.json: {len(CIFRAS['nuevas'])} nuevas + {len(CIFRAS['heredadas'])} heredadas · "
      f"datos_mockup.json: {num_es(Path('mockup/datos_mockup.json').stat().st_size / 1024, 0)} KB · {num_es(SEGUNDOS)} s")
que_cambia("informe, póster, presentación y página leen las mismas cifras; la página puede recalcular el semáforo "
           "con los deslizadores sin servidor" + (" y calcular el color de Guardian en vivo." if PARAMS["exportable"] else "."))
''')

# =====================================================================================
# 19. Verificación y resumen
# =====================================================================================
md(r'''
---
## 19. Verificación final y resumen de resultados
**Necesidad de Shiro.** Antes de construir la página y los documentos, el grupo necesita saber en pocas líneas qué
modelo maneja Guardian, cuántos picos avisa con margen, a qué costo y qué cambia en Shiro. Se releen los dos JSON y se
validan (claves obligatorias, sin valores no finitos, textos con coma decimal).
''')

code(r'''
C_ = json.load(open("cifras.json", encoding="utf-8"))
M_ = json.load(open("mockup/datos_mockup.json", encoding="utf-8"))
assert all(a["ok"] for a in ANCLAS)
OBLIG = ["caso_letra", "caso_frase", "sel_elegido", "sel_nivel", "titular_n20", "titular_p20", "titular_m20", "titular_m20_pct",
         "titular_min_dia", "caso_d", "caso_ic_inf", "caso_ic_sup", "azar_p20_teorico", "azar_p20_sim", "def_tasa_base_r",
         "energia_exceso_kwh", "energia_exceso_anticipado_kwh", "n1b_persistencia_total_mae", "n1b_g3a_total_mae",
         "n1c_antes_n", "expl_fidelidad", "g0_prueba_p20", "regla_prueba_p20", "g4_val_p20", "g5_val_p20",
         "ancla_det_f1", "def_picos_prueba", "def_picos_validacion", "azar_p20_desplegado", "lect_elegido_exactitud",
         "lect_elegido_f1", "lect_elegido_sensibilidad", "lect_todo_verde_exactitud", "lect_elegido_auc", "datos_n_lecturas",
         "datos_dias", "caso1_puntaje", "caso1_consumo_wh", "caso2_puntaje", "expl_base_nunca_rojo", "cal_para_mdp",
         "part_umbral_p90_temporal", "n1c_antes_ya_encendida_n", "fig2_elegido_desp_p20_ic_inf",
         "cal_deciles_con_rango", "cal_optimismo_max", "caso1_ventana_fragil", "caso1_margen_amarillo_s1",
         "semillas_linea", "semillas_g4_val_p20_media", "semillas_elegido_cambia_n", "semillas_complejo_cambia_n",
         "fig_n"] + [f"fig_g{i}_ruta" for i in range(1, 7)]
faltan = [k for k in OBLIG if k not in C_["nuevas"]]
assert not faltan, faltan
for i in range(1, 7):
    assert Path(C_["nuevas"][f"fig_g{i}_ruta"]["valor"]).exists()
assert len(M_["calibracion"]["mostrar_rango"]) == len(M_["calibracion"]["tasa_mdp"])
assert "ventana_fragil" in M_["casos_criticos"]["pico_no_anticipado"]
for k in ["serie_prueba", "picos_prueba", "validacion_calma", "parametros_elegido", "calibracion", "explicador", "g3c",
          "momentos_tarjeta1", "situaciones_tarjeta4", "dia_antes_despues", "esperado", "r_defecto"]:
    assert k in M_, k
assert len(M_["serie_prueba"]["wh"]) == N - cl and len(M_["momentos_tarjeta1"]) == 5 and len(M_["situaciones_tarjeta4"]) == 4

def recorrer(o):
    if isinstance(o, dict):
        for v in o.values(): yield from recorrer(v)
    elif isinstance(o, list):
        for v in o: yield from recorrer(v)
    else:
        yield o
assert all(not (isinstance(v, float) and not np.isfinite(v)) for v in recorrer(M_))
mal = []
for bloque in ("nuevas", "heredadas"):
    for k, v in C_[bloque].items():
        assert set(v) == {"valor", "texto", "unidad", "particion", "fuente", "descripcion"}, k
        if isinstance(v["valor"], (int, float)):
            assert np.isfinite(v["valor"]), k
            if re.search(r"\d\.\d{1,2}(?!\d)", v["texto"]) or re.search(r"\d\.\d{4,}", v["texto"]):
                mal.append(k)
            if v["unidad"] == "%" and not v["texto"].endswith(" %"):
                mal.append(k)
assert not mal, mal
print(f"Verificación: {len(ANCLAS)} anclas OK · {len(C_['nuevas'])} cifras nuevas y {len(C_['heredadas'])} heredadas válidas · "
      f"datos del mockup completos.")

# ---- Resumen de resultados (≤ 15 líneas) ----
t = lambda k: C_["nuevas"][k]["texto"]
v = lambda k: C_["nuevas"][k]["valor"]
ic = lambda a, b: f"IC 95 % {num_es(v(a))} a {num_es(v(b))} puntos"
if otro is None:
    l4_otro = "."
elif otro[2] > 0:
    l4_otro = f"; la prueba favorece a {mejor_te} por {t('caso_otro_d')} ({ic('caso_otro_ic_inf', 'caso_otro_ic_sup')})."
else:
    l4_otro = (f"; {mejor_te} queda {t('caso_otro_d')} por encima en prueba, sin distinguirse "
               f"({ic('caso_otro_ic_inf', 'caso_otro_ic_sup')}).")
lineas = [
    f"RESUMEN DE RESULTADOS — Shiro Guardian (prueba: {t('def_picos_prueba')} en {t('def_dias_prueba')})",
    f"1. Caso {CASO}. Elegido en validación: {NOMBRE[ELEG]} (nivel {NIVEL[ELEG]}); pasan el piso: {C_['nuevas']['sel_pasan_piso']['texto']}.",
    f"2. Titular: {v('titular_n20')} de {len(ids_te)} picos avisados con ≥ 20 min ({t('titular_p20')}), desplegado con cortes de validación.",
    f"3. Regla de nivel al mismo rojo realizado: {v('titular_m20')} picos ({t('titular_m20_pct')}); diferencia {t('titular_d_regla')} "
    f"({ic('titular_d_regla_ic_inf', 'titular_d_regla_ic_sup')}). Azar a ese rojo ({t('titular_rojo_pct')}): "
    f"{t('azar_p20_desplegado')} (a r = {t('def_tasa_base_r')}: {t('azar_p20_teorico')}).",
    f"4. Diferencia del caso ({par[0]} − {par[1]}, mismo rojo r): {t('caso_d')} ({ic('caso_ic_inf', 'caso_ic_sup')})" + l4_otro,
    f"5. Costo: {num_es(v('titular_min_dia'), 0)} minutos al día en rojo ({t('titular_rojo_pct')} de la calma, presupuesto "
    f"{t('def_tasa_base_r')}), {t('titular_avisos_dia')}, {t('titular_falsos')} de avisos falsos.",
    f"6. Validación (mismo rojo, ≥ 20 min): " + " · ".join(f"{g} {pct_es(RES[('val', g)]['p20'], 0)}" for g in ["regla"] + CANDIDATOS) + ".",
    f"7. Prueba (mismo rojo, ≥ 20 min): " + " · ".join(f"{g} {pct_es(RES[('prueba', g)]['p20'], 0)}" for g in ["regla"] + CANDIDATOS) + ".",
    f"8. Latencia del parcial 1 (0,40): primera alerta antes del inicio en {v('n1c_antes_n')} de {len(ids_te)} picos "
    f"({v('n1c_antes_20_n')} con ≥ 20 min; en {v('n1c_antes_ya_encendida_n')} la alerta ya venía encendida), en el inicio "
    f"{v('n1c_inicio_n')}, después {v('n1c_despues_n')}, nunca {v('n1c_nunca_n')}; en alerta el {t('n1c_alerta_calma_pct')} "
    f"de la calma; con el rojo de Guardian: {t('n1c_det_mismo_r_p20')} a ≥ 20 min.",
    f"9. Persistencia: gemelo MAE {t('n1b_g3a_total_mae')} vs {t('n1b_persistencia_total_mae')}; RMSE {t('n1b_g3a_total_rmse')} vs "
    f"{t('n1b_persistencia_total_rmse')}; sesgo en > 200 Wh {t('n1b_g3a_altas_sesgo')} vs {t('n1b_persistencia_altas_sesgo')}.",
    f"10. Energía: exceso sobre 200 Wh {t('energia_exceso_kwh')}; en picos avisados con ≥ 20 min {t('energia_exceso_anticipado_kwh')} "
    f"({t('energia_exceso_anticipado_pct')}).",
    f"11. Explicador: {t('expl_fidelidad')} de coincidencia con el semáforo en prueba ({t('expl_base_nunca_rojo')} si nunca "
    f"pintara rojo); reproduce el {t('expl_cobertura')} del rojo. Rojo realizado entre señales {t('deriva_rojo_min')}–{t('deriva_rojo_max')}.",
    f"12. Frase: {FRASE}",
]
assert len(lineas) <= 15
RESUMEN_H2 = "\n".join(lineas)
print("\n" + RESUMEN_H2)
print(f"\nTiempo de ejecución hasta la exportación: {num_es(C_['meta']['segundos'])} s (meta.segundos de cifras.json)")
''')

md(r'''
### Página del mockup
La página se arma sin servidor: si existe `mockup/plantilla.html`, su marcador `/*__DATOS__*/` se reemplaza por el
contenido de `mockup/datos_mockup.json` y el resultado se escribe en `Mockup_Shiro_Guardian.html`, en la carpeta de este
cuaderno. La plantilla no lleva ninguna cifra de resultado: todas llegan con los datos.
''')

code(r'''
PLANTILLA = Path("mockup/plantilla.html")
SALIDA_HTML = Path("Mockup_Shiro_Guardian.html")
MARCADOR = "/*__DATOS__*/"
if PLANTILLA.exists():
    html_ = PLANTILLA.read_text(encoding="utf-8")
    assert html_.count(MARCADOR) == 1, f"la plantilla debe tener exactamente un marcador {MARCADOR}"
    datos_ = Path("mockup/datos_mockup.json").read_text(encoding="utf-8").replace("</", "<\\/")   # no cerrar el <script>
    SALIDA_HTML.write_text(html_.replace(MARCADOR, datos_), encoding="utf-8")
    print(f"Página escrita: {SALIDA_HTML} ({num_es(SALIDA_HTML.stat().st_size / 1024, 0)} KB) desde {PLANTILLA} con los datos "
          f"del mockup incrustados.")
else:
    print(f"No existe {PLANTILLA}: la página no se arma en esta ejecución (el resto del cuaderno no depende de ella).")
''')


def construir():
    nb = nbformat.v4.new_notebook()
    nb.cells = CELDAS
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3 (venv ml)", "language": "python"}
    nb.metadata["language_info"] = {"name": "python"}
    return nb


def cargar_cifras():
    if not CIFRAS.exists():
        return None
    with open(CIFRAS, encoding="utf-8") as fh:
        c = json.load(fh)
    return {"nuevas": c.get("nuevas"), "heredadas": c.get("heredadas")}


def main():
    if sys.platform == "win32":
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    previas = cargar_cifras()
    nb = construir()
    t0 = time.time()
    cliente = NotebookClient(nb, timeout=900, kernel_name="python3",
                             resources={"metadata": {"path": str(CARPETA)}})
    try:
        cliente.execute()
    finally:
        nbformat.write(nb, CUADERNO)
    dt = time.time() - t0
    print(f"Cuaderno ejecutado y guardado con salidas: {CUADERNO.name} ({len(nb.cells)} celdas, {dt:.1f} s)")
    # Resumen de resultados y aviso de la página (celdas finales)
    for celda in nb.cells[-3:]:
        if celda.cell_type != "code":
            continue
        for o in celda.get("outputs", []):
            if o.get("output_type") == "stream":
                print(o.get("text", ""))
    nuevas = cargar_cifras()
    # Chequeo de residuos en los entregables: sin nombres de herramientas ni referencias internas de gestión
    import re
    patrones = [r"(?i)claude", r"(?i)\bplan\b", r"\bH[0-9][a-z]?\b", r"\[por calcular\]", r"\bTODO\b", r"\{\{"]
    rutas = [CUADERNO, CIFRAS, CARPETA / "mockup" / "datos_mockup.json"]
    if (CARPETA / "Mockup_Shiro_Guardian.html").exists():
        rutas.append(CARPETA / "Mockup_Shiro_Guardian.html")
    for ruta in rutas:
        texto = ruta.read_text(encoding="utf-8")
        for pat in patrones:
            hallados = sorted(set(m.group(0) for m in re.finditer(pat, texto)))
            assert not hallados, f"residuo {pat!r} en {ruta.name}: {hallados}"
    print("Residuos: ninguno (nombres de herramientas, 'plan', hitos, marcadores) en "
          + ", ".join(r_.name for r_ in rutas) + ".")
    if previas is not None:
        iguales = previas == nuevas
        print(f"DETERMINISTA: {'sí' if iguales else 'NO'} (comparado con el cifras.json anterior, sin 'meta')")
        if not iguales:
            for bloque in ("nuevas", "heredadas"):
                a, b = previas.get(bloque) or {}, nuevas.get(bloque) or {}
                for k in sorted(set(a) | set(b)):
                    if a.get(k) != b.get(k):
                        print("  difiere:", bloque, k, a.get(k, {}).get("valor"), "→", b.get(k, {}).get("valor"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
