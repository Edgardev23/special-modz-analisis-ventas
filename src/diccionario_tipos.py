# -*- coding: utf-8 -*-
"""
diccionario_tipos.py
====================

Clasifica cada fragmento de la columna TIPO DE VENTA en una de las 3 categorías
de CLAUDE.md:

    "SERVICIO TECNICO"    -> reparar / mantener algo que el cliente ya tiene
    "COMPRA DE CONTROL"   -> venta de un control / consola / accesorio nuevo
    "MODIFICACION PROPIA" -> personalización o mejora que antes no existía

Más tres "categorías técnicas" que NO generan fila de salida:

    "ETIQUETA" -> solo el nombre del dispositivo ("CONTROL PS4 NEGRO # 1"):
                  es contexto, no un servicio. Se descarta en silencio.
    "IGNORAR"  -> domicilio, envío, descuento, abono... no es un tipo de venta.
    "AMBIGUO"  -> podría ir en más de una categoría. CLAUDE.md pide NO adivinar:
                  va al reporte `tipos_sin_clasificar.csv` para que Edgar decida.

Y `None` = fragmento desconocido (ninguna regla coincide) -> también al reporte.

--------------------------------------------------------------------------
FLUJO de `clasificar_fragmento` (todo en MAYÚSCULAS, sin tildes):
  0. Se le quitan prefijos "PROMO ", "OBSEQUIO ", "OFERTA " (precio, no categoría).
  1. ¿Es solo etiqueta de dispositivo?          -> "ETIQUETA"
  2. ¿Coincide con un concepto AMBIGUO?          -> "AMBIGUO"
  3. ¿Es logística/pago?                          -> "IGNORAR"
  4. ¿Coincide alguna regla de categoría?         -> esa categoría (orden importa)
  5. ¿Es un dispositivo con nombre raro y sin
     señal de reparación?                         -> "ETIQUETA"
  6. Nada coincide                                -> None
--------------------------------------------------------------------------

Este archivo es SOLO DATOS + funciones puras. La orquestación está en
`limpieza_clientes.py`. Cuando Edgar decida un fragmento AMBIGUO/DESCONOCIDO:
  - si es una categoría -> añade su palabra clave a REGLAS_<categoria>
  - si es logística      -> añádela a NEEDLES_IGNORAR
  - si es contexto       -> añádela a PALABRAS_ETIQUETA
y se vuelve a correr el script.
"""

import re
import unicodedata

ST = "SERVICIO TECNICO"
CC = "COMPRA DE CONTROL"
MP = "MODIFICACION PROPIA"
XX = "FUERA DE ALCANCE"      # productos que no son un control (códigos de juego, skins...)


# ---------------------------------------------------------------------------
def normalizar(texto: str) -> str:
    """MAYÚSCULAS, sin tildes/ñ, sin signos raros (deja letras, dígitos, % y #)."""
    t = unicodedata.normalize("NFKD", texto)
    t = t.encode("ascii", "ignore").decode("ascii")     # quita tildes; ñ -> n
    t = t.upper()
    t = re.sub(r"[^A-Z0-9%#]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


_PREFIJOS_PRECIO = re.compile(r"^(PROMO(CION)?|OBSEQUIO|OFERTA|OBSEQ|REGALO)\s+")


# ---------------------------------------------------------------------------
# PASO 1 — Palabras "etiqueta de dispositivo".
# Si al borrarlas TODAS el fragmento queda vacío, es solo contexto -> ETIQUETA.
# Se usan como expresión regular, por eso hay comodines (\w*) y variantes.
# ---------------------------------------------------------------------------
PALABRAS_ETIQUETA = [
    r"CONTR\w*", r"C[AO]NTR\w*", r"CTROL\w*", r"CONS?OL\w*", r"CONDSOL\w*", r"MANDOS?",  # control / consola / mando (+ typos y pegados)
    r"ALPINE", r"MIDNIGHT", r"BERRY", r"BLUE\w*", r"SUNSET", r"SUSET", r"ORANGE",
    r"PULSE", r"TURTLE", r"BEACH", r"POWER\s?A", r"CALL\s+OF\s+DUTY",
    r"PLAY\s?STATION", r"PLAYS?", r"PS\s?[1-5]", r"PS\w*",
    r"XBOX", r"X\s?BOX", r"X360", r"\b360\b", r"\bONE\b",
    r"SERIES?", r"\bSCUFF?\b", r"\bELITE\b", r"DUAL\w*", r"NACON",
    r"\bFAT\b", r"\bSLIM\b", r"\bPRO\b", r"PHA?NTOM", r"\bEDGE\b",
    # colores
    r"NEGR[OA]S?", r"BLANC[OA]S?", r"ROJ[OA]S?", r"AZUL(ES)?", r"MARINO",
    r"VERDES?", r"AMARILL[OA]S?", r"NARANJAS?", r"MORAD[OA]S?", r"ROSAD[OA]S?",
    r"\bROSA\b", r"GRIS(ES)?", r"DORAD[OA]S?", r"PLATEAD[OA]S?", r"VIN[OI]TINTO",
    r"CAMUFLAD[OA]S?", r"TRANSPARENTES?", r"CELESTES?", r"MINTY", r"\bX\b", r"\bS\b",
    r"\bMATE\b", r"\bVANTAGE\b", r"\bSPIDERMAN\b", r"\bPICO\b",
    # disponibilidad / marketing = contexto, no servicio
    r"ENTREGA", r"INMEDIATA?", r"DISPONIBLES?", r"PROMO\w*", r"OFERTAS?",
    # conectores / relleno
    r"\bDE\b", r"\bDEL\b", r"\bLA\b", r"\bLAS\b", r"\bLOS\b", r"\bEL\b",
    r"\bY\b", r"\bCON\b", r"\bPARA\b", r"\bPOR\b", r"\bA\b",
    r"CLI?E?NTES?", r"CLEINTE", r"TRAE", r"TRAJO", r"PROPIO",
    r"\bNRO\b", r"\bNUM\b", r"\bNO\b", r"#", r"\d+",
]
_RE_ETIQUETA = re.compile("|".join(PALABRAS_ETIQUETA))


# ---------------------------------------------------------------------------
# PASO 2 — Conceptos AMBIGUOS: los decide Edgar.
#
# Edgar resolvió TODOS los conceptos ambiguos el 2026-08-28. Sus decisiones
# quedaron incorporadas a REGLAS (más abajo):
#   - acetato / carcasa / chasis .................... SERVICIO TECNICO
#   - "cambio" del sistema táctico .................. SERVICIO TECNICO
#   - cambio de capuchas / caperuzas ............... SERVICIO TECNICO
#   - pasta térmica / metal líquido ................ SERVICIO TECNICO
#   - calibración ................................. SERVICIO TECNICO
#   - disco duro / SSD / ampliar memoria .......... SERVICIO TECNICO
#   - rejilla antipolvo .......................... SERVICIO TECNICO
#   - batería / pila ............................. SERVICIO TECNICO
#   - garantía .................................. SERVICIO TECNICO
#   - personalización genérica .................. MODIFICACION PROPIA
#   - Back Button Attachment .................... MODIFICACION PROPIA
#   - cable de carga / estuche / cargador ....... COMPRA DE CONTROL
#   - códigos de juego / skins Fortnite / V-bucks  FUERA DE ALCANCE (se excluyen
#                                                 y se listan aparte)
#
# La lista queda vacía. Si en el futuro aparece un concepto nuevo dudoso,
# añádelo aquí y su fila quedará pendiente para que lo revises.
# ---------------------------------------------------------------------------
PATRONES_AMBIGUOS = []
_RE_AMBIGUOS = [re.compile(p) for p in PATRONES_AMBIGUOS]


# ---------------------------------------------------------------------------
# PASO 3 — Logística / pagos: se ignoran (no son una venta).
# ---------------------------------------------------------------------------
NEEDLES_IGNORAR = [
    r"DOM[A-Z]{0,3}LIO", r"DOMICILIO", r"DOMCILIO", r"\bDOMI\b",
    r"\bENVIO\b", r"\bENVIOS\b", r"\bENVI\b", r"MENSAJERIA", r"ENTREGA\s+RAPIDA",
    r"RECOGIDA", r"RECOLECCION",
    r"PORCENTAJE", r"DESCUENTO", r"\bDCTO\b", r"\d+\s*%",
    r"^ABONO$", r"^SALDO$", r"^PAGO$", r"^RESTA\w*$", r"^GRACIAS$", r"PAGO\s*DE\s*PAQUETE",
    r"^PROMO(CION)?$", r"^O[BS]SEQUIO$", r"^REGALO$", r"^CORTESIA$", r"^OFERTA$",
    r"TRAN[SP]?PORTADORA", r"^FLETE$", r"^O[BS]?SEQUIO$",
]
_RE_IGNORAR = [re.compile(p) for p in NEEDLES_IGNORAR]


# ---------------------------------------------------------------------------
# PASO 4 — Reglas de categoría, EN ORDEN. Primera que coincide gana.
# Cada regla es (patrón_regex, categoria). Se buscan como subcadena
# (`rx.search`) sobre el fragmento normalizado.
#
# ¡El ORDEN importa!  Ejemplos:
#   - "ANALOGOS INTERCAMBIABLES" -> MODIFICACION (kit), no SERVICIO (cambio).
#   - "JOYSTICKS ALUMINIO"       -> MODIFICACION, no SERVICIO.
#   por eso las reglas de INTER / ALUMINIO van primero.
# ---------------------------------------------------------------------------
REGLAS = [
    # ---- FUERA DE ALCANCE: no es un control (se excluye y se lista aparte) ----
    (r"CODIGO|FORNITE|FORTNITE|V\s?BUCKS|\bVBUCKS\b|\bPAVOS\b|SKIN\s*FORT|\bMOUSE\b|TECLADO|STRIKE\s*PACK|\bALQUILER\b|INSTALACION\s+DE\s+JUEGO", XX),

    # ---- MODIFICACION: intercambiables / aluminio (antes que SERVICIO) ----
    (r"INTERCAM|\bINTER\b|\w+INTER\b|ANALO\w*INTER|JOYS\w*INTER", MP),
    (r"ALUMIN|KITALU|JOYSALU|BOT\w*ALU|JOYALU|\bALU\b", MP),

    # ---- SERVICIO TECNICO: conceptos que resolvió Edgar (2026-08-28) ----
    (r"\bACET\w*|CAMB\w*ACET|CARCA\w*|\bCHASIS\b|PANEL\s*TRASER|TAPA\s*TRASER|TAPA\s*DE\s*(LA\s*)?PILA", ST),
    (r"CAMB\w*\s*(DEL?\s*)?SIST\w*\s*(TACT\w*|SCUF)|CAMB\w*SIST\w*|CAMBIO\s+DEL?\s+SISTEMA|CAMBIOSISTEMA|CAMBISIST", ST),
    (r"CAPUCH\w*|CAPERU[ZS]A\w*|CAPUCHON|CAOCHA\w*|\bCPUCH\w*|\bCAPU\b", ST),
    (r"PASTA|KITPAS\w*|THERMAL|GRIZZLY|METAL\s*LIQUIDO|LIQUIDO\s*METAL", ST),
    (r"CALIBRA\w*", ST),
    (r"DISCO\s*DURO|DISCODURO|\bSSD\b|DISCO\s*SOLIDO|AMPLIA\w*\s*MEMORIA", ST),
    (r"REJILLA\w*", ST),
    (r"\bGARANT\w*", ST),
    (r"^BATERIA$|^PILA$|CAMBIO\s*DE\s*(LA\s*)?(BATERIA|PILA)", ST),

    # ---- SERVICIO TECNICO ----
    (r"MANTEN|MAN[A-Z]{0,3}NIM|M[A-Z]{1,2}T[A-Z]{0,2}NIM\w*|M[A-Z]NTEN|MANTTO|\bMANT\w*|\bMTTO\b|\bMTO\b|\bMNTO\b|\bMNT\b|REFRI|REFYMANT|LIMPI", ST),
    (r"ACTUALIZ\w*|ACTUIALIZ\w*|ACTUALIZACIN\w*|\bACT\s+SISTEMA\s+TACT", ST),
    (r"^ARR|^CAM[A-Z]|^REVIS|\bREPARA\w*|\bREPARACION\b|^AJUSTE|^REBALIN|^REBALL|\bFLEX\b", ST),
    (r"\bFISIC[OA]\b|SOLDAD|\bSOLDA\b|\bCORTO\b|SOBRECALENT|HUMEDAD|SULFAT|\bOXIDO\b|LIQUIDO|BOVINA|\bFUENTE\b|NO\s+(ENCIENDE|CONECTA|FUNCIONA|PRENDE|CARGA|SIRVE|DA\s+IMAGEN|ACTIVAN)", ST),
    (r"RECONSTRUCC|RECONTRUCC|REINSTALAC|RECONEXION|SINCRONIZ|SOFTWARE|FORMATE|\bPISTAS?\b|TARJETA|COMPONENTE|TORNILLER|CHASIS|\bHDMI\b", ST),
    (r"PUERTO\s*(DE\s*)?(CARGA|AUDIO|HDMI|USB|INTERNET)|PUERTOCARGA|PUERTO\s*DE\s*AUDIO", ST),
    (r"\bRESORTES?\b|\bMUELLES?\b|VIBRADOR|QUITAR\s+(LA\s+)?(MODIF|VIBRA)", ST),
    (r"P[O0]TENCIOMETR\w*|\bPOTEN\b|\bPCB\b|REFLUX|REBALL|REBALIN|REVICAUCH\w*|\bTAPAS?\b|TORNILLO", ST),
    (r"\bPIN\b|OIN\s*DE\s*CARGA|\bREJILLA", ST),
    (r"ANALOG|\bANALO\b|NALOGO|\bJOYS\b|JOYSTICK|JOYSTICIK|\bJOY\b|ARREJOYS|ARREGLOJOYS", ST),
    (r"PULSADOR|\bCAMBPUL\w*|\bPUERTO DE AUDIO\b|PUERTO\s*DE\s*CARGA|PIN\s*DE\s*CARGA|FLEX\s*DE\s*CARGA|CENTRO\s*DE\s*CARGA", ST),
    (r"POTENCIOMETR|\bMUELLE\b|\bRESORTE\b|\bCAUCHO\b|VENTILAD|DISIPAD|\bDIADEMA\b|\bMEJORA\b", ST),
    (r"DI[AS]?[GS]N\w*TIC\w*|\bDIGNOST\w*|GENERIC\w*|UNIDAD\s+DE\s+CD|\bLECTOR\b|BLU\s?RAY|DISCO\s+OPTICO|\bREVISION\b|\bREVI\b", ST),
    (r"CAU?[CV]HO\w*|\bCUCHO\b|JOYSRECOR|\bJOS[YC]\w*|JOYSTI[CK]\w*", ST),
    (r"ACTUALIZA\w*\s*(DEL?\s*)?SISTEMA\s*TACTICO|ACTUALIZA\w*\s*TACTIC", ST),
    (r"\bSERVICIO\s*TECNICO\b|\bST\b", ST),
    (r"CAMBIO\s*DE\s*BATERIA", ST),
    (r"^(RB|LB|L1|L2|L3|R1|R2|R3)$|^(L|R)[123]\s*(Y\s*)?(L|R)[123]$", ST),

    # ---- COMPRA DE CONTROL ----
    (r"\bCOMPRA\w*|^COMPR|\bCOMPA\b|\bCOMRA\b|\bCOPRA\b|\bCONRA\b|\bCX+C\w*|\bCXCM?\b|ADQUISIC|SE\s+LLEVA|LLEVA\s+CONTROL", CC),
    (r"\bNUEVOS?\b|\bNUEVAS?\b", CC),
    (r"KONTROL|K?[ROT]*NTROLFREE?K|FREE?K|FREAK", CC),
    # accesorios que se venden (decisión de Edgar 2026-08-28)
    (r"\bCABLE\b|\bCABLES\b|\bCABL\b|CALBLE|CABLE\s*USB|CABLE\s*DE\s*CARGA|CABLECAR\w*", CC),
    (r"ESTUCHE\w*|MALETIN\w*|\bMALETA\b|\bFUNDA\b|\bCASE\b", CC),
    (r"CARGADOR\w*|BASE\s*DE\s*CARGA|ESTACION\s*DE\s*CARGA|\bDOCK\b|MUELLE\s*DE\s*CARGA", CC),
    (r"^ADAPTADOR\w*$", CC),

    # ---- MODIFICACION PROPIA ----
    (r"PERSONALIZ\w*|BACK\s*BUTTON|BACKBUTTON|\bATTACHMENT\b|\d*GRIPS?\b", MP),  # decisión de Edgar 2026-08-28
    (r"DISE\w*|\bD[IO][SD]EN?O\w*|\bISENO\b|\bDIS\b|\bDSN\b|\bDS[ÑN]\b|\bJOKER\b|\bMARMOL\w*|^COLOR\b", MP),
    (r"ANTIDE\w*|ANTIDES\w*|ANTDES\w*|\w*[IE]DESLIZ\w*|\w*IDELIZ\w*|\bANTID?\b|\bANTI\b", MP),
    (r"PREVISUALIZ\w*|\bTACT\w*|SISTEMA\s+TACT\w*", MP),
    (r"MO[A-Z]{0,3}TAC|MO[A-Z]{0,3}TC|MDTAC|MODIF\s*TAC|MODIFIC\w*\s*TAC|\bTACTIC\w*|SISTEMA\s*TACTICO|4FUN|\d\s*FUN(CION)?|FUNCION\w*", MP),
    (r"\bMODIF\w*|\bMODIC\w*|\bMODF\w*|\bMDF\b|^MOD\b|\bMOD\s|\bANT\b", MP),
    (r"\bGAT\w*|G[AO]TILL\w*|\bGATLLOS\b|GATLAR|TRIGGER", MP),
    (r"RAPID\s*FIR|RAPIDF\w*|RAP\w*\s*FIR|RA[OP]ID\s*FIR|RAIPF\w*|RAPIF\w*|[FR]APID\s*FIR|AUTO\s*FIR|AUTOFIR|CHIP|\bMACRO\b|\bTURBO\b|REMAPE\w*", MP),
    (r"\bTOPES?\b|\bTOP\b|\bTOPS\b|TOPE\s*DE\s*GATILLO", MP),
    (r"\bBOT[A-Z0-9]\w*|\bBOOTN\w*|\bBTONE\w*|KITBOT|BOT\w*FLE|BOTYFLE|FECYBOTO|\bBOT\b|\bBOTO\b|\bBALAS?\b", MP),
    (r"\bFLECHA\w*|\bFLEC\w*|\bFLE\b|ARREFLE|CRUCETA|\bDPAD\b|\bD PAD\b", MP),
    (r"\bPALETA\w*|\bPALET\w*|PALANCAS?\s*TRASERAS?|\bPADDLES?\b", MP),
    (r"\bLOGOS?\b", MP),
    (r"\bNOMBR\w*|\bNOMB\b|\bNOM\b|\bNOMS\b|\bPANEL\b", MP),
    (r"HIDROGRAF|\bHIDRO\b|AEROGRAF|PINTUR|PINTAD|PINTAR|\bVINIL\w*|\bSKIN\b|\bSKYN\w*|CROMAD|\bCARBONO?\b|SPIDERMAN", MP),
    (r"SALPICAD\w*|PESTAN\w*|STI?C?KER\w*|STIKER\w*|\bPANEL\b|PANELLED|PANELTACT\w*|NOMBLOG\w*|MONBLOG\w*|\bNOMR\w*|\bNOBRE\b", MP),
    (r"\bLED\b|\bLEDS\b|\bLUCES\b|ILUMINAC|\bGLOW\b|PULSLED|PANELLED", MP),
    (r"\bKI[RT]?T\w*|\bKIRT\w*",  MP),   # kit* (kit de botones/flechas/joystick/joker...) -> MP
    (r"\bESTANDAR\b|\bPREMIUM\b|\bEXTRA\b|ADICIONAL\w*",  MP),  # niveles/extras de modificación
]
_REGLAS = [(re.compile(p), cat) for p, cat in REGLAS]


# ---------------------------------------------------------------------------
def clasificar_fragmento(fragmento_normalizado: str):
    """
    Devuelve una de:
      "SERVICIO TECNICO" | "COMPRA DE CONTROL" | "MODIFICACION PROPIA"
      "FUERA DE ALCANCE" | "ETIQUETA" | "IGNORAR" | "AMBIGUO" | None

    (La lista PATRONES_AMBIGUOS está vacía tras las decisiones de Edgar, así que
    "AMBIGUO" hoy no se devuelve; se deja el mecanismo por si aparece un
    concepto dudoso nuevo.)
    """
    f = fragmento_normalizado.strip()
    # PASO 0 — quitar prefijos de precio ("PROMO MOD TACTICA" -> "MOD TACTICA")
    prev = None
    while prev != f:
        prev = f
        f = _PREFIJOS_PRECIO.sub("", f).strip()
    if not f:
        return "IGNORAR"

    # PASO 1 — ¿solo etiqueta de dispositivo?
    resto = _RE_ETIQUETA.sub(" ", f)
    resto = re.sub(r"[#\s]+", " ", resto).strip()
    if not resto:
        return "ETIQUETA"

    # PASO 2 — conceptos ambiguos (preguntar a Edgar)
    for rx in _RE_AMBIGUOS:
        if rx.search(f):
            return "AMBIGUO"

    # PASO 3 — logística / pagos
    for rx in _RE_IGNORAR:
        if rx.search(f):
            return "IGNORAR"

    # PASO 4 — reglas de categoría, en orden
    for rx, cat in _REGLAS:
        if rx.search(f):
            return cat

    # PASO 5 — ¿es un control/consola con nombre de edición raro y SIN señal de
    # servicio? (p. ej. "CONTROL BERRY BLUE PS4", "XBOX ONE PHANTOM WHITE").
    # Entonces es solo etiqueta de dispositivo, aunque el color/edición no esté
    # en nuestra lista. Si en cambio hay indicio de reparación, lo dejamos
    # pendiente (None) para revisión.
    tiene_dispositivo = re.search(r"\bCONTROL\w*|\bCONS?OL\w*|\bMANDO|\bXBOX|\bPS\s?[1-5]|\bPLAY|\bNINTENDO|\bSWITCH\b|\bSCUFF?\b|\bELITE\b|\bNACON\b", f)
    tiene_señal_servicio = re.search(
        r"CAMB|ARREGL|REPAR|REVIS|DAÑ|DANI|FALLA|\bNO\b|SIRVE|MALO|CORTO|MOJ|SULF|GARANT|AJUST|SOLD", f)
    if tiene_dispositivo and not tiene_señal_servicio:
        return "ETIQUETA"

    # PASO 6 — desconocido
    return None
