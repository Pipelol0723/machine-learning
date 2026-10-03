# Plan de desarrollo - Parcial 2 de Aprendizaje Supervisado

## Objetivo

Construir un sistema que estime el ingreso de taquilla de una pelicula antes de su estreno y traduzca esa estimacion en una recomendacion para apoyar decisiones de produccion, marketing y distribucion. Esta linea mantiene coherencia con la documentacion de referencia, pero el modelo final se elegira con resultados reproducibles sobre el dataset seleccionado.

## Entregables del parcial

| Parte | Entregable | Resultado esperado |
| --- | --- | --- |
| 1 | Informe ejecutivo en APA | Problema, decision habilitada, resultados interpretados, limites, etica y recomendaciones. |
| 2 | Mockup funcional | Aplicacion que recibe datos de una pelicula, estima el ingreso y muestra una recomendacion accionable. |
| 3 | Presentacion de implementacion | Arquitectura, datos, roles, sistemas y capacitacion para operar la solucion. |
| 4 | Poster academico | Resumen visual del problema, datos, evolucion de modelos, resultado, etica y mockup. |

## Estructura de trabajo

```text
Parcial_2_Aprendizaje_Supervisado/
  Documentacion/              # Enunciado y ejemplos recibidos
  data/                       # Dataset original y version procesada
  notebooks/                  # Exploracion, entrenamiento y evaluacion
  src/                        # Preprocesamiento y pipeline reutilizable
  app/                        # Mockup funcional
  informe/                    # Informe ejecutivo APA y sus figuras
  poster/                     # Fuente y exportacion del poster
  presentacion/               # Propuesta de implementacion
  PLAN_DESARROLLO.md
```

## Secuencia de desarrollo

1. Definir el caso de uso y la variable objetivo. Usar ingresos de taquilla como objetivo de regresion y fijar la decision que apoyara el sistema: aprobar, revisar o ajustar la estrategia de una pelicula.
2. Conseguir y documentar el dataset. La referencia usa TMDB Movie Dataset v11; antes de entrenar, registrar licencia, fecha de descarga, numero de filas y diccionario de variables. Separar los datos originales de los procesados.
3. Preparar los datos. Eliminar duplicados, tratar faltantes, revisar valores imposibles y evitar variables que solo se conocen despues del estreno. Crear una division temporal de entrenamiento y prueba para no filtrar informacion del futuro.
4. Construir una linea base. Entrenar una regresion lineal con las variables disponibles antes del estreno. Servira para comprobar que los modelos mas complejos aportan una mejora real.
5. Evaluar modelos candidatos. Probar Random Forest y Gradient Boosting, con el mismo pipeline y la misma division de datos. Comparar MAE, RMSE y R2; elegir el modelo que combine error comprensible, estabilidad e interpretabilidad.
6. Convertir la prediccion en una decision. Definir tres bandas de riesgo usando el ingreso estimado y un umbral de rentabilidad: verde para potencial alto, amarillo para revision y rojo para riesgo alto. Cada banda debe incluir una accion sugerida.
7. Crear el mockup funcional. Implementar una aplicacion local en Streamlit con entradas validadas, resultado de ingreso estimado, banda de riesgo, factores principales y recomendacion. Guardar capturas para el informe y el poster.
8. Redactar y disenar los entregables. Primero el informe ejecutivo, luego la presentacion y finalmente el poster. Todos deben reutilizar las mismas cifras, definiciones y visualizaciones validadas.

## Mockup minimo viable

Entradas: presupuesto, popularidad previa, genero, duracion, mes de estreno y variables que se puedan justificar como disponibles antes del estreno.

Salidas: ingreso estimado, rango de incertidumbre, semaforo de riesgo, tres factores que influyen en el resultado y una recomendacion concreta. Ejemplo: "Riesgo alto: revisar presupuesto y plan de marketing antes de aprobar la produccion".

Pantallas: formulario de evaluacion, resultado ejecutivo y vista de seguimiento con historial de simulaciones. El mockup debe mostrar una simulacion antes y despues al modificar una variable controlable, como presupuesto de marketing.

## Contenido de cada pieza

### Informe ejecutivo

Evitar una tabla centrada solo en metricas tecnicas. Explicar el resultado con lenguaje de negocio: cuanto se reduce el error frente a la linea base, que decisiones cambia y que riesgo permanece. Incluir problema sectorial, modelo elegido, visualizaciones, caso de uso, limitaciones, sesgos historicos y recomendaciones.

### Presentacion de implementacion

Mostrar un flujo simple: fuente de datos -> validacion y preparacion -> modelo -> API o aplicacion -> usuario de negocio. Definir responsables: analista de datos, responsable de negocio, TI y persona que aprueba decisiones. Proponer capacitacion breve sobre interpretacion del semaforo, limites del modelo y protocolo de escalamiento.

### Poster academico

Incluir titulo, autores, universidad, problema, dataset, calidad de datos, evolucion de modelos, modelo final, metricas, visualizaciones, riesgos eticos, imagen del mockup, conclusion y siguiente mejora. Mantener el texto breve y priorizar graficos legibles.

## Criterios de aceptacion

- Todo resultado puede reproducirse desde el dataset documentado y un notebook de entrenamiento.
- Las variables usadas por el mockup estan disponibles antes del estreno.
- La prediccion se presenta como apoyo a la decision, con incertidumbre y limites visibles.
- Las cifras del informe, presentacion y poster coinciden.
- El mockup permite ejecutar al menos una simulacion completa sin editar codigo.

## Orden recomendado de los proximos hitos

1. Seleccionar y descargar el dataset.
2. Crear el notebook de exploracion y el diccionario de variables.
3. Entrenar la linea base y los modelos candidatos.
4. Acordar reglas del semaforo con las metricas obtenidas.
5. Construir el mockup y capturar la simulacion.
6. Producir informe, presentacion y poster a partir de los resultados finales.
