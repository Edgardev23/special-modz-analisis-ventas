# Tarea 2 — Análisis de la base 2024 y generación de datos sintéticos

Datos **sintéticos** (inventados) para el periodo **2024-07-04 → 2025-11-10**. No son ventas reales.

## 1. Análisis de los datos reales de 2024

> El histórico real de la Tarea 1 termina el **2024-07-03**, así que "2024" aquí significa **enero–junio 2024 (H1)**: **400 pedidos**, **553 líneas**, ventas **$85,525,250**.

### 1.1 valor_compra por tipo_compra (nivel línea, 2024-H1)

| tipo_compra | n | mín | p10 | mediana | media | p90 | máx |
|---|--:|--:|--:|--:|--:|--:|--:|
| SERVICIO TECNICO | 301 | 15,000 | 40,000 | 107,750 | 129,696 | 250,000 | 630,000 |
| MODIFICACION PROPIA | 197 | 15,000 | 64,000 | 140,000 | 167,312 | 294,200 | 497,500 |
| COMPRA DE CONTROL | 55 | 45,000 | 88,550 | 250,000 | 245,930 | 356,500 | 497,500 |

Los valores sintéticos se copian **tal cual** de pedidos reales de 2024, por lo que siempre caen dentro de estos rangos (no se inflan).

### 1.2 Proporción de tipo_compra (nivel línea, 2024-H1)

| tipo_compra | líneas | % |
|---|--:|--:|
| SERVICIO TECNICO | 301 | 54.4% |
| MODIFICACION PROPIA | 197 | 35.6% |
| COMPRA DE CONTROL | 55 | 9.9% |

### 1.3 Distribución de ciudad (nivel pedido, 2024-H1)

| ciudad | pedidos | % |
|---|--:|--:|
| BOGOTA | 395 | 98.75% |
| MEDELLIN | 2 | 0.50% |
| DOSQUEBRADAS | 1 | 0.25% |
| TULUA | 1 | 0.25% |
| SABANETA MEDELLIN | 1 | 0.25% |

2024 es casi 100 % Bogotá. Como la generación re-muestrea pedidos reales completos, la ciudad de cada pedido sintético se hereda del pedido plantilla y la distribución se conserva exactamente.

### 1.4 Estacionalidad — volumen de pedidos por mes

2024-H1 es real; para la forma de jul–dic se usa 2023 (único año reciente completo), anclada al nivel real de 2024-H1.

| mes | pedidos 2023 | pedidos 2024 | base 2024 (usada) |
|---|--:|--:|--:|
| 01 | 99 | 99 | 99.0 |
| 02 | 107 | 53 | 53.0 |
| 03 | 90 | 49 | 49.0 |
| 04 | 76 | 75 | 75.0 |
| 05 | 77 | 68 | 68.0 |
| 06 | 73 | 50 | 50.0 |
| 07 | 79 | 6 | 59.6 *(proy.)* |
| 08 | 63 | — | 47.6 *(proy.)* |
| 09 | 66 | — | 49.8 *(proy.)* |
| 10 | 68 | — | 51.3 *(proy.)* |
| 11 | 87 | — | 65.7 *(proy.)* |
| 12 | 101 | — | 76.2 *(proy.)* |
| **año** | **986** | **400** (parcial) | **744** |

### 1.5 Estacionalidad — pedidos por día de la semana (2023+2024)

| día | pedidos | peso |
|---|--:|--:|
| lunes | 180 | 13.0% |
| martes | 269 | 19.4% |
| miércoles | 228 | 16.5% |
| jueves | 217 | 15.7% |
| viernes | 237 | 17.1% |
| sábado | 248 | 17.9% |
| domingo | 7 | 0.5% |

Domingo es casi nulo (taller cerrado). Dentro de cada mes las fechas sintéticas se sortean con estos pesos.

## 2. Línea base 2024 (referencia de crecimiento)

- Pedidos reales 2024-H1 (ene–jun): **400**
- Ticket medio por pedido 2024-H1: **$213,813**
- **Pedidos 2024 completo (estimado)**: **744** (H1 real + H2 proyectado con la forma de 2023)
- **Ventas 2024 completo (estimado)**: **$159,124,479** (≈ 744 × $213,813)

## 3-4. Periodo sintético generado

- Crecimiento aplicado: **+8%** sobre el número de pedidos mensual de la base 2024 (tasa anual). Solo cambia el **volumen**; los valores por tipo no se tocan.

- **Pedidos sintéticos**: **1046** en 17 meses (2024-07 parcial desde el día 4; 2025-11 parcial hasta el día 10)

- **Líneas sintéticas (filas CSV)**: **1438**

- **Ventas sintéticas totales**: **$221,418,500**

- Mezcla de tipo_compra resultante: SERVICIO TECNICO 56.3%, MODIFICACION PROPIA 35.0%, COMPRA DE CONTROL 8.8% (comparar con 1.2)


### Plan mensual

| mes | base 2024 | fracción activa | objetivo (×1.08) | pedidos generados |
|---|--:|--:|--:|--:|
| 2024-07 | 59.6 | 0.903 | 58.2 | 58 |
| 2024-08 | 47.6 | 1.0 | 51.4 | 51 |
| 2024-09 | 49.8 | 1.0 | 53.8 | 54 |
| 2024-10 | 51.3 | 1.0 | 55.4 | 56 |
| 2024-11 | 65.7 | 1.0 | 70.9 | 71 |
| 2024-12 | 76.2 | 1.0 | 82.3 | 82 |
| 2025-01 | 99 | 1.0 | 106.9 | 107 |
| 2025-02 | 53 | 1.0 | 57.2 | 57 |
| 2025-03 | 49 | 1.0 | 52.9 | 53 |
| 2025-04 | 75 | 1.0 | 81.0 | 81 |
| 2025-05 | 68 | 1.0 | 73.4 | 74 |
| 2025-06 | 50 | 1.0 | 54.0 | 54 |
| 2025-07 | 59.6 | 1.0 | 64.4 | 64 |
| 2025-08 | 47.6 | 1.0 | 51.4 | 51 |
| 2025-09 | 49.8 | 1.0 | 53.8 | 54 |
| 2025-10 | 51.3 | 1.0 | 55.4 | 55 |
| 2025-11 | 65.7 | 0.333 | 23.6 | 24 |

## 5. Nombres de cliente

- **1046** nombres ficticios distintos, compuestos con nombres y apellidos colombianos comunes.
- Verificado: **0** colisiones con los 3.231 nombres del histórico real (comparación sin tildes / mayúsculas).


## 6. Notas / supuestos

- **2024 incompleto**: el histórico real solo llega a 2024-07-03. La base de jul–dic 2024 es una *proyección* con la estacionalidad de 2023; documentado arriba por si Edgar prefiere otra base.

- **Reparto de valor en pedidos multi-tipo**: se hereda el mismo criterio de la Tarea 1 (partes iguales, la suma del pedido cuadra). Igual que en la Tarea 1, **no sumar `valor_compra` directamente** sin agrupar por pedido: hay filas que comparten el valor de un mismo pedido dividido.

- **Método**: cada pedido sintético = un pedido real de 2024 elegido al azar (con sus líneas, tipos, valores y ciudad) + fecha nueva (estacionalidad) + nombre ficticio. Semilla fija (`SEED=20260829`) ⇒ reproducible.

- **Fuera de alcance** (igual que Tarea 1): no se crean ni cargan tablas SQL; esto es solo el extracto tabular.

