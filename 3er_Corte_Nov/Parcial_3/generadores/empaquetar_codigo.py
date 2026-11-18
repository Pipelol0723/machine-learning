# -*- coding: utf-8 -*-
r"""Arma entrega/Codigo_y_Dataset_Prototipo_Shiro.zip: el código del prototipo final (la Consola de Shiro), los cuadernos
que entrenan cada modelo que la consola usa y el dataset, con la misma estructura de carpetas del proyecto para que los
scripts corran sin tocar rutas. Lo pidió el profesor el 18-nov («slides, artículo y código del prototipo final con
dataset respectivos»).

Uso (desde la carpeta del parcial):
    C:\Users\pipel\venvs\ml\Scripts\python.exe -X utf8 generadores\empaquetar_codigo.py
"""
import zipfile
from pathlib import Path

from comun import PROY, RAIZ

SALIDA = RAIZ / "entrega" / "Codigo_y_Dataset_Prototipo_Shiro.zip"
CARPETA = "Shiro_Twin_prototipo"          # carpeta raíz dentro del zip

ARCHIVOS = [
    # dataset
    "data set/energydata_complete.csv",
    # supervisado: simulador lineal y anticipador G0 (Parcial 2) y los cuadernos que usa como anclas
    "2do_Corte_Oct/Parcial_2_Aprendizaje_Supervisado/Parcial2_Guardian.ipynb",
    "2do_Corte_Oct/Parcial_2_Aprendizaje_Supervisado/cifras.json",
    "2do_Corte_Oct/Parcial_2_Aprendizaje_Supervisado/mockup/datos_mockup.json",
    "2do_Corte_Oct/Parcial_2_Aprendizaje_Supervisado/mockup/plantilla.html",
    "1er_Corte_Sept/Parcial_Corte1/Parcial_Corte1.ipynb",
    "2do_Corte_Oct/Taller_1_Boosting/Taller1_Boosting.ipynb",
    # no supervisado: tipo de día (K-Means), auditoría (jerárquico) y rareza (DBSCAN)
    "2do_Corte_Oct/Taller_2_KMeans/Taller2_KMeans.ipynb",
    "2do_Corte_Oct/Taller_3_Jerarquico/Taller3_Jerarquico.ipynb",
    "2do_Corte_Oct/Taller_4_DBSCAN/Taller4_DBSCAN.ipynb",
    # refuerzo: MDP (iteración de valor), Q-learning y DQN
    "3er_Corte_Nov/Taller_1_RL_MDP/Taller1_C3_MDP_Shiro.ipynb",
    "3er_Corte_Nov/Taller_1_RL_MDP/cifras.json",
    "3er_Corte_Nov/Taller_1_RL_MDP/politica_optima_shiro.csv",
    "3er_Corte_Nov/Taller_2_QLearning/Taller2_C3_QLearning_Shiro.ipynb",
    "3er_Corte_Nov/Taller_2_QLearning/cifras.json",
    "3er_Corte_Nov/Taller_2_QLearning/politicas_base.csv",
    "3er_Corte_Nov/Taller_3_DQN/Taller3_C3_DQN_Shiro.ipynb",
    "3er_Corte_Nov/Taller_3_DQN/cifras.json",
    "3er_Corte_Nov/Taller_3_DQN/dqn_pesos.json",
    # prototipo final
    "3er_Corte_Nov/Parcial_3/Consola_Shiro.html",
    "3er_Corte_Nov/Parcial_3/generadores/comun.py",
    "3er_Corte_Nov/Parcial_3/generadores/exportar_c2.py",
    "3er_Corte_Nov/Parcial_3/generadores/exportar_datos.py",
    "3er_Corte_Nov/Parcial_3/generadores/construir_consola.py",
    "3er_Corte_Nov/Parcial_3/generadores/consola_plantilla.html",
    "3er_Corte_Nov/Parcial_3/datos/consola.json",
    "3er_Corte_Nov/Parcial_3/datos/cifras_c2.json",
    "3er_Corte_Nov/Parcial_3/datos/cifras_p3.json",
    "3er_Corte_Nov/Parcial_3/datos/dbscan_mayo.json",
]

REQUISITOS = """numpy==2.4.6
pandas==3.0.5
scikit-learn==1.9.0
scipy==1.17.1
matplotlib==3.11.1
pillow==12.3.0
nbformat==5.11.1
nbclient==0.11.0
ipykernel==7.3.0
"""

LEEME = """# Shiro Twin — código del prototipo final y dataset

Parcial 3 · Aprendizaje de Máquina 26-2 · Universidad Sergio Arboleda
Grupo Shiro: Jose Leonardo Diazgranados, Sofía Londoño, Andrés Felipe Céspedes Rondón y Alex Duran.
Docente: Hernán Darío Cruz Bueno.

## 1. Abrir el prototipo

`3er_Corte_Nov/Parcial_3/Consola_Shiro.html` es el prototipo final: una página autocontenida (sin internet ni
librerías) que ejecuta los tres aprendizajes en el navegador sobre los datos de mayo de 2016:

| Pantalla | Aprendizaje | Qué calcula en la página |
|---|---|---|
| Hoy en casa | Supervisado | Predicción lineal a un paso y semáforo de picos G0 |
| ¿Qué tipo de día es? | No supervisado | K-Means sobre la curva parcial del día, margen y bandera de DBSCAN |
| ¿Qué haría Shiro? | Refuerzo | Iteración de valor (π*) con la λ y la tarifa elegidas; Q-learning y la red DQN |
| Pregúntale a Shiro | Los tres | Respuestas por plantilla con cifras reales |
| Ficha del modelo | — | Particiones, intervalos y límites |

Abrir `Consola_Shiro.html#prueba` muestra la autoprueba: la iteración de valor en JavaScript da la misma política que
Python en 35 combinaciones de λ y tarifa, y la red DQN y el margen de K-Means coinciden con sus valores de referencia.

## 2. Estructura

La estructura de carpetas es la del proyecto, para que todas las rutas relativas funcionen sin cambios.

```
data set/energydata_complete.csv              dataset (ver §4)
2do_Corte_Oct/Parcial_2_.../Parcial2_Guardian.ipynb   supervisado: simulador lineal y anticipador G0
2do_Corte_Oct/Taller_2_KMeans/                no supervisado: tipos de día (K-Means)
2do_Corte_Oct/Taller_3_Jerarquico/            no supervisado: auditoría con jerárquico
2do_Corte_Oct/Taller_4_DBSCAN/                no supervisado: días atípicos (DBSCAN)
3er_Corte_Nov/Taller_1_RL_MDP/                refuerzo: MDP e iteración de valor
3er_Corte_Nov/Taller_2_QLearning/             refuerzo: Q-learning
3er_Corte_Nov/Taller_3_DQN/                   refuerzo: DQN en NumPy (pesos en dqn_pesos.json)
3er_Corte_Nov/Parcial_3/                      prototipo: consola, generadores y datos exportados
1er_Corte_Sept/..., 2do_Corte_Oct/Taller_1_Boosting/  cuadernos que el Parcial 2 usa como anclas
```

Los cuadernos se entregan **con sus salidas guardadas**: se pueden leer sin ejecutarlos. Cada uno reproduce sus cifras
y las escribe en su `cifras.json`.

## 3. Regenerar el prototipo

Requiere Python 3.11 y las librerías de `requirements.txt` (`pip install -r requirements.txt`). Desde
`3er_Corte_Nov/Parcial_3/`:

```
python -X utf8 generadores/exportar_c2.py          # cifras del 2.º corte (K-Means, jerárquico, DBSCAN) → datos/
python -X utf8 generadores/exportar_datos.py       # MDP, Q-learning, DQN, G0 y simulador de mayo → datos/consola.json
python -X utf8 generadores/construir_consola.py --sin-edge   # → Consola_Shiro.html
```

Sin `--sin-edge`, en Windows con Microsoft Edge el último paso además ejecuta la autoprueba de la página y guarda
capturas. Cada script falla si una de sus anclas contra los cuadernos no coincide.

## 4. Dataset

Appliances Energy Prediction, UCI Machine Learning Repository n.º 374
(https://archive.ics.uci.edu/dataset/374/appliances+energy+prediction). L. M. Candanedo, V. Feldheim y D. Deramaix,
«Data driven prediction models of energy use of appliances in a low-energy house», Energy and Buildings, vol. 140,
pp. 81–97, 2017. Una vivienda en Bélgica, del 11 de enero al 27 de mayo de 2016, 19.735 lecturas cada 10 minutos y sin
faltantes. Objetivo: `Appliances` (Wh). Se excluyen `rv1` y `rv2`, ruido que los autores inyectaron como control.

## 5. Límites declarados

- Una sola vivienda, en invierno y primavera: todo umbral y modelo se recalibra cada mes.
- Los agentes de refuerzo se entrenan en una réplica de días reales, no sobre el gemelo lineal (pendiente).
- La tarifa con punta ×1,5 es un supuesto de diseño.
- El ahorro de aplazar es pequeño (0,59 % en mayo) y no se distingue de no actuar.
"""


def main():
    SALIDA.parent.mkdir(exist_ok=True)
    faltan = [a for a in ARCHIVOS if not (PROY / a).exists()]
    if faltan:
        raise FileNotFoundError(f"Faltan archivos: {faltan}")
    with zipfile.ZipFile(SALIDA, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr(f"{CARPETA}/LEEME.md", LEEME)
        z.writestr(f"{CARPETA}/requirements.txt", REQUISITOS)
        for a in ARCHIVOS:
            z.write(PROY / a, f"{CARPETA}/{a}")
    total = sum((PROY / a).stat().st_size for a in ARCHIVOS)
    print(f"{SALIDA.name}: {len(ARCHIVOS) + 2} archivos, {total / 1e6:.1f} MB sin comprimir, "
          f"{SALIDA.stat().st_size / 1e6:.1f} MB comprimido")


if __name__ == "__main__":
    main()
