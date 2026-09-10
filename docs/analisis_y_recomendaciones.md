# Análisis y recomendaciones — SpecialModz

> Taller colombiano de **modificación y reparación de controles de videojuego**.
> Este documento resume lo que se puede leer en la base ya limpia
> (`data/processed/ventas.csv`) y traduce cada hallazgo en una acción.
>
> Cifras generadas por [`src/analisis.py`](../src/analisis.py) →
> [`docs/metricas.json`](metricas.json). Gráficos en
> [`reports/figuras/`](../reports/figuras).

## Cobertura de los datos (leer primero)

| Tramo | Origen | Nota |
|---|---|---|
| 2016-01 → 2021-02 | registro real | crecimiento del taller |
| 2021-03 → 2022-12 | **sin datos** | 22 meses no registrados en la fuente |
| 2023-01 → 2024-07-03 | registro real | operación madura |
| 2024-07-04 → 2025-11-10 | **simulación** | re-muestreo de pedidos reales de 2024 con estacionalidad; ver [`datos_sinteticos_2024.md`](datos_sinteticos_2024.md) |

Los totales de este informe (7.433 líneas · 5.096 pedidos · 4.276 clientes ·
$1.152 M) mezclan ambos tramos. Las lecturas estructurales (mezcla de negocio,
estacionalidad, geografía, ticket) se sostienen en los **~4.100 pedidos reales**;
la simulación solo prolonga la forma de 2023-2024 y no cambia ninguna conclusión.
Los porcentajes de **recurrencia** hay que leerlos como **piso** (ver §5).

---

## 1. El negocio se concentra casi todo en Bogotá

![Top ciudades](../reports/figuras/05_top_ciudades.png)

- **74 %** de los pedidos son de Bogotá; en el tramo 2024 la cifra sube a ~99 %.
- Hay pedidos de 196 municipios, pero la cola es mínima: Medellín (2º) y Cali
  (3º) juntos no llegan al 7 %.

**Recomendación**
- **Profundizar Bogotá**, que es donde el taller ya gana: programa de referidos,
  recompra y alianzas con tiendas de barrio / cafés de gaming.
- **Piloto de envío nacional** a Medellín y Cali con recogida y entrega por
  transportadora. Sirve para responder una pregunta que hoy no se puede: ¿fuera
  de Bogotá hay poca demanda, o solo falta logística?

## 2. La modificación es el motor de ingresos; el servicio técnico es el gancho

![Mezcla por tipo](../reports/figuras/03_mix_tipo_compra.png)
![Valor por tipo](../reports/figuras/04_ticket_por_tipo.png)

| tipo | % de líneas | % de ingresos | valor mediano / línea |
|---|--:|--:|--:|
| Modificación propia | 42 % | **50 %** | $150.000 |
| Servicio técnico | 38 % | 28 % | $95.000 |
| Compra de control | 20 % | 21 % | $154.000 |

- **Modificación propia** genera la mitad de los ingresos con el ticket unitario
  más alto: es el producto a empujar.
- **Servicio técnico** es mucho volumen y poco valor por línea: funciona como
  **puerta de entrada** de clientes nuevos más que como fuente de margen.

**Recomendación**
- Guion de mostrador para **subir de servicio a modificación**: cuando entra un
  control a mantenimiento, ofrecer el upgrade (gatillos rápidos, antideslizante,
  botones). El puente ya existe — ver §3.
- Medir **margen** por tipo (falta el costo en los datos) para confirmar que
  modificación no solo tiene más ticket sino más utilidad.

## 3. 4 de cada 10 pedidos ya combinan varios servicios

![Combinación de tipos](../reports/figuras/10_combinacion_tipos.png)

- **40 %** de los pedidos incluyen 2 o 3 tipos de compra.
- Combos más frecuentes: **control + modificación** (932 pedidos) y
  **modificación + servicio** (741). El que compra un control casi siempre lo
  manda a modificar.

**Recomendación**
- Formalizar el combo **"control nuevo + modificación"** como un SKU con precio
  de paquete. Hoy ocurre de forma orgánica en ~1 de cada 5 pedidos; volverlo
  oferta explícita sube ticket y ordena el taller.
- Bundle **"mantenimiento + 1 mejora"** con descuento pequeño, apuntado a la
  base que solo ha pagado servicio técnico.

## 4. Estacionalidad fuerte: diciembre dobla a marzo

![Estacionalidad por mes](../reports/figuras/06_estacionalidad_mes.png)
![Estacionalidad por día](../reports/figuras/07_estacionalidad_dia.png)

- Pico en **noviembre-diciembre-enero** (regalos y prima); valle en
  **febrero-abril**. Diciembre ≈ **2×** marzo. Repunte secundario en julio.
- **Domingo** el taller prácticamente no opera (0,5 %); **martes** es el día más
  cargado.

**Recomendación**
- Planear **inventario y personal** por temporada: reforzar compras y turnos de
  oct-dic; no sobre-contratar en el primer trimestre.
- **Promoción de temporada baja** (feb-abr) para nivelar la carga del taller y
  no depender de la punta de fin de año.

## 5. Base muy transaccional — la recompra es la oportunidad barata

![Recurrencia](../reports/figuras/08_recurrencia_clientes.png)

- Solo **13 %** de los clientes vuelve (registro), y ese grupo aporta **22 %**
  de los ingresos: un cliente que regresa vale ~**1,9×** uno que no.
- Este 13 % es un **piso**: la fuente no tiene teléfono ni documento, así que dos
  visitas de la misma persona con el nombre escrito distinto cuentan como dos
  clientes, y el hueco de 2021-2022 corta historiales. La recompra real es mayor.

**Recomendación**
- **Capturar teléfono o documento** en cada pedido (ver §6). Sin identificador
  no hay forma de medir retención, LTV ni de hacer campañas.
- **Recordatorio de mantenimiento** cada 6-12 meses por WhatsApp. Es ingreso
  incremental de bajo costo sobre una base de 4.000+ clientes.

## 6. Qué cambiar en la captura de datos (lo que este proyecto deja claro)

La hoja de Excel actual costó recuperar el 98 % de los pedidos a fuerza de
reglas: `TIPO DE VENTA` traía **3.355 textos distintos** en 4.173 filas, 228
fechas escritas a mano y 343 variantes de ciudad (ver
[`reporte_incidencias.md`](reporte_incidencias.md)).

**Recomendación — formulario con campos estructurados** (Google Forms, AppSheet,
o un POS sencillo):

| Campo | Cómo capturarlo |
|---|---|
| Fecha | automática |
| Cliente | nombre **+ teléfono** (el teléfono es el ID) |
| Ciudad | lista desplegable de municipios |
| Tipo(s) de venta | **casillas**: ☐ servicio técnico ☐ modificación ☐ compra de control |
| Detalle | texto libre, aparte, sin afectar la categoría |
| Valor | un renglón por tipo, no un total a repartir |

Esto elimina ~90 % del trabajo de limpieza a futuro y habilita todo lo de §5.
El catálogo de 3 categorías y el diccionario de
[`src/diccionario_tipos.py`](../src/diccionario_tipos.py) sirven como norma.

## 7. Analítica siguiente (cuando haya ID de cliente real)

- **Cohortes de retención** y **LTV** por mes de primera compra.
- **RFM** (recencia / frecuencia / monto) para segmentar la base y priorizar
  campañas.
- **Margen por tipo y por combo** — requiere sumar costo de repuestos y mano de
  obra a la captura.
- **Elasticidad de precio** del combo control + modificación.

---

### Resumen para la vitrina

| Métrica | Valor |
|---|--:|
| Pedidos analizados | 5.096 |
| Clientes únicos | 4.276 |
| Ingresos totales (real + simulado) | $1.152.812.212 |
| Ticket mediano por pedido | $175.000 |
| Participación de Bogotá | 74 % |
| Ingresos de modificación propia | 50 % |
| Pedidos con 2+ tipos | 40 % |
| Clientes recurrentes (piso) | 13 % → 22 % de los ingresos |
| Mes pico / valle | Diciembre / Marzo |
