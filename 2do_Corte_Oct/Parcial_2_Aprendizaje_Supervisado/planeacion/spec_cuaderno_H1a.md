# Especificación del cuaderno — hito H1a (+ latencia N1c)

> Traducción implementable de `../PLAN_DESARROLLO.md` (aprobado el 21-oct-2026: sí a las 4 decisiones; cifras solo en kWh).
> Donde esta especificación y el plan discrepen, manda el plan; si el plan es ambiguo, manda esta especificación.
> Las figuras de 300 dpi (G1–G6) y el mockup NO son parte de este hito.

## 0. Entregables de este hito
Todo dentro de `2do_Corte_Oct/Parcial_2_Aprendizaje_Supervisado/`:
- `generadores/construir_cuaderno.py` — genera el cuaderno con `nbformat` (celdas markdown + código) y lo ejecuta con `nbclient` (kernel `python3` del venv `C:\Users\pipel\venvs\ml`, `cwd` = carpeta del cuaderno, timeout por celda ≥ 600 s). Se corre con `C:\Users\pipel\venvs\ml\Scripts\python.exe generadores\construir_cuaderno.py`.
- `Parcial2_Guardian.ipynb` — guardado CON salidas. Profundidad 2: el CSV se lee con `"../../data set/energydata_complete.csv"`.
- `cifras.json` — única fuente de cifras (lo escribe el cuaderno).
- `mockup/datos_mockup.json` — datos que el mockup incrustará (lo escribe el cuaderno).
- Tiempo total objetivo de ejecución: ≤ 5 min (registrar el tiempo real en `cifras.json`).

## 1. Encuadre del cuaderno (CLAUDE.md §0 — Shiro primero)
Español es-CO. Cada sección abre con la necesidad de Shiro Guardian que resuelve y cierra con "Qué cambia en Shiro" (1–3 líneas, con la cifra). Celda inicial: la pregunta ("¿cuánto antes puede avisar Guardian de un pico, y con qué modelo?"), la decisión de arquitectura que depende de la respuesta (qué probabilidad entra al estado del MDP y si Guardian notifica) y el mapa de secciones. Sin relleno: el texto explica decisiones, no la API de sklearn. Ninguna cifra tecleada a mano en markdown: las cifras se imprimen desde el código.

## 2. Datos y particiones (idénticos a los cuadernos fuente)
- Carga y variables EXACTAMENTE como `Parcial_Corte1.ipynb` c.3 (TEMPORALES, INTERIOR, CLIMA, FEATURES = 29, TARGET = `Appliances`, `franja`).
- `UMBRAL = np.percentile(y_tr_aleatoria, 90)` con `train_test_split(test_size=.2, random_state=42)` sobre `df[FEATURES]`; `assert UMBRAL == 200`.
- `dfo` ordenado por fecha; `dl` con retardos EXACTAMENTE como c.22 (`lag1, lag2, lag3, lag6` con `shift(k)`; `media_1h, max_1h, std_1h` = `shift(1).rolling(6)`; `dropna`, `reset_index`). `cl = int(len(dl) * .8)` → `assert cl == 15783` y `len(dl) - cl == 3946`.
- **fit** = `dl[:n_fit]` con `n_fit = int(0.85 * cl)` (= 13.415, hasta el 13-abr); **validación** = `dl[n_fit:cl]` (2.368 lecturas); **prueba** = `dl[cl:]` (3.946). Registrar fechas de cada frontera.
- `RS = 42` en todo.

## 3. Definiciones operativas
- **Lectura alta:** `Appliances > 200`. **Pico (episodio):** lecturas altas agrupadas con `gap=3` (función `episodios` de `Taller1_Boosting.ipynb` c.17), calculados sobre la SERIE COMPLETA `dl`. Inicio `s`, fin `e` (índices de `dl`).
- **Picos de un segmento** (validación o prueba): los episodios que tienen alguna lectura en el segmento. `assert` prueba = 84 picos y 27,4 días (como `Parcial_Corte1.ipynb` c.38). Registrar los de validación (indicio: 51).
- **En calma:** lectura fuera de todo tramo `[s, e]`. "Rojo en curso" = dentro de un tramo. Declarar en el cuaderno que fijar `e` mira hasta 3 lecturas adelante y contar cuántas lecturas de prueba quedan afectadas (indicio: 17).
- **Etiqueta de anticipación** `y_ant(t) = 1` si `t` está en calma y `t ∈ [s−3, s−1]` de algún pico (un pico empieza en las próximas 1–3 lecturas). **Tasa base** = media de `y_ant` en la calma del entrenamiento completo (`dl[:cl]`); indicio 7,66 %. Se guarda como `r` (presupuesto de rojo). Registrar también la de prueba (indicio 6,91 %).
- **Purga:** para todo lo que se estima con `y_ant` (G0, G4, G5, explicador, calibración), excluir las 3 últimas lecturas de fit y las 3 últimas de validación (su etiqueta mira al segmento siguiente).
- **Antelación de un pico** con una señal en rojo: `10 × (s − primera lectura en rojo dentro de [s−3, s−1])` minutos (nominal). Un pico con `s−3 < inicio del segmento` solo puede anticiparse con las lecturas de la ventana que caen en el segmento (el primer pico de prueba empezó en el entrenamiento → máximo 83 de 84). Reportar % de picos con antelación ≥ 10, ≥ 20 y ≥ 30 min sobre el total de picos del segmento.
- **Aviso:** lecturas en calma en rojo agrupadas con `gap=3`. **Útil** si alguna de sus lecturas está en `[s−3, s−1]` de algún pico; si no, **falso**. Reportar avisos/día (días del segmento como en c.38: `(última − primera fecha) / 1 día`), % útiles, duración media (lecturas × 10 min).
- **Mismo tiempo en rojo (comparación):** cada señal marca en rojo el top-`r` de su puntaje en la calma del segmento; empates → la lectura más temprana primero (orden estable por puntaje descendente, índice ascendente); `k = round(r × n_calma)`.
- **Desplegado:** cortes de validación aplicados a prueba: `corte_rojo` = cuantil `1−r` del puntaje en la calma de validación; `corte_amarillo` = cuantil `1−2r`. Rojo si `puntaje ≥ corte_rojo`. Reportar el % de rojo realizado en prueba y minutos/día en rojo.
- **Acierto de un color:** % de las lecturas en calma de ese color con `y_ant = 1`.
- **Azar:** % esperado de picos con ≥ 20 min si se marca al azar el `r` de la calma (`1 − (1−r)²`, y verificación por simulación con semilla 42).
- **Bootstrap pareado por día:** 2.000 réplicas (semilla 42); se remuestrean con reemplazo los días calendario del segmento de prueba (día del inicio `s` de cada pico; picos sin antelación posible incluidos), y se recalcula la diferencia en % de picos con ≥ 20 min entre dos señales con su marcado fijo de "mismo tiempo en rojo". IC 95 % por percentiles.

## 4. Señales candidatas (todas se aplican "un paso adelante")
**Vector desplazado en `t`** (lo que Guardian conoce en `t`): las 29 exógenas de la fila `t`; `lag1 = A(t)`, `lag2 = A(t−1)`, `lag3 = A(t−2)`, `lag6 = A(t−5)`; `media_1h`, `max_1h`, `std_1h` sobre `A(t−5..t)` (misma `std` de pandas, ddof=1). Construirlo con `shift(k−1)` y `rolling(6)` sin `shift`. **`assert` de no fuga:** en 200 instantes al azar (semilla 42) el vector construido solo con `dl.loc[:t]` es idéntico al de la tabla.
- **Regla de nivel** (sin etiquetas; listón): puntaje = `A(t)`.
- **G0, modelo mínimo entrenado de 2 variables:** `p_nivel(t)` = ECDF de `A` en la calma de fit evaluada en `A(t)`; `freq[celda]` = media de `y_ant` en la calma de fit por celda `hora × es_fin_semana` (48 celdas); `p_hora(t)` = ECDF de `freq[celda(r)]` sobre la calma de fit evaluada en `freq[celda(t)]`. Puntaje = `p_nivel + p_hora`. Exportable (48 frecuencias + 2 tablas ECDF).
- **G1** `RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)` y **G2** `LogisticRegression(max_iter=2000)` con `StandardScaler` ajustado en fit: entrenados en fit para RECONOCER (`A(t) > 200` con el vector original de 36 variables, todas las filas); puntaje = probabilidad sobre el vector desplazado.
- **G3b** `LinearRegression` de 36 variables entrenada en fit (objetivo `A(t)`, vector original); puntaje = pronóstico sobre el vector desplazado (= consumo esperado en `t+1`).
- **G4** RF (200 árboles, rs 42) y **G5** logística (escalado en fit) entrenados para ANTICIPAR: `y_ant` en la calma de fit (con purga), entradas = vector desplazado.
- **Simplicidad:** nivel 0 = G0; nivel 1 = G3b, G2, G5; nivel 2 = G1, G4.
- **Modelos de referencia (no candidatos):** **G3a** = `LinearRegression` 36 var. entrenada en `dl[:cl]` (anclas y pronóstico); **G3c** = lineal de 6 variables `hora, lights, T2, RH_2, T_out, lag1` en `dl[:cl]` (tarjeta 1); **detector del parcial 1** = RF 200 árboles en `dl[:cl]`, etiqueta `A(t) > 200`, umbral 0,40 (anclas y N1c).

## 5. Anclas (N1a) — `assert` con tolerancia; si falla, el cuaderno se detiene
G3a en prueba: R² 0,557 (±0,001), MAE 28,17 Wh (±0,01), RMSE 60,54 Wh (±0,01), sesgo 0,457 (±0,01). G3c: MAE 28,85 (±0,01), R² 0,5358 (±0,001), coeficientes e intercepto de CLAUDE.md hallazgo 17 (±0,0001). Detector del parcial 1 a 0,40 con `evaluar_alertas` de c.17: 84 picos, 27,4 días (±0,05), 86,9 % (±0,05), 3,03 avisos/día (±0,005), 37,3 % falsos (±0,05), F1 por lectura 0,47 (±0,005), 21,1 % del tiempo en alerta (±0,05), 100,5 min (±0,05).

## 6. Cálculos
- **N1b Persistencia:** en prueba (vector original), G3a y G3c frente a `ŷ = lag1`: MAE, RMSE y sesgo — total, por franja y en lecturas > 200 Wh (indicios: persistencia 26,64 / 66,44 total; 148,2 / −58,6 en las 324 lecturas > 200 Wh).
- **N1c Latencia del parcial 1:** con el detector a 0,40 en prueba: para cada pico, posición de la primera lectura en alerta dentro de `[s−3, e]`: antes de `s` (con minutos), en `s`, después de `s`, nunca. Más: % de la energía del pico (Wh dentro de `[s, e]`) que aún quedaba por delante en la primera alerta (mediana y media).
- **N1d Anticipación:** para cada señal (regla, G0–G5), en validación y en prueba con "mismo tiempo en rojo", y en prueba desplegado: % de picos con ≥ 10/20/30 min, avisos/día, duración media, % útiles, acierto del rojo, % de rojo realizado. Indicios en prueba a mismo tiempo en rojo: regla ≥ 20 min 20–24 %; G0 27–32 %; útiles regla 31–33 %, G0 37–41 %.
- **Piso (en validación):** % ≥ 20 min mayor que el de la regla de nivel, ≥ 25 % de picos y ≥ 33 % de avisos útiles.
- **Selección (solo validación):** entre los que pasan el piso, el más simple de los que quedan a menos de 10 puntos del mejor (≥ 20 min); dentro de un nivel, el de mayor %. Si ninguno pasa el piso: misma regla sin piso → caso C1. El gemelo (G3a/G3c) es siempre el segundo modelo elegido (pronóstico).
- **Casos (prueba, ≥ 20 min, mismo tiempo en rojo), en orden:** C1 = ninguno pasó el piso; A = elegido ≠ G0 y (elegido − G0) ≥ 10 puntos con IC > 0; C2 = elegido = G0 y (G0 − complejo) ≥ 10 con IC > 0, complejo = el mejor de los demás candidatos en validación; B = cualquier otro (anotar si la prueba favorece a otro candidato, y cuál y por cuánto).
- **Calibración del elegido:** deciles del puntaje en la calma de validación (purgada) → tasa de `y_ant` por decil ("de cada 100 momentos así, X precedieron un pico"); bordes y tasas exportados.
- **N1e Explicador:** `DecisionTreeClassifier(max_depth=3, random_state=42)` que imita el rojo del elegido (`puntaje ≥ corte_rojo`) en la calma de fit (purgada); si el elegido es un bosque, usar puntajes OOB en fit (`oob_score=True` en un RF gemelo con la misma configuración) para no imitar el sobreajuste. Entradas legibles: el vector desplazado más `freq_hora` si el elegido es G0. Fidelidad en prueba = % de coincidencia rojo/no rojo en la calma de prueba y precisión del rojo del árbol. Exportar las reglas en texto es-CO (nombres de variables en lenguaje llano: "consumo actual", "hora", "luces", etc.).
- **N1f Energía y casos:** kWh de prueba = `ΣA/1000` (indicio 380,0); kWh dentro de picos (115,7); kWh de exceso sobre 200 Wh (50,9; determinar si es `Σmax(A−200, 0)` o `ΣA[A>200]` y usar la que corresponda, declarándola). Exceso de los picos anticipados con ≥ 20 min por el elegido desplegado. **Casos críticos por regla:** (1) pico NO anticipado con más energía; (2) aviso falso más largo (empate → el más temprano). Para cada uno: fecha y hora, valores de entrada, puntaje, antelación o duración.
- **Ejemplos por regla para el mockup (prueba; empate → el más temprano):** Tarjeta 1 (5 momentos): calma verde de puntaje mediano; primer rojo del aviso útil de antelación mediana; primer rojo del aviso falso más largo; 20 min antes del pico no anticipado con más energía; inicio del pico de energía mediana. Tarjeta 4 (4 situaciones): avisos útiles de mayor y de mediana antelación, falso más largo, no anticipado con más energía. **Día del antes/después:** entre los días de prueba con ≥ 3 picos, el de mediana en % de picos anticipados (≥ 20 min, desplegado); empate → el más temprano.
- **Deriva de cortes:** % de rojo realizado en prueba de cada señal con sus cortes de validación (indicio 6,7–11,0 %; G0 ≈ 9,3 %).
- **Sensibilidad:** % ≥ 20 min del elegido y de la regla con `r` = 5 % y 10 %.

## 7. Exportación
- **`cifras.json`** = `{"meta": {fecha_ejecucion, segundos, sklearn, pandas, numpy, python}, "nuevas": {...}, "heredadas": {...}}`. Cada clave → `{"valor": número, "texto": "86,9 %" (es-CO: coma decimal, punto de miles, espacio antes de %), "unidad", "particion": "temporal", "fuente": "sección del cuaderno", "descripcion"}`. Claves en snake_case con prefijos por familia (`ancla_`, `n1b_`, `n1c_`, `sel_`, `caso_`, `g0_`, `g4_`, `regla_`, `energia_`, …) e incluir: caso (A/B/C1/C2) y frase del caso; modelo elegido y su nivel; titular `n20` (desplegado, picos de 84 y %), `m20` (regla al mismo rojo realizado), `min_dia` en rojo; `d` (diferencia del caso) con su IC; azar.
- **`heredadas`**: leídas con `nbformat` de las SALIDAS guardadas de `1er_Corte_Sept/Parcial_Corte1/Parcial_Corte1.ipynb` (c.7 tabla aleatoria de regresión y clasificación, c.25, c.29, c.38) y `2do_Corte_Oct/Taller_1_Boosting/Taller1_Boosting.ipynb` (c.8 tablas de regresión, c.22) con regex fijada por celda (rutas relativas desde el cuaderno: `../../1er_Corte_Sept/...`, `../Taller_1_Boosting/...`), contrastadas con `assert` contra la tabla de CLAUDE.md §6 (tolerancia de redondeo). Si discrepan, manda la salida guardada y se anota. Incluir la corrección: F1 a 0,40 = 0,47 (no 0,580).
- **`mockup/datos_mockup.json`**: serie de prueba (fecha ISO, Wh, en calma, rojo en curso, `y_ant`, puntaje del elegido, puntaje de la regla, id de pico); lista de picos (inicio, fin, energía); puntajes del elegido y de la regla en la calma de validación (para recalcular cortes con los deslizadores); `r` por defecto; parámetros del elegido si es exportable (G0: 48 frecuencias + tablas ECDF; logística/lineal: coeficientes, intercepto y media/escala del `StandardScaler`, con el orden de variables); si es un bosque, solo puntajes precalculados; calibración por deciles; reglas del explicador; G3c (coeficientes, intercepto, MAE por franja); los 5 momentos y 4 situaciones con todas sus variables de entrada y su color esperado; el día del antes/después; **valores esperados para la autoverificación del mockup** (métricas de la tarjeta 2 con `r` por defecto desplegado y el color de los 5 momentos).

## 8. Verificación interna del cuaderno (celda final)
- Todas las anclas pasan. `cifras.json` y `datos_mockup.json` se releen y se validan (claves obligatorias presentes, sin NaN, textos es-CO).
- Reejecución determinista: mismas cifras en dos ejecuciones (lo comprueba el generador o el revisor).
- Imprimir un resumen ≤ 15 líneas para el punto de control H2: caso, modelo elegido, titular, regla al mismo rojo, IC, costo (falsos, min/día), latencia del parcial 1, persistencia.
