# SpecialModz · Limpieza y análisis de datos de ventas

*[English version →](README.en.md)*

Proyecto de datos de punta a punta sobre la base de clientes de **SpecialModz**,
un taller colombiano de **modificación y reparación de controles de videojuego**.
Parte de una hoja de Excel de 8 años llena de texto libre y termina en un
dataset limpio, un set de métricas y un tablero de recomendaciones de negocio.

> **Privacidad.** La fuente tiene ~4.300 nombres reales de clientes. Nada de eso
> se publica: el Excel original y los intermedios están en `.gitignore`, y el
> único dataset del repo (`data/processed/ventas.csv`) tiene los nombres
> reemplazados por **seudónimos** consistentes por cliente
> ([`src/anonimizar.py`](src/anonimizar.py)). Cumple con la Ley 1581 de 2012.

---

## Qué hay en el repo

| Etapa | Script | Entrada → salida |
|---|---|---|
| 1. Limpieza | [`src/limpieza_clientes.py`](src/limpieza_clientes.py) | Excel crudo → CSV tabular (5 columnas) |
| 2. Simulación | [`src/generar_sinteticos.py`](src/generar_sinteticos.py) | 2024 real → proyección jul-2024 a nov-2025 |
| 3. Integración | [`src/integrar_database.py`](src/integrar_database.py) | + `id_cliente` por orden de 1ª compra |
| 4. Anonimización | [`src/anonimizar.py`](src/anonimizar.py) | nombres reales → seudónimos |
| 5. Análisis | [`src/analisis.py`](src/analisis.py) | CSV → 10 gráficos + `metricas.json` |

La limpieza (etapas 1-3) usa **solo la librería estándar de Python** — el `.xlsx`
se lee con `zipfile` + `xml.etree`, sin `pandas` ni `openpyxl`. El análisis
(etapa 5) sí usa `pandas` + `matplotlib`.

```
src/                código del pipeline (+ diccionarios de reglas)
data/processed/     dataset publicado (anonimizado) + diccionario de datos
data/raw/           fuente — NO versionada (privacidad)
reports/figuras/    los 10 gráficos (PNG)
docs/               metodología, reporte de incidencias, análisis y recomendaciones
sql/                esquema y carga de referencia (SQL Server)
dashboard/          tablero HTML de una página
```

## El problema de limpieza

La columna `TIPO DE VENTA` era texto libre: **3.355 valores distintos** en 4.173
filas, con varios servicios mezclados en una celda, abreviaturas y errores de
tipeo (`MANTENIMIENTO` aparece como `MTTO`, `MTO`, `MANTEMNIMIENTO`…). Se
resolvió con un **diccionario de reglas** ([`src/diccionario_tipos.py`](src/diccionario_tipos.py))
que parte cada celda, clasifica cada fragmento en una de 3 categorías
(`SERVICIO TECNICO`, `MODIFICACION PROPIA`, `COMPRA DE CONTROL`) y **no adivina**:
lo que no reconoce va a un reporte para revisión manual.

Además: 228 fechas escritas a mano (`13/4/2019`, `' 24/05/2018'`), 343 variantes
de ciudad corregidas contra un listado de municipios, y filas sin valor
excluidas. Detalle completo en [`docs/metodologia_limpieza.md`](docs/metodologia_limpieza.md)
y [`docs/reporte_incidencias.md`](docs/reporte_incidencias.md).

**Resultado:** 98 % de los pedidos recuperados → 5.996 filas limpias (una por
pedido-tipo), con el cuadre de ingresos conservado.

## Hallazgos principales

<p align="center">
  <img src="reports/figuras/03_mix_tipo_compra.png" width="80%"><br>
  <img src="reports/figuras/01_ingresos_mensuales.png" width="80%">
</p>

1. **Concentración en Bogotá** — 74 % de los pedidos (≈99 % en 2024).
2. **La modificación es el motor** — 50 % de los ingresos, ticket unitario más alto.
   El servicio técnico es alto volumen / bajo valor: funciona como gancho.
3. **Cross-sell orgánico** — 40 % de los pedidos combinan 2-3 tipos; el combo
   *control + modificación* es el más frecuente.
4. **Estacionalidad fuerte** — diciembre ≈ 2× marzo; valle en feb-abr.
5. **Base transaccional** — solo 13 % de clientes vuelve (piso), pero aportan
   22 % de los ingresos.

→ Análisis completo con recomendaciones accionables:
**[`docs/analisis_y_recomendaciones.md`](docs/analisis_y_recomendaciones.md)**
· tablero: **[`dashboard/index.html`](dashboard/index.html)**

## Reproducir

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
./run.sh
```

`run.sh` regenera el análisis y los gráficos desde el CSV anonimizado del repo.
Las etapas 1-4 (limpieza y anonimización) necesitan el Excel original en
`data/raw/` y se omiten si no está.

## Stack

Python 3 (`pandas`, `matplotlib`) · el pipeline de limpieza es *zero-dependency*
· HTML/CSS/JS para el tablero · SQL Server para el esquema de referencia.

## Nota

Los datos de jul-2024 en adelante son una **simulación** con la forma de
2023-2024 (la fuente real termina el 2024-07-03); se integran sin distinción por
decisión del proyecto, y las conclusiones estructurales se sostienen en el tramo
real. Ver [`docs/datos_sinteticos_2024.md`](docs/datos_sinteticos_2024.md).

## Licencia

Código bajo [MIT](LICENSE). Datos de negocio anonimizados, solo con fines de
portafolio.
