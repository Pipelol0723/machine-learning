# Plan: Taller 1 del Corte 3 (RL / MDP), el MDP de Shiro Twin

*Redactado el 2026-11-04. **Classroom marca «Fecha límite: Hoy» (5 puntos).** Tarea «C3 Taller1», publicada por
Hernán Cruz Bueno el 30-oct. La tarea no trae texto propio: todo el enunciado está en el PDF adjunto.*

> **Ejecutado el mismo día.** Las cifras finales están en `cifras.json` y prevalecen sobre las de este plan. Desviaciones:
> - **ΔE = 310 Wh, no ≈ 125 Wh.** La exploración previa promedió el exceso sobre el tercil alto, no sobre el nivel > 200 Wh;
>   el exceso real es de 776 Wh/h.
> - **Repetir estado a 10 min: 0,73, no 0,82** (corte en < 60 Wh, igual que en el paso horario).
> - **Contabilidad corregida de la carga aplazada.** Con descuento, pagar después parecía ahorro y la contabilidad ingenua
>   no ejecutaba nunca.
> - **Perfil «exigente» (λ = 0,02).** Se añadió para las reglas de oro, porque con λ = 0,005 π\* = codiciosa en los 40
>   estados.

---

## 0. Material descargado (`Documentacion/`)

| Archivo | Qué es |
|---|---|
| `ML_TALLER 1 CORTE 3 - RL.pdf` | **Enunciado** (3 pp.): Parte 1 diseño (5 preguntas), Parte 2 adaptar el código, Parte 3 «batalla de las políticas». |
| `RL_MDP.ipynb` | Código del profesor (fresas, `ProductPriceIndex.csv`): pasos 1–5 + gráficas de precios y de distribución de política. Es el código que hay que adaptar. |
| `RL_MDP 26.pdf` | Diapositivas de clase (123): MDP, Bellman, iteración de valor, guía de diseño por sector, política codiciosa frente a óptima. |
| `Ejemplo MDP.pdf` | Ejemplo de otro grupo (marketing bancario, 21 diapositivas): 4 clústers como estados, 5 acciones, Q por acción en cada estado, 3 «reglas de oro», MDP frente a política simple (+22,2 %). **Marca el formato esperado; no se copia.** |

## 1. Qué pide el enunciado

- **Parte 1, documento de diseño.** Responder: (1) objetivo y agente: una **única** decisión; (2) acciones finitas; (3)
  estados con información **mínima**, usando el clustering y justificando 2–3 variables contra la maldición de la
  dimensionalidad; (4) recompensa numérica; (5) transición: Opción A, conteo `shift(-1)`, u Opción B, el modelo
  supervisado «llena» la tabla P.
- **Parte 2, adaptar el código.** Paso 1: limpieza. Paso 2: quitar `pd.qcut` y asignar estados con `.predict()` del
  clustering o con una discretización propia. Paso 3a: recompensa con reglas de negocio. Paso 3b: construir P. Pasos 4 y 5:
  iteración de valor y extracción de π*, «casi sin cambios».
- **Parte 3, evaluar y justificar.** Gráfica de distribución de la política, qué acciones favorece y si tiene sentido. Además,
  **2–3 reglas de oro** no obvias, explicadas con R y P (como el «dilema NY contra Chicago»).

### Lo que el código del profesor no hace, y que para Shiro es el punto central

En `RL_MDP.ipynb` la transición es `P(s'|s)`: **no depende de la acción** (diapositiva 59: «el distribuidor es pequeño, no
mueve el mercado»). Por eso, dentro del bucle de acciones, `expected_future_value` es el mismo para las cuatro ciudades.
Así, **π\* = argmax R(s,a): la política óptima coincide con la codiciosa** y el dilema de las diapositivas 120–121 no
puede aparecer con ese código. Para que un MDP le aporte algo a Shiro, la acción tiene que **cambiar el futuro**. Eso
condiciona todo el diseño que sigue (estado «carga pendiente»).

---

## 2. Apertura Shiro (plantilla del 2.º corte en adelante)

1. **Qué se construye.** El **MDP formal de Shiro Twin**, criterio de cierre aún abierto («MDP formalizado por escrito y
   agente de Q-learning…»), y la tabla de transición que el Taller 2 del corte usará para Q-learning. La diapositiva 30 lo
   anuncia: «Entrenar un agente Q-Learning … (Taller 2), primero MDP».
2. **Qué decisiones de arquitectura dependen del resultado.**
   - El **espacio de estados**: ¿cabe el tipo de día estimado (C2-T2, hallazgos 21–22)? ¿Hace falta una variable
     aparte para la probabilidad de pico de G0 (hallazgo 27)?
   - Si la **transición depende de la acción**: sin «carga pendiente», aplazar equivale a *borrar* consumo, que es el
     ahorro ficticio del hallazgo 3 («el agente explota errores del entorno»).
   - **λ, el precio de una hora de espera**: a partir de qué valor deja de convenir aplazar. Es el parámetro que la persona
     ajustaría, análogo al umbral ajustable del hallazgo 9.
   - Qué hace el agente en estados **poco visitados**: política conservadora (hallazgo 24).
3. Después: datos, algoritmo y parámetros (§3–§4).
4. Cierre: qué cambia en el diseño de Shiro por estos números (§5, último punto).

---

## 3. Diseño del MDP (Parte 1): propuesta con valores por defecto

**Q1. Objetivo y agente.** El agente es **Shiro**: propone y la persona aprueba; en el gemelo se supone la aprobación.
Decisión única: **cada hora, ¿dejo correr la carga desplazable del hogar o la aplazo (y cuándo la ejecuto)?** Objetivo:
minimizar el costo energético ponderado por tarifa **sin imponer esperas largas**.

**Q2. Acciones**: A = {**No actuar**, **Aplazar** la carga desplazable, **Ejecutar** la carga pendiente}.
- *Aplazar* solo es válida con nivel = alto y sin carga pendiente (hay un solo cupo). *Ejecutar* solo es válida con carga
  pendiente. En los demás casos Q = −∞ y la acción no se elige.
- **Excluida a propósito:** «ajustar la consigna ±1 °C» de la propuesta. El dataset no trae actuador térmico ni dato que
  mida su efecto, así que modelarla sería inventar la física. Se declara como límite.

**Q3. Estados**: s = (**tipo de día estimado**, **franja**, **nivel de demanda**, **carga pendiente**), con
2 × 4 × 3 × 2 = **48 teóricos**.
- *Tipo de día* (la conexión con el aprendizaje no supervisado que pide el enunciado): K-Means k = 2 del C2-T2
  (`n_init=10, random_state=42`), **ajustado solo con los 110 días de entrenamiento**, que dan 25 de carga alta y
  centroides de 12,3 frente a 20,7 kWh/día. Asignación en línea con la **curva parcial**: centroide más cercano sobre las
  horas ya vistas. Antes de las 8 h el tipo es «normal», porque el C2-T2 mostró que antes de esa hora asignar con la curva
  parcial es peor que decir siempre «normal». Equivale a `.predict()` restringido a las horas observadas, y es el
  «estimado que se actualiza» del hallazgo 21.
- *Franja*: madrugada 0–6, mañana 6–12, tarde 12–18, noche 18–24 (convención §4.1, aquí sí dentro del estado).
- *Nivel*: media horaria de lecturas < 60 / 60–200 / > 200 Wh, con el umbral de 200 Wh de §4.3.
- *Carga pendiente*: 0 o 1. No sale del dataset: la crea la acción.
- **Justificación contra la maldición de la dimensionalidad** (exploración ya corrida, paso horario):
  - Cobertura: de las 24 combinaciones exógenas aparecen 20 en el entrenamiento, con mediana de **74 visitas por estado** y
    mínimo de 4 (carga alta · tarde · bajo).
  - Las ausencias son ceros estructurales: no hay «carga alta» en la madrugada porque el tipo no es observable antes de las
    8 h.
  - Mayo visita 19 estados y **ninguno es nuevo**.
  - Con la hora (24) en lugar de la franja serían 288 estados exógenos y unas 9 visitas por estado: P no sería estimable.
  - **G0 no necesita variable propia.** Sus dos entradas, consumo actual y hora × laborable, ya son *nivel* y *franja*, así
    que la P contada generaliza a G0.
- **Paso de decisión de 1 hora, no de 10 minutos.** A 10 min la probabilidad de quedarse en el mismo estado es **0,82**
  (P ≈ identidad, autocorrelación §8.1); por hora es **0,60**. Además, aplazar se decide a escala de horas.

**Q4. Recompensa** (en kWh-equivalentes de valle, sin pesos, como se decidió en el Parcial 2):

  r(s,a) = −tarifa(franja) · E(s,a) − λ · [queda carga pendiente tras a]

- **E(s,a)** = demanda media del estado (un `groupby` como el del profesor) − ΔE si se aplaza + ΔE si se ejecuta.
- **ΔE = f · exceso sobre 200 Wh.** El exceso medio en horas de nivel alto es **312 Wh/h** (entrenamiento). Se toma
  **f = 0,40**, anclado en el hallazgo 31: solo el 39,7 % del exceso estaba en picos avisables. Resultado: ΔE ≈ 125 Wh.
- **Tarifa** por defecto: valle (madrugada) = 1,0 y punta (resto) = **r = 1,5**. Se hace sensibilidad con r ∈ {1,0; 1,25;
  1,5; 2,0}. **Prueba de cordura: con r = 1,0 π\* no debe aplazar nunca.**
- **λ** = costo de cada hora con la carga esperando. No se mide: se barre λ ∈ {0; 0,002; 0,005; 0,01; 0,02} y se reporta el
  **λ crítico por franja** (a partir del cual deja de aplazar). El valor por defecto es el centro de la rejilla y se dice
  que es un supuesto.

**Q5. Transición**: P(s'|s,a) = P_datos(x'|x) · P_acción(p'|p,a), con x = (tipo, franja, nivel).
- **Opción A (implementada):** conteo `shift(-1)` sobre la serie horaria de **entrenamiento (hasta el 30-abr)**, igual que
  el profesor. Supuesto declarado: lo que el hogar *demanda* no depende de que Shiro aplace (aplazar no cambia lo demás que
  la gente enciende).
- **Parte determinista:** aplazar → p' = 1; ejecutar → p' = 0; no actuar → p' = p.
- **Opción B (explicada, no implementada):** consultar el simulador lineal + retardos (la función de transición ya
  decidida, hallazgos 11 y 30) con los residuos por franja × tipo de día cientos de veces, para llenar la tabla. Ese es el
  entorno de Q-learning del Taller 2. Contraste opcional si sobra tiempo: P_A(nivel' = alto | franja, nivel) frente a la
  tabla de G0.

**γ = 0,95 por hora**: vida media de unas 13,5 h, lo que dura una espera hasta el valle. Sensibilidad con
{0; 0,5; 0,9; 0,95; 0,99}; **γ = 0 es exactamente la política codiciosa**. **θ = 1e-6**, porque las recompensas que
importan son del orden de 0,06 kWh-eq (regla de la diapositiva 76).

---

## 4. Implementación (Parte 2)

Cuaderno `Taller1_C3_MDP_Shiro.ipynb`, generado por `generadores/construir_cuaderno.py` y ejecutado con `nbclient` (patrón
del Parcial 2). Conserva los **nombres de paso del profesor** para que el evaluador reconozca su código:

| Paso | Contenido |
|---|---|
| 1 | Carga y limpieza: 136 días completos, serie horaria, partición temporal 110 / 26 días. |
| 1.5 | Gráfica de justificación, equivalente a la de precios: demanda por hora y tipo de día, con la punta y el valle. |
| 2 | Estados: **se elimina `pd.qcut`**. K-Means + `.predict` sobre la curva parcial, franja, nivel y pendiente. Tabla de cobertura de estados. |
| 3a | `R_table` por `groupby` y reglas de negocio (ΔE, tarifa, λ). |
| 3b | `P_dict[s][a][s']`, con la parte contada más la parte de la acción. |
| 4 | Iteración de valor. **Único cambio al código del profesor:** `expected_future_value` pasa a calcularse **dentro** del bucle de acciones, porque P depende de a. Acciones inválidas con −∞. |
| 5 | π\*, CSV de política, gráfica de distribución de la política (la pedida) y V\*(s). |

## 5. Evaluación (Parte 3)

- **Interpretar.**
  - Gráfica de distribución de la política (obligatoria).
  - Mapa de la política (tipo × franja × nivel × pendiente) y V\*(s) por estado, como la diapositiva 19 del ejemplo.
- **Reglas de oro.** Estados donde **π\* ≠ codiciosa**, cada uno con su desglose Q(s,a) = R + γ·ΣP·V\* y las filas de P que
  lo explican. Candidatas a confirmar o refutar con los datos, sin prometerlas:
  - En la noche se aplaza y en la mañana no, porque el valle está cerca o lejos.
  - En un día de carga alta se reserva el cupo para la joroba de las 17 h en vez de gastarlo en la de las 11 h.
  - Con carga pendiente en la tarde, se espera en lugar de ejecutar.
- **Batalla de las políticas.**
  - Escenario: **repetición de mayo**, los 26 días fuera de muestra. Lo exógeno es real; las acciones mueven ΔE y la carga
    pendiente.
  - Contendientes: no actuar, codiciosa (γ = 0), regla fija («aplazar todo nivel alto y ejecutar en la madrugada») y π\*.
  - Métricas: costo en kWh-eq, % de ahorro frente a no actuar, **horas de espera**, aplazamientos por día (carga para la
    persona, como los avisos/día de Guardian).
  - Cada cifra de mayo va con su par de enero a abril, dentro de muestra (espíritu de §4.2).
  - Diferencia entre π\* y la regla fija con **bootstrap pareado por día** (2.000 réplicas, semilla 42); «no se distingue»
    si el IC incluye 0 (§4.6).
- **Sensibilidad λ × r**: fracción de estados que aplazan y ahorro en mayo.
- **Límites que se declaran:**
  - El ahorro es simulado.
  - ΔE y f son supuestos.
  - La demanda se supone independiente de la acción.
  - En mayo baja la carga alta (22,7 % → 11,5 % de los días, C2-T2).
  - Sin acción térmica.
- **Cierre Shiro.** Qué estado y qué λ usará Q-learning, si la carga pendiente se queda en el estado y qué hace el agente
  en estados con pocas visitas.

## 6. Entregables

```
3er_Corte_Nov/Taller_1_RL_MDP/
├─ Documentacion/                         (material del profesor, ya guardado)
├─ PLAN_TALLER1_C3.md                     (este plan)
├─ Taller1_C3_MDP_Shiro.ipynb             (Parte 2 + cálculos de la Parte 3; corre de principio a fin)
├─ Taller1_C3_Diseno_MDP_RESUELTO.docx/.pdf  (Parte 1 + análisis de la Parte 3, apertura Shiro, estilo de los talleres)
├─ Taller1_C3_presentacion.pptx/.pdf      (≈ 10 diapositivas, formato del «Ejemplo MDP»; opcional por el plazo)
├─ politica_optima_shiro.csv · figuras/ (R1…R7) · cifras.json
└─ generadores/  construir_cuaderno.py · generar_documento.py · generar_presentacion.py · verificar.py
```

`verificar.py` comprueba que cada cifra del docx y del pptx salga de `cifras.json` y que el cuaderno no tenga errores. **Debe
terminar con código 0 antes de subir.**

## 7. Orden de trabajo para hoy

1. Generador del cuaderno y primera ejecución, con la prueba de cordura r = 1 → no aplazar (≈ 1 h).
2. Figuras R1–R7 y `cifras.json`; buscar las reglas de oro (≈ 45 min).
3. Documento de diseño (docx → PDF por Word para revisarlo) (≈ 1 h).
4. Presentación corta (≈ 45 min, si da el tiempo).
5. `verificar.py`, revisión de los PDF, actualizar `CLAUDE.md` y hacer commit.
6. **Pipe (Andrés) sube los archivos a Classroom.**

## 8. Decisiones abiertas (con el valor por defecto que se usará si no se dice otra cosa)

| Decisión | Por defecto |
|---|---|
| Paso de decisión | 1 hora |
| Acciones | {No actuar, Aplazar, Ejecutar}; sin acción térmica |
| Tarifa punta / valle | r = 1,5 (sensibilidad 1,0–2,0) |
| Fracción desplazable | f = 0,40 (hallazgo 31) |
| λ | barrido; por defecto el centro de la rejilla (0,005), declarado como supuesto |
| Formato | docx + ipynb + presentación corta |

## 9. Riesgos

- **π\* = codiciosa o «no aplazar nunca»** con los valores por defecto. Se reporta tal cual: es un resultado para Shiro
  («con esta tarifa, aplazar no compensa la espera»), y la sensibilidad muestra dónde cambia.
- **Estados con pocas visitas** (mínimo 4). Se marcan en la tabla de cobertura; en la evaluación, el estado sin datos usa
  «no actuar».
- **El evaluador espera clústers como estados.** Se usan (tipo de día de K-Means) y se explica por qué solos no bastan:
  con 2 clústers, la decisión no vería la hora ni la demanda.
