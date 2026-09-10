USE sm_database;
GO

-- 3.1 Tabla temporal con las columnas EN EL MISMO ORDEN que el CSV
DROP TABLE IF EXISTS stg_clientes;
GO
CREATE TABLE stg_clientes (
    codigo_cliente  VARCHAR(10)  COLLATE Latin1_General_100_CI_AS_SC_UTF8,
    fecha_compra    DATE,
    nombre_cliente  VARCHAR(100) COLLATE Latin1_General_100_CI_AS_SC_UTF8,
    ciudad          VARCHAR(50)  COLLATE Latin1_General_100_CI_AS_SC_UTF8,
    valor_compra    INT,
    tipo_venta      VARCHAR(20)  COLLATE Latin1_General_100_CI_AS_SC_UTF8
);
GO

-- 3.2 Carga masiva del archivo
BULK INSERT stg_clientes
FROM '/var/opt/mssql/import/clientes_carga.csv'
WITH (
    FIRSTROW        = 2,
    FIELDTERMINATOR = ';',
    ROWTERMINATOR   = '0x0a',
    TABLOCK
);   -- sin CODEPAGE
GO

-- 3.3 Chequeo rápido del staging
SELECT COUNT(*) AS filas_staging FROM stg_clientes;              -- espera 7434
SELECT tipo_venta, COUNT(*) FROM stg_clientes GROUP BY tipo_venta;
GO

-- 3.4 Pasar de staging a la tabla real (lista explícita de columnas => el orden no importa)
INSERT INTO clientes (codigo_cliente, fecha_compra, nombre_cliente, ciudad, valor_compra, tipo_venta)
SELECT codigo_cliente, fecha_compra, nombre_cliente, ciudad, valor_compra, tipo_venta
FROM stg_clientes;
GO

-- 3.5 Limpieza
DROP TABLE stg_clientes;
GO







