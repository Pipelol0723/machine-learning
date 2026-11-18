# Plan de desarrollo: Parcial del Corte 3 — la consola de Shiro y el artículo IEEE del semestre

*Reescrito el 2026-11-17 a las 20:40 (sustituye el borrador del 12-nov). **Classroom «C3 Parcial»: vence el 18-nov a las
23:59** (revisado hoy: el texto no cambió desde el 10-nov y no hay anuncios nuevos). Quedan ≈ 27 horas.*

Enunciado (literal, resumido):

1. **Prototipo que implemente los 3 aprendizajes en el sector (3,0).** Ejemplo: el Space de Hugging Face
   `julianrincon-savi-agent`, que «cubre no supervisado y supervisado; a esto se le agrega lo de agente de refuerzo».
2. **Artículo en formato IEEE (2,0) que cubra todo el semestre**, con un ejemplo adjunto.

## 1. Apertura Shiro (plantilla del proyecto)

1. **Qué se construye.** Los dos criterios de cierre del proyecto que siguen abiertos: «demostración del entorno funcionando
   de principio a fin» (la consola) e «informe final» (el artículo). La consola es Shiro Twin completo por primera vez:
   el gemelo predice, Guardian avisa, el tipo de día da contexto y el agente propone. Hasta hoy cada pieza vivía en su
   propio taller.
2. **Decisiones de arquitectura que se fijan con este parcial.**
   - **Qué agente propone en Shiro Twin.** π\* del MDP (exacta, explicable), Q-learning con recompensa centrada (aprende sin
     modelo en ≈ 100 días, hallazgo 41) o DQN (ve la hora exacta, hallazgo 44). La consola los muestra lado a lado y decide
     por defecto π\*, con los otros dos como verificación.
   - **Cómo se muestra la incertidumbre:** decisión «dudosa» si la brecha de Q es pequeña (hallazgo 35); tipo de día con
     su margen (hallazgo 22) y bandera «desconocido» (hallazgo 24); rango de G0 (hallazgo 29); «fuera de los datos» cuando
     la red extrapola (madrugada con pico, hallazgo 44).
   - **Qué controla la persona:** λ (cuánto le cuesta esperar, hallazgo 34) y la tarifa de punta. La política se
     recalcula en la página para cada valor.
3. Recién entonces: datos, modelos y verificación (abajo).
4. Cierre del artículo: qué queda listo para Shiro Home y qué no (ahorro simulado pequeño, una sola vivienda, falta saber
   qué aparato se enciende).

## 2. Lo que ya existe y se reutiliza (inventario del 17-nov)

| Pieza | Dónde | Uso en el parcial |
|---|---|---|
| Simulador lineal de 6 variables (coeficientes del hallazgo 17) | Parcial 1, `Mockup_Shiro_Twin (1).html` | «¿Y si…?» de la pantalla 1 |
| G0: puntajes, cortes del semáforo, serie de mayo y 84 picos | Parcial 2, `mockup/datos_mockup.json` (394 KB) | semáforo de la próxima media hora |
| Tablero supervisado y cifras de Guardian | Parcial 2, `cifras.json` (nuevas + heredadas; incluye 0,567 · −4,459 · 0,557 · 0,642 · 33,3 %) | ficha del modelo y artículo |
| MDP de 40 estados, π\* y su tabla de Q | T1, `cifras.json`, `politica_optima_shiro.csv` | pantalla 3 y artículo |
| Política de Q-learning y brechas | T2, `cifras.json`, `politicas_base.csv` | pantalla 3 |
| Red DQN (semilla mediana) y cifras E1–E4 | T3, `dqn_pesos.json`, `cifras.json` | pantalla 3 (la red corre en la página) |
| Figuras | `figuras/` de cada taller (K5 perfiles, D5 atípicos, T2 arranque en frío, T5 batalla, POSTER_* del P2…) | artículo |
| Estética y patrón de página sin dependencias | mockups del Parcial 1 y 2 | consola |

**Lo que falta y hay que fabricar:**
- **Cifras del 2.º corte** (K-Means, jerárquico, DBSCAN): no están en ningún `cifras.json`. El exportador las
  **recalcula** (K-Means k = 2 sobre 136 días, silueta, tamaños, ARI con Ward) y las **ancla** contra los valores del
  CLAUDE.md (silueta 0,392 · 108 / 28 días · ARI 0,736). La lista de días «desconocidos» de mayo (2 de 26) se lee de las
  salidas guardadas del cuaderno del C2-T4.
- **El MDP en forma de datos** para resolverlo en la página: P(s′|s, a) (40 × 3 × 40), las recompensas por estado y
  la tarifa. Se obtiene ejecutando las celdas de preparación del cuaderno del T3 (datos, K-Means y MDP; sin entrenar), y
  se ancla contra π\* y V\* del T1.

## 3. Parte 1 (3,0) · `Consola_Shiro.html`

Una sola página **autocontenida** (sin red ni librerías; los datos van incrustados como JSON), oscura y sobria como el
ejemplo y los mockups anteriores, con el pie «Verificación: OK · N cifras comprobadas». **Una sola elección de contexto
arriba** (día de mayo + hora, con flechas) alimenta las cinco pantallas, así la demostración cuenta una historia continua.

| # | Pantalla | Aprendizaje | Qué hace (todo calculado en la página) |
|---|---|---|---|
| 1 | **Hoy en casa** | Supervisado | Curva real del día hasta la hora elegida, predicción del simulador lineal a un paso y **semáforo de G0** para los próximos 30 min con su rango. Mini «¿Y si…?»: luces y temperatura exterior cambian la predicción en vivo. |
| 2 | **¿Qué tipo de día es?** | No supervisado | K-Means k = 2 sobre la curva parcial del día: tipo estimado, **margen como confianza** y las dos curvas tipo. Bandera DBSCAN si el día es «desconocido» o atípico. Muestra que hasta media mañana la estimación es débil (hallazgo 21). |
| 3 | **¿Qué haría Shiro?** | Refuerzo | Para el estado de esa hora: la acción de **π\*** (iteración de valor resuelta en la página con λ y tarifa de los deslizadores), de **Q-learning** (tabla del T2) y de **DQN** (red del T3 ejecutada en la página). Marca «dudosa» y «fuera de los datos». Botón **«repetir el día»**: costo y espera del día con cada política frente a no actuar. |
| 4 | **Pregúntale a Shiro** | Integra todo | 8–10 preguntas sugeridas con respuestas por plantilla que leen el estado actual y citan cifras reales («¿Por qué aplazas ahora?», «¿Qué tan seguro estás del tipo de día?», «¿Por qué no aplazas a las 9?», «¿Cuánto ahorra esto al mes?»). Sin LLM ni red: modo determinista, como el ejemplo. |
| 5 | **Ficha del modelo** | — | Tablero supervisado con las **dos particiones** (regla del proyecto), tipos de día, G0 frente a la regla y al azar, agentes con IC del bootstrap, la recompensa centrada, fuentes y **límites honestos** (hallazgos 3, 4, 31, 33 y 41). |

**Arquitectura de los datos:**
```
generadores/exportar_datos.py → datos/consola.json   (serie de mayo: 10 min y por hora, G0, simulador, tipo de día,
                                                       DBSCAN, MDP P/R, políticas, pesos DQN, tablero)
                              → datos/cifras_semestre.json (unión de P2, T1, T2, T3 + bloque C2 recalculado; fuente única)
generadores/construir_consola.py → Consola_Shiro.html (plantilla + JSON incrustado)
```
**Anclas del exportador** (deben pasar antes de escribir nada): π\* recalculada en Python = `politica_optima_shiro.csv`;
VI en JavaScript = la de Python (se comprueba con Edge headless); la red en JS = la red en NumPy en 50 estados de
prueba; K-Means recalculado = 108 / 28 días y silueta 0,392.

**Alojamiento (decisión P1 ya tomada):** archivo HTML adjunto en Classroom **+ enlace publicado** como Artifact de
claude.ai, que Pipe comparte (sin cuentas nuevas).

## 4. Parte 2 (2,0) · Artículo IEEE del semestre

Word a dos columnas generado con python-docx → PDF por Word (decisión P2). Español, ≈ 6 páginas, autores: **Jose Leonardo
Diazgranados, Sofía Londoño, Andrés Felipe Céspedes Rondón, Alex Duran** (decisión P4). **Shiro como hilo:** cada
sección abre con lo que el gemelo necesitaba y cierra con la decisión que tomó.

| Sección | Contenido | Figura / tabla |
|---|---|---|
| Resumen · palabras clave | Shiro Twin; resultado principal de cada paradigma en una frase cada uno. | — |
| I. Introducción | El hogar, Twin → Guardian → Home, la pregunta del semestre y las contribuciones. | Fig. 1: arquitectura de Shiro (nueva, simple) |
| II. Datos y método | UCI n.º 374, las **dos particiones** y por qué, autocorrelación, variables de retardo, convenciones (umbral, bootstrap pareado por día). | — |
| III. Qué consume la casa (supervisado) | Tablero de regresores y clasificadores con la **inversión** bajo la partición temporal; retardos; confusor estacional (hallazgos 7, 11, 12, 18, 19). | Tabla I: tablero con las dos particiones |
| IV. Qué tipo de día es (no supervisado) | K-Means, jerárquico y DBSCAN; dos tipos de día que el calendario no explica; observabilidad; atípicos (hallazgos 21–25). | Fig. 2: perfiles de los dos tipos (K5) |
| V. Cuándo avisar (Guardian) | Reconocer frente a anticipar; G0 frente a modelos de 36 variables; validación optimista (hallazgos 26–31). | Fig. 3: G0 frente a la regla y el azar |
| VI. Qué decidir (refuerzo) | MDP y contabilidad corregida; λ; Q-learning; recompensa centrada y arranque en frío; DQN y la hora exacta (hallazgos 32–44). | Tabla II: agentes en mayo · Fig. 4: arranque en frío |
| VII. Prototipo | La consola: qué hace cada pantalla y cómo se verifican sus cifras. | Fig. 5: captura de la consola |
| VIII. Discusión, ética y límites | Ahorro simulado pequeño (0,59 %), una sola vivienda en invierno–primavera, falta el aparato, aprobación humana, quién paga cada error. | — |
| IX. Conclusiones · Referencias | Qué queda listo para Shiro Home. Candanedo et al. 2017, Breiman 2001, Ke et al. 2017, Ester et al. 1996, Sutton y Barto 2018, Watkins y Dayan 1992, Mnih et al. 2015, van Hasselt et al. 2016. | — |

`generadores/generar_articulo.py` → `Articulo_IEEE_Shiro_Twin.docx/.pdf`; toda cifra entra como `{clave}` de
`cifras_semestre.json` (patrón de los talleres del corte 3).

## 5. Verificación (debe terminar con código 0 antes de entregar)

`generadores/verificar.py`:
- anclas del exportador superadas (π\*, VI en JS = Python, red JS = NumPy, K-Means);
- la consola abre sin errores en la consola del navegador y sus cinco pantallas responden (Edge headless + navegador
  integrado), con captura de cada una;
- cero residuos (`{clave}`, nan, TODO, menciones internas) en la consola y en el artículo;
- **todo decimal de la consola y del artículo sale de `cifras_semestre.json`** o es un parámetro declarado;
- regla de las dos particiones: ningún R² o F1 de la aleatoria sin su par temporal;
- el artículo cabe en 5–7 páginas y el PDF existe.

## 6. Calendario (hora de Colombia)

| Cuándo | Trabajo | Hecho cuando |
|---|---|---|
| **17-nov, 20:45–24:00** | `exportar_datos.py` con sus anclas → `consola.json` y `cifras_semestre.json`. Esqueleto de la consola con la elección de contexto y la pantalla 1. | anclas en verde; pantalla 1 funciona |
| **18-nov, 08:00–13:00** | Pantallas 2–5 (VI y red en JS, «repetir el día», plantillas, ficha). Revisión en el navegador. | las 5 pantallas responden; VI y red coinciden con Python |
| **18-nov, 13:00–18:00** | Artículo: `generar_articulo.py`, figura de arquitectura, captura de la consola, PDF. | PDF de 5–7 pp. |
| **18-nov, 18:00–20:00** | `verificar.py`, correcciones, publicar el Artifact. | código 0; enlace funcionando |
| **18-nov, 20:00–21:00** | Revisión de Pipe y entrega en Classroom (HTML + PDF del artículo + enlace en un comentario privado). | «Se entregó la tarea» |
| 21:00–23:59 | Holgura. | — |

**Paralelo recomendado:** el artículo no depende de la consola salvo por su captura (Fig. 5, se añade al final). Si se
arranca en una sesión aparte desde ya, sobre los `cifras.json` existentes, la holgura sube de 3 a ≈ 7 horas.

## 7. Recortes en orden, si el tiempo aprieta

1. «Repetir el día» de la pantalla 3 → se queda la decisión de la hora elegida.
2. «¿Y si…?» de la pantalla 1 → se queda la predicción.
3. Pregúntale a Shiro: de 10 preguntas a 5.
4. Artículo: la Fig. 1 pasa a ser una tabla de componentes.

**No se recorta:** las tres familias funcionando en la página (supervisado, no supervisado y refuerzo), la ficha con
límites honestos, las dos particiones y `verificar.py` en código 0.

## 8. Riesgos

- **Integrar cinco fuentes de cifras sin contradicciones.** Mitigación: fuente única `cifras_semestre.json` y
  `verificar.py`.
- **La VI en JavaScript no coincide con Python** (orden de estados, empates). Mitigación: ancla con los 40 estados y la
  regla de desempate del T1 (si Q(no actuar) empata, no actuar).
- **El DQN no supera a π\*** (ya medido: 97 % del ahorro). Se muestra tal cual, como hace el ejemplo del profesor.
- **Sin sustentación confirmada** (P5). Si el profesor la anuncia, el guion corto se hace el 18-nov en la holgura.

## 9. Decisiones

| # | Decisión | Estado |
|---|---|---|
| P1 | Alojamiento | **Tomada:** HTML adjunto + enlace publicado (Artifact) |
| P2 | Formato del artículo | **Tomada:** Word a dos columnas → PDF |
| P3 | Chat | **Tomada:** preguntas sugeridas con plantillas (determinista) |
| P4 | Autores | **Tomada:** los cuatro, en el orden del C2 |
| P5 | Sustentación | Sin anuncio en Classroom al 17-nov; confirmar por WhatsApp |
| P6 | Quién entrega | Propuesto: Claude entrega el 18-nov a las 20:00–21:00 **después del visto bueno de Pipe** |
| P7 | Artículo en paralelo | Propuesto: sí, en una sesión aparte desde esta noche |
