#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
limpieza_clientes.py
====================

Extrae y homogeniza la base de datos de clientes de SpecialModz siguiendo las
reglas de CLAUDE.md. NO diseña el esquema SQL ni hace INSERT: solo entrega
datos limpios listos para que Edgar los cargue.

Entradas:
    Doc/1.Base de Datos Clientes 2017.xlsx   (hoja "Hoja1")

Salidas (carpeta limpieza/salida/):
    especialmodz_clientes_limpio.csv   -> el extracto final, 5 columnas
    reporte_incidencias.md             -> qué se excluyó y por qué
    tipos_sin_clasificar.csv           -> fragmentos que Edgar debe clasificar
    correcciones_ciudad.csv            -> log original -> corregido

No usa librerías externas: el .xlsx se lee con `zipfile` + `xml.etree`
(un .xlsx no es más que un ZIP con XMLs dentro) y se escribe con `csv`.

Uso:
    python3 limpieza_clientes.py
"""

from __future__ import annotations

import csv
import datetime as dt
import os
import re
import sys
import unicodedata
import zipfile
from collections import Counter, defaultdict
from xml.etree import ElementTree as ET

# Módulos de datos que viven al lado de este script (se pueden editar sin tocar
# la lógica). Ver sus docstrings.
import diccionario_tipos as dic
import typos_ciudades as tc


# ===========================================================================
# 0. RUTAS Y CONSTANTES
# ===========================================================================

# Carpeta donde está este .py -> todo lo demás es relativo a ella.
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)                        # .../SM_DataBase

RUTA_XLSX = os.path.join(RAIZ, "data", "raw", "1.Base de Datos Clientes 2017.xlsx")
DIR_SALIDA = os.path.join(AQUI, "salida")

# CLAUDE.md §2: los datos reales están en la hoja "Hoja1".
HOJA_OBJETIVO = "Hoja1"

# CLAUDE.md §2: encabezados en la fila 4, datos desde la fila 5.
FILA_ENCABEZADOS = 4
PRIMERA_FILA_DATOS = 5

# Índice de columna (0 = A, 1 = B, ...) para cada campo de origen.
COL_FECHA, COL_NOMBRE, COL_CIUDAD, COL_TELEFONO, COL_TIPO, COL_VALOR = 0, 1, 2, 3, 4, 5

# CLAUDE.md §2: rango esperado de fechas. Fuera de esto se conserva pero se avisa.
FECHA_MIN = dt.date(2016, 1, 1)
FECHA_MAX = dt.date.today()

# Orden fijo de categorías en la salida -> hace el resultado reproducible.
ORDEN_CATEGORIAS = ["COMPRA DE CONTROL", "MODIFICACION PROPIA", "SERVICIO TECNICO"]

# Separador del CSV. En Excel-Colombia el punto y coma es lo habitual.
DELIM = ";"

# Espacio de nombres XML de una hoja de cálculo OpenXML (todas las etiquetas
# vienen con este prefijo, p. ej. "{...}row").
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


# ===========================================================================
# 1. LECTURA DEL .XLSX (sin openpyxl)
# ===========================================================================

def _col_a_indice(ref_celda: str) -> int:
    """'B7' -> 1 ; 'AA1' -> 26. Convierte las letras de columna a índice 0-based."""
    letras = re.match(r"[A-Z]+", ref_celda).group(0)
    n = 0
    for ch in letras:                              # base 26 tipo Excel
        n = n * 26 + (ord(ch) - ord("A") + 1)
    return n - 1


def _cargar_shared_strings(z: zipfile.ZipFile) -> list[str]:
    """
    Excel guarda casi todo el texto UNA sola vez en xl/sharedStrings.xml y en
    las celdas solo pone el índice. Aquí devolvemos la lista de textos.
    """
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    raiz = ET.fromstring(z.read("xl/sharedStrings.xml"))
    textos = []
    for si in raiz.findall("s:si", NS):
        # Un <si> puede ser un <t> simple o varios <r><t> (texto con formato).
        textos.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["s"])))
    return textos


def _estilos_que_son_fecha(z: zipfile.ZipFile) -> set[int]:
    """
    Devuelve el conjunto de índices de estilo (atributo `s` de cada celda) cuyo
    formato de número es una FECHA. Sirve para distinguir una celda que ya es
    fecha nativa de Excel (número serial + formato de fecha) de un número normal.
    """
    raiz = ET.fromstring(z.read("xl/styles.xml"))

    # Formatos de fecha "de fábrica" de Excel (id 14-22, 45-47, etc.).
    FMT_FECHA_BUILTIN = {14, 15, 16, 17, 18, 19, 20, 21, 22, 45, 46, 47}

    # Formatos personalizados: nos quedamos con los que tienen d/m/y (día/mes/año)
    # y no son de hora pura.
    fmt_personalizados_fecha = set()
    numfmts = raiz.find("s:numFmts", NS)
    if numfmts is not None:
        for nf in numfmts.findall("s:numFmt", NS):
            code = nf.get("formatCode", "").lower()
            if re.search(r"[dmy]", code):
                fmt_personalizados_fecha.add(int(nf.get("numFmtId")))

    ids_fecha = FMT_FECHA_BUILTIN | fmt_personalizados_fecha

    # cellXfs = lista de estilos aplicables; posición i -> lo usa la celda con s="i".
    estilos_fecha = set()
    cellxfs = raiz.find("s:cellXfs", NS)
    for i, xf in enumerate(cellxfs.findall("s:xf", NS)):
        if int(xf.get("numFmtId", 0)) in ids_fecha:
            estilos_fecha.add(i)
    return estilos_fecha


def _ruta_hoja(z: zipfile.ZipFile, nombre_hoja: str) -> str:
    """
    Traduce el NOMBRE de una hoja ('Hoja1') al archivo interno que la contiene
    ('xl/worksheets/sheetN.xml'), resolviendo la relación r:id.
    """
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))

    # r:id de la hoja pedida.
    rid = None
    for hoja in wb.find("s:sheets", NS).findall("s:sheet", NS):
        if hoja.get("name") == nombre_hoja:
            rid = hoja.get("{%s}id" % NS["r"])
    if rid is None:
        raise SystemExit(f"No encontré la hoja '{nombre_hoja}' en el Excel.")

    # r:id -> Target (ruta relativa dentro de xl/).
    for rel in rels:
        if rel.get("Id") == rid:
            destino = rel.get("Target")
            return destino if destino.startswith("xl/") else "xl/" + destino
    raise SystemExit(f"No pude resolver la relación {rid} de la hoja.")


def leer_hoja1(ruta_xlsx: str) -> list[dict]:
    """
    Lee la hoja objetivo y devuelve una lista de dicts, uno por fila de datos:

        {"fila": <nº de fila en Excel>,
         "fecha_cruda": <str>, "fecha_es_texto": <bool>,
         "nombre_crudo": <str>, "ciudad_cruda": <str>,
         "tipo_crudo": <str>, "valor_crudo": <str>}

    Solo devuelve las columnas A, B, C, E, F (el TELÉFONO, columna D, se ignora
    por CLAUDE.md §2).
    """
    with zipfile.ZipFile(ruta_xlsx) as z:
        shared = _cargar_shared_strings(z)
        estilos_fecha = _estilos_que_son_fecha(z)
        raiz = ET.fromstring(z.read(_ruta_hoja(z, HOJA_OBJETIVO)))

        sheet_data = raiz.find("s:sheetData", NS)
        filas = []

        for fila_xml in sheet_data.findall("s:row", NS):
            num_fila = int(fila_xml.get("r"))
            if num_fila < PRIMERA_FILA_DATOS:      # saltar título y encabezados
                continue

            # Reunir el valor y (si aplica) el estilo de cada celda de la fila.
            valores = {}                            # indice_columna -> (texto, es_texto, es_fecha_nativa)
            for c in fila_xml.findall("s:c", NS):
                idx = _col_a_indice(c.get("r"))
                tipo_celda = c.get("t")             # 's' = shared string, None = número, etc.
                estilo = c.get("s")
                v = c.find("s:v", NS)
                bruto = v.text if v is not None else None
                if bruto is None:
                    continue

                if tipo_celda == "s":               # texto compartido
                    texto = shared[int(bruto)]
                    valores[idx] = (texto, True, False)
                elif tipo_celda == "str":           # texto en línea (fórmula)
                    valores[idx] = (bruto, True, False)
                else:                                # número
                    es_fecha = estilo is not None and int(estilo) in estilos_fecha
                    valores[idx] = (bruto, False, es_fecha)

            def crudo(idx):
                return valores.get(idx, ("", False, False))[0] or ""

            fecha_txt, fecha_es_texto, fecha_nativa = valores.get(
                COL_FECHA, ("", False, False))

            filas.append({
                "fila": num_fila,
                "fecha_cruda": fecha_txt or "",
                "fecha_es_texto": bool(fecha_es_texto) or not fecha_nativa,
                "nombre_crudo": crudo(COL_NOMBRE),
                "ciudad_cruda": crudo(COL_CIUDAD),
                "tipo_crudo": crudo(COL_TIPO),
                "valor_crudo": crudo(COL_VALOR),
            })
        return filas


# ===========================================================================
# 2. LIMPIEZA CAMPO POR CAMPO  (funciones puras: entrada -> salida, sin efectos)
# ===========================================================================

def _serial_excel_a_fecha(serial: float) -> dt.date:
    """
    Excel cuenta los días desde el 1899-12-30 (día 0). Ej.: 42370 -> 2015-12-05.
    (El desfase de 2 días respecto al 1900-01-01 viene del bug histórico de
    Excel con el año bisiesto 1900; usar 1899-12-30 lo corrige para fechas
    modernas.)
    """
    return dt.date(1899, 12, 30) + dt.timedelta(days=int(round(float(serial))))


_RE_FECHA_TEXTO = re.compile(r"^\s*(\d{1,2})\s*/\s*(\d{1,2})\s*/\s*(\d{2,4})\s*$")


def limpiar_fecha(cruda: str, es_texto: bool):
    """
    Devuelve (fecha_iso | None, nota | None).
      - fecha_iso: 'YYYY-MM-DD'
      - nota: texto para el reporte si algo no cuadró (fuera de rango) o None.
    Si no se puede parsear de ninguna forma -> (None, motivo) y la fila se excluye.
    """
    cruda = (cruda or "").strip()
    if not cruda:
        return None, "fecha vacía"

    fecha = None
    if not es_texto:
        # Fecha nativa de Excel: 'cruda' es el número serial.
        try:
            fecha = _serial_excel_a_fecha(cruda)
        except (ValueError, OverflowError):
            return None, f"serial de fecha inválido: {cruda!r}"
    else:
        # Fecha escrita a mano. CLAUDE.md §4.1: formato colombiano DD/MM/YYYY.
        # (Confirmado en el análisis: las 228 fechas-texto tienen día > 12,
        #  así que no hay ambigüedad con MM/DD.)
        m = _RE_FECHA_TEXTO.match(cruda)
        if not m:
            return None, f"fecha-texto no reconocida: {cruda!r}"
        d, mth, y = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if y < 100:                                 # '19' -> 2019
            y += 2000
        try:
            fecha = dt.date(y, mth, d)
        except ValueError:
            return None, f"fecha-texto imposible (día/mes fuera de rango): {cruda!r}"

    # Fecha válida pero fuera del rango esperado -> se conserva y se avisa.
    if fecha < FECHA_MIN or fecha > FECHA_MAX:
        return fecha.isoformat(), f"fecha fuera de rango [{FECHA_MIN}..{FECHA_MAX}]: {fecha.isoformat()} (original {cruda!r})"

    return fecha.isoformat(), None


def limpiar_nombre(crudo: str) -> str:
    """
    CLAUDE.md §4.2: quitar tabulaciones/saltos al inicio y final, colapsar
    espacios múltiples. NO se cambia mayúsculas/minúsculas.
    `\\s` cubre espacio, tab (\\t) y salto de línea (\\n).
    """
    return re.sub(r"\s+", " ", (crudo or "")).strip()


def _normalizar_ciudad(texto: str) -> str:
    """MAYÚSCULAS, sin tildes, sin puntuación de borde, espacios colapsados."""
    t = unicodedata.normalize("NFKD", texto or "")
    t = t.encode("ascii", "ignore").decode("ascii")
    t = t.upper()
    t = re.sub(r"\(.*?\)", " ", t)                  # quita "(ANTIOQUIA)"
    t = re.sub(r"[^A-Z0-9 ]+", " ", t)              # deja letras/dígitos/espacio
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _quitar_sufijo_departamento(ciudad: str) -> str:
    """
    'IBAGUE TOLIMA' -> 'IBAGUE' ; 'CALI VALLE DEL CAUCA' -> 'CALI'.
    Va probando: si la ciudad TERMINA en el nombre de un departamento, lo corta.
    Se ordena de más largo a más corto para cortar 'NORTE DE SANTANDER' antes
    que 'SANTANDER'.
    """
    for dep in sorted(tc.DEPARTAMENTOS, key=len, reverse=True):
        if ciudad != dep and ciudad.endswith(" " + dep):
            return ciudad[: -len(dep)].strip()
    return ciudad


def limpiar_ciudad(cruda: str):
    """
    Devuelve (ciudad_final, correccion | None, reconocida: bool).
      - ciudad_final: texto normalizado (posiblemente corregido)
      - correccion: (original, corregida) si se aplicó un typo del diccionario
      - reconocida: True si la consideramos una ciudad válida conocida
    CLAUDE.md §4.3: solo corregimos typos evidentes; lo dudoso se deja igual y
    se reporta.
    """
    original_norm = _normalizar_ciudad(cruda)
    if not original_norm:
        return "", None, False

    sin_sufijo = _quitar_sufijo_departamento(original_norm)
    correccion = None

    if original_norm in tc.TYPOS:                   # typo sobre el texto completo
        ciudad = tc.TYPOS[original_norm]
        correccion = (original_norm, ciudad)
    elif sin_sufijo in tc.TYPOS:                    # typo tras quitar departamento
        ciudad = tc.TYPOS[sin_sufijo]
        correccion = (original_norm, ciudad)
    elif sin_sufijo != original_norm and sin_sufijo in tc.CIUDADES_CONOCIDAS:
        # Quitar el departamento SOLO si lo que queda es una ciudad conocida.
        # Así "IBAGUE TOLIMA" -> "IBAGUE", pero "PUERTO BOYACA" no se vuelve
        # "PUERTO" (Boyacá es departamento pero aquí es parte del nombre).
        ciudad = sin_sufijo
    else:
        ciudad = original_norm

    reconocida = ciudad in tc.CIUDADES_CONOCIDAS
    return ciudad, correccion, reconocida


_RE_SOLO_DIGITOS = re.compile(r"^\d+(\.\d+)?$")


def limpiar_valor(crudo: str):
    """
    Devuelve (valor_int | None, nota | None).
    CLAUDE.md §4.4: si no hay valor o es corrupto -> None (la fila se excluye).
    """
    s = (crudo or "").strip().replace("$", "").replace(" ", "")
    if not s:
        return None, "sin valor de venta"
    if _RE_SOLO_DIGITOS.match(s):
        n = int(round(float(s)))
        # Un valor 0 se trata como "sin valor" (dato incompleto): la fila se
        # excluye y se reporta, igual que las celdas vacías.
        return (n, None) if n > 0 else (None, "valor de venta = 0")
    # Quitar separadores de miles tipo 1.234.567 o 1,234,567 y reintentar.
    s2 = re.sub(r"[.,](?=\d{3}(\D|$))", "", s)
    s2 = re.sub(r"[^\d]", "", s2)
    if s2:
        return int(s2), f"valor de venta con formato raro, se interpretó {crudo!r} -> {int(s2)}"
    return None, f"valor de venta no numérico: {crudo!r}"


# ===========================================================================
# 3. COLUMNA TIPO DE VENTA  (la más compleja - CLAUDE.md §4.5)
# ===========================================================================

# Muchas celdas describen todo el pedido en un solo párrafo sin comas. Además
# de los separadores obvios, cortamos JUSTO ANTES de estas palabras clave, que
# casi siempre inician un ítem nuevo dentro de la celda (CLAUDE.md §4.5: "si hay
# indicios de más de una categoría, generar una fila por categoría").
_RE_CORTE_SECUNDARIO = re.compile(
    r"(?=\bCAMBIO\s+DE\b|\bCAMBIO\b|\bARREGLO\b|\bMANTENIMIENTO\b|\bMTTO\b"
    r"|\bDISE(?:N|Ñ)O\b|\bACTUALIZACION\b|\bREVISION\b|\bINSTALACION\b"
    r"|\bCOMPRA\b|\bMODIFICACION\b|\bCONTROL\b|\bCONSOLA\b|\bOBSEQUIO\b"
    # separar también la logística: si no, "MODIF TACTICA DOMICILIO" se
    # tomaría entero como logística y se perdería la modificación.
    r"|\bDOMICILIOS?\b|\bENVIO\b|\bENVIOS\b|\bPORCENTAJE\b|\bDESCUENTO\b)",
    re.IGNORECASE,
)


def separar_tipos(tipo_crudo: str):
    """
    Parte la celda TIPO DE VENTA en fragmentos, clasifica cada uno y devuelve:

        categorias     -> lista ordenada de categorías detectadas (sin repetir)
        pendientes     -> lista de (fragmento_normalizado, motivo) que Edgar debe
                          resolver: motivo ∈ {'DESCONOCIDO', 'AMBIGUO'}
        fuera_alcance  -> lista de fragmentos "FUERA DE ALCANCE" (códigos de
                          juego, skins...): no generan categoría pero se
                          reportan aparte.

    Separadores primarios: coma, salto de línea, punto y coma y '+'.
    Corte secundario: antes de palabras clave (ver `_RE_CORTE_SECUNDARIO`).
    """
    categorias = []
    pendientes = []
    fuera_alcance = []
    hubo_etiqueta = False        # ¿se descartó al menos un nombre de dispositivo?

    # 1º nivel: separadores explícitos.
    trozos_1 = re.split(r"[\n,;+/]+", tipo_crudo or "")
    # 2º nivel: cada trozo se vuelve a cortar justo antes de las palabras clave
    # de "ítem nuevo" (muchas celdas describen todo el pedido sin comas).
    trozos = []
    for t in trozos_1:
        trozos.extend(p for p in _RE_CORTE_SECUNDARIO.split(t) if p and p.strip())

    for trozo in trozos:
        frag = dic.normalizar(trozo)
        if not frag:
            continue

        etiqueta = dic.clasificar_fragmento(frag)

        if etiqueta == "ETIQUETA":
            hubo_etiqueta = True
            continue                                # nombre de dispositivo: contexto
        elif etiqueta == "IGNORAR":
            continue                                # logística/pago: se descarta
        elif etiqueta == "FUERA DE ALCANCE":
            fuera_alcance.append(frag)
        elif etiqueta == "AMBIGUO":
            pendientes.append((frag, "AMBIGUO"))
        elif etiqueta is None:
            pendientes.append((frag, "DESCONOCIDO"))
        else:                                        # una de las 3 categorías
            if etiqueta not in categorias:
                categorias.append(etiqueta)

    # Decisión de Edgar (2026-08-28): si la celda es SOLO el nombre de un
    # control/consola (todo quedó como ETIQUETA) y no hay servicio ni producto
    # fuera de alcance, se cuenta como COMPRA DE CONTROL.
    if not categorias and not pendientes and not fuera_alcance and hubo_etiqueta:
        categorias = [dic.CC]

    # Ordenar según ORDEN_CATEGORIAS para que la salida sea reproducible.
    categorias.sort(key=lambda c: ORDEN_CATEGORIAS.index(c))
    return categorias, pendientes, fuera_alcance


def repartir_valor(total: int, n: int) -> list[int]:
    """
    Reparte `total` en `n` enteros que SUMAN EXACTAMENTE `total`
    (decisión de Edgar: partes iguales). El sobrante de la división (unos pocos
    pesos) se reparte de a $1 entre las primeras filas.

        repartir_valor(100, 3) -> [34, 33, 33]
    """
    base, resto = divmod(total, n)
    return [base + (1 if i < resto else 0) for i in range(n)]


# ===========================================================================
# 4. PIPELINE PRINCIPAL
# ===========================================================================

def procesar():
    os.makedirs(DIR_SALIDA, exist_ok=True)
    filas = leer_hoja1(RUTA_XLSX)
    total_leidas = len(filas)

    # --- acumuladores para las salidas y el reporte ---
    salida = []                                     # filas finales del CSV
    excluidas = defaultdict(list)                   # motivo -> [descripcion, ...]
    fechas_avisos = []                              # notas de fecha fuera de rango
    valor_avisos = []                               # notas de valor con formato raro
    correcciones_ciudad = []                        # (original, corregida)
    ciudades_a_revisar = Counter()                  # ciudad -> veces (no reconocida)
    pendientes_frag = Counter()                     # fragmento -> veces (sin clasificar)
    pendientes_motivo = {}                          # fragmento -> 'AMBIGUO'/'DESCONOCIDO'
    pendientes_ejemplo = {}                         # fragmento -> celda de ejemplo
    repartos = []                                   # (fila, valor, n, lista) para el reporte
    fuera_alcance_items = []                         # (fila, fragmento) productos fuera de alcance
    vistas = set()                                  # firmas de fila -> detectar duplicados

    for f in filas:
        etiqueta_fila = f"fila {f['fila']}"

        # ---------- 4.1 limpiar cada campo ----------
        fecha_iso, nota_fecha = limpiar_fecha(f["fecha_cruda"], f["fecha_es_texto"])
        nombre = limpiar_nombre(f["nombre_crudo"])
        ciudad, correccion, ciudad_ok = limpiar_ciudad(f["ciudad_cruda"])
        valor, nota_valor = limpiar_valor(f["valor_crudo"])
        categorias, pendientes, fuera_alcance = separar_tipos(f["tipo_crudo"])

        # ---------- 4.2 exclusiones (CLAUDE.md §4 + decisiones de Edgar) ----------
        motivos = []
        if fecha_iso is None:
            motivos.append(f"fecha inválida ({nota_fecha})")
        if not nombre:
            motivos.append("sin nombre")
        if not ciudad:
            motivos.append("sin ciudad")
        if valor is None:
            motivos.append(nota_valor or "sin valor")
        if not (f["tipo_crudo"] or "").strip():
            motivos.append("sin tipo de venta")

        if motivos:
            excluidas["campos incompletos"].append(f"{etiqueta_fila}: " + "; ".join(motivos))
            continue

        # ---------- 4.3 duplicado exacto ----------
        firma = (fecha_iso, nombre, ciudad, (f["tipo_crudo"] or "").strip(), valor)
        if firma in vistas:
            excluidas["fila duplicada exacta"].append(
                f"{etiqueta_fila}: {nombre} / {ciudad} / {fecha_iso} / {valor}")
            continue
        vistas.add(firma)

        # ---------- 4.4 avisos que NO excluyen ----------
        if nota_fecha:
            fechas_avisos.append(f"{etiqueta_fila}: {nota_fecha}")
        if nota_valor:
            valor_avisos.append(f"{etiqueta_fila}: {nota_valor}")
        if correccion:
            correcciones_ciudad.append(correccion)
        if not ciudad_ok:
            ciudades_a_revisar[ciudad] += 1
        for frag in fuera_alcance:
            fuera_alcance_items.append(f"{etiqueta_fila}: {frag}")

        # ---------- 4.5 TIPO DE VENTA con fragmentos sin resolver ----------
        # Si la fila tiene algún fragmento AMBIGUO o DESCONOCIDO, la fila
        # ENTERA queda pendiente (no la partimos con un valor mal repartido).
        if pendientes:
            for frag, motivo in pendientes:
                pendientes_frag[frag] += 1
                pendientes_motivo[frag] = motivo
                pendientes_ejemplo.setdefault(frag, f["tipo_crudo"].replace("\n", " / ").strip())
            excluidas["pendiente de clasificar TIPO DE VENTA"].append(
                f"{etiqueta_fila}: fragmentos {', '.join(repr(fr) for fr, _ in pendientes)}"
                f"  |  celda: {f['tipo_crudo'].replace(chr(10), ' / ').strip()!r}")
            continue

        # ---------- 4.6 sin ninguna categoría (todo era etiqueta/logística) ----------
        if not categorias:
            motivo = ("solo producto fuera de alcance (código de juego / skin)"
                      if fuera_alcance else
                      "sin categoría detectada en TIPO DE VENTA")
            excluidas[motivo].append(
                f"{etiqueta_fila}: celda {f['tipo_crudo'].replace(chr(10), ' / ').strip()!r}")
            continue

        # ---------- 4.7 expandir: una fila de salida por categoría ----------
        montos = repartir_valor(valor, len(categorias))
        if len(categorias) > 1:
            repartos.append((f["fila"], valor, len(categorias), montos))
        for cat, monto in zip(categorias, montos):
            salida.append({
                "fecha_compra": fecha_iso,
                "nombre_cliente": nombre,
                "ciudad": ciudad,
                "valor_compra": monto,
                "tipo_compra": cat,
            })

    _escribir_csv_final(salida)
    _escribir_tipos_sin_clasificar(pendientes_frag, pendientes_motivo, pendientes_ejemplo)
    _escribir_correcciones_ciudad(correcciones_ciudad)
    _escribir_reporte(
        total_leidas, salida, excluidas, fechas_avisos, valor_avisos,
        correcciones_ciudad, ciudades_a_revisar, pendientes_frag,
        pendientes_motivo, repartos, fuera_alcance_items)

    _resumen_consola(total_leidas, filas, salida, excluidas, pendientes_frag)


# ===========================================================================
# 5. ESCRITURA DE ARCHIVOS
# ===========================================================================

def _escribir_csv_final(salida: list[dict]):
    ruta = os.path.join(DIR_SALIDA, "especialmodz_clientes_limpio.csv")
    columnas = ["fecha_compra", "nombre_cliente", "ciudad", "valor_compra", "tipo_compra"]
    # utf-8-sig = UTF-8 con BOM -> Excel lo abre con acentos correctos.
    with open(ruta, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=columnas, delimiter=DELIM)
        w.writeheader()
        w.writerows(salida)


def _escribir_tipos_sin_clasificar(frag_cnt, frag_motivo, frag_ej):
    ruta = os.path.join(DIR_SALIDA, "tipos_sin_clasificar.csv")
    with open(ruta, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, delimiter=DELIM)
        w.writerow(["fragmento", "frecuencia", "motivo", "categoria_asignada", "celda_ejemplo"])
        for frag, n in frag_cnt.most_common():
            w.writerow([frag, n, frag_motivo[frag], "", frag_ej.get(frag, "")])


def _escribir_correcciones_ciudad(correcciones):
    ruta = os.path.join(DIR_SALIDA, "correcciones_ciudad.csv")
    resumen = Counter(correcciones)
    with open(ruta, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, delimiter=DELIM)
        w.writerow(["ciudad_original", "ciudad_corregida", "veces"])
        for (orig, corr), n in sorted(resumen.items(), key=lambda x: -x[1]):
            w.writerow([orig, corr, n])


def _escribir_reporte(total_leidas, salida, excluidas, fechas_avisos, valor_avisos,
                      correcciones_ciudad, ciudades_a_revisar, pendientes_frag,
                      pendientes_motivo, repartos, fuera_alcance_items):
    ruta = os.path.join(DIR_SALIDA, "reporte_incidencias.md")
    total_excluidas = sum(len(v) for v in excluidas.values())
    suma_valor = sum(r["valor_compra"] for r in salida)

    L = []
    L.append("# Reporte de incidencias — limpieza base de datos clientes")
    L.append("")
    L.append(f"- Generado: {dt.datetime.now():%Y-%m-%d %H:%M}")
    L.append(f"- Archivo fuente: `Doc/1.Base de Datos Clientes 2017.xlsx`, hoja `{HOJA_OBJETIVO}`")
    L.append("")
    L.append("## 1. Cuadre de filas")
    L.append("")
    L.append(f"| Concepto | Filas |")
    L.append(f"|---|---:|")
    L.append(f"| Leídas del Excel (fila {PRIMERA_FILA_DATOS} en adelante) | {total_leidas} |")
    for motivo, items in sorted(excluidas.items()):
        L.append(f"| Excluidas — {motivo} | {len(items)} |")
    L.append(f"| **Pedidos que pasan a la salida** | **{total_leidas - total_excluidas}** |")
    L.append(f"| Filas en el CSV final (tras dividir por tipo) | {len(salida)} |")
    L.append("")
    L.append(f"Cuadre: {total_leidas} leídas = {total_leidas - total_excluidas} incluidas "
             f"+ {total_excluidas} excluidas.")
    L.append("")
    L.append(f"Suma de `valor_compra` en el CSV final: **{suma_valor:,}**. "
             f"Por decisión de Edgar el valor de cada pedido se reparte en partes "
             f"iguales entre sus filas, así que esta suma SÍ equivale al ingreso "
             f"real de los pedidos incluidos.")
    L.append("")

    L.append("## 2. Filas excluidas (detalle)")
    for motivo, items in sorted(excluidas.items()):
        L.append("")
        L.append(f"### {motivo} — {len(items)}")
        L.append("")
        for it in items:
            L.append(f"- {it}")

    L.append("")
    L.append("## 3. Fechas fuera del rango esperado (se conservan)")
    L.append("")
    L.extend(f"- {a}" for a in fechas_avisos) if fechas_avisos else L.append("_Ninguna._")

    L.append("")
    L.append("## 4. Valores de venta con formato inusual (se conservan)")
    L.append("")
    L.extend(f"- {a}" for a in valor_avisos) if valor_avisos else L.append("_Ninguno._")

    L.append("")
    L.append("## 5. Correcciones de ciudad aplicadas")
    L.append("")
    if correcciones_ciudad:
        resumen = Counter(correcciones_ciudad)
        L.append("| Original | Corregida | Veces |")
        L.append("|---|---|---:|")
        for (orig, corr), n in sorted(resumen.items(), key=lambda x: -x[1]):
            L.append(f"| {orig} | {corr} | {n} |")
        L.append("")
        L.append("Detalle completo en `correcciones_ciudad.csv`.")
    else:
        L.append("_Ninguna._")

    L.append("")
    L.append("## 6. Ciudades NO reconocidas (revisar a mano — se dejaron tal cual)")
    L.append("")
    if ciudades_a_revisar:
        L.append("| Ciudad (normalizada) | Veces |")
        L.append("|---|---:|")
        for ciu, n in ciudades_a_revisar.most_common():
            L.append(f"| {ciu} | {n} |")
    else:
        L.append("_Ninguna._")

    L.append("")
    L.append("## 7. Fragmentos de TIPO DE VENTA sin clasificar")
    L.append("")
    if pendientes_frag:
        n_amb = sum(1 for f in pendientes_frag if pendientes_motivo[f] == "AMBIGUO")
        n_des = len(pendientes_frag) - n_amb
        L.append(f"{len(pendientes_frag)} fragmentos distintos sin resolver "
                 f"({n_amb} ambiguos + {n_des} desconocidos). "
                 f"**Las filas que los contienen NO están en el CSV final.** "
                 f"Revisa `tipos_sin_clasificar.csv`, asigna categoría y volvemos a correr.")
        L.append("")
        L.append("| Fragmento | Frecuencia | Motivo |")
        L.append("|---|---:|---|")
        for frag, n in pendientes_frag.most_common(60):
            L.append(f"| {frag} | {n} | {pendientes_motivo[frag]} |")
        if len(pendientes_frag) > 60:
            L.append(f"| … {len(pendientes_frag) - 60} más | | |")
    else:
        L.append("_Ninguno: toda la columna TIPO DE VENTA quedó clasificada._")

    L.append("")
    L.append("## 8. Pedidos divididos en varias filas (reparto de valor)")
    L.append("")
    if repartos:
        L.append(f"{len(repartos)} pedidos se dividieron en 2+ filas. Ejemplos:")
        L.append("")
        L.append("| Fila Excel | Valor pedido | Nº filas | Reparto |")
        L.append("|---:|---:|---:|---|")
        for fila, val, n, montos in repartos[:40]:
            L.append(f"| {fila} | {val:,} | {n} | {' + '.join(f'{m:,}' for m in montos)} |")
        if len(repartos) > 40:
            L.append(f"| … {len(repartos) - 40} más | | | |")
    else:
        L.append("_Ningún pedido tuvo más de una categoría._")

    L.append("")
    L.append("## 9. Productos fuera de alcance (códigos de juego / skins)")
    L.append("")
    if fuera_alcance_items:
        L.append(f"{len(fuera_alcance_items)} menciones. No generan fila (no son "
                 f"un control). Si el pedido tenía además otro servicio, ese sí "
                 f"quedó en el CSV.")
        L.append("")
        L.extend(f"- {it}" for it in fuera_alcance_items)
    else:
        L.append("_Ninguno._")

    L.append("")
    with open(ruta, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


def _resumen_consola(total_leidas, filas, salida, excluidas, pendientes_frag):
    print("=" * 64)
    print(f"Filas leídas del Excel      : {total_leidas}")
    for motivo, items in sorted(excluidas.items()):
        print(f"  - excluidas ({motivo}): {len(items)}")
    incluidas = total_leidas - sum(len(v) for v in excluidas.values())
    print(f"Pedidos incluidos           : {incluidas}")
    print(f"Filas en el CSV final       : {len(salida)}")
    print(f"Suma valor_compra (CSV)     : {sum(r['valor_compra'] for r in salida):,}")
    print(f"Fragmentos TIPO sin resolver: {len(pendientes_frag)}")
    print("=" * 64)

    # --- comprobaciones automáticas (assert) ---
    assert incluidas + sum(len(v) for v in excluidas.values()) == total_leidas, \
        "El cuadre de filas no da: revisar."
    for r in salida:
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", r["fecha_compra"]), r
        assert r["tipo_compra"] in ORDEN_CATEGORIAS, r
        assert isinstance(r["valor_compra"], int) and r["valor_compra"] >= 0, r
        assert r["nombre_cliente"] and r["ciudad"], r
    print("OK: todas las comprobaciones automáticas pasaron.")
    if pendientes_frag:
        print(f"\n>>> Quedan {len(pendientes_frag)} fragmentos sin clasificar "
              f"(ver salida/tipos_sin_clasificar.csv y §7 del reporte). Son "
              f"trozos sueltos o descripciones muy específicas; sus filas NO "
              f"están en el CSV. Si reconoces alguno, añádelo a "
              f"diccionario_tipos.py y vuelve a correr.")


# ===========================================================================
# 6. PUNTO DE ENTRADA
# ===========================================================================

if __name__ == "__main__":
    if not os.path.exists(RUTA_XLSX):
        sys.exit(f"No encuentro el Excel en: {RUTA_XLSX}")
    procesar()
