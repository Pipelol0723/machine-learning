# CLAUDE.md — Proyecto "machine learning" (Shiro Twin)

Memoria consolidada del proyecto. Léela completa antes de trabajar en cualquier taller, parcial o
entrega de esta materia.

---

## 0. Principio rector: **Shiro primero**

Todo el trabajo de esta materia gira **principalmente en torno a Shiro y su implementación futura**,
no en torno a cumplir el temario o los enunciados al pie de la letra.

Está permitido desviarse del temario, de los ejemplos del profesor o de los requisitos formales de
un taller **siempre que el motivo sea avanzar o servir a Shiro** (arquitectura, roadmap,
implementación real — ver `03_Plan_Unificado_Shiro_Twin_a_Home.docx`, fases Shiro Twin → Guardian →
Home). Ante tensión entre "seguir la letra del enunciado" y "lo que más le sirve a Shiro", **se
prioriza Shiro**.

Esto ya está validado, no es solo preferencia: el profesor aceptó la propuesta (sector Energía y
Medio Ambiente / IoT reorientado hacia el módulo `iot-bridge` de Shiro). Los ejemplos del profesor
(frutas/precios, mascotas/adopción) se adaptan siempre al consumo energético del hogar.

### El principio aplica también al ORDEN DEL RELATO, no solo al tema

Un texto organizado por técnica de ML —"qué hice con el árbol", "qué hice con KNN", con la
consecuencia para Shiro como párrafo de cierre— **no cumple el principio**, aunque el contenido sea
correcto. Poner a Shiro al final lo convierte en corolario; el principio exige que sea la premisa.

**Cómo aplicarlo:** la pregunta que abre y estructura el texto debe ser una necesidad de Shiro
("el gemelo digital necesita una función de transición", "el MDP necesita definir su espacio de
estados"); el algoritmo entra como el instrumento que la resuelve. Cada resultado numérico llega
acompañado de qué componente de Shiro cambia por su causa.

**Prueba rápida:** si al quitar todas las menciones a Shiro el texto sigue leyéndose completo y
coherente, entonces Shiro era decoración y hay que reescribirlo.

**Plantilla de apertura reutilizable** (usar del 2.º corte en adelante, por defecto y sin que haga
falta pedirlo):

1. Qué componente de Shiro se construye o desbloquea con este trabajo.
2. Qué decisión de arquitectura depende del resultado (espacio de estados del MDP, función de
   transición, recompensa, capa Guardian, `iot-bridge`).
3. Recién entonces: dataset, algoritmo, hiperparámetros, métricas.
4. Cierre: qué cambia en el diseño de Shiro por causa de estos números.

*Nota histórica:* los entregables del Taller 2 y el Taller 3 **no** se reescribieron con este
encuadre (ya entregados, cumplen la plantilla del profesor y conectan con Shiro en su sección
final). El encuadre aplica de aquí en adelante.

---

## 1. Contexto del curso

- **Universidad Sergio Arboleda**, Aprendizaje de Máquina, semestre 26-2 (03.08.2026 – 28.11.2026).
- **Docente:** Hernán Darío Cruz Bueno. Comunicación por grupo de WhatsApp del curso.
- **Grupo Shiro:** Jose Leonardo Diazgranados, Sofía Londoño, Andrés Felipe Céspedes Rondón,
  Alex Duran.
- **Sector asignado:** Energía y Medio Ambiente / IoT.
- Tres cortes: septiembre, octubre, noviembre.
- El curso sigue 7 fases de un proyecto de ML y 5 bloques temáticos (fundamentos → supervisado
  básico → supervisado avanzado → no supervisado → refuerzo).
- **El profesor recicla material de semestres anteriores.** Las fechas que aparecen en sus
  diapositivas no son fiables (ej.: `KMEANS NOSUP 26-2.pdf` dice «Martes 23», que no existe en el
  26-2). No planear sobre ellas: confirmar por el grupo de WhatsApp. Por defecto, hacer todo.

---

## 2. Estructura de carpetas

```
machine learning/
├─ CLAUDE.md                                  ← este archivo
├─ 00_Guia_del_Curso.docx
├─ 01_Glosario_Conceptos_ML.docx
├─ 02_Propuesta_Shiro_IoT.docx
├─ 03_Plan_Unificado_Shiro_Twin_a_Home.docx   ← fases Twin → Guardian → Home
├─ 04_Taller1_Seleccion_Dataset_Shiro_Twin.docx
├─ 05_Propuesta_Proyecto_Shiro_Twin.docx      ← MDP, recompensa, métricas, criterios de cierre
├─ data set/energydata_complete.csv
├─ 1er_Corte_Sept/
│  ├─ Taller_Seleccion_Dataset/               (Taller 1 + material de clase)
│  ├─ Taller_2_Arboles_KNN/                   (+ figuras/, deck, material de clase)
│  ├─ Taller_3_RF_SVM/                        (+ deck, material de clase)
│  └─ Parcial_Corte1/                         (docx, notebook, mockup HTML, figuras/, diapositivas)
├─ 2do_Corte_Oct/
│  ├─ Plan_Talleres_Corte2.md                 ← plan de T1 y T2 (terminados)
│  ├─ Plan_Talleres_3_4_Corte2.md             ← plan de T3 (jerárquico) y T4 (DBSCAN)
│  ├─ Taller_1_Boosting/                      (AdaBoost, GBM, XGBoost, LightGBM, CatBoost)
│  ├─ Taller_2_KMeans/                        (+ KMEANS NOSUP 26-2.pdf)
│  ├─ Taller_3_Jerarquico/                    (ward / complete / average vs K-Means)
│  ├─ Taller_4_DBSCAN/                        (días atípicos + anomalía contextual por franja)
│  └─ Presentacion_Talleres_C2/               (deck único de los 4 talleres, 65 diap. + guion de video)
└─ 3er_Corte_Nov/
```

Convención: cada taller vive en su propia carpeta bajo el corte que le corresponde, junto con el
material de clase del profesor que le aplica.

---

## 3. Dataset

**Appliances Energy Prediction (UCI #374)** — `data set/energydata_complete.csv`.
Elegido en el Taller 1 con 24/25 en la rúbrica, sobre Individual Household Electric Power
Consumption (21/25) y Smart Home + Weather (19/25).

- 19.735 filas, 29 columnas, **0 valores faltantes**.
- Del 2016-01-11 al 2016-05-27 → **137 días** de extensión, lecturas cada 10 minutos. Son 138
  días de calendario, de los cuales **136 están completos** (144 lecturas): el 11-ene tiene 42 y el
  27-may tiene 109. Para análisis por día, usar los 136 (110 hasta el 30-abr, 26 de mayo).
- Objetivo: `Appliances` (Wh). Media 97,69 · mediana 60 · desviación 102,5 · rango 10–1080.
  Cola larga a la derecha: el 90 % de las lecturas está por debajo de 196 Wh.

**Por qué este y no otro:** es el único de los tres candidatos que combina **temperatura y humedad
interior por habitación** con clima exterior. La recompensa del agente es ahorro menos penalización
de confort, y sin temperatura interior esa segunda mitad no se puede calcular.

**Debilidad declarada:** una sola vivienda de bajo consumo en Bélgica, 4,5 meses de invierno y
primavera, sin verano, consumo agregado sin desglose por aparato. Mitigación prevista: usar UCI
Household (#235, 47 meses) como fuente secundaria.

Fuente secundaria pendiente: **Individual Household Electric Power Consumption (UCI #235)** —
2.075.259 filas, 47 meses, sub-medición por grupo de aparatos, ~1,25 % de nulos codificados como
`?`.

---

## 4. Convenciones metodológicas — MANTENER en todos los cortes

Estas decisiones se fijaron en el Taller 2 y el Taller 3 las reutilizó sin cambios, para que los
modelos sean comparables punto a punto. **No cambiarlas sin una razón explícita.**

### 4.1 Las 29 variables predictoras
- 4 temporales derivadas de la marca de tiempo: `hora`, `dia_semana`, `es_fin_semana`, `mes`.
- 1 de iluminación: `lights`.
- 18 sensores interiores: `T1`–`T9`, `RH_1`–`RH_9`.
- 6 de clima exterior: `T_out`, `RH_out`, `Press_mm_hg`, `Windspeed`, `Visibility`, `Tdewpoint`.

**Se excluyen `rv1` y `rv2`**: son variables aleatorias que los autores del dataset inyectaron como
control de ruido. En KNN/SVM son especialmente dañinas porque distorsionan la distancia.

`franja` (madrugada/mañana/tarde/noche) **no entra al modelo** — solo se usa para segmentar errores.

### 4.2 Las dos particiones — la decisión metodológica clave
Se reportan **siempre dos**, nunca una:

- **Aleatoria 80/20, `random_state=42`** (15.788 / 3.947 filas) → **principal**. Es la del material
  del curso y la del paper de Candanedo et al. (2017). Responde: *dado el estado observado del
  hogar, ¿cuánto consume?*
- **Temporal 80/20** (entrena hasta 2016-04-30, prueba el último mes) → **control de robustez**.
  Responde: *¿generaliza a un mes que nunca vio?*

**Por qué las dos.** Con partición temporal SOLA todo colapsa (el mejor árbol sería de profundidad 2
con R² = 0,105) y el trabajo parece fallido. Con las dos, el contraste se vuelve el hallazgo más
fuerte: confirma con números el sesgo de representatividad que el Taller 1 declaró en palabras.

**Regla:** nunca presentar un número de partición aleatoria sin su contraparte temporal al lado.

### 4.3 Otras convenciones
- **Umbral de anomalía:** percentil 90 del consumo **de entrenamiento** ≈ 200 Wh. Calcularlo sobre
  el dataset completo filtraría información del test.
- **Escalado:** `StandardScaler` ajustado **solo sobre entrenamiento**, para KNN y SVM.
- **Hiperparámetros:** se eligen por **validación cruzada sobre el entrenamiento**, no mirando el
  test. Elegir K o C sobre el conjunto de prueba infla el resultado reportado.
- **Métricas:** RMSE por encima de MAE en regresión (penaliza los picos, que son lo que importa);
  **Recall** y F1 por encima de accuracy en clasificación (clases desbalanceadas, 9,6 % de
  anomalías — un modelo que dice "todo normal" ya saca 0,904 de accuracy y 0,000 de F1).
- **Semilla:** `random_state=42` en todo.

### 4.4 Convenciones añadidas en el parcial (2026-09-09)
- **Variables de retardo** — `lag1`, `lag2`, `lag3`, `lag6`, `media_1h`, `max_1h`, `std_1h`
  (consumo de 10, 20, 30 y 60 min antes, y estadísticos de la última hora, siempre con
  `shift(1)` para no mirar el presente). **Solo se usan en la partición temporal**: en la aleatoria
  filtran, porque el vecino de 10 minutos está en entrenamiento.
- **El detector se evalúa por episodio, no solo por lectura.** Un episodio agrupa las lecturas
  positivas separadas por menos de 30 min (`gap=3`). Se reportan alertas/día, % de eventos reales
  detectados y % de alertas falsas. El F1 por lectura elige el modelo equivocado para el producto.
- **⚠ Corrección del C2-T1 (2026-09-23): los detectores se comparan con el mismo TIEMPO EN ALERTA**
  (fracción de lecturas marcadas: se marca el top-k % de probabilidades de cada modelo), **no con
  el mismo número de avisos/día.** Los avisos/día se pueden ganar con trampa: un umbral muy bajo
  produce pocas alertas larguísimas (GBM a umbral 0,05: 98,8 % de episodios con ~3 avisos/día y
  62 % falsos). Reportar siempre también la **duración media del aviso**. El punto de operación
  del parcial (RF, umbral 0,40) = **21,1 % del tiempo en alerta, avisos de 100 min de media**.
- **Clasificadores con balanceo de clases: parada temprana por average precision, no por
  log-loss.** Con log-loss sobre una validación sin pesos, LightGBM `is_unbalance` se detuvo a los
  5 árboles con F1 = 0,000 (el balanceo sube las probabilidades y eso empeora el log-loss).
- **Validación para parada temprana:** 15 % final del entrenamiento en orden cronológico en la
  partición temporal; 15 % aleatorio en la aleatoria. Nunca el test.
- **Toda decisión de arquitectura de Shiro se toma sobre la partición temporal**, no sobre la
  aleatoria. La aleatoria se sigue reportando (regla §4.2), pero no decide.
- **Importancia ≠ coste de pérdida.** Antes de afirmar qué se pierde sin un bloque de variables,
  reentrenar sin él y medirlo (ver hallazgo 16).

### 4.5 Convenciones de clustering (C2-T2 a C2-T4)
- **Unidad: días** (136 × 24 medias horarias en Wh), **sin estandarizar por columna**. En el
  jerárquico, estandarizar vuelve degenerados a *complete* y *average*.
- **k nunca se elige solo por la métrica:** tamaño mínimo de clúster del **5 %** de los datos. La
  silueta y Dunn premiaron una partición de 1 día contra 135 (C2-T3).
- **Métodos de densidad sobre lecturas:** `Appliances` es 100 % múltiplo de 10 Wh; aplicar
  **dithering de ±5 Wh** (semilla 42) antes de DBSCAN o las capas de valores idénticos crean clústers
  falsos. Nunca usar las 30 columnas: DBSCAN agrupa semanas (autocorrelación + deriva).
- Un solo `eps` no sirve para densidades distintas: separar por **tipo de día** (días) o por
  **franja** (lecturas), nunca por calendario.

---

## 5. Estado de los talleres

### Taller 1 — Selección de dataset (entregado)
Rúbrica de 5 criterios sobre 3 candidatos. Ganó Appliances Energy Prediction con 24/25.
Documento: `04_Taller1_Seleccion_Dataset_Shiro_Twin.docx`.

### Taller 2 — Árboles de Decisión y KNN (entregado 2026-08-16)
Carpeta: `1er_Corte_Sept/Taller_2_Arboles_KNN/`
Entregables: `Parte_A_Arbol_Decision_RESUELTO.docx`, `Parte_B_KNN_RESUELTO.docx`,
`Taller2_Arboles_KNN.ipynb` (verificado: corre completo), `Slide_deck_structure_requirements.pptx`
(19 diapositivas), `figuras/` (8 PNG).

**Árbol** `max_depth=15, min_samples_leaf=10` → R² test **0,325** (train 0,587) · MAE 40,07 Wh ·
RMSE 82,20 Wh · 829 hojas. Temporal: R² −2,891.
- **Raíz: `hora ≤ 7,5`** — el árbol encontró solo la hora a la que despierta el hogar. Separa casa
  dormida (54,9 Wh) de casa activa (119,6 Wh), factor 2,2×.
- Importancia por bloque: sensores interiores 54,3 % · temporales 29,2 % · clima 12,4 % ·
  lights 4,0 %. (`hora` individual: 24,7 %.)
- Sesgo estructural: **sobreestima horas valle, subestima picos** (Q4: −53,8 Wh).

**KNN clasificador** K=3 (por CV) → F1 0,634 · precisión 0,727 · recall 0,562 · accuracy 0,938.
Temporal: F1 0,169.
**KNN regresor** K=5 → MAE 30,90 Wh · RMSE 67,89 Wh · R² 0,539. Temporal: R² −0,602.

### Taller 3 — Random Forest y SVM (fechado 2026-09-03)
Carpeta: `1er_Corte_Sept/Taller_3_RF_SVM/`
Entregables: `Parte_1_Random_Forest_RESUELTO.docx`, `Parte_2_SVM_RESUELTO.docx`,
`Taller3_RandomForest_SVM.ipynb` (59 celdas con salidas), `Slide_deck_sobre_metricas.pptx`
(9 diapositivas).

**Random Forest** `n_estimators=200, max_depth=None, min_samples_leaf=1` (16 combinaciones
probadas) → R² train 0,938 · **R² test 0,567** · MAE 30,73 Wh · RMSE 65,83 Wh · 27,5 s.
Clasificador: accuracy 0,944 · precisión 0,832 · recall 0,522 · F1 0,642 · **AUC 0,951**.
Temporal: **R² −4,459**, F1 0,206.
Importancia por bloque: interiores 60,7 % · clima 18,3 % · temporales 18,1 % · lights 2,9 %.

**SVM** — no escala (2 núcleos, no converge sobre 15.788 filas). Se entrenó sobre **submuestra
estratificada de 4.000 filas** pero se **evaluó sobre el test completo**, así que las métricas son
comparables. Ese submuestreo explica en parte que quede último.
- Barrido 3 kernels × C {0,1 / 1 / 10}: **6 de 9 colapsan a clasificador trivial** (F1 = 0,000).
  `linear` con C=10 no convergió.
- Mejor: **rbf, C=10** → precisión 0,617 · recall 0,285 · F1 0,390 · AUC 0,832.
- **Con `class_weight='balanced'`** → recall **0,662** · precisión 0,367 · **F1 0,472** · AUC 0,855.
  Supera al árbol individual. Es la variante que iría a producción si Recall manda.
- Temporal: recall 0,012 · F1 0,024 — el colapso más severo de los cuatro.

### Parcial del Corte 1 (entregado 2026-09-09)
Ver §9.

---

## 6. Tablero completo — 4 regresores y 4 clasificadores

| Regresión | R² aleatoria | R² temporal | MAE (Wh) | RMSE (Wh) |
|---|---|---|---|---|
| Regresión Lineal | 0,171 | **+0,106** | 52,55 | 91,07 |
| Árbol de Decisión | 0,325 | −2,891 | 40,07 | 82,20 |
| KNN (K=5) | 0,539 | −0,602 | 30,90 | 67,89 |
| Random Forest | **0,567** | **−4,459** | **30,73** | **65,83** |
| **Lineal + retardos** (parcial) | — | **+0,557** | 28,17* | 60,54* |
| RF + retardos (parcial) | — | −0,484 | 76,20* | 110,80* |
| LightGBM (C2-T1) | **0,598** | −0,320 | 31,35 | 63,45 |
| LightGBM + retardos (C2-T1) | — | +0,554 | 30,34* | 60,74* |

\* MAE y RMSE de estas dos filas son de la partición temporal; las demás, de la aleatoria.

**Bajo partición temporal el orden se invierte por completo:** la lineal pasa de último a primero y
Random Forest de primero a último. Con retardos, la lineal iguala en la partición difícil lo que RF
lograba en la fácil. **La función de transición de Shiro es la regresión lineal con retardos.**

| Clasificación | Precisión | Recall | F1 | AUC |
|---|---|---|---|---|
| Árbol | 0,580 | 0,383 | 0,461 | 0,861 |
| KNN | 0,727 | **0,562** | 0,634 | 0,903 |
| **Random Forest** | **0,832** | 0,522 | **0,642** | **0,951** |
| SVM (rbf, C=10) | 0,617 | 0,285 | 0,390 | 0,832 |
| SVM balanceado | 0,367 | **0,662** | 0,472 | 0,855 |

Línea base de regresión (predecir la media): MAE 59,87 Wh · RMSE 100,04 Wh.
Línea base de clasificación (todo "normal"): accuracy 0,904 · F1 0,000.

**Matiz que no hay que olvidar:** KNN tiene mejor Recall que Random Forest (0,562 vs 0,522), y
Recall es la métrica crítica del sector. RF no es ganador absoluto.

**Detector vigente (parcial):** Random Forest + retardos, partición temporal, umbral 0,40 →
F1 por lectura 0,580 (desde 0,167 sin retardos) · **86,9 % de eventos reales detectados ·
3,0 alertas/día · 37,3 % de alertas falsas** (84 episodios reales en 27,4 días = 3,1/día). La
regresión logística con retardos tiene mejor F1 por lectura (0,657) pero detecta 17 puntos menos de
eventos con el mismo presupuesto de avisos — por eso no es la elegida.

---

## 7. Hallazgos que cambian el diseño de Shiro (no solo la nota)

1. **`lights` es el proxy de ocupación que el dataset no trae etiquetado.** El árbol lo eligió solo
   en el nivel 3 de la rama "día activo". El MDP necesita ocupación en el estado; esto la aporta.
2. **El error del regresor no es uniforme en el día** (MAE 8,6 Wh de madrugada contra 53,3 Wh en la
   tarde). Si el simulador declara una sola incertidumbre, el agente explotará las horas donde en
   realidad es mucho menos fiable de lo que cree.
3. **Todos los modelos subestiman los picos.** El árbol, 53,8 Wh en el cuartil alto; Random Forest,
   en sus 20 peores casos, 653 Wh reales contra 243 predichos. La recompensa del MDP es
   `−(energía × tarifa) − λ·desviación de confort`: subestimar picos abarata el primer término y
   produce un **ahorro simulado que no existe**. Es el riesgo "el agente explota errores del
   entorno" de la propuesta, ahora localizado y cuantificado.
4. **La variable que falta es "qué aparato está encendido".** Ese es el techo real, no los
   hiperparámetros. Ningún sensor ambiental puede inferir "horno + secadora simultáneos". La mitad
   de los 20 peores errores ocurre en la mañana (06–12 h), el tramo de rutina más variable.
5. **El clasificador rinde mejor donde el regresor rinde peor** (tarde: peor MAE, mejor F1 = 0,727).
   Detectar que hay un pico es más fácil que predecir su magnitud → justifica con datos la
   arquitectura de dos familias en paralelo que la propuesta ya planteaba.
6. **Regularizar un bosque lo empeora.** La regularización que un árbol individual necesita
   (`max_depth=15, min_samples_leaf=10`) es contraproducente en Random Forest: subir
   `min_samples_leaf` de 1 a 20 hunde el R² de 0,567 a 0,395. El bagging obtiene su regularización
   **del promedio, no de la poda** — cada árbol memoriza ruido distinto y al promediar se cancela.
7. **El modelo más preciso es el menos robusto en el tiempo.** RF cae a R² −4,459, peor que el árbol
   individual (−2,891). Precisión y robustez temporal son ejes distintos; para desplegar el gemelo
   digital importa el segundo.
8. **El gemelo digital debe validarse contra un periodo temporalmente reservado ANTES de que el
   agente entrene sobre él.** Si no, el agente aprenderá a explotar un simulador que solo sabe
   repetir el pasado inmediato.
9. **El umbral de decisión debe ser un parámetro ajustable por el usuario, no un valor fijo.** Shiro
   Twin es "solo propuesta": una anomalía perdida es recuperable (la persona ve la factura), pero
   demasiadas falsas alarmas destruyen la confianza y el sistema se termina ignorando. La respuesta
   correcta no es maximizar Recall a toda costa.
10. **Condición de despliegue:** reentrenamiento periódico (p. ej. mensual) a medida que el gemelo
    digital acumule datos nuevos. No es un detalle técnico.

*Hallazgos del parcial (2026-09-09):*

11. **Los árboles no extrapolan; la lineal sí.** Random Forest + retardos predice una media de
    160 Wh en mayo cuando la real es 96: sesgo de **+64 Wh sostenido todo el mes**, porque solo puede
    promediar valores vistos en invierno. La lineal, dominada por `lag1` (coef. 79,0 estandarizado),
    predice el *cambio* respecto del nivel actual; su sesgo es +0,46 Wh. Cualquier modelo basado en
    árboles (incluido el boosting) hereda este límite.
12. **Los retardos son la ingeniería de variables que más rindió en todo el proyecto.** Ningún
    barrido de hiperparámetros se le acerca: F1 temporal del detector 0,167 → 0,580, y regresor de
    R² −4,58 a +0,557 (con la lineal). El techo estaba en la información, no en el algoritmo.
13. **La definición de anomalía envejece.** El percentil 90 mensual cae de 250 Wh (enero, T_out
    4,1 °C) a 150 Wh (mayo, 13,8 °C). El umbral fijo de 200 Wh queda *por encima* del p90 real desde
    marzo. El umbral debe recalibrarse, y el sistema debe declarar baja confianza mientras tanto.
14. **Error por franja del RF:** madrugada 7,34 · mañana 42,12 · tarde 38,16 · noche 34,74 Wh (los
    8,6/53,3 del hallazgo 2 son del árbol). Sesgo por cuartil de consumo real: +9,8 / +6,2 /
    +21,6 / **−40,6 Wh**. La incertidumbre del simulador debe ser función de la hora.
15. **Explicación del árbol en producción:** la ruta `hora > 7,5 → hora ≤ 20,5 → lights > 5,0` es
    real y es la que muestra la capa de explicación. Nunca atribuir una decisión a un sensor T1–T9.
16. **Importancia ≠ coste de pérdida, ni siquiera por bloque.** Los sensores interiores concentran
    el 60,7 % de la importancia, pero al reentrenar sin ellos (13 variables: temporales + lights +
    T_out + retardos) la detección solo cae de 86,9 % a **77,4 %** y el simulador **no cae**
    (R² +0,560). El modo degradado es una configuración defendible, no un gesto.
17. **Seis variables bastan para el simulador:** `hora, lights, T2, RH_2, T_out, lag1` →
    R² 0,536 · MAE 28,85 Wh (96 % del modelo de 36). Coeficientes: intercepto 49,1819 ·
    hora 0,3772 · lights 0,7726 · T2 −0,1388 · RH_2 −0,8008 · T_out 0,7555 · lag1 0,7343.
    Son los que usa el mockup.

*Hallazgos del 2.º corte (2026-09-23):*

18. **La temperatura interior es un confusor estacional — la causa del colapso temporal de los
    árboles.** El 71,9 % de las lecturas de mayo son más cálidas que la más cálida del entrenamiento
    (media interior 20,2 → 23,4 °C), y en invierno el quintil más cálido era el de más consumo
    (113,9 vs 87,8 Wh): parte de ese calor lo producen los aparatos (secadora → lavandería, horno →
    cocina; coherente con el Caso C y con RH_3 en K-Means). **Sin temperaturas, el sesgo de LightGBM
    en mayo pasa de +47 a +3,8 Wh** (R² −0,320 → +0,110). Quitar `mes` no lo arregla. → El simulador
    no predice consumo desde la temperatura interior con modelos que no extrapolan; la temperatura
    interior entra al MDP como variable de **confort**, no como predictor. Precisa el hallazgo 11.
19. **El boosting no reemplaza nada en Shiro** (C2-T1): simulador = lineal + retardos, detector =
    RF + retardos. LightGBM aprende casi lo mismo que la lineal (86,5 % de su ganancia en retardos,
    74,9 % solo `lag1`) y lo que añade (8,9 % de sensores interiores) es lo que trae el sesgo.
20. **El punto de operación del parcial deja al sistema en alerta el 21,1 % del tiempo, con avisos
    de 100 min de media.** El control de umbral de la interfaz debería mostrar también el tiempo en
    alerta, no solo cuántos avisos. (El mockup del parcial no se modificó.)
21. **Tipos de día (C2-T2):** dos — normal y carga alta — que el calendario no explica y que solo se
    observan desde media mañana (ver §10). Entran al MDP como estimación que se actualiza.

*Hallazgos del jerárquico y DBSCAN (2026-09-28):*

22. **El tipo de día es real pero de frontera difusa.** Tres criterios (K-Means, Ward, complete)
    coinciden en el 94 % de los días; los desacuerdos están todos junto a la frontera. El estado del
    MDP lleva el tipo **con su margen al centroide como confianza**.
23. **K-Means asigna el tipo en producción; el jerárquico solo audita.** El corte superior del árbol
    cambia al quitar un mes (ARI 0,359); K-Means no (1,000). Correr Ward/complete en cada
    reentrenamiento mensual: si su acuerdo con K-Means cae, la definición de tipo está cambiando.
24. **El día de carga alta es 2,2× más disperso que el normal** (`eps` 452 frente a 208 Wh). La
    incertidumbre del simulador debe depender del **tipo de día además de la franja** (hallazgo 14).
    Los días atípicos (16 %, sobre todo de enero) se **marcan, no se borran**, y un día sin vecinos
    densos en la historia («desconocido», 2 de 26 en mayo) pide una política conservadora.
25. **Guardian tendrá dos alarmas:** umbral (magnitud → costo) y DBSCAN por franja sobre consumo +
    retardos (rareza en contexto → desperdicio nocturno, arranques inusuales), solo en subidas. De
    madrugada DBSCAN ve lo que el umbral no ve (86 % de su ruido bajo 200 Wh); en la tarde ignora lo
    que el umbral marca por rutina. **Ninguna de las dos es inmune a la estación** (mayo: −33 % y
    −25 %): ambas se reajustan cada mes.

---

## 8. Dos advertencias técnicas que deben sobrevivir a los cortes

1. **Autocorrelación temporal.** Las lecturas son cada 10 minutos y dos consecutivas son casi
   idénticas, así que la partición aleatoria filtra vecinos entre train y test. Verificado: en KNN,
   **K = 1 da mejor F1 (0,690) que cualquier K mayor** — señal inequívoca. Los números de la
   partición aleatoria están en parte inflados y no deben leerse como promesa de desempeño futuro.
2. **`feature_importances_` con variables correlacionadas.** `T1`–`T9` son habitaciones de la misma
   casa. Su ranking interno no es interpretable ("el cuarto 8 importa más que el 3" no significa
   nada); solo el **peso agregado por bloque** lo es.

---

## 9. Parcial del Corte 1 — ENTREGADO (2026-09-09)

Carpeta: `1er_Corte_Sept/Parcial_Corte1/`. Aunque el PDF dice "PARCIAL CORTE 2", es el del
Corte 1; el póster (punto 5) quedó excluido → 4 puntos de 1.0.

**Entregables:**
- `Parcial_Corte1_Shiro_Twin.docx` — 20 páginas, 15 figuras, encuadre Shiro-primero.
- `Parcial_Corte1.ipynb` — 41 celdas, corre de principio a fin; toda cifra del docx sale de aquí.
- `Mockup_Shiro_Twin.html` — consola de 8 pantallas, **sin dependencias** (solo Google Fonts,
  que degrada sola). Deep links por ancla: `#panel`, `#alerta`, `#accion`, `#umbral`, `#ingreso`,
  `#historico`, `#confianza`, `#degradado`, con parámetros (`#accion?decision=aprobada`).
  El diseño original vino de Claude Design (`.dc.html` + `support.js`, que carga React desde
  unpkg); se portó a HTML autocontenido y se corrigieron cifras inventadas.
- `figuras/` — P1…P4 (análisis) y M1…M8 (capturas del mockup, Edge headless a 2×).
- `Diapositivas Parcial Shiro Twin/` y `App_web_mockup.pptx` — hechas por el grupo.

**Estructura del documento:** 1) comparativo histórico con la inversión bajo partición temporal;
2) tres casos críticos (A: 16-abr 10:40, 800 Wh reales / 192 predichos, lights 0 — error
irreducible; B: 8-feb 11:10, 710 / 141, lights 20 — subajuste de una relación minoritaria;
C: 4-abr 15:20, 100 / 509, T3 26,2 °C — falsa alarma, el pico llegó 20 min después) y la propuesta
de mejora medida (retardos); 3) ética: deriva del umbral, quién paga cada error, explicabilidad,
modo degradado medido; 4) lazo de decisión con umbral por defecto 0,40 y override obligatorio.

Hallazgos que salieron del parcial: 11 a 17 en §7.

---

## 10. 2.º corte — en curso

Plan completo: `2do_Corte_Oct/Plan_Talleres_Corte2.md`. Decisiones tomadas con el grupo
(2026-09-23): hacer los dos talleres completos; en K-Means agrupar **días** (no lecturas); incluir
**clustering jerárquico** como segunda técnica.

- **C2 Taller 1 — Boosting — TERMINADO (2026-09-23).** Carpeta `2do_Corte_Oct/Taller_1_Boosting/`:
  `Taller1_Boosting.ipynb` (28 celdas, corre limpio, ~15 min por el GBM de sklearn),
  `Taller1_Boosting_RESUELTO.docx` (6 pp.), `Taller1_Boosting_presentacion.pptx` (11 diapositivas),
  `figuras/` B1…B5. Librerías: xgboost 3.2, lightgbm 4.7, catboost 1.2 (instaladas en `~/venvs/ml`).
  Pregunta Shiro: ¿algún boosting reemplaza al simulador o al detector? **Respuesta: no.**
  - **Regresión.** Aleatoria: LightGBM **0,598** y XGBoost 0,596 > RF 0,567 (mejor regresor del
    proyecto en esa partición). Temporal + retardos: **LightGBM 0,554 ≈ lineal 0,557**, con más MAE
    (30,34 vs 28,17) y sesgo +9,1 vs +0,5 Wh → el simulador sigue siendo la lineal. Resto de la
    familia entre −0,20 (GBM) y 0,51 (CatBoost). En la aleatoria XGB/LGBM/CatBoost llegan al tope de
    3.000 árboles (la validación aleatoria nunca deja de mejorar: autocorrelación); en la temporal
    la parada temprana corta a 1–180 árboles.
  - **Hipótesis:** H1 (árboles no extrapolan) a medias — todos sobreestiman mayo (+9 a +64 Wh);
    H2 (hojas lineales de LightGBM extrapolan) **refutada** (0,426; sin retardos −2,553);
    H3 (AdaBoost frágil) confirmada en regresión (la validación elige 14, 1 y 14 árboles).
    CatBoost con `hora` categórica no aporta (el pendiente de codificar la hora solo aplica a KNN).
  - **Clasificación.** Por lectura, el boosting ordena mejor en temporal + retardos (AP CatBoost
    0,715, XGB 0,703 vs RF 0,605). Pero **con el mismo tiempo en alerta el detector sigue siendo RF**:
    al 21,1 % todos detectan 84,5–88,1 % de episodios; RF con **3,0 avisos/día y 37,3 % falsos**
    (el mínimo en ambos) vs boosting 3,2–3,8 avisos y 42,5–51,0 % falsos. Con 4 % del tiempo en
    alerta, RF detecta 63,1 % vs ≤ 47,6 %. Ver hallazgos 18–20.
- **C2 Taller 2 — K-Means — TERMINADO (2026-09-23).** Carpeta `2do_Corte_Oct/Taller_2_KMeans/`:
  `Taller2_KMeans.ipynb` (37 celdas, corre limpio), `Taller2_KMeans_RESUELTO.docx` (9 pp.),
  `Taller2_KMeans_presentacion.pptx` (13 diapositivas, estética oscura de la consola), `figuras/`
  K1…K9. Unidad: 136 días × 24 medias horarias (Wh), sin estandarizar por columna.
  **Resultados:**
  - **k = 2 — las tres métricas coinciden** (en el ejemplo de clase se contradecían): codo −28 %
    de inercia de 1 a 2 clústers, silueta **0,392** (0,225 con k=3), Dunn **0,260** (máximo).
    Tipos: **día normal** (108 días, 12,2 kWh, pico 18 h) y **día de carga alta** (28 días,
    20,9 kWh, bloque diurno 8–18 h con jorobas a las 11 y 17 h). Madrugadas idénticas (51/49 Wh).
  - **El calendario no los explica:** V de Cramér con fin de semana = **0,000** (28 % vs 29 %);
    mes p = 0,655. **El clima tampoco:** T_out 7,3 vs 7,4 °C; ninguna variable fuera del consumo
    tiene |d| > 0,5. Suben lights (+39 %) y las humedades interiores, encabezadas por **RH_3
    (lavandería)** y RH_1 (cocina). Árbol de prof. 2: `h13 > 199 Wh` reproduce el clúster (96,3 %).
  - **Ward coincide con K-Means** (ARI 0,736 con k=2) → criterio de cierre «dos técnicas» ✅.
    La versión *forma* no tiene estructura (silueta ≈ 0,14; ARI entre métodos 0,19).
  - Estandarizar por columna da los **mismos grupos** (ARI 1,000) pero baja la silueta a 0,259.
  - **Control temporal:** 0/26 días de mayo fuera del p95 → no hay tipos nuevos; pero los días de
    carga alta caen de **22,7 % a 11,5 %** (misma lección que el umbral del parcial).
  - **Observabilidad (hallazgo propio):** hasta las 8 h asignar con la curva parcial es peor que
    decir siempre «normal» (79,4 %); con el día visto hasta las 12 h reconoce el 89,3 % de los días
    de carga alta. → En el MDP el tipo de día entra como **estimación que se actualiza**, no como
    etiqueta; se revela con la joroba de las 11 h, a tiempo para actuar en la de las 17 h.
  - k = 3 revela una «mañana activa» de vie–dom (48 % fin de semana, V = 0,248, p = 0,015), pero
    se descarta como variable de estado (peor silueta y peor observabilidad). ⚠ **No es la carga
    alta partida en dos:** reúne 23 días que con k = 2 eran normales y 8 de carga alta (verificado el
    2026-10-02). El cuaderno y el documento del C2-T2 dicen lo contrario y están por corregir.
  - Hipótesis del plan (nivel → estación, forma → rutina): la primera refutada, la segunda solo a
    medias (forma vs finde: V = 0,185, p = 0,031).

- **C2 Taller 3 — Jerárquico — TERMINADO (2026-09-28).** Carpeta `2do_Corte_Oct/Taller_3_Jerarquico/`:
  `Taller3_Jerarquico.ipynb` (46 celdas), `Taller3_Jerarquico_RESUELTO.docx` (7 pp.),
  `Taller3_Jerarquico_presentacion.pptx` (13 diapositivas), figuras J1, J2, J4–J7. Misma matriz que
  K-Means (136 días × 24 h en Wh). Pregunta Shiro: ¿el tipo de día es real o artefacto de K-Means?
  - **Ward y complete eligen k = 2 con el mismo tamaño (114 / 22)** pero no la misma partición: coinciden
    en 132 de 136 días (ARI 0,855); cada uno coincide con K-Means en 128 (94 %, ARI 0,736). Los 8
    desacuerdos están todos en el 20 % de días más cercanos a la frontera → el margen al centroide
    es la **confianza** de la estimación del tipo de día.
  - **Trampa de la métrica:** *average* tiene la mejor silueta (0,423) y el mejor Dunn (0,475)
    aislando **un solo día** (24-ene, 608 Wh a las 8 h) y nunca da una partición válida entre k = 2 y
    10. Cofenética más alta (0,880) = partición inútil. → **Convención nueva: tamaño mínimo de
    clúster del 5 % (7 días); k nunca se elige solo por la métrica.**
  - Estandarizar: en K-Means ARI 1,000; en el jerárquico degenera (complete 134 / 2, aísla noches raras
    del 12 y 26-ene).
  - Ward k = 3 = «mañana activa» del C2-T2 (28 días, 46,4 % finde, ARI 0,796 con K-Means k = 3).
  - **Estabilidad (decide):** ajustado con 110 días, K-Means da el mismo reparto (ARI 1,000); Ward
    corta 70 / 40 (ARI 0,359; complete 0,401): el grupo intermedio cambia de lado. → **K-Means asigna
    en producción; el jerárquico es auditoría mensual.** K-Means con `n_init=1` reproduce solo el 40 %.
- **C2 Taller 4 — DBSCAN — TERMINADO (2026-09-28).** Carpeta `2do_Corte_Oct/Taller_4_DBSCAN/`:
  `Taller4_DBSCAN.ipynb` (43 celdas), `Taller4_DBSCAN_RESUELTO.docx` (6 pp.),
  `Taller4_DBSCAN_presentacion.pptx` (11 diapositivas), figuras D1–D7.
  - **Parte A (días):** codo `eps` ≈ 208 Wh (`min_samples` = 5, ≈ 42 Wh/h) → 1 clúster de 82 días y
    54 de ruido, **los 28 de carga alta incluidos**. Separando por tipo (la decisión): carga alta
    tiene `eps` 452 → **2,2× más dispersa**, 24 de 28 forman grupo. Por calendario: 27 de 28 siguen en
    ruido. 147 configuraciones: nunca dos grupos comparables. 22 atípicos robustos (≥ 80 % de 25
    configuraciones), **8 de 20 días de enero** (estación), mediana de 4 horas > 100 Wh sobre su tipo;
    incluyen 24-ene, 16-mar y 15-abr. Mayo: 2 de 26 días «desconocidos».
  - **Parte B (lecturas):** con las 30 columnas DBSCAN agrupa **semanas** (26 de 30 clústers en ≤ 7
    días). `Appliances` es 100 % múltiplo de 10 Wh → capas de densidad falsa (14 clústers, 6 de un solo
    valor) → **dithering ±5 Wh** (convención nueva para métodos de densidad). Consumo + retardos con
    `log1p`, un DBSCAN por franja: de madrugada el 86 % del ruido está bajo 200 Wh y cubre el 100 % de
    lo que supera el umbral; en la tarde solo marca el 6 % de las lecturas > 200 Wh. 35–60 % del ruido
    son bajadas → alertar solo subidas. Mayo: DBSCAN −33 %, umbral −25 % → **ninguna definición es
    inmune a la estación.**

- **Presentación unificada del 2.º corte (2026-10-02).** `2do_Corte_Oct/Presentacion_Talleres_C2/`:
  `Presentacion_Talleres_C2_Shiro.pptx` (65 diapositivas, estética de la consola, notas del orador
  en todas) y `Guion_Video_Talleres_C2.docx` (≈ 17 min; apertura y Boosting: Jose; K-Means: Sofía;
  jerárquico: Andrés; DBSCAN: Alex; cierre compartido). Construida desde los cuadernos verificados,
  **no** desde las `*_presentacion_ampliada.pptx`, que tienen errores señalados el 2026-09-30.

**Pendientes que siguen abiertos:**
- **Formalizar el MDP por escrito** y construir el entorno de simulación con la función de
  transición ya decidida (lineal + retardos) e incertidumbre por **franja × tipo de día**. El estado
  incluye el tipo de día estimado con su confianza (margen) y la bandera «día desconocido».
- **Prototipo de Guardian con dos alarmas** (umbral + DBSCAN por franja, solo subidas) evaluado por
  episodio con igual tiempo en alerta, contra el detector RF vigente.
- **Incorporar UCI Household (#235)** para medir la caída de desempeño al cambiar de vivienda.
- **Codificar `hora`** — probado en el C2-T1 con CatBoost categórico: en árboles **no aporta**.
  Queda solo para modelos de distancia (KNN, seno/coseno).
- **Probar el detector RF sin temperaturas interiores** (hallazgo 18): en regresión quitarlas elimina
  el sesgo estacional; falta ver si el detector también mejora con el mismo tiempo en alerta.
- **Agente de Q-learning** entrenado y evaluado dentro del gemelo, con métricas de ahorro simulado
  frente a una política base.
- *(Hecho en el parcial: variables de retardo.)*

**Criterios de cierre del proyecto** (de `05_Propuesta_Proyecto_Shiro_Twin.docx`): dataset
documentado ✅ · al menos un regresor y un clasificador entrenados ✅ · al menos dos técnicas de
clustering comparadas ✅ (K-Means, jerárquico con tres enlaces y DBSCAN, C2-T2 a C2-T4) · MDP formalizado y agente de
Q-learning entrenado y evaluado ⬜ · informe final y demostración del entorno funcionando ⬜.

---

## 11. Cómo trabajar en este proyecto

- **Idioma:** español. Números con coma decimal y punto de miles (convención es-CO).
- Para tareas de código y análisis, escribir directamente el código y los análisis en vez de
  explicar paso a paso.
- **Verificar antes de entregar:** que el notebook corra de principio a fin, que cada cifra del
  documento coincida con la salida del código, y que no queden celdas de plantilla vacías.
- **Ser honesto con los límites.** Los entregables de este proyecto declaran explícitamente lo que
  no funciona (el colapso temporal, la autocorrelación, el submuestreo de SVM, el techo de las
  variables disponibles). Un evaluador que detecta un problema no mencionado asume que no se
  entendió; uno que lo lee explicado asume lo contrario. Mantener ese estándar.
- Las rutas de los notebooks son relativas: `"../../data set/energydata_complete.csv"` desde la
  carpeta de un taller. Ajustar si el cuaderno cambia de sitio.

### Entorno de ejecución en este equipo
- **No hay Python en el PATH.** Usar `C:\Users\pipel\venvs\ml\Scripts\python.exe` (Python 3.11 con
  scikit-learn 1.9, pandas, numpy, matplotlib, python-docx, pymupdf, nbformat, nbclient e
  ipykernel). El venv `~/venvs/bigdata` es de otra materia y **no** tiene scikit-learn.
- Con scikit-learn 1.9 todas las cifras de los Talleres 2, 3 y del parcial **reproducen al
  decimal**.
- Los notebooks se construyen con un script generador y se ejecutan con `nbclient` para que queden
  guardados con salidas. Los `.docx` se generan con `python-docx` imitando el estilo de los
  entregables anteriores (Calibri, cabeceras `1F3864` con texto blanco, recuadros `E8F3E8` /
  `FDF2E3` / `F2F2F2`).
- Word está disponible por COM (conversión docx → PDF para revisar). Capturas de páginas HTML:
  Edge headless (`msedge.exe --headless=new --screenshot`). `pdftotext` viene con Git.
- ⚠ El notebook del Taller 2 (`Taller2_Arboles_KNN.ipynb`) **no tiene salidas guardadas**.
