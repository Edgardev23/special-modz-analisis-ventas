#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tarea 5 — Datos SINTÉTICOS para el hueco 2021-03 → 2022-12.

El histórico real no tiene ni una fila entre 2021-03-01 y 2022-12-31 (22
meses). No hay forma de saber si el taller estuvo cerrado, si se perdieron
los registros de esa época o algo intermedio. Este script NO reconstruye lo
que pasó: genera un relleno estimado a partir del ritmo de negocio real
inmediatamente antes y después del hueco, para que los dashboards muestren
una serie continua en vez de un salto.

Método:
  - Estacionalidad (forma mes a mes): promedio de la participación de cada
    mes en el total del año, usando los 3 años reales más cercanos y
    completos (2019, 2020, 2023).
  - Nivel (cuántos pedidos por mes): se interpola linealmente, en la escala
    "pedidos/año equivalente", entre dos anclas reales:
      ancla izquierda  = ene+feb 2021 (últimos meses reales antes del hueco)
      ancla derecha    = ene+feb+mar 2023 (primeros meses reales después)
    des-estacionalizadas con los pesos de arriba. Entre esas dos anclas el
    nivel real apenas cambia (~110-115 pedidos/mes equivalentes), así que la
    interpolación es casi plana, no una proyección de crecimiento.
  - Cada pedido sintético = un pedido real completo (sus líneas, tipos,
    valores y ciudad) tomado al azar de un pool de donantes reales cercanos
    en el tiempo (2019, 2020, ene-feb 2021, 2023) + fecha nueva dentro del
    mes (con el mismo peso por día de semana del histórico real) + nombre
    ficticio colombiano que no existe ni en el histórico real ni en el otro
    lote de sintéticos (Tarea 2, cola 2024-2025).
  - Los valores de valor_compra se copian tal cual del pedido donante: no se
    inflan ni se ajustan por año.

Entradas : limpieza/salida/especialmodz_clientes_limpio.csv      (Tarea 1, real)
           limpieza/salida/especialmodz_ventas_sinteticas.csv    (Tarea 2, para
                                                                   no repetir nombres)
Salidas  : limpieza/salida/especialmodz_ventas_sinteticas_gap.csv
           limpieza/salida/analisis_gap_2021_2022.md
Solo librería estándar. Semilla fija => reproducible.
"""

import csv
import collections
import datetime as dt
import random
import re
import unicodedata
from pathlib import Path

SEED = 20260915
RAIZ = Path(__file__).resolve().parent
ENTRADA_REAL = RAIZ / "salida" / "especialmodz_clientes_limpio.csv"
ENTRADA_SYN_TAREA2 = RAIZ / "salida" / "especialmodz_ventas_sinteticas.csv"
SAL_CSV = RAIZ / "salida" / "especialmodz_ventas_sinteticas_gap.csv"
SAL_MD = RAIZ / "salida" / "analisis_gap_2021_2022.md"

GAP_INI = dt.date(2021, 3, 1)
GAP_FIN = dt.date(2022, 12, 31)
ANIOS_ESTACIONALIDAD = (2019, 2020, 2023)   # años completos más cercanos al hueco
ANIOS_DONANTES = (2019, 2020, 2021, 2023)   # 2021 solo aporta ene-feb (real)


# --------------------------------------------------------------------------
# utilidades (mismas que Tarea 2, duplicadas para mantener el script autónomo)
# --------------------------------------------------------------------------
def sin_tildes_upper(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().upper()


def leer_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh, delimiter=";"))


def reconstruir_pedidos(filas: list[dict]) -> list[dict]:
    grupos: dict = collections.defaultdict(list)
    for f in filas:
        clave = (f["fecha_compra"], f["nombre_cliente"], f["ciudad"])
        grupos[clave].append(
            {"tipo_compra": f["tipo_compra"], "valor_compra": int(f["valor_compra"])}
        )
    pedidos = []
    for (fecha, nombre, ciudad), lineas in grupos.items():
        pedidos.append(
            {
                "fecha": dt.date.fromisoformat(fecha),
                "nombre": nombre,
                "ciudad": ciudad,
                "lineas": lineas,
            }
        )
    return pedidos


# --------------------------------------------------------------------------
# nombres ficticios colombianos (mismo estilo que Tarea 2)
# --------------------------------------------------------------------------
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
    "ALEJANDRA", "MANUELA", "JULIANA", "CAROLINA", "PAOLA", "MARCELA",
    "FERNANDA", "XIMENA", "VALERIA", "SARA", "ANTONIA", "SALOMÉ", "NOHORA",
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
    "PACHÓN", "VELÁSQUEZ", "SANABRIA", "GALINDO", "CUELLAR", "MONROY",
    "AVENDAÑO", "CARVAJAL", "BAUTISTA", "TOVAR", "PRIETO", "SEGURA",
]


def generador_nombres(rng: random.Random, prohibidos: set[str]):
    usados: set[str] = set()
    while True:
        fem = rng.random() < 0.30
        base = NOMBRES_F if fem else NOMBRES_M
        seg = SEGUNDOS_F if fem else SEGUNDOS_M
        partes = [rng.choice(base)]
        if rng.random() < 0.30:
            partes.append(rng.choice(seg))
        partes.append(rng.choice(APELLIDOS))
        if rng.random() < 0.70:
            ap2 = rng.choice(APELLIDOS)
            if ap2 != partes[-1]:
                partes.append(ap2)
        nombre = " ".join(partes)
        clave = sin_tildes_upper(nombre)
        if clave in prohibidos or clave in usados:
            continue
        usados.add(clave)
        yield nombre


# --------------------------------------------------------------------------
# estacionalidad + nivel interpolado
# --------------------------------------------------------------------------
def peso_mensual(pedidos_por_anio: dict[int, list[dict]]) -> dict[int, float]:
    """Participación promedio de cada mes (1-12) en el total del año,
    promediada sobre los años de referencia."""
    part_por_anio = []
    for anio, peds in pedidos_por_anio.items():
        cont = collections.Counter(p["fecha"].month for p in peds)
        tot = sum(cont.values())
        part_por_anio.append({m: cont[m] / tot for m in range(1, 13)})
    return {m: sum(p[m] for p in part_por_anio) / len(part_por_anio) for m in range(1, 13)}


def meses_del_periodo(ini: dt.date, fin: dt.date):
    out = []
    y, m = ini.year, ini.month
    while (y, m) <= (fin.year, fin.month):
        out.append((y, m))
        y, m = (y + (m == 12), (m % 12) + 1)
    return out


def indice_mes(y: int, m: int) -> int:
    return y * 12 + m


def main() -> None:
    rng = random.Random(SEED)

    reales = leer_csv(ENTRADA_REAL)
    pedidos_reales = reconstruir_pedidos(reales)
    por_anio = collections.defaultdict(list)
    for p in pedidos_reales:
        por_anio[p["fecha"].year].append(p)

    # --- estacionalidad: forma mensual promedio (años completos cercanos) ---
    ref = {a: por_anio[a] for a in ANIOS_ESTACIONALIDAD}
    peso_mes = peso_mensual(ref)

    # --- nivel: interpolación lineal entre dos anclas reales ---
    def nivel_ancla(pedidos_ancla: list[dict], meses_ancla: list[int]) -> float:
        n = len(pedidos_ancla)
        w = sum(peso_mes[m] for m in meses_ancla)
        return n / w  # "pedidos/año equivalentes" implícitos en esos meses

    ancla_izq_peds = [p for p in por_anio[2021] if p["fecha"].month in (1, 2)]
    ancla_der_peds = [p for p in por_anio[2023] if p["fecha"].month in (1, 2, 3)]
    nivel_izq = nivel_ancla(ancla_izq_peds, [1, 2])
    nivel_der = nivel_ancla(ancla_der_peds, [1, 2, 3])
    t_izq = indice_mes(2021, 1) + 0.5   # centro ene-feb 2021
    t_der = indice_mes(2023, 2)          # centro ene-feb-mar 2023 (mes del medio)

    def nivel_en(t: float) -> float:
        frac = (t - t_izq) / (t_der - t_izq)
        return nivel_izq + frac * (nivel_der - nivel_izq)

    # --- pool de pedidos donantes (líneas/tipos/valores/ciudad reales) ---
    donantes = []
    for a in ANIOS_DONANTES:
        if a == 2021:
            donantes.extend(p for p in por_anio[a] if p["fecha"].month in (1, 2))
        else:
            donantes.extend(por_anio[a])

    # --- peso por día de semana (todo el histórico real) ---
    wd = collections.Counter(p["fecha"].weekday() for p in pedidos_reales)
    tot_wd = sum(wd.values())
    peso_wd = {d: wd[d] / tot_wd for d in range(7)}

    # --- nombres prohibidos: histórico real + sintéticos de la Tarea 2 ---
    prohibidos = {sin_tildes_upper(f["nombre_cliente"]) for f in reales}
    if ENTRADA_SYN_TAREA2.exists():
        prohibidos |= {sin_tildes_upper(f["nombre_cliente"])
                       for f in leer_csv(ENTRADA_SYN_TAREA2)}
    nombres = generador_nombres(rng, prohibidos)

    # --- generación mes a mes ---
    filas_out: list[dict] = []
    plan = []
    for y, m in meses_del_periodo(GAP_INI, GAP_FIN):
        t = indice_mes(y, m)
        objetivo = nivel_en(t) * peso_mes[m]
        n = int(objetivo) + (1 if rng.random() < (objetivo - int(objetivo)) else 0)

        prim = dt.date(y, m, 1)
        ult = dt.date(y + (m == 12), (m % 12) + 1, 1) - dt.timedelta(days=1)
        dias = [prim + dt.timedelta(days=i) for i in range((ult - prim).days + 1)]
        pesos_dia = [peso_wd[d.weekday()] for d in dias]

        for _ in range(n):
            donante = rng.choice(donantes)
            fecha = rng.choices(dias, weights=pesos_dia, k=1)[0]
            nombre = next(nombres)
            for linea in donante["lineas"]:
                filas_out.append({
                    "fecha_compra": fecha.isoformat(),
                    "nombre_cliente": nombre,
                    "ciudad": donante["ciudad"],
                    "valor_compra": linea["valor_compra"],
                    "tipo_compra": linea["tipo_compra"],
                })
        plan.append({"mes": f"{y}-{m:02d}", "nivel": round(nivel_en(t), 1),
                     "peso_mes": round(peso_mes[m], 4), "objetivo": round(objetivo, 1),
                     "pedidos": n})

    filas_out.sort(key=lambda r: (r["fecha_compra"], r["nombre_cliente"]))

    with open(SAL_CSV, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["fecha_compra", "nombre_cliente", "ciudad",
                                            "valor_compra", "tipo_compra"], delimiter=";")
        w.writeheader()
        w.writerows(filas_out)

    # --- reporte ---
    tot_ped = sum(p["pedidos"] for p in plan)
    tot_lineas = len(filas_out)
    tot_ventas = sum(int(f["valor_compra"]) for f in filas_out)
    L = []
    L.append("# Tarea 5 — Relleno SINTÉTICO del hueco 2021-03 → 2022-12\n")
    L.append("El histórico real no tiene **ninguna fila** entre 2021-03-01 y "
             "2022-12-31 (22 meses). No sabemos si el taller cerró, si se "
             "perdieron los registros o algo intermedio — el archivo fuente "
             "simplemente salta de 2021-02 a 2023-01. Este relleno es una "
             "**estimación**, no una reconstrucción de lo ocurrido.\n")
    L.append("## Método\n")
    L.append(f"- **Estacionalidad**: participación promedio de cada mes en el año, "
             f"calculada sobre los años completos más cercanos al hueco: "
             f"{', '.join(str(a) for a in ANIOS_ESTACIONALIDAD)}.\n"
             f"- **Nivel**: interpolación lineal (en pedidos/año equivalentes) entre "
             f"dos anclas reales — ene-feb 2021 (nivel {nivel_izq:.1f}) y "
             f"ene-mar 2023 (nivel {nivel_der:.1f}). Como ambas anclas están casi al "
             "mismo nivel, la interpolación es prácticamente plana: no asume "
             "crecimiento ni caída durante el hueco.\n"
             f"- **Pedidos donantes**: cada pedido sintético copia líneas, tipos, "
             f"valores y ciudad de un pedido real elegido al azar entre "
             f"{len(donantes)} pedidos reales cercanos en el tiempo "
             f"({', '.join(str(a) for a in ANIOS_DONANTES)}, 2021 solo ene-feb). "
             "Los valores NO se inflan ni se ajustan.\n"
             "- **Fecha exacta dentro del mes**: sorteada con el peso por día de "
             "semana de todo el histórico real (domingo casi nulo).\n"
             "- **Nombres**: ficticios colombianos, verificados para no repetir "
             "ningún nombre del histórico real ni de los sintéticos de la Tarea 2 "
             "(cola 2024-07→2025-11).\n")

    L.append("## Plan mensual\n")
    L.append("| mes | nivel interpolado | peso del mes | objetivo | pedidos generados |")
    L.append("|---|--:|--:|--:|--:|")
    for p in plan:
        L.append(f"| {p['mes']} | {p['nivel']} | {p['peso_mes']*100:.2f}% "
                  f"| {p['objetivo']} | {p['pedidos']} |")

    L.append(f"\n## Totales\n")
    L.append(f"- **Pedidos sintéticos**: **{tot_ped}** en {len(plan)} meses\n"
             f"- **Líneas sintéticas (filas CSV)**: **{tot_lineas}**\n"
             f"- **Ventas sintéticas totales**: **${tot_ventas:,}**\n")
    nombres_syn = {sin_tildes_upper(f["nombre_cliente"]) for f in filas_out}
    L.append(f"- **{len(nombres_syn)}** nombres ficticios distintos, 0 colisiones "
             "con el histórico real ni con la Tarea 2.\n")
    L.append("\n## Notas\n")
    L.append("- **No es un pronóstico ni una reconstrucción**: es un relleno "
             "estadístico para que las series de tiempo del dashboard no tengan "
             "un salto de 22 meses. Cualquier lectura de crecimiento/caída "
             "*dentro* del hueco no tiene respaldo real — solo los extremos "
             "(ene-feb 2021 y ene-mar 2023) son datos reales.\n")
    L.append(f"- **Semilla fija** (`SEED={SEED}`) ⇒ reproducible.\n")
    L.append("- **Fuera de alcance** (igual que las tareas anteriores): no se "
             "crean ni cargan tablas SQL; esto es solo el extracto tabular.\n")

    SAL_MD.write_text("\n".join(L) + "\n", encoding="utf-8")

    print(f"OK  {len(filas_out)} filas -> {SAL_CSV}")
    print(f"    {tot_ped} pedidos sintéticos en {len(plan)} meses")
    print(f"    reporte -> {SAL_MD}")


if __name__ == "__main__":
    main()
