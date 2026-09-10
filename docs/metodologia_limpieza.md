# Cómo funciona `limpieza_clientes.py` — explicación paso a paso

Este documento recorre el script **bloque por bloque** para que puedas
entender (y modificar) cada parte. Está pensado como material de aprendizaje:
además de "qué hace", explica "por qué se hace así".

Archivos del proyecto:

```
src/
├── limpieza_clientes.py   ← el programa principal (orquesta todo)
├── diccionario_tipos.py   ← DATOS: reglas para clasificar "TIPO DE VENTA"
├── typos_ciudades.py      ← DATOS: correcciones de ciudad
└── salida/                ← se genera al correr el script (fuera del repo)
    ├── especialmodz_clientes_limpio.csv
    ├── reporte_incidencias.md
    ├── tipos_sin_clasificar.csv
    └── correcciones_ciudad.csv
```

> Nota: este documento se escribió cuando los scripts vivían en `limpieza/`;
> hoy están en `src/` y la salida limpia, ya anonimizada, se publica en
> `data/processed/`. La lógica que se explica abajo no cambió.

Para ejecutarlo (necesita el Excel original en `data/raw/`):

```bash
python3 src/limpieza_clientes.py
```

No necesita instalar nada (`pip install ...`): usa solo la **librería estándar**
de Python.

---

## 0. La idea general

Un archivo `.xlsx` **no es un formato binario mágico**: es un archivo ZIP que
dentro tiene varios archivos XML (texto). Entonces, para leerlo sin `pandas` ni
`openpyxl`, hacemos:

1. Abrir el ZIP (`zipfile`).
2. Leer los XML que nos interesan (`xml.etree.ElementTree`).
3. Interpretar las celdas.

Para escribir usamos el módulo `csv`, que también es estándar.

El flujo completo del programa es:

```
leer Hoja1  →  limpiar cada campo  →  decidir si la fila se excluye
            →  partir "TIPO DE VENTA" en categorías  →  repartir el valor
            →  escribir 4 archivos de salida
```

---

## 1. Imports y constantes (`limpieza_clientes.py`, arriba del todo)

```python
import csv, datetime as dt, os, re, sys, unicodedata, zipfile
from collections import Counter, defaultdict
from xml.etree import ElementTree as ET
import diccionario_tipos as dic
import typos_ciudades as tc
```

- `re` → expresiones regulares (patrones de texto). Se usan muchísimo.
- `unicodedata` → para quitar tildes ("BOGOTÁ" → "BOGOTA").
- `zipfile` + `ElementTree` → para leer el `.xlsx`.
- `Counter` → un diccionario que cuenta ("cuántas veces aparece X").
- `defaultdict(list)` → un diccionario donde cada clave nueva arranca como `[]`.
- `dic` y `tc` → nuestros dos archivos de datos.

Luego se definen rutas y parámetros. Lo importante:

```python
HOJA_OBJETIVO      = "Hoja1"     # CLAUDE.md §2
FILA_ENCABEZADOS   = 4
PRIMERA_FILA_DATOS = 5
COL_FECHA, COL_NOMBRE, COL_CIUDAD, COL_TELEFONO, COL_TIPO, COL_VALOR = 0,1,2,3,4,5
FECHA_MIN = dt.date(2016, 1, 1)   # fuera de este rango se avisa
FECHA_MAX = dt.date.today()
ORDEN_CATEGORIAS = ["COMPRA DE CONTROL", "MODIFICACION PROPIA", "SERVICIO TECNICO"]
DELIM = ";"                       # separador del CSV (Excel-Colombia usa ';')
```

`ORDEN_CATEGORIAS` fija el orden en que salen las categorías de un pedido, para
que el resultado sea **reproducible** (correr el script dos veces da el mismo
archivo).

---

## 2. Leer el `.xlsx` sin librerías

### 2.1 `_col_a_indice("B7") → 1`

Excel nombra las columnas con letras (A, B, …, Z, AA, AB…). Necesitamos pasarlas
a números (0, 1, 2…). Es una conversión **base 26**:

```python
letras = re.match(r"[A-Z]+", ref_celda).group(0)   # "B7" -> "B"
n = 0
for ch in letras:
    n = n * 26 + (ord(ch) - ord("A") + 1)          # 'B' -> 2
return n - 1                                        # 2 -> índice 1
```

`ord('A')` es el código del carácter 'A'. `ord('B') - ord('A') + 1 = 2`.

### 2.2 `_cargar_shared_strings(z)`

Excel, para no repetir texto, guarda **todas las cadenas una sola vez** en
`xl/sharedStrings.xml` y en cada celda pone solo el número de índice. Esta
función devuelve la lista de textos:

```python
raiz = ET.fromstring(z.read("xl/sharedStrings.xml"))
for si in raiz.findall("s:si", NS):
    textos.append("".join(t.text or "" for t in si.iter("{...}t")))
```

Un `<si>` (string item) puede ser un `<t>` simple o varios `<r><t>` (texto con
formato). Por eso recorremos **todos** los `<t>` de adentro y los unimos.

### 2.3 `_estilos_que_son_fecha(z)` — la parte más sutil

Problema: en Excel una fecha se guarda como un **número** (días desde el
1899-12-30). `42370` puede ser la fecha `2016-01-01` **o** el número
cuarenta-y-dos-mil. La única forma de distinguir es mirar el **formato** de la
celda.

`xl/styles.xml` tiene:
- `<numFmts>` → formatos personalizados con un `formatCode` (ej. `"dd/mm/yyyy"`).
- `<cellXfs>` → lista de estilos; cada celda apunta a uno con su atributo `s`.

La función arma el conjunto de índices de estilo que son fecha:

```python
FMT_FECHA_BUILTIN = {14,15,16,17,18,19,20,21,22,45,46,47}   # formatos de fábrica
# + los personalizados cuyo formatCode tenga 'd', 'm' o 'y'
...
for i, xf in enumerate(cellxfs.findall("s:xf", NS)):
    if int(xf.get("numFmtId", 0)) in ids_fecha:
        estilos_fecha.add(i)
```

Después, al leer una celda numérica, si su `s` está en `estilos_fecha`, sabemos
que es una fecha nativa.

### 2.4 `_ruta_hoja(z, "Hoja1")`

El nombre visible de la hoja ("Hoja1") **no** es el nombre del archivo interno
(`sheet1.xml`, `sheet3.xml`…). La relación se resuelve en dos pasos:

1. `xl/workbook.xml` → `<sheet name="Hoja1" r:id="rId1">`
2. `xl/_rels/workbook.xml.rels` → `<Relationship Id="rId1" Target="worksheets/sheet1.xml">`

La función busca el `r:id` por nombre y luego el `Target` por `r:id`.

### 2.5 `leer_hoja1(ruta)` — junta todo

```python
with zipfile.ZipFile(ruta_xlsx) as z:
    shared        = _cargar_shared_strings(z)
    estilos_fecha = _estilos_que_son_fecha(z)
    raiz          = ET.fromstring(z.read(_ruta_hoja(z, HOJA_OBJETIVO)))
    sheet_data    = raiz.find("s:sheetData", NS)
```

Luego recorre cada `<row>`:

```python
num_fila = int(fila_xml.get("r"))
if num_fila < PRIMERA_FILA_DATOS:   # saltar título y encabezados (filas 1-4)
    continue
```

Y cada `<c>` (celda):

```python
tipo_celda = c.get("t")     # 's' = shared string ; None = número ; 'str' = fórmula
v = c.find("s:v", NS)       # <v> = value
bruto = v.text if v is not None else None

if tipo_celda == "s":
    texto = shared[int(bruto)]                 # el número es un índice
elif ...:                                       # número
    es_fecha = estilo in estilos_fecha
```

Devuelve una lista de diccionarios, uno por fila:

```python
{
  "fila": 5,
  "fecha_cruda": "42370", "fecha_es_texto": False,
  "nombre_crudo": "JUGADOR EJEMPLO",
  "ciudad_cruda": "BOGOTA",
  "tipo_crudo": "MODIFICACION",
  "valor_crudo": "167000",
}
```

La columna **D (teléfono) se ignora** por completo (CLAUDE.md §2).

---

## 3. Limpiar cada campo

Todas estas son **funciones puras**: reciben un texto y devuelven un valor
limpio. No tocan archivos ni variables globales → son fáciles de probar y
entender.

### 3.1 `limpiar_fecha(cruda, es_texto)`

```python
if not es_texto:                       # fecha nativa de Excel
    fecha = dt.date(1899,12,30) + dt.timedelta(days=int(round(float(cruda))))
```

El `1899-12-30` es el "día 0" de Excel. (Excel arrastra un bug histórico: cree
que 1900 fue bisiesto. Usar 1899-12-30 como ancla lo corrige para fechas
modernas.)

```python
else:                                  # fecha escrita a mano, formato "D/M/YYYY"
    m = re.match(r"^\s*(\d{1,2})\s*/\s*(\d{1,2})\s*/\s*(\d{2,4})\s*$", cruda)
    d, mth, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if y < 100: y += 2000              # '19' -> 2019
    fecha = dt.date(y, mth, d)         # DD/MM/YYYY (formato colombiano)
```

En el análisis previo se confirmó que **las 228 fechas-texto tienen el día > 12**
(ej. `13/02/2019`, `24/05/2018`), así que no hay ambigüedad con el formato
americano MM/DD.

Devuelve `(fecha_iso, nota)`:
- Si no se puede parsear → `(None, motivo)` y **la fila se excluye**.
- Si la fecha es válida pero está fuera de `[2016-01-01, hoy]` → se conserva
  pero se añade una nota al reporte (hay 1 caso: `2003-01-05`, seguro un typo
  de 2023).

### 3.2 `limpiar_nombre(crudo)`

```python
return re.sub(r"\s+", " ", crudo).strip()
```

`\s` en regex significa "cualquier espacio en blanco": espacio, tabulación
(`\t`) y salto de línea (`\n`). `re.sub(r"\s+", " ", ...)` reemplaza cualquier
grupo de espacios por **uno solo**, y `.strip()` quita los de los extremos.
CLAUDE.md §4.2 pedía exactamente esto (1.481 nombres traían tabs). **No** se
cambian mayúsculas/minúsculas.

### 3.3 `limpiar_ciudad(cruda)` (usa `typos_ciudades.py`)

Tres sub-pasos:

1. **Normalizar formato** — `_normalizar_ciudad`:
   ```python
   t = unicodedata.normalize("NFKD", texto).encode("ascii","ignore").decode()
   t = t.upper()
   t = re.sub(r"\(.*?\)", " ", t)        # quita "(ANTIOQUIA)"
   t = re.sub(r"[^A-Z0-9 ]+", " ", t)    # quita comas, guiones, etc.
   t = re.sub(r"\s+", " ", t).strip()
   ```
   `NFKD` + `encode("ascii","ignore")` es el truco estándar para quitar tildes:
   descompone "Á" en "A" + acento, y luego bota lo que no sea ASCII.

2. **Quitar el sufijo de departamento** — `_quitar_sufijo_departamento`:
   `"IBAGUE TOLIMA"` → `"IBAGUE"`. Prueba los departamentos de más largo a más
   corto (para cortar `"NORTE DE SANTANDER"` antes que `"SANTANDER"`).
   **Ojo**: solo se aplica si lo que queda es una ciudad conocida. Así
   `"PUERTO BOYACA"` **no** se convierte en `"PUERTO"` (Boyacá es departamento,
   pero ahí es parte del nombre del municipio).

3. **Corregir typos evidentes** — busca la ciudad en `tc.TYPOS`
   (`"BOOGTA"` → `"BOGOTA"`, `"MDELLIN"` → `"MEDELLIN"`, …).

Devuelve `(ciudad, correccion, reconocida)`:
- `reconocida` = `True` si la ciudad final está en `tc.CIUDADES_CONOCIDAS`.
- Si **no** es reconocida, la fila **igual pasa** (no se borra), pero la ciudad
  se lista en la §6 del reporte para que la revises a mano. CLAUDE.md §4.3:
  *"si es ambiguo, dejarlo tal cual y reportarlo — no inventar ciudades"*.

### 3.4 `limpiar_valor(crudo)`

```python
s = crudo.strip().replace("$","").replace(" ","")
if not s:                    return None, "sin valor de venta"
if re.match(r"^\d+(\.\d+)?$", s):
    n = int(round(float(s)))
    return (n, None) if n > 0 else (None, "valor de venta = 0")
```

Si el valor está vacío **o es 0**, se trata como dato faltante → la fila se
excluye (CLAUDE.md §4.4 hablaba de "sin valor"; un 0 no aporta nada y suele ser
un error de captura). Si trae separadores raros (`1.234.567`), se intenta
limpiar y se deja una nota.

---

## 4. `TIPO DE VENTA` — la columna difícil

Es texto libre con **3.356 variantes** sobre 4.178 filas. Muchas celdas mezclan
varios servicios. La estrategia (CLAUDE.md §4.5): **partir la celda en trozos,
clasificar cada trozo, y generar una fila de salida por cada categoría
detectada**.

### 4.1 `separar_tipos(tipo_crudo)` (en `limpieza_clientes.py`)

**Corte de 1º nivel** — separadores obvios:

```python
trozos_1 = re.split(r"[\n,;+/]+", tipo_crudo)
```

**Corte de 2º nivel** — muchas celdas describen todo el pedido en un párrafo sin
comas (`"CONTROL PS4 CAMBIO DE ANALOGOS MANTENIMIENTO DISEÑO..."`). Cortamos
**justo antes** de palabras clave que casi siempre inician un ítem nuevo:

```python
_RE_CORTE_SECUNDARIO = re.compile(
    r"(?=\bCAMBIO\b|\bARREGLO\b|\bMANTENIMIENTO\b|\bDISE(?:N|Ñ)O\b"
    r"|\bACTUALIZACION\b|\bCOMPRA\b|\bMODIFICACION\b|\bCONTROL\b|\bCONSOLA\b"
    r"|\bDOMICILIOS?\b|\bENVIO\b|\bPORCENTAJE\b|...)"
)
```

El `(?=...)` es un **lookahead**: marca la posición *antes* de la palabra sin
consumirla, así el `re.split` deja la palabra al inicio del siguiente trozo.
(Incluir la logística — DOMICILIO, ENVIO — es importante: si no,
`"MODIF TACTICA DOMICILIO"` se tomaría entera como logística y se perdería la
modificación.)

Luego, para cada trozo:

```python
frag = dic.normalizar(trozo)                # MAYÚSCULAS, sin tildes
etiqueta = dic.clasificar_fragmento(frag)   # ver 4.2

if   etiqueta == "ETIQUETA":       hubo_etiqueta = True; continue
elif etiqueta == "IGNORAR":        continue
elif etiqueta == "FUERA DE ALCANCE": fuera_alcance.append(frag)
elif etiqueta == "AMBIGUO":        pendientes.append((frag, "AMBIGUO"))
elif etiqueta is None:             pendientes.append((frag, "DESCONOCIDO"))
else:                              categorias.append(etiqueta)   # ST / CC / MP
```

**Regla clave (decisión de Edgar):** si la celda quedó **solo** con nombres de
dispositivo (todo fue `ETIQUETA`) y no hay servicio ni pendientes, se cuenta
como **COMPRA DE CONTROL**:

```python
if not categorias and not pendientes and not fuera_alcance and hubo_etiqueta:
    categorias = [dic.CC]
```

Si un trozo queda `AMBIGUO` o `DESCONOCIDO`, **toda la fila queda pendiente** y
NO entra al CSV (no la partimos con un valor mal repartido). Esos fragmentos se
juntan en `tipos_sin_clasificar.csv`.

### 4.2 `clasificar_fragmento(frag)` (en `diccionario_tipos.py`)

Recibe un fragmento ya normalizado y lo pasa por una cascada:

```
PASO 0 — quita prefijos de precio:  "PROMO MOD TACTICA" -> "MOD TACTICA"
PASO 1 — ¿es solo etiqueta?         borra todas las PALABRAS_ETIQUETA;
                                    si no queda nada -> "ETIQUETA"
PASO 2 — ¿concepto AMBIGUO?         (lista vacía hoy; Edgar los resolvió)
PASO 3 — ¿logística/pago?           NEEDLES_IGNORAR -> "IGNORAR"
PASO 4 — REGLAS de categoría        primera regex que coincide gana -> ST/CC/MP/XX
PASO 5 — ¿dispositivo con nombre
         raro y sin señal de
         reparación?                -> "ETIQUETA"  (ej. "CONTROL BERRY BLUE PS4")
PASO 6 — nada coincide              -> None  (queda pendiente)
```

**`normalizar(texto)`**:
```python
t = unicodedata.normalize("NFKD", texto).encode("ascii","ignore").decode()
t = t.upper()
t = re.sub(r"[^A-Z0-9%#]+", " ", t)
t = re.sub(r"\s+", " ", t).strip()
```

**PASO 1 — `PALABRAS_ETIQUETA`**: lista de regex de palabras que son solo
"nombre del aparato": `CONTROL`, `CONSOLA`, `PS4`, `XBOX`, colores, números,
`#`, conectores (`DE`, `Y`, `CON`)… Se borran todas del fragmento; si no queda
nada útil, era pura etiqueta.

```python
resto = _RE_ETIQUETA.sub(" ", f)
if not re.sub(r"[#\s]+", " ", resto).strip():
    return "ETIQUETA"
```

**PASO 4 — `REGLAS`**: una **lista ordenada** de `(regex, categoria)`. Se
prueban en orden y **gana la primera** que coincide. El orden importa:

```python
REGLAS = [
    (r"CODIGO|FORNITE|...",            XX),   # códigos de juego -> fuera de alcance
    (r"INTERCAM|\bINTER\b|...",        MP),   # "análogos intercambiables" (kit)
    (r"ALUMIN|KITALU|JOYSALU|...",     MP),   # antes que la regla de "análogos"
    (r"\bACET\w*|CARCA\w*|...",        ST),   # acetato/carcasa (decisión de Edgar)
    (r"CAMB\w*SIST\w*(TACT|SCUF)|...", ST),   # "cambio del sistema táctico"
    (r"CAPUCH\w*|CAPERU[ZS]A\w*|...",  ST),   # cambio de capuchas
    (r"PASTA|KITPAS\w*|THERMAL|...",   ST),   # pasta térmica / metal líquido
    (r"CALIBRA\w*",                    ST),
    (r"DISCO\s*DURO|\bSSD\b|...",      ST),
    (r"REJILLA\w*",                    ST),
    (r"\bGARANT\w*",                   ST),
    (r"MANTEN|...|LIMPI",              ST),   # mantenimiento (y sus typos)
    (r"^ARR|^CAM[A-Z]|^REVIS|...",     ST),   # "arreglo/cambio/revisión de ..."
    ... etc ...
    (r"\bCOMPRA\w*|...\bCXC\w*|...",   CC),
    (r"\bNUEVOS?\b|\bNUEVAS?\b",       CC),
    (r"KONTROL|...FREEK|...",          CC),   # KontrolFreek (accesorio que se vende)
    (r"\bCABLE\b|ESTUCHE\w*|CARGADOR", CC),   # accesorios (decisión de Edgar)
    (r"PERSONALIZ\w*|BACK\s*BUTTON",   MP),   # (decisión de Edgar)
    (r"DISE\w*|...",                   MP),   # diseño
    (r"ANTIDE\w*|...",                 MP),   # antideslizante
    (r"MO[A-Z]{0,3}TAC|...TACTIC\w*",  MP),   # modificación táctica
    (r"GATILLO|...|TRIGGER",           MP),
    (r"RAPID\s*FIR|AUTOFIR|CHIP|...",  MP),   # rapid fire / auto fire
    (r"\bTOPES?\b|...",                MP),
    (r"\bBOT[A-Z0-9]\w*|...|BALAS?",   MP),   # botones (de aluminio, "bala", etc.)
    (r"\bFLECHA\w*|CRUCETA|...",       MP),
    (r"\bPALETA\w*|PADDLES?|...",      MP),
    (r"\bLOGOS?\b",                    MP),
    (r"\bNOMBR\w*|\bPANEL\b|...",      MP),
    (r"HIDROGRAF|PINTUR|SKIN|...",     MP),   # pintura / hidrografía / skin
    (r"\bLED\b|LUCES|ILUMINAC|...",    MP),
    (r"\bKI[RT]?T\w*",                 MP),   # "kit ..." suelto
]
```

Las regex están llenas de variantes porque los datos tienen **muchísimos
errores de tipeo**: `MANTENIMIENTO` aparece como `MTTO`, `MTO`, `MANTEMNIMIENTO`,
`MSNTENIMIENTO`… Por eso hay patrones como `MAN[A-Z]{0,3}NIM` (M-A-N, hasta 3
letras cualesquiera, N-I-M).

**PASO 5 — fallback de dispositivo**: si el fragmento menciona un aparato
(`CONTROL`, `XBOX`, `PS5`, `SCUF`…) y **no** tiene ninguna señal de reparación
(`CAMB`, `ARREGL`, `NO`, `FALLA`, `GARANT`…), se asume que es solo el nombre de
una edición rara (`"CONTROL BERRY BLUE PS4"`) → `ETIQUETA`.

### 4.3 `repartir_valor(total, n)`

Decisión de Edgar: el valor del pedido se **reparte en partes iguales** entre
las filas generadas.

```python
base, resto = divmod(total, n)                 # 380000, 3 -> base=126666, resto=2
return [base + (1 if i < resto else 0) for i in range(n)]   # [126667, 126667, 126666]
```

El `resto` (unos pocos pesos) se reparte de a $1 entre las primeras filas, para
que **la suma cuadre exacto** con el valor original. Así `SUM(valor_compra)` en
SQL da el ingreso real, sin sobre-contar.

---

## 5. El pipeline: `procesar()`

```python
filas = leer_hoja1(RUTA_XLSX)
for f in filas:
    # 4.1 limpiar
    fecha_iso, nota_fecha           = limpiar_fecha(f["fecha_cruda"], f["fecha_es_texto"])
    nombre                          = limpiar_nombre(f["nombre_crudo"])
    ciudad, correccion, ciudad_ok   = limpiar_ciudad(f["ciudad_cruda"])
    valor, nota_valor               = limpiar_valor(f["valor_crudo"])
    categorias, pendientes, fuera   = separar_tipos(f["tipo_crudo"])

    # 4.2 exclusiones -> si falta fecha/nombre/ciudad/valor/tipo, se descarta
    if motivos: excluidas["campos incompletos"].append(...); continue

    # 4.3 duplicado exacto (misma fecha+nombre+ciudad+tipo+valor) -> se descarta
    if firma in vistas: excluidas["fila duplicada exacta"].append(...); continue

    # 4.4 avisos que NO excluyen (fecha rara, corrección de ciudad, ...)

    # 4.5 si hay fragmentos pendientes -> la fila entera queda fuera y se reporta
    if pendientes: ...; continue

    # 4.6 si no se detectó ninguna categoría -> fuera y se reporta
    if not categorias: ...; continue

    # 4.7 EXPANDIR: una fila de salida por categoría, con el valor repartido
    montos = repartir_valor(valor, len(categorias))
    for cat, monto in zip(categorias, montos):
        salida.append({fecha_compra, nombre_cliente, ciudad, valor_compra=monto, tipo_compra=cat})
```

El `continue` significa "salta a la siguiente fila". Cada `excluidas[...]` es
una lista que se vuelca al reporte.

Al final se escriben los 4 archivos y se imprime un resumen con **assert**
(comprobaciones que revientan si algo no cuadra):

```python
assert incluidas + total_excluidas == total_leidas      # el cuadre de filas
for r in salida:
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", r["fecha_compra"])
    assert r["tipo_compra"] in ORDEN_CATEGORIAS
    assert r["valor_compra"] >= 0
    assert r["nombre_cliente"] and r["ciudad"]
```

---

## 6. Los archivos de datos (los que vas a editar tú)

### `diccionario_tipos.py`

- `PALABRAS_ETIQUETA` — palabras que son "solo el nombre del aparato".
- `PATRONES_AMBIGUOS` — conceptos que el script NO decide solo (hoy vacío).
- `NEEDLES_IGNORAR` — logística y pagos.
- `REGLAS` — la lista ordenada `(regex, categoria)`. **Aquí agregas** cuando
  reconozcas un fragmento nuevo: pon su palabra clave en la categoría correcta.

### `typos_ciudades.py`

- `DEPARTAMENTOS` — para quitar el sufijo `"CIUDAD DEPARTAMENTO"`.
- `TYPOS` — `forma_mal_escrita → ciudad_correcta`.
- `CIUDADES_CONOCIDAS` — lista para decidir qué ciudad se reporta como "revisar".

---

## 7. Ciclo de trabajo para afinar el resultado

1. Corres `python3 limpieza_clientes.py`.
2. Abres `salida/tipos_sin_clasificar.csv` y `salida/reporte_incidencias.md`.
3. Para cada fragmento que reconozcas: agregas su palabra clave a `REGLAS`
   (en `diccionario_tipos.py`) en la categoría que corresponda.
4. Para cada ciudad mal escrita: la agregas a `TYPOS` (en `typos_ciudades.py`).
5. Vuelves a correr. El CSV y el reporte se regeneran.
6. Repites hasta que lo que quede sin clasificar sean casos raros que aceptes
   dejar fuera (y quedan documentados en el reporte).

Correr el script dos veces produce archivos **idénticos** (salvo la fecha de
generación del reporte).

---

## 8. Resultado de la última corrida

| Concepto | Filas |
|---|---:|
| Leídas del Excel (fila 5 en adelante) | 4.178 |
| Excluidas — campos incompletos (fecha/nombre/ciudad/valor/tipo) | 34 |
| Excluidas — fila duplicada exacta | 1 |
| Excluidas — TIPO DE VENTA sin clasificar (trozos sueltos / muy específicos) | 32 |
| Excluidas — solo producto fuera de alcance (código de juego / skin) | 17 |
| **Pedidos incluidos** | **4.094** (98 %) |
| **Filas en el CSV final** (tras dividir por tipo) | **5.996** |

Distribución de `tipo_compra` en el CSV:

| tipo_compra | filas |
|---|---:|
| MODIFICACION PROPIA | 2.589 |
| SERVICIO TECNICO | 2.041 |
| COMPRA DE CONTROL | 1.366 |

Suma de `valor_compra` = **931.453.712** (igual al ingreso real de los pedidos
incluidos, porque el reparto conserva la suma).

**Decisiones de Edgar incorporadas (2026-08-28):**
- Valor de pedidos divididos → repartido en partes iguales (resto a la 1ª fila).
- Filas sin nombre / sin ciudad / sin tipo / sin valor (o valor 0) → excluidas.
- Fila duplicada exacta → se elimina una.
- Ciudad → solo normalización + typos evidentes; el resto se reporta.
- Acetato/carcasa, "cambio del sistema táctico", capuchas, pasta térmica,
  calibración, disco duro, rejilla, batería, garantía → **SERVICIO TECNICO**.
- Personalización, Back Button Attachment → **MODIFICACION PROPIA**.
- Cable de carga, estuche, cargador → **COMPRA DE CONTROL**.
- Códigos de juego / skins Fortnite / V-bucks → **fuera de alcance** (§9 del reporte).
- Celda que es solo el nombre de un control (± "entrega inmediata") →
  **COMPRA DE CONTROL**.

**Lo que queda para revisión manual de Edgar** (en el reporte):
- §6: ~35 ciudades no reconocidas (barrios, dos ciudades juntas, typos raros).
- §7: 32 filas con fragmentos de TIPO DE VENTA sin clasificar.
- §3: 1 fecha fuera de rango (`2003-01-05`, probable typo de 2023).
