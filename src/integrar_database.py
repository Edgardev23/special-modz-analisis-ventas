#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integra el CSV limpio real (Tarea 1) y los CSV sintéticos (Tarea 2: cola
2024-07→2025-11; Tarea 5: relleno del hueco 2021-03→2022-12) en un solo
archivo `specialmodz_database.csv`, añadiendo un código identificador de cliente.

- Un "cliente único" se identifica por su nombre normalizado (sin tildes, en
  mayúsculas, espacios colapsados). Es lo único que hay: no existe teléfono ni
  cédula en la fuente. Dos personas distintas con el mismo nombre quedarían bajo
  el mismo código (limitación conocida).
- Los nombres sintéticos se generaron para NO colisionar con el histórico, así
  que no se mezclan clientes reales con inventados.
- Códigos: `SM-00001`, `SM-00002`, … asignados por orden de primera compra
  (fecha más antigua). Si el cliente se repite, se repite el código.
- El nombre mostrado de cada cliente se unifica a su variante de grafía más
  frecuente (desempate: la primera vista).

Entradas : limpieza/salida/especialmodz_clientes_limpio.csv
           limpieza/salida/especialmodz_ventas_sinteticas.csv
           limpieza/salida/especialmodz_ventas_sinteticas_gap.csv
Salida   : limpieza/salida/specialmodz_database.csv
           columnas: id_cliente;fecha_compra;nombre_cliente;ciudad;valor_compra;tipo_compra
Solo librería estándar.
"""

import collections
import csv
import re
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SAL = RAIZ / "salida"
FUENTES = [
    SAL / "especialmodz_clientes_limpio.csv",         # reales (Tarea 1)
    SAL / "especialmodz_ventas_sinteticas.csv",       # sintéticos (Tarea 2)
    SAL / "especialmodz_ventas_sinteticas_gap.csv",   # sintéticos (Tarea 5)
]
DESTINO = SAL / "specialmodz_database.csv"
COLS = ["id_cliente", "fecha_compra", "nombre_cliente",
        "ciudad", "valor_compra", "tipo_compra"]


def clave_cliente(nombre: str) -> str:
    s = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().upper()


def leer(path: Path) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh, delimiter=";"))


def main() -> None:
    filas: list[dict] = []
    for f in FUENTES:
        filas.extend(leer(f))

    # orden estable por fecha para que el nº de código siga la 1ª compra
    filas.sort(key=lambda r: (r["fecha_compra"], clave_cliente(r["nombre_cliente"])))

    # nombre canónico por cliente: grafía más frecuente (desempate: 1ª vista)
    grafias: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    primera_grafia: dict[str, str] = {}
    for r in filas:
        k = clave_cliente(r["nombre_cliente"])
        grafias[k][r["nombre_cliente"]] += 1
        primera_grafia.setdefault(k, r["nombre_cliente"])
    canonico = {
        k: max(c.items(), key=lambda kv: (kv[1], kv[0] == primera_grafia[k]))[0]
        for k, c in grafias.items()
    }

    # asignar códigos por orden de aparición (ya ordenado por fecha)
    codigo: dict[str, str] = {}
    for r in filas:
        k = clave_cliente(r["nombre_cliente"])
        if k not in codigo:
            codigo[k] = f"SM-{len(codigo) + 1:05d}"

    ajustes = 0
    salida = []
    for r in filas:
        k = clave_cliente(r["nombre_cliente"])
        nombre = canonico[k]
        if nombre != r["nombre_cliente"]:
            ajustes += 1
        salida.append({
            "id_cliente": codigo[k],
            "fecha_compra": r["fecha_compra"],
            "nombre_cliente": nombre,
            "ciudad": r["ciudad"],
            "valor_compra": r["valor_compra"],
            "tipo_compra": r["tipo_compra"],
        })

    salida.sort(key=lambda r: (r["fecha_compra"], r["id_cliente"]))

    with open(DESTINO, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, delimiter=";")
        w.writeheader()
        w.writerows(salida)

    print(f"OK  {DESTINO}")
    print(f"    filas         : {len(salida)}")
    print(f"    clientes únicos: {len(codigo)}  ({list(codigo.values())[0]} … {list(codigo.values())[-1]})")
    print(f"    grafías unificadas: {ajustes} filas")


if __name__ == "__main__":
    main()
