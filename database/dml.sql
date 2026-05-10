-- ============================================================
-- GestionParqueadero - DML  (datos de prueba)
-- Ejecutar después de ddl.sql
-- ============================================================

USE gestion_parqueadero;

-- ------------------------------------------------------------
-- Tipos de vehículo
-- ------------------------------------------------------------
INSERT INTO TipoVehiculo (nombre) VALUES
  ('Carro'),
  ('Moto'),
  ('Camión'),
  ('Bicicleta');

-- ------------------------------------------------------------
-- Tarifas por tipo
-- ------------------------------------------------------------
INSERT INTO Tarifa (valor_hora, descripcion, id_tipo_vehiculo) VALUES
  (3500.00, 'Tarifa estándar para carros',      1),
  (2000.00, 'Tarifa estándar para motos',       2),
  (6000.00, 'Tarifa estándar para camiones',    3),
  (500.00,  'Tarifa estándar para bicicletas',  4);

-- ------------------------------------------------------------
-- Empresas con convenio
-- ------------------------------------------------------------
INSERT INTO Empresa (nombre, nit, direccion, telefono, ciudad) VALUES
  ('TechCorp S.A.S',   '900123456-1', 'Calle 10 #5-20',    '3001234567', 'Bogotá'),
  ('LogiExpress Ltda', '800987654-2', 'Carrera 7 #45-80',  '3107654321', 'Medellín');

-- ------------------------------------------------------------
-- Usuario admin por defecto (DEBE SER EL PRIMERO)
-- ------------------------------------------------------------
INSERT INTO Usuario (cedula, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, correo, contrasena)
VALUES ('1000000000', 'Admin', NULL, 'Sistema', NULL, 'admin@parqueadero.com', 'admin123');

INSERT INTO Administrador (cedula, nivel_acceso, fecha_asignacion, area_responsable)
VALUES ('1000000000', 'SUPER', CURDATE(), 'Sistemas');

-- ------------------------------------------------------------
-- Usuarios adicionales de prueba
-- ------------------------------------------------------------
INSERT INTO Usuario (cedula, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, correo, contrasena) VALUES
  ('1001001001', 'Carlos',   'Andrés',  'García',   'Ruiz',     'carlos.garcia@email.com',  'pass123'),
  ('1002002002', 'María',    'Isabel',  'López',    'Vargas',   'maria.lopez@email.com',    'pass123'),
  ('1003003003', 'Juan',     NULL,      'Martínez', 'Peña',     'juan.martinez@email.com',  'pass123'),
  ('1004004004', 'Luisa',    'Fernanda','Rodríguez','Castro',   'luisa.rodriguez@email.com','pass123'),
  ('1005005005', 'Pedro',    NULL,      'Sánchez',  NULL,       'pedro.sanchez@email.com',  'pass123'),
  ('1006006006', 'Ana',      'Milena',  'Torres',   'Mora',     'ana.torres@email.com',     'pass123');

-- Especializaciones
INSERT INTO Operador (cedula, fecha_inicio_turno, fecha_final_turno, codigo_interno, turno_asignado, estado) VALUES
  ('1001001001', '2025-01-01 06:00:00', '2025-12-31 14:00:00', 'OP-001', 'Mañana',  'Activo'),
  ('1002002002', '2025-01-01 14:00:00', '2025-12-31 22:00:00', 'OP-002', 'Tarde',   'Activo');

INSERT INTO Administrador (cedula, nivel_acceso, fecha_asignacion, area_responsable) VALUES
  ('1003003003', 'MEDIO', '2024-03-15', 'Operaciones');

INSERT INTO Suscriptor (cedula, tipo_suscriptor, fecha_registro) VALUES
  ('1004004004', 'Premium',  '2024-06-01'),
  ('1005005005', 'Estándar', '2024-09-10'),
  ('1006006006', 'Premium',  '2025-01-15');

-- Teléfonos
INSERT INTO Telefono (cedula_usuario, telefono) VALUES
  ('1000000000', '3100000000'),
  ('1001001001', '3111001001'),
  ('1002002002', '3122002002'),
  ('1004004004', '3144004004'),
  ('1004004004', '3144004405'),
  ('1005005005', '3155005005');

-- ------------------------------------------------------------
-- Vehículos
-- ------------------------------------------------------------
INSERT INTO Vehiculo (placa, color, marca, modelo, cedula_usuario, id_tipo_vehiculo) VALUES
  ('ABC123', 'Rojo',    'Toyota',    'Corolla',   '1004004004', 1),
  ('XYZ789', 'Negro',   'Honda',     'CB500',     '1005005005', 2),
  ('DEF456', 'Blanco',  'Ford',      'F-150',     '1006006006', 3),
  ('GHI321', 'Azul',    'Chevrolet', 'Spark',     '1004004004', 1),
  ('JKL654', 'Gris',    'Yamaha',    'FZ-25',     '1005005005', 2),
  ('MNO987', 'Verde',   NULL,        NULL,        '1006006006', 4);

-- ------------------------------------------------------------
-- Suscripciones
-- ------------------------------------------------------------
INSERT INTO Suscripcion (fecha_inicio, fecha_final, estado, descuento, horario_permitido_inicio, horario_permitido_final, id_vehiculo, id_empresa) VALUES
  ('2025-01-01', '2025-12-31', 'Activa',   15.00, '06:00:00', '22:00:00', 1, 1),
  ('2025-03-01', '2025-08-31', 'Activa',    5.00, '07:00:00', '20:00:00', 2, NULL),
  ('2024-10-01', '2025-03-31', 'Inactiva', 10.00, '08:00:00', '18:00:00', 3, 2);

-- ------------------------------------------------------------
-- Zonas y espacios
-- ------------------------------------------------------------
INSERT INTO Zona (nombre, piso, tipo_zona, capacidad) VALUES
  ('Zona A', 1, 'Cubierta',    20),
  ('Zona B', 1, 'Descubierta', 30),
  ('Zona C', 2, 'Cubierta',    15);

INSERT INTO EspacioParqueo (numero, estado, tipo_espacio, id_zona) VALUES
  (1,  'Libre',  'Estándar',      1),
  (2,  'Libre',  'Estándar',      1),
  (3,  'Ocupado','Estándar',      1),
  (4,  'Libre',  'Discapacitados',1),
  (5,  'Libre',  'Estándar',      2),
  (6,  'Libre',  'Estándar',      2),
  (7,  'Ocupado','Estándar',      2),
  (8,  'Libre',  'Motos',         2),
  (9,  'Libre',  'Estándar',      3),
  (10, 'Libre',  'VIP',           3);

-- ------------------------------------------------------------
-- Sesiones de parqueo (algunas cerradas, una activa)
-- ------------------------------------------------------------
INSERT INTO SesionParqueo (fecha_inicio, fecha_fin, tiempo, id_vehiculo, id_espacio) VALUES
  ('2025-04-10 08:00:00', '2025-04-10 10:00:00', 2.00, 1, 3),
  ('2025-04-11 09:30:00', '2025-04-11 12:00:00', 2.50, 2, 7),
  ('2025-04-12 07:00:00', '2025-04-12 09:00:00', 2.00, 3, 5),
  ('2025-05-01 14:00:00', NULL,                  NULL, 4, 6);

-- ------------------------------------------------------------
-- Facturas (sesiones cerradas)
-- ------------------------------------------------------------
INSERT INTO Factura (fecha_ingreso, fecha_salida, tiempo, valor_total, estado_pago, id_sesion, id_tarifa) VALUES
  ('2025-04-10 08:00:00', '2025-04-10 10:00:00', 2.00,  7000.00, 'Pagado',   1, 1),
  ('2025-04-11 09:30:00', '2025-04-11 12:00:00', 2.50,  5000.00, 'Pagado',   2, 2),
  ('2025-04-12 07:00:00', '2025-04-12 09:00:00', 2.00, 12000.00, 'Pendiente',3, 3);

-- ------------------------------------------------------------
-- Multas
-- ------------------------------------------------------------
INSERT INTO Multa (fecha, motivo, valor, estado, id_sesion) VALUES
  ('2025-04-11', 'Vehículo en espacio no asignado',   50000.00, 'Pagada',   2),
  ('2025-04-12', 'Tiempo excedido en zona de carga', 100000.00, 'Pendiente',3);

-- ------------------------------------------------------------
-- Notificaciones
-- ------------------------------------------------------------
INSERT INTO Notificacion (fecha, mensaje, tipo_notificacion, cedula_usuario) VALUES
  ('2025-04-10', 'Su suscripción vence en 30 días.',         'Alerta',       '1004004004'),
  ('2025-04-11', 'Multa registrada en sesión del 11/04.',    'Multa',        '1005005005'),
  ('2025-04-12', 'Pago pendiente en factura #3.',            'Recordatorio', '1006006006'),
  ('2025-05-01', 'Vehículo GHI321 ingresó al parqueadero.', 'Información',  '1004004004');
