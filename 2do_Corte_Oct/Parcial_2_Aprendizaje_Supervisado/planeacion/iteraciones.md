# Registro de iteraciones del plan — Parcial 2

| Ronda | Agente | Insumo | Resultado |
|---|---|---|---|
| 0a | Sonnet (extracción) | 4 PDF de Documentacion | análisis del enunciado y los ejemplos: 13 ambigüedades, 25 ítems de verificación (archivo perdido en la limpieza del 10-oct) |
| 0b | Sonnet (inventario) | repo + CLAUDE.md | activos, mapa cifra→requisito, errores a no propagar (archivo perdido) |
| 1 | Opus (planificador) | prompt v1 | plan v1 (460 líneas): reformula el detector a "pico en 30 min"; mockup HTML de 3 pantallas |
| 1 | Sonnet (revisor) | plan v1 + rúbrica A–I | REVISAR: líneas base de paja (una regla de nivel ya anticipa mucho); mockup no mínimo; ruta del árbol de otro modelo; calibración circular |
| 2 | Opus (planificador) | prompt v2 = v1 + 10 reglas + modelo supervisado en todo caso + documento para decidir | plan v2 (379 líneas, 6.731 palabras): líneas base reales; mockup 1 página, 4 tarjetas; N2 condicionado |
| 2 | Sonnet (revisor) | plan v2 | APTO condicionado: "nivel + horario" es un modelo entrenado; ilegible para decidir; dos semáforos en el mockup |
| 3 (intento 1) | Opus | prompt v3 | falló por límite de sesión de la API (3-oct) |
| — | — | — | 10-oct: limpieza del directorio temporal borró planes, críticas y prompts. Restaurados desde el contexto del orquestador el 21-oct: plan_v2.md (textual), critica_v2.md (secciones 2, 6, 7), reglas_vigentes.md (reglas 1–19 + marco) |
| 3 | Workflow (9 agentes, 21-oct): Opus redacta → 4 revisores Sonnet (cumplimiento, compañera del grupo, cifras/fugas, enunciado/Shiro) → Opus corrige → Sonnet re-verifica, 2 vueltas | plan_v2 + critica_v2 + reglas_vigentes | v3 inicial 4.458 palabras; los 4 revisores: REVISAR (17 MAYOR, 29 MENOR, 0 BLOQUEANTE); vuelta 1: 46 hallazgos aplicados o parciales, 0 descartados; re-verificación: 9 problemas; vuelta 2: 9 aplicados; re-verificación final **OK** con 6 menores |
| 3 (cierre) | Orquestador | 6 menores de la re-verificación + titular "1 de cada 3" → "3 de cada 10" (el rango es 27–32 %) | PLAN_DESARROLLO.md (≈ 4.500 palabras, 182 líneas) |

## Hallazgos principales de la ronda 3 (ya corregidos)
- La regla que elige el modelo (validación) y la tabla de casos (prueba) podían contradecirse → margen único de 10 puntos, casos sin huecos, discrepancia escrita dentro de B.
- El titular "1 de cada 3" exageraba el extremo bajo del rango y mezclaba dos tiempos en rojo → "3 de cada 10", costo atado a 100–120 min/día.
- El mínimo del mockup dejaba fuera el antes/después del ejemplo de classroom → antes/después dentro de la tarjeta 2 (pasada 1) y en "nunca se recorta".
- El orden de recorte empezaba por el mockup (2,5) → ahora empieza por la presentación (0,5) y el informe.
- Exactitud y F1 del póster quedarán por debajo de "todo verde" a propósito → frase escrita de antemano.
- La portada perdió la salvedad de que Guardian es una fase opcional del proyecto → restituida.

## Ejecución

| Hito | Agentes | Resultado |
|---|---|---|
| H0 (21-oct) | — | El usuario aprueba las 4 decisiones (Guardian; titular honesto; página web sin instalar nada; solo kWh) y pide arrancar con el cuaderno |
| H1a (21-oct) | Workflow: Opus construye → 3 revisores Sonnet (fidelidad/fuga, réplica independiente desde el CSV, exportación/narrativa) → Opus corrige → Sonnet re-verifica | `generadores/construir_cuaderno.py` → `Parcial2_Guardian.ipynb` (38 celdas, ≈ 12 s, determinista), `cifras.json` (645 nuevas + 128 heredadas), `mockup/datos_mockup.json`. 21/21 anclas; 60/60 heredadas coinciden con la tabla del proyecto. Revisores: fidelidad APTO (6 menores), réplica APTO (429 cifras reproducidas, 8 menores), exportación REVISAR (6 mayores: residuos de nombres de herramienta, doble redondeo de una heredada, heredadas aleatorias sin par temporal, cifras faltantes para póster, azar a otro tiempo en rojo, explicador que contradecía un color). Corrector: 25 aplicados/parciales, 0 descartados |

| H1b + H3 (21-oct) | Workflow: Opus (ajustes + figuras) → Opus (mockup pasada 1) → 3 revisores Sonnet (figuras, cálculos del mockup reimplementados en Python, enunciado/experiencia) → Opus corrige → Sonnet re-verifica | Cuaderno de 44 celdas (≈ 28 s, determinista, PNG idénticos byte a byte); figuras G1–G6 a 300 dpi; `mockup/plantilla.html` → `Mockup_Shiro_Guardian.html` (tarjetas 1–2, antes/después, "Verificación: OK"); capturas MG1–MG3. Revisores: los tres REVISAR (9 mayores: el antes/después decía "pasó a rojo a las 08:10" cuando el rojo empezó a las 08:00; figuras ilegibles reducidas al informe; un par aleatoria/temporal de G6 mezclaba modelos; navegación que atrapaba en una tarjeta; umbral con jerga; sin rango junto al titular; faltaba el rótulo de maqueta). Corrector: 25 aplicados/parciales, 0 descartados. Re-verificación: OK, 5 menores. Comprobado además en el navegador: OK, sin errores de consola; deslizador 7,66 % → 12 % lleva los picos avisados de 28 a 37 de 84 |

| Cierre del 21-oct | Orquestador | `CLAUDE.md` §6 corregido (F1 0,47 a umbral 0,40; el 0,40 se eligió en prueba); escudo oficial descargado de Wikimedia Commons (SVG + PNG 2400 px) en `recursos/`; commit `f7c5328` llevado a `master` por avance directo. Decisiones del usuario: mockup se queda con 2 tarjetas; guion de sustentación con reparto; póster A1 vertical PDF; autores confirmados; enunciado vigente = PDF "26-1" subido a Classroom; sin fecha, con sustentación corta |

| H5–H8 (21-oct) | Workflow (11 agentes): Opus ajusta el mockup → tres líneas en paralelo (informe · póster · presentación + guion), cada una Opus construye → Sonnet revisa → Opus corrige → Opus integra (`verificar.py`, consistencia, regenera todo) | Informe APA (19 págs., 12 de cuerpo), póster A1, presentación de 7 diapositivas con notas y guion de sustentación de 10 min. Revisores: informe REVISAR (3 mayores: dos bases de "mismo tiempo en rojo" sin explicar; afirmar que la prueba se usó una sola vez cuando el piso se fijó tras indicios de la prueba), póster REVISAR (5 mayores: legibilidad, casos críticos sin texto, variables sin nombrar, métricas sin interpretar, titular ambiguo), presentación + guion REVISAR (3 mayores: la misma ambigüedad de presupuestos, una cifra del deslizador que no coincidía con la página, la misma afirmación sobre el piso). Todo corregido; la integración añadió al cuaderno las cifras que faltaban (deslizador a 12 % y 5 %, fracciones del titular, reglas del explicador…) y alineó el relato entre piezas. `verificar.py`: TODO PASA (277 números verificados contra `cifras.json`) |
| Póster legible (21-oct) | Opus + Sonnet | Figuras propias del póster (`POSTER_G1/G2/G3/G5`) a tamaño físico con letra de 18 pt y cifras de 22 pt; comprobación automática en el cuaderno. Revisor: APTO (32 rótulos medidos a 18,0 ± 0,3 pt) |

**Ajustes de H1b:** la variación de semillas de los bosques (G1 25,5–31,4 %, G4 29,4–39,2 % en validación) no cambia el elegido, el complejo ni el caso. El optimismo de la calibración se concentra en el decil más alto (31 en validación frente a 20 en prueba); la página muestra el rango. El amarillo del caso crítico 1 en s−1 está a 0,0001 del corte: la narrativa se ancla en s−2.

**Menores pendientes para la pasada 2:** la autoverificación no cubre la frase del antes/después; el deslizador no vuelve exactamente al valor por defecto (7,6638 %); el subtítulo de G6 menciona una corrección interna; MG3 es muy alta para una página del informe; un comentario obsoleto en el generador.

**Resultado del punto de control H2:** caso **B**. Elegido en validación: **G0** (modelo mínimo de dos variables). Titular desplegado: **28 de 84 picos (33,3 %) avisados con ≥ 20 min**, con 127 min/día en rojo (9,68 % de la calma), 3,10 avisos/día y 61,2 % de avisos falsos. Regla de nivel al mismo rojo: 21 de 84 (25,0 %); diferencia +8,3 puntos (IC 95 % −1,2 a 18,4). Azar a ese rojo: 18,4 %. Ningún modelo complejo se distingue de G0 (G5 +1,2, IC −11,1 a 12,9).

**Hallazgos que cambian el relato del plan:**
- El detector del parcial 1 sí avisaba antes del inicio en 35 de 84 picos (33 con ≥ 20 min), pero en 23 la alerta ya venía encendida (alertas de 100 min de media, 15,3 % de la calma en alerta). Con el mismo tiempo en rojo que Guardian anticipa 26,2 % a ≥ 20 min, comparable a G0. El informe debe decir "su 86,9 % no medía anticipación" en vez de "nunca avisaba antes".
- Los bosques derivan fuerte en mayo con los cortes de validación (G1 en rojo el 40,7 % de la calma, G4 el 34,4 %); G0 (9,7 %) y G5 (7,5 %) son los únicos que se mantienen cerca del presupuesto.
- La validación es generosa (G0: 41 % en validación frente a 27 % en prueba a mismo rojo); la calibración que pasa al MDP usa una versión monótona y se declara el optimismo.
- Gemelo frente a persistencia: MAE 28,17 vs 26,64 Wh (pierde), RMSE 60,54 vs 66,44 (gana); ambos subestiman los picos (sesgo −101 vs −59 Wh en lecturas > 200 Wh).

## Verificaciones hechas por el orquestador
- F1 por lectura del RF + retardos a umbral 0,40 = 0,47 (Parcial_Corte1.ipynb c.38); el 0,580 de CLAUDE.md §6 es a 0,5 (c.22).
- El barrido de umbrales de c.38 se hace sobre `Xb` (prueba) y c.40 elige 0,40 con esa tabla → viola §4.3.
