#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera dashboard/index.html: un tablero de una página, autocontenido (los
gráficos van embebidos en base64), a partir de docs/metricas.json y los PNG de
reports/figuras/. Reproducible: correr de nuevo reescribe el archivo.
"""

import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "reports" / "figuras"
OUT = ROOT / "dashboard" / "index.html"
M = json.loads((ROOT / "docs" / "metricas.json").read_text(encoding="utf-8"))


def img(nombre: str) -> str:
    b64 = base64.b64encode((FIG / nombre).read_bytes()).decode()
    return f"data:image/png;base64,{b64}"


def cop(n: int) -> str:
    return f"${n:,.0f}".replace(",", ".")


KPIS = [
    ("Pedidos analizados", f"{M['pedidos']:,}".replace(",", "."), "una fila por pedido-tipo"),
    ("Clientes únicos", f"{M['clientes']:,}".replace(",", "."), "por orden de 1ª compra"),
    ("Ingresos (real + simulado)", f"${M['ingresos_total']/1e6:,.0f} M".replace(",", "."), "reparto conserva la suma"),
    ("Ticket mediano / pedido", cop(M["ticket_mediano_pedido"]), f"media {cop(M['ticket_medio_pedido'])}"),
    ("Participación de Bogotá", f"{M['bogota_share_pedidos']*100:.0f}%", f"{M['ciudades_distintas']} municipios en total"),
    ("Pedidos recuperados", "98%", "de 4.173 filas de origen"),
]

mod_ing = M["mix_ingresos"]["MODIFICACION PROPIA"] / sum(M["mix_ingresos"].values())
st_lin = M["mix_lineas"]["SERVICIO TECNICO"] / sum(M["mix_lineas"].values())

SECCIONES = [
    dict(
        n="01", tema="Mezcla de negocio",
        titulo="La modificación es el motor; el servicio técnico es el gancho",
        figs=["03_mix_tipo_compra.png", "04_ticket_por_tipo.png"],
        hallazgo=(
            f"<b>Modificación propia</b> genera el {mod_ing*100:.0f}% de los ingresos "
            f"con el ticket unitario más alto (mediana {cop(M['ticket_mediano_por_tipo']['MODIFICACION PROPIA'])}). "
            f"<b>Servicio técnico</b> es el {st_lin*100:.0f}% de las líneas pero solo el "
            f"{M['mix_ingresos']['SERVICIO TECNICO']/sum(M['mix_ingresos'].values())*100:.0f}% de los ingresos "
            f"(mediana {cop(M['ticket_mediano_por_tipo']['SERVICIO TECNICO'])}): alto volumen, bajo valor por línea."),
        reco=(
            "Guion de mostrador para subir de servicio a modificación cuando entra "
            "un control a mantenimiento. Medir margen por tipo (falta el costo) para "
            "confirmar que modificación es lo más rentable, no solo lo de mayor ticket."),
    ),
    dict(
        n="02", tema="Ingresos y estacionalidad",
        titulo=f"Diciembre casi dobla a marzo; el pico es noviembre–enero",
        figs=["01_ingresos_mensuales.png", "06_estacionalidad_mes.png", "07_estacionalidad_dia.png"],
        hallazgo=(
            f"Pico en <b>{M['pico_mes'].lower()}</b> (regalos y prima), valle en "
            f"<b>{M['valle_mes'].lower()}</b> — diciembre ≈ 2× marzo. Repunte secundario "
            "en julio. El domingo el taller casi no opera (0,5%); el martes es el día "
            "más cargado."),
        reco=(
            "Planear inventario y turnos por temporada: reforzar oct–dic, no "
            "sobre-contratar en el primer trimestre. Promoción de temporada baja "
            "(feb–abr) para nivelar la carga del taller."),
    ),
    dict(
        n="03", tema="Cross-sell",
        titulo="4 de cada 10 pedidos ya combinan varios servicios",
        figs=["10_combinacion_tipos.png"],
        hallazgo=(
            f"El <b>{M['pedidos_multitipo_share']*100:.0f}%</b> de los pedidos incluyen "
            "2 o 3 tipos de compra. Los combos más frecuentes son "
            "<b>control + modificación</b> y <b>modificación + servicio</b>: quien "
            "compra un control casi siempre lo manda a modificar."),
        reco=(
            "Formalizar el combo «control nuevo + modificación» como un SKU con "
            "precio de paquete — hoy ocurre solo de forma orgánica. Bundle "
            "«mantenimiento + 1 mejora» para la base que solo ha pagado servicio."),
    ),
    dict(
        n="04", tema="Geografía",
        titulo=f"El {M['bogota_share_pedidos']*100:.0f}% del negocio es Bogotá",
        figs=["05_top_ciudades.png"],
        hallazgo=(
            "Medellín (2º) y Cali (3º) juntos no llegan al 7%. En el tramo 2024 "
            "Bogotá sube a ~99%. La cola de 196 municipios es mínima."),
        reco=(
            "Doble apuesta: profundizar Bogotá (referidos, recompra) y un piloto "
            "de envío nacional a Medellín y Cali para saber si afuera falta "
            "demanda o falta logística."),
    ),
    dict(
        n="05", tema="Clientes",
        titulo="La recompra es la oportunidad barata",
        figs=["08_recurrencia_clientes.png", "09_distribucion_valor_pedido.png"],
        hallazgo=(
            f"Solo el <b>{M['share_recurrentes']*100:.0f}%</b> de los clientes vuelve "
            f"(registro), y ese grupo aporta el <b>{M['ingresos_recurrentes_share']*100:.0f}%</b> "
            "de los ingresos. Es un piso: sin teléfono ni documento en la fuente, "
            "la recompra real es mayor."),
        reco=(
            "Capturar teléfono o documento en cada pedido (es el identificador que "
            "falta). Recordatorio de mantenimiento cada 6–12 meses por WhatsApp: "
            "ingreso incremental barato sobre 4.000+ clientes."),
    ),
]

CSS = """
:root{
  --ground:#f4f5f7; --surface:#ffffff; --chart-paper:#ffffff;
  --ink:#161a24; --muted:#5c6473; --hair:#e2e4ea;
  --accent:#2a78d6; --accent-ink:#1b5798;
  --mod:#eb6834; --serv:#1baf7a;
  --warn-bg:#fdf3e3; --warn-ink:#9a6a12; --warn-line:#e8c684;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme=light]){
    --ground:#0d1017; --surface:#141924; --chart-paper:#ffffff;
    --ink:#e7e9f0; --muted:#98a1b3; --hair:#252c3a;
    --accent:#4f97e8; --accent-ink:#8fbdf0;
    --warn-bg:#2a2113; --warn-ink:#e6b95f; --warn-line:#5a4a2a;
  }
}
:root[data-theme=dark]{
  --ground:#0d1017; --surface:#141924; --chart-paper:#ffffff;
  --ink:#e7e9f0; --muted:#98a1b3; --hair:#252c3a;
  --accent:#4f97e8; --accent-ink:#8fbdf0;
  --warn-bg:#2a2113; --warn-ink:#e6b95f; --warn-line:#5a4a2a;
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);
  font-family:"IBM Plex Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  line-height:1.6;-webkit-font-smoothing:antialiased}
.wrap{max-width:1080px;margin:0 auto;padding:16px;padding-block:clamp(28px,6vw,64px)}
h1,h2,h3{font-family:"Chakra Petch","IBM Plex Sans",sans-serif;text-wrap:balance;
  line-height:1.15;font-weight:600;letter-spacing:-.01em}
h1{font-size:clamp(1.9rem,5vw,3rem);margin:0 0 .3em}
.lede{font-size:1.12rem;color:var(--muted);max-width:60ch;margin:0}
.eyebrow{font-family:"IBM Plex Mono",monospace;font-size:.72rem;letter-spacing:.16em;
  text-transform:uppercase;color:var(--accent-ink);margin:0 0 .5em}
.tag{font-family:"IBM Plex Mono",monospace;font-size:.72rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--muted)}
.banner{display:flex;gap:14px;align-items:flex-start;margin-top:28px;padding:14px 18px;
  background:var(--warn-bg);border:1px solid var(--warn-line);border-radius:10px;
  color:var(--warn-ink);font-size:.92rem}
.banner b{color:var(--warn-ink)}
.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--hair);
  border:1px solid var(--hair);border-radius:14px;overflow:hidden;margin:36px 0 8px}
.kpi{background:var(--surface);padding:18px 18px 16px}
.kpi .v{font-family:"Chakra Petch",sans-serif;font-size:clamp(1.5rem,4vw,2.1rem);
  font-weight:600;font-variant-numeric:tabular-nums;letter-spacing:-.02em}
.kpi .k{font-size:.86rem;color:var(--ink);margin-top:2px}
.kpi .s{font-size:.78rem;color:var(--muted);font-family:"IBM Plex Mono",monospace}
section.finding{margin-top:52px;border-top:2px solid var(--ink);padding-top:22px}
section.finding h2{font-size:clamp(1.3rem,3.4vw,1.8rem);margin:.1em 0 0}
.charts{display:flex;flex-wrap:wrap;gap:14px;margin:22px 0;justify-content:center}
.charts figure{flex:1 1 340px;max-width:620px;margin:0;background:var(--chart-paper);
  border:1px solid var(--hair);border-radius:10px;padding:10px}
.charts img{display:block;width:100%;height:auto;border-radius:4px}
.readout{display:grid;grid-template-columns:1fr 1fr;gap:18px 28px}
.readout .h{font-size:.98rem}
.readout .r{background:var(--surface);border-left:3px solid var(--accent);
  border-radius:0 8px 8px 0;padding:12px 16px;font-size:.95rem}
.readout .r .tag{display:block;margin-bottom:4px;color:var(--accent-ink)}
footer{margin-top:56px;border-top:1px solid var(--hair);padding-top:20px;
  font-size:.88rem;color:var(--muted)}
footer a{color:var(--accent-ink)}
@media(max-width:640px){
  .kpis{grid-template-columns:repeat(2,1fr)}
  .readout{grid-template-columns:1fr}
}
"""

kpis_html = "\n".join(
    f'<div class="kpi"><div class="v">{v}</div><div class="k">{k}</div>'
    f'<div class="s">{s}</div></div>' for k, v, s in KPIS)

secs_html = ""
for sec in SECCIONES:
    figs = "\n".join(
        f'<figure><img alt="{sec["tema"]}" src="{img(f)}"></figure>' for f in sec["figs"])
    secs_html += f"""
<section class="finding">
  <p class="eyebrow">{sec['n']} · {sec['tema']}</p>
  <h2>{sec['titulo']}</h2>
  <div class="charts">{figs}</div>
  <div class="readout">
    <p class="h">{sec['hallazgo']}</p>
    <div class="r"><span class="tag">Recomendación</span>{sec['reco']}</div>
  </div>
</section>"""

FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700'
         '&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600'
         '&display=swap" rel="stylesheet">')

BODY = f"""<div class="wrap">
  <p class="eyebrow">SpecialModz · Análisis de datos de ventas</p>
  <h1>De una hoja de Excel de 8 años a decisiones de negocio</h1>
  <p class="lede">Taller colombiano de modificación y reparación de controles de
  videojuego. {M['pedidos']:,} pedidos limpios, {M['clientes']:,} clientes, cinco
  hallazgos con acción.</p>

  <div class="banner">
    <span>&#9888;</span>
    <div><b>Cobertura de datos.</b> Registro real 2016-01 → 2024-07-03
    (con relleno simulado entre 2021-03 y 2022-12) + simulación 2024-07-04 → 2025-11-10.
    Las lecturas estructurales se sostienen en los ~4.100 pedidos reales;
    la recurrencia hay que leerla como piso.</div>
  </div>

  <div class="kpis">
  {kpis_html}
  </div>
  <p class="tag">Cifras: <code>src/analisis.py</code> → <code>docs/metricas.json</code></p>

  {secs_html}

  <footer>
    <p><b>Cómo se hizo.</b> Limpieza en Python solo con librería estándar
    (el <code>.xlsx</code> se lee con <code>zipfile</code> + <code>xml.etree</code>).
    <code>TIPO DE VENTA</code> era texto libre con 3.355 variantes; se clasificó con
    un diccionario de reglas que no adivina. Nombres de cliente reemplazados por
    seudónimos.</p>
    <p>Detalle: <code>docs/analisis_y_recomendaciones.md</code> ·
    <code>docs/metodologia_limpieza.md</code> ·
    <code>docs/reporte_incidencias.md</code></p>
  </footer>
</div>"""

STANDALONE = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SpecialModz · Tablero de ventas</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{FONTS}
<style>{CSS}</style>
</head>
<body>
{BODY}
</body>
</html>
"""

# Fragmento para publicar como Artifact (el host añade doctype/head/body).
FRAGMENT = f'<title>Tablero de Ventas SpecialModz</title>\n{FONTS}\n<style>{CSS}</style>\n{BODY}\n'

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(STANDALONE, encoding="utf-8")
(OUT.parent / "_artifact.html").write_text(FRAGMENT, encoding="utf-8")
kb = OUT.stat().st_size / 1024
print(f"OK  dashboard/index.html  ({kb:,.0f} KB, {len(SECCIONES)} secciones)")
print(f"OK  dashboard/_artifact.html  (fragmento para publicar)")
