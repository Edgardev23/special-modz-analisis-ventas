#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis exploratorio + métricas + gráficos de la base limpia de SpecialModz.

    entrada : data/processed/ventas.csv   (seudonimizado; ver src/anonimizar.py)
    salidas : reports/figuras/*.png       (10 gráficos)
              docs/metricas.json          (métricas para el reporte y el dashboard)

Requiere: pandas, matplotlib  (ver requirements.txt).

Un "pedido" = (id_cliente, fecha_compra). Un pedido puede tener varias filas
(una por tipo_compra detectado); el valor del pedido ya viene repartido entre
sus filas, así que sum(valor_compra) NO sobre-cuenta.
"""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "processed" / "ventas.csv"
FIG = ROOT / "reports" / "figuras"
DOCS = ROOT / "docs"

# --- paleta (dataviz skill: paleta de referencia validada, modo claro) -------
AZUL, NARANJA, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
TINTA, TINTA2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
SURF = "#ffffff"
COLOR_TIPO = {
    "COMPRA DE CONTROL": AZUL,
    "MODIFICACION PROPIA": NARANJA,
    "SERVICIO TECNICO": AQUA,
}
ORDEN_TIPO = ["SERVICIO TECNICO", "MODIFICACION PROPIA", "COMPRA DE CONTROL"]

plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "font.size": 11, "font.family": "DejaVu Sans",
    "text.color": TINTA, "axes.labelcolor": TINTA2, "axes.edgecolor": GRID,
    "xtick.color": TINTA2, "ytick.color": TINTA2,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.axisbelow": True, "figure.dpi": 120,
})
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
         "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
DIAS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]


def _miles(x, _=None):
    return f"{x:,.0f}".replace(",", ".")


def _millones(x, _=None):
    return f"${x/1e6:,.0f}M".replace(",", ".")


def _guardar(fig, nombre):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIG / nombre, bbox_inches="tight")
    plt.close(fig)
    print(f"  fig  reports/figuras/{nombre}")


# ---------------------------------------------------------------------------
def cargar():
    df = pd.read_csv(CSV, sep=";", parse_dates=["fecha_compra"])
    df = df[df["fecha_compra"] >= "2016-01-01"].copy()   # descarta 1 fecha atípica (2003)
    df["anio"] = df["fecha_compra"].dt.year
    df["mes"] = df["fecha_compra"].dt.month
    df["dow"] = df["fecha_compra"].dt.weekday
    df["ym"] = df["fecha_compra"].dt.to_period("M")
    return df


def pedidos(df):
    return (df.groupby(["id_cliente", "fecha_compra"])
              .agg(valor=("valor_compra", "sum"),
                   ntipos=("tipo_compra", "nunique"),
                   ciudad=("ciudad", "first"),
                   anio=("anio", "first"), mes=("mes", "first"), dow=("dow", "first"),
                   ym=("ym", "first"))
              .reset_index())


# ---------------------------------------------------------------------------
def fig_ingresos_mensuales(df):
    agg = df.set_index("fecha_compra")["valor_compra"].resample("MS")
    s, n = agg.sum(), agg.count()
    s = s.where(n > 0)                       # meses sin pedidos -> NaN (corta la línea)
    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.plot(s.index, s.values / 1e6, color=AZUL, lw=2)
    ax.fill_between(s.index, s.values / 1e6, color=AZUL, alpha=0.10)
    hueco = (pd.Timestamp("2021-03-01"), pd.Timestamp("2022-12-31"))
    ax.axvspan(*hueco, color=GRID, alpha=0.25, lw=0)
    ax.text(pd.Timestamp("2022-01-15"), ax.get_ylim()[1] * 0.9,
            "relleno simulado\n2021-03 a 2022-12", ha="center", va="top",
            fontsize=9, color=TINTA2)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}M"))
    ax.set_title("Ingresos mensuales", fontweight="bold", loc="left")
    ax.set_ylabel("millones COP")
    ax.margins(x=0.01)
    _guardar(fig, "01_ingresos_mensuales.png")


def fig_anual(df, ped):
    g = ped.groupby("anio").agg(pedidos=("valor", "size"),
                                ingresos=("valor", "sum"))
    g = g.reindex(range(g.index.min(), g.index.max() + 1), fill_value=0)
    parciales = {2016, 2017, 2021, 2022, 2024, 2025}   # años con datos simulados
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
    colores = [GRID if y in parciales else AZUL for y in g.index]
    a1.bar(g.index.astype(str), g["pedidos"], color=colores)
    a1.set_title("Pedidos por año", fontweight="bold", loc="left")
    a2.bar(g.index.astype(str), g["ingresos"] / 1e6,
           color=[GRID if y in parciales else AQUA for y in g.index])
    a2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}M"))
    a2.set_title("Ingresos por año", fontweight="bold", loc="left")
    for a in (a1, a2):
        a.tick_params(axis="x", rotation=45)
    fig.text(0.5, -0.03, "gris = año con cobertura parcial o con datos simulados "
             "(2016-2017 arranque, 2021-2022 relleno de hueco, 2024-2025 cola simulada)",
             ha="center", fontsize=9, color=TINTA2)
    _guardar(fig, "02_pedidos_ingresos_anuales.png")


def fig_mix_tipo(df):
    lin = df["tipo_compra"].value_counts().reindex(ORDEN_TIPO)
    ingr = df.groupby("tipo_compra")["valor_compra"].sum().reindex(ORDEN_TIPO)
    fig, ax = plt.subplots(figsize=(10, 2.8))
    datos = {"Ingresos": ingr / ingr.sum(), "Líneas de pedido": lin / lin.sum()}
    y = range(len(datos))
    izq = [0.0, 0.0]
    for t in ORDEN_TIPO:
        vals = [datos[k][t] for k in datos]
        ax.barh(list(y), vals, left=izq, color=COLOR_TIPO[t], label=t.title(),
                height=0.55)
        for i, v in enumerate(vals):
            if v > 0.04:
                ax.text(izq[i] + v / 2, i, f"{v*100:.0f}%", ha="center",
                        va="center", color="white", fontweight="bold", fontsize=10)
            izq[i] += v
    ax.set_yticks(list(y))
    ax.set_yticklabels(list(datos.keys()))
    ax.set_xlim(0, 1)
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.grid(False)
    ax.set_title("Mezcla de negocio por tipo de compra", fontweight="bold", loc="left")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=3, frameon=False)
    _guardar(fig, "03_mix_tipo_compra.png")


def fig_ticket_tipo(df):
    fig, ax = plt.subplots(figsize=(8.6, 4))
    q3max = max(df.loc[df.tipo_compra == t, "valor_compra"].quantile(.75)
                for t in ORDEN_TIPO)
    for i, t in enumerate(ORDEN_TIPO):
        v = df.loc[df["tipo_compra"] == t, "valor_compra"]
        q1, med, q3 = v.quantile([.25, .5, .75])
        ax.barh(i, med, color=COLOR_TIPO[t], height=0.5)
        ax.hlines(i, q1, q3, color=TINTA, lw=2)
        ax.plot([q1, q3], [i, i], "|", color=TINTA, ms=10)
        ax.text(q3, i, f"  mediana ${med:,.0f}".replace(",", "."),
                fontsize=9, color=TINTA2, va="center")
    ax.set_yticks(range(len(ORDEN_TIPO)))
    ax.set_yticklabels([t.title() for t in ORDEN_TIPO])
    ax.set_ylim(-0.6, len(ORDEN_TIPO) - 0.4)
    ax.set_xlim(0, q3max * 1.7)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(_miles))
    ax.set_xlabel("valor por línea (COP) — barra = mediana, línea = rango intercuartil")
    ax.set_title("Valor típico por tipo de compra", fontweight="bold", loc="left")
    _guardar(fig, "04_ticket_por_tipo.png")


def fig_ciudades(ped):
    g = ped["ciudad"].value_counts().head(12)[::-1]
    col = [NARANJA if c == "BOGOTA" else AZUL for c in g.index]
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.barh(g.index.str.title(), g.values, color=col)
    ax.set_xlim(0, g.max() * 1.12)
    for i, v in enumerate(g.values):
        ax.text(v, i, f" {v:,}".replace(",", "."), va="center", fontsize=9,
                color=TINTA2)
    share = (ped["ciudad"] == "BOGOTA").mean()
    ax.set_title(f"Top ciudades por nº de pedidos  ·  Bogotá = {share*100:.0f}% del total",
                 fontweight="bold", loc="left")
    ax.grid(axis="y")
    _guardar(fig, "05_top_ciudades.png")


def fig_estacional_mes(ped):
    # índice estacional: promedio de pedidos por mes usando años completos
    comp = ped[ped["anio"].isin([2018, 2019, 2020, 2023])]
    g = comp.groupby("mes").size() / comp["anio"].nunique()
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.bar([MESES[m - 1] for m in g.index], g.values, color=AZUL)
    ax.axhline(g.mean(), color=TINTA2, ls="--", lw=1)
    ax.text(-0.4, g.mean(), f"promedio {g.mean():.0f}", va="bottom", ha="left",
            fontsize=9, color=TINTA2)
    ax.set_ylabel("pedidos / mes (años completos)")
    ax.set_title("Estacionalidad por mes del año", fontweight="bold", loc="left")
    ax.grid(axis="x")
    _guardar(fig, "06_estacionalidad_mes.png")


def fig_estacional_dia(ped):
    g = ped.groupby("dow").size().reindex(range(7), fill_value=0)
    g = g / g.sum()
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.bar(DIAS, g.values * 100, color=[AZUL] * 6 + [GRID])
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax.set_ylabel("% de pedidos")
    ax.set_title("Distribución de pedidos por día de la semana",
                 fontweight="bold", loc="left")
    ax.grid(axis="x")
    _guardar(fig, "07_estacionalidad_dia.png")


def fig_recurrencia(ped, df):
    pc = ped.groupby("id_cliente").size()
    nuevos, recur = (pc == 1).sum(), (pc >= 2).sum()
    rev = df.merge(pc.rename("n"), on="id_cliente")
    rev_rec = rev.loc[rev["n"] >= 2, "valor_compra"].sum() / df["valor_compra"].sum()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8))
    a1.bar(["1 pedido", "2+ pedidos"], [nuevos, recur], color=[AZUL, NARANJA])
    for i, v in enumerate([nuevos, recur]):
        a1.text(i, v, f"{v:,}".replace(",", "."), ha="center", va="bottom", fontsize=10)
    a1.set_title("Clientes por nº de pedidos", fontweight="bold", loc="left")
    a1.grid(axis="x")
    a2.bar(["Clientes\nrecurrentes", "Ingresos de\nrecurrentes"],
           [recur / len(pc) * 100, rev_rec * 100], color=NARANJA)
    a2.yaxis.set_major_formatter(mticker.PercentFormatter())
    for i, v in enumerate([recur / len(pc) * 100, rev_rec * 100]):
        a2.text(i, v, f"{v:.0f}%", ha="center", va="bottom", fontsize=10)
    a2.set_title("Peso de los clientes recurrentes", fontweight="bold", loc="left")
    a2.grid(axis="x")
    _guardar(fig, "08_recurrencia_clientes.png")


def fig_distribucion_valor(ped):
    v = ped["valor"].clip(upper=900_000)
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.hist(v, bins=36, color=AZUL, alpha=0.9)
    med = ped["valor"].median()
    ax.axvline(med, color=NARANJA, lw=2)
    ax.text(med, ax.get_ylim()[1] * 0.92, f" mediana ${med:,.0f}".replace(",", "."),
            color=NARANJA, fontsize=9)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(_miles))
    ax.set_xlabel("valor del pedido (COP; recortado a $900k)")
    ax.set_ylabel("nº de pedidos")
    ax.set_title("Distribución del valor por pedido", fontweight="bold", loc="left")
    ax.grid(axis="x")
    _guardar(fig, "09_distribucion_valor_pedido.png")


def fig_bundling(ped):
    g = ped["ntipos"].value_counts().sort_index()
    g.index = [f"{i} tipo" + ("s" if i > 1 else "") for i in g.index]
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.bar(g.index, g.values, color=[AZUL, NARANJA, AQUA][:len(g)])
    for i, v in enumerate(g.values):
        ax.text(i, v, f"{v:,}\n{v/g.sum()*100:.0f}%".replace(",", "."),
                ha="center", va="bottom", fontsize=9, color=TINTA2)
    ax.set_title("Pedidos según cuántos tipos de compra combinan",
                 fontweight="bold", loc="left")
    ax.grid(axis="x")
    ax.margins(y=0.18)
    _guardar(fig, "10_combinacion_tipos.png")


# ---------------------------------------------------------------------------
def metricas(df, ped):
    pc = ped.groupby("id_cliente").size()
    rev = df.merge(pc.rename("n"), on="id_cliente")
    combos = (df.groupby(["id_cliente", "fecha_compra"])["tipo_compra"]
                .apply(lambda g: " + ".join(sorted(set(g)))).value_counts())
    comp = ped[ped["anio"].isin([2018, 2019, 2020, 2023])]
    m = {
        "filas": int(len(df)),
        "pedidos": int(len(ped)),
        "clientes": int(df["id_cliente"].nunique()),
        "ingresos_total": int(df["valor_compra"].sum()),
        "fecha_min": str(df["fecha_compra"].min().date()),
        "fecha_max": str(df["fecha_compra"].max().date()),
        "ticket_medio_pedido": int(ped["valor"].mean()),
        "ticket_mediano_pedido": int(ped["valor"].median()),
        "mix_lineas": {t: int(v) for t, v in df["tipo_compra"].value_counts().items()},
        "mix_ingresos": {t: int(v) for t, v in
                         df.groupby("tipo_compra")["valor_compra"].sum().items()},
        "ticket_mediano_por_tipo": {t: int(df.loc[df.tipo_compra == t, "valor_compra"].median())
                                    for t in ORDEN_TIPO},
        "bogota_share_pedidos": round((ped["ciudad"] == "BOGOTA").mean(), 4),
        "ciudades_distintas": int(ped["ciudad"].nunique()),
        "top_ciudades": {c: int(v) for c, v in ped["ciudad"].value_counts().head(10).items()},
        "clientes_recurrentes": int((pc >= 2).sum()),
        "share_recurrentes": round((pc >= 2).mean(), 4),
        "ingresos_recurrentes_share": round(
            rev.loc[rev["n"] >= 2, "valor_compra"].sum() / df["valor_compra"].sum(), 4),
        "pedidos_multitipo_share": round((ped["ntipos"] > 1).mean(), 4),
        "combos_top": {k: int(v) for k, v in combos.head(7).items()},
        "estacional_mes": {MESES[k - 1]: round(v, 1) for k, v in
                           (comp.groupby("mes").size() / comp["anio"].nunique()).items()},
        "pico_mes": MESES[(comp.groupby("mes").size()).idxmax() - 1],
        "valle_mes": MESES[(comp.groupby("mes").size()).idxmin() - 1],
        "valor_pedido_p25": int(ped["valor"].quantile(.25)),
        "valor_pedido_p75": int(ped["valor"].quantile(.75)),
        "valor_pedido_p90": int(ped["valor"].quantile(.90)),
    }
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "metricas.json").write_text(
        json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  json docs/metricas.json  ({len(m)} métricas)")
    return m


def main():
    df = cargar()
    ped = pedidos(df)
    print(f"cargado: {len(df):,} filas · {len(ped):,} pedidos · "
          f"{df['id_cliente'].nunique():,} clientes")
    fig_ingresos_mensuales(df)
    fig_anual(df, ped)
    fig_mix_tipo(df)
    fig_ticket_tipo(df)
    fig_ciudades(ped)
    fig_estacional_mes(ped)
    fig_estacional_dia(ped)
    fig_recurrencia(ped, df)
    fig_distribucion_valor(ped)
    fig_bundling(ped)
    metricas(df, ped)
    print("listo.")


if __name__ == "__main__":
    main()
