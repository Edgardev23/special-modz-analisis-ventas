#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tarea 2 — Generación de datos SINTÉTICOS de ventas (2024-07-04 → 2025-11-10).

NO son datos reales. Se construyen re-muestreando los pedidos reales de 2024
(único tramo con precios actuales) y aplicando:
  - +8 % en el NÚMERO de pedidos respecto a la línea base 2024 (tasa anual),
  - misma proporción de tipo_compra, misma distribución de ciudad y misma
    estacionalidad (mes + día de semana) del histórico reciente,
  - nombres de cliente ficticios colombianos que NO existen en el histórico.

Los valores de valor_compra se toman tal cual de pedidos reales de 2024, así
que quedan siempre dentro de los rangos observados por tipo (no se inflan).

Entradas : limpieza/salida/especialmodz_clientes_limpio.csv  (salida de Tarea 1)
Salidas  : limpieza/salida/especialmodz_ventas_sinteticas.csv
           limpieza/salida/analisis_base_2024.md
Solo librería estándar. Semilla fija => reproducible.
"""

import csv
import collections
import datetime as dt
import random
import re
import statistics
import unicodedata
from pathlib import Path

SEED = 20260829
RAIZ = Path(__file__).resolve().parent
ENTRADA = RAIZ / "salida" / "especialmodz_clientes_limpio.csv"
SAL_CSV = RAIZ / "salida" / "especialmodz_ventas_sinteticas.csv"
SAL_MD = RAIZ / "salida" / "analisis_base_2024.md"

PERIODO_INI = dt.date(2024, 7, 4)
PERIODO_FIN = dt.date(2025, 11, 10)
CRECIMIENTO = 0.08  # +8 % en número de pedidos (tasa anual sobre la base 2024)

TIPOS = ["SERVICIO TECNICO", "MODIFICACION PROPIA", "COMPRA DE CONTROL"]


# --------------------------------------------------------------------------
# utilidades
# --------------------------------------------------------------------------
def sin_tildes_upper(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().upper()


def leer_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh, delimiter=";"))


def reconstruir_pedidos(filas: list[dict]) -> list[dict]:
    """Agrupa filas de salida (1 por categoría) en pedidos.

    Clave = (fecha, nombre, ciudad). Devuelve un dict por pedido con la lista
    de líneas (tipo + valor) tal como aparecen en el CSV.
    """
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
                "total": sum(l["valor_compra"] for l in lineas),
                "patron": tuple(sorted(l["tipo_compra"] for l in lineas)),
            }
        )
    return pedidos


# --------------------------------------------------------------------------
# 1-2. análisis de la base real
# --------------------------------------------------------------------------
def analizar(filas: list[dict]) -> dict:
    p2023 = reconstruir_pedidos([f for f in filas if f["fecha_compra"][:4] == "2023"])
    p2024 = reconstruir_pedidos([f for f in filas if f["fecha_compra"][:4] == "2024"])
    l2024 = [f for f in filas if f["fecha_compra"][:4] == "2024"]

    # --- valor_compra por tipo (líneas 2024) ---
    valor_tipo = {}
    for t in TIPOS:
        v = sorted(int(f["valor_compra"]) for f in l2024 if f["tipo_compra"] == t)
        q = statistics.quantiles(v, n=10)
        valor_tipo[t] = {
            "n": len(v),
            "min": v[0],
            "max": v[-1],
            "media": round(statistics.mean(v)),
            "mediana": round(statistics.median(v)),
            "p10": round(q[0]),
            "p90": round(q[-1]),
        }

    # --- proporción de tipo_compra (nivel línea, 2024) ---
    cont_tipo = collections.Counter(f["tipo_compra"] for f in l2024)
    tot_lineas = sum(cont_tipo.values())
    prop_tipo = {t: cont_tipo[t] / tot_lineas for t in TIPOS}

    # --- distribución de ciudad (nivel pedido, 2024) ---
    cont_ciudad = collections.Counter(p["ciudad"] for p in p2024)
    prop_ciudad = {c: n / len(p2024) for c, n in cont_ciudad.items()}

    # --- estacionalidad ---
    # 2024 real solo llega hasta 2024-07-03 (H1). Para la forma mensual de
    # todo el año se usa 2023 (único año reciente completo); el nivel se
    # ancla a los pedidos reales de 2024-H1.
    mes_2023 = collections.Counter(p["fecha"].month for p in p2023)
    mes_2024 = collections.Counter(p["fecha"].month for p in p2024)
    h1_2023 = sum(mes_2023[m] for m in range(1, 7))
    h1_2024 = sum(mes_2024[m] for m in range(1, 7))  # = pedidos reales ene-jun 2024

    base_mes = {}
    for m in range(1, 13):
        if m <= 6:
            base_mes[m] = mes_2024[m]  # real
        else:
            # proyección: H1 2024 real * (peso del mes en 2023 / H1 2023)
            base_mes[m] = h1_2024 * mes_2023[m] / h1_2023
    base_2024_total = sum(base_mes.values())

    # --- día de semana (pedidos, 2023 + 2024 combinados) ---
    wd = collections.Counter()
    for p in p2023 + p2024:
        wd[p["fecha"].weekday()] += 1
    tot_wd = sum(wd.values())
    peso_wd = {d: wd[d] / tot_wd for d in range(7)}

    # --- línea base 2024 (número de pedidos y ventas) ---
    ventas_h1_2024 = sum(p["total"] for p in p2024)
    ticket_medio_2024 = ventas_h1_2024 / len(p2024)
    ventas_2024_est = round(base_2024_total * ticket_medio_2024)

    return {
        "p2023": p2023,
        "p2024": p2024,
        "valor_tipo": valor_tipo,
        "prop_tipo": prop_tipo,
        "cont_tipo": cont_tipo,
        "prop_ciudad": prop_ciudad,
        "cont_ciudad": cont_ciudad,
        "mes_2023": mes_2023,
        "mes_2024": mes_2024,
        "base_mes": base_mes,
        "base_2024_total": base_2024_total,
        "peso_wd": peso_wd,
        "wd": wd,
        "pedidos_h1_2024": len(p2024),
        "ventas_h1_2024": ventas_h1_2024,
        "ticket_medio_2024": ticket_medio_2024,
        "ventas_2024_est": ventas_2024_est,
    }


# --------------------------------------------------------------------------
# 5. nombres ficticios colombianos
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
# 3-4. generación del periodo sintético
# --------------------------------------------------------------------------
def meses_del_periodo(ini: dt.date, fin: dt.date):
    """Lista de (anio, mes, dia_ini, dia_fin) cubriendo [ini, fin]."""
    out = []
    y, m = ini.year, ini.month
    while (y, m) <= (fin.year, fin.month):
        prim = dt.date(y, m, 1)
        ult = dt.date(y + (m == 12), (m % 12) + 1, 1) - dt.timedelta(days=1)
        d0 = max(prim, ini)
        d1 = min(ult, fin)
        out.append((y, m, d0, d1, prim, ult))
        y, m = (y + (m == 12), (m % 12) + 1)
    return out


def generar(a: dict, rng: random.Random) -> tuple[list[dict], list[dict]]:
    donantes = a["p2024"]  # pedidos reales de 2024 (H1) = plantillas

    filas_out: list[dict] = []
    plan: list[dict] = []  # resumen mensual para el reporte

    nombres = generador_nombres(rng, GEN_PROHIBIDOS)

    for y, m, d0, d1, prim, ult in meses_del_periodo(PERIODO_INI, PERIODO_FIN):
        dias_mes = (ult - prim).days + 1
        dias_activos = (d1 - d0).days + 1
        fraccion = dias_activos / dias_mes

        objetivo = a["base_mes"][m] * (1 + CRECIMIENTO) * fraccion
        n = int(objetivo) + (1 if rng.random() < (objetivo - int(objetivo)) else 0)

        # días candidatos dentro del tramo activo, con peso por día de semana
        dias = [d0 + dt.timedelta(days=i) for i in range(dias_activos)]
        pesos = [a["peso_wd"][d.weekday()] for d in dias]

        n_pedidos_mes = 0
        for _ in range(n):
            donante = rng.choice(donantes)
            fecha = rng.choices(dias, weights=pesos, k=1)[0]
            nombre = next(nombres)
            for linea in donante["lineas"]:
                filas_out.append(
                    {
                        "fecha_compra": fecha.isoformat(),
                        "nombre_cliente": nombre,
                        "ciudad": donante["ciudad"],
                        "valor_compra": linea["valor_compra"],
                        "tipo_compra": linea["tipo_compra"],
                    }
                )
            n_pedidos_mes += 1

        plan.append(
            {
                "mes": f"{y}-{m:02d}",
                "base_2024": round(a["base_mes"][m], 1),
                "fraccion": round(fraccion, 3),
                "objetivo": round(objetivo, 1),
                "pedidos": n_pedidos_mes,
            }
        )

    filas_out.sort(key=lambda r: (r["fecha_compra"], r["nombre_cliente"]))
    return filas_out, plan


# --------------------------------------------------------------------------
# salida
# --------------------------------------------------------------------------
def escribir_csv(filas: list[dict]):
    with open(SAL_CSV, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(
            fh,
            fieldnames=["fecha_compra", "nombre_cliente", "ciudad",
                        "valor_compra", "tipo_compra"],
            delimiter=";",
        )
        w.writeheader()
        w.writerows(filas)


def escribir_md(a: dict, plan: list[dict], filas: list[dict]):
    DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    L = []
    L.append("# Tarea 2 — Análisis de la base 2024 y generación de datos sintéticos\n")
    L.append("Datos **sintéticos** (inventados) para el periodo "
             f"**{PERIODO_INI.isoformat()} → {PERIODO_FIN.isoformat()}**. "
             "No son ventas reales.\n")

    L.append("## 1. Análisis de los datos reales de 2024\n")
    L.append("> El histórico real de la Tarea 1 termina el **2024-07-03**, así que "
             "\"2024\" aquí significa **enero–junio 2024 (H1)**: "
             f"**{a['pedidos_h1_2024']} pedidos**, "
             f"**{sum(len(p['lineas']) for p in a['p2024'])} líneas**, "
             f"ventas **${a['ventas_h1_2024']:,}**.\n")

    L.append("### 1.1 valor_compra por tipo_compra (nivel línea, 2024-H1)\n")
    L.append("| tipo_compra | n | mín | p10 | mediana | media | p90 | máx |")
    L.append("|---|--:|--:|--:|--:|--:|--:|--:|")
    for t in TIPOS:
        v = a["valor_tipo"][t]
        L.append(f"| {t} | {v['n']} | {v['min']:,} | {v['p10']:,} | {v['mediana']:,} "
                 f"| {v['media']:,} | {v['p90']:,} | {v['max']:,} |")
    L.append("\nLos valores sintéticos se copian **tal cual** de pedidos reales de "
             "2024, por lo que siempre caen dentro de estos rangos (no se inflan).\n")

    L.append("### 1.2 Proporción de tipo_compra (nivel línea, 2024-H1)\n")
    L.append("| tipo_compra | líneas | % |")
    L.append("|---|--:|--:|")
    for t in TIPOS:
        L.append(f"| {t} | {a['cont_tipo'][t]} | {a['prop_tipo'][t]*100:.1f}% |")

    L.append("\n### 1.3 Distribución de ciudad (nivel pedido, 2024-H1)\n")
    L.append("| ciudad | pedidos | % |")
    L.append("|---|--:|--:|")
    for c, n in a["cont_ciudad"].most_common():
        L.append(f"| {c} | {n} | {n/len(a['p2024'])*100:.2f}% |")
    L.append("\n2024 es casi 100 % Bogotá. Como la generación re-muestrea pedidos "
             "reales completos, la ciudad de cada pedido sintético se hereda del "
             "pedido plantilla y la distribución se conserva exactamente.\n")

    L.append("### 1.4 Estacionalidad — volumen de pedidos por mes\n")
    L.append("2024-H1 es real; para la forma de jul–dic se usa 2023 (único año "
             "reciente completo), anclada al nivel real de 2024-H1.\n")
    L.append("| mes | pedidos 2023 | pedidos 2024 | base 2024 (usada) |")
    L.append("|---|--:|--:|--:|")
    for m in range(1, 13):
        r2024 = a["mes_2024"].get(m, 0)
        marca = "" if m <= 6 else " *(proy.)*"
        L.append(f"| {m:02d} | {a['mes_2023'].get(m,0)} | {r2024 or '—'} "
                 f"| {a['base_mes'][m]:.1f}{marca} |")
    L.append(f"| **año** | **{sum(a['mes_2023'].values())}** | "
             f"**{sum(a['mes_2024'].values())}** (parcial) | "
             f"**{a['base_2024_total']:.0f}** |")

    L.append("\n### 1.5 Estacionalidad — pedidos por día de la semana (2023+2024)\n")
    L.append("| día | pedidos | peso |")
    L.append("|---|--:|--:|")
    for d in range(7):
        L.append(f"| {DIAS[d]} | {a['wd'][d]} | {a['peso_wd'][d]*100:.1f}% |")
    L.append("\nDomingo es casi nulo (taller cerrado). Dentro de cada mes las "
             "fechas sintéticas se sortean con estos pesos.\n")

    L.append("## 2. Línea base 2024 (referencia de crecimiento)\n")
    L.append(f"- Pedidos reales 2024-H1 (ene–jun): **{a['pedidos_h1_2024']}**\n"
             f"- Ticket medio por pedido 2024-H1: **${a['ticket_medio_2024']:,.0f}**\n"
             f"- **Pedidos 2024 completo (estimado)**: **{a['base_2024_total']:.0f}** "
             "(H1 real + H2 proyectado con la forma de 2023)\n"
             f"- **Ventas 2024 completo (estimado)**: "
             f"**${a['ventas_2024_est']:,}** "
             f"(≈ {a['base_2024_total']:.0f} × ${a['ticket_medio_2024']:,.0f})\n")

    L.append("## 3-4. Periodo sintético generado\n")
    tot_ped = sum(p["pedidos"] for p in plan)
    tot_lineas = len(filas)
    tot_ventas = sum(int(f["valor_compra"]) for f in filas)
    L.append(f"- Crecimiento aplicado: **+{CRECIMIENTO*100:.0f}%** sobre el número "
             "de pedidos mensual de la base 2024 (tasa anual). Solo cambia el "
             "**volumen**; los valores por tipo no se tocan.\n")
    L.append(f"- **Pedidos sintéticos**: **{tot_ped}** en {len(plan)} meses "
             f"(2024-07 parcial desde el día 4; 2025-11 parcial hasta el día 10)\n")
    L.append(f"- **Líneas sintéticas (filas CSV)**: **{tot_lineas}**\n")
    L.append(f"- **Ventas sintéticas totales**: **${tot_ventas:,}**\n")
    cont_t = collections.Counter(f["tipo_compra"] for f in filas)
    L.append(f"- Mezcla de tipo_compra resultante: " +
             ", ".join(f"{t} {cont_t[t]/tot_lineas*100:.1f}%" for t in TIPOS) +
             " (comparar con 1.2)\n")

    L.append("\n### Plan mensual\n")
    L.append("| mes | base 2024 | fracción activa | objetivo (×1.08) | pedidos generados |")
    L.append("|---|--:|--:|--:|--:|")
    for p in plan:
        L.append(f"| {p['mes']} | {p['base_2024']} | {p['fraccion']} "
                 f"| {p['objetivo']} | {p['pedidos']} |")

    L.append("\n## 5. Nombres de cliente\n")
    nombres_syn = {sin_tildes_upper(f["nombre_cliente"]) for f in filas}
    L.append(f"- **{len(nombres_syn)}** nombres ficticios distintos, compuestos con "
             "nombres y apellidos colombianos comunes.\n"
             "- Verificado: **0** colisiones con los 3.231 nombres del histórico "
             "real (comparación sin tildes / mayúsculas).\n")

    L.append("\n## 6. Notas / supuestos\n")
    L.append("- **2024 incompleto**: el histórico real solo llega a 2024-07-03. "
             "La base de jul–dic 2024 es una *proyección* con la estacionalidad "
             "de 2023; documentado arriba por si Edgar prefiere otra base.\n")
    L.append("- **Reparto de valor en pedidos multi-tipo**: se hereda el mismo "
             "criterio de la Tarea 1 (partes iguales, la suma del pedido cuadra). "
             "Igual que en la Tarea 1, **no sumar `valor_compra` directamente** "
             "sin agrupar por pedido: hay filas que comparten el valor de un mismo "
             "pedido dividido.\n")
    L.append("- **Método**: cada pedido sintético = un pedido real de 2024 elegido "
             "al azar (con sus líneas, tipos, valores y ciudad) + fecha nueva "
             "(estacionalidad) + nombre ficticio. Semilla fija "
             f"(`SEED={SEED}`) ⇒ reproducible.\n")
    L.append("- **Fuera de alcance** (igual que Tarea 1): no se crean ni cargan "
             "tablas SQL; esto es solo el extracto tabular.\n")

    SAL_MD.write_text("\n".join(L) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
GEN_PROHIBIDOS: set[str] = set()


def main():
    global GEN_PROHIBIDOS
    rng = random.Random(SEED)
    filas = leer_csv(ENTRADA)
    GEN_PROHIBIDOS = {sin_tildes_upper(f["nombre_cliente"]) for f in filas}

    a = analizar(filas)
    syn, plan = generar(a, rng)
    escribir_csv(syn)
    escribir_md(a, plan, syn)

    print(f"OK  {len(syn)} filas -> {SAL_CSV}")
    print(f"    {sum(p['pedidos'] for p in plan)} pedidos sintéticos")
    print(f"    reporte -> {SAL_MD}")


if __name__ == "__main__":
    main()
