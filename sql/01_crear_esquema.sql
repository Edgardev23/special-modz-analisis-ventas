CREATE DATABASE sm_data_int;
GO 
USE sm_data_int;

CREATE TABLE clientes (
    id_cliente VARCHAR(20) PRIMARY KEY,
    tipo_documento_cliente VARCHAR(2) NOT NULL,
    numero_documento_cliente VARCHAR(20) NOT NULL,
    primer_nombre_cliente VARCHAR(20) NOT NULL, 
    segundo_nombre_cliente VARCHAR(20),
    primer_apellido_cliente VARCHAR(20) NOT NULL,
    segundo_apellido_cliente VARCHAR(20),
    telefono_cliente VARCHAR(20)NOT NULL, 
    ciudad_cliente VARCHAR(50) NOT NULL 
);


CREATE TABLE empleados (
    id_empleado VARCHAR(20) PRIMARY KEY,
    primer_nombre_empleado VARCHAR(20) NOT NULL,
    segundo_nombre_empleado VARCHAR(20),
    primer_apellido_empleado VARCHAR(20) NOT NULL,
    segundo_apellido_empleado VARCHAR(20),
    cargo_empleado VARCHAR(30) NOT NULL,
    fecha_contratacion DATE      
);


CREATE TABLE proveedores (
    id_proveedor VARCHAR(20) PRIMARY KEY,
    nombre_proveedor VARCHAR(20) NOT NULL,
    ciudad_proveedor VARCHAR(20),
    nit VARCHAR(15) NOT NULL 
);


CREATE TABLE productos (
    id_producto VARCHAR(20) PRIMARY KEY,
    nombre_producto VARCHAR(50) NOT NULL,
    categoria_producto VARCHAR(30) NOT NULL, 
    precio_unitario INT NOT NULL
);


CREATE TABLE servicios (
    id_servicio VARCHAR(20) PRIMARY KEY,
    nombre_servicio VARCHAR(30) NOT NULL,
    valor_servicio INT NOT NULL
);


CREATE TABLE compras_proveedores (
    id_compra VARCHAR(20) PRIMARY KEY,
    id_proveedor VARCHAR(20) NOT NULL,
    fecha_compra DATE NOT NULL,
    descripcion_pedido VARCHAR(100) NOT NULL,
    valor_total INT NOT NULL
);


CREATE TABLE ventas (
id_venta VARCHAR(20) PRIMARY KEY,
    id_cliente VARCHAR(20) NOT NULL,
    fecha_venta DATE NOT NULL,
    valor_venta INT NOT NULL,
    id_empleado VARCHAR(20) NOT NULL
);


CREATE TABLE detalle_venta_producto (
    id_detalle_venta VARCHAR(20) PRIMARY KEY,
    id_venta VARCHAR(20) NOT NULL,
    id_producto VARCHAR(20) NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario INT NOT NULL
);


CREATE TABLE detalle_venta_servicio (
    id_detalle_venta VARCHAR(20) PRIMARY KEY,
    id_venta VARCHAR(20) NOT NULL,
    id_servicio VARCHAR(20) NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario INT NOT NULL
);


CREATE TABLE detalle_compra (
    id_detalle_compra VARCHAR(20) PRIMARY KEY,
    id_compra VARCHAR(20) NOT NULL,
    id_producto VARCHAR(20) NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario INT NOT NULL
);



--ventas / clientes
ALTER TABLE ventas
ADD CONSTRAINT fk_ventas_cliente
FOREIGN KEY (id_cliente)
REFERENCES clientes(id_cliente);

--ventas / empleados
ALTER TABLE ventas
ADD CONSTRAINT fk_ventas_empleado
FOREIGN KEY (id_empleado)
REFERENCES empleados(id_empleado);

--ventas / detalle_venta_producto
ALTER TABLE detalle_venta_producto
ADD CONSTRAINT fk_detalle_venta_producto_venta
FOREIGN KEY (id_venta)
REFERENCES ventas(id_venta);

--detalle_venta_producto / productos
ALTER TABLE detalle_venta_producto
ADD CONSTRAINT fk_detalle_venta_producto_producto
FOREIGN KEY (id_producto)
REFERENCES productos(id_producto);

--ventas / detalle_venta_servicio
ALTER TABLE detalle_venta_servicio
ADD CONSTRAINT fk_detalle_venta_servicio_venta
FOREIGN KEY (id_venta)
REFERENCES ventas(id_venta);

--detalle_venta_servicio / servicios
ALTER TABLE detalle_venta_servicio
ADD CONSTRAINT fk_detalle_venta_servicio_servicio
FOREIGN KEY (id_servicio)
REFERENCES servicios(id_servicio);

--compras_proveedores / proveedores
ALTER TABLE compras_proveedores
ADD CONSTRAINT fk_compras_proveedores_proveedor
FOREIGN KEY (id_proveedor)
REFERENCES proveedores(id_proveedor);

--compras_proveedores / detalle_compra
ALTER TABLE detalle_compra
ADD CONSTRAINT fk_detalle_compra_compra
FOREIGN KEY (id_compra)
REFERENCES compras_proveedores(id_compra);

--detalle_compra / productos
ALTER TABLE detalle_compra
ADD CONSTRAINT fk_detalle_compra_producto
FOREIGN KEY (id_producto)
REFERENCES productos(id_producto);


