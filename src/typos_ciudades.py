# -*- coding: utf-8 -*-
"""
typos_ciudades.py
=================

Datos de apoyo para limpiar la columna CIUDAD.

NO usamos una lista oficial de municipios (decisión de Edgar del 2026-08-28):
solo normalizamos el formato y corregimos una lista corta de errores de tipeo
"evidentes". Todo lo que quede sin reconocer se deja igual y se lista en el
reporte de incidencias para revisión manual.

Este archivo es SOLO DATOS. La lógica que lo usa está en `limpieza_clientes.py`
(función `limpiar_ciudad`). Puedes editar los diccionarios de abajo sin tocar
el script principal.
"""

# ---------------------------------------------------------------------------
# 1. Departamentos de Colombia (y algunas variantes mal escritas encontradas
#    en los datos). Se usan para quitar el sufijo cuando la celda trae
#    "CIUDAD DEPARTAMENTO", p. ej. "IBAGUE TOLIMA" -> "IBAGUE".
#    Todo va normalizado: MAYÚSCULAS y sin tildes.
# ---------------------------------------------------------------------------
DEPARTAMENTOS = {
    "AMAZONAS", "ANTIOQUIA", "ARAUCA", "ATLANTICO", "BOLIVAR", "BOYACA",
    "CALDAS", "CAQUETA", "CASANARE", "CAUCA", "CESAR", "CHOCO", "CORDOBA",
    "CUNDINAMARCA", "GUAINIA", "GUAVIARE", "HUILA", "MAGDALENA", "META",
    "NARINO", "NORTE DE SANTANDER", "PUTUMAYO", "QUINDIO", "RISARALDA",
    "SAN ANDRES Y PROVIDENCIA", "SANTANDER", "SUCRE", "TOLIMA",
    "VALLE DEL CAUCA", "VAUPES", "VICHADA", "LA GUAJIRA", "GUAJIRA",
    # variantes/errores vistos en la base:
    "VALLE",               # abreviación de "Valle del Cauca"
    "NORTE DE SANTNDER",   # falta la 'A'
    "DEPARTAMENTO DE SANTANDER",
    "RISALDA", "RISALADA", "RISARALADA",  # 'Risaralda' mal escrito
    "ANTOQUIA",            # 'Antioquia' mal escrito
    # abreviaturas de departamento vistas en la base:
    "ANT", "ANTIOQ", "TOL", "SANT", "STDER", "CUND", "CUNDI",
    "RISA", "NAR", "MAG", "BOY", "CORD", "CAQ", "CES",
}

# ---------------------------------------------------------------------------
# 2. Correcciones de tipeo "evidentes": forma-normalizada -> ciudad correcta.
#    La clave se compara DESPUÉS de: normalizar (mayúsculas, sin tildes,
#    espacios colapsados) y de quitar el sufijo de departamento.
#    Solo se incluyen casos con confianza alta.
# ---------------------------------------------------------------------------
TYPOS = {
    # --- Bogotá y sus barrios/localidades ---
    "BOOGTA": "BOGOTA",
    "BOGOTOA": "BOGOTA",
    "BOGOTA DC": "BOGOTA",
    "BOGOTA D C": "BOGOTA",
    "AMAPOLAS BOGOTA": "BOGOTA",
    "TINTAL BOGOTA": "BOGOTA",
    "FONTIBON": "BOGOTA",           # localidad de Bogotá
    "CIUDAD BOLIVAR": "BOGOTA",     # localidad de Bogotá (no el municipio de Antioquia)

    # --- Medellín y área metropolitana ---
    "MDELLIN": "MEDELLIN",
    "MEDELIIN": "MEDELLIN",
    "EL POBLADO": "MEDELLIN",       # comuna de Medellín
    "LACEJA": "LA CEJA",
    "CEJA": "LA CEJA",
    "SBANETA": "SABANETA",
    "ENVIGDO": "ENVIGADO",

    # --- Cali / Valle ---
    "CIUDAD DE CALI": "CALI",
    "CARATENA": "CARTAGENA",
    "GUADALAJARA DE BUGA": "BUGA",
    "RODALDILLO": "ROLDANILLO",
    "RONALDILLO": "ROLDANILLO",
    "ROZO": "PALMIRA",              # corregimiento de Palmira

    # --- Cartagena ---
    "CARTAGENA DE INDIAS": "CARTAGENA",

    # --- Eje cafetero ---
    "DOSQUEBRADAS": "DOSQUEBRADAS",
    "DOS QUEBRADAS": "DOSQUEBRADAS",
    "DOS QUEBRADA": "DOSQUEBRADAS",
    "DOS QUEBRDAS": "DOSQUEBRADAS",
    "DOS QUEBRDAS": "DOSQUEBRADAS",

    # --- Santander ---
    "PIE DE CUESTA": "PIEDECUESTA",
    "PIED DE CUESTA": "PIEDECUESTA",
    "FLORIDA BLANCA": "FLORIDABLANCA",

    # --- Otros ---
    "CAUCACIA": "CAUCASIA",
    "CATARGO": "CARTAGO",
    "CARTAJO": "CARTAGO",
    "FINLANDIA": "FILANDIA",
    "CARMEN DE VIBORAL": "EL CARMEN DE VIBORAL",
    "CHIA BOGOTA": "CHIA",
    "POAPYAN": "POPAYAN",
    "VILLAVIVENCIO": "VILLAVICENCIO",
    "SANTAROSADEOSOS": "SANTA ROSA DE OSOS",
    "SAN JOSE DEL GUAVAIRE": "SAN JOSE DEL GUAVIARE",
    "ESPINAL": "ESPINAL",
    "TOLIMA ESPINAL": "ESPINAL",
}

# ---------------------------------------------------------------------------
# 3. Lista corta de ciudades/municipios que consideramos "reconocidos".
#    Sirve solo para decidir si un valor va o no al reporte de incidencias.
#    No es exhaustiva: son las que aparecen varias veces en la base y las
#    principales del país. Un valor que no esté aquí NO se borra ni se cambia;
#    solo se marca "revisar" en el reporte.
# ---------------------------------------------------------------------------
CIUDADES_CONOCIDAS = {
    "BOGOTA", "MEDELLIN", "CALI", "BARRANQUILLA", "CARTAGENA", "CUCUTA",
    "BUCARAMANGA", "PEREIRA", "SANTA MARTA", "IBAGUE", "MANIZALES", "VILLAVICENCIO",
    "PASTO", "MONTERIA", "NEIVA", "ARMENIA", "POPAYAN", "SINCELEJO", "VALLEDUPAR",
    "TUNJA", "RIOHACHA", "FLORENCIA", "QUIBDO", "YOPAL", "MOCOA", "ARAUCA",
    "LETICIA", "SAN ANDRES ISLAS",
    # área metropolitana / municipios frecuentes en la base:
    "SOACHA", "CHIA", "ZIPAQUIRA", "CAJICA", "FACATATIVA", "MADRID", "MOSQUERA",
    "FUNZA", "COTA", "TENJO", "TOCANCIPA", "LA CALERA", "UBATE", "FUSAGASUGA",
    "GIRARDOT", "VILLETA", "LA VEGA", "SILVANIA",
    "ENVIGADO", "ITAGUI", "BELLO", "SABANETA", "LA ESTRELLA", "COPACABANA",
    "GIRARDOTA", "CALDAS", "RIONEGRO", "LA CEJA", "MARINILLA", "GUARNE",
    "EL RETIRO", "EL PENOL", "EL SANTUARIO", "EL CARMEN DE VIBORAL", "APARTADO",
    "CAREPA", "CHIGORODO", "TURBO", "SANTA ROSA DE OSOS", "SEGOVIA", "BARBOSA",
    "SANTAFE DE ANTIOQUIA", "SAN ROQUE", "SAN RAFAEL", "GRANADA", "ARANZAZU",
    "SALAMINA", "SUPIA", "RIOSUCIO", "CHINCHINA", "VILLAMARIA", "SANTA ROSA DE CABAL",
    "LA DORADA",
    "PALMIRA", "BUGA", "TULUA", "CARTAGO", "JAMUNDI", "YUMBO", "BUENAVENTURA",
    "SEVILLA", "CAICEDONIA", "ANDALUCIA", "CANDELARIA", "FLORIDA", "PRADERA",
    "ROLDANILLO", "EL DOVIO", "ALCALA", "MIRANDA", "CORINTO", "TIMBIO", "GUARANDA",
    "DOSQUEBRADAS", "SANTA ROSA DE CABAL", "LA VIRGINIA",
    "FLORIDABLANCA", "PIEDECUESTA", "GIRON", "BARRANCABERMEJA", "SAN GIL",
    "SOCORRO", "BARICHARA", "BARBOSA", "MALAGA", "VELEZ", "SABANA DE TORRES",
    "CONCEPCION", "ABREGO", "OCANA", "PAMPLONA", "LOS PATIOS", "VILLA DEL ROSARIO",
    "SOLEDAD", "MALAMBO", "BARANOA", "PUERTO COLOMBIA", "SABANALARGA",
    "CIENAGA", "PLATO", "EL BANCO", "SANTA ANA", "FUNDACION", "ARACATACA",
    "MAICAO", "URIBIA", "FONSECA", "SAN JUAN DEL CESAR", "VILLANUEVA",
    "AGUACHICA", "EL COPEY", "LA JAGUA DE IBIRICO", "BOSCONIA",
    "TURBACO", "ARJONA", "MAGANGUE", "EL CARMEN DE BOLIVAR",
    "SOGAMOSO", "DUITAMA", "CHIQUINQUIRA", "PAZ DE RIO", "PUERTO BOYACA",
    "MONTERIA", "PLANETA RICA", "MONTELIBANO", "CERETE", "SAHAGUN", "LORICA",
    "ESPINAL", "MARIQUITA", "HONDA", "LERIDA", "GUAMO", "MELGAR", "CHAPARRAL",
    "LIBANO", "PURIFICACION", "FLANDES",
    "GARZON", "PITALITO", "LA PLATA", "ACEVEDO", "CAMPOALEGRE",
    "GRANADA", "ACACIAS", "PUERTO GAITAN", "PUERTO LLERAS", "CASTILLA LA NUEVA",
    "PUERTO LOPEZ",
    "IPIALES", "TUMACO", "TUQUERRES", "LA UNION", "SANDONA", "SAN JUAN DE PASTO",
    "YOPAL", "AGUAZUL", "TAURAMENA", "VILLANUEVA", "PAZ DE ARIPORO",
    "MAICAO", "SAN JOSE DEL GUAVIARE",
    "PUERTO ASIS", "ORITO", "SIBUNDOY",
    "SABANETA", "BARRANCA",
    "MARIQUITA", "FRESNO", "SANTA ISABEL",
    "CAUCASIA", "TARAZA", "EL BAGRE", "NECHI", "ZARAGOZA",
    "BUGALAGRANDE", "ZARZAL", "OBANDO", "LA VICTORIA",
    "MESETAS", "SAN VICENTE DEL CAGUAN", "SALDANA",
    "VALLE DE SAN JOSE", "GUADALUPE",
    "GUADALAJARA DE BUGA",
    "PLANETA RICA",
    "PUERTO SALGAR", "GUADUAS",
    "SEGOVIA", "REMEDIOS",
    "PUERTO BERRIO", "CISNEROS", "MACEO",
    "SAN PEDRO", "SAN PELAYO",
    "PALMIRA",
    "DAGUA", "LA CUMBRE", "RESTREPO",
    "CAJIBIO", "PIENDAMO", "SANTANDER DE QUILICHAO", "PUERTO TEJADA", "VILLA RICA",
    "CALOTO", "GUACHENE",
    "GALAPA", "TUBARA", "USIACURI",
    "PAILITAS", "CURUMANI", "CHIMICHAGUA", "LA GLORIA", "PELAYA",
    "SAN MARCOS", "COROZAL", "SAMPUES", "TOLU", "COVENAS",
    "APIA", "BELEN DE UMBRIA", "GUATICA", "MARSELLA", "MISTRATO", "PUEBLO RICO",
    "QUINCHIA", "SANTUARIO", "FILANDIA", "MONTENEGRO", "CIRCASIA", "SALENTO",
    "GENOVA", "PIJAO", "CORDOBA", "BUENAVISTA",
    "PUERTO BOYACA", "PUERTO SALGAR", "PUERTO COLOMBIA", "PUERTO GAITAN",
    "PUERTO LOPEZ", "PUERTO LLERAS", "PUERTO ASIS", "PUERTO BERRIO",
    "PUERTO TEJADA", "PUERTO NARE", "PUERTO TRIUNFO", "PUERTO WILCHES",
    "EL CARMEN DE VIBORAL", "SUPIA",
}
