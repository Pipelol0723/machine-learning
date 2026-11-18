# Guion del video · Taller 3 del 3.er corte (DQN) · Grupo Shiro

Duración estimada: 8 min 47 s (2,4 palabras por segundo). Una toma por diapositiva, nombrada NN_nombre (por ejemplo 03_sofia.m4a). Se lee solo el texto de cada bloque, sin el número ni el narrador.

- **Jose:** diapositivas 1, 2 · ≈ 68 s
- **Sofía:** diapositivas 3, 4, 5 · ≈ 134 s
- **Alex:** diapositivas 6, 7, 13 · ≈ 139 s
- **Andrés:** diapositivas 8, 9, 10, 11, 12 · ≈ 186 s

## 01 · Jose · ≈ 18 s

Hola, somos el grupo Shiro: Jose, Sofía, Andrés y Alex. En este video presentamos el Taller 3 del tercer corte: de Q-learning a Deep Q-Networks, aplicado al agente de Shiro, que decide cada hora si conviene aplazar el consumo de un hogar.

## 02 · Jose · ≈ 50 s

Shiro es el gemelo digital de un hogar. En el Taller 1 resolvimos su problema de decisión con iteración de valor: cuarenta estados y una política óptima que en mayo ahorra el 0,59 % del costo. En el Taller 2 el agente aprendió sin conocer el modelo, con Q-learning, pero necesitó 15.000 días simulados, unos 41 años de experiencia real, y aun así no llegó al noventa por ciento de acierto. Hoy preguntamos: ¿una red neuronal resuelve eso? ¿Y qué gana Shiro cuando ve la hora exacta en vez de la franja? Primero Sofía explica la investigación; después Alex muestra cómo se aplica a nuestro sector, y Andrés presenta el prototipo y sus resultados. Al final contamos qué cambia en Shiro.

## 03 · Sofía · ≈ 37 s

La Q-table guarda un valor por cada combinación de estado y acción. Eso tiene dos problemas. Primero, no generaliza: para la tabla, las cinco y las seis de la tarde son celdas distintas, aunque se parezcan. Segundo, cada variable nueva multiplica el número de celdas. Nosotros lo medimos: con solo cuarenta estados, Q-learning necesitó 15.000 días y no llegó al noventa por ciento. Y el estado real de Shiro es continuo: la hora, el consumo, la confianza en el tipo de día. Eso no cabe en ninguna tabla.

## 04 · Sofía · ≈ 47 s

La pieza central de DQN es una red neuronal que reemplaza a la tabla. Recibe el estado como un vector de 9 números y devuelve, de una vez, el valor Q de cada acción: no actuar, aplazar y ejecutar. Su papel no es memorizar celdas sino generalizar: si aprende que a las cinco de la tarde conviene aplazar, lo extiende a las seis. ¿Cómo aprende? Compara lo que predice con el objetivo de Bellman, que es la recompensa más el valor descontado del estado siguiente, y corrige sus pesos con descenso de gradiente. La escribimos en NumPy, sin librerías de aprendizaje profundo, para que sus pesos puedan correr en la consola del parcial.

## 05 · Sofía · ≈ 50 s

Pero reemplazar la tabla por una red no basta: sin ayuda, el entrenamiento es inestable. El primer truco es la memoria de experiencias: guardamos veinte mil transiciones y entrenamos con lotes tomados al azar. Así se rompe la correlación entre horas consecutivas, que son casi idénticas, y cada día se reutiliza muchas veces. El segundo truco es la red objetivo: una copia congelada que calcula el objetivo y se actualiza cada quinientos pasos. Sin ella, el objetivo se mueve con cada actualización. Probamos además una variante, Double DQN, que separa quién elige la acción siguiente de quién la evalúa, para reducir la sobreestimación que medimos en el Taller 2. En la Parte 3 mostramos qué pasa si quitamos cada truco.

## 06 · Alex · ≈ 43 s

Ahora, el sector. El problema de Shiro Home es decidir cada hora qué hacer con la carga que se puede mover, como la lavadora o la secadora, para pagar menos energía sin obligar a la persona a esperar demasiado. El agente ve un vector de 9 números: la hora como seno y coseno, el consumo de la hora actual y la anterior, qué tanto se parece el día a uno de carga alta según K-Means, la tarifa, si hay una carga esperando y desde hace cuánto, y si hay un pico. Y tiene tres acciones: no actuar, aplazar el pico o ejecutar lo pendiente.

## 07 · Alex · ≈ 49 s

La recompensa premia el sobrecosto de punta que se evita al aplazar y castiga cada hora de espera. Aquí hicimos un cambio importante: el costo de lo que consume la casa no depende de lo que decida Shiro, así que lo quitamos de la recompensa. La política óptima es exactamente la misma, pero el agente deja de aprender ruido. Es una lección que se repite en todo el semestre: el agente optimiza exactamente lo que se le pide, así que la recompensa debe medir solo lo que su decisión puede cambiar. ¿Y por qué DQN? Porque la tabla necesita demasiados días, no ve la hora exacta, no transfiere lo aprendido, y el estado que viene es continuo.

## 08 · Andrés · ≈ 36 s

Pasamos al prototipo. Es la evolución de los dos talleres anteriores: mismos datos, misma tarifa y mismo costo de espera. El agente aprende con enero a abril y se evalúa en mayo, un mes que nunca vio. Antes de entrenar, 6 anclas comprueban que el entorno reproduce exactamente los resultados de los talleres 1 y 2. Todo está escrito en NumPy: la red, la retropropagación y el optimizador Adam. Y cada configuración se entrena con 5 semillas distintas, para no confundir un buen resultado con suerte.

## 09 · Andrés · ≈ 33 s

Primer experimento, la batalla en mayo. La red, con 1.500 días de entrenamiento, consigue el 97 % del ahorro de la política óptima, y la semilla mediana toma exactamente las mismas decisiones que ella durante todo el mes: comparadas día por día con un bootstrap, la diferencia es cero. Q-learning del Taller 2 se quedaba en el 89 % con diez veces más días. La variante Double DQN no mejora en este problema: una de sus semillas se queda atrás.

## 10 · Andrés · ≈ 35 s

Segundo experimento, el arranque en frío: cuántos días necesita cada agente para conseguir el ochenta por ciento del ahorro óptimo. Q-learning del Taller 2 necesitaba 15.000 días. La red, 750 días. Y aquí viene la sorpresa: el mismo Q-learning de tabla, con la recompensa centrada, lo logra en 100 días y termina en el 100 %. El problema del Taller 2 no era la tabla: era el ruido de la recompensa. Para Shiro Home eso significa pasar de décadas a unos meses de experiencia.

## 11 · Andrés · ≈ 32 s

Tercer experimento: quitamos los trucos. Sin la memoria de experiencias, la red baja al 86 % y se vuelve inestable entre semillas. Sin la red objetivo, al 94 %. Y sin ninguno de los dos, al 79 %, con semillas que no ahorran nada y una espera de 10,1 h/día. A la derecha se ve por qué: el valor Q oscila mucho más. Los dos trucos no son adornos: son lo que hace que la red aprenda.

## 12 · Andrés · ≈ 50 s

Cuarto experimento: lo que la tabla no veía. La red decide hora por hora. Para una persona exigente, que valora más su tiempo, la red solo aplaza los picos desde las 17:00. Y no es casualidad: el sobrecosto que se evita paga como mucho 7,76 h de espera, así que aplazar conviene desde las 16:15. La red lo descubrió sola; la tabla, que veía toda la tarde como una sola casilla, no podía. Con una carga pendiente, la persona paciente espera siempre a la madrugada, y la exigente la ejecuta también en la mañana, porque esperar quince horas le cuesta más que el sobrecosto. Una advertencia honesta: de madrugada nunca hubo picos en los datos, así que ahí la red extrapola.

## 13 · Alex · ≈ 47 s

Para cerrar, lo que cambia en Shiro. Primero, la recompensa centrada es obligatoria: sin ella ningún agente aprende rápido. Segundo, con cuarenta estados basta la tabla, que es lo más rápido y lo más explicable. Tercero, la red se justifica por el estado que viene: la hora exacta, la probabilidad de pico de Guardian, otras casas. Y los dos trucos son imprescindibles. Y un límite que no escondemos: el ahorro es pequeño, el 0,59 % en mayo, porque en esta casa aplazar mueve poco; el techo está en saber qué aparato se enciende. En el parcial, la consola de Shiro ejecutará esta red en la página, junto a la política óptima. Gracias.
