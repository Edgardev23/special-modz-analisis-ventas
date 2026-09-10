#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anonimización para publicación / Anonymization for publishing.

La base de SpecialModz contiene ~4.300 nombres reales de clientes. Para poder
compartir el proyecto como portafolio público sin exponer datos personales
(Ley 1581 de 2012, Colombia), este script reemplaza cada `nombre_cliente` por
un seudónimo colombiano ficticio, **consistente por `id_cliente`** (el mismo
cliente siempre recibe el mismo seudónimo, así que el análisis de recurrencia
sigue siendo válido).

    entrada : src/salida/specialmodz_database.csv   (real + sintético)
    salidas : data/processed/ventas.csv                  (seudonimizado)
              data/processed/correcciones_ciudad.csv     (copia, solo ciudades)
              data/processed/tipos_sin_clasificar.csv     (copia, solo fragmentos)
              docs/reporte_incidencias.md                 (copia con nombres tachados)

Solo librería estándar. Semilla fija => reproducible.
"""

import csv
import random
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SALIDA_LIMPIEZA = Path(__file__).resolve().parent / "salida"
ENTRADA = SALIDA_LIMPIEZA / "specialmodz_database.csv"
SAL_DIR = ROOT / "data" / "processed"
DOCS_DIR = ROOT / "docs"
SEED = 20260910

# --- pools de nombres colombianos comunes (para seudónimos) ------------------
NOMBRES_M = [
    "JUAN", "CARLOS", "ANDRÉS", "LUIS", "JOSÉ", "DIEGO", "FELIPE", "SANTIAGO",
    "DANIEL", "DAVID", "SEBASTIÁN", "MIGUEL", "JORGE", "ÓSCAR", "FERNANDO",
    "JAVIER", "CAMILO", "NICOLÁS", "CRISTIAN", "MAURICIO", "ÁLVARO", "GERMÁN",
    "RICARDO", "HÉCTOR", "JULIÁN", "ESTEBAN", "MATEO", "SAMUEL", "IVÁN",
    "GUSTAVO", "WILSON", "EDWIN", "BRAYAN", "JHON", "KEVIN", "MANUEL",
    "RAFAEL", "GABRIEL", "TOMÁS", "EMILIANO", "JERÓNIMO", "SIMÓN", "PABLO",
    "ALEJANDRO", "SERGIO", "LEONARDO", "HERNÁN", "ORLANDO", "WILLIAM", "YEISON",
]
NOMBRES_F = [
    "MARÍA", "LAURA", "ANDREA", "PAULA", "DANIELA", "CAROLINA", "DIANA",
    "CATALINA", "VALENTINA", "NATALIA", "JOHANA", "LINA", "ÁNGELA", "SANDRA",
    "CLAUDIA", "PATRICIA", "LILIANA", "TATIANA", "CAMILA", "MARIANA", "LUISA",
    "ADRIANA", "MÓNICA", "YENNY", "VIVIANA", "GABRIELA", "ISABELLA", "SOFÍA",
    "ALEJANDRA", "MANUELA", "JULIANA", "PAOLA", "MARCELA", "NOHORA",
    "FERNANDA", "XIMENA", "VALERIA", "SARA", "ANTONIA", "SALOMÉ",
]
SEGUNDOS_M = ["ANDRÉS", "DAVID", "FELIPE", "ALEJANDRO", "JOSÉ", "ESTEBAN",
              "CAMILO", "EDUARDO", "ANTONIO", "IGNACIO", "SANTIAGO", "MANUEL"]
SEGUNDOS_F = ["FERNANDA", "ISABEL", "LUCÍA", "CAMILA", "SOFÍA", "ALEJANDRA",
              "CAROLINA", "PAOLA", "CRISTINA", "VICTORIA", "MERCEDES", "BEATRIZ"]
APELLIDOS = [
    "RODRÍGUEZ", "GÓMEZ", "GONZÁLEZ", "HERNÁNDEZ", "LÓPEZ", "MARTÍNEZ",
    "GARCÍA", "PÉREZ", "SÁNCHEZ", "RAMÍREZ", "TORRES", "DÍAZ", "VARGAS",
    "CASTRO", "RUIZ", "ÁLVAREZ", "ROMERO", "SUÁREZ", "ROJAS", "MORENO",
    "MUÑOZ", "VALENCIA", "GUTIÉRREZ", "JIMÉNEZ", "MENDOZA", "ORTIZ",
    "CASTILLO", "SILVA", "RINCÓN", "CÁRDENAS", "QUINTERO", "CORTÉS",
    "HERRERA", "MEDINA", "AGUILAR", "NIÑO", "PARRA", "CÁCERES", "BERNAL",
    "OSPINA", "ARANGO", "RESTREPO", "GIRALDO", "ZAPATA", "CARDONA", "PEÑA",
    "ACOSTA", "LEÓN", "GUERRERO", "SALAZAR", "BUITRAGO", "PINZÓN", "FORERO",
    "BELTRÁN", "MOLINA", "CAMACHO", "OSORIO", "MEJÍA", "BARRERA", "CASAS",
    "PACHÓN", "VELÁSQUEZ", "SANABRIA", "GALINDO", "CUÉLLAR", "MONROY",
    "AVENDAÑO", "CARVAJAL", "BAUTISTA", "TOVAR", "PRIETO", "SEGURA",
]


def _sin_tildes_upper(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().upper()


def _generador_nombres(rng: random.Random):
    """Nombres ficticios únicos: 'NOMBRE [SEGUNDO] APELLIDO [APELLIDO2]'."""
    usados: set[str] = set()
    while True:
        fem = rng.random() < 0.32
        base, seg = (NOMBRES_F, SEGUNDOS_F) if fem else (NOMBRES_M, SEGUNDOS_M)
        partes = [rng.choice(base)]
        if rng.random() < 0.30:
            partes.append(rng.choice(seg))
        partes.append(rng.choice(APELLIDOS))
        if rng.random() < 0.70:
            ap2 = rng.choice(APELLIDOS)
            if ap2 != partes[-1]:
                partes.append(ap2)
        nombre = " ".join(partes)
        clave = _sin_tildes_upper(nombre)
        if clave in usados:
            continue
        usados.add(clave)
        yield nombre


def _leer(path: Path) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh, delimiter=";"))


def _escribir(path: Path, filas: list[dict], cols: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter=";")
        w.writeheader()
        w.writerows(filas)


def main() -> None:
    filas = _leer(ENTRADA)
    rng = random.Random(SEED)
    gen = _generador_nombres(rng)

    # id_cliente -> seudónimo estable (orden de aparición para reproducibilidad)
    seudonimo: dict[str, str] = {}
    for r in filas:
        seudonimo.setdefault(r["id_cliente"], next(gen))

    for r in filas:
        r["nombre_cliente"] = seudonimo[r["id_cliente"]]

    cols = ["id_cliente", "fecha_compra", "nombre_cliente",
            "ciudad", "valor_compra", "tipo_compra"]
    _escribir(SAL_DIR / "ventas.csv", filas, cols)
    print(f"OK  {SAL_DIR / 'ventas.csv'}")
    print(f"    filas          : {len(filas):,}")
    print(f"    clientes (id)  : {len(seudonimo):,}  seudonimizados")

    # copias que NO tienen datos personales -------------------------------------
    for nombre in ("correcciones_ciudad.csv", "tipos_sin_clasificar.csv"):
        origen = SALIDA_LIMPIEZA / nombre
        if origen.exists():
            (SAL_DIR / nombre).write_bytes(origen.read_bytes())
            print(f"OK  {SAL_DIR / nombre}  (copia)")

    # reporte de incidencias: copiar tachando nombres propios evidentes ---------
    rep = SALIDA_LIMPIEZA / "reporte_incidencias.md"
    if rep.exists():
        txt = rep.read_text(encoding="utf-8")
        # línea de "fila duplicada exacta": Nombre / CIUDAD / fecha / valor
        txt = re.sub(
            r"(- fila \d+: )([A-Za-zÁÉÍÓÚÑáéíóúñ.]+(?: [A-Za-zÁÉÍÓÚÑáéíóúñ.]+){1,4})( / [A-ZÁÉÍÓÚÑ ]+ / \d{4}-\d{2}-\d{2})",
            r"\1[cliente anonimizado]\3", txt)
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        (DOCS_DIR / "reporte_incidencias.md").write_text(txt, encoding="utf-8")
        print(f"OK  {DOCS_DIR / 'reporte_incidencias.md'}  (nombres tachados)")


if __name__ == "__main__":
    main()
