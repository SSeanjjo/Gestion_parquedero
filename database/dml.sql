-- ============================================================
-- GestionParqueadero - DML v2.0
-- Los datos se cargan mediante el modulo Python:
--
--   1. Generar Excel con datos aleatorios:
--      python data/generar_datos.py
--
--   2. Cargar datos desde Excel a la base de datos:
--      python database/dml_loader.py
--
-- El administrador inicial se configura en el archivo .env:
--   ADMIN_CEDULA, ADMIN_NOMBRE, ADMIN_APELLIDO, ADMIN_CORREO,
--   ADMIN_PASS, ADMIN_CODIGO
-- El bootstrap ocurre automaticamente al iniciar la aplicacion.
-- ============================================================

-- Solo se ejecuta si se necesita resetear manualmente las tarifas:
USE gestion_parqueadero;

INSERT IGNORE INTO TipoVehiculo (id_tipo_vehiculo, nombre) VALUES
  (1, 'Carro'),
  (2, 'Moto'),
  (3, 'Camion'),
  (4, 'Bicicleta');

INSERT IGNORE INTO Tarifa (valor_hora, descripcion, id_tipo_vehiculo) VALUES
  (3500.00, 'Tarifa estandar para carros',      1),
  (2000.00, 'Tarifa estandar para motos',       2),
  (6000.00, 'Tarifa estandar para camiones',    3),
  (500.00,  'Tarifa estandar para bicicletas',  4);
