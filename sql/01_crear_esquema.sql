CREATE DATABASE sm_database;
GO 
USE sm_database;

CREATE TABLE clientes (
    fecha_compra DATE,
    nombre_cliente VARCHAR(100),
    ciudad VARCHAR(50),
    valor_compra INT    
)
