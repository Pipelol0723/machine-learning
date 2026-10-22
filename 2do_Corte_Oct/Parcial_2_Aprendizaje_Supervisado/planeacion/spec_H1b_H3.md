# Especificación — hitos H1b (figuras + ajustes) y H3 (mockup, pasada 1)

> Deriva de `../PLAN_DESARROLLO.md` (§7 mockup, §8 informe, §9 póster, §11 hitos) y de los resultados del hito H1a
> (`../cifras.json`, `../mockup/datos_mockup.json`, `iteraciones.md`). Donde discrepe del plan, manda el plan.
> Resultado vigente: **caso B**, modelo elegido **G0** (mínimo de dos variables, exportable), titular 28 de 84 picos
> con ≥ 20 min (33,3 %) a 127 min/día en rojo, regla de nivel 21 de 84.

## A. Ajustes al generador (`generadores/construir_cuaderno.py`) — antes de todo lo demás
Toda corrección se hace en el generador (nunca editando el .ipynb a mano) y se re-ejecuta; anclas en verde y determinismo
(dos ejecuciones, `cifras.json` idéntico sin `meta`).
1. **Calibración:** cuantificar el optimismo de la validación en los deciles altos. Añadir a `datos_mockup.json › calibracion`
   un campo con la tasa de prueba por decil visible como contraste (p. ej. `mostrar_rango: [prueba, validación]` en los
   deciles donde difieren más de 5 puntos) y ampliar la nota con la cifra. Claves equivalentes en `cifras.json`.
2. **Caso crítico 1:** exportar `margen_corte_amarillo` por lectura de la ventana `[s−3, s−1]` y `ventana_fragil: true`
   si algún margen < 0,01. La narrativa del caso se ancla en el momento `s−2`.
3. **Ruido de los bosques:** medir G1 y G4 en validación con 5 semillas (42–46) y registrar media, mínimo y máximo; en el
   cuaderno, una línea que declare la variación y si cambia la selección o el "complejo" del caso (no debe cambiar la
   decisión tomada con la semilla 42; si la cambiara, reportarlo sin ocultarlo).
4. **Inyección del mockup:** la última celda lee `mockup/plantilla.html` (si existe), reemplaza el marcador
   `/*__DATOS__*/` por el contenido de `datos_mockup.json` y escribe `Mockup_Shiro_Guardian.html` en la carpeta del
   parcial. Si la plantilla no existe, lo dice y sigue.

## B. Figuras (H1b) — sección nueva del cuaderno "Figuras para el informe y el póster"
Una sola exportación por figura, **PNG a 300 dpi**, en `figuras/`, con tamaño pensado para el póster A1 (texto ≥ 9 pt al
tamaño de exportación, legible reducido al informe). Fondo claro; colores del semáforo: verde `#188038`, ámbar `#e8710a`,
rojo `#d93025`; gris neutro para referencias; azul `#1a73e8` solo para el pronóstico del gemelo. Títulos y ejes en
español es-CO; cada figura dice qué componente de Shiro informa (subtítulo corto). Ninguna cifra tecleada: todo de las
variables del cuaderno / `cifras.json`. Registrar en `cifras.json` las rutas y una descripción por figura.
- **G1 — Un día del mes nunca visto, con y sin Guardian:** el día del antes/después (`ejemplo_dia`): consumo cada 10 min,
  picos sombreados, tira de semáforo debajo (verde/ámbar/rojo anticipado; rojo en curso con otro trazo), primer rojo y
  minutos de antelación anotados. Sin curva "con Shiro" (no hay modelo del efecto de la acción).
- **G2 — Picos avisados con margen:** % de los 84 picos con ≥ 10, ≥ 20 y ≥ 30 min para el modelo elegido y la regla de
  nivel (mismo tiempo en rojo), con barras de rango plausible (IC 95 % bootstrap por día) y la línea de azar.
- **G3 — Cuánto molesta cada color:** tiempo en cada color (min/día) y acierto por color (de cada 100 lecturas de ese
  color, cuántas precedieron un pico), en prueba con cortes de validación; marca del presupuesto 7,66 %.
- **G4 — La regla que explica el rojo:** el árbol explicador de profundidad 3 dibujado como reglas legibles → acción
  ("consumo actual > X Wh y hora con picos frecuentes → rojo: no encender cargas grandes"), con su fidelidad.
- **G5 — Dos casos críticos:** pico no anticipado con más energía y aviso falso más largo: consumo ±2 h, colores, puntaje
  y cortes; anotación de qué faltó (el aparato) y qué costó (minutos de rojo inútil).
- **G6 — Evolución de modelos (póster):** línea de tiempo Taller 2 → Taller 3 → Parcial 1 → C2-Taller 1 → Parcial 2
  con la decisión de cada hito y su cifra en par aleatoria/temporal (bloque `heredadas`), y la pregunta que cambió en el
  Parcial 2 (reconocer → anticipar).

## C. Mockup, pasada 1 (H3) — `mockup/plantilla.html` → `Mockup_Shiro_Guardian.html`
**Restricciones duras:** un solo archivo HTML + CSS + JS, sin librerías, sin red, sin fuentes externas (fuentes del
sistema); abre con doble clic. ≈ 320 líneas de plantilla en esta pasada (tarjetas 1–2 + antes/después + autoverificación);
tarjetas 3–4 quedan para la pasada 2 (dejar el hueco previsto en el diseño, sin implementarlas). **Ningún número de
resultado escrito en la plantilla**: todo se lee del objeto de datos inyectado. Español llano, es-CO.
**Estética:** la consola oscura del parcial 1 (fondo `#0d0f13`, verde `#188038`, ámbar `#e8710a`, rojo `#d93025`), con
contraste legible. Encabezado: "Shiro Guardian — semáforo de la próxima media hora" y la promesa: "Shiro propone, la
persona decide".

**Tarjeta 1 — ¿Y si…? (nunca se recorta; anclas `#t1`)**
- Entradas agrupadas: *Lo que mira Guardian* (consumo actual en Wh, hora, laborable/fin de semana) y *Lo que además usa el
  pronóstico* (`lights`, T2, RH_2, T_out). Botones para cargar los 5 momentos reales (`momentos_tarjeta1`) con su fecha.
- **En vivo, modelo real:** el puntaje de **G0** en JS (ECDF del nivel + ECDF de la frecuencia horaria por hora ×
  laborable/fin de semana, de las tablas exportadas) → color con los cortes vigentes (los mismos de la tarjeta 2) →
  "de cada 100 momentos así, X precedieron un pico en la media hora siguiente" (calibración monótona; mostrar el rango
  frente a la prueba donde la validación es optimista) → acción sugerida (verde: nada; ámbar: revisar antes de encender
  cargas grandes; rojo: propuesta "no encender cargas grandes en los próximos 30 min" con aprobar/ajustar/rechazar,
  sin ejecutar nada).
- **Consumo esperado en 10 min (G3c)**, en una barra **azul** con marcas en 60 y 200 Wh, con su error típico
  ("± MAE") y la advertencia de que subestima los picos (sesgo en lecturas > 200 Wh). Nunca usa los colores del semáforo.
- La regla del explicador como "por qué" debajo del color, rotulada como aproximación si no coincide.

**Tarjeta 2 — El semáforo del mes nunca visto (`#t2`)**
- Controles: presupuesto de rojo y de amarillo (deslizadores en % de la calma, por defecto `r`); selector de día.
- **En vivo:** cortes = cuantiles de los puntajes de validación exportados; colores de las 3.946 lecturas; agrupación de
  avisos (`gap=3`); picos con ≥ 10/20/30 min, avisos/día, duración media, % útiles, rojo realizado (min/día), acierto
  por color; la regla de nivel al mismo tiempo en rojo, en cifras (sin colores propios).
- **Tira del día** elegido: consumo y colores, picos marcados, minutos de antelación.
- **Antes / después** (dentro de la tarjeta, núcleo): "Antes: el hogar se entera por la factura o cuando el pico ya
  empezó. Después: a las HH:MM el semáforo pasó a rojo, K min antes del pico…" construido desde los datos del día de
  ejemplo; y la energía de exceso > 200 Wh de los picos avisados con margen, en kWh, con el rótulo **SIMULADO** para
  cualquier parte que dependa de supuestos (% evitable y % aceptado como deslizadores, por defecto 0 para que lo medido
  y lo simulado no se mezclen hasta que el usuario los mueva). Solo kWh, sin pesos.
**Autoverificación (≤ 20 líneas de JS):** al cargar, con los valores por defecto, compara las métricas de la tarjeta 2 y el
color de los 5 momentos (tarjeta 1 frente a tarjeta 2) con los esperados exportados por el cuaderno y escribe al pie
"Verificación: OK" o "Verificación: DIFIERE (…)". Debe dar OK.
**Anclas:** `#t1`, `#t2` muestran solo esa tarjeta (para capturas); sin anclas se ve la página completa.
**Capturas:** Edge headless (`msedge --headless=new --screenshot --window-size=… --force-device-scale-factor=2`) de la
página completa, `#t1` y `#t2` → `figuras/MG1.png` (página), `MG2.png` (tarjeta 1), `MG3.png` (tarjeta 2). Comprobar con
`msedge --headless=new --dump-dom` que el pie dice "Verificación: OK" y que la consola no tiene errores.

## D. Criterios de aceptación de esta etapa
1. Cuaderno: corre limpio, 21/21 anclas, determinista; figuras G1–G6 a 300 dpi; los 4 ajustes de §A presentes.
2. Mockup: abre sin red; "Verificación: OK"; mover el presupuesto de rojo cambia las métricas en el sentido esperado
   (más rojo → más picos avisados y más avisos/día); el color de la tarjeta 1 para cada momento real coincide con la
   tarjeta 2; ningún número de resultado en la plantilla.
3. Sin residuos ("TODO", "[por calcular]", nombres de herramientas) en cuaderno, JSON, HTML y figuras.
