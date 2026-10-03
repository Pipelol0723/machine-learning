# Plan de los talleres 3 y 4 del 2.º corte — Jerárquico y DBSCAN

*Plan del 28 de septiembre de 2026. Decisiones cerradas en la sección 7.*
*Continuación de `Plan_Talleres_Corte2.md` (Boosting y K-Means, ambos terminados).*

> **✅ LOS DOS TALLERES ESTÁN TERMINADOS (28-sep).**
> - **T3** (`Taller_3_Jerarquico/`): cuaderno de 46 celdas, documento RESUELTO de 7 pp. y presentación
>   de 13 diapositivas.
> - **T4** (`Taller_4_DBSCAN/`): cuaderno de 43 celdas, documento de 6 pp. y presentación de 11.
>
> **Correcciones a este plan, con los números de los cuadernos:**
> 1. Ward y *complete* **no** dan el mismo reparto: coinciden en tamaño (114 / 22) y en 132 de 136
>    días (ARI 0,855).
> 2. Lo que decide la comparación no estaba en el plan: **el árbol es inestable** al quitar un mes
>    (ARI 0,359), y K-Means no (1,000).
> 3. En lecturas, los clústers pequeños eran **capas de la resolución de 10 Wh** del medidor: se
>    corrigieron con dithering de ±5 Wh.
> 4. Los atípicos robustos son el 16 % de los días y se concentran en enero, así que se **marcan,
>    no se borran**.
> 5. DBSCAN **no resuelve** el envejecimiento: en mayo marca un 33 % menos, frente al 25 % menos del
>    umbral.
>
> El resto del documento es el plan original, conservado como referencia. Los resultados están en
> `CLAUDE.md` (§4.5, hallazgos 22–25 y §10).

---

## 0. Qué desbloquean estos dos talleres para Shiro

El C2-T2 le dio al MDP su primera variable de rutina: **el tipo de día** (normal / carga alta).
Estos dos talleres la someten a prueba y buscan lo que queda fuera de ella. Juntos cierran una
cadena de tres pasos: **K-Means encuentra los tipos → el jerárquico los audita → DBSCAN encuentra lo
que no pertenece a ningún tipo.**

| Taller | Pieza de Shiro que decide | Estado hoy |
|---|---|---|
| **C2-T3 · Jerárquico** | Robustez de la variable «tipo de día» del MDP. Qué técnica asigna el tipo en producción | K-Means da k = 2. Ward coincide (ARI 0,736), pero se probó un solo enlace y Ward optimiza lo mismo que K-Means: no es una auditoría independiente |
| **C2-T4 · DBSCAN** | (a) Días atípicos: qué datos no debe aprender el gemelo como rutina. (b) Definición de anomalía de la capa Guardian | La anomalía es un umbral fijo (p90 de entrenamiento) que **envejece**: el p90 mensual cae de 250 a 150 Wh (hallazgo 13) |

**Pregunta que ordena cada taller**

- **T3:** ¿los dos tipos de día son una propiedad de esta casa o un artefacto de K-Means? K-Means
  siempre devuelve k grupos, existan o no. Si tres definiciones distintas de «grupo» (Ward,
  *complete*, *average*) llegan al mismo reparto, la variable de estado es sólida.
- **T4:** ¿qué no pertenece a ningún patrón? Días que el simulador no debería aprender como rutina,
  y lecturas que son raras *para su hora* aunque no superen el umbral.

---

## 1. Lo que ya adelantó la exploración (28-sep)

Corrida rápida sobre los datos del proyecto para planear con números y no con supuestos. **Son
cifras preliminares**: los cuadernos las recalculan y el documento solo cita las de los cuadernos.

### 1.1 Jerárquico sobre los 136 días (curva de 24 h en Wh, sin estandarizar)

| Enlace | Silueta k=2 | k=3 | k=4 | Reparto con k=2 | ARI con K-Means | Correlación cofenética |
|---|---|---|---|---|---|---|
| Ward | 0,400 | 0,200 | 0,141 | 114 / 22 | 0,736 | 0,755 |
| Complete | 0,414 | 0,401 | 0,381 | 114 / 22 | 0,736 | 0,808 |
| Average | **0,423** | 0,371 | 0,373 | **135 / 1** | 0,041 | **0,880** |

- **Ward y *complete* encuentran el mismo reparto** (114/22, mismo cruce con K-Means). Son dos
  criterios de fusión distintos: Ward minimiza varianza, como K-Means, pero *complete* acota el
  diámetro. Que coincidan es la auditoría independiente que el C2-T2 no tenía.
- **La trampa de la silueta:** la silueta más alta del barrido es la partición inservible. *Average*
  aísla un solo día, el **24-ene-2016**, un domingo con un pico de 608 Wh a las 8 h, frente a los otros
  135. Y *average* es el enlace que mejor conserva las distancias (cofenética 0,880). Elegir k solo
  por la silueta daría un «tipo de día» con un único ejemplar.
- **Aquí el escalado sí cambia el resultado.** En K-Means estandarizar daba los mismos grupos
  (ARI 1,000). En el jerárquico, con `StandardScaler` Ward pasa a 105/31 (ARI 0,842 con K-Means),
  mientras que *complete* y *average* aíslan 1–2 días con silueta todavía más alta (0,517–0,538).
- Los 7 días que K-Means llama «carga alta» y Ward «normal» son todos **de frontera**: 16–21 kWh,
  con picos de 317–455 Wh.

### 1.2 DBSCAN

- **Días, `eps` en la rodilla (≈ 208 Wh, min_samples = 5): un solo clúster más 54 días de ruido, y
  los 28 días de carga alta caen todos en el ruido.** Es el caso «todo un gran grupo» que el
  enunciado anticipa. Para DBSCAN, «carga alta» no es un grupo denso: es una periferia dispersa
  alrededor de la rutina normal.
- **Separando por tipo, cada uno tiene su propia densidad.** La rodilla de los días normales está en
  ≈ 208 Wh y la de los de carga alta en ≈ 452 Wh: son **2,2 veces más dispersos**. Con su propio
  `eps`, 24 de los 28 forman grupo y 4 quedan como ruido. Es la limitación clásica de DBSCAN (un solo
  `eps` no sirve para densidades distintas), y aquí tiene una lectura directa para el simulador.
- **Control temporal:** ajustando con enero–abril, 5 de los 26 días de mayo (19 %) no tienen ningún
  punto núcleo a menos de `eps`: serían «días desconocidos» para el gemelo.
- **Lecturas con las 29 variables:** en la rodilla, un clúster con 0,8 % de ruido. Con la mitad de
  ese `eps` aparecen 35 clústers que son **ventanas de fechas** (el mayor va del 21-mar al 14-abr).
  DBSCAN agrupa **semanas, no comportamientos**, arrastrado por la autocorrelación (§8 de
  `CLAUDE.md`) y la deriva de los sensores interiores (hallazgo 18). La selección de variables es
  la decisión que manda.
- **Lecturas con consumo y retardos, separadas por franja: anomalía contextual.** De madrugada el
  ruido (2,5 %) cubre el 100 % de las lecturas que superan el umbral, pero el 89 % de lo que marca
  está *por debajo* del umbral: consumo modesto pero raro para esa hora. En la tarde pasa lo
  contrario: el ruido cubre solo el 13 % de las lecturas altas, porque consumir mucho a esa hora es
  normal.

---

## 2. C2 Taller 3 — Clustering jerárquico

### 2.1 La decisión de fondo: la misma unidad que K-Means (días)

El enunciado pide comparar con K-Means («¿cambió la forma?», «¿se mantuvieron agrupamientos?»).
Esa comparación solo es directa **sobre la misma matriz**: 136 días × 24 medias horarias de
`Appliances`. Así se puede cruzar día por día quién cambia de grupo. Agrupar otra cosa (lecturas,
sensores) daría un taller nuevo, pero la comparación quedaría sin respuesta.

### 2.2 Preparación del dataset (punto 3 del enunciado)

- **Selección de variables:** la curva de consumo de 24 h, y *solo* esa. Justificación con datos del
  C2-T2: el calendario no explica los tipos (V de Cramér = 0,000) y el clima tampoco (ninguna
  variable con |d| > 0,5). Las variables de contexto (`lights`, humedades, T_out, fin de semana)
  sirven para **caracterizar después**, no para agrupar, igual que en K-Means: así se evita la
  circularidad.
- **Limpieza:** se descartan los 2 días incompletos (11-ene y 27-may); no hay nulos. **Los días
  atípicos no se eliminan**: son parte del objeto de estudio (*average* los aísla y el T4 los busca).
- **Escalado:** se aplica y se compara, no se da por hecho. La versión principal es la curva en Wh
  sin estandarizar, con la misma desviación declarada que en el C2-T2: las 24 columnas están en la
  misma unidad y su varianza va de 50 a 12.477. Como contraste va `StandardScaler`, que aquí **sí
  cambia el resultado** (ver §1.1). Es una lección sobre el método: el escalado que a K-Means le
  era indiferente decide el resultado del jerárquico.

### 2.3 Enlaces y dendrograma

- `scipy.cluster.hierarchy.linkage` con **ward, complete y average**, los tres del enunciado.
  *Single* solo en una nota al pie, porque encadena y repite lo de *average*.
- Un `dendrogram()` por enlace, sin etiquetas (136 hojas), coloreado por encima del corte elegido.
- **Correlación cofenética** por enlace: qué tan fielmente conserva cada árbol las distancias
  originales. Da la paradoja de §1.1: el árbol más fiel es el que produce la partición inútil.

### 2.4 Número de clústers (evaluación)

- **Silueta con k de 2 a 10** para los tres enlaces, con `fcluster(Z, k, criterion="maxclust")`. Una
  tabla y un gráfico con tres curvas.
- **Criterio adicional de Shiro: tamaño mínimo de clúster.** Un tipo de día con uno o dos ejemplares
  no lo puede aprender el agente (sus estados de la tabla Q casi no se visitan) ni lo puede estimar
  el simulador. Se exige que ningún clúster baje del 5 % de los días (7 días). Con esta regla,
  *average* queda descartado aunque tenga la mejor silueta, y el documento lo explica.
- **Índice de Dunn** (la función del profesor, sin modificarla) como métrica secundaria, por
  continuidad con el C2-T2.
- **Línea de corte:** para el k elegido, la altura se toma entre la fusión k-ésima y la (k−1)-ésima
  (`Z[-k, 2]` y `Z[-k+1, 2]`) y se dibuja sobre el dendrograma. Se verifica que
  `fcluster(Z, t, "distance")` con esa altura dé las mismas etiquetas que `maxclust`.

### 2.5 Visualización 2D

**Las mismas coordenadas PCA y t-SNE del C2-T2** (misma semilla, misma perplexity), para que las
figuras se comparen punto a punto. Irán en cuatro paneles: K-Means | Ward | complete | average.
Se resaltan los días que cambian de grupo entre K-Means y Ward (los 7 + 1 de frontera) y el día que
*average* aísla.

### 2.6 Interpretación y ejemplos representativos

- **Ejemplos por clúster:** el **medoide** (el día con menor distancia total al resto de su grupo) y
  los dos siguientes más típicos, en una tabla con fecha, día de la semana, kWh, hora pico, T_out y
  `lights`. Además, una fila para cada día aislado por *average* y *complete*, con lo que lo hace
  raro.
- Curvas medias de cada clúster superpuestas a los centroides de K-Means: si se tapan, el tipo de día
  no depende de la técnica.
- La jerarquía completa de Ward: qué se separa en el siguiente nivel. Con k = 3 los días normales se
  parten en 86 + 28, y ese grupo de 28 contiene 7 días que K-Means llama de carga alta: es la zona
  de frontera.

### 2.7 Comparación con K-Means (las tres preguntas del enunciado)

1. **¿Cambió la forma de los clústers?** K-Means y Ward producen grupos compactos y más o menos
   esféricos. *Complete* acota el diámetro del grupo, y *average* separa lo lejano. Se mide con el
   diámetro y la dispersión interna de cada clúster, y se ve en PCA/t-SNE.
2. **¿Se mantuvieron agrupamientos?** Tablas de contingencia K-Means × cada enlace, ARI y la lista de
   días que cambian, con su curva. La hipótesis es que los que cambian son solo los días de frontera.
3. **¿Qué técnica es más adecuada para Shiro?** Se decide con criterios de producto, no de nota:

| Criterio | K-Means | Jerárquico |
|---|---|---|
| Asignar un día nuevo | Sí: centroide más cercano | No tiene `predict`: hay que recalcular todo o usar centroides derivados |
| Estimar el tipo con el día a medio transcurrir (C2-T2 §7) | Sí, compara con la curva parcial del centroide | Solo a través de centroides derivados |
| Determinismo | Depende de la inicialización (`n_init`) | Determinista |
| Coste | Lineal en n | Matriz de distancias O(n²): trivial para 136 días, pero 1,6–3,1 GB para las 19.735 lecturas |
| Estructura anidada (para la capa de explicación) | No | Sí |
| Detecta días atípicos | No: los absorbe en algún grupo | *Average*/*complete* los aíslan |

**Conclusión esperada:** K-Means asigna el tipo de día en producción y el jerárquico queda como
**auditoría fuera de línea** y detector de días raros, que es exactamente la pregunta que retoma el T4.

### 2.8 Hipótesis que el taller pone a prueba

1. **Ward y *complete* reproducen los dos tipos de K-Means** → la variable de estado es robusta.
2. ***Average* aísla días atípicos**, y la silueta, usada sola, lo premia.
3. **El escalado importa en el jerárquico** aunque no importara en K-Means.
4. **Los días que cambian de grupo son de frontera**, no un tercer tipo escondido.

### 2.9 Producto

`Taller3_Jerarquico.ipynb` (corre de principio a fin), `Taller3_Jerarquico_RESUELTO.docx` y la
**presentación que pide el enunciado**, con la estética oscura de la consola, igual que las
anteriores. Esquema previsto de unas 11 diapositivas:

1. Portada: qué decide este taller para Shiro.
2. Dataset y preparación: selección, limpieza, escalado (y por qué el escalado aquí sí importa).
3. Tres enlaces, tres definiciones de «grupo».
4. **Tabla de silueta k 2–10 por enlace** y selección de k con la regla de tamaño mínimo.
5. **Dendrograma con línea de corte** (Ward, con complete y average a los lados).
6. La trampa: la mejor silueta es un solo día.
7. **Visualización 2D PCA / t-SNE**, los tres enlaces frente a K-Means.
8. **Tabla de ejemplos representativos por clúster** (medoides).
9. Contingencia con K-Means y días que cambian.
10. **Reflexión comparativa K-Means vs. jerárquico**: la tabla de §2.7.
11. Qué cambia en Shiro.

---

## 3. C2 Taller 4 — DBSCAN

### 3.1 Dos niveles, una sola pregunta: ¿qué no pertenece a ningún patrón?

- **Parte A · Días (principal):** la misma matriz de 136 × 24. Cierra la cadena K-Means →
  jerárquico → DBSCAN y permite responder «¿qué puntos fueron ruido?» con fechas concretas.
- **Parte B · Lecturas de 10 minutos:** la anomalía **contextual** para la capa Guardian. Es la
  parte que más aporta al producto, y la que muestra con más claridad por qué hay que «separar por
  grupos».

### 3.2 Parte A — días (pasos 1–7 del enunciado)

1. **Columnas:** las 24 medias horarias, como en T2 y T3.
2. **Escalado:** versión principal en Wh, porque así `eps` se puede leer. 208 Wh de distancia
   euclídea en 24 dimensiones son unos 42 Wh por hora en media cuadrática: «dos días son vecinos si
   difieren en unos 42 Wh por hora». La versión estandarizada entra como contraste.
3. **Gráfico de k-distancias** con min_samples ∈ {3, 4, 5, 8}. La regla habitual (min_samples ≥
   dimensiones + 1 = 25) exige tomar un 18 % de la muestra como vecindario mínimo. Se declara, y como
   contraste se corre DBSCAN sobre las primeras componentes de PCA (pocas dimensiones →
   min_samples = 2·D ya es razonable).
4. **El codo:** la rodilla se detecta como el punto más alejado de la cuerda entre los extremos de
   la curva (un Kneedle simplificado, sin librería nueva) y se marca en el gráfico.
5. **DBSCAN con los parámetros de la rodilla.**
6. **Visualización** en las mismas coordenadas PCA/t-SNE, con el ruido como cruces grises. Se espera
   el caso «todo un gran grupo» → **se separa por grupos**, y el grupo elegido es el **tipo de día**
   (validado en T2 y T3). Separar por fin de semana sería una peor decisión, porque el calendario no
   explica el consumo (V = 0,000); va como contraste para mostrarlo. Cada tipo recibe su propio `eps`.
7. **Respuestas:**
   - *¿Cuántos clústers?* Global y por grupo.
   - *¿Qué puntos son ruido?* La lista de días con fecha, día de la semana, kWh y hora pico, y qué
     los hace raros comparados con el medoide de su tipo.
   - *¿Cómo cambia con eps y min_samples?* Mapas de calor eps × min_samples con el número de
     clústers, el % de ruido y el ARI con K-Means. Se define como **«atípico robusto»** el día que es
     ruido en la mayoría de la rejilla, no en una sola configuración.
   - *¿Implicaciones en el sector?* Ver §3.5.
8. **Control temporal** (convención §4.2): ajuste con enero–abril. Un día de mayo sin ningún punto
   núcleo a menos de `eps` es un «día desconocido» para el gemelo.

### 3.3 Parte B — lecturas: anomalía contextual

1. **Primero, todas las variables.** Las 29 variables estandarizadas: DBSCAN agrupa ventanas de
   fechas. Se muestra con el rango de fechas de cada clúster y sirve para justificar la selección.
2. **Selección:** `Appliances` y los retardos del parcial (`lag1`, `media_1h`, `std_1h`), la
   ingeniería de variables que más rindió en el proyecto. Se aplica `log1p` porque la cola es larga y
   luego `StandardScaler`, ajustado solo sobre entrenamiento. `lights` y `Appliances` solos no
   sirven: están cuantizados en pasos de 10, hay miles de puntos repetidos y la k-distancia de la
   rodilla sale exactamente 0.
3. **Global → un gran grupo con ~4 % de ruido → se separa por franja.** La franja es la
   segmentación que el proyecto ya usa (§4.1: nunca entra al modelo, solo segmenta) y la que mostró
   que el error cambia con la hora (hallazgo 14).
4. **Por franja:** k-distancias, rodilla y DBSCAN. Tabla con el % de ruido, el % del ruido que supera
   el umbral y el % de las lecturas sobre el umbral que el ruido cubre. Ejemplos concretos: lecturas
   de madrugada bajo el umbral marcadas como raras, y lecturas de la tarde sobre el umbral que DBSCAN
   considera normales.
5. **Temporal:** ajuste por franja con enero–abril y aplicación a mayo. Se compara cuánto marca
   DBSCAN con cuánto marca el umbral fijo, que en mayo casi no se dispara porque el consumo baja.
6. **Coste:** unas 4.900 lecturas por franja, instantáneo.

### 3.4 Hipótesis

1. **Un `eps` global produce un solo gran grupo**, y los días de carga alta caen todos en el ruido.
2. **Separados por tipo, cada uno tiene su densidad**: carga alta es alrededor del doble de dispersa.
3. **Con las 29 variables DBSCAN encuentra semanas, no comportamientos.**
4. **Por franja, el ruido es anomalía contextual** y no coincide con el umbral: marca de más de
   madrugada y de menos en la tarde.

### 3.5 Qué podría cambiar en Shiro (a confirmar con los números del cuaderno)

- **Incertidumbre del simulador por tipo de día**, no solo por franja. Si los días de carga alta son
  unas 2 veces más dispersos, el gemelo es menos fiable justo esos días, y el agente no debe confiar
  igual en su predicción.
- **«Carga alta» es una desviación de la rutina, no una segunda rutina.** Si DBSCAN no la ve como
  grupo denso, su forma es poco anticipable, y la política en esos días debe ser reactiva: esperar la
  joroba de las 11 h, como ya sugería el C2-T2.
- **Filtro de datos del gemelo:** los atípicos robustos se marcan. No se borran, pero no deben
  definir la rutina.
- **Guardian con dos tipos de alarma:** *consumo alto* (umbral, habla de costo) y *consumo raro para
  la hora* (DBSCAN, habla de desperdicio o de un aparato olvidado). Las anomalías contextuales de
  madrugada son el candidato natural para ahorro en espera (*standby*).

### 3.6 Producto

`Taller4_DBSCAN.ipynb`, `Taller4_DBSCAN_RESUELTO.docx` y una presentación corta (unas 9 diapositivas,
a confirmar: el enunciado de DBSCAN no la pide de forma explícita).

---

## 4. Riesgos y cómo se manejan

| # | Riesgo | Manejo |
|---|---|---|
| R1 | La rodilla con 136 puntos en 24 dimensiones marca ~40 % como ruido: demasiado para llamarlo «anomalía» | Se reporta la sensibilidad completa. «Ruido» se define como baja densidad, no como anomalía, y solo se habla de atípico robusto cuando lo es en la mayoría de la rejilla |
| R2 | Circularidad: separar por los tipos de K-Means y luego comparar con K-Means | Se declara, y se añade el contraste con otra agrupación (fin de semana) |
| R3 | Autocorrelación: lecturas consecutivas son vecinas y DBSCAN puede encadenar el tiempo | Se revisa el rango de fechas de cada clúster de lecturas: si un clúster es una semana, se dice |
| R4 | `Appliances` cuantizado en pasos de 10 Wh (puntos duplicados, eps = 0) | Se usan variables continuas (medias y desviaciones de la última hora) y se declara |
| R5 | Sobreinterpretar «carga alta = ruido» | Es una afirmación de densidad, no de rareza. Se contrasta con el `eps` propio de cada tipo |
| R6 | Repetir el C2-T2 | Todo resultado se presenta como *comparación* con K-Means, nunca como descubrimiento nuevo de los mismos tipos |

---

## 5. Qué se reutiliza

- Del C2-T2: la carga de datos, la matriz `NIVEL`, la tabla `info` de caracterización, las
  coordenadas PCA/t-SNE, `ordenar()`, la paleta, `dunn_index` y la función de observabilidad.
- Del parcial: el umbral de la convención §4.3 y la construcción de retardos.
- Scripts: `docx_estilo.py`, `pptx_estilo.py`, `exportar.ps1` y `revisar_pdf.py` (páginas vacías,
  asteriscos sueltos, figuras presentes).

## 6. Orden y estructura de carpetas

**T3 primero:** es la continuación directa del C2-T2 y su conclusión (qué agrupación usar) es la que
el T4 necesita para «separar por grupos».

```
2do_Corte_Oct/
├─ Plan_Talleres_Corte2.md            (T1 y T2, terminados)
├─ Plan_Talleres_3_4_Corte2.md        ← este documento
├─ Taller_3_Jerarquico/               (+ figuras/ J1…)
└─ Taller_4_DBSCAN/                   (+ figuras/ D1…)
```

---

## 7. Decisiones tomadas (28-sep-2026)

1. **Ubicación:** C2-T3 y C2-T4 dentro de `2do_Corte_Oct/`. Si el profesor los cuenta en el 3.er
   corte, se mueven sin cambiar nada más.
2. **Unidad del T3:** días (necesario para comparar con K-Means).
3. **Alcance del T4:** ✅ Parte A (días) + Parte B (lecturas por franja).
4. **Presentación del T4:** ✅ sí, corta.
5. **Arranque:** ✅ se ejecutan los dos talleres ya, T3 primero.
