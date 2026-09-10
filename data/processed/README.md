# data/processed/ — dataset publicado

## `ventas.csv`  (7.434 filas · separador `;` · UTF-8)

Una fila por **pedido-tipo**. Un pedido puede aparecer en varias filas (una por
categoría de compra detectada); el valor del pedido ya viene **repartido** entre
esas filas, así que `SUM(valor_compra)` **no** sobre-cuenta los ingresos.

| Columna | Tipo | Descripción |
|---|---|---|
| `id_cliente` | texto | `SM-00001`… asignado por orden de primera compra. El mismo cliente conserva su código. |
| `fecha_compra` | fecha `YYYY-MM-DD` | fecha del pedido |
| `nombre_cliente` | texto | **seudónimo** colombiano, estable por `id_cliente` (ver aviso de privacidad) |
| `ciudad` | texto | ciudad normalizada (mayúsculas, sin tildes, typos corregidos) |
| `valor_compra` | entero (COP) | parte del valor del pedido que corresponde a esta fila |
| `tipo_compra` | categoría | `SERVICIO TECNICO` · `MODIFICACION PROPIA` · `COMPRA DE CONTROL` |

> **Privacidad.** `nombre_cliente` NO es real. Los nombres originales se
> reemplazaron por seudónimos en [`src/anonimizar.py`](../../src/anonimizar.py).
> `id_cliente`, fechas, ciudades y valores sí son los del negocio.

> **Cobertura.** Real 2016-01 → 2024-07-03 (sin registros 2021-03 → 2022-12) +
> simulación 2024-07-04 → 2025-11-10. Ver
> [`docs/analisis_y_recomendaciones.md`](../../docs/analisis_y_recomendaciones.md).

## Archivos de auditoría (sin datos personales)

| Archivo | Qué contiene |
|---|---|
| `correcciones_ciudad.csv` | cada corrección de ciudad aplicada: `original → corregida` + frecuencia |
| `tipos_sin_clasificar.csv` | fragmentos de `TIPO DE VENTA` que el diccionario no reconoció, con ejemplo de celda |
