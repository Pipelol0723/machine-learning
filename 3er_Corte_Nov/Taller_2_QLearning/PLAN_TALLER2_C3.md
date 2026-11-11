# Plan: Taller 2 del Corte 3 (Q-learning), el agente de Shiro que aprende sin conocer el modelo

*Redactado el 2026-11-11. **Classroom: «C3 Taller2», publicado el 6-nov, fecha límite HOY (11-nov).** La tarea no
trae texto propio: el enunciado está en el PDF adjunto. No indica formato de entrega; se sigue el del Taller 1
(cuaderno + documento + presentación corta).*

---

## 0. Material descargado (`Documentacion/`)

| Archivo | Qué es |
|---|---|
| `TALLER 2 -QLEARNING RL.pdf` | **Enunciado** (2 pp.), con cuatro partes (resumen en §1). |
| `RL_QLEARNING.ipynb` | Código del profesor (fresas, `ProductPriceIndex.csv`): pasos 1–5, Q-table con pandas y gráficas de distribución, curva de aprendizaje, decaimiento de ε y *heatmap* de la Q-table. |
| `RL_Q-Learning.pdf` | Diapositivas de clase: ε-greedy, Q-learning *model-free* («jugar el videojuego sin el código fuente») frente al MDP *model-based*, y lectura de las gráficas. |

## 1. Qué pide el enunciado

| Parte | Qué hay que hacer | Gráficas |
|---|---|---|
| **1 · Explorador de entornos** | Correr el problema A, cambiar la variable objetivo (problema B), volver a correr y comparar las dos políticas. ¿Qué dice eso de la «personalidad» de cada caso? | — |
| **2 · Sintonizador** | γ 0,5 frente a 0,99 y α 0,01 frente a 0,9 sobre el problema base. | Curva de aprendizaje, decaimiento de ε y *heatmap*, **por cada cambio** |
| **3 · Arquitecto del mundo** | Correr con `pd.qcut` y después con K-Means (`.labels_`) en los estados. ¿Cambia la política? ¿Es mejor? ¿Por qué K-Means es más «realista»? | Las mismas, por cada cambio |
| **4 · Ingeniero de recompensas** | Recompensa lógica frente a «+1 por transacción» y frente a «penalización −1000 si la ganancia es negativa». | Las mismas, por cada cambio |

### Lo que el código del profesor hace y que el de Shiro no debe heredar
1. **La «acción» no la controla el agente.** Es la cubeta del precio de venta en Atlanta, un dato observado. El agente
   aprende qué combinaciones (estado, precio) se dieron con más ganancia, no qué decisión conviene. La propia diapositiva
   108 del Taller 1 dice que las acciones deben estar bajo el control del agente.
2. **Cada «episodio» es un solo paso desde un estado al azar.** No hay secuencia, así que γ casi no tiene a quién
   propagarle valor y la «curva de aprendizaje» sigue sobre todo a ε: sube porque se exploran menos combinaciones
   castigadas con −100, no porque el agente aprenda.
3. **El −100 por combinación nunca vista** enseña a evitar lo que no está en los datos, no lo que es malo.

Para Shiro se conservan los nombres y la estructura de pasos del profesor, pero las acciones son decisiones reales
(las del C3-T1) y **cada episodio es un día completo de 24 horas**, como fija la propuesta del proyecto.

---

## 2. Apertura Shiro (plantilla)

1. **Qué se construye.** El agente que **aprende sin conocer el modelo**. En el C3-T1 Shiro resolvió el MDP de este
   hogar con iteración de valor porque tenía la tabla P contada. En un hogar nuevo (Shiro Home) esa tabla no existe: el
   agente tiene que aprender jugando. Q-learning es esa pieza y es el puente al DQN del Taller 3.
2. **Qué decisiones de arquitectura dependen del resultado.**
   - **¿Q-learning recupera la π\* del C3-T1, y con cuántos días de experiencia?** El MDP resuelto es la respuesta
     correcta, así que se puede medir el % de estados en que coinciden. Esa cifra es el «arranque en frío» de Shiro
     Home: cuántos días necesita el agente en una casa nueva antes de proponer bien.
   - **Qué α, γ y ε** sirven a un agente que seguirá aprendiendo cada mes (hallazgo 10).
   - **Si la definición del estado cambia la política**: qcut frente a K-Means (C2-T2 a C2-T4).
   - **Qué recompensas rompen a Shiro.** Un Shiro «nervioso» que aplaza por aplazar repite la fatiga de alertas de
     Guardian (hallazgos 20 y 26). Uno «miedoso» nunca actúa. Y está el que nunca ejecuta (hallazgo 32).
3. Después: entorno, algoritmo e hiperparámetros (§3–§4).
4. Cierre: qué cambia en Shiro (§5, último punto).

---

## 3. Diseño

### 3.1 Agente, estados, acciones y recompensa: los del C3-T1, sin cambios
- **Estado:** 40 estados = tipo de día estimado (K-Means sobre la curva parcial) × franja × nivel (<60 / 60–200 /
  >200 Wh) × carga pendiente. **Acciones:** {no actuar, aplazar, ejecutar}, con las mismas reglas de validez.
- **Recompensa:** r = −tarifa·E − λ·espera, con **contabilidad corregida** (hallazgo 32). Tarifa valle 1,0 y punta 1,5;
  f = 0,40; perfil paciente λ = 0,005. ΔE = 310 Wh es el valor de referencia del C3-T1; en el entorno de réplica se
  usa el ΔE de cada hora (§3.2).
- Partición temporal: el agente **aprende con enero–abril** (110 días) y **se evalúa en mayo** (26 días), repitiendo el
  mes con su política voraz final, igual que la batalla del C3-T1.

### 3.2 Dos entornos (Paso 3)
| Entorno | Cómo genera s′ y r | Para qué sirve |
|---|---|---|
| **Réplica de días reales** (principal, al estilo del profesor: «el dataset como simulador») | Cada episodio es un día de entrenamiento al azar, recorrido hora por hora con su demanda real. La acción mueve la energía y la carga pendiente. | Lo que vería Shiro aprendiendo con datos reales. |
| **Modelo contado** (control) | s′ ~ P_datos del C3-T1 y R medias del C3-T1. | Es *exactamente* el MDP que resolvió la iteración de valor, así que Q-learning debe converger a π\*. Prueba el algoritmo por separado de los datos. |

La diferencia entre los dos entornos mide cuánto se aleja la realidad del modelo de Markov. Por ejemplo, la hora
dentro de la franja, que el hallazgo 35 ya sospechaba.

**Detalle de realismo del entorno de réplica:** la energía que se puede aplazar en cada hora es
ΔE_t = 0,40 · (exceso real sobre 200 Wh) y el entorno guarda cuánta energía quedó pendiente. Así no se aplaza lo que no
existe. Se documenta como diferencia con el modelo de valor medio.

### 3.3 Agente (Paso 4)
- Q-table en NumPy (40 × 3; acciones inválidas enmascaradas), no `DataFrame.loc`: miles de episodios en segundos.
- Hiperparámetros base del profesor: α = 0,1; ε de 1,0 a 0,01 con decaimiento 0,999 por episodio. γ = 0,95, el del
  C3-T1, para poder comparar con π\* (el 0,9 del profesor queda como variante).
- **Episodios:** 5.000 días simulados, unas 45 pasadas por cada día de entrenamiento. **5 semillas** por configuración,
  para que «¿es una más estable?» se responda con bandas y no con una sola curva.
- **Métricas por configuración** (todas por semilla, con media y rango):
  - curva de aprendizaje: recompensa por episodio, media móvil;
  - decaimiento de ε;
  - *heatmap* de la Q-table;
  - **% de estados en que la política coincide con π\*** (VI) a lo largo de los episodios;
  - repetición de mayo: costo, ahorro, horas de espera y aplazamientos por día.

---

## 4. Las cuatro partes, traducidas a Shiro

### Parte 1 · Explorador de entornos: ¿la política es la misma en otro problema?
**Decisión abierta (D1): qué es el «problema B».**

| Opción | Qué compara | Costo | Qué le aporta a Shiro |
|---|---|---|---|
| **B1 · Otro hogar: UCI Household #235** (recomendada) | El mismo agente y el mismo diseño de estados en una casa de Francia, en la misma estación (ene–may 2008), con umbrales por percentil equivalentes (nivel alto = el mismo 10,9 % de las horas) y K-Means propio. | Descargar unos 20 MB de UCI y procesarlos: +1 a 1,5 h | Responde la pregunta de Shiro Home: **¿la política se transfiere entre hogares o cada casa tiene su «personalidad»?** Cierra un pendiente abierto desde el 1.er corte (fuente secundaria). |
| B2 · Otra estación del mismo hogar | Agente entrenado en invierno (ene–abr) frente a uno entrenado solo con mayo (26 días). | Bajo | Conecta con la recalibración mensual (hallazgos 13 y 18) y con el arranque en frío (26 días). |

Análisis común: la política estado por estado (dónde coincide y dónde no), los valores Q, y la «personalidad»: cuántas
horas altas, qué tan lejos queda el valle y cuánto se puede aplazar.

### Parte 2 · Sintonizador (sobre el problema base)
- **γ = 0,5 frente a 0,99.** Cada agente se compara con la π\* de la iteración de valor **para ese mismo γ**. Pregunta
  Shiro: el agente miope, ¿deja de ver que la carga pendiente hay que ejecutarla en el valle?
- **α = 0,01 frente a 0,9**, con las tres gráficas por cambio y bandas de 5 semillas. Pregunta Shiro: con α = 0,9,
  ¿un día raro desordena lo aprendido? Eso decide el α del reentrenamiento mensual.
- Resultado esperado y medible: días hasta alcanzar el 90 % de coincidencia con π\*. **Es el arranque en frío.**

### Parte 3 · Arquitecto del mundo: qcut frente a K-Means
- **Base (qcut):** nivel por terciles (`pd.qcut(q=3)`, cortes en unos 52 y 88 Wh) y franja, sin tipo de día.
- **K-Means:** tipo de día con K-Means k = 2 (`.labels_`, C2-T2) y nivel con **K-Means k = 3 sobre el consumo
  horario**, que encuentra los cortes «naturales». También se compara con el umbral de 200 Wh del C3-T1 como referencia.
- Las acciones **no** se agrupan con K-Means, a diferencia del ejemplo: en Shiro son decisiones, no datos. Se explica
  por qué (Shiro primero).
- Análisis: ¿cambia la política? ¿Da más recompensa en mayo? Hipótesis para contrastar: con terciles, «alto» incluye
  horas sin nada que aplazar (el tercil superior arranca en unos 88 Wh, y el 200 Wh del proyecto es el percentil 90).

### Parte 4 · Ingeniero de recompensas
| Recompensa | Qué se espera | Lectura Shiro |
|---|---|---|
| Base (lógica: costo + λ·espera, contabilidad corregida) | π\* del C3-T1 | — |
| **+1 por cada acción** (aplazar o ejecutar) | Aplaza y ejecuta en ciclo para «hacer cosas»: los aplazamientos por día se disparan | El **Shiro nervioso**: fatiga de alertas, como el punto de operación del parcial 1 (hallazgo 20) |
| **Ganancia neta del paso frente a no actuar, con −1000 si es negativa** | Esperar (−λ) o ejecutar en punta salen negativos, así que deja de aplazar y queda en «no actuar» casi siempre | El **Shiro miedoso**: nunca propone |
| *(extra)* Contabilidad ingenua del C3-T1 | Aplaza y nunca ejecuta (hallazgo 32) | ¿Q-learning cae en la misma trampa que la iteración de valor? |

Por cada recompensa: las tres gráficas, más aplazamientos por día, horas de espera y costo real en mayo, medido siempre
con la cuenta real y no con la recompensa trucada.

---

## 5. Entregables (patrón del C3-T1: todo se regenera desde `generadores/`)

```
3er_Corte_Nov/Taller_2_QLearning/
├─ Documentacion/                        (material del profesor)
├─ PLAN_TALLER2_C3.md                    (este plan)
├─ Taller2_C3_QLearning_Shiro.ipynb      (pasos 1–5 adaptados y partes 1–4; corre de principio a fin)
├─ Taller2_C3_QLearning_RESUELTO.docx/.pdf
├─ Taller2_C3_presentacion.pptx/.pdf     (≈ 10 diapositivas)
├─ cifras.json · figuras/ (Q1…Qn) · politicas_*.csv
└─ generadores/ construir_cuaderno.py · generar_documento.py · generar_presentacion.py · verificar.py
```
- El entorno y el MDP del C3-T1 se reutilizan **copiando** sus funciones al generador nuevo (estados, P, R, iteración de
  valor). No se importan desde la otra carpeta, para que cada taller se regenere solo.
- **Cierre Shiro:** días de arranque en frío, α y γ recomendados, si la definición del estado cambia la política, qué
  recompensas quedan prohibidas en el entorno de Q-learning/DQN y (si se elige B1) si la política se transfiere a otro
  hogar.
- `verificar.py` con las mismas reglas del C3-T1: sin errores, sin residuos, todo decimal sale de `cifras.json`, más la
  cordura de que en el entorno modelo Q-learning coincide con π\* en al menos el 90 % de los estados.

## 6. Orden de trabajo para hoy

| # | Paso | Tiempo |
|---|---|---|
| 1 | Generador del cuaderno: entorno (réplica y modelo), agente y la cordura contra π\* | ≈ 1 h |
| 2 | Partes 2 a 4: barridos con 5 semillas y figuras | ≈ 1 h |
| 3 | Parte 1: B1 (+1 a 1,5 h, con descarga de UCI #235) o B2 (≈ 20 min) | según D1 |
| 4 | Documento y presentación con los generadores del C3-T1 adaptados | ≈ 1,5 h |
| 5 | `verificar.py`, revisión de PDF, `CLAUDE.md`, commit; entrega en Classroom por Drive (`G:\Mi unidad`), como en el C3-T1 | ≈ 30 min |

**Total: unas 4,5 h con B2 y 5,5–6 h con B1.**

## 7. Decisiones (tomadas por el usuario el 2026-11-11)

| # | Decisión | Elegida |
|---|---|---|
| D1 | Problema B de la Parte 1 | **B2: otra estación del mismo hogar.** Agente que aprende con enero–abril frente a uno que aprende solo con mayo, con transferencia cruzada entre los dos. |
| D2 | Formato | **Cuaderno + documento (docx/PDF) + presentación corta**, como el C3-T1 |
| D3 | Entrega | **La hace Claude** al terminar y verificar (adjuntar por Drive y entregar), como el C3-T1 |
| D4 | Alcance | **Completo:** 5 semillas, entorno de réplica + entorno modelo, y la contabilidad ingenua como extra |
| D5 | Base del agente | **γ = 0,95 y λ = 0,005 del C3-T1** (el 0,9 del profesor como variante). El documento debe explicar en una sección propia **por qué se usan nuestros datos, nuestro MDP y nuestra π\* y no el ejemplo del profesor**. |
| D6 | Episodio | Un día (24 pasos), no un paso suelto como en el ejemplo |
| — | ΔE | **Constante (310 Wh), como en el C3-T1**, para que π\* repetida en mayo reproduzca al decimal las cifras del C3-T1 (anclas). Reemplaza la idea de ΔE por hora de §3.2. |

## 8. Riesgos
- **Q-learning no alcanza a π\* en los estados poco visitados** (mínimo 4 visitas en el C3-T1). Se reporta la
  coincidencia ponderada por visitas, y en los estados raros manda «no actuar».
- **Los Q con γ = 0,99 son grandes y lentos de converger.** Más episodios solo para ese experimento, declarado.
- **El ahorro es pequeño (0,59 % en el C3-T1)** y las diferencias entre configuraciones pueden no separarse del ruido.
  Se dice así, con bootstrap por día, como en el C3-T1.
