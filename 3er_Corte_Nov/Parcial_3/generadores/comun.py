# -*- coding: utf-8 -*-
"""Utilidades comunes del Parcial 3 (C3): cifras de todo el semestre con prefijo, plantillas {clave} y PDF por COM.

Fuentes (prefijo → archivo):
    p2:  Parcial 2 (cifras.json: «nuevas» + «heredadas», que incluyen el tablero supervisado del 1.er corte)
    t1:  C3 Taller 1 (MDP)          t2:  C3 Taller 2 (Q-learning)          t3:  C3 Taller 3 (DQN)
    c2:  datos/cifras_c2.json       (K-Means, jerárquico y DBSCAN del 2.º corte, recalculados y anclados)
    p3:  datos/cifras_p3.json       (cifras propias del parcial: anclas de la consola, tamaños, etc.)

F("texto con {t3:dqn_captura} y {c2:km_silueta}") sustituye cada {prefijo:clave} por su texto. Una clave que no existe
hace fallar la generación: ninguna cifra queda escrita a mano. Un archivo que todavía no existe no rompe la importación;
solo falla cuando se pide una de sus claves.
"""
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent          # 3er_Corte_Nov/Parcial_3
C3 = RAIZ.parent                                       # 3er_Corte_Nov
PROY = C3.parent                                       # raíz del proyecto
CANDADO = Path(r"C:\Users\pipel\AppData\Local\Temp\shiro_office.lock")
FUENTES = {
    "p2": PROY / "2do_Corte_Oct" / "Parcial_2_Aprendizaje_Supervisado" / "cifras.json",
    "t1": C3 / "Taller_1_RL_MDP" / "cifras.json",
    "t2": C3 / "Taller_2_QLearning" / "cifras.json",
    "t3": C3 / "Taller_3_DQN" / "cifras.json",
    "c2": RAIZ / "datos" / "cifras_c2.json",
    "p3": RAIZ / "datos" / "cifras_p3.json",
}


def cargar():
    """Devuelve {"prefijo:clave": {"valor", "texto", ...}} con todas las fuentes que existan."""
    out = {}
    for pref, ruta in FUENTES.items():
        if not ruta.exists():
            continue
        d = json.loads(ruta.read_text(encoding="utf-8"))
        bloques = [d["nuevas"], d["heredadas"]] if pref == "p2" else [d["cifras"]]
        for b in bloques:
            for k, v in b.items():
                out[f"{pref}:{k}"] = v
    return out


_C = cargar()
USADAS = set()


def recargar():
    global _C
    _C = cargar()


def C(clave):
    if clave not in _C:
        raise KeyError(f"Falta la cifra '{clave}' (¿existe su archivo? prefijos: {', '.join(FUENTES)})")
    USADAS.add(clave)
    return str(_C[clave]["texto"])


def V(clave):
    if clave not in _C:
        raise KeyError(f"Falta la cifra '{clave}'")
    return _C[clave]["valor"]


def F(texto):
    return re.sub(r"\{([a-z0-9]+:[^{}]+)\}", lambda m: C(m.group(1)), texto)

_PS = r'''
$ErrorActionPreference = 'Stop'
$lock = '__LOCK__'
$fs = $null; $t0 = Get-Date
while ($fs -eq $null) {
  try { $fs = [System.IO.File]::Open($lock, 'CreateNew', 'Write', 'None') }
  catch {
    if (((Get-Date) - $t0).TotalMinutes -gt 20) { Write-Output 'CANDADO_TIEMPO_AGOTADO'; exit 3 }
    Start-Sleep -Seconds 15
  }
}
$app = $null
try {
__CUERPO__
  Write-Output 'PDF_OK'
}
catch { Write-Output ('PDF_ERROR: ' + $_.Exception.Message); $code = 1 }
finally {
  if ($app -ne $null) { try { $app.Quit() } catch {} ; [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($app) }
  if ($fs -ne $null) { $fs.Close() }
  Remove-Item -LiteralPath $lock -Force -ErrorAction SilentlyContinue
}
if ($code) { exit $code }
'''
_PPT = r'''
  $app = New-Object -ComObject PowerPoint.Application
  $p = $app.Presentations.Open('__IN__', -1, 0, 0)
  $p.SaveAs('__OUT__', 32)
  $p.Close()
'''
_WORD = r'''
  $app = New-Object -ComObject Word.Application
  $app.Visible = $false
  $app.DisplayAlerts = 0
  $d = $app.Documents.Open('__IN__', $false, $true)
  $d.ExportAsFixedFormat('__OUT__', 17)
  $d.Close(0)
'''


def exportar_pdf(entrada, salida):
    entrada, salida = Path(entrada).resolve(), Path(salida).resolve()
    cuerpo = _PPT if entrada.suffix.lower() == ".pptx" else _WORD
    cuerpo = cuerpo.replace("__IN__", str(entrada).replace("'", "''")).replace("__OUT__", str(salida).replace("'", "''"))
    script = _PS.replace("__LOCK__", str(CANDADO)).replace("__CUERPO__", cuerpo)
    with tempfile.NamedTemporaryFile("w", suffix=".ps1", delete=False, encoding="utf-8-sig") as f:
        f.write(script)
        ps1 = f.name
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", ps1],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1500)
    finally:
        os.remove(ps1)
    txt = (r.stdout or "") + (r.stderr or "")
    if "PDF_OK" not in txt or not salida.exists():
        raise RuntimeError(f"No se pudo exportar {entrada.name} a PDF:\n{txt}")
    return salida
