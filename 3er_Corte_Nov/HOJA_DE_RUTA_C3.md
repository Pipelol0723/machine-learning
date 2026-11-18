# Hoja de ruta del 3.er corte (revisada en Classroom el 2026-11-11)

| Tarea | Publicada | Vence | Estado | Carpeta |
|---|---|---|---|---|
| C3 Taller1 · MDP | 30-oct | 4-nov | **Entregada** (4-nov, 12:28) | `Taller_1_RL_MDP/` |
| C3 Taller2 · Q-learning | 6-nov | 11-nov | **Entregada** (11-nov, 01:28) | `Taller_2_QLearning/` |
| C3 Taller3 · De Q-learning a DQN | 6-nov | 13-nov, 23:59 | **Entregada** (13-nov, 13:20; video 9:22 con voz sintética en las diapositivas 3–5 porque Sofía no grabó) | `Taller_3_DQN/` → `PLAN_TALLER3_C3.md` |
| C3 Parcial | 6-nov (editado el 10-nov) | 18-nov, 23:59 | **Entregada** (17-nov, 23:55; `Consola_Shiro.html` como archivo + `Articulo_IEEE_Shiro_Twin.pdf`) | `Parcial_3/` → `PLAN_PARCIAL3.md` |

Las tres piezas forman una sola cadena de Shiro:

**MDP resuelto (T1) → agente que aprende sin modelo (T2) → agente con estado continuo (T3) → prototipo que integra los
tres aprendizajes + artículo IEEE (Parcial).**

## C3 Taller3 · De Q-learning a DQN (vence el 13-nov)
Enunciado: `Taller_3_DQN/Documentacion/ML TALLER3 C3 DQN.pdf` (1 p.). Material de apoyo:
`De-Q-Learning-a-Deep-Q-Networks-DQN.pdf` y el ejemplo de otro grupo
`Ejemplo Taller_DQN_Investigacion_Completo.docx.pdf` (marca el formato, no se copia).
- **Parte 1 (30 %) · Investigación:** por qué la Q-table no escala, qué reemplaza la red, *experience replay* y *target
  network*. Respuesta Shiro: el estado real (G0 continuo, retardos, margen al centroide como confianza) no cabe en 40
  celdas.
- **Parte 2 (30 %) · Aplicación al sector:** problema, estado, acciones, recompensa y por qué DQN y no Q-table.
- **Parte 3 (40 %) · Prototipo:** «evolucionar el prototipo de los talleres 1 y 2». Candidato natural: DQN sobre el
  **estado continuo** con el simulador lineal + retardos y la probabilidad de G0. Es el pendiente «entorno de simulación
  continuo» del CLAUDE.md. Se compara contra la π\* tabular.
- **Formato de entrega: VIDEO** con las tres partes. Hay que planear el guion y el reparto del grupo (como en el C2).
- Dependencia: el entorno y las cifras del T2 (arranque en frío, α y γ).

## C3 Parcial (vence el 18-nov)
Material: `Parcial_3/Documentacion/Articulo_IEEE_Semestre_ML.pdf` (ejemplo de artículo de 5 pp. de otro estudiante) y
`EJEMPLO SAVI_v2_ParcialFinal.html` (ejemplo de prototipo; sin abrir todavía). Ejemplo publicado en línea que cita el
profesor: `https://julianrincon-savi-agent.static.hf.space/index.html`.
1. **Prototipo (3,0):** implementar los tres aprendizajes (supervisado, no supervisado y refuerzo) en el sector. Para
   Shiro: una consola que junte el simulador y G0 (supervisado), el tipo de día (K-Means) y el agente (MDP/Q-learning/DQN)
   proponiendo «aplazar / no actuar» con λ ajustable. Se reutilizan los mockups del Parcial 1 y 2 (HTML sin
   dependencias).
2. **Artículo IEEE (2,0) de todo el semestre:** los 35 hallazgos del CLAUDE.md son la materia prima, y las cifras salen
   de los `cifras.json` de cada entrega.
- Pendiente de decidir: alojamiento del prototipo (el ejemplo está en Hugging Face Spaces) y reparto del grupo.
