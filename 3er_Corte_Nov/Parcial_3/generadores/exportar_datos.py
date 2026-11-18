# -*- coding: utf-8 -*-
r"""Exporta los datos de la consola de Shiro (Parcial 3) desde los cuadernos ya verificados.

Salidas:
    datos/consola.json    todo lo que la página necesita para calcular en vivo (mayo hora a hora y cada 10 min, G0,
                          simulador, K-Means, MDP, Q-learning, red DQN) y los valores ESPERADOS con que verificar.py
                          comprueba que el JavaScript calcula lo mismo que Python
    datos/cifras_p3.json  cifras propias del parcial (tamaños y anclas), con el formato de los demás cifras.json

Fuentes: celdas de preparación del cuaderno del C3-T3 (datos, K-Means y MDP; no entrena nada y ya verifica sus anclas con
el C3-T1), `politicas_base.csv` del C3-T2, `dqn_pesos.json` del C3-T3 y `mockup/datos_mockup.json` del Parcial 2.

Uso (desde la carpeta del parcial):
    C:\Users\pipel\venvs\ml\Scripts\python.exe -X utf8 generadores\exportar_datos.py
"""
import json
import os
import sys
import time
from pathlib import Path

import nbformat
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import C3, PROY, RAIZ  # noqa: E402

T3 = C3 / "Taller_3_DQN"
T2 = C3 / "Taller_2_QLearning"
P2 = PROY / "2do_Corte_Oct" / "Parcial_2_Aprendizaje_Supervisado"
SALIDA = RAIZ / "datos"
CIFRAS = {}
ANCLAS = []


def es(x, dec=1):
    s = f"{x:,.{dec}f}".replace(",", "§").replace(".", ",").replace("§", ".")
    return s.replace("-", "−")


def reg(k, v, t, desc=""):
    CIFRAS[k] = {"valor": v, "texto": t, "fuente": "exportar_datos.py", "descripcion": desc}


def ancla(nombre, ok, detalle=""):
    ANCLAS.append(nombre)
    if not ok:
        raise AssertionError(f"Ancla fallida: {nombre} {detalle}")
    print(f"  ✓ {nombre}")


# ---------------------------------------------------------------------------------------------------------------------
# 1. Celdas de preparación del cuaderno del T3 (1: parámetros, 3: datos, 5: K-Means y rasgos, 7: MDP y anclas con el T1)
# ---------------------------------------------------------------------------------------------------------------------
t0 = time.time()
nb = nbformat.read(T3 / "Taller3_C3_DQN_Shiro.ipynb", as_version=4)
ns = {"__name__": "t3"}
cwd = os.getcwd()
os.chdir(T3)
import matplotlib  # noqa: E402
matplotlib.use("Agg")
try:
    for i in (1, 3, 5, 7):
        src = "\n".join(ln for ln in nb.cells[i].source.splitlines() if not ln.lstrip().startswith(("%", "!")))
        exec(compile(src, f"T3-celda-{i}", "exec"), ns)
finally:
    os.chdir(cwd)
print(f"Preparación del T3 ejecutada en {time.time() - t0:.1f} s (incluye sus anclas con el T1)")

H, TE, mU, QSTAR, piU = ns["H"], ns["TE"], ns["mU"], ns["QSTAR"], ns["piU"]
MDP, iteracion_valor, politica_de = ns["MDP"], ns["iteracion_valor"], ns["politica_de"]
TR = ns["TR"]
DIAS_TE = [d.strftime("%Y-%m-%d") for d in ns["DIAS_TE"]]
ACC = {"No actuar": 0, "Aplazar": 1, "Ejecutar": 2}

print("Anclas del exportador:")
# π* recalculada = política óptima publicada en el T1
t1_pol = pd.read_csv(C3 / "Taller_1_RL_MDP" / "politica_optima_shiro.csv")
pol_t1 = {r["Estado (s)"]: ACC[r["Acción óptima (a)"]] for _, r in t1_pol.iterrows()}
ancla("π* (λ = 0,005, punta 1,5) igual a politica_optima_shiro.csv en los 40 estados",
      all(pol_t1[s] == int(piU[i]) for i, s in enumerate(mU.S)) and len(pol_t1) == mU.nS)

# ---------------------------------------------------------------------------------------------------------------------
# 2. Mayo hora a hora (lo que ve el agente) y K-Means
# ---------------------------------------------------------------------------------------------------------------------
horas = []
for r in TE.itertuples(index=False):
    horas.append({"d": DIAS_TE.index(r.dia.strftime("%Y-%m-%d")), "h": int(r.hora), "media": round(float(r.media), 3),
                  "wh": round(float(r.wh), 3), "logw": round(float(r.logw), 6), "logw_prev": round(float(r.logw_prev), 6),
                  "tipo": int(r.tipo), "margen": round(float(r.margen), 6), "franja": int(r.franja),
                  "nivel": int(r.nivel_umbral), "x": r.x_umbral})
NIVEL_DIA = ns["NIVEL_DIA"]
kmeans = {"C": np.round(ns["C"], 6).tolist(), "alto": int(ns["ALTO"]), "hora_tipo": int(ns["HORA_TIPO"]),
          "nivel_bajo": float(ns["NIVEL_BAJO"]), "umbral": float(ns["UMBRAL"]),
          "curvas_mayo": [np.round(NIVEL_DIA.loc[pd.Timestamp(d)].values, 3).tolist() for d in DIAS_TE],
          "formula": "tipo/margen con las primeras h horas de la curva (h ≥ hora_tipo); margen = (d_normal − d_alto)/(d_normal + d_alto)"}
# Ancla: recalcular tipo y margen con la fórmula exportada (la misma que hará la página)
Cc = np.array(kmeans["C"]); A = kmeans["alto"]
err = 0.0
for hh in horas:
    curva = np.array(kmeans["curvas_mayo"][hh["d"]]); h = hh["h"]
    if h < kmeans["hora_tipo"]:
        t, m = 0, 0.0
    else:
        dd = np.sqrt(((Cc[:, :h] - curva[:h]) ** 2).sum(1)); t = int(np.argmin(dd) == A)
        m = float((dd[1 - A] - dd[A]) / (dd[1 - A] + dd[A] + 1e-9))
    err = max(err, abs(m - hh["margen"])); assert t == hh["tipo"]
ancla("tipo y margen de K-Means recalculados con la fórmula exportada (624 horas de mayo)", err < 1e-4, f"error {err}")

# ---------------------------------------------------------------------------------------------------------------------
# 3. MDP para resolverlo en la página, y políticas de referencia en una rejilla de λ y tarifa
# ---------------------------------------------------------------------------------------------------------------------
mdp = {"X": mU.X, "S": mU.S, "P": np.round(mU.P, 10).tolist(), "E": np.round(mU.E, 10).tolist(), "F": mU.F.tolist(),
       "N": mU.N.tolist(), "DE_wh": float(mU.DE), "gamma": float(ns["GAMMA"]), "theta": float(ns["THETA"]),
       "lam_def": float(ns["LAMBDA"]), "lam_ex": float(ns["LAMBDA_EX"]), "punta_def": float(ns["R_PUNTA"]),
       "nota": "costo: no actuar tar·E; aplazar tar·(E−ΔE)+1,0·ΔE; ejecutar tar·E+(tar−1)·ΔE; r = −costo − λ·pendiente siguiente"}
ref = {}
for lam in (0.0, 0.002, 0.005, 0.01, 0.02, 0.03, 0.05):
    for rp in (1.0, 1.2, 1.5, 2.0, 3.0):
        m_ = MDP(TR, r_punta=rp, lam=lam); _, Q_, it_ = iteracion_valor(m_); pol_ = politica_de(Q_, m_.VALID)
        ref[f"{lam}|{rp}"] = {"pol": pol_.astype(int).tolist(), "it": int(it_),
                              "Q": [[(round(float(q), 8) if np.isfinite(q) else None) for q in fila] for fila in Q_]}
QS = ref[f"{mdp['lam_def']}|{mdp['punta_def']}"]["Q"]
ancla("VI de la rejilla en (0,005; 1,5) reproduce la Q* del cuaderno",
      np.nanmax(np.abs(np.where(np.isfinite(QSTAR), QSTAR, np.nan) - np.array([[np.nan if q is None else q for q in f] for f in QS],
                                                                              float))) < 1e-6)

# Q-learning (consenso de las semillas, T2)
ql_csv = pd.read_csv(T2 / "politicas_base.csv")
ql = {r["Estado"]: ACC[r["Q-learning recomendado (consenso)"]] for _, r in ql_csv.iterrows()}
ancla("política de Q-learning cubre los 40 estados del MDP", set(ql) == set(mU.S))

# ---------------------------------------------------------------------------------------------------------------------
# 4. Red DQN del T3 y vectores de prueba
# ---------------------------------------------------------------------------------------------------------------------
pesos = json.loads((T3 / "dqn_pesos.json").read_text(encoding="utf-8"))
Pw = {k: np.array(v) for k, v in pesos["capas"].items()}


def q_red(X):
    a1 = np.maximum(0, X @ Pw["W1"] + Pw["b1"]); a2 = np.maximum(0, a1 @ Pw["W2"] + Pw["b2"])
    return a2 @ Pw["W3"] + Pw["b3"]


rng = np.random.default_rng(42)
pruebas = []
for _ in range(50):
    hh = horas[int(rng.integers(len(horas)))]; p = int(rng.integers(2)); hp = int(rng.integers(0, 19)) if p else 0
    h = hh["h"]
    x = [np.sin(2 * np.pi * h / 24), np.cos(2 * np.pi * h / 24), (hh["logw"] - pesos["mu_logw"]) / pesos["sd_logw"],
         (hh["logw_prev"] - pesos["mu_logw"]) / pesos["sd_logw"], hh["margen"], float(hh["franja"] != 0), p, hp / 24,
         float(hh["nivel"] == 2)]
    pruebas.append({"x": [float(v) for v in x], "q": q_red(np.array([x]))[0].round(10).tolist()})
pesos["pruebas"] = pruebas
ancla("red DQN: 9 → 64 → 64 → 3 y 50 vectores de prueba con su Q esperado",
      Pw["W1"].shape == (9, 64) and Pw["W3"].shape == (64, 3) and len(pruebas) == 50)

# ---------------------------------------------------------------------------------------------------------------------
# 5. Mayo cada 10 minutos: G0 (Parcial 2) y simulador lineal de 6 variables (G3c, hallazgo 17)
# ---------------------------------------------------------------------------------------------------------------------
dm = json.loads((P2 / "mockup" / "datos_mockup.json").read_text(encoding="utf-8"))
sp = dm["serie_prueba"]; g3c = dm["g3c"]
df = pd.read_csv(PROY / "data set" / "energydata_complete.csv", parse_dates=["date"]).set_index("date")
df["lag1"] = df["Appliances"].shift(1)
fechas = pd.to_datetime(sp["fecha"])
sub = df.loc[fechas]
X6 = np.column_stack([sub.index.hour if v == "hora" else sub[v].values for v in g3c["variables"]])
pred = g3c["intercepto"] + X6 @ np.array(g3c["coeficientes"])
real = np.array(sp["wh"], float)
ancla("la serie de mayo del Parcial 2 coincide con el CSV", np.allclose(sub["Appliances"].values, real))
mae = float(np.mean(np.abs(pred - real)))
cut = dm["cortes_defecto"]["elegido"]
punt = np.array(sp["puntaje_elegido"], float)
color = np.where(punt >= cut["rojo"], 2, np.where(punt >= cut["amarillo"], 1, 0))
lect = {"t": [f.strftime("%Y-%m-%dT%H:%M") for f in fechas], "wh": real.round(1).tolist(), "g0": punt.round(6).tolist(),
        "color": color.astype(int).tolist(), "en_calma": [int(v) for v in sp["en_calma"]], "pico": [int(v) for v in sp["pico"]],
        "sim": pred.round(2).tolist(), **{v: X6[:, j].round(3).tolist() for j, v in enumerate(g3c["variables"]) if v != "hora"}}
reg("sim6_mae_mayo", mae, es(mae, 2) + " Wh", "MAE del simulador lineal de 6 variables (G3c) en las lecturas de mayo")
print(f"  · simulador de 6 variables en mayo: MAE {mae:.2f} Wh ({len(real)} lecturas)")

# ---------------------------------------------------------------------------------------------------------------------
# 6. Escribir
# ---------------------------------------------------------------------------------------------------------------------
consola = {"meta": {"generado": time.strftime("%Y-%m-%d %H:%M"), "fuentes": ["C3-T3 cuaderno (celdas 1, 3, 5, 7)",
                                                                         "C3-T2 politicas_base.csv", "C3-T3 dqn_pesos.json",
                                                                         "Parcial 2 mockup/datos_mockup.json"]},
           "dias": DIAS_TE, "horas": horas, "kmeans": kmeans, "mdp": mdp, "ref_vi": ref, "ql": ql, "dqn": pesos,
           "lecturas": lect, "g0": {"cortes": dm["cortes_defecto"], "incertidumbre": dm["incertidumbre"],
                                    "r_defecto": dm["r_defecto"], "parametros": dm["parametros_elegido"]},
           "sim": g3c}
SALIDA.mkdir(exist_ok=True)
(SALIDA / "consola.json").write_text(json.dumps(consola, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
reg("n_dias_mayo", len(DIAS_TE), es(len(DIAS_TE), 0), "días completos de mayo en la consola")
reg("n_horas_mayo", len(horas), es(len(horas), 0), "horas de mayo que recorre el agente")
reg("n_lecturas_mayo", len(real), es(len(real), 0), "lecturas de 10 min de mayo con G0 y simulador")
reg("n_rejilla_vi", len(ref), es(len(ref), 0), "combinaciones (λ, tarifa) con política de referencia para verificar la VI en la página")
reg("n_anclas_exportador", len(ANCLAS), es(len(ANCLAS), 0), "anclas superadas por exportar_datos.py")
(SALIDA / "cifras_p3.json").write_text(json.dumps({"meta": consola["meta"], "cifras": CIFRAS}, ensure_ascii=False, indent=1,
                                                  default=float), encoding="utf-8")
kb = (SALIDA / "consola.json").stat().st_size / 1024
print(f"consola.json {kb:,.0f} KB · cifras_p3.json {len(CIFRAS)} cifras · {len(ANCLAS)} anclas OK · {time.time() - t0:.1f} s")
