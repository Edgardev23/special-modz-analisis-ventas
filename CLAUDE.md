# CLAUDE.md — Proyecto: Extracción y Limpieza de Datos SpecialModz

## 1. Objetivo

Extraer y homogenizar datos de clientes desde una base de datos en Excel
(`1_Base_de_Datos_Clientes_2017.xlsx`) para que Edgar los cargue manualmente
a una base de datos SQL. **El agente NO diseña el esquema SQL ni hace el
INSERT** — su única responsabilidad es entregar datos limpios, consistentes
y en un formato tabular listo para importar (CSV/XLSX).

## 2. Fuente de datos

- Archivo: `1_Base_de_Datos_Clientes_2017.xlsx`
- Hoja a usar: **`Hoja1`** (única con datos reales)
  - Encabezados en la fila 4, datos desde la fila 5 hasta la fila 4182
  - ~4,173 registros, del 2016-01-01 al 2024-07-03
- Ignorar las hojas `BASE DE DATOS DE CLIENTES 2023` y `Hoja2` (casi vacías,
  son plantillas sin datos útiles).
- Columnas de origen: `FECHA COMPRA`, `NOMBRE COMPLETO`, `CIUDAD`,
  `TELEFONO` (no se extrae), `TIPO DE VENTA`, `VALOR VENTA`.

## 3. Columnas de salida

| Columna salida     | Columna origen   | Tipo esperado                                            |
|---------------------|------------------|-----------------------------------------------------------|
| `fecha_compra`       | FECHA COMPRA     | `YYYY-MM-DD`                                               |
| `nombre_cliente`     | NOMBRE COMPLETO  | texto limpio                                                |
| `ciudad`             | CIUDAD           | texto limpio, en mayúsculas, normalizado                    |
| `valor_compra`       | VALOR VENTA      | entero, sin decimales, sin separadores de miles             |
| `tipo_compra`        | TIPO DE VENTA    | uno de: `SERVICIO TECNICO`, `COMPRA DE CONTROL`, `MODIFICACION PROPIA` |

## 4. Reglas de limpieza por campo

### 4.1 `fecha_compra`
- La mayoría de celdas ya son fecha nativa de Excel → convertir a `YYYY-MM-DD`.
- 228 registros tienen la fecha como **texto** en formato `DD/MM/YYYY`, con
  inconsistencias: sin cero inicial (`13/4/2019`), espacios sueltos
  (`' 24/05/2018'`). Parsear asumiendo formato colombiano día/mes/año y
  normalizar al mismo `YYYY-MM-DD`.
- Si una fecha no se puede parsear de ninguna forma, excluir la fila y
  agregarla al reporte de incidencias (ver sección 6).

### 4.2 `nombre_cliente`
- Quitar tabulaciones y saltos de línea al final/inicio (~1,367 registros
  los tienen).
- Colapsar espacios múltiples a uno solo.
- Mantener el texto tal como está escrito (no forzar mayúsculas/minúsculas)
  salvo el trim descrito arriba.

### 4.3 `ciudad`
- Normalizar a mayúsculas, sin tildes ni espacios extra.
- Hay 343 valores distintos con errores de tipeo y variantes
  (`BOGOTA` / `BOOGTA`, `IBAGUE` / `IBAGUE TOLIMA`, etc.).
- **Corregir errores obvios de tipeo** hacia el nombre de municipio/ciudad
  colombiano correcto (comparación contra lista de municipios de Colombia,
  ej. con distancia de edición / fuzzy matching).
- Solo aplicar la corrección automática cuando la confianza sea alta. Si el
  valor es ambiguo o no hay match razonable, dejarlo tal cual y agregarlo al
  reporte de incidencias para que Edgar lo revise manualmente — **no
  inventar ni fusionar ciudades a la fuerza**.
- Producir, junto con el archivo final, un log de las correcciones
  aplicadas (valor original → valor corregido) para que Edgar pueda
  auditarlas.

### 4.4 `valor_compra`
- Ya son enteros sin decimales en casi todos los casos.
- 9 registros no tienen valor de venta → **excluir esas filas** del
  extracto final (decisión confirmada).
- Si aparece algún valor no numérico o corrupto, tratarlo igual que un
  valor faltante: excluir y reportar.

### 4.5 `tipo_compra` (la columna más compleja)

`TIPO DE VENTA` es texto libre y muy heterogéneo: 3,355 valores distintos
sobre ~4,173 filas, muchas veces con varios servicios mezclados en una
misma celda (separados por comas o saltos de línea), por ejemplo:

```
CONSOLA XBOX NEGRA
MANTENIMIENTO

CONTROL XBOX BLANCO # 1
CAMBIO DE ANALOGOS
OBSEQUIO MANTENIMIENTO

CONTROL XBOX NEGRO # 2
CAMBIO DE PULSADOR RB
DOMICILIO RECOGIDA Y ENTREGA
```

**Regla de división confirmada:** si una fila contiene indicios de más de
una categoría, generar **una fila de salida por cada categoría detectada**
(mismo `fecha_compra`, `nombre_cliente` y `ciudad`; ver nota sobre
`valor_compra` en la sección 7 — asunción pendiente de confirmar).

#### Diccionario de clasificación (borrador inicial — ajustar con Edgar)

Basado en el análisis de los fragmentos más frecuentes de `TIPO DE VENTA`:

**`SERVICIO TECNICO`** (reparación/mantenimiento de algo que el cliente ya tiene):
`MANTENIMIENTO`, `MTTO`, `MANTENIMIENTO CONSOLA`, `OBSEQUIO MANTENIMIENTO`,
`CAMBIO DE ANALOGO(S)`, `ARREGLO ANALOGO(S)`, `ARREGLOJOYS`, `ARREJOYS`,
`ANALOINTER`, `CAMBIO DE CAPUCHAS`, `CAMBIO DE MUELLE`, `POTENCIOMETRO`,
`DIAGNOSTICO`, `VENTILADOR`, `CAMBIO DE PULSADOR`, `ACTUALIZACION (DEL) SISTEMA TACTICO`,
`SERVICIO TECNICO` (literal)

**`COMPRA DE CONTROL`** (venta de un control/consola/accesorio nuevo):
`COMPRA`, `CXC`, `CONTROL NUEVO`, `KONTROLFREEK(S)`, `KONTROL FREEK`
- Ojo: fragmentos como `CONTROL PS4`, `CONTROL PS5 BLANCO`, `CONTROL XBOX`
  **no implican compra por sí solos** — casi siempre son solo la etiqueta
  del control que el cliente trajo para servicio/modificación (ej. "control
  # 1", "control # 2"). Solo clasificar como `COMPRA DE CONTROL` cuando el
  texto incluya explícitamente `COMPRA`, `CXC` o `NUEVO`.

**`MODIFICACION PROPIA`** (personalización/mejora que no existía antes):
`DISEÑO`, `DISE`, `DIS`, `ANTIDESLIZANTE`, `ANTIDES`, `ANTIDESL`, `ANTI`,
`MODTAC`, `MODIF TACTICA`, `MODIFICACION TACTICA`, `MOD TACTICA`,
`MODIFIC TACTICA`, `MODTAC4FUN`, `MODIFICACION` (genérico),
`GATILLOS RAPIDOS`, `GATILLOS DE ACTIVACION INMEDIATA`, `RAPIDFIRE`,
`RAPID FIRE`, `CHIP AUTOFIRE`, `AUTOFIRE`, `TOPES`, `BOTONES`,
`KIT DE BOTONES`, `KITBOTYFLE`, `KITALU`, `LOGO`, `NOMBRE EN EL PANEL`

**Ignorar (no generan fila / no son un tipo de compra):**
`DOMICILIO`, `DOMICILIOS`, `DOMICILIO RECOGIDA Y ENTREGA`, `ENVIO`,
`PORCENTAJE 5%` (nota de descuento, no un servicio)

**Casos dudosos a confirmar con Edgar antes de darlos por definitivos:**
- `CAMBIO DE ACETATO` / `ACETATO`: ¿reemplazo de una carcasa dañada
  (servicio técnico) o carcasa personalizada (modificación)?
- `CAMBIO DEL SISTEMA TACTICO`: ¿reparación de un mod ya instalado
  (servicio técnico) o instalación nueva (modificación)?
- `KITPASTA` (kit de pasta térmica): ¿mantenimiento de refrigeración
  (servicio técnico) o parte de un paquete de modificación?
- `CODIGO FORNITE` y otros productos sueltos que no encajan en ninguna
  categoría (ej. venta de códigos de juego): no clasificar a la fuerza —
  excluir del extracto y listarlos aparte para que Edgar decida.

**Regla general:** ante un fragmento de texto no reconocido, el agente
**no debe adivinar** — debe dejarlo fuera de las 3 categorías y añadirlo a
un listado de "tipos sin clasificar" con su frecuencia, para revisión
manual. Es preferible pedir revisión que ensuciar la base de datos con
clasificaciones incorrectas.

## 5. Formato de salida

- Un archivo tabular (CSV o XLSX) con exactamente las 5 columnas de la
  sección 3, una fila por combinación cliente-pedido-tipo detectado.
- Nombre sugerido: `especialmodz_clientes_limpio.csv`.

## 6. Reporte de incidencias (obligatorio, aparte del archivo principal)

Entregar junto con el extracto un resumen con:
- Filas excluidas por falta de valor de venta (con su fila original).
- Fechas que no se pudieron parsear.
- Correcciones de ciudad aplicadas (original → corregido).
- Fragmentos de `TIPO DE VENTA` sin clasificar, con su frecuencia, para que
  Edgar decida cómo mapearlos.

## 7. Decisiones ya confirmadas

- Un pedido con varios tipos de compra → una fila de salida por tipo
  detectado (puede duplicar fecha/cliente/ciudad).
- Se corrigen errores de tipeo obvios en `ciudad`.
- Las 9 filas sin `valor_compra` se excluyen del extracto final.

## 8. Pendiente de definir

- **Valor de compra en filas divididas**: cuando un pedido se separa en
  varias filas por tipo, ¿cada fila lleva el `valor_compra` completo del
  pedido original, o el valor se debe repartir entre las filas generadas?
  Por defecto, mientras no se indique lo contrario, el agente debe **repetir
  el valor completo en cada fila** y dejarlo señalado en el reporte de
  incidencias, porque sumar `valor_compra` directamente en SQL
  sobreestimaría los ingresos totales.

## 9. Fuera de alcance

- No crear ni modificar tablas SQL.
- No hacer el `INSERT`/carga a la base de datos — eso lo hace Edgar.
- No inventar clasificaciones para texto ambiguo.
- No eliminar el archivo Excel original ni sobrescribirlo.
