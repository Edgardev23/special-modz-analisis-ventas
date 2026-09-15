# Tarea 5 — Relleno SINTÉTICO del hueco 2021-03 → 2022-12

El histórico real no tiene **ninguna fila** entre 2021-03-01 y 2022-12-31 (22 meses). No sabemos si el taller cerró, si se perdieron los registros o algo intermedio — el archivo fuente simplemente salta de 2021-02 a 2023-01. Este relleno es una **estimación**, no una reconstrucción de lo ocurrido.

## Método

- **Estacionalidad**: participación promedio de cada mes en el año, calculada sobre los años completos más cercanos al hueco: 2019, 2020, 2023.
- **Nivel**: interpolación lineal (en pedidos/año equivalentes) entre dos anclas reales — ene-feb 2021 (nivel 922.3) y ene-mar 2023 (nivel 1375.2). Como ambas anclas están casi al mismo nivel, la interpolación es prácticamente plana: no asume crecimiento ni caída durante el hueco.
- **Pedidos donantes**: cada pedido sintético copia líneas, tipos, valores y ciudad de un pedido real elegido al azar entre 3038 pedidos reales cercanos en el tiempo (2019, 2020, 2021, 2023, 2021 solo ene-feb). Los valores NO se inflan ni se ajustan.
- **Fecha exacta dentro del mes**: sorteada con el peso por día de semana de todo el histórico real (domingo casi nulo).
- **Nombres**: ficticios colombianos, verificados para no repetir ningún nombre del histórico real ni de los sintéticos de la Tarea 2 (cola 2024-07→2025-11).

## Plan mensual

| mes | nivel interpolado | peso del mes | objetivo | pedidos generados |
|---|--:|--:|--:|--:|
| 2021-03 | 950.0 | 6.13% | 58.2 | 58 |
| 2021-04 | 968.5 | 6.71% | 65.0 | 65 |
| 2021-05 | 987.0 | 7.70% | 76.0 | 76 |
| 2021-06 | 1005.5 | 8.04% | 80.9 | 81 |
| 2021-07 | 1024.0 | 9.25% | 94.7 | 94 |
| 2021-08 | 1042.5 | 7.30% | 76.1 | 76 |
| 2021-09 | 1060.9 | 7.85% | 83.3 | 84 |
| 2021-10 | 1079.4 | 9.05% | 97.7 | 97 |
| 2021-11 | 1097.9 | 10.34% | 113.5 | 113 |
| 2021-12 | 1116.4 | 12.23% | 136.5 | 137 |
| 2022-01 | 1134.9 | 7.99% | 90.7 | 90 |
| 2022-02 | 1153.4 | 7.40% | 85.4 | 86 |
| 2022-03 | 1171.8 | 6.13% | 71.8 | 72 |
| 2022-04 | 1190.3 | 6.71% | 79.9 | 80 |
| 2022-05 | 1208.8 | 7.70% | 93.1 | 93 |
| 2022-06 | 1227.3 | 8.04% | 98.7 | 98 |
| 2022-07 | 1245.8 | 9.25% | 115.2 | 115 |
| 2022-08 | 1264.3 | 7.30% | 92.3 | 92 |
| 2022-09 | 1282.8 | 7.85% | 100.7 | 100 |
| 2022-10 | 1301.2 | 9.05% | 117.8 | 117 |
| 2022-11 | 1319.7 | 10.34% | 136.5 | 137 |
| 2022-12 | 1338.2 | 12.23% | 163.6 | 164 |

## Totales

- **Pedidos sintéticos**: **2125** en 22 meses
- **Líneas sintéticas (filas CSV)**: **3131**
- **Ventas sintéticas totales**: **$503,586,074**

- **2125** nombres ficticios distintos, 0 colisiones con el histórico real ni con la Tarea 2.


## Notas

- **No es un pronóstico ni una reconstrucción**: es un relleno estadístico para que las series de tiempo del dashboard no tengan un salto de 22 meses. Cualquier lectura de crecimiento/caída *dentro* del hueco no tiene respaldo real — solo los extremos (ene-feb 2021 y ene-mar 2023) son datos reales.

- **Semilla fija** (`SEED=20260915`) ⇒ reproducible.

- **Fuera de alcance** (igual que las tareas anteriores): no se crean ni cargan tablas SQL; esto es solo el extracto tabular.

