# Especificación — hitos H5–H8: informe, póster, presentación, guion y verificación final

> Deriva de `../PLAN_DESARROLLO.md` (§6 lenguaje, §8 informe, §9 presentación y póster, §12 verificación) y de los
> ajustes del usuario del 21-oct: **el mockup se queda con 2 tarjetas** (sin pasada 2), **guion de sustentación con
> reparto**, **póster A1 vertical en PDF**, autores confirmados. Detalle fino adicional en `plan_v2_detalle.md`
> (§8 APA, §9 Parte 3, §10 póster). Donde discrepe, manda el plan y luego esta especificación.

## 0. Reglas comunes a todas las piezas
- **Fuente única:** toda cifra sale de `../cifras.json` (campo `texto` en es-CO) leída por el generador. Nada tecleado a
  mano salvo parámetros de definición (200 Wh, ≥ 20 min, 10 puntos…) y fechas del dataset. Si falta una cifra, se añade
  al cuaderno (vía `generadores/construir_cuaderno.py`), nunca se calcula a mano en el documento.
- **Generadores versionados** en `generadores/`: `generar_informe.py`, `generar_poster.py`, `generar_presentacion.py`,
  `generar_guion.py`, `verificar.py`. Cada uno se ejecuta con `C:\Users\pipel\venvs\ml\Scripts\python.exe` y regenera su
  pieza desde cero.
- **PDF por COM vía PowerShell** (pywin32 no está instalado): Word `Word.Application` → `SaveAs2(..., 17)` o
  `ExportAsFixedFormat`; PowerPoint `PowerPoint.Application` → `SaveAs(..., 32)`. **Candado obligatorio** antes de usar
  Office: crear en exclusiva `C:\Users\pipel\AppData\Local\Temp\shiro_office.lock` (si existe, esperar 15 s y reintentar,
  máximo 20 min); borrarlo al terminar, también si hay error. Cerrar siempre la aplicación (`Quit()`).
- **Revisión visual obligatoria:** renderizar el PDF a PNG con `pymupdf` y mirar cada página/diapositiva con la
  herramienta Read antes de dar la pieza por terminada.
- **Shiro primero (CLAUDE.md §0):** cada pieza abre con la necesidad de Shiro Guardian y cada resultado dice qué cambia
  en Shiro. Prueba rápida: si al tachar "Shiro" y "Guardian" el texto sigue completo, se reescribe.
- **Honestidad:** el titular va siempre con su costo (127 min/día en rojo, 61 % de avisos falsos) y con la comparación
  frente a la regla del medidor y su rango plausible; "no se distingue del azar" cuando el IC incluye 0. Lo simulado se
  rotula **SIMULADO** y va separado de lo medido. Solo kWh (sin pesos).
- **Sin residuos:** nada de "TODO", "[por calcular]", `{{`, nombres de herramientas o de asistentes, referencias a
  "el plan", "hito", "spec", "CLAUDE.md" o IDs internos (G0–G5 se pueden usar solo en el apéndice técnico y en el póster
  con su nombre llano al lado: "modelo mínimo de dos variables (G0)").
- **Autores (en este orden):** Jose Leonardo Diazgranados, Sofía Londoño, Andrés Felipe Céspedes Rondón, Alex Duran.
  Universidad Sergio Arboleda · Aprendizaje de Máquina · Docente: Hernán Darío Cruz Bueno · 2.º corte, 2026-2.
- **Escudo:** `recursos/escudo_universidad_sergio_arboleda.png` (transparente, 2400 × 1320) en el póster y en la portada
  de la presentación. En el informe APA no va (portada APA de estudiante).
- Idioma español es-CO (coma decimal, punto de miles, espacio antes de %).

## 1. Relato común (las cuatro piezas cuentan lo mismo)
1. **Necesidad de Shiro:** Guardian debe avisar *antes* de un pico (> 200 Wh en 10 min) para que la persona alcance a
   aplazar una carga; un aviso con el pico ya empezado no deja hacer nada. Decide qué probabilidad entra al estado del
   MDP del 3.er corte y si Guardian notifica (propuesta en `ApprovalGate`: la persona aprueba, ajusta o rechaza).
2. **Corrección honesta del parcial 1:** su "86,9 % de picos detectados" contaba avisos que tocaban picos ya en curso
   (alertas de 100 min de media; el 15,3 % de la calma en alerta) y su umbral 0,40 se eligió mirando el mes de prueba.
   No medía anticipación. Con el mismo tiempo en rojo que Guardian, anticipa 26,2 % a ≥ 20 min (claves `n1c_*`).
3. **Cómo se eligió el modelo:** 6 candidatos supervisados (del mínimo de 2 variables a bosques y logísticas de 36),
   elegidos en validación con un piso de utilidad y preferencia por lo simple; el mes de prueba se usa una sola vez.
4. **Resultado (caso B):** el **modelo mínimo de dos variables** (consumo actual + frecuencia histórica de picos a esa hora)
   avisa **28 de 84 picos (33,3 %) con al menos dos lecturas de antelación**, con 127 min/día en rojo, 3,1 avisos/día y
   61,2 % de avisos falsos. La regla del medidor, con el mismo tiempo en rojo: 21 de 84 (+8,3 puntos; rango −1,2 a
   18,4: no concluyente con 84 picos). Azar: 18,4 %. Ningún modelo complejo se distingue del mínimo.
5. **Lo que se aprendió:** el gemelo se equivoca casi lo mismo que repetir la última lectura y subestima los picos; los
   bosques derivan en mayo (rojo 40,7 % y 34,4 % de la calma con cortes de abril); la validación es optimista (41 % frente a
   27 %); la variable que falta es *qué aparato se enciende*. → Recalibración mensual, revalidar con otra vivienda.
6. **Qué cambia en Shiro:** la probabilidad calibrada (decil, con su rango) entra al estado del MDP; Guardian notifica
   con propuesta aprobable; el gemelo es la función de transición pero no el semáforo; recalibración mensual con gris.

## 2. Informe ejecutivo APA (Parte 1, 1,0) — `Informe_Ejecutivo_Shiro_Guardian.docx` + `.pdf`
- **Formato APA 7 de estudiante:** portada (título en negrita centrado en la mitad superior; autores; Universidad Sergio
  Arboleda; Aprendizaje de Máquina; docente; fecha); Calibri 11; interlineado doble; márgenes 2,54 cm; número de página
  arriba a la derecha (campo `PAGE`); sangría de primera línea 1,27 cm; estilos reales `Heading 1–3` con formato APA
  (1 centrado negrita, 2 izquierda negrita, 3 izquierda negrita cursiva); **Tabla n / Figura n** en negrita arriba, título
  en cursiva debajo del número, nota "*Nota.* …" debajo; tablas sin bordes verticales; citas autor-año en el texto
  ("Candanedo et al. (2017)"); referencias en página aparte con sangría francesa.
- **Extensión:** ≤ 12 páginas de cuerpo a doble espacio, más portada, resumen, referencias y Apéndices A (ficha técnica:
  aquí sí F1, exactitud, AUC con analogía, R², pares aleatoria/temporal heredados) y B (glosario en lenguaje llano).
- **Estructura** (cada sección abre con la necesidad de Shiro y cierra con "qué cambia en Shiro"):
  - *Resumen* (1 pág.): pregunta, respuesta (frase del caso B), 3–4 cifras, decisión para Shiro.
  - *1. Problema real del sector*: el hogar no sabe que viene un pico; Guardian; qué decisión depende del resultado;
    contexto sectorial solo con fuente verificable (si no se consigue, con los datos del propio hogar y Candanedo et al.).
    Fig. 1 = G1.
  - *2. Modelo elegido y justificación*: datos y calidad en un párrafo; las dos familias (anticipador y gemelo) con
    analogía; validación temporal ("examen con un mes que nunca vio"); listones (regla del medidor, azar); por qué no
    los complejos, contado como decisiones. Tabla 1 = línea de tiempo de decisiones (sin métricas lado a lado).
  - *3. Resultados clave*: 3.1 escenario de uso (frase plantilla del plan §6 con `{min_dia}`, `{n20}`, `{m20}`);
    3.2 antes/después (día de ejemplo, inicio real del rojo); 3.3 reglas y patrones → acción (explicador, Tabla 2 regla →
    acción; Fig. 4 = G4); 3.4 semáforo y scorecard (Fig. 3 = G3; tablero de 4 indicadores sin colores inventados);
    3.5 impacto: medido (kWh de exceso en picos avisados) y **SIMULADO** (tabla de escenarios bajo/medio/alto con sus
    supuestos, Tabla 3). Fig. 2 = G2. Fig. 5 = captura de la tarjeta 1 del mockup (MG2).
  - *4. Conclusiones y decisiones que permite tomar*: por actor (hogar, equipo de Shiro, diseño de Shiro).
  - *5. Limitaciones y consideraciones éticas*: una vivienda belga de invierno-primavera; deriva; 84 picos; corrección del
    parcial 1; quién paga cada error y su mitigación (Tabla 4: pico no avisado / falsa alarma / deriva / privacidad);
    privacidad (el consumo revela ocupación; Ley 1581 de 2012); "Shiro propone, la persona decide"; los dos casos
    críticos (Fig. 6 = G5).
  - *6. Recomendaciones finales*: 5 accionables con su porqué.
- **Prohibido en el cuerpo** (antes de Referencias): "F1", "AUC", "R²", "log-loss", "accuracy", "exactitud",
  comparativas tipo "A 0,81 vs B 0,79", R² como "precisión", cifras de la partición aleatoria sin su par temporal,
  "a tiempo" sin minutos, "20 minutos" sin "al menos dos lecturas", "ahorro" sin supuestos, causalidad desde importancias.
- **Referencias** (verificar cada DOI abriendo `https://doi.org/<doi>`; si no se puede verificar, omitir el DOI, no
  inventarlo): Candanedo, Feldheim y Deramaix (2017), *Energy and Buildings*, 140, 81–97; el conjunto de datos de UCI
  (Appliances Energy Prediction); Breiman (2001) *Machine Learning*, 45(1); Pedregosa et al. (2011) *JMLR*, 12; Efron y
  Tibshirani (1993) *An introduction to the bootstrap*; APA (2020) *Publication manual* 7.ª ed.; Ley 1581 de 2012.
- Figuras: insertar a ancho de columna (≈ 16 cm). Si una figura queda ilegible a ese ancho (texto < 7 pt), usar la
  versión para informe que exporte el cuaderno o recortarla; nunca deformarla.

## 3. Póster académico (Parte 4, 1,0) — `Poster_Shiro_Guardian.pptx` + `.pdf` + `.png`
- **A1 vertical** (594 × 841 mm), una sola diapositiva python-pptx editable; PDF por PowerPoint; PNG de vista previa
  (≈ 2.400 px de alto, renderizado del PDF con pymupdf).
- Fondo claro con acentos de la paleta del semáforo; cuerpo ≥ 24 pt, títulos de sección ≥ 40 pt, título ≥ 72 pt;
  ≤ 500 palabras; mucho gráfico, poco texto. Escudo arriba a la izquierda; título como pregunta ("¿Cuánto antes se puede
  avisar de un pico de consumo? Modelos supervisados para Shiro Guardian"); autores, universidad, curso, docente.
- **Secciones en el orden del enunciado:** Problema y contexto (G1) · Dataset y características (19.735 lecturas,
  29 variables, 137 días, 0 faltantes; calidad: una vivienda sin verano, `rv1`/`rv2` excluidas, consumo múltiplo de
  10 Wh, T6/RH_6 exteriores, 2 días incompletos) · Modelos aplicados y evolución (G6) · Modelo final y resultados (G2, G3;
  aquí sí: el gemelo con MAE y RMSE frente a repetir la última lectura; el semáforo con exactitud y F1 frente a "todo
  verde", con la frase "el semáforo cuesta exactitud a propósito…") · Errores y reflexiones éticas (G5 + 2 riesgos de
  automatizar mal y su mitigación) · Mockup (MG1 o MG2 + MG3 recortada) · Conclusión y futuro (qué aprendimos, qué
  mejoraríamos, qué haría falta para producción).
- Revisar legibilidad: renderizar a escala del 25 % y comprobar que el título y las cifras clave se leen.

## 4. Presentación de implementación (Parte 3, 0,5) — `Implementacion_Shiro_Guardian.pptx` + `.pdf`
- 7 diapositivas 13,33 × 7,5 in con **notas del orador** en todas; estética de la consola del deck del 2.º corte
  (`2do_Corte_Oct/Presentacion_Talleres_C2/Presentacion_Talleres_C2_Shiro.pptx`: fondo `#0D0F13`, tarjetas `#151920`/
  `#232833`, texto `#E6E9EF`/`#C9D1DE`/`#9AA3B2`, acentos `#7BD992`/`#188038` y `#E8710A`; Segoe UI, Segoe UI Semibold y
  Consolas). Escudo en la portada.
- **Organización real = Shiro como producto propio** (el equipo de Shiro lo despliega en hogares). Diapositivas:
  1. Portada. 2. Guardian como producto y arquitectura: medidor y sensores → `iot-bridge` (`IDeviceModule`,
  `DeviceRegistry`; hoy transporte en proceso, luego MQTT / Home Assistant) → servicio Python de modelos → semáforo +
  `ApprovalGate` → app; eventos `iot:reading`, `iot:anomaly-detected`, `iot:action-suggested`; qué promete (≈ 3 de cada
  10 picos con margen) y qué no (no actúa sin aprobación; no ahorra solo). 3. Datos y privacidad: lectura cada 10 min,
  ventana de 1 h en memoria, proceso local; solo salen indicadores agregados con consentimiento; datos mínimos
  (medidor + hora; el modelo elegido solo necesita dos variables). 4. Roles (tabla RACI): titular que aprueba,
  convivientes; equipo Shiro: ciencia de datos (recalibración mensual, auditoría), plataforma, soporte, privacidad.
  5. Ciclo mensual y hogar nuevo: recalibrar cortes cada mes (la deriva medida lo exige), tablero de 4 indicadores,
  primer mes en "modo aprendizaje" (gris, sin notificaciones) porque el modelo es de una sola vivienda. 6. Capacitación al
  usuario: recorrido por el semáforo y la propuesta (usando el mockup), guía de una página, video corto, preguntas
  frecuentes; cómo se mide el éxito (% de propuestas respondidas, ajustes del deslizador). 7. Piloto y riesgos: fases
  Twin → Guardian → Home sin fechas, criterios de salida, riesgos y mitigación.
- Verificación de arquitectura contra `02_Propuesta_Shiro_IoT.docx` y `03_Plan_Unificado_Shiro_Twin_a_Home.docx` (no
  inventar componentes de Shiro que esos documentos no nombren).

## 5. Guion de sustentación — `Guion_Sustentacion_Shiro_Guardian.docx` + `.pdf`
- Estilo del guion del video del 2.º corte (`Presentacion_Talleres_C2/Guion_Video_Talleres_C2.docx`): portada corta,
  "cómo usar este guion", tabla de bloques (quién, qué se muestra, minutos) y luego el texto por bloque.
- **Duración objetivo: 10 minutos** + preguntas. **Reparto propuesto** (editable): Jose — apertura (necesidad de Shiro y
  la pregunta) y cierre; Sofía — datos y cómo se eligió el modelo (validación, listones); Andrés — resultados y **demo
  del mockup** (el mockup vale la mitad de la nota: el bloque más cuidado); Alex — ética, limitaciones y propuesta de
  implementación (Parte 3). Frase de pase entre expositores.
- **Qué se muestra en cada momento:** póster (PDF), mockup (HTML) o diapositivas de implementación. Para la demo, el
  recorrido exacto de clics con lo que debe verse: cargar "30-abr-2016 09:10 · primer rojo de un aviso útil" → ROJO y
  la propuesta; cargar el momento verde; cambiar el consumo a mano y ver el color; mover el deslizador de rojo de 7,66 % a
  12 % → los picos avisados pasan de 28 a 37 de 84 y suben los avisos/día; antes/después del día de ejemplo; pie
  "Verificación: OK". Todas esas cifras del guion salen de `cifras.json`/`datos_mockup.json` (no tecleadas).
- **Preguntas probables del profesor con respuesta corta** (8–10): ¿por qué el modelo más simple y no Random Forest?;
  ¿33 % es bueno?; ¿por qué tantas falsas alarmas?; ¿qué es validación vs prueba?; ¿por qué no el 86,9 % del parcial 1?;
  ¿cómo saben que no hay fuga de información?; ¿funcionaría en otra casa?; ¿qué pasa con la privacidad?; ¿qué haría falta
  para producción?; ¿dónde está el aprendizaje supervisado si gana un modelo de dos variables?
- "Plan B" si falla el mockup en vivo: mostrar las capturas MG1–MG3 del póster/informe.

## 6. Mockup: 5 ajustes menores (no se añaden tarjetas)
1. La autoverificación compara también la frase del antes/después (inicio real del rojo y minutos) con lo exportado.
2. Se puede volver al presupuesto por defecto exacto (botón "Restablecer" o paso del deslizador que lo incluya).
3. El subtítulo de G6 no menciona correcciones internas ("tabla del proyecto"); queda limpio para el póster.
4. Captura MG3 apta para el informe (versión recortada o más ancha, que quepa en una página a ≈ 16 cm de ancho).
5. Se elimina el comentario obsoleto del generador con la frase antigua del antes/después.
Además: el cuaderno exporta a `cifras.json` las claves del **impacto SIMULADO** (escenarios bajo / medio / alto =
exceso de kWh en picos avisados con ≥ 20 min × % evitable × % de propuestas aceptadas, con supuestos 10 %/50 %,
25 %/70 % y 50 %/90 %, declarados como supuestos) para la Tabla 3 del informe.
Re-ejecutar el generador: 21/21 anclas, determinismo, "Verificación: OK" en Edge headless, capturas revisadas.

## 7. Verificación final (H8) — `generadores/verificar.py`
- (i) Ningún `{{`, "[por calcular]", "TODO", "Claude", "Anthropic", "ChatGPT", "IA generativa", "CLAUDE.md", "spec",
  "hito" en docx (con tablas, encabezados y pies), pptx (con notas), HTML y guion. (ii) En el cuerpo del informe (antes de
  Referencias) 0 apariciones de "F1", "AUC", "R²", "log-loss", "accuracy", "exactitud". (iii) Toda cifra de partición
  aleatoria va con su par temporal. (iv) "a tiempo" y "antes del pico" solo en frases con "min"; "20 minutos" con "al
  menos dos lecturas". (v) **Consistencia de cifras:** el titular (28 de 84; 33,3 %), la regla (21 de 84), el costo
  (127 min/día; 61,2 %), el azar (18,4 %) y el rango (−1,2 a 18,4) aparecen idénticos en informe, póster, presentación y
  guion; extraer los números con decimales de cada pieza y comprobar que cada uno está en `cifras.json` (`texto`) o en
  una lista blanca justificada (años, fechas, numeración, parámetros de definición). Reportar huérfanos.
- Salida: `verificar.py` imprime un informe y termina con código 0 solo si todo pasa.
