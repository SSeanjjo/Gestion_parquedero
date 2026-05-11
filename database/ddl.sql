-- ============================================================
-- GestionParqueadero - DDL
-- Crear la base de datos y todas las tablas en orden correcto
-- ============================================================

CREATE DATABASE IF NOT EXISTS gestion_parqueadero
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE gestion_parqueadero;

-- ------------------------------------------------------------
-- Entidad base: Usuario
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Usuario (
  cedula           VARCHAR(20)  NOT NULL,
  primer_nombre    VARCHAR(50)  NOT NULL,
  segundo_nombre   VARCHAR(50),
  primer_apellido  VARCHAR(50)  NOT NULL,
  segundo_apellido VARCHAR(50),
  correo           VARCHAR(100) NOT NULL,
  PRIMARY KEY (cedula)
);

-- Atributo multivaluado de Usuario
CREATE TABLE IF NOT EXISTS Telefono (
  cedula_usuario VARCHAR(20) NOT NULL,
  telefono       VARCHAR(20) NOT NULL,
  PRIMARY KEY (cedula_usuario, telefono),
  FOREIGN KEY (cedula_usuario) REFERENCES Usuario(cedula) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- Especializaciones de Usuario (disjuntas)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Administrador (
  cedula           VARCHAR(20)  NOT NULL,
  contrasena       VARCHAR(255) NOT NULL,
  nivel_acceso     VARCHAR(50)  NOT NULL,
  fecha_asignacion DATE         NOT NULL,
  area_responsable VARCHAR(100) NOT NULL,
  PRIMARY KEY (cedula),
  FOREIGN KEY (cedula) REFERENCES Usuario(cedula) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Operador (
  cedula              VARCHAR(20) NOT NULL,
  fecha_inicio_turno  DATETIME,
  fecha_final_turno   DATETIME,
  codigo_interno      VARCHAR(50),
  turno_asignado      VARCHAR(50),
  estado              VARCHAR(20),
  PRIMARY KEY (cedula),
  FOREIGN KEY (cedula) REFERENCES Usuario(cedula) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Suscriptor (
  cedula           VARCHAR(20) NOT NULL,
  tipo_suscriptor  VARCHAR(50),
  fecha_registro   DATE,
  PRIMARY KEY (cedula),
  FOREIGN KEY (cedula) REFERENCES Usuario(cedula) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- Tipo de vehículo
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS TipoVehiculo (
  id_tipo_vehiculo INT          NOT NULL AUTO_INCREMENT,
  nombre           VARCHAR(50)  NOT NULL,
  PRIMARY KEY (id_tipo_vehiculo)
);

-- ------------------------------------------------------------
-- Vehículo
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Vehiculo (
  id_vehiculo      INT         NOT NULL AUTO_INCREMENT,
  placa            VARCHAR(20) NOT NULL,
  color            VARCHAR(30),
  marca            VARCHAR(50),
  modelo           VARCHAR(50),
  cedula_usuario   VARCHAR(20) NOT NULL,
  id_tipo_vehiculo INT         NOT NULL,
  PRIMARY KEY (id_vehiculo),
  FOREIGN KEY (cedula_usuario)   REFERENCES Usuario(cedula)         ON DELETE CASCADE,
  FOREIGN KEY (id_tipo_vehiculo) REFERENCES TipoVehiculo(id_tipo_vehiculo)
);

-- ------------------------------------------------------------
-- Empresa (convenio para suscripciones)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Empresa (
  id_empresa INT          NOT NULL AUTO_INCREMENT,
  nombre     VARCHAR(100) NOT NULL,
  nit        VARCHAR(20),
  direccion  VARCHAR(150),
  telefono   VARCHAR(20),
  ciudad     VARCHAR(50),
  PRIMARY KEY (id_empresa)
);

-- ------------------------------------------------------------
-- Suscripcion (un vehículo → una suscripción máximo)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Suscripcion (
  id_suscripcion         INT            NOT NULL AUTO_INCREMENT,
  fecha_inicio           DATE           NOT NULL,
  fecha_final            DATE           NOT NULL,
  estado                 VARCHAR(20)    NOT NULL DEFAULT 'Activa',
  descuento              DECIMAL(5,2)   DEFAULT 0.00,
  horario_permitido_inicio TIME,
  horario_permitido_final  TIME,
  id_vehiculo            INT            NOT NULL,
  id_empresa             INT,
  PRIMARY KEY (id_suscripcion),
  UNIQUE KEY uk_suscripcion_vehiculo (id_vehiculo),
  FOREIGN KEY (id_vehiculo) REFERENCES Vehiculo(id_vehiculo) ON DELETE CASCADE,
  FOREIGN KEY (id_empresa)  REFERENCES Empresa(id_empresa)   ON DELETE SET NULL
);

-- ------------------------------------------------------------
-- Zona y EspacioParqueo
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Zona (
  id_zona   INT         NOT NULL AUTO_INCREMENT,
  nombre    VARCHAR(50) NOT NULL,
  piso      INT         NOT NULL,
  tipo_zona VARCHAR(50),
  capacidad INT,
  PRIMARY KEY (id_zona)
);

CREATE TABLE IF NOT EXISTS EspacioParqueo (
  id_espacio   INT         NOT NULL AUTO_INCREMENT,
  numero       INT         NOT NULL,
  estado       VARCHAR(20) NOT NULL DEFAULT 'Libre',
  tipo_espacio VARCHAR(50),
  id_zona      INT         NOT NULL,
  PRIMARY KEY (id_espacio),
  FOREIGN KEY (id_zona) REFERENCES Zona(id_zona) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- Tarifa por tipo de vehículo (1:1)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Tarifa (
  id_tarifa        INT            NOT NULL AUTO_INCREMENT,
  valor_hora       DECIMAL(10,2)  NOT NULL,
  descripcion      VARCHAR(150),
  id_tipo_vehiculo INT            NOT NULL,
  PRIMARY KEY (id_tarifa),
  UNIQUE KEY uk_tarifa_tipo (id_tipo_vehiculo),
  FOREIGN KEY (id_tipo_vehiculo) REFERENCES TipoVehiculo(id_tipo_vehiculo)
);

-- ------------------------------------------------------------
-- Sesión de parqueo
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS SesionParqueo (
  id_sesion    INT            NOT NULL AUTO_INCREMENT,
  fecha_inicio DATETIME       NOT NULL,
  fecha_fin    DATETIME,
  tiempo       DECIMAL(10,2),
  id_vehiculo  INT            NOT NULL,
  id_espacio   INT            NOT NULL,
  PRIMARY KEY (id_sesion),
  FOREIGN KEY (id_vehiculo) REFERENCES Vehiculo(id_vehiculo),
  FOREIGN KEY (id_espacio)  REFERENCES EspacioParqueo(id_espacio)
);

-- ------------------------------------------------------------
-- Factura (generada al cerrar la sesión)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Factura (
  id_factura   INT            NOT NULL AUTO_INCREMENT,
  fecha_ingreso DATETIME      NOT NULL,
  fecha_salida  DATETIME      NOT NULL,
  tiempo        DECIMAL(10,2) NOT NULL,
  valor_total   DECIMAL(10,2) NOT NULL,
  estado_pago   VARCHAR(20)   NOT NULL DEFAULT 'Pendiente',
  id_sesion     INT           NOT NULL,
  id_tarifa     INT           NOT NULL,
  PRIMARY KEY (id_factura),
  UNIQUE KEY uk_factura_sesion (id_sesion),
  FOREIGN KEY (id_sesion)  REFERENCES SesionParqueo(id_sesion) ON DELETE CASCADE,
  FOREIGN KEY (id_tarifa)  REFERENCES Tarifa(id_tarifa)
);

-- ------------------------------------------------------------
-- Multa (asociada a una sesión)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Multa (
  id_multa  INT            NOT NULL AUTO_INCREMENT,
  fecha     DATE           NOT NULL,
  motivo    VARCHAR(200),
  valor     DECIMAL(10,2)  NOT NULL,
  estado    VARCHAR(20)    NOT NULL DEFAULT 'Pendiente',
  id_sesion INT            NOT NULL,
  PRIMARY KEY (id_multa),
  UNIQUE KEY uk_multa_sesion (id_sesion),
  FOREIGN KEY (id_sesion) REFERENCES SesionParqueo(id_sesion) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- Notificación
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Notificacion (
  id_notificacion   INT         NOT NULL AUTO_INCREMENT,
  fecha             DATE        NOT NULL,
  mensaje           TEXT        NOT NULL,
  tipo_notificacion VARCHAR(50),
  cedula_usuario    VARCHAR(20) NOT NULL,
  PRIMARY KEY (id_notificacion),
  FOREIGN KEY (cedula_usuario) REFERENCES Usuario(cedula) ON DELETE CASCADE
);
