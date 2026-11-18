# Plan: Taller 3 del Corte 3 (de Q-learning a DQN), el agente de Shiro con estado continuo

*Redactado el 2026-11-12. **Classroom: «C3 Taller3», publicado el 6-nov, vence MAÑANA (13-nov).** Sin texto propio: el
enunciado está en el PDF. **Formato de entrega: VIDEO** con las tres partes.*

## 0. Material (`Documentacion/`)

| Archivo | Qué es |
|---|---|
| `ML TALLER3 C3 DQN.pdf` | **Enunciado** (1 p.): Parte 1 investigación (30 %), Parte 2 aplicación al sector (30 %), Parte 3 prototipo (40 %): «evolucionar el prototipo de los talleres 1 y 2 del corte». Entrega en video. |
| `Ejemplo Taller_DQN_Investigacion_Completo.docx.pdf` | Ejemplo de otro grupo (2025, seguridad vial, 18 pp.): responde las partes 1 y 2 en texto. **No trae prototipo con resultados.** Marca el formato; no se copia. |
| `De-Q-Learning-a-Deep-Q-Networks-DQN.pdf` | Presentación de otro grupo (banca, 12 diapositivas). Mismo nivel conceptual, sin cifras propias. |

No hay cuaderno del profesor para este taller: la Parte 3 parte de nuestro código de los talleres 1 y 2.

## 1. Apertura Shiro

1. **Qué se construye.** El agente de Shiro con **estado continuo**: la red reemplaza a la Q-table. Es la evolución
   directa del MDP (T1) y de Q-learning (T2), y el pendiente abierto del proyecto («entorno continuo para el agente»).
2. **Qué decisiones de arquitectura dependen del resultado.**
   - **¿DQN acorta el arranque en frío?** En el T2 Q-learning no llegó al 90 % en 15.000 días (hallazgo 36). El
     *experience replay* reutiliza cada día muchas veces: ¿cuántos días necesita la red?
   - **¿La hora exacta y el consumo continuo mejoran la decisión?** El hallazgo 35 sospechaba que la hora dentro de la
     franja importa; con 24 horas la tabla no tenía datos suficientes, y la red sí puede usarla.
   - **¿Qué trucos son imprescindibles con nuestros datos?** Se quitan, uno por vez, el replay y la red objetivo, y se mide
     qué se rompe. El T2 ya midió un sesgo de sobreestimación de +0,25.
   - **¿Sirve un γ alto con una red?** En el T2 γ = 0,99 se ahogó en ruido (hallazgo 38).
3. Después: datos, red, hiperparámetros.
4. Cierre: qué agente usa la consola del Parcial y qué necesita Shiro Home.

## 2. Parte 1 (30 %) · Investigación, respondida con nuestros propios números

| Pregunta | Respuesta conceptual | Evidencia de Shiro |
|---|---|---|
| ¿Por qué falla la Q-table? | Cada combinación de estado es una celda aparte: no generaliza y crece multiplicativamente. | Con solo 40 estados, Q-learning necesitó más de 15.000 días (≈ 41 años) sin llegar al 90 %. El estado que Shiro realmente necesita (hora exacta, consumo continuo, confianza del tipo de día, probabilidad de pico de G0) son variables continuas. |
| ¿Qué reemplaza a la tabla? | Una red que recibe el vector de estado y devuelve Q para cada acción. Su rol: generalizar entre estados parecidos. | Las 17:00 y las 18:00 con consumo parecido deberían decidir parecido: la tabla las separaba por franja. |
| *Experience replay* | Memoria de transiciones y mini-lotes al azar: rompe la correlación y reutiliza datos. | Lecturas consecutivas casi idénticas (advertencia §8.1 del proyecto) y arranque en frío. **Se demuestra quitándolo.** |
| Red objetivo fija | Dos redes: el objetivo no se mueve con cada actualización. | Sobreestimación de +0,25 y ruido de los Q del T2. **Se demuestra quitándola** (y con Double DQN como variante). |

## 3. Parte 2 (30 %) · Aplicación al sector: Shiro Home

- **Problema:** cada hora, decidir si dejar correr, aplazar o ejecutar la carga desplazable, minimizando costo + espera.
- **Estado (vector continuo, unas 8 dimensiones), todo calculable con lo que Shiro sabe a esa hora:**
  - hora como seno y coseno;
  - consumo de la hora en curso y de la anterior (log Wh);
  - **probabilidad de «carga alta»** de K-Means sobre la curva parcial (el margen al centroide del hallazgo 22);
  - tarifa vigente;
  - carga pendiente y horas que lleva esperando.
- **Acciones:** no actuar · aplazar · ejecutar (las mismas del T1 y el T2).
- **Recompensa:** −tarifa·energía − λ·espera con la contabilidad corregida; quedan prohibidas las del hallazgo 40.
- **Justificación de DQN:** hallazgos 35 a 38. La tabla no escala, no usa la hora exacta y no transfiere entre casas.

## 4. Parte 3 (40 %) · Prototipo: evolucionar los talleres 1 y 2

- **Entorno:** el de réplica del T2 (días reales en orden, sin reiniciar a medianoche), ahora con estado continuo. Mismo
  ΔE (310 Wh), tarifa, λ = 0,005 y contabilidad. Aprende con enero–abril y se evalúa en mayo.
- **Agente:**
  - MLP 2 × 64 con ReLU, pérdida Huber, Adam;
  - replay de 20.000 transiciones, lote 64, red objetivo sincronizada cada N pasos, ε con decaimiento;
  - Double DQN como variante;
  - 5 semillas.
- **Experimentos:**
  - **E1 · La batalla:** DQN frente a π\* (T1) y frente a Q-learning recomendado (T2) en mayo. Ahorro capturado, espera
    y bootstrap pareado por día.
  - **E2 · Arranque en frío:** ahorro capturado según días de experiencia (1, 2, 5, 10, 20, 50 pasadas), comparado con
    Q-learning. Es la cifra que decide cuánto pre-entrenamiento necesita Shiro Home.
  - **E3 · Ablación de los trucos:** sin replay, sin red objetivo y sin ninguno. Curva, oscilación y divergencia de los Q.
    Es la Parte 1 demostrada con datos.
  - **E4 · Lo que la tabla no veía:** mapa de la política hora × consumo. ¿Cambia la decisión dentro de una misma franja?
    ¿Qué hace con estados nunca vistos (consumos extremos)?
  - **E5 (si hay tiempo) · γ = 0,99 con red.**
- **Implementación:** decisión D2.
- **Cuaderno y cifras:** con el patrón de siempre: `generadores/`, `cifras.json` y `verificar.py` con código 0.

## 5. Entregables

```
3er_Corte_Nov/Taller_3_DQN/
├─ Documentacion/
├─ PLAN_TALLER3_C3.md                    (este plan)
├─ Taller3_C3_DQN_Shiro.ipynb            (Parte 3: E1–E4)
├─ Taller3_C3_DQN_RESUELTO.docx/.pdf     (partes 1–3 por escrito, apertura Shiro; respaldo del video)
├─ Taller3_C3_video_diapositivas.pptx/.pdf   (soporte visual del video, ≈ 12 diapositivas)
├─ Guion_Video_Taller3_C3.docx/.pdf      (≈ 8–10 min, con reparto)
├─ (video) Taller3_C3_Shiro_DQN.mp4      (según D1)
└─ generadores/ · figuras/ · cifras.json
```

## 6. Orden de trabajo (vence mañana)

| # | Paso | Tiempo |
|---|---|---|
| 1 | Hoy: cuaderno DQN (entorno continuo, red, E1–E4, 5 semillas) | ≈ 2–3 h |
| 2 | Hoy: documento, diapositivas y guion con reparto | ≈ 2 h |
| 3 | Hoy por la noche o mañana: grabación del video (según D1) | — |
| 4 | Mañana: verificación y entrega en Classroom (video + PDF + cuaderno) | ≈ 30 min |

## 7. Decisiones abiertas

| # | Decisión | Opciones (recomendada primero) |
|---|---|---|
| D1 | Quién y cómo se hace el video | **a) Guion + diapositivas por Claude; el grupo graba con sus voces**, con el reparto del C2 (Jose apertura, Sofía, Andrés, Alex) · b) Video narrado automático con voz sintética de Windows (Sabina, es-MX) + diapositivas; hay que instalar un ffmpeg en el portátil · c) Pipe graba la pantalla solo |
| D2 | Biblioteca de la red | **a) NumPy propio:** sin instalar nada, transparente, y los pesos se exportan a JSON para que la consola del Parcial ejecute la red en la página · b) PyTorch CPU: estándar de la industria; instalar ≈ 200 MB en el venv |
| D3 | Duración del video | **≈ 8–10 min** (el C2 duró ≈ 17 para 4 talleres) |
| D4 | Adjuntos además del video | **Sí:** PDF + cuaderno, como en el T1 y el T2 |

## 8. Riesgos
- **El DQN puede no superar a la tabla** con 40 estados y 110 días. Se reporta tal cual: es un resultado («la red se
  justifica por el estado que viene, no por el de hoy»). E2 y E4 muestran dónde sí aporta.
- **Inestabilidad de la red.** Por eso hay 5 semillas, Huber, recorte de gradiente y Double DQN como variante.
- **Tiempo:** el video depende del grupo. El guion y las diapositivas tienen que estar listos hoy.
