"""Exporta la fuente única de cifras del 2.º corte (K-Means, jerárquico, DBSCAN) para el Parcial 3.

Recalcula lo barato reutilizando el código de los cuadernos C2-T2, C2-T3 y C2-T4 y compara cada valor
con la salida guardada de su cuaderno (ANCLAS). Si alguna no coincide al decimal mostrado, termina con
código 1 y no escribe nada.

Salidas (carpeta ../datos/): cifras_c2.json y dbscan_mayo.json.
Ejecutar:  C:\\Users\\pipel\\venvs\\ml\\Scripts\\python.exe -X utf8 exportar_c2.py
"""
import json
import re
import sys
import warnings
from datetime import datetime
from pathlib import Path

import nbformat
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.stats import chi2_contingency
from sklearn.cluster import DBSCAN, KMeans
from sklearn.metrics import adjusted_rand_score, pairwise_distances, silhouette_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

warnings.filterwarnings("ignore")

RS = 42
AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
DATOS = AQUI.parent / "datos"
C2 = RAIZ / "2do_Corte_Oct"
NB = {"T2": C2 / "Taller_2_KMeans" / "Taller2_KMeans.ipynb",
      "T3": C2 / "Taller_3_Jerarquico" / "Taller3_Jerarquico.ipynb",
      "T4": C2 / "Taller_4_DBSCAN" / "Taller4_DBSCAN.ipynb"}
NOMBRE = {"T2": "Taller2_KMeans.ipynb", "T3": "Taller3_Jerarquico.ipynb", "T4": "Taller4_DBSCAN.ipynb"}
CSV = RAIZ / "data set" / "energydata_complete.csv"


# ───────────────────────── utilidades ─────────────────────────
def leer_salidas(ruta):
    nb = nbformat.read(ruta, 4)
    out = {}
    for i, c in enumerate(nb.cells):
        if c.cell_type != "code":
            continue
        txt = ""
        for o in c.get("outputs", []):
            txt += o.get("text") or o.get("data", {}).get("text/plain", "")
        out[i] = txt
    return out


SAL = {k: leer_salidas(v) for k, v in NB.items()}


def es(x, dec=0, signo=False):
    """Formato es-CO: coma decimal, punto de miles, signo menos tipográfico."""
    s = f"{abs(x):,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if x < 0 and float(f"{abs(x):.{dec}f}") != 0:
        return "−" + s
    return ("+" + s) if signo and float(f"{abs(x):.{dec}f}") != 0 else s


CIFRAS = {}
ANCLAS = []      # (clave, calculado, guardado, ok)
FALLOS = []


def cif(clave, valor, texto, fuente, descripcion):
    if isinstance(valor, (np.floating, np.integer)):
        valor = valor.item()
    CIFRAS[clave] = {"valor": valor, "texto": texto, "fuente": fuente, "descripcion": descripcion}


def ancla(clave, calculado, nb, celda, patron, dec, grupo=1, signo=False):
    """Compara `calculado` con el número que la salida guardada del cuaderno muestra en `celda`."""
    txt = SAL[nb][celda]
    m = re.search(patron, txt)
    if not m:
        FALLOS.append(f"{clave}: patrón no encontrado en {NOMBRE[nb]} c.{celda}: {patron}")
        return
    guardado = float(m.group(grupo).replace(",", ""))
    ok = round(float(calculado), dec) == round(guardado, dec)
    ANCLAS.append((clave, round(float(calculado), dec), guardado, ok, f"{NOMBRE[nb]} c.{celda}"))
    if not ok:
        FALLOS.append(f"{clave}: recalculado {round(float(calculado), dec)} ≠ guardado {guardado} "
                      f"({NOMBRE[nb]} c.{celda})")


def desde_salida(nb, celda, patron, grupo=1):
    m = re.search(patron, SAL[nb][celda])
    if not m:
        FALLOS.append(f"no se pudo leer {patron} en {NOMBRE[nb]} c.{celda}")
        return float("nan")
    return float(m.group(grupo).replace(",", ""))


def ordenar(labels, V):
    u = np.unique(labels)
    tot = np.array([V[labels == c].sum(axis=1).mean() for c in u])
    mapa = {u[old]: new for new, old in enumerate(np.argsort(tot))}
    return np.vectorize(mapa.get)(labels)


def dunn_index(X, labels):                       # idéntica a la de los cuadernos
    distances = pairwise_distances(X)
    unique_clusters = np.unique(labels)
    min_inter, max_intra = np.inf, 0
    for i in unique_clusters:
        idx_i = np.where(labels == i)[0]
        if len(idx_i) > 1:
            max_intra = max(max_intra, np.max(distances[np.ix_(idx_i, idx_i)]))
        for j in unique_clusters:
            if i != j:
                idx_j = np.where(labels == j)[0]
                min_inter = min(min_inter, np.min(distances[np.ix_(idx_i, idx_j)]))
    return 0 if max_intra == 0 else min_inter / max_intra


def kdist(V, ms):
    return NearestNeighbors(n_neighbors=ms).fit(V).kneighbors(V)[0][:, -1]


def rodilla(kd):
    y = np.sort(kd)
    x = np.arange(len(y))
    xn, yn = x / x[-1], (y - y[0]) / (y[-1] - y[0])
    i = int(np.argmax(xn - yn))
    return y[i], i


def cramer(a, b):
    ct = pd.crosstab(a, b).values
    chi2, p, _, _ = chi2_contingency(ct)
    return np.sqrt(chi2 / (ct.sum() * (min(ct.shape) - 1))), p


# ───────────────────────── datos ─────────────────────────
df = pd.read_csv(CSV, parse_dates=["date"])
df["dia"] = df["date"].dt.normalize()
df["hora"] = df["date"].dt.hour
lecturas = df.groupby("dia").size()
d = df[df["dia"].isin(lecturas[lecturas == 144].index)].copy()
NIVEL = d.groupby(["dia", "hora"])["Appliances"].mean().unstack()
NIVEL.columns = [f"h{h:02d}" for h in NIVEL.columns]
X = NIVEL.values
assert X.shape == (136, 24)
info = pd.DataFrame(index=NIVEL.index)
info["fin_de_semana"] = (info.index.dayofweek >= 5).astype(int)
info["mes"] = info.index.month
info["kwh_dia"] = d.groupby("dia")["Appliances"].sum() / 1000
tr = (info.index <= "2016-04-30")
assert tr.sum() == 110 and (~tr).sum() == 26


def km(k, V=X, n_init=10):
    return KMeans(n_clusters=k, n_init=n_init, random_state=RS)


# ═════════════ C2-T2 · K-Means ═════════════
F2 = NOMBRE["T2"]
inercia = {k: km(k).fit(X).inertia_ for k in (1, 2, 3)}
LAB2 = {k: ordenar(km(k).fit_predict(X), X) for k in (2, 3)}
lab2 = LAB2[2]
sil2, sil3 = silhouette_score(X, lab2), silhouette_score(X, LAB2[3])
dunn2 = dunn_index(X, lab2)
caida = (1 - inercia[2] / inercia[1]) * 100
n_normal, n_alta = int((lab2 == 0).sum()), int((lab2 == 1).sum())
kwh_n, kwh_a = info["kwh_dia"][lab2 == 0].mean(), info["kwh_dia"][lab2 == 1].mean()
v_finde, p_finde = cramer(lab2, info["fin_de_semana"])
v_mes, p_mes = cramer(lab2, info["mes"])
pct_finde_n = info["fin_de_semana"][lab2 == 0].mean() * 100
pct_finde_a = info["fin_de_semana"][lab2 == 1].mean() * 100

ancla("km_silueta", sil2, "T2", 10, r"\n2\s+[\d.e+]+\s+([\d.]+)", 4)
ancla("km_silueta_k3", sil3, "T2", 10, r"\n3\s+[\d.e+]+\s+([\d.]+)", 4)
ancla("km_dunn", dunn2, "T2", 10, r"\n2\s+[\d.e+]+\s+[\d.]+\s+([\d.]+)", 4)
ancla("km_inercia_k2", inercia[2], "T2", 10, r"\n2\s+([\d.e+]+)", -1)   # la salida muestra 7 cifras significativas
ancla("km_n_normal", n_normal, "T2", 19, r"dias\s+[\d.]+\s+([\d.]+)", 0)
ancla("km_n_alta", n_alta, "T2", 19, r"dias\s+([\d.]+)", 0)
ancla("km_kwh_normal", kwh_n, "T2", 19, r"kwh_dia\s+[\d.]+\s+([\d.]+)", 2)
ancla("km_kwh_alta", kwh_a, "T2", 19, r"kwh_dia\s+([\d.]+)", 2)
ancla("km_cramer_finde", v_finde, "T2", 19, r"fin de semana\s*: V de Cramér = ([\d.]+)", 3)
ancla("km_p_mes", p_mes, "T2", 19, r"mes\s*: V de Cramér = [\d.]+ \(p = ([\d.]+)\)", 3)
ancla("km_cramer_mes", v_mes, "T2", 19, r"mes\s*: V de Cramér = ([\d.]+)", 3)

cif("km_silueta", sil2, es(sil2, 3), f"{F2} c.10", "Silueta de K-Means k=2 sobre los 136 días (curva en Wh sin estandarizar)")
cif("km_silueta_k3", sil3, es(sil3, 3), f"{F2} c.10", "Silueta de K-Means k=3")
cif("km_dunn", dunn2, es(dunn2, 3), f"{F2} c.10", "Índice de Dunn de K-Means k=2 (máximo del barrido)")
cif("km_caida_inercia", caida, es(caida, 0) + " %", f"{F2} c.10",
    "Caída de la inercia al pasar de k=1 a k=2 (el codo)")
cif("km_n_normal", n_normal, f"{n_normal} días", f"{F2} c.19", "Días del tipo «día normal» (k=2)")
cif("km_n_alta", n_alta, f"{n_alta} días", f"{F2} c.19", "Días del tipo «día de carga alta» (k=2)")
cif("km_kwh_normal", kwh_n, es(kwh_n, 1) + " kWh", f"{F2} c.19", "Consumo medio del día normal")
cif("km_kwh_alta", kwh_a, es(kwh_a, 1) + " kWh", f"{F2} c.19", "Consumo medio del día de carga alta")
cif("km_cramer_finde", v_finde, es(v_finde, 3), f"{F2} c.19",
    f"V de Cramér entre tipo de día y fin de semana ({es(pct_finde_a, 0)} % de los de carga alta frente a {es(pct_finde_n, 0)} % de los normales son fin de semana)")
cif("km_p_mes", p_mes, es(p_mes, 3), f"{F2} c.19", "Valor p de la asociación entre tipo de día y mes (V de Cramér)")
cif("km_cramer_mes", v_mes, es(v_mes, 3), f"{F2} c.19", "V de Cramér entre tipo de día y mes")

# árbol de profundidad 2
arbol = DecisionTreeClassifier(max_depth=2, random_state=RS).fit(NIVEL, lab2)
acc_arbol = arbol.score(NIVEL, lab2) * 100
ancla("km_arbol_h13", acc_arbol, "T2", 21, r"en el ([\d.]+) % de los días", 1)
cif("km_arbol_h13", acc_arbol, es(acc_arbol, 1) + " %", f"{F2} c.21",
    "Un árbol de profundidad 2 (raíz h13 ≤ 199 Wh) reproduce el clúster de carga alta en este % de los días")

# observabilidad: asignar con la curva parcial
cen2 = np.vstack([X[lab2 == c].mean(axis=0) for c in (0, 1)])
obs = []
for h in range(24):
    dist = ((X[:, None, :h + 1] - cen2[None, :, :h + 1]) ** 2).sum(axis=2)
    par = dist.argmin(axis=1)
    obs.append(((par == lab2).mean() * 100, (par[lab2 == 1] == 1).mean() * 100))
base_normal = (lab2 == 0).mean() * 100
ancla("km_obs_8h", base_normal, "T2", 34, r"Línea base \(decir siempre «día normal»\): ([\d.]+) %", 1)
ancla("km_obs_8h_acierto", obs[8][0], "T2", 34, r"\n8\s+([\d.]+)", 1)
ancla("km_obs_12h", obs[12][1], "T2", 34, r"\n12\s+[\d.]+\s+([\d.]+)", 1)
ancla("km_obs_12h_acierto", obs[12][0], "T2", 34, r"\n12\s+([\d.]+)", 1)
ancla("km_obs_17h", obs[17][1], "T2", 34, r"\n17\s+[\d.]+\s+([\d.]+)", 1)
cif("km_obs_8h", base_normal, es(base_normal, 1) + " %", f"{F2} c.34",
    f"Línea base «decir siempre día normal» (79,4 %), que es el listón que la asignación con la curva observada hasta las 8 h no supera: esa asignación acierta {es(obs[8][0], 1)} %")
cif("km_obs_8h_acierto", obs[8][0], es(obs[8][0], 1) + " %", f"{F2} c.34",
    "Días bien asignados con la curva observada hasta las 8 h (peor que la línea base)")
cif("km_obs_12h", obs[12][1], es(obs[12][1], 1) + " %", f"{F2} c.34",
    f"Días de carga alta reconocidos con la curva observada hasta las 12 h (aciertos totales {es(obs[12][0], 1)} %)")
cif("km_obs_12h_acierto", obs[12][0], es(obs[12][0], 1) + " %", f"{F2} c.34",
    "Días bien asignados (ambos tipos) con la curva observada hasta las 12 h")
cif("km_obs_17h", obs[17][1], es(obs[17][1], 1) + " %", f"{F2} c.34",
    "Días de carga alta reconocidos con la curva observada hasta las 17 h")

# control temporal: ajustar con enero–abril
km_tr = KMeans(n_clusters=2, n_init=10, random_state=RS).fit(X[tr])
alto = int(np.argmax(km_tr.cluster_centers_.sum(axis=1)))
frac_tr = (km_tr.labels_ == alto).mean() * 100
frac_my = (km_tr.predict(X[~tr]) == alto).mean() * 100
d_tr = km_tr.transform(X[tr]).min(axis=1)
d_my = km_tr.transform(X[~tr]).min(axis=1)
fuera_p95 = int((d_my > np.percentile(d_tr, 95)).sum())
ancla("km_alta_tr", frac_tr, "T2", 31, r"entrenamiento ([\d.]+) %", 1)
ancla("km_alta_te", frac_my, "T2", 31, r"mayo ([\d.]+) %", 1)
ancla("km_mayo_fuera_p95", fuera_p95, "T2", 31, r"percentil 95 del entrenamiento: (\d+) de", 0)
cif("km_alta_tr", frac_tr, es(frac_tr, 1) + " %", f"{F2} c.31",
    "Proporción de días de carga alta en enero–abril (K-Means ajustado con 110 días)")
cif("km_alta_te", frac_my, es(frac_my, 1) + " %", f"{F2} c.31", "Proporción de días de carga alta en mayo (26 días)")
cif("km_mayo_fuera_p95", fuera_p95, f"{fuera_p95} de 26", f"{F2} c.31",
    "Días de mayo más lejos que el p95 del entrenamiento (ningún tipo nuevo)")

# ═════════════ C2-T3 · jerárquico ═════════════
F3 = NOMBRE["T3"]
Zw, Zc, Za = (linkage(X, method=m) for m in ("ward", "complete", "average"))
WARD = ordenar(fcluster(Zw, 2, "maxclust"), X)
COMP = ordenar(fcluster(Zc, 2, "maxclust"), X)
AVG = fcluster(Za, 2, "maxclust")
ari_w_km = adjusted_rand_score(lab2, WARD)
ari_c_km = adjusted_rand_score(lab2, COMP)
ari_wc = adjusted_rand_score(WARD, COMP)
coin_w = int((WARD == lab2).sum())
coin_c = int((COMP == lab2).sum())
coin_wc = int((WARD == COMP).sum())
sil_avg = silhouette_score(X, AVG)
dunn_avg = dunn_index(X, AVG)
tam_avg = sorted(np.bincount(AVG)[1:].tolist(), reverse=True)
sil_w3 = silhouette_score(X, fcluster(Zw, 2, "maxclust"))

ancla("ward_ari_kmeans", ari_w_km, "T3", 38, r"ward\s+· ARI con K-Means ([\d.]+)", 3)
ancla("ward_complete_ari", ari_wc, "T3", 25, r"ARI ([\d.]+) ·", 3)
ancla("ward_complete_coinciden", coin_wc, "T3", 25, r"coinciden en (\d+) de", 0)
ancla("ward_cambian_kmeans", 136 - coin_w, "T3", 38, r"ward\s+· ARI con K-Means [\d.]+ · días con distinto tipo: (\d+)", 0)
ancla("complete_ari_kmeans", ari_c_km, "T3", 38, r"complete\s+· ARI con K-Means ([\d.]+)", 3)
ancla("avg_silueta", sil_avg, "T3", 10, r"\n2\s+0\.400\s+0\.414\s+([\d.]+)", 3)
ancla("avg_dunn", dunn_avg, "T3", 10, r"\n2\s+0\.272\s+0\.287\s+([\d.]+)", 3)
ancla("ward_silueta", sil_w3, "T3", 10, r"\n2\s+([\d.]+)\s+0\.414", 3)

cif("ward_ari_kmeans", ari_w_km, es(ari_w_km, 3), f"{F3} c.38", "ARI entre Ward (k=2) y K-Means (k=2)")
cif("complete_ari_kmeans", ari_c_km, es(ari_c_km, 3), f"{F3} c.38", "ARI entre complete (k=2) y K-Means (k=2)")
cif("ward_complete_ari", ari_wc, es(ari_wc, 3), f"{F3} c.25", "ARI entre Ward y complete (k=2; mismos tamaños 114 / 22)")
cif("ward_coinciden", coin_w, f"{coin_w} de 136", f"{F3} c.38", "Días en que Ward y K-Means asignan el mismo tipo")
cif("complete_coinciden", coin_c, f"{coin_c} de 136", f"{F3} c.38", "Días en que complete y K-Means asignan el mismo tipo")
cif("ward_complete_coinciden", coin_wc, f"{coin_wc} de 136", f"{F3} c.25", "Días en que Ward y complete asignan el mismo tipo")
cif("ward_cambian_kmeans", 136 - coin_w, f"{136 - coin_w} días", f"{F3} c.38",
    "Días en que Ward y K-Means discrepan; todos en el 20 % de días más cercanos a la frontera")
cif("avg_silueta", sil_avg, es(sil_avg, 3), f"{F3} c.10",
    f"Silueta de average con k=2: la mejor, pero aísla {tam_avg[-1]} solo día (tamaños {tam_avg[0]} / {tam_avg[1]})")
cif("avg_dunn", dunn_avg, es(dunn_avg, 3), f"{F3} c.10", "Dunn de average con k=2 (partición de 135 / 1)")
cif("avg_tam_menor", tam_avg[-1], f"{tam_avg[-1]} día", f"{F3} c.10", "Tamaño del clúster más pequeño de average con k=2")

# estabilidad: ajustar con 110 días y comparar con el ajuste de 136
def ajustar(nombre, V):
    if nombre == "kmeans":
        return ordenar(KMeans(n_clusters=2, n_init=10, random_state=RS).fit_predict(V), V)
    return ordenar(fcluster(linkage(V, nombre), 2, "maxclust"), V)

est = {}
for nom in ("kmeans", "ward", "complete"):
    todo, solo = ajustar(nom, X), ajustar(nom, X[tr])
    est[nom] = adjusted_rand_score(todo[tr], solo)
ancla("estab_ari_kmeans", est["kmeans"], "T3", 42, r"\nK-Means\s+([\d.]+)", 3)
ancla("estab_ari_ward", est["ward"], "T3", 42, r"\nWard\s+([\d.]+)", 3)
ancla("estab_ari_complete", est["complete"], "T3", 42, r"\ncomplete\s+([\d.]+)", 3)
cif("estab_ari_kmeans", est["kmeans"], es(est["kmeans"], 3), f"{F3} c.42", "ARI de K-Means ajustado con 110 días frente a 136 días (sobre los mismos 110)")
cif("estab_ari_ward", est["ward"], es(est["ward"], 3), f"{F3} c.42", "ARI de Ward ajustado con 110 días frente a 136 días")
cif("estab_ari_complete", est["complete"], es(est["complete"], 3), f"{F3} c.42", "ARI de complete ajustado con 110 días frente a 136 días")

# ═════════════ C2-T4 · DBSCAN ═════════════
F4 = NOMBRE["T4"]
TIPO = lab2           # mismo K-Means (n_init=10, semilla 42) y mismo orden: 0 normal, 1 carga alta
MS = 5
eps_t, ETQ_TIPO = {}, np.full(136, -1)
for t in (0, 1):
    idx = np.where(TIPO == t)[0]
    e, _ = rodilla(kdist(X[idx], MS))
    eps_t[t] = e
    lab = DBSCAN(eps=e, min_samples=MS).fit_predict(X[idx])
    ETQ_TIPO[idx[lab >= 0]] = lab[lab >= 0] + (0 if t == 0 else 1)
ratio = eps_t[1] / eps_t[0]
ancla("db_eps_normal", eps_t[0], "T4", 10, r"día normal\s+108\s+([\d.]+)", 1)
ancla("db_eps_alta", eps_t[1], "T4", 10, r"día de carga alta\s+28\s+([\d.]+)", 1)
ancla("db_ratio_eps", ratio, "T4", 10, r"están ([\d.]+) veces más dispersos", 1)
cif("db_eps_normal", eps_t[0], es(eps_t[0], 0) + " Wh", f"{F4} c.10", "eps (codo de la k-distancia, min_samples=5) del día normal")
cif("db_eps_alta", eps_t[1], es(eps_t[1], 0) + " Wh", f"{F4} c.10", "eps del día de carga alta")
cif("db_ratio_eps", ratio, es(ratio, 1) + "×", f"{F4} c.10", "Cuántas veces más dispersos son los días de carga alta que los normales")

# atípicos robustos: ruido en ≥ 80 % de 25 configuraciones (factor de eps × min_samples)
FACT, MSR = (0.8, 0.9, 1.0, 1.1, 1.2), (3, 4, 5, 6, 8)
veces = np.zeros(136)
for t in (0, 1):
    idx = np.where(TIPO == t)[0]
    for ms in MSR:
        e, _ = rodilla(kdist(X[idx], ms))
        for f in FACT:
            veces[idx] += DBSCAN(eps=e * f, min_samples=ms).fit_predict(X[idx]) == -1
frac_ruido = veces / (len(FACT) * len(MSR))
ROB = frac_ruido >= 0.8
n_rob = int(ROB.sum())
enero_rob = int((info.index[ROB].month == 1).sum())
enero_dias = int((info.index.month == 1).sum())
ancla("db_atipicos", n_rob, "T4", 17, r"configuraciones: (\d+)", 0)
ancla("db_atipicos_enero", enero_rob, "T4", 17, r"'ene': '(\d+)/", 0)
ancla("db_atipicos_enero_dias", enero_dias, "T4", 17, r"'ene': '\d+/(\d+)'", 0)
cif("db_atipicos", n_rob, f"{n_rob} días", f"{F4} c.17", "Días de ruido en al menos el 80 % de 25 configuraciones de DBSCAN por tipo")
cif("db_atipicos_pct", n_rob / 136 * 100, es(n_rob / 136 * 100, 0) + " %", f"{F4} c.17", "Atípicos robustos como porcentaje de los 136 días")
cif("db_atipicos_enero", enero_rob, f"{enero_rob} de {enero_dias}", f"{F4} c.17", "Atípicos robustos que caen en enero (de sus días completos)")

# mayo: «desconocidos» (sin núcleo del tipo a menos de eps), modelo ajustado con enero–abril
Xtr, Xmy = X[tr], X[~tr]
t_tr = ordenar(km_tr.labels_, Xtr)
cen = np.vstack([Xtr[t_tr == c].mean(axis=0) for c in (0, 1)])
t_my = np.linalg.norm(Xmy[:, None, :] - cen[None], axis=2).argmin(axis=1)
desconocido = np.zeros(len(Xmy), bool)
dist_nucleo = np.zeros(len(Xmy))
eps_modelo = {}
for t in (0, 1):
    V = Xtr[t_tr == t]
    e, _ = rodilla(kdist(V, MS))
    eps_modelo[t] = e
    db = DBSCAN(eps=e, min_samples=MS).fit(V)
    nuc = V[db.core_sample_indices_]
    m = t_my == t
    dd = NearestNeighbors(n_neighbors=1).fit(nuc).kneighbors(Xmy[m])[0][:, 0]
    dist_nucleo[np.where(m)[0]] = dd
    desconocido[np.where(m)[0]] = dd > e
n_desc = int(desconocido.sum())
ancla("db_mayo_desconocidos", n_desc, "T4", 21, r"Mayo: (\d+) de \d+ días desconocidos", 0)
cif("db_mayo_desconocidos", n_desc, f"{n_desc} de 26", f"{F4} c.21",
    "Días de mayo sin ningún punto núcleo de su tipo a menos de eps (modelo ajustado con enero–abril)")

# lecturas: un DBSCAN por franja sobre consumo + retardos (con dithering ±5 Wh)
dl = df.sort_values("date").reset_index(drop=True)
dl["lag1"] = dl["Appliances"].shift(1)
rng = np.random.default_rng(RS)
dl["A_d"] = dl["Appliances"] + rng.uniform(-5, 5, len(dl))
dl["lag1_d"] = dl["A_d"].shift(1)
dl["media_1h_d"] = dl["A_d"].shift(1).rolling(6).mean()
dl["std_1h_d"] = dl["A_d"].shift(1).rolling(6).std()
dl["media_1h"] = dl["Appliances"].shift(1).rolling(6).mean()
dl["std_1h"] = dl["Appliances"].shift(1).rolling(6).std()
dl["franja"] = pd.cut(dl["hora"], [-1, 5, 11, 17, 23], labels=["madrugada", "mañana", "tarde", "noche"])
dl = dl.dropna().reset_index(drop=True)
UMBRAL = np.percentile(train_test_split(df["Appliances"], test_size=.2, random_state=RS)[0], 90)
TR = (dl["date"] < "2016-05-01").values
ALTO = (dl["Appliances"] > UMBRAL).values
assert len(dl) == 19729 and TR.sum() == 15876

DIN_D = ["A_d", "lag1_d", "media_1h_d", "std_1h_d"]
MSD = 2 * len(DIN_D)
log = np.log1p(dl[DIN_D])
VD = StandardScaler().fit(log[TR]).transform(log)
FRANJAS = ["madrugada", "mañana", "tarde", "noche"]
RUIDO = np.zeros(len(dl), bool)
fr_tab = {}
for fr in FRANJAS:
    m = TR & (dl["franja"] == fr).values
    mm = ~TR & (dl["franja"] == fr).values
    V = VD[m]
    e, _ = rodilla(kdist(V, MSD))
    db = DBSCAN(eps=e, min_samples=MSD).fit(V)
    r = db.labels_ == -1
    RUIDO[np.where(m)[0]] = r
    a = ALTO[m]
    dist = NearestNeighbors(n_neighbors=1).fit(V[db.core_sample_indices_]).kneighbors(VD[mm])[0][:, 0]
    RUIDO[np.where(mm)[0]] = dist > e
    fr_tab[fr] = {"ruido": r.mean() * 100, "ruido_bajo": (~a[r]).mean() * 100,
                  "alto_en_ruido": r[a].mean() * 100, "dbscan_ta": r.mean() * 100,
                  "dbscan_mayo": (dist > e).mean() * 100}
tot_tr, tot_my = RUIDO[TR].mean() * 100, RUIDO[~TR].mean() * 100
umb_tr, umb_my = ALTO[TR].mean() * 100, ALTO[~TR].mean() * 100
cae_db = (tot_my / tot_tr - 1) * 100
cae_um = (umb_my / umb_tr - 1) * 100

pat = r"{fr}\s+\d+\s+[\d.]+\s+\d+\s+\[[^\]]*\]\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)"
ancla("db_madrugada_bajo200", fr_tab["madrugada"]["ruido_bajo"], "T4", 34, pat.format(fr="madrugada"), 1, grupo=2)
ancla("db_madrugada_cubre", fr_tab["madrugada"]["alto_en_ruido"], "T4", 34, pat.format(fr="madrugada"), 1, grupo=3)
ancla("db_tarde_marca", fr_tab["tarde"]["alto_en_ruido"], "T4", 34, pat.format(fr="tarde"), 1, grupo=3)
ancla("db_mayo_caida", cae_db, "T4", 39, r"DBSCAN ([+-]\d+) %", 0)
ancla("umbral_mayo_caida", cae_um, "T4", 39, r"umbral fijo ([+-]\d+) %", 0)
ancla("db_total_ta", tot_tr, "T4", 39, r"ene–abr\s+([\d.]+)", 1)
ancla("db_total_mayo", tot_my, "T4", 39, r"\nmayo\s+([\d.]+)", 1)
ancla("umbral_total_ta", umb_tr, "T4", 39, r"ene–abr\s+[\d.]+\s+([\d.]+)", 1)
ancla("umbral_total_mayo", umb_my, "T4", 39, r"\nmayo\s+[\d.]+\s+([\d.]+)", 1)

cif("db_madrugada_bajo200", fr_tab["madrugada"]["ruido_bajo"], es(fr_tab["madrugada"]["ruido_bajo"], 0) + " %", f"{F4} c.34",
    f"De madrugada, % del ruido de DBSCAN que está por debajo del umbral de {es(UMBRAL, 0)} Wh")
cif("db_madrugada_cubre", fr_tab["madrugada"]["alto_en_ruido"], es(fr_tab["madrugada"]["alto_en_ruido"], 0) + " %", f"{F4} c.34",
    "De madrugada, % de las lecturas sobre el umbral que DBSCAN marca como ruido")
cif("db_tarde_marca", fr_tab["tarde"]["alto_en_ruido"], es(fr_tab["tarde"]["alto_en_ruido"], 0) + " %", f"{F4} c.34",
    "En la tarde, % de las lecturas sobre el umbral que DBSCAN marca como ruido (el resto lo trata como rutina)")
cif("db_mayo_caida", cae_db, es(cae_db, 0) + " %", f"{F4} c.39",
    f"Cambio relativo de la fracción de lecturas marcadas por DBSCAN en mayo ({es(tot_tr, 1)} % → {es(tot_my, 1)} %)")
cif("umbral_mayo_caida", cae_um, es(cae_um, 0) + " %", f"{F4} c.39",
    f"Cambio relativo de la fracción de lecturas sobre el umbral fijo en mayo ({es(umb_tr, 1)} % → {es(umb_my, 1)} %)")
cif("db_umbral_wh", float(UMBRAL), es(UMBRAL, 0) + " Wh", "recalculado (convención §4.3)", "Umbral de anomalía: p90 del entrenamiento de la partición aleatoria")

# lecturas desde la salida guardada (barridos caros)
n_conf = int(desde_salida("T4", 14, r"Configuraciones con 2 o más clústers: (\d+) de"))
n_rej = int(desde_salida("T4", 14, r"Configuraciones con 2 o más clústers: \d+ de (\d+)"))
max_cl = int(desde_salida("T4", 14, r"Máximo número de clústers en toda la rejilla: (\d+)"))
cl30 = int(desde_salida("T4", 26, r"Clústers que caben en una ventana de 7 días o menos: (\d+) de"))
cl30_tot = int(desde_salida("T4", 26, r"Clústers que caben en una ventana de 7 días o menos: \d+ de (\d+)"))
capas = int(desde_salida("T4", 30, r"un único valor de consumo: (\d+) de"))
capas_tot = int(desde_salida("T4", 30, r"un único valor de consumo: \d+ de (\d+)"))
cif("db_rejilla_2cl", n_conf, f"{n_conf} de {n_rej}", f"{F4} c.14 (leído de la salida guardada)",
    f"Configuraciones de la rejilla (eps × min_samples) con 2 o más clústers; el máximo es {max_cl}")
cif("db_30cols_semanas", cl30, f"{cl30} de {cl30_tot}", f"{F4} c.26 (leído de la salida guardada)",
    "Con las 30 columnas, clústers que caben en una ventana de 7 días o menos (DBSCAN agrupa semanas)")
cif("db_capas_10wh", capas, f"{capas} de {capas_tot}", f"{F4} c.30 (leído de la salida guardada)",
    "Sin dithering, clústers que contienen un único valor de consumo (Appliances es 100 % múltiplo de 10 Wh)")

# ═════════════ dbscan_mayo.json ═════════════
MAYO_IDX = np.where(~tr)[0]
dias_mayo = []
for j, i in enumerate(MAYO_IDX):
    if desconocido[j]:
        estado = "desconocido"
    elif ETQ_TIPO[i] == -1:
        estado = "atípico"
    else:
        estado = "en grupo"
    dias_mayo.append({"fecha": str(NIVEL.index[i].date()),
                      "tipo_kmeans": "carga alta" if TIPO[i] == 1 else "normal",
                      "dbscan": estado,
                      "kwh_dia": round(float(info["kwh_dia"].iloc[i]), 2),
                      "atipico_robusto": bool(ROB[i]),
                      "frac_ruido_25_config": round(float(frac_ruido[i]), 2),
                      "dist_a_nucleo_Wh": round(float(dist_nucleo[j]), 1),
                      "eps_modelo_Wh": round(float(eps_modelo[int(t_my[j])]), 1)})
assert len(dias_mayo) == 26
n_at_my = sum(x["dbscan"] == "atípico" for x in dias_mayo)
n_en_my = sum(x["dbscan"] == "en grupo" for x in dias_mayo)
cif("db_mayo_atipicos", n_at_my, f"{n_at_my} de 26", "recalculado (ruido de DBSCAN por tipo sobre los 136 días, c.10 de T4)",
    "Días de mayo que son ruido del DBSCAN por tipo (eps 208/452 Wh) sin ser «desconocidos»")
cif("db_mayo_en_grupo", n_en_my, f"{n_en_my} de 26", "recalculado", "Días de mayo dentro de un clúster de su tipo")

# ───────────────────────── verificación y escritura ─────────────────────────
OBLIGATORIAS = """km_silueta km_silueta_k3 km_dunn km_caida_inercia km_n_normal km_n_alta km_kwh_normal km_kwh_alta
km_cramer_finde km_p_mes km_obs_8h km_obs_12h km_alta_tr km_alta_te km_arbol_h13 ward_ari_kmeans ward_complete_ari
ward_coinciden ward_complete_coinciden avg_silueta avg_dunn estab_ari_kmeans estab_ari_ward estab_ari_complete
db_eps_normal db_eps_alta db_ratio_eps db_atipicos db_atipicos_pct db_mayo_desconocidos db_madrugada_bajo200
db_tarde_marca db_mayo_caida umbral_mayo_caida""".split()
faltan = [k for k in OBLIGATORIAS if k not in CIFRAS]
if faltan:
    FALLOS.append(f"faltan claves obligatorias: {faltan}")

print(f"ANCLAS: {sum(a[3] for a in ANCLAS)} de {len(ANCLAS)} coinciden con las salidas guardadas")
for a in ANCLAS:
    print(f"  {'OK ' if a[3] else 'FALLA'} {a[0]:24s} recalculado={a[1]} guardado={a[2]}  ({a[4]})")
if FALLOS:
    print("\nERRORES:")
    for f in FALLOS:
        print("  -", f)
    sys.exit(1)

DATOS.mkdir(parents=True, exist_ok=True)
meta = {"generado": datetime.now().isoformat(timespec="seconds"),
        "script": "generadores/exportar_c2.py",
        "convencion": "136 días completos × 24 medias horarias (Wh), sin estandarizar; K-Means n_init=10, random_state=42",
        "cuadernos": {k: str(v.relative_to(RAIZ)).replace("\\", "/") for k, v in NB.items()},
        "anclas": [{"clave": a[0], "recalculado": a[1], "guardado": a[2], "fuente": a[4]} for a in ANCLAS],
        "n_cifras": len(CIFRAS)}
(DATOS / "cifras_c2.json").write_text(json.dumps({"meta": meta, "cifras": CIFRAS}, ensure_ascii=False, indent=1), encoding="utf-8")
(DATOS / "dbscan_mayo.json").write_text(json.dumps(dias_mayo, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\nEscritas {len(CIFRAS)} cifras y {len(dias_mayo)} días de mayo en {DATOS}")
for k, v in CIFRAS.items():
    print(f"{k:24s} {v['texto']}")
