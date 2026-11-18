# -*- coding: utf-8 -*-
"""Utilidades comunes del Taller 3 (C3): cifras.json propio y de los talleres 1 y 2, plantillas {clave} y PDF por COM.

F("texto con {clave}") usa las cifras de este taller; {t1:clave} y {t2:clave} las de los talleres 1 y 2. Una clave que
no existe hace fallar la generación: ninguna cifra queda escrita a mano.
"""
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CANDADO = Path(r"C:\Users\pipel\AppData\Local\Temp\shiro_office.lock")
_FUENTES = {"": RAIZ / "cifras.json", "t1:": RAIZ.parent / "Taller_1_RL_MDP" / "cifras.json",
            "t2:": RAIZ.parent / "Taller_2_QLearning" / "cifras.json"}
_C = {}
for pref, ruta in _FUENTES.items():
    for k, v in json.loads(ruta.read_text(encoding="utf-8"))["cifras"].items():
        _C[pref + k] = v
USADAS = set()


def C(clave):
    if clave not in _C:
        raise KeyError(f"Falta la cifra '{clave}'")
    USADAS.add(clave)
    return str(_C[clave]["texto"])


def V(clave):
    if clave not in _C:
        raise KeyError(f"Falta la cifra '{clave}'")
    return _C[clave]["valor"]


def F(texto):
    return re.sub(r"\{([^{}]+)\}", lambda m: C(m.group(1)), texto)


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
