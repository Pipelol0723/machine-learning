# Plan del Parcial 2 (Aprendizaje Supervisado) — Shiro Guardian: ¿cuánto antes se puede avisar de un pico de consumo?

> **Estado:** aprobado el 21-oct-2026 (sí a las 4 decisiones; cifras solo en kWh). Reemplaza el plan anterior de taquilla de cine (TMDB), que copiaba el tema de un ejemplo de otro grupo. **Ajustes posteriores del usuario (21-oct):** el mockup se queda con las tarjetas 1–2 (sin pasada 2); se añade un guion de sustentación con reparto entre los 4 integrantes y recorrido de la demo; póster A1 vertical en PDF; autores en este orden: Jose Leonardo Diazgranados, Sofía Londoño, Andrés Felipe Céspedes Rondón, Alex Duran. El enunciado vigente es el PDF "26-1" que el profesor subió a Classroom con los 3 ejemplos; no hay fecha de entrega y habrá una sustentación corta. Historial de iteraciones y reglas de diseño en `planeacion/`.

## Portada — lo que hay que decidir (≈ 2 páginas)

**Shiro Guardian** es la parte de Shiro que vigila el consumo del hogar y avisa *antes* de un **pico** (más de 200 Wh en una lectura de 10 minutos, como varios aparatos grandes a la vez) para que la persona alcance a aplazar una carga grande. Este parcial mide cuánta anticipación se logra y cuántas falsas alarmas cuesta.

**Qué verás al final**
1. Una página web sin internet: escribes cómo está la casa y ves el consumo esperado en 10 minutos y el color del **semáforo** (verde, amarillo o rojo según la probabilidad de un pico en la próxima media hora); luego recorres el mes que los modelos nunca vieron, con su antes y después.
2. Informe APA (≤ 12 páginas), póster y 7 diapositivas con las mismas cifras, de un solo cuaderno.
3. Con cualquier resultado: qué modelo usa Guardian, cuántos picos avisa con margen y qué cambia en Shiro.

**Palabras clave**
- *Momento tranquilo*: lectura fuera de un pico. *Aviso*: racha de lecturas en rojo; *útil* si un pico empieza en los 30 minutos siguientes.
- *Regla de nivel*: avisar cuando el consumo actual ya es alto, sin aprender de ejemplos (lo que el medidor da gratis).
- *Modelo mínimo*: modelo **entrenado** con dos variables: consumo actual y qué tan seguido hubo picos a esa hora (laborable o fin de semana). *Modelos complejos* (36 variables): bosque aleatorio (comité de árboles que votan), regresión logística y gemelo digital (simula el consumo siguiente).
- *Validación*: las dos semanas y media previas al mes de prueba, donde se elige el modelo y se fijan los colores; ahí el *piso* exige más picos avisados que la regla de nivel, 1 de cada 4 con margen y 1 aviso útil de cada 3.

**El cambio que tienes que aceptar**
- El parcial 1 reportó "86,9 % de picos detectados", pero midió **reconocer un pico que ya empezó** (su modelo aprendía "¿la lectura de ahora supera 200 Wh?" y contaba avisos tardíos), y su probabilidad mínima para alarmar (0,40) se eligió mirando el mes de evaluación, como estudiar con el examen. Por eso el 86,9 % no sirve como promesa de avisar a tiempo.
*Cálculo rápido al planear (rangos; se confirman al ejecutar):*
- Exigiendo margen (al menos dos lecturas antes: 10 a 20 minutos o más), el titular esperado ronda **3 de cada 10 picos** (23 a 27 de los 84 del mes de prueba, según cómo se construya la señal).
- Costo: con 100 a 120 minutos de rojo al día, **cerca de 6 de cada 10 avisos rojos (59–63 %) no tendrán un pico detrás** (el 37,3 % del parcial 1 contaba picos ya empezados). Menos rojo: menos falsas alarmas y menos picos avisados.
- La regla de nivel logra cerca de 1 de cada 5; el modelo mínimo la superaría por pocos picos, quizá indistinguibles con 84. Entregamos la medición honesta, no una victoria segura.
- El pronóstico de consumo se equivoca casi lo mismo que repetir la última lectura (solo gana en los errores grandes) y se queda corto en los picos; la página lo advierte.

**Por qué es mejor para Shiro y para la nota**
- **Shiro:** solo un aviso con margen deja tiempo para "aplazar", la acción que aprenderá el agente del tercer corte; con el 86,9 %, Guardian prometería lo que el medidor ya hace.
- **Nota:** el enunciado pide una cifra de anticipación con escenario, antes y después, semáforo y limitaciones; un número inflado sería lo contrario.

**Cuatro resultados posibles** (el elegido sale de la validación y siempre maneja el semáforo; página, póster y diapositivas no cambian de estructura)
- **C1** En validación, ningún modelo pasa el piso → Guardian colorea sin notificar.
- **A** En el mes de prueba, el complejo elegido avisa 10 picos más de cada 100 que el mínimo, sin ser azar → usa el complejo.
- **C2** El mínimo elegido avisa 10 de cada 100 más que el mejor complejo, sin ser azar → usa el mínimo.
- **B** Cualquier otro (diferencia menor, azar o prueba que no confirma) → usa el elegido y lo declara.

**Decisiones sí/no**

| # | Pregunta | Recomendación | Si no | Detiene |
|---|---|---|---|---|
| 1 | ¿Centrar el parcial en Guardian, cuyo aviso alimentará al agente del tercer corte? | Sí | el gemelo con su margen de error | todo |
| 2 | ¿Presentar ≈ 3 de cada 10 picos avisados con margen (23 a 27 de 84), con ≈ 6 de cada 10 avisos rojos sin pico, en lugar del 86,9 %? | Sí | mantener el 86,9 % declarando que mide otra cosa | informe, póster, diapositivas |
| 3 | ¿Mockup como página web sin instalar nada? | Sí | cuaderno con controles e instalar librerías | la página |
| 4 | ¿Cifras en pesos? | No, solo kWh | tarifa citada por el grupo | esas cifras |

**Ya decidido por defecto** (objetable al aprobar; no detiene nada; razones en §3 y §13)
- El informe dice qué medía el 86,9 % y de dónde salió el 0,40; el parcial 1 no se toca. La memoria del proyecto (`CLAUDE.md`) anota 0,580 como F1 por lectura (medida que combina aciertos y cobertura) del detector a 0,40; es 0,47 (0,580 es con el valor por defecto, 0,5): se corrige esa nota.
- Se entrenan dos modelos hechos para anticipar (≈ 1 min); el resultado se informa sin esperar respuesta.
- Rojo en ≈ 8 de cada 100 momentos tranquilos, tantos como los que preceden un pico; movible en la página.
- Modelos con datos hasta el 13 de abril, sin reentrenar al final; el piso se fijó viendo cálculos rápidos de la prueba, por eso solo decide en validación.
- Póster A1 vertical; 7 diapositivas.

> Resumen técnico. **Indicio** = chequeo de solo lectura al planear (rango; se confirma al ejecutar). **CM** = `CLAUDE.md`; **P05** = propuesta del proyecto. Fuentes en §15.

## 1. La necesidad de Shiro
**Componente:** Shiro Guardian, "capa de clasificación de riesgo y notificación proactiva" (P05 §13): semáforo de la próxima media hora y propuesta que la persona aprueba, ajusta o rechaza en `ApprovalGate` (pantalla de aprobación). Fase opcional: no desplaza el MDP (entorno donde aprende el agente del tercer corte). De sus dos alarmas (CM §7.25) va la de umbral, anticipada; la de rareza (DBSCAN) queda para el tercer corte.
**Decide:** qué probabilidad de pico entra al MDP y si Guardian notifica. **No se reabre:** gemelo = lineal + retardos; boosting fuera (CM §7.19); convenciones de CM §4.

## 2. Definiciones (fijadas antes de calcular)
- **Pico:** lecturas > 200 Wh separadas por < 30 min (`gap=3`); inicio *s*. **En calma** (momento tranquilo): fuera de [*s*, fin] de todo pico; dentro, "rojo en curso" (medidor, sin ML). Fijar el fin mira 3 lecturas adelante (17 de prueba, < 0,5 %; declarado).
- **Etiqueta de anticipación:** calma en [*s*−3, *s*−1]. **Antelación:** 10 × (*s* − primera lectura en rojo de la ventana) min, nominal; la real es 0 a 10 min menor. **Tiempo útil:** ≥ 20 min nominales (≥ 10 reales) para ver, aprobar y no encender; la propuesta vence a los 30; se reportan 10, 20 y 30. El primer pico de prueba empezó en el entrenamiento: máximo 83 de 84.
- **Aviso:** lecturas en rojo agrupadas con `gap=3`; útil si toca [*s*−3, *s*−1]; con duración media. **Presupuesto:** % de la calma en rojo; amarillo, el tramo siguiente igual. **Acierto de un color:** % de sus lecturas con etiqueta 1 (base en prueba 6,91 %). **Azar:** ≈ 15 % de picos a ≥ 20 min.
- **Desplegado y mismo tiempo en rojo:** el titular ({n20}) aplica a la prueba los cortes de validación y reporta los minutos reales; para comparar señales, cada una marca su top-*r* % en la calma de prueba (empates por orden cronológico): en los casos, *r* = 7,66 %; para la regla del escenario ({m20}), *r* = rojo realizado del elegido.
- **Particiones:** solo temporal; entrenamiento con retardos, 15.783 filas hasta 30-abr 08:20; prueba = las 3.946 filas de las cifras ya publicadas, o anclas (84 picos en 27,4 días); `fit` = 85 % inicial del entrenamiento (hasta el 13-abr); validación = 15 % final (2.368 lecturas, 51 picos); purga de 3 lecturas en las fronteras. **Rango plausible:** IC 95 % de un bootstrap pareado por día. **Exportable:** corre en el navegador (G0, lineales).
- **Calibración:** en validación, cada puntaje pasa a "de cada 100 momentos así, X precedieron un pico" (10 deciles), que entra al MDP.

## 3. Candidatos, piso, selección y casos
**Candidatos.** **G0, modelo mínimo entrenado de 2 variables:** percentil del nivel actual + percentil de la frecuencia de la etiqueta por hora × laborable/fin de semana (48 celdas), estimados en `fit`. **G1** RF y **G2** logística con retardos, entrenados para reconocer. **G3b** gemelo de 36 variables en `fit` (su pronóstico es el puntaje). **G4** RF y **G5** logística entrenados para anticipar. La **regla de nivel** (consumo actual frente a un cuantil, sin etiquetas) es listón. **Simplicidad:** G0; G3b, G2, G5; G1, G4.

**Piso, en validación:** más picos con ≥ 20 min que la regla de nivel, ≥ 25 % de picos y ≥ 33 % de avisos útiles. Idea de CM §7.9 (con demasiadas falsas alarmas el semáforo se ignora); cifras nuestras, fijadas tras ver indicios de la prueba. Indicio: en validación la regla misma pasa el 25 % y el 33 % (en prueba queda debajo: 20–24 %); lo que discrimina es superarla.

**Selección, solo en validación:** entre los que pasan el piso, el más simple de los que quedan a menos de 10 puntos del mejor (≥ 20 min; dentro de un nivel, el de mayor %); si ninguno pasa, igual sin piso (C1). Sesgo deliberado hacia lo simple (10 puntos es lo mínimo que justifica 36 variables frente a 2): el rango plausible de una diferencia es ±5 puntos entre señales casi iguales y ±9 a ±12 entre distintas (indicio). El gemelo es siempre el segundo elegido.

**Casos** (en orden; prueba, ≥ 20 min, mismo tiempo en rojo; complejo = el mejor de los demás candidatos en validación; criterio → qué cambia en Shiro)
- **C1** ninguno pasa el piso en validación → el elegido colorea sin notificar; "diferir" solo en picos anticipados.
- **A** elegido ≠ G0 y, en prueba, elegido − G0 ≥ 10 con IC > 0 → su probabilidad calibrada entra al MDP y dispara `ApprovalGate`.
- **C2** elegido = G0 y, en prueba, G0 − complejo ≥ 10 con IC > 0 → Guardian despliega G0; lo complejo queda para el gemelo.
- **B** cualquier otro → Guardian usa el elegido; si la prueba no lo confirma o lo contradice, se declara y se revalida con otra vivienda.

## 4. Qué se reutiliza, qué ya se sabe y qué se calcula
**Reutilizado** (salidas guardadas verificadas)
- Detector del parcial 1 (RF + retardos, "lectura actual > 200 Wh") a 0,40: 86,9 % de picos tocados, 3,03 avisos/día, 37,3 % falsos, F1 0,47, 21,1 % del tiempo en alerta, avisos de 100,5 min.
- Gemelos (objetivo `Appliances`, temporal): **G3a**, 36 variables, todo el entrenamiento (anclas, KPI): R² 0,557, MAE 28,17, RMSE 60,54 Wh; **G3b**, 36 variables, `fit`; **G3c**, 6 variables (hora, `lights`, T2, RH_2, T_out, `lag1`), todo el entrenamiento, vio la validación (solo tarjeta 1): MAE 28,85.

**Indicios** (rojo = 7,66 % de la calma; rangos entre construcciones y desempates)

| Señal | ≥ 10 min | ≥ 20 min (de 84) | Avisos/día | Duración | Útiles |
|---|---|---|---|---|---|
| Regla de nivel | ≈ 39 % | 20–24 % (17–20) | ≈ 3,6 | ≈ 27 min | 31–33 % |
| **G0** | ≈ 37 % | **27–32 % (23–27)** | 2,6–3,1 | ≈ 38 min | 37–41 % |

Además: G3c como puntaje ≈ regla (21–23 %); a ≥ 10 min la regla iguala a G0 (su ventaja está en el margen); G0 − regla, +6 puntos, IC [−3; +15]; validación ≈ 8 a 14 puntos más generosa; con cortes de validación, el rojo realizado en prueba va de 6,7 % a 11,0 % (G0 ≈ 9,3 %, ≈ 120 min/día). Persistencia: MAE 26,64, RMSE 66,44 Wh; en lecturas > 200 Wh, MAE 148,2 y sesgo −58,6 (gemelos ≈ 140 y ≈ −103). **En Shiro:** el pronóstico no sirve de semáforo (es casi `lag1`); el listón real es G0.

**Un paso adelante, columna por columna** (G1 a G5, G3c, explicador)
- G0, G4 y G5 estiman si un pico empieza en *t*+1 a *t*+3; G1, G2 y G3b, la lectura *t*+1 (proxy: se espera que no superen a la regla); G3c, el consumo en *t*+1.
- 29 exógenas (4 temporales, `lights`, T1–T9, RH_1–RH_9, 6 de clima): las de *t*. `lag1`, `lag2`, `lag3`, `lag6` = `Appliances` en *t*, *t*−1, *t*−2, *t*−5; `media_1h`, `max_1h`, `std_1h` sobre *t*−5 a *t*.
- `assert` de no fuga: en 200 instantes al azar (semilla 42), el vector hecho solo con `df.loc[:t]` es idéntico al de la tabla. Percentiles, horario, escalado y modelos, con `fit`; cortes y calibración, con validación.

**Cálculos del núcleo** (hipótesis · Shiro · nota)
- **N1a Anclas** (`assert` contra cifras publicadas): G3a, detector a 0,40 y G3c (R² ±0,001; Wh ±0,01; % ±0,05; F1 ±0,005; min ±0,05; conteos exactos); si una falla, se detiene · cifras alineadas.
- **N1b Persistencia:** MAE y RMSE de G3a y G3c un paso adelante frente a repetir la última lectura (total, por franja, > 200 Wh). G3a pierde en MAE (≈ +6 %) y gana en RMSE (≈ −9 %); G3c pierde ≈ +8 % en MAE (RMSE por calcular); todos subestiman picos; con exógenas en *t* el MAE cambia < 0,05 Wh (indicio) · la recompensa del MDP corrige la subestimación · KPI; tarjeta 1.
- **N1c Latencia del parcial 1:** ¿el detector a 0,40 avisa antes, en el inicio, después o nunca? Casi nunca antes · corrige el "a tiempo" heredado · limitaciones.
- **N1d Anticipación:** G0 a G5 frente a la regla: piso, elección, calibración, bootstrap. Los entrenados para reconocer anticipan como la regla · qué anticipador usa Guardian · escenario, semáforo, mockup.
- **N1e Explicador:** árbol de profundidad 3 que imita el rojo del elegido en `fit` (con puntajes OOB si es bosque); fidelidad en prueba. Reproduce casi todo el rojo · capa de explicación · "reglas o patrones".
- **N1f Energía y casos:** exceso > 200 Wh en picos anticipados; casos críticos = pico no anticipado con más energía y aviso falso más largo. Casi todo el exceso queda sin anticipar · cuánto alcanza "diferir" · KPI, ética.
- **N2 Entrenar para anticipar (sí por defecto):** G4 RF (200 árboles) y G5 logística con la etiqueta de anticipación y el mismo vector; ≈ 80 líneas, 1 min. Superan a G0 por ≥ 10 puntos · probabilidad de pico al MDP · evolución del póster.

**No se propaga:** "F1 0,580 a 0,40"; `prob()` del mockup del parcial 1 (una rampa) y sus cifras inventadas; "18 sensores interiores" (T6/RH_6 miden fuera); la ruta `hora > 7,5 → lights > 5,0` como explicación de avisos.

## 5. Semáforo
**Unidad:** la próxima media hora, recalculada cada 10 min. Todo color sale de la señal elegida, salvo el rojo en curso (medidor), que se dibuja distinto.

- **Verde** (calma, bajo el corte amarillo): nada; Shiro registra. **Amarillo** (calma, entre cortes): ámbar con la regla del explicador, sin notificar.
- **Rojo anticipado** (calma, sobre el corte rojo): notificación y propuesta en `ApprovalGate`, que vence en 30 min; en C1, solo el color.
- **Rojo en curso** (lectura > 200 Wh o dentro de un pico): borde y texto "en curso"; no repite la notificación.
- **Gris** (> 30 días sin recalibrar cortes): "baja confianza"; no propone. No se activa en la prueba (27,4 días); limitación: el modelo usa datos hasta el 13-abr (44 días al 27-may); en producción, modelo y cortes se reentrenan juntos cada mes.

**Sin circularidad:** cortes = cuantiles del puntaje en la calma de validación (rojo: top 7,66 %; amarillo: el siguiente 7,66 %); en prueba se reportan tiempo y acierto por color (si se apartan, es deriva); el 21,1 % y el 0,40 no son objetivo.

## 6. Lenguaje de negocio sin mentir
F1, exactitud, R² y AUC solo en el Apéndice A (AUC: "probabilidad de que un momento previo a un pico puntúe más que uno tranquilo"), el póster y el cuaderno. Analogías: bosque = comité que vota; gemelo = lo gastado hace 10 min corregido por hora, luz y clima.

**Frases plantilla** (`{…}` desde `cifras.json`)
- *Escenario:* "Si Shiro Guardian hubiera funcionado en el mes que el modelo nunca vio (30-abr a 27-may de 2016), con el semáforo en rojo {min_dia} minutos al día, habría avisado con al menos dos lecturas de antelación (entre 10 y 20 minutos o más) {n20} de los 84 picos; con el mismo tiempo en rojo, avisar cuando el consumo ya es alto, {m20}."
- *C1:* "En validación ningún modelo cumplió el piso ({condición}): el semáforo informa sin notificar; en prueba el mejor avisó {n20} de 84. → {Los modelos no mejoran lo que el medidor ya da | Con estos sensores anticipar es difícil}; falta saber qué aparato se enciende." (La primera si solo falló superar a la regla; la segunda si falló el 25 % o el 33 %.)
- *A:* "{elegido} avisa {d} picos más de cada 100 que el de dos variables. → Guardian puede ser proactivo: su aviso entra al estado del MDP."
- *B:* "{Con 84 picos, el de {k} variables y el de dos no se distinguen | La prueba favorece a {otro} por {d} de cada 100, al revés que la validación}: Guardian usa {elegido}, elegido en validación. → Avisar con margen es posible en {p20} de los picos; el modelo se revalida con otra vivienda."
- *C2:* "El de dos variables avisa {d} picos más de cada 100 que el de {k}. → Más variables no ayudan a anticipar; la complejidad queda para el gemelo."
- *Antes/después:* "Antes: el hogar se entera por la factura o cuando el pico ya empezó. Después: a las {hh:mm} el semáforo pasó a rojo, {k} min antes del pico, y Shiro propuso no encender cargas grandes; la persona decide." Día mediano en picos anticipados; sin curva "con Shiro".
- *Pronóstico:* "El gemelo se equivoca {mae} Wh frente a {mae_p} de repetir la última lectura; en los picos, {según N1b}: la recompensa del MDP debe corregirlo." Nunca "−46,5 % frente a la media".
- *Exactitud (póster):* "El semáforo cuesta exactitud a propósito: pinta de rojo ≈ 1 de cada 13 momentos tranquilos para avisar con margen", junto a "todo verde" (≈ 93 %), precisión y sensibilidad.

**KPI** medidos (picos con ≥ 20 min, avisos/día, duración, útiles, error frente a la persistencia, kWh de exceso en picos anticipados) y simulados (exceso anticipado × % evitable × % aceptado; $ solo con tarifa; escenarios bajo, medio y alto), nunca mezclados; con tarifa plana, diferir no ahorra dinero. **Prohibido en el cuerpo:** "A 0,81 vs B 0,79", R² como "precisión", cifras aleatorias solas, "a tiempo" sin minutos, "ahorro" sin supuestos, cifras de sector sin fuente, causalidad desde importancias.

## 7. Mockup (Parte 2, 2,5)
HTML autocontenido, sin librerías ni red: una página, 4 tarjetas, **≈ 400–500 líneas en dos pasadas**. Pasada 1 (≈ 320, el mínimo entregable): tarjetas 1–2 con antes/después y autoverificación. Pasada 2: tarjetas 3–4.

| Tarjeta | Entrada | En vivo | Precalculado | Color y señal |
|---|---|---|---|---|
| 1 ¿Y si…? (nunca se recorta) | "lo que mira Guardian" (consumo actual, hora, laborable/fin de semana) y "lo que además usa el pronóstico" (`lights`, T2, RH_2, T_out); o 5 momentos reales | color de Guardian, "de cada 100 momentos así, X precedieron un pico" y acción; "Consumo esperado en 10 min" (G3c) con su error | coeficientes, tablas, cortes, momentos | pronóstico: barra azul (marcas en 60 y 200 Wh); Guardian: señal de la tarjeta 2 |
| 2 Semáforo del mes | rojo y amarillo; día; % evitable y aceptado | colores de las 3.946 lecturas; picos con ≥ 10/20/30 min, avisos/día, duración, útiles, rojo realizado, acierto por color; la regla en cifras; tira del día; ANTES/DESPUÉS en kWh, SIMULADO | serie, energía, puntajes | señal elegida; la regla, sin colores |
| 3 Impacto simulado | tarifa (vacía), escenario | kWh y $, SIMULADO; aviso de tarifa plana | energía | ninguno |
| 4 Propuestas | aprobar, ajustar, rechazar | bitácora | 4 situaciones con la regla del explicador | el de la tarjeta 2 |

**Guardian en la tarjeta 1:** si el elegido es exportable, se calcula en vivo (G0: 48 celdas, dos tablas de percentiles y 10 tasas, ≈ 20 líneas de JS; lineales: coeficientes de `fit`; variables no visibles, del momento cargado y rotuladas). Si es un bosque, los momentos cargados llevan su color exacto (el de la tarjeta 2) y, al editar, la regla del explicador en grises, rotulada "aproximación ({fid} % de coincidencia)": nunca contradice a la tarjeta 2.
**Ejemplos por regla** (prueba; empate, el más temprano). Tarjeta 1: calma verde de puntaje mediano; primer rojo del útil de antelación mediana y del falso más largo; 20 min antes del no anticipado con más energía; inicio del pico de energía mediana. Tarjeta 4: útiles de mayor y mediana antelación, falso más largo, no anticipado con más energía.
**Funcional (v1):** abre sin red ni errores; ≤ 20 líneas de JS en la página (excepción acotada, no un arnés aparte) comparan métricas de la tarjeta 2 y el color de los 5 momentos en ambas tarjetas, y escriben "Verificación: OK / DIFIERE" (Edge headless); más rojo sube anticipación y avisos/día; ningún número en la plantilla.

## 8. Informe ejecutivo APA (Parte 1, 1,0)
**APA 7 de estudiante:** portada; Calibri 11, doble espacio; `Heading 1–3`; tablas y figuras con rótulo APA; "Candanedo et al. (2017)" en el texto (UCI n.º 374, Breiman, Pedregosa et al., Ley 1581; DOI verificados); cifras de sector solo con fuente. **Extensión:** ≤ 12 páginas de cuerpo (≈ 2.400 palabras, 6 figuras, 4 tablas), más resumen, referencias y Apéndices A (ficha técnica) y B (glosario).

**Secciones** (abren con la necesidad de Shiro y cierran con qué cambia; págs.): 1 Problema y decisión de Shiro (1,5; Fig. 1 un día con y sin semáforo) · 2 Modelo elegido: datos, dos familias con analogía, validación temporal, listones (2; Tabla 1 decisiones) · 3 Resultados: escenario, antes/después, reglas y acción, semáforo, impacto (5; Fig. 2 picos avisados a ≥ 10/20/30 min frente a la regla, con rango plausible; Fig. 3 tiempo y acierto por color; Fig. 4 regla del explicador → acción; Fig. 5 mockup; Tablas 2 y 3, regla → acción y supuestos) · 4 Conclusiones por actor (1) · 5 Limitaciones y ética: una vivienda sin verano, deriva, 84 picos, latencia del parcial 1, quién paga cada error, privacidad (2; Fig. 6 casos críticos; Tabla 4) · 6 Recomendaciones (0,5).

## 9. Presentación (Parte 3, 0,5) y póster (Parte 4, 1,0)
**Presentación (Shiro como producto propio):** 7 diapositivas con notas: portada; arquitectura (medidor, `iot-bridge`, servicio de modelos, semáforo con `ApprovalGate`, app); datos y privacidad (proceso local, agregados con consentimiento); roles; ciclo mensual (tablero sin colores; primer mes en gris); capacitación; piloto Twin → Guardian → Home.
**Póster:** A1 vertical editable (PDF, PNG); cuerpo ≥ 24 pt, ≤ 500 palabras; título como pregunta; orden del enunciado. Dataset: 19.735 lecturas, 29 variables, 137 días; calidad: una vivienda sin verano, `rv1`/`rv2` fuera, consumo múltiplo de 10 Wh, T6/RH_6 exteriores, 2 días incompletos. Evolución T2 → P2 con "qué cambió en Shiro" y etiqueta rotulada (reconocer o anticipar). Resultados: gemelo frente a persistencia; elegido con exactitud y F1 frente a "todo verde" (§6); picos avisados frente a la regla; dos casos críticos; capturas.

## 10. Carpeta
`2do_Corte_Oct/Parcial_2_Aprendizaje_Supervisado/` (cuaderno a profundidad 2, `cifras.json` con claves G0–G5 y G3a–G3c, `figuras/`, `mockup/`, `generadores/`).

## 11. Hitos (sin fechas), núcleo, recorte y esfuerzo
- **H0** aprobación de las 4 decisiones → **H1a** cuaderno: anclas, persistencia, G0–G5, elección, cortes, explicador, energía y casos (alimentan ejemplos y antes/después de la página) y JSON (kernel limpio, anclas OK, `cifras.json`) → **H2** punto de control (≤ 15 líneas; informa, no espera) y **H3** mockup, pasada 1 (tarjetas 1–2, "Verificación: OK"; plantilla desde H0).
- **H1b** (tras H1a): latencia del parcial 1 y figuras → **H4** pasada 2 (tarjetas 3–4; tras H3) y **H5–H7** informe, póster y presentación (tras H1b, H2 y H3; docx, pptx, PDF, `verificar.py` limpio) → **H8** verificación final (§12; un integrante por pieza; correcciones a CM).

**Núcleo mínimo:** H0 a H3, H1b, informe, póster, 6 diapositivas, `verificar.py`. **Recorte, en orden:** presentación a 6; Fig. 1 y Apéndice B; sección 4 del informe a un párrafo; tarjeta 4; tarjeta 3; tira del día. **Nunca:** tarjeta 1 con color de Guardian, bloque antes/después, anclas, listones, partición temporal, `cifras.json`, limitaciones y ética.
**Esfuerzo:** cuaderno ≈ 500 líneas y 3–4 min; plantilla 400–500; informe 400; presentación y póster 200 cada uno; `verificar.py` 90 (≈ 1.900 líneas, cinco generadores).

## 12. Verificación
1. Cuaderno generado por script, ejecutado con nbclient en kernel limpio; `cifras.json` (valor, texto es-CO, partición, fuente) alimenta todo.
2. Heredadas: leídas con `nbformat` de las salidas guardadas y contrastadas con CM §6; si difieren, manda la salida guardada y se propone corregir CM (F1 0,580 → 0,47), sin detener el cuaderno.
3. `verificar.py`: sin `{{`, "[por calcular]", "TODO" ni nombres de herramientas; en el cuerpo del informe, ni "F1", "AUC", "R²", "log-loss", "accuracy" ni "exactitud"; cifra aleatoria con su par temporal; "a tiempo" y "antes del pico" solo con minutos; "20 minutos" con "al menos dos lecturas"; en el póster, F1 del parcial 1 solo con su etiqueta.
4. PDF revisado; prueba de Shiro primero (tachar "Shiro" y "Guardian") en informe, póster y diapositivas.

## 13. Decisiones de diseño y por qué
- **Presupuesto por tasa base (7,66 %), no 5 % fijo:** se decide sin mirar la prueba; 5 % y 10 %, como sensibilidad.
- **Sin reentrenar con el 100 %:** se evalúa el modelo de `fit` cuyos cortes fijó la validación; la escala del puntaje no se mueve.
- **Logística y mínimo, candidatos:** son supervisados y exportables; el listón sin etiquetas es la regla de nivel.

## 14. Riesgos y preguntas abiertas
**Riesgos:** el mínimo iguala o gana (probable): B y C2 ya escritos · elección y piso con 51 picos de validación: ruidosos, de ahí el margen de 10 puntos · cortes de abril en mayo: deriva reportada. **Por WhatsApp, sin bloquear nada** (supuesto): enunciado vigente (26-1), entrega (PDF y HTML), demo (sin red), "ejemplo adjunto" (`Parcial2.pdf`).

## 15. Fuentes
c.N = celda desde 0. Detalle comprimido (APA, Parte 3, carpetas, "no se propaga"): `planeacion/plan_v2_detalle.md`; reglas: `planeacion/reglas_vigentes.md`. **CM** §4, §6, §7.n (hallazgo n) · **P05** (`05_Propuesta_Proyecto_Shiro_Twin.docx`) §13 · **`Parcial_Corte1.ipynb`:** c.25 G3a; c.33 G3c; c.37 regla de 30 días; c.38 detector y 84 picos; c.40 elección del 0,40; c.22 F1 a 0,5; c.7 y c.35 árbol regresor · **`Taller1_Boosting.ipynb`:** c.3 particiones; c.17 evaluación; c.22 21,1 % y 100,5 min.
