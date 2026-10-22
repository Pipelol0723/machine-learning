> **Versión anterior (v2), más detallada.** Se conserva porque el plan vigente (`../PLAN_DESARROLLO.md`) comprimió aquí detalles que se usan al implementar: formato APA fino, arquitectura de la Parte 3, árbol de carpetas y nombres de archivo, lista completa de "no se propaga", tabla de indicios con horario solo y ≥ 30 min. **Donde discrepe, manda `PLAN_DESARROLLO.md`** (p. ej. G0 como modelo entrenado, N2 sí por defecto, una sola señal de color en el mockup, titular ≈ 3 de cada 10).

# Plan de desarrollo — Parcial 2 (2.º corte, Aprendizaje Supervisado)
# Shiro Guardian: ¿cuánto antes se puede avisar de un pico de consumo?

> Reemplaza el plan de taquilla de cine (TMDB), que no correspondía a este proyecto. **Borrador v2 para aprobación:** no
> se escribe ni se ejecuta código hasta H0. **Fuentes:** CM = `CLAUDE.md` (§) · N = `Parcial_Corte1.ipynb` (celda) · B =
> `Taller1_Boosting.ipynb` · D = `Taller4_DBSCAN.ipynb` · INV = inventario de activos · AE = análisis del enunciado ·
> P05 = `05_Propuesta_Proyecto_Shiro_Twin.docx`. **[chequeo de solo lectura, no reproducido]** = cálculo con pandas sobre
> el CSV hecho al planear, sin entrenar modelos (lo reproduce N1) · **[por calcular]** = lo produce el cuaderno · *decisión* = fijado de antemano.

## 0. Resumen ejecutivo
- **Qué se entrega:** cuaderno `Parcial2_Guardian.ipynb` + `cifras.json` (única fuente de cifras) → informe APA (.docx/.pdf),
  mockup HTML de **una página con 4 tarjetas**, presentación de implementación (7 diapositivas) y póster A1.
- **Necesidad de Shiro que lo abre:** el semáforo de **Shiro Guardian** debe avisar *antes* del pico. Con un medidor en
  tiempo real, reconocer un pico en curso (lo que mide el 86,9 % del parcial 1, N c.38) no añade nada: el medidor ya lo sabe.
- **Qué ya sabemos sin entrenar nada [chequeo de solo lectura, no reproducido]:** con el semáforo en rojo el 7,7 % del tiempo en calma, la mejor regla
  simple (nivel actual + horario) avisa con ≥ 20 min de 27 de los 84 picos del mes nunca visto (32,1 %, IC 95 % 24–41);
  repetir la última lectura le gana al gemelo en error típico y pierde en los picos.
- **Qué se calcula nuevo:** N1 (núcleo, bajo riesgo, solo modelos existentes): anclas, persistencia, latencia del detector
  del parcial 1 y anticipación de los modelos existentes frente a las reglas al mismo tiempo en rojo, explicador y
  energía. N2 (**mejora condicionada**): un clasificador entrenado para anticipar, solo si el usuario lo aprueba en H2.
- **Relato invariante:** título en pregunta, frases por caso escritas aquí y un **modelo supervisado elegido** siempre (§3.4).
- **Qué pido:** aprobar el plan y las 7 decisiones de abajo (cada una dice qué hito bloquea); en H2, decidir N2 con N1.

## 1. Decisiones que pido aprobar
| # | Decisión | Recomendación | Alternativa | Bloquea |
|---|---|---|---|---|
| D1 | Componente que abre el trabajo | Semáforo anticipado de Guardian (§2) | Simulador con incertidumbre por franja × tipo de día | H1 |
| D2 | Reencuadre honesto del parcial 1 | "Reconocer en curso ≠ avisar antes"; F1 0,47 a 0,40 (N c.38); el 0,40 se eligió en prueba (N c.38–40) | Mantener el detector y su relato tal cual | H5 (relato) |
| D3 | Presupuesto de rojo | 7,7 % de las lecturas en calma = tasa base de la etiqueta en entrenamiento [chequeo de solo lectura, no reproducido]; amarillo, otro 7,7 % | 5 % / 10 % (se reportan como sensibilidad) | H1 |
| D4 | Mockup | HTML autocontenido, 1 página, 4 tarjetas, ~300 líneas (§7) | ipywidgets o Streamlit (no instalados, INV §7) | H4 |
| D5 | N2 (clasificador de anticipación) | Mejora condicionada; se decide en H2 con las cifras de N1 | Meterlo en el núcleo | H3 |
| D6 | Tarifa | Campo vacío por defecto: el informe da kWh; $ solo con tarifa que el grupo aporte y cite | Tarifa colombiana citada | solo cifras en $ |
| D7 | Póster y presentación | A1 vertical (PDF + PNG); 7 diapositivas (mínimo 6) | Otro tamaño; 10 diapositivas | ninguno |

## 2. La necesidad de Shiro que abre el trabajo
**2.1 Componente.** Shiro Guardian, "capa de clasificación de riesgo y notificación proactiva sobre los mismos modelos ya
entrenados" (P05 §13; CM hallazgo 25): el **semáforo de la próxima media hora** y la **propuesta con aprobación**
(`ApprovalGate`, ADR 0022; eventos `iot:anomaly-detected` / `iot:action-suggested`, doc 03). Es lo que premia el enunciado:
"a tiempo", alertas con acción, semáforo y KPI (AE §1.1). P05 lo deja como objetivo opcional fuera del alcance evaluable;
el parcial no cambia eso: usa los modelos ya entrenados (N1) y no desplaza el MDP ni el Q-learning (3.er corte).

**2.2 Por qué ahora.** (a) El detector vigente (RF + retardos, etiqueta "la lectura actual supera 200 Wh") cuenta un pico
como detectado si *cualquier* aviso lo toca (N c.38): mide cuánto reproduce al medidor, no cuánto antes avisa. (b) Su
umbral 0,40 se eligió barriendo el mes de prueba (N c.38, justificado en c.40), contra CM §4.3. (c) "A tiempo" no está
medido en ningún cuaderno (INV §6.1). (d) Solo un aviso anticipado deja ventana a la acción "diferir" del MDP (P05).

**2.3 Decisión de arquitectura que depende del resultado** (partición temporal, por episodio, **mismo tiempo en rojo**,
≥ 20 min de antelación; comparación con la **mejor regla simple en validación**, bootstrap pareado por día):

| Caso | Criterio (modelo elegido vs mejor regla, en prueba) | Qué cambia en Shiro |
|---|---|---|
| **A** | ≥ +10 puntos, IC 95 % pareado > 0 y sobre el piso | Guardian es proactivo: P(pico en 30 min) entra al estado del MDP y dispara las propuestas de `ApprovalGate` |
| **B** | cualquier otro resultado sobre el piso (diferencia < 10 puntos o IC que incluye 0) | El modelo entra al estado con su probabilidad graduada; con estos datos no se justifica uno más complejo; se revalida con UCI #235 |
| **C** | ≤ −10 puntos con IC < 0, o bajo el piso | El rojo anticipado usa la regla (declarada como regla); el esfuerzo supervisado va al gemelo; "diferir" solo se evalúa en picos anticipados |

**Piso absoluto de utilidad (*decisión*):** ≥ 25 % de los picos con ≥ 20 min y ≥ 33 % de avisos útiles ("1 de cada 4
picos con margen; 1 de cada 3 rojos precede un pico"). Una señal bajo el piso no se despliega; si ninguna lo alcanza,
Guardian queda reactivo (rojo en curso) + pronóstico del gemelo, y se dice que avisar con 20 min es difícil con estos
sensores (la variable que falta es el aparato, CM hallazgo 4). Margen de 10 puntos: con 84 picos el IC de una sola regla
mide ±8–9 puntos y el de una diferencia pareada entre puntajes parecidos ±5 [chequeo de solo lectura, no reproducido].

**2.4 No se reabre:** gemelo = lineal + retardos (CM §6; hallazgos 11, 12, 19) · el boosting no reemplaza nada (hallazgo
19) · K-Means asigna el tipo de día y el jerárquico audita (hallazgo 23) · CM §4: umbral 200 Wh (p90 del entrenamiento
aleatorio, se fija con `assert`), `random_state=42`, episodios `gap=3`, igual tiempo en alerta, duración media del aviso,
15 % final cronológico como validación, retardos solo en la partición temporal, que es la que decide.

## 3. Qué se reutiliza, qué ya se sabe y qué se calcula
**3.1 Se reutiliza (salidas guardadas, verificadas)**
| Activo | Cifra | Fuente |
|---|---|---|
| Partición temporal con retardos | 15.783 / 3.946 filas, 36 variables; entrena hasta 30-abr 08:20, prueba desde 08:30 | B c.3; fechas [chequeo de solo lectura, no reproducido] |
| Picos del mes de prueba | 84 episodios en 27,4 días (3,1/día); 8,2 % de lecturas altas | N c.38; B c.22 |
| Detector del parcial 1 a 0,40 | 86,9 % de picos tocados · 3,03 avisos/día · 37,3 % falsos · F1 por lectura 0,47 · 21,1 % del tiempo en alerta · 100,5 min | N c.38; B c.22 |
| Logística + retardos (misma etiqueta) | a 0,20: 70,2 % · 2,70 avisos/día · 32,4 % falsos | N c.38 |
| Gemelo lineal + retardos (36 var.) | R² 0,557 · MAE 28,17 Wh · RMSE 60,54 Wh · sesgo +0,457 Wh; media: MAE 52,65 · RMSE 90,96 | N c.25 |
| Gemelo de 6 variables | R² 0,5358 · MAE 28,85 Wh; intercepto 49,1819; coeficientes de CM hallazgo 17 | N c.33 |
| Deriva mensual | p90 250 / 230 / 180 / 190 / 150 Wh; lecturas altas 11,50 % → 7,63 % | N c.29 (`P3_deriva`) |
| Código de evaluación | `episodios`, `evaluar_alertas`, `con_presupuesto` | B c.17 |

**3.2 Lo que ya se sabe [chequeo de solo lectura, no reproducido] — 84 picos; presupuesto 7,66 % de lecturas en calma en rojo (≈ 10 lecturas ≈ 100 min/día)**
| Señal (mismo tiempo en rojo en prueba) | ≥ 10 min | ≥ 20 min (IC 95 %) | ≥ 30 min | Avisos/día | Útiles | Acierto del rojo |
|---|---|---|---|---|---|---|
| Horario (frecuencia por hora × laborable/fin de semana) | 25,0 % | 23,8 % (15–34) | 22,6 % | 1,97 | 37,0 % | 19,5 % |
| Nivel (consumo actual) | 39,3 % | 22,6 % (14–31) | 20,2 % | 3,58 | 32,7 % | 18,4 % |
| **Nivel + horario** (suma de percentiles, sin entrenar) | 36,9 % | **32,1 % (24–41)** | 28,6 % | 2,56 | 41,4 % | 23,8 % |
| Gemelo de 6 variables como puntaje (coeficientes de N c.33) | 39,3 % | 22,6 % (15–30) | 22,6 % | 3,87 | 27,4 % | 19,9 % |

Otros [chequeo de solo lectura, no reproducido]: validación = 2.368 lecturas (13-abr 21:50 → 30-abr 08:20), 51 picos · tasa base de la etiqueta en
calma: 7,66 % entrenamiento, 6,91 % prueba · 59 % de los picos arranca desde ≤ 100 Wh (inicios abruptos) · el primer pico
de prueba ya estaba en curso (empezó a las 08:10, en entrenamiento): techo 83/84 · gemelo vs nivel, IC pareado (−5; 5);
nivel vs horario (−14; 11) · con cortes de validación, el rojo realizado en prueba de las cuatro señales va de 6,7 % a 11,0 %
(deriva) · el gemelo de 6 variables reproduce MAE 28,851 (ancla) y su pronóstico supera 200 Wh en el 0,03 % de las
lecturas en calma · persistencia: MAE 26,64 / RMSE 66,44 Wh (gemelo: +5,7 % de MAE, −8,9 % de RMSE) · energía del mes:
380,0 kWh, 115,7 kWh dentro de picos, 50,9 kWh por encima de 200 Wh; picos de 20 min de mediana (40,6 de media).
**Lectura:** el gemelo como puntaje no le gana a la regla de nivel (es casi `lag1`); el listón real es nivel + horario.

**3.3 Cálculos nuevos**
**N1 — Núcleo** (solo modelos existentes, deterministas con semilla 42; entra el 100 %)
| Cálculo | Qué | Hipótesis | Salida / éxito | Qué cambia en Shiro | Nota que mejora |
|---|---|---|---|---|---|
| N1a Anclas | `assert` de N c.25 (0,557 / 28,17 / 60,54), N c.38 (84 / 27,4 / 86,9 / 3,03 / 37,3 / 0,47), B c.22 (21,1 % / 100,5 min), N c.33 (28,85) | el entorno reproduce | todas pasan; si una falla, el cuaderno se detiene | ninguna cifra desalineada entre piezas | todas |
| N1b Persistencia | MAE y RMSE del gemelo frente a repetir la última lectura, total y por franja | empata en MAE y gana en picos [chequeo de solo lectura, no reproducido] | cifras con su signo | el valor del gemelo es condicionar por hora, luz, clima y acción, no el paso a paso; su error se medirá a varios pasos (3.er corte) | KPI de pronóstico; póster |
| N1c Latencia del parcial 1 | detector a 0,40 como en N c.38: primer aviso antes / en el inicio / después / nunca; % de la energía del pico aún por delante | casi siempre en el inicio o después | distribución | corrige el "a tiempo" del parcial 1 (D2) | limitaciones; Apéndice A |
| N1d Anticipación | G1 RF + retardos, G2 logística + retardos, G3 gemelo de 36 variables, aplicados un paso adelante (en *t* ven la lectura actual como `lag1`), frente a horario, nivel y nivel + horario; presupuesto D3; elección en validación (§3.4); una evaluación en prueba; bootstrap pareado por día (2.000 réplicas) | entrenados para reconocer, anticipan como la regla de nivel | caso A/B/C (§2.3) | si Guardian ya tiene un anticipador supervisado o necesita N2 | escenario, semáforo; datos del mockup |
| N1e Explicador | `DecisionTreeClassifier(max_depth=3)` que imita el rojo del elegido en `fit`; fidelidad en prueba [por calcular]; si el elegido es el gemelo, coeficiente × valor | 3 niveles reproducen la mayor parte del rojo | Tabla 2 y G4 regla → acción (con su fidelidad declarada) | capa de explicación de los avisos | ítem "reglas o patrones" |
| N1f Energía y casos | kWh del mes; exceso > 200 Wh en picos anticipados; caso 1 = pico no anticipado con más energía; caso 2 = aviso falso más largo (reglas, no elección a mano) | — | cifras y G5 | qué parte del exceso alcanza "diferir" | KPI; ética; póster |

**N2 — Mejora condicionada** (se ejecuta solo si en H2 el usuario la aprueba; recomendada si N1 cae en B o C).
- G4 RF (200 árboles) y G5 logística con etiqueta "algún pico empieza en los próximos 30 min" (lecturas en calma),
  entradas = 29 variables + ventana de la última hora **incluida la lectura actual** (7 variables); purga de 3 lecturas
  en las fronteras fit/validación/prueba.
- *Hipótesis:* entrenar para el objetivo combina nivel, subida de la última hora, hora y `lights` (proxy de ocupación,
  hallazgo 1) y supera a nivel + horario por ≥ 10 puntos. *Éxito:* caso A. *Reemplaza al elegido de N1* si lo supera
  en validación por ≥ 5 puntos. *Shiro:* P(pico en 30 min) entra al estado del MDP. *Nota:* Parte 1 y póster (un paso
  más en la evolución). Coste: ~80 líneas, ~1 min de cómputo.

**3.4 Modelo supervisado elegido en todos los casos (regla de selección fijada hoy)**
- **Siempre:** el **gemelo lineal + retardos** (función de transición; tarjeta "¿Y si…?" con su versión de 6 variables).
- **Clasificador de Guardian:** el candidato (G1–G3, o G4–G5 si hubo N2) con mayor % de picos con ≥ 20 min **en
  validación**; si otro queda a ≤ 5 puntos y es exportable (G2, G3, G5), gana el exportable: corre en el navegador y se
  explica con coeficientes. Las reglas nunca son candidatas: son el listón.
- **Cómo se cuenta:** A: "el modelo avisa de X picos más por cada 100 que la mejor regla". B: "el modelo iguala a la mejor
  regla (no distinguible con 84 picos) y la generaliza: da una probabilidad graduada que el semáforo y el MDP usan".
  C: "el clasificador no supera a la regla; Guardian la usa mientras tanto y el modelo que el sistema usa es el gemelo".
  La sección "Modelo elegido" presenta siempre las dos familias (CM hallazgo 5); solo cambia una frase.

**3.5 Fuera de este parcial:** banda de incertidumbre por franja, variante sin temperaturas, gris por deriva de
entradas, tipo de día como contexto, DBSCAN como segunda alarma, UCI #235, MDP y Q-learning (3.er corte).

**3.6 No se propaga:** "F1 0,580 a 0,40" (CM §6; es 0,47, N c.38; el 0,580 es a 0,5, N c.22) · del mockup del parcial 1
(INV §3): `prob()` (rampa, no el RF), "27-may 19:40" (el dataset termina el 27-may 18:00), "27-may 07:20, 800 Wh" (es
60 Wh), "≈ 0,9 kWh", MAE por franja del RF aleatorio mostrado como del lineal · K-Means k = 3 como "carga alta partida en
dos" (CM §10) · "18 sensores interiores" (T6/RH_6 miden fuera) · "la factura llega 20–50 días después" (N c.40, sin
fuente) · la ruta `hora > 7,5 → hora ≤ 20,5 → lights > 5,0` como explicación de avisos: sale de un **árbol regresor de
consumo, partición aleatoria** (N c.7, c.35); solo puede ilustrar ese árbol · `*_presentacion_ampliada.pptx`.

## 4. Definiciones operativas (fijadas antes de calcular)
| Término | Definición |
|---|---|
| Lectura alta / pico | `Appliances` > 200 Wh; pico = lecturas altas separadas por < 30 min (`gap=3`); inicio *s* = primera lectura alta |
| En calma | lectura fuera del tramo [*s*, fin] de todo pico. "Rojo en curso" = dentro de ese tramo (medidor, sin ML) |
| Etiqueta de anticipación | lectura en calma en [*s*−3, *s*−1] de algún pico (un pico empieza en los próximos 30 min) |
| Antelación | 10 × (*s* − primera lectura en rojo de esa ventana) min. Cada lectura resume 10 min: el margen real hasta el arranque está entre la antelación − 10 y la antelación |
| Tiempo útil | **≥ 20 min nominales** (≥ 10 min reales): ver el aviso, aprobar y no encender la carga; la propuesta vence a los 30 min. Se reportan ≥ 10, ≥ 20 y ≥ 30; el titular usa ≥ 20 |
| Aviso | lecturas en rojo anticipado agrupadas con `gap=3`; **útil** si toca [*s*−3, *s*−1] de algún pico; si no, falso. Duración media en min |
| Presupuesto | % de lecturas en calma en rojo anticipado (D3). Fuera de verde = amarillo + rojo anticipado; el rojo en curso se reporta aparte |
| Acierto de un color | % de lecturas en calma de ese color con etiqueta 1 (tasa base en prueba 6,91 % [chequeo de solo lectura, no reproducido]) |
| Mismo tiempo en rojo | cada señal marca el top-*r* % de su puntaje en calma (`con_presupuesto`, B c.17): sirve para comparar, no para desplegar |
| Particiones | solo temporal (con retardos la aleatoria filtra, CM §4.4); prueba = exactamente las 3.946 filas de N c.38 (84 picos); `fit` = 85 % inicial del entrenamiento, validación = 15 % final. Las cifras históricas aleatorias van siempre con su par temporal (CM §4.2), solo en póster y cuaderno |

## 5. Semáforo
**5.1 Unidad:** la próxima media hora del hogar, recalculada cada 10 min (lo que agrupa un pico, el tiempo para diferir
una carga y la vigencia de una propuesta). El F1 por lectura no mide lo que la persona vive (CM §4.4).

**5.2 Niveles y acción ("Shiro propone, la persona aprueba")**
| Estado | Condición | Lo que ve la persona | Lo que hace Shiro |
|---|---|---|---|
| Verde | en calma, puntaje < corte amarillo | panel verde | registra, no molesta |
| Amarillo | en calma, entre cortes | panel ámbar con la regla del explicador (N1e) | sugiere revisar antes de encender cargas grandes; sin notificación |
| Rojo anticipado | en calma, puntaje ≥ corte rojo | notificación + propuesta | `ApprovalGate`: aprobar / ajustar / rechazar; vence en 30 min; nada se ejecuta sin aprobación (en Twin, ninguna acción física) |
| Rojo en curso | lectura > 200 Wh o dentro del tramo de un pico | "pico en curso" | no repite la notificación si ya avisó |
| Gris | > 30 días desde la última calibración (regla de N c.37; aquí, 30-abr 08:20) | colores con "baja confianza" | no propone; pide recalibración. En el mes de prueba no se activa (27,4 días) y se dice; el modelo usa datos hasta el 13-abr (§5.3) |

**5.3 Calibración sin circularidad.** Cortes = cuantiles del puntaje en las lecturas en calma de **validación** al
presupuesto D3 (rojo: top 7,66 %; amarillo: siguiente 7,66 %). El modelo que se evalúa en prueba es **el mismo** que se
entrenó en `fit` (sin reentrenar con el 100 %: así no se mueve la escala de P). En prueba se *reportan* el tiempo realizado
en cada color frente al presupuesto y el acierto por color; si se apartan, es deriva (CM hallazgo 13). El 21,1 % y el
0,40 del parcial 1 no se usan como objetivo: solo aparecen en el Apéndice, con su advertencia.

**5.4 Scorecard del sistema** (equipo Shiro, Parte 3): % de picos con ≥ 20 min, % de avisos útiles, tiempo en rojo
realizado / presupuesto, días desde el reentrenamiento y p90 del mes frente a 200 Wh (deriva, N c.29); verde si está
dentro de ±25 % del valor de validación, amarillo hasta ±50 %, rojo fuera (*decisión*).

## 6. Traducción a lenguaje de negocio sin mentir
**6.1 Dónde va cada cosa**
| Contenido | Cuerpo del informe | Apéndice | Póster | Cuaderno |
|---|---|---|---|---|
| Escenario, antes/después, semáforo, reglas → acción, KPI | sí, interpretado | — | sí | sí |
| Modelo elegido vs mejor regla | en picos avisados de 84 y avisos/día | ficha | sí | sí |
| MAE / RMSE | en Wh, frente a "repetir la última lectura" | ficha | sí | sí |
| F1, accuracy, R², AUC | **no** | solo del modelo elegido y su línea base | F1 y accuracy con línea base (lo pide el enunciado) | sí |
| Evolución de modelos | narrada como decisiones (Tabla 1, sin métricas lado a lado) | **no** | tabla en pares aleatoria/temporal | sí |

**6.2 Frases plantilla** (los `{…}` salen de `cifras.json`; una variante por caso, escritas hoy)
- *Escenario (forma única):* "Si Shiro Guardian hubiera funcionado durante el mes que el modelo nunca vio (30-abr a
  27-may de 2016), con el semáforo en rojo unos {min_dia} minutos al día, habría avisado con 20 minutos o más de
  antelación {n20} de los 84 picos; la mejor regla simple, con el mismo tiempo en rojo, {m20}." + A: "Son {d} picos más
  por cada 100." / B: "Con 84 picos la diferencia no se distingue del azar: el modelo iguala a la regla y además gradúa
  el riesgo." / C: "La regla avisa de más picos; Guardian la usa mientras un modelo no la supere."
- *Antes / después:* "Antes: el hogar se entera por la factura o, con un medidor, cuando el pico ya empezó. Después: a
  las {hh:mm} el semáforo pasó a rojo, {k} min antes del pico de las {hh:mm}, y Shiro propuso no encender cargas grandes;
  la persona decide." Día elegido por regla: el día mediano en picos anticipados entre los que tienen ≥ 3 picos. No se
  dibuja una curva de consumo "con Shiro": no hay modelo del efecto de la acción.
- *Pronóstico:* "El gemelo se equivoca {mae} Wh por lectura frente a {mae_p} Wh de repetir la última lectura, y en los
  picos {rmse_dif}" (texto según el signo de N1b). Nunca "−46,5 % frente a la media": exagera el aporte.
- *Conclusión (una por caso):* A "Guardian puede ser proactivo: el aviso anticipado entra al estado del MDP." · B "Avisar
  con margen es posible en {p20} de los picos sin un modelo complejo; Shiro usa el más simple que lo logra." · C "Con
  estos sensores anticipar es difícil; la mejora está en saber qué aparato se enciende, no en el algoritmo."
- *Analogías:* bosque = comité de 200 árboles que votan; gemelo = "parte de lo gastado hace 10 min y lo corrige por hora,
  luz y clima"; validación temporal = "examen con un mes que nunca vio"; presupuesto = "cuánto se tolera que el semáforo moleste".

**6.3 KPI: medidos y simulados, nunca mezclados.** *Medidos:* % de picos con ≥ 20 min, avisos/día, % útiles, min/día
fuera de verde, error del pronóstico frente a la persistencia, kWh del exceso > 200 Wh en picos anticipados (de 50,9 kWh
en el mes [chequeo de solo lectura, no reproducido]). *Simulados:* kWh evitables = exceso anticipado × % evitable × % de propuestas aceptadas; $ = kWh ×
tarifa (D6). Rótulo **SIMULADO**, tabla de supuestos y una tabla de 3 filas (bajo / medio / alto). Con tarifa plana,
diferir no ahorra dinero: solo lo evitable.

**6.4 Prohibido en el cuerpo:** comparativas "A 0,81 vs B 0,79" · R² como "precisión" · cifras aleatorias solas · "a
tiempo" sin antelación · cifras de sector sin cita · "ahorro" sin supuestos · causalidad desde importancias (CM §8).

## 7. Mockup mínimo (Parte 2, 2,5)
**7.1 Opción: un HTML único autocontenido** (HTML + CSS + JS, sin librerías ni red, fuentes del sistema). Es lo mínimo
que sigue siendo funcional: no hay que instalar nada (Streamlit e ipywidgets no están, INV §7), abre con doble clic sin
red, ya existe la estética y el gemelo de 6 variables ya corre en JS (INV §3), y reproduce la arquitectura real (modelos
en Python, interfaz que consume sus salidas). Una página, 4 tarjetas, ≤ ~300 líneas de plantilla.

| Tarjeta | Entrada | En vivo (en el navegador) | Precalculado (lo incrusta el cuaderno) |
|---|---|---|---|
| **1 ¿Y si…?** (nunca se recorta) | hora, `lights`, T2, RH_2, T_out, consumo actual; o "cargar un momento real" (5 momentos) | **Modelo real:** lineal de 6 variables (objetivo `Appliances` siguiente; partición temporal con retardos, entrenado hasta 30-abr 08:20; N c.33) → Wh en 10 min; aporte de cada entrada (coef. × valor); color con sus cortes de validación (rojo ≥ 117,0 / amarillo ≥ 103,7 Wh [chequeo de solo lectura, no reproducido]; ese modelo vio la validación al entrenar, se declara); acción sugerida; "qué tendría que cambiar para salir del rojo" | coeficientes (N c.33), cortes del gemelo, 5 momentos reales |
| **2 Semáforo del mes** | deslizadores de presupuesto rojo y amarillo; selector de día | cortes = cuantiles de los puntajes de validación; colores de las 3.946 lecturas con la señal que maneja el semáforo (§3.4); agrupación de avisos (`gap=3`); % de picos con ≥ 10/20/30 min, avisos/día, % útiles, duración, rojo realizado, acierto por color; **lo mismo para la mejor regla** al mismo presupuesto; tira del día elegido "solo medidor / con Guardian" | serie real (Wh), puntaje del clasificador elegido y de la regla en prueba y validación |
| **3 Impacto simulado** | tarifa (vacía por defecto), % evitable, % de aceptación | kWh y $ = exceso > 200 Wh de los picos anticipados con los cortes vigentes × supuestos; rótulo SIMULADO; aviso de tarifa plana | energía por lectura (ya en la serie) |
| **4 Propuestas** | aprobar / ajustar / rechazar | estado y bitácora | 4 avisos reales del mes: hora, regla del explicador (N1e), desenlace (pico a los X min / falso) |

**Funcional verificable (v1):** (1) abre sin red y sin errores de consola; (2) el cuaderno incrusta valores esperados
(métricas de la tarjeta 2 al presupuesto por defecto y el gemelo en 3 filas) y el JS los compara al cargar y escribe
"Verificación: OK / DIFIERE" en el pie, que se lee con `msedge --headless --dump-dom`; (3) subir el presupuesto rojo sube
la anticipación y los avisos/día (dos capturas); (4) ningún número de resultado escrito en la plantilla: todo viene del
JSON. **Construcción:** la última celda del cuaderno hace `plantilla.replace('/*__DATOS__*/', json)` y escribe
`Mockup_Shiro_Guardian.html` (sin script aparte). **Capturas:** Edge headless a 2× (`--force-device-scale-factor=2`) de
la página y de cada tarjeta con `#t1…#t4` (el ancla muestra solo esa tarjeta, ~5 líneas de JS) → `figuras/MG1–MG5`.
**Extensión E1** (si el clasificador elegido es exportable): la tarjeta 1 calcula también P(pico en 30 min) en vivo.
**Orden de recorte:** tarjeta 4 → tarjeta 3 (pasa a una línea de la 2) → tira del día → E1. **Nunca** la tarjeta 1.

## 8. Informe ejecutivo APA (Parte 1, 1,0)
**8.1 Formato APA 7** (trabajo de estudiante): portada (título en negrita centrado; Jose Leonardo Diazgranados, Sofía
Londoño, Andrés Felipe Céspedes Rondón, Alex Duran; Universidad Sergio Arboleda; Aprendizaje de Máquina; Hernán Darío Cruz
Bueno; fecha) · Calibri 11 (la de la casa; APA 7 la admite), doble espacio, márgenes 2,54 cm, número de página arriba a la
derecha, sangría 1,27 cm · estilos reales `Heading 1–3` con formato APA (1 centrado negrita; 2 izquierda negrita; 3
negrita cursiva) · **Tabla n / Figura n** en negrita arriba, título en cursiva, nota debajo; tablas sin bordes verticales
ni rellenos · citas autor-año y referencias con sangría francesa: Candanedo, Feldheim y Deramaix (2017, *Energy and
Buildings*); conjunto UCI n.º 374; Breiman (2001); Pedregosa et al. (2011); APA (2020); Ley 1581 de 2012; DOI y páginas
se verifican antes de citar. Cifras de sector solo con fuente verificable; si no hay, el problema se plantea con los datos
del propio hogar y Candanedo et al. (2017). **Convivencia con la casa:** tablas APA en blanco y negro; los colores de la
casa solo en figuras, donde verde / naranja / rojo son el semáforo. Base: plantilla python-docx con estilos ajustados y
XML para el campo de página; revisión visual en PDF (Word COM).

**8.2 Extensión:** 9 páginas de cuerpo (núcleo: 8) + portada + resumen + referencias + Apéndice A (ficha técnica, 1–2)
+ Apéndice B (glosario, 1). Sin Parte 3 dentro (el ejemplo de cine se fue a 34 páginas, AE §3.1).

**8.3 Estructura** (seis viñetas del enunciado con la plantilla de apertura de CM §0)
| Sección | Contenido | Págs. | Figuras / tablas |
|---|---|---|---|
| Resumen | pregunta de Guardian, respuesta (frase del caso), 3–4 cifras del mes nunca visto, decisión para Shiro | 1 | — |
| 1 Problema real del sector | el hogar no sabe que viene un pico; Guardian debe avisar antes; qué decisión de arquitectura depende del resultado (§2.3) | 1 | Fig. 1 un día del mes: medidor y semáforo (G1) |
| 2 Modelo elegido y justificación | dataset y calidad en un párrafo; las dos familias con analogía; validación temporal; listón = mejor regla; por qué no los otros, como decisiones | 1,5 | Tabla 1 línea de tiempo de decisiones |
| 3 Resultados clave | 3.1 escenario · 3.2 antes/después · 3.3 reglas → acción (explicador) · 3.4 semáforo y scorecard · 3.5 impacto medido vs simulado | 3,5 | Fig. 2 anticipación ≥ 10/20/30 min, modelo vs mejor regla con IC (G2) · Fig. 3 tiempo y acierto por color (G3) · Fig. 4 reglas → acción (G4) · Fig. 5 captura del mockup (MG1) · Tabla 2 regla → acción · Tabla 3 supuestos |
| 4 Conclusiones y decisiones | por actor: hogar, equipo Shiro, diseño de Shiro (estado del MDP, "diferir", reentrenamiento mensual) | 1 | — |
| 5 Limitaciones y ética | una vivienda belga sin verano; deriva; 84 picos; latencia del parcial 1; quién paga cada error y su mitigación; privacidad (el consumo revela ocupación, hallazgo 1; Ley 1581); Shiro propone, la persona aprueba; 2 casos críticos | 1,5 | Fig. 6 deriva (`P3_deriva`, N c.29) · Fig. 7 casos críticos (G5) · Tabla 4 error → quién paga → mitigación |
| 6 Recomendaciones | 5 accionables con su porqué | 0,5 | — |

## 9. Presentación de implementación (Parte 3, 0,5) — Shiro como producto propio
7 diapositivas con notas del orador (13,33 × 7,5 in, estética del deck del C2, INV §5); python-pptx y PDF por PowerPoint.
1 Portada · 2 Guardian como producto y arquitectura: medidor y sensores → `iot-bridge` (`IDeviceModule`, `DeviceRegistry`,
ADR 0003; `InProcessTransport` → `MQTTTransport` / Home Assistant) → servicio Python de modelos → semáforo + `ApprovalGate`
(ADR 0022) → app; qué promete y qué no (no actúa sin aprobación, no ahorra solo) · 3 Datos y privacidad: lectura cada 10
min, ventana de 1 h en memoria, procesamiento local; solo salen indicadores agregados con consentimiento · 4 Roles (RACI):
titular que aprueba, convivientes; equipo Shiro: ciencia de datos (reentrenamiento y recalibración mensual, auditoría
jerárquica, hallazgo 23), plataforma, soporte, privacidad · 5 Ciclo mensual y hogar nuevo: reentrenar, recalibrar cortes,
revisar el scorecard (§5.4); primer mes en "modo aprendizaje" (gris, sin notificaciones), modelo de una sola vivienda
(CM §3) · 6 Capacitación: recorrido por las 4 tarjetas, guía de una página del semáforo, video corto, preguntas
frecuentes; éxito = % de propuestas respondidas y de ajustes del presupuesto · 7 Piloto y riesgos: fases Twin → Guardian
→ Home (doc 03), sin fechas, criterios de salida. *Mínimo:* 6 (fusiona 2 y 3).

## 10. Póster (Parte 4, 1,0)
A1 vertical (594 × 841 mm), una diapositiva python-pptx (editable por el grupo) → PDF por PowerPoint + PNG. Fondo claro
con acentos de la consola; cuerpo ≥ 24 pt, títulos ≥ 48 pt, ≤ 500 palabras (*decisiones*). Figuras exportadas **una vez**
a 300 dpi con tamaño de póster; el informe usa las mismas reducidas. Las P* de 120 dpi no se usan grandes (INV §4).
| Sección (orden del enunciado) | Contenido | Figura |
|---|---|---|
| Título + autores + Universidad Sergio Arboleda | "¿Cuánto antes se puede avisar de un pico de consumo? Modelos supervisados para Shiro Guardian" | — |
| Problema y contexto | Guardian debe avisar antes; el medidor ya sabe lo que pasa ahora | G1 |
| Dataset y características | 19.735 lecturas, 29 variables, 137 días, 0 faltantes (CM §3); calidad: una vivienda sin verano, `rv1/rv2` excluidas, `Appliances` 100 % múltiplo de 10 Wh (D c.30), T6/RH_6 exteriores, 2 días incompletos | mini tabla |
| Modelos aplicados y evolución | línea de tiempo T2 → T3 → P1 → C2-T1 → P2 con la decisión de cada hito + tabla en pares (bloque `heredadas`) | G6 |
| Modelo final y resultados | gemelo: MAE y RMSE vs persistencia y media; clasificador: accuracy y F1 vs "todo verde", y picos con ≥ 20 min vs mejor regla | G2, G3 |
| Errores y reflexiones éticas | los 2 casos críticos + riesgos de automatizar mal | G5 |
| Mockup | 2–3 capturas | MG1–MG3 |
| Conclusión y futuro | el criterio de validación pesa más que el algoritmo; medir lo que la persona vive; qué falta (aparato, más hogares) | — |

## 11. Estructura de carpetas
```
2do_Corte_Oct/Parcial_2_Aprendizaje_Supervisado/
├─ Documentacion/                      material del profesor y ejemplos (no se toca)
├─ PLAN_DESARROLLO.md                  este plan
├─ Parcial2_Guardian.ipynb             profundidad 2: "../../data set/energydata_complete.csv" funciona
├─ cifras.json                         única fuente de cifras (bloques "nuevas" y "heredadas")
├─ figuras/                            G1–G6 (300 dpi) · MG1–MG5 (capturas 2×)
├─ mockup/plantilla.html               marcador /*__DATOS__*/
├─ generadores/                        construir_cuaderno · generar_informe · generar_presentacion · generar_poster · verificar (.py)
├─ Mockup_Shiro_Guardian.html          Parte 2 (lo escribe el cuaderno)
├─ Informe_Ejecutivo_Shiro_Guardian.docx/.pdf · Implementacion_Shiro_Guardian.pptx/.pdf · Poster_Shiro_Guardian.pptx/.pdf/.png
```
Cinco generadores (CM §11), cada uno exporta su PDF por COM. Se descartan `notebooks/`, `src/`, `app/`, `data/` del plan
anterior (rompen la ruta relativa, INV §8.3). Al cierre se propone añadir la carpeta a CM §2 (con permiso).

## 12. Hitos (sin fechas), núcleo, recorte y esfuerzo
| Hito | Depende de | Entregable verificable |
|---|---|---|
| H0 Aprobación | — | visto bueno a D1–D7 |
| H1 Cuaderno + N1 + exportación | H0 | corre con nbclient en kernel limpio; anclas OK; `cifras.json`; datos del mockup; G1–G6 |
| H2 Punto de control | H1 | resumen ≤ 15 líneas: caso A/B/C de N1, cifras clave, recomendación sobre N2; el usuario decide N2 |
| H3 N2 (condicional) | H2 = sí | re-ejecución limpia; `cifras.json` y figuras actualizadas; caso final |
| H4 Mockup | H1 (plantilla desde H0; no depende del caso) | §7 "funcional" en verde; MG1–MG5 |
| H5 Informe | H2 o H3, H4 | docx + PDF; `verificar.py` limpio; lista APA |
| H6 Póster | H2 o H3, H4 | pptx + PDF A1 + PNG |
| H7 Presentación | H2 | pptx con notas + PDF |
| H8 Verificación final | H5–H7 | §13 completo; un integrante revisa cada pieza; propuesta de correcciones a CM |

**Núcleo mínimo entregable:** H0–H2 sin N2 · tarjetas 1–3 · informe de 8 páginas · póster · 6 diapositivas · `verificar.py`
v1. **Orden de recorte:** 1) N2 · 2) tarjeta 4 · 3) tarjeta 3 → línea en la 2 · 4) tira del día · 5) presentación a 6 ·
6) sección 4 del informe → un párrafo. **Nunca:** tarjeta 1, anclas, líneas base, partición temporal, `cifras.json`,
chequeo de residuos, limitaciones y ética. **Prioridad por nota:** mockup (2,5) > informe y póster (1,0) > presentación (0,5).

**Esfuerzo estimado:** `construir_cuaderno.py` ≈ 400 líneas (N1 ≈ 220, exportación ≈ 60, figuras ≈ 120); cuaderno ≈ 2–3
min (2 ajustes de RF a ~8–16 s c/u según N c.22 y B c.8; lo demás en segundos), + ≈ 1 min con N2 · plantilla ≈ 300 ·
`generar_informe.py` ≈ 400 · `generar_presentacion.py` y `generar_poster.py` ≈ 200 c/u · `verificar.py` ≈ 80. Ningún
hito depende de cómputo largo; el cuaderno de boosting (1.010 s) no se repite.

## 13. Verificación
1. **Cuaderno:** se genera con `construir_cuaderno.py` y se ejecuta con nbclient en kernel limpio; se registra el tiempo.
2. **Una sola fuente:** `cifras.json` = clave → {valor, texto es-CO, unidad, partición, fuente (sección del cuaderno o
   celda fuente), descripción}. Los generadores solo formatean `{{clave}}` desde ahí; nada se teclea.
3. **Heredadas (regla 7):** el cuaderno lee con `nbformat` las salidas guardadas de N c.7–c.8, c.25, c.29, c.38 y B c.8,
   c.22 con regex fijadas por celda, las guarda en el bloque `heredadas` y las contrasta con `assert` contra CM §6. Si
   difieren, manda la salida guardada y se propone corregir CM.
4. **`verificar.py` v1:** (i) ningún `{{` sin resolver; (ii) ninguna aparición de "[por calcular]", "TODO", "{{", "Claude",
   "Anthropic", "ChatGPT", "IA generativa" en docx (con tablas y encabezados), pptx (con notas) y HTML; (iii) en el cuerpo
   del informe (antes de las referencias) 0 apariciones de "F1", "AUC", "R²", "log-loss", "accuracy", "exactitud";
   (iv) toda clave de partición aleatoria usada tiene su par temporal usado; (v) "a tiempo" y "antes del pico" solo en
   frases con "min". *Extensión:* detector completo de números huérfanos.
5. **Visual:** docx y pptx → PDF; revisión de páginas, lista APA y legibilidad del póster a tamaño real.
6. **Lista del enunciado (AE §6):** 1–2 → §8 · 3–4 → §6.1, `verificar` (iii) · 5–6 → informe 3.1–3.3, tarjeta 1–2,
   Tabla 2 · 7–8 → 3.4–3.5, Tabla 3, §5, tarjetas 2–3 · 9, 16–18, 24 → §7 · 10 → §9 · 11 → §10 · 12–13, 25 →
   `cifras.json` + `verificar` · 14 → §4 (temporal, purga) · 15 → no aplica (no entra el tipo de día) · 19–23 → §8.3,
   Ap. B, Tabla 4, póster ≥ 24 pt.
7. **Prueba rápida de CM §0:** releer el informe tachando "Shiro" y "Guardian"; si sigue completo, se reescribe.
8. **Revisión humana:** un integrante del grupo por pieza.

## 14. Riesgos
| Riesgo | Efecto | Mitigación |
|---|---|---|
| R1 Ningún modelo supera a nivel + horario (probable en N1, §3.2) | escenario menos vistoso | relato invariante (§6.2), caso C definido, N2 detrás de H2 |
| R2 Validación con 51 picos | elección ruidosa | banda de 5 puntos a favor del exportable; IC en todo |
| R3 Los cortes de abril no valen en mayo (reglas: 6,7–11,0 % de rojo realizado [chequeo de solo lectura, no reproducido]) | presupuesto incumplido | se reporta como deriva; scorecard; recalibración mensual |
| R4 El relato del parcial 1 queda corregido | parecer contradicción | "el parcial 1 midió si reconoce; este, cuánto antes avisa"; correcciones en el Apéndice A |
| R5 Supuestos de impacto leídos como cifras | crítica tipo AE I-1/I-12 | SIMULADO, supuestos como parámetros, tarifa vacía por defecto |
| R6 Enunciado reciclado del 26-1; formato desconocido | retrabajo | confirmar por WhatsApp; valores por defecto (§15) |
| R7 Referencias no verificables | citas erróneas | solo referencias comprobadas; problema planteado con datos propios |
| R8 APA con python-docx (campo de página, sangría francesa) | formato defectuoso | estilos + XML mínimo; revisión visual en PDF |

## 15. Preguntas abiertas
**Bloquean:** (1) el plan con D1 y D3 → H1; D4 → H4; D2 → H5 (relato); (2) ¿ejecutar N2? (D5) → se decide en H2 con las
cifras de N1 y bloquea solo H3.
**No bloquean (valor por defecto entre paréntesis):** tarifa y moneda (campo vacío; solo kWh) · tamaño del póster (A1
vertical) · por WhatsApp: enunciado vigente (el del 26-1), fecha y medio de entrega (Classroom: PDF + HTML), si hay
sustentación o demo (el mockup corre sin red), qué es el "ejemplo adjunto de Classroom" (se asume `Parcial2.pdf`),
escudo de la universidad (si el grupo lo aporta).

## 16. Discrepancias con la crítica
- **Presupuesto de rojo (M2):** la crítica sugiere un top fijo del 5 %; uso la tasa base de la etiqueta en entrenamiento
  (7,66 %), que se decide sin mirar la prueba y significa "tanto rojo como lecturas que de verdad preceden un pico". El
  5 % y el 10 % quedan como sensibilidad y como deslizador.
- **Reentrenar con el 100 % (m12):** no se reentrena; se evalúa el mismo modelo de `fit` cuyos cortes fijó la
  validación. Pierde el 15 % de datos pero elimina el desplazamiento de escala.
- **Tarjeta 1 (B2):** el color no se fija "respecto de 200 Wh": el pronóstico del gemelo supera 200 Wh en el 0,03 % de
  las lecturas en calma [chequeo de solo lectura, no reproducido] y nunca se pondría rojo; usa sus cortes de validación al mismo presupuesto.
- **Listón (B1):** la logística con la misma ventana no es línea base sino **candidata** (G2/G5): la regla 11 la admite
  como modelo elegido y es exportable. El listón son las reglas sin entrenar, incluida nivel + horario, la más fuerte a
  ≥ 20 min en el chequeo; y el criterio A/B/C se mide a ≥ 20 min (m3), no a ≥ 10.
- **Tres escenarios de $ (M6 vs §7.5):** se conservan como una tabla de 3 filas; es aritmética sin coste.
