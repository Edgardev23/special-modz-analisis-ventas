# Reporte de incidencias — limpieza base de datos clientes

- Generado: 2026-09-10 17:59
- Archivo fuente: `Doc/1.Base de Datos Clientes 2017.xlsx`, hoja `Hoja1`

## 1. Cuadre de filas

| Concepto | Filas |
|---|---:|
| Leídas del Excel (fila 5 en adelante) | 4178 |
| Excluidas — campos incompletos | 34 |
| Excluidas — fila duplicada exacta | 1 |
| Excluidas — pendiente de clasificar TIPO DE VENTA | 32 |
| Excluidas — solo producto fuera de alcance (código de juego / skin) | 17 |
| **Pedidos que pasan a la salida** | **4094** |
| Filas en el CSV final (tras dividir por tipo) | 5996 |

Cuadre: 4178 leídas = 4094 incluidas + 84 excluidas.

Suma de `valor_compra` en el CSV final: **931,453,712**. Por decisión de Edgar el valor de cada pedido se reparte en partes iguales entre sus filas, así que esta suma SÍ equivale al ingreso real de los pedidos incluidos.

## 2. Filas excluidas (detalle)

### campos incompletos — 34

- fila 185: sin ciudad
- fila 227: sin ciudad
- fila 269: sin valor de venta
- fila 276: sin valor de venta
- fila 278: sin valor de venta
- fila 279: sin ciudad
- fila 288: valor de venta = 0
- fila 293: sin nombre
- fila 331: sin ciudad
- fila 360: sin ciudad
- fila 373: sin ciudad
- fila 437: sin valor de venta
- fila 444: sin valor de venta
- fila 450: sin valor de venta
- fila 476: sin ciudad
- fila 505: sin ciudad
- fila 542: sin nombre
- fila 555: sin ciudad
- fila 945: sin nombre
- fila 1007: sin valor de venta
- fila 1150: sin ciudad
- fila 1193: sin ciudad
- fila 1216: sin ciudad
- fila 2518: sin ciudad
- fila 2519: sin ciudad
- fila 2520: sin ciudad
- fila 2521: sin ciudad
- fila 2522: sin ciudad
- fila 2523: sin ciudad
- fila 2524: sin ciudad; sin valor de venta; sin tipo de venta
- fila 2679: sin valor de venta
- fila 2704: sin ciudad
- fila 2724: sin nombre
- fila 2738: sin nombre

### fila duplicada exacta — 1

- fila 768: [cliente anonimizado] / SANTA ROSA DE OSOS / 2019-08-20 / 340000

### pendiente de clasificar TIPO DE VENTA — 32

- fila 654: fragmentos 'CALZA'  |  celda: 'CXC,DISE,MODTAC,CALZA,KITALUM'
- fila 655: fragmentos 'CARROJA'  |  celda: 'CXC,DIS,CARROJA,RAPIDFIRE,KITALU,MODTAC'
- fila 668: fragmentos 'COLORPT'  |  celda: 'CXXC,DIS,COLORPT,BOTYFLE'
- fila 737: fragmentos 'CAPMETA'  |  celda: 'CXC,MODTAC,ARREGLOEJEY,CAPMETA'
- fila 747: fragmentos 'SHAR', 'PAN', 'TAC'  |  celda: 'COMPRA,DIS,ANTIDESLIZ,KITALUM,SHAR,PAN,TAC'
- fila 819: fragmentos 'SHAYOPT'  |  celda: 'CXC,DISE,KITPASTA,SHAYOPT,ARREGLOL2R2'
- fila 828: fragmentos 'PUL'  |  celda: 'CXC,MODTAC,PUL'
- fila 928: fragmentos 'PULED'  |  celda: 'CXC,DISE,ANTIDES,PULED,RAPIDFIRE,CONSOLPS4,SISREFRIYMANT'
- fila 1380: fragmentos 'GOMITAS BLANCAS'  |  celda: 'ARREGLO 2 CONTROLES, L1, R1 Y GATILLOS,DOMICILIO, GOMITAS BLANCAS,ARREGLO MUELLES, joystciks azules ambos controles'
- fila 1476: fragmentos 'B'  |  celda: 'DOMICILIO,CONTROL 1, DISEÑO MARMOL 3 ROJO,BOTONES A,B,Y, X,CONTROL 2, DISEÑO NARUTO (NUBES),TOPES,TAPA DE UN CONTROL'
- fila 1532: fragmentos 'SOCCER MADNESS'  |  celda: 'CONTROL PS4,DISEÑO MARMOL 3,KIT DE BOTONES,NOMBRE EN EL MANGO, SOCCER MADNESS,NOMBRE EN EL PANEL LEDANTIDESLIZANTE,MODIF TACTICA'
- fila 1555: fragmentos 'B IZ'  |  celda: 'CONTROL XBOX,KIT DE BOTONES EN ROJO,MODIFICACION TACTICA (A DE, B IZ),TOPES,ENVIO'
- fila 1738: fragmentos 'S10 ROJO'  |  celda: 'CONTROL DE ENTREGA INMEDIATA, S10 ROJO'
- fila 2336: fragmentos 'ALPINE GREEN CON'  |  celda: 'ALPINE GREEN CON MODIFICACION TACTICA'
- fila 2384: fragmentos 'ALPINE GREEN ENTREGA INMEDIATA'  |  celda: 'ALPINE GREEN ENTREGA INMEDIATA'
- fila 2454: fragmentos 'ACT'  |  celda: 'ACT, SISTEMA TACT, MANT Y CALIBRAC DE ANALOGOS'
- fila 2491: fragmentos 'EJE Y DE L3'  |  celda: 'EJE Y DE L3, MANTENIMIETNO, CAMBIO DE POTENCIOMETROS, CALIBRACION'
- fila 2674: fragmentos 'INTERC'  |  celda: 'COMPRAEDICIONGALAXY,INTERC'
- fila 2683: fragmentos 'PAYU'  |  celda: 'COMPRA,DISEÑO,ANTIDESLIZ,KITALUMINMIO,NOMBRE,PayU'
- fila 2725: fragmentos 'ANAL'  |  celda: 'COMPRA,DISEÑO,ANTIDESLIZ,BOT,ANAL,FLECH'
- fila 2941: fragmentos 'R3 DERECHA'  |  celda: 'CONTROL 1 CAPUCHAS NUEVAS\tMANTENIMIENTO\tPREVISUALIZACION DISEÑO AMERICA REAL MADRID CONTROL 2\tCAMBIO ANALOGOS MODIFICACION TACTICA 2 FUNCIONES  X, R3 DERECHA MANTENIMIENTO INCLUIDO'
- fila 3039: fragmentos 'IZQUIERDO CUADRO'  |  celda: 'CONTROL PS5\t MODIFICACION TACTICA 4 FUNCIONES (PALETAS ESTANDAR. BOTONES: DERECHO TRIANGULO,  IZQUIERDO CUADRO'
- fila 3060: fragmentos 'X DERECHA'  |  celda: 'CONTROL PS5\tMODIFICACION TACTICA (O izquierdo, X derecha)'
- fila 3067: fragmentos 'DERECHO Y'  |  celda: 'CONTROL XBOX ONE  DISEÑO FANTASMA\tMODIFICACION TACTICA 4 FUNCIONES (PALETAS: Izquierda X, Derecha B.BOTONES: Izquierdo A, Derecho Y)\tCAMBIO DE ANALOGOS \tMTTO'
- fila 3602: fragmentos 'SE'  |  celda: 'CONSOLA PS4\t\t\t\t / MANTENIMIENTO\t\t\t\t / REVISION DE UNIDAD DE CD\t\t\t\t / SE CAMBIO EL VENTILADOR\t\t\t\t / PORCENTAJE 5%'
- fila 3764: fragmentos 'INGRESA CON CD COD'  |  celda: 'CONSOLA PS4 FAT\t\t\t\t / MANTENIMIENTO\t\t\t\t / UNIDAD DE CD SE TRABA\t\t\t\t / INGRESA CON CD COD\t\t\t\t / CONTROL PS4\t\t\t\t / FLEX DE CARGA\t\t\t\t / CAMBIO ANALOGOS\t\t\t\t / MANTENIMIENTO\t\t\t\t / CAMBIO ACETATO\t\t\t\t / CAUCHO R2 L2'
- fila 3885: fragmentos 'SE RECIBE'  |  celda: 'CONTROL PS4 NEGRO NUEVO\t\t\t\t / SE RECIBE CONTROL POR 30000 MIL PESOS'
- fila 3901: fragmentos 'PC'  |  celda: 'PC\t\t\t\t / MANTENIMIENTO'
- fila 3906: fragmentos 'SELE CAMBIA EL'  |  celda: 'CONTROL PS5 NUEVO\t\t\t\t / MODIFICACION TACTICA DE 2 FUNCIONES\t\t\t\t / SELE CAMBIA EL CONTROL COMO GARANTIA YA QUE PRESENTO INCOVENIENTES 16/03/24'
- fila 3910: fragmentos 'EJE X R3'  |  celda: 'MANTENIMIENTO + VENTILADOR PS4 SLIM\t\t\t\t / \t\t\t\t / \t\t\t\t / CONTROL PS4\t\t\t\t / CAMBIO DE ANALOGO IZQUIERDO\t\t\t\t / GATILLO RAPIDO EN R2\t\t\t\t / EJE X R3\t\t\t\t / PULSADOR IZQ MOD TACTICA'
- fila 4113: fragmentos 'SE'  |  celda: 'CONNTROL PS4 AZUL\t\t\t\t / PROMO ANALOGOS + CALIBRACION + MANTENIMIENTO\t\t\t\t / SE COMPRA CONTROL EN 30 MIL PESOS\t\t\t\t / CAMBIO DE CAPUCHAS'
- fila 4165: fragmentos 'AGREGAR'  |  celda: 'CONTROL PS5 BLANCO\t\t\t\t / AGREGAR MODIFICACION DE 2 FUNCIONES EN LA PARTE DE ABAJO'

### solo producto fuera de alcance (código de juego / skin) — 17

- fila 897: celda 'ALQUILER CONTROL PS4'
- fila 1044: celda 'COMPRA SKIN FORTNITE'
- fila 1531: celda 'STRIKE PACK,DOMICILIO'
- fila 1633: celda 'CODIGO FORNITE'
- fila 1636: celda 'CODIGO FORNITE'
- fila 1660: celda 'CODIGO FORNITE'
- fila 1672: celda 'CODIGO FORNITE'
- fila 1709: celda 'CODIGO FORNITE'
- fila 1713: celda 'CODIGO FORNITE'
- fila 1763: celda 'CODIGO FORNITE'
- fila 1828: celda 'CONTROL DE ENTREGA INMEDIATA FORNITE'
- fila 1877: celda 'CODIGO FORNITE'
- fila 1884: celda 'CODIGO FORNITE'
- fila 1907: celda 'CODIGO FORNITE'
- fila 1925: celda 'CODIGO FORNITE'
- fila 2101: celda 'CODIGO FORNITE'
- fila 2138: celda 'CODIGO FORNITE'

## 3. Fechas fuera del rango esperado (se conservan)

- fila 2758: fecha fuera de rango [2016-01-01..2026-09-10]: 2003-01-05 (original '37626')

## 4. Valores de venta con formato inusual (se conservan)

_Ninguno._

## 5. Correcciones de ciudad aplicadas

| Original | Corregida | Veces |
|---|---|---:|
| BOOGTA | BOGOTA | 11 |
| BOGOTOA | BOGOTA | 6 |
| DOSQUEBRADAS RISARALDA | DOSQUEBRADAS | 5 |
| CARTAGENA DE INDIAS | CARTAGENA | 5 |
| DOS QUEBRADAS RISARALDA | DOSQUEBRADAS | 5 |
| DOS QUEBRADAS | DOSQUEBRADAS | 2 |
| FINLANDIA QUINDIO | FILANDIA | 2 |
| CAUCACIA | CAUCASIA | 2 |
| CIUDAD DE CALI | CALI | 2 |
| DOSQUEBRADAS | DOSQUEBRADAS | 2 |
| FLORIDA BLANCA | FLORIDABLANCA | 2 |
| GUADALAJARA DE BUGA VALLE DEL CAUCA | BUGA | 2 |
| GUADALAJARA DE BUGA | BUGA | 2 |
| LACEJA ANTIOQUIA | LA CEJA | 1 |
| SANTAROSADEOSOS ANTIOQUIA | SANTA ROSA DE OSOS | 1 |
| ROZO VALLE | PALMIRA | 1 |
| CARMEN DE VIBORAL | EL CARMEN DE VIBORAL | 1 |
| RODALDILLO | ROLDANILLO | 1 |
| TINTAL BOGOTA | BOGOTA | 1 |
| AMAPOLAS BOGOTA | BOGOTA | 1 |
| PIE DE CUESTA SANT | PIEDECUESTA | 1 |
| CIUDAD BOLIVAR ANT | BOGOTA | 1 |
| DOSQUEBRADAS RISA | DOSQUEBRADAS | 1 |
| POAPYAN | POPAYAN | 1 |
| CATARGO | CARTAGO | 1 |
| CHIA BOGOTA | CHIA | 1 |
| VILLAVIVENCIO | VILLAVICENCIO | 1 |
| CEJA ANTIOQUIA | LA CEJA | 1 |
| TOLIMA ESPINAL | ESPINAL | 1 |
| ENVIGDO | ENVIGADO | 1 |
| MEDELIIN | MEDELLIN | 1 |
| RONALDILLO | ROLDANILLO | 1 |
| CARATENA | CARTAGENA | 1 |
| PIED DE CUESTA | PIEDECUESTA | 1 |
| MDELLIN | MEDELLIN | 1 |
| FONTIBON | BOGOTA | 1 |
| SBANETA ANTIOQUIA | SABANETA | 1 |
| CARTAJO VALLE DEL CAUCA | CARTAGO | 1 |
| SAN JOSE DEL GUAVAIRE | SAN JOSE DEL GUAVIARE | 1 |
| DOS QUEBRDAS RISARALDA | DOSQUEBRADAS | 1 |

Detalle completo en `correcciones_ciudad.csv`.

## 6. Ciudades NO reconocidas (revisar a mano — se dejaron tal cual)

| Ciudad (normalizada) | Veces |
|---|---:|
| ANTIOQUIA | 7 |
| SANTANDER | 3 |
| ATLANTICO | 2 |
| META | 2 |
| JAMUNDI ALFAGUARA | 2 |
| TAUREMENA | 1 |
| LOS PATIOS CUCUTA | 1 |
| RISARALDA | 1 |
| NORTE DE SANTANDER | 1 |
| EL POBLADO MEDELLIN | 1 |
| URUBIA GUAJIRA | 1 |
| EL GUAMO TOL | 1 |
| YULIMA ARMENIA | 1 |
| UMBRIA RISARALDA | 1 |
| OFICINA | 1 |
| VILLANUEVA COPACABANA | 1 |
| PATALITO | 1 |
| PLATA MAGDALENA | 1 |
| VALLE DEL CAUCA | 1 |
| RISALDA PEREIRA | 1 |
| ATLANTICO SOLEDAD | 1 |
| DOSQUEBRADAS PEREIRA | 1 |
| MEDELLIN BELLO | 1 |
| MUNICIPIO DE CAJICA CUNDINAMARCA | 1 |
| UBIRIA LA GUAJIRA | 1 |
| VEDA VERGANZO | 1 |
| BELLO MEDELLIN | 1 |
| PASTO NACIO | 1 |
| DOS QUEBRADA PEREIRA | 1 |
| LA CALERA DEPARTAMENTO CUNDINAMARCA | 1 |
| DORALDA ANTIOQUIA | 1 |
| ESTADOS UNIDOS | 1 |
| MEDELLIN SABANETA | 1 |
| GUAYMARAL | 1 |
| MUNICIPIO DE LOS PATIOS | 1 |
| FLORIDABLANCA SAN | 1 |
| NORTE DE SANTNDER | 1 |
| CUNDINAMARCA | 1 |
| CATAN | 1 |
| TIOQUIA | 1 |
| CESAR | 1 |
| SABANETA MEDELLIN | 1 |

## 7. Fragmentos de TIPO DE VENTA sin clasificar

33 fragmentos distintos sin resolver (0 ambiguos + 33 desconocidos). **Las filas que los contienen NO están en el CSV final.** Revisa `tipos_sin_clasificar.csv`, asigna categoría y volvemos a correr.

| Fragmento | Frecuencia | Motivo |
|---|---:|---|
| SE | 2 | DESCONOCIDO |
| CALZA | 1 | DESCONOCIDO |
| CARROJA | 1 | DESCONOCIDO |
| COLORPT | 1 | DESCONOCIDO |
| CAPMETA | 1 | DESCONOCIDO |
| SHAR | 1 | DESCONOCIDO |
| PAN | 1 | DESCONOCIDO |
| TAC | 1 | DESCONOCIDO |
| SHAYOPT | 1 | DESCONOCIDO |
| PUL | 1 | DESCONOCIDO |
| PULED | 1 | DESCONOCIDO |
| GOMITAS BLANCAS | 1 | DESCONOCIDO |
| B | 1 | DESCONOCIDO |
| SOCCER MADNESS | 1 | DESCONOCIDO |
| B IZ | 1 | DESCONOCIDO |
| S10 ROJO | 1 | DESCONOCIDO |
| ALPINE GREEN CON | 1 | DESCONOCIDO |
| ALPINE GREEN ENTREGA INMEDIATA | 1 | DESCONOCIDO |
| ACT | 1 | DESCONOCIDO |
| EJE Y DE L3 | 1 | DESCONOCIDO |
| INTERC | 1 | DESCONOCIDO |
| PAYU | 1 | DESCONOCIDO |
| ANAL | 1 | DESCONOCIDO |
| R3 DERECHA | 1 | DESCONOCIDO |
| IZQUIERDO CUADRO | 1 | DESCONOCIDO |
| X DERECHA | 1 | DESCONOCIDO |
| DERECHO Y | 1 | DESCONOCIDO |
| INGRESA CON CD COD | 1 | DESCONOCIDO |
| SE RECIBE | 1 | DESCONOCIDO |
| PC | 1 | DESCONOCIDO |
| SELE CAMBIA EL | 1 | DESCONOCIDO |
| EJE X R3 | 1 | DESCONOCIDO |
| AGREGAR | 1 | DESCONOCIDO |

## 8. Pedidos divididos en varias filas (reparto de valor)

1681 pedidos se dividieron en 2+ filas. Ejemplos:

| Fila Excel | Valor pedido | Nº filas | Reparto |
|---:|---:|---:|---|
| 6 | 290,000 | 2 | 145,000 + 145,000 |
| 7 | 305,000 | 2 | 152,500 + 152,500 |
| 9 | 235,000 | 2 | 117,500 + 117,500 |
| 14 | 270,000 | 2 | 135,000 + 135,000 |
| 15 | 140,000 | 2 | 70,000 + 70,000 |
| 27 | 300,000 | 2 | 150,000 + 150,000 |
| 28 | 280,000 | 2 | 140,000 + 140,000 |
| 31 | 280,000 | 2 | 140,000 + 140,000 |
| 34 | 270,000 | 2 | 135,000 + 135,000 |
| 40 | 270,000 | 2 | 135,000 + 135,000 |
| 41 | 285,000 | 2 | 142,500 + 142,500 |
| 46 | 295,000 | 2 | 147,500 + 147,500 |
| 49 | 779,000 | 2 | 389,500 + 389,500 |
| 55 | 300,000 | 2 | 150,000 + 150,000 |
| 56 | 285,000 | 2 | 142,500 + 142,500 |
| 60 | 325,000 | 2 | 162,500 + 162,500 |
| 66 | 315,000 | 2 | 157,500 + 157,500 |
| 67 | 180,000 | 2 | 90,000 + 90,000 |
| 69 | 280,000 | 2 | 140,000 + 140,000 |
| 70 | 313,000 | 2 | 156,500 + 156,500 |
| 76 | 245,000 | 2 | 122,500 + 122,500 |
| 86 | 193,000 | 2 | 96,500 + 96,500 |
| 87 | 370,000 | 2 | 185,000 + 185,000 |
| 88 | 320,000 | 2 | 160,000 + 160,000 |
| 89 | 312,000 | 2 | 156,000 + 156,000 |
| 90 | 245,000 | 2 | 122,500 + 122,500 |
| 91 | 325,000 | 2 | 162,500 + 162,500 |
| 97 | 188,000 | 2 | 94,000 + 94,000 |
| 99 | 309,000 | 2 | 154,500 + 154,500 |
| 102 | 340,000 | 2 | 170,000 + 170,000 |
| 103 | 460,000 | 2 | 230,000 + 230,000 |
| 106 | 340,000 | 2 | 170,000 + 170,000 |
| 107 | 248,000 | 2 | 124,000 + 124,000 |
| 108 | 255,000 | 2 | 127,500 + 127,500 |
| 110 | 160,000 | 2 | 80,000 + 80,000 |
| 113 | 270,000 | 2 | 135,000 + 135,000 |
| 118 | 320,000 | 2 | 160,000 + 160,000 |
| 120 | 298,000 | 2 | 149,000 + 149,000 |
| 123 | 265,000 | 2 | 132,500 + 132,500 |
| 125 | 240,000 | 2 | 120,000 + 120,000 |
| … 1641 más | | | |

## 9. Productos fuera de alcance (códigos de juego / skins)

20 menciones. No generan fila (no son un control). Si el pedido tenía además otro servicio, ese sí quedó en el CSV.

- fila 525: ALQUILER
- fila 897: ALQUILER
- fila 1044: COMPRA SKIN FORTNITE
- fila 1531: STRIKE PACK
- fila 1633: CODIGO FORNITE
- fila 1636: CODIGO FORNITE
- fila 1660: CODIGO FORNITE
- fila 1672: CODIGO FORNITE
- fila 1709: CODIGO FORNITE
- fila 1713: CODIGO FORNITE
- fila 1763: CODIGO FORNITE
- fila 1828: CONTROL DE ENTREGA INMEDIATA FORNITE
- fila 1877: CODIGO FORNITE
- fila 1884: CODIGO FORNITE
- fila 1907: CODIGO FORNITE
- fila 1925: CODIGO FORNITE
- fila 2101: CODIGO FORNITE
- fila 2138: CODIGO FORNITE
- fila 3031: MOUSE LOGITECH G903 SE
- fila 3247: INSTALACION DE JUEGO
