# Plan de los talleres del 2.º corte — Shiro Twin

*Plan acordado con el grupo · 23 de septiembre de 2026. Decisiones cerradas en la sección 6.*

---

## 0. Qué desbloquean estos dos talleres para Shiro

El cronograma de `05_Propuesta_Proyecto_Shiro_Twin.docx` fija cuatro hitos para el 2.º corte:
clustering de patrones de uso (al menos dos técnicas), formalización escrita del MDP, entorno de
simulación y un primer agente de Q-learning tabular. Los dos talleres del profesor son el
instrumento para dos de ellos.

| Taller | Pieza de Shiro que decide | Estado tras el parcial |
|---|---|---|
| **C2-T1 · Boosting** | Función de transición del simulador, y detector de anomalías | Simulador: regresión lineal + retardos (R² 0,557 en partición temporal). Detector: Random Forest + retardos (86,9 % de eventos detectados con umbral 0,40) |
| **C2-T2 · K-Means** | Variable «tipo de día» del espacio de estados del MDP | No existe todavía. La propuesta ya decía que los perfiles de rutina «alimentan al agente como variables de estado» |

**Pregunta que ordena cada taller**

- **T1:** ¿algún método de boosting supera a los modelos vigentes *bajo partición temporal con
  retardos*? Y si no, ¿por qué no?
- **T2:** ¿cuántos tipos de día distingue esta vivienda, y son rutinas o son estaciones?

---

## 1. C2 Taller 2 — K-Means y número de clústers

> **✅ TERMINADO (23-sep).** `Taller_2_KMeans/`: notebook (37 celdas), documento RESUELTO (9 pp.),
> presentación (13 diapositivas), figuras K1–K9. **k = 2** con las tres métricas de acuerdo
> (silueta 0,392 · Dunn 0,260): *día normal* (108) y *día de carga alta* (28, bloque diurno 8–18 h).
> El calendario no los explica (V de Cramér = 0,000); Ward coincide (ARI 0,736). Hallazgo propio:
> el tipo de día solo es observable desde media mañana → entra al MDP como estimación que se
> actualiza. La hipótesis de §1.3 (nivel → estación, forma → rutina) **no se confirmó**: ver el
> documento. El resto de esta sección es el plan original, conservado como referencia.

Va primero: tiene material de clase (`KMEANS NOSUP 26-2.pdf`) y fecha de presentación.

### 1.1 La decisión que manda sobre todo lo demás: ¿qué es un punto? ✅ Días

| | **A · Días** (recomendado) | **B · Lecturas de 10 minutos** |
|---|---|---|
| Qué se agrupa | 136 días completos, cada uno como su curva de carga de 24 h | 19.735 lecturas × 29 variables |
| Qué produce | Tipos de día (rutinas) → variable de estado del MDP | Regímenes de hora y temperatura: lo que el árbol ya encontró en el Taller 2 (`hora ≤ 7,5`) |
| Índice de Dunn con el código del profesor | Matriz 136 × 136, instantánea | Matriz de **3,1 GB**: obliga a submuestrear |
| t-SNE | Instantáneo | Minutos, e ilegible sin submuestra |
| Riesgo | Muestra pequeña (110 días de entrenamiento) | Dunn ≈ 0 para todo k: la definición mín/máx colapsa con picos de 1.080 Wh. El propio ejemplo del profesor da 0,0025 |

**Recomendación:** A como análisis principal. B, si se quiere, solo como contraste corto sobre una
submuestra estratificada de ~3.000 lecturas (70 MB de matriz).

Datos verificados: 138 días de calendario, de los cuales **136 están completos** (144 lecturas);
el 11-ene tiene 42 y el 27-may tiene 109, y se descartan. Entrenamiento hasta el 30-abr:
**110 días** (31 de fin de semana). Mayo: **26 días** (7 de fin de semana).

### 1.2 Una desviación deliberada de la diapositiva 57: no estandarizar por columna

El material recomienda `StandardScaler` antes de K-Means. Esa receta es para variables en unidades
distintas. Aquí las 24 columnas están todas en Wh, y su varianza va de **50** (4 a. m.) a **12.477**
(11 a. m.): 250 veces. Estandarizar por columna daría al ruido de las 4 de la mañana el mismo peso
que al pico de las 11 — lo amplificaría unas 16 veces en desviación típica.

La normalización correcta aquí es **por fila**, y se declara en el documento por qué nos apartamos
de la receta. Es exactamente el tipo de decisión que el profesor valora ver justificada.

### 1.3 El riesgo que hay que anticipar: que los clústers sean meses

El parcial midió una deriva fuerte: el percentil 90 cae de 250 Wh en enero a 150 Wh en mayo. Si se
agrupan curvas en Wh absolutos, K-Means puede separar invierno de primavera por **nivel** y no
rutinas por **forma**. Por eso se agrupan dos versiones del mismo día:

- **Nivel:** consumo horario en Wh.
- **Forma:** la curva dividida por el total del día — aísla la rutina del nivel.

**Prueba de fuego:** si los clústers de *forma* se alinean con laboral / fin de semana y los de
*nivel* con el mes, el hallazgo está hecho — y el MDP debe usar la forma, porque la estación ya la
aportan las variables de temperatura.

### 1.4 Pasos, en el orden del enunciado

1. **Preparación.** Matriz día × hora (medias horarias de `Appliances`) sobre los 136 días
   completos. Versiones *nivel* y *forma*.
2. **Punto 1 — k entre 2 y 10.** K-Means con `n_init=10`, `random_state=42`. Método del codo
   (inercia), silueta y Dunn con la función del profesor, sin modificarla. Un gráfico con las tres
   curvas lado a lado.
   - **Criterio adicional propio de Shiro para elegir k:** cada tipo de día multiplica el tamaño de
     la tabla Q. Con 24 horas × k tipos × bandas de temperatura × …, elegir 3 o elegir 8 es la
     diferencia entre un agente que converge y uno que no. La k óptima no es solo la de mejor
     métrica: es la que el espacio de estados puede sostener.
3. **Punto 2 — PCA y t-SNE.** PCA 2D, reportando la varianza explicada por PC1 + PC2. t-SNE 2D con
   perplexity 5, 15 y 30, semilla 42. Comparar cuál separa mejor y advertir que en t-SNE las
   distancias no son interpretables.
4. **Punto 3 — Caracterización.** Se agrupa *solo* con la curva de consumo y se caracteriza *después*
   con variables que no entraron al modelo — así no hay circularidad: % de días de fin de semana,
   mes predominante, T_out media, `lights` del día, hora pico, consumo total. Tabla de medias por
   clúster y, sobre todo, **las curvas de carga de los centroides**: la figura más legible del
   taller («así es un día tipo 1, así un día tipo 2»).
5. **Control temporal** (convención §4.2: siempre dos particiones). Ajustar con los 110 días hasta
   el 30-abr y asignar los 26 de mayo. ¿Caen cerca de centroides conocidos o lejos de todos? Si caen
   lejos, el tipo de día también envejece — el mismo hallazgo que el umbral de anomalía del parcial,
   ahora en no supervisado.
6. **Punto 4 — Presentación:** dataset, k elegida y por qué, visualizaciones, análisis y
   conclusiones.

### 1.5 Extensión por Shiro ✅ Se incluye el jerárquico

El criterio de cierre del proyecto exige **al menos dos técnicas de clustering comparadas**, y hoy
está sin cumplir. Con 136 puntos, el **jerárquico (Ward)** cuesta casi nada y da un dendrograma
legible; se compara con K-Means mediante el índice de Rand ajustado. **DBSCAN** queda como opcional
para marcar días atípicos (festivos, casa vacía): justo los días con los que el simulador no debería
entrenar.

### 1.6 Entregables

`Taller2_KMeans.ipynb` (ejecutado de principio a fin), `Taller2_KMeans_RESUELTO.docx`, presentación.

---

## 2. C2 Taller 1 — Boosting (exploratorio)

> **✅ TERMINADO (23-sep).** `Taller_1_Boosting/`: notebook (28 celdas), documento RESUELTO (6 pp.),
> presentación (11 diapositivas), figuras B1–B5. **Ningún boosting reemplaza a Shiro:** el simulador
> sigue siendo la lineal con retardos (LightGBM la iguala, 0,554 vs 0,557, sin superarla) y el
> detector sigue siendo RF (con el mismo tiempo en alerta avisa menos y con menos falsos). H1 a
> medias, **H2 refutada** (las hojas lineales empeoran), H3 confirmada en regresión. Hallazgo nuevo:
> la **temperatura interior** es la causa del colapso temporal de los árboles (72 % de mayo fuera de
> rango). Corrección metodológica: los detectores se comparan con igual **tiempo en alerta**, no con
> igual número de avisos/día. El resto de esta sección es el plan original.

### 2.1 Las tres hipótesis que el taller pone a prueba

1. **Los cuatro boostings de árboles no van a extrapolar.** GBM, XGBoost, LightGBM y CatBoost
   predicen sumando valores de hoja aprendidos en invierno — el mismo límite que tumbó a Random
   Forest (sesgo de +64 Wh sobre todo mayo). Expectativa: ganan la partición aleatoria y repiten el
   colapso en la temporal.
2. **La excepción que justifica el taller: LightGBM con `linear_tree=True`.** Ajusta un modelo
   lineal dentro de cada hoja. Si extrapola, combina la no linealidad de los árboles con la
   extrapolación de la lineal: el mejor candidato posible a función de transición del simulador.
   Es el experimento con mayor retorno para Shiro.
3. **AdaBoost será inestable.** Repondera los casos difíciles, y los picos de 800 Wh sin señal (el
   Caso A del parcial) recibirán un peso enorme. Un resultado previsible y explicable, que encaja
   con el «de forma exploratoria» del enunciado.

### 2.2 Protocolo — convenciones §4 intactas

- Las mismas 29 variables, las dos particiones, umbral de 200 Wh, semilla 42, hiperparámetros por
  validación cruzada sobre entrenamiento.
- Partición temporal **con retardos** (el escenario decisivo del parcial); la aleatoria, sin ellos,
  porque ahí filtran.
- Dos tareas: **regresión** (candidato a simulador) y **clasificación** (candidato a detector).
- El detector se evalúa también **por episodio**, no solo por lectura: el parcial mostró que el F1
  por lectura elige el modelo equivocado para el producto.
- Desbalance con la herramienta nativa de cada librería — `scale_pos_weight` (XGBoost),
  `is_unbalance` (LightGBM), `auto_class_weights` (CatBoost) —, continuación directa del
  `class_weight='balanced'` del SVM.
- CatBoost con `hora` y `dia_semana` como categóricas nativas: prueba directa del pendiente
  «codificar la hora», sin tocar las variables de los demás modelos.
- Tiempo de entrenamiento como métrica (Random Forest tardaba 27,5 s).
- Importancias solo por bloque (advertencia §8: T1–T9 están correlacionados).

Librerías verificadas sobre el entorno del proyecto: xgboost 3.2, lightgbm 4.7 y catboost 1.2
instalan sin conflictos en Python 3.11.

### 2.3 El tablero que cierra el taller

Cinco algoritmos × {R² aleatoria · R² temporal con retardos · F1 temporal · % de eventos
detectados · tiempo}, con los dos modelos vigentes (lineal + retardos, RF + retardos) como filas de
referencia. La conclusión se formula como decisión: **¿cambia el simulador de Shiro? ¿cambia el
detector?**

### 2.4 Entregables

`Taller1_Boosting.ipynb`, `Taller1_Boosting_RESUELTO.docx`, presentación.

---

## 3. Qué se reutiliza del parcial

- El pipeline de carga, las dos particiones, el umbral y la construcción de retardos — copiados como
  celda inicial de cada cuaderno, igual que el Taller 3 recalculó el Taller 2, para que cada
  cuaderno corra solo.
- La función de episodios y el barrido por umbral (evaluación del detector en T1).
- La paleta de colores y el formato de los documentos RESUELTO (Calibri, cabeceras `1F3864`,
  recuadros `E8F3E8` / `FDF2E3`).

---

## 4. Orden y calendario ✅ Se hacen los dos

La última diapositiva del material dice **«C2 TALLER2 · FECHA: Martes 23 — cada grupo presenta
resultados y hallazgos»**. En el semestre 26-2 no existe un martes 23: el 23 de septiembre de 2026
es miércoles, y los demás días 23 del semestre caen en domingo, viernes y lunes. En 2025 el 23 de
septiembre sí era martes, así que la diapositiva viene probablemente del 25-2 sin actualizar.
**Hay que confirmar la fecha real con el profesor.**

Orden propuesto: **K-Means primero** (tiene material y fecha), **Boosting después** (todavía no hay
material de clase en la carpeta).

---

## 5. Estructura de carpetas

```
2do_Corte_Oct/
├─ Plan_Talleres_Corte2.md          ← este documento
├─ Taller_1_Boosting/               (material de clase cuando llegue)
└─ Taller_2_KMeans/
   └─ KMEANS NOSUP 26-2.pdf         (copia del material; el original sigue en la raíz)
```

---

## 6. Decisiones tomadas (23-sep-2026)

1. **Fechas:** no se planea sobre ellas. El profesor recicla el material de semestres anteriores y
   las fechas de las diapositivas son falsas → se hacen los dos talleres completos.
2. **Unidad de clustering en T2:** **días** (136 curvas de carga de 24 h).
3. **Segunda técnica de clustering:** **sí, jerárquico (Ward)** dentro del T2. DBSCAN queda fuera.
4. **`CLAUDE.md`:** actualizado con los hallazgos del parcial (§4.4, §6, §7 hallazgos 11–17, §9, §10).
