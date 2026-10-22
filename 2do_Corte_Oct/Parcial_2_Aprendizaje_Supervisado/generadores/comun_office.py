# -*- coding: utf-8 -*-
"""Utilidades comunes de la Parte 3 y del guion: lectura de cifras.json y exportación a PDF por COM.

- Toda cifra sale de ../cifras.json (campo "texto", es-CO) o de ../mockup/datos_mockup.json.
- El PDF se exporta con Word o PowerPoint vía PowerShell (no hay pywin32), con un candado de uso exclusivo de
  Office en %LOCALAPPDATA%\\Temp\\shiro_office.lock: se crea en exclusiva (si existe, se espera 15 s y se reintenta,
  máximo 20 min), se borra siempre al terminar y la aplicación se cierra siempre (Quit()).
"""
import json
import os
import re
import tempfile
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent          # carpeta del parcial
CANDADO = Path(r"C:\Users\pipel\AppData\Local\Temp\shiro_office.lock")


class Cifras:
    """Acceso a cifras.json por clave. T() devuelve el texto es-CO con el signo menos tipográfico."""

    def __init__(self, ruta=RAIZ / "cifras.json"):
        c = json.loads(Path(ruta).read_text(encoding="utf-8"))
        self.d = {}
        for sec in ("nuevas", "heredadas"):
            self.d.update(c.get(sec, {}))
        self.usadas = set()

    def existe(self, k):
        return k in self.d

    def T(self, k):
        if k not in self.d:
            raise KeyError(f"Falta la cifra '{k}' en cifras.json")
        self.usadas.add(k)
        t = str(self.d[k]["texto"])
        return re.sub(r"(^|[\s(])-(\d)", lambda m: m.group(1) + "\u2212" + m.group(2), t)

    def N(self, k):
        """Solo la parte numérica del texto ('28 picos' -> '28'; '127 min/día' -> '127')."""
        return self.T(k).split(" ")[0]

    def V(self, k):
        if k not in self.d:
            raise KeyError(f"Falta la cifra '{k}' en cifras.json")
        self.usadas.add(k)
        return self.d[k]["valor"]


def datos_mockup():
    return json.loads((RAIZ / "mockup" / "datos_mockup.json").read_text(encoding="utf-8"))


def num_es(x, dec=1):
    """Formato es-CO (coma decimal, punto de miles, signo menos tipográfico); solo da formato, no calcula."""
    s = f"{abs(x):,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    neg = x < 0 and round(abs(x), dec) != 0
    return ("\u2212" if neg else "") + s


_PALABRAS = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez", "once", "doce"]


def en_palabras(n, femenino=False):
    """Entero pequeño en palabras (es-CO): 6 -> 'seis'. Para cifras de cifras.json dichas con letra."""
    n = int(n)
    if not 0 <= n < len(_PALABRAS):
        return str(n)
    w = _PALABRAS[n]
    return "una" if (femenino and n == 1) else w


_PS_CANDADO = r'''
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

_CUERPO_PPT = r'''
  $app = New-Object -ComObject PowerPoint.Application
  $p = $app.Presentations.Open('__IN__', -1, 0, 0)
  $p.SaveAs('__OUT__', 32)
  $p.Close()
'''

_CUERPO_WORD = r'''
  $app = New-Object -ComObject Word.Application
  $app.Visible = $false
  $app.DisplayAlerts = 0
  $d = $app.Documents.Open('__IN__', $false, $true)
  $d.ExportAsFixedFormat('__OUT__', 17)
  $d.Close(0)
'''


def exportar_pdf(entrada, salida):
    entrada, salida = Path(entrada).resolve(), Path(salida).resolve()
    cuerpo = _CUERPO_PPT if entrada.suffix.lower() == ".pptx" else _CUERPO_WORD
    cuerpo = cuerpo.replace("__IN__", str(entrada).replace("'", "''")).replace("__OUT__", str(salida).replace("'", "''"))
    script = _PS_CANDADO.replace("__LOCK__", str(CANDADO)).replace("__CUERPO__", cuerpo)
    with tempfile.NamedTemporaryFile("w", suffix=".ps1", delete=False, encoding="utf-8-sig") as f:
        f.write(script)
        ps1 = f.name
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", ps1],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1500)
    finally:
        os.remove(ps1)
    salida_txt = (r.stdout or "") + (r.stderr or "")
    if "PDF_OK" not in salida_txt or not salida.exists():
        raise RuntimeError(f"No se pudo exportar {entrada.name} a PDF:\n{salida_txt}")
    return salida


RESIDUOS = ["{{", "[por calcular]", "TODO", "Claude", "Anthropic", "ChatGPT", "IA generativa", "CLAUDE.md",
            "spec", "hito", "el plan"]


def buscar_residuos(texto):
    """Devuelve los residuos prohibidos presentes (TODO en mayúsculas; el resto sin distinguir mayúsculas)."""
    hall = []
    for r in RESIDUOS:
        if r == "TODO":
            if re.search(r"\bTODO\b", texto):
                hall.append(r)
        elif r.lower() in texto.lower():
            hall.append(r)
    return hall
