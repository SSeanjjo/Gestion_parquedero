# GestionParqueadero

Sistema de administración de parqueadero desarrollado con Python, Flet y MariaDB.

---

## Requisitos

| Herramienta | Versión mínima |
|-------------|---------------|
| Python | 3.11+ |
| MariaDB / MySQL | 10.6+ |
| pip | incluido con Python |

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd gestion_parqueadero
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar credenciales

Copia el archivo de ejemplo y edítalo con tus datos:

```bash
cp .env.example .env
```

Abre `.env` y completa:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_contraseña
```

Los campos `ADMIN_*` definen el administrador inicial. Puedes dejarlos como están o personalizarlos antes de correr el setup.

### 4. Inicializar la base de datos

```bash
python setup_db.py
```

Este comando:
- Elimina la base de datos anterior si existe (evita conflictos de esquema)
- Crea el esquema v2.0 completo
- Carga los datos de prueba desde `data/datos_parqueadero.xlsx`

> Si ya tenías una versión anterior del proyecto, **siempre corre `setup_db.py` primero** para aplicar el nuevo esquema.

### 5. Iniciar la aplicación

```bash
python main.py
```

---

## Primer inicio de sesión

| Campo | Valor por defecto |
|-------|------------------|
| Cédula | `1000000000` |
| Contraseña | `admin123` |

Estos valores se configuran en el archivo `.env` con las variables `ADMIN_CEDULA` y `ADMIN_PASS`.

---

## Módulos del sistema

### CRUD 1 — Usuarios

Gestión de los tres tipos de usuario del sistema:

- **Administrador** — acceso total, tiene contraseña y código interno
- **Operador** — gestiona turnos y sesiones de parqueo
- **Suscriptor** — usuario con plan de suscripción activa

Operaciones: crear, editar datos personales, eliminar.

Reportes incluidos:
- Multas por estado
- Usuarios con más suscripciones (filtrable por periodo)
- Horas trabajadas por operador
- Usuarios con mayor ganancia generada

---

### CRUD 2 — Vehículos

Registro de vehículos vinculados a propietarios y opcionalmente a una empresa con convenio.

- Búsqueda de propietario por nombre o cédula al crear
- Filtro por estado de suscripción activa
- Muestra si el vehículo tiene suscripción vigente y a qué empresa pertenece

---

### CRUD 3 — Suscripciones

Planes de parqueo vinculados a un vehículo y a un suscriptor.

- Al cerrar una sesión, si el vehículo tiene suscripción activa el valor de la factura es **$0**
- Acción de extender fecha final
- Acción de cancelar (cambia estado a `cancelado`)

Reportes incluidos:
- Suscripciones activas ordenadas por vencimiento próximo
- Suscripciones por empresa con convenio
- Ahorro real vs tarifa por hora

---

### CRUD 4 — Empresas con Convenio

Empresas cuyos vehículos obtienen descuento al pagar sesiones (cuando no tienen suscripción activa).

- Cada empresa tiene un convenio con porcentaje de descuento configurable
- Acción de desactivar empresa y convenio (sin eliminar datos)

Reportes incluidos:
- Catálogo de tarifas por tipo de vehículo
- Vehículos vinculados a empresas con convenio activo

---

### CRUD 5 — Sesiones de Parqueo

Control de entrada y salida de vehículos.

**Regla de compatibilidad de espacios:**
- Vehículos tipo **Moto** → solo espacios tipo `Motos`
- Cualquier otro tipo → espacios que no sean `Motos`

**Lógica de facturación al cerrar sesión (prioridad):**

| Condición | Cobro |
|-----------|-------|
| Suscripción activa en el vehículo | $0 |
| Empresa con convenio activo | Tarifa × (1 − descuento%) |
| Sin ninguna de las anteriores | Tarifa completa por hora |

Reportes incluidos:
- Ocupación de zonas y espacios por periodo
- Ganancias mensuales por sesiones (sin suscripción)

---

## Estructura del proyecto

```
gestion_parqueadero/
├── main.py                  # Punto de entrada
├── setup_db.py              # Inicialización / reset de base de datos
├── .env.example             # Plantilla de configuración
├── requirements.txt
├── config/
│   └── db.py                # Conexión y bootstrap automático
├── database/
│   ├── ddl.sql              # Esquema v2.0
│   ├── dml.sql              # Datos base (TipoVehiculo, Tarifas)
│   └── dml_loader.py        # Cargador de datos desde Excel
├── data/
│   └── datos_parqueadero.xlsx  # Datos de prueba (400 usuarios, 200 vehículos…)
├── models/                  # Acceso a datos (SQL)
├── controllers/             # Lógica de negocio
└── views/                   # Interfaz gráfica (Flet)
```

---

## Datos de prueba incluidos

| Entidad | Cantidad |
|---------|----------|
| Usuarios | 400 (15 admins, 5 operadores, 380 suscriptores) |
| Vehículos | 200 |
| Empresas + Convenios | 10 |
| Suscripciones | 100 |
| Sesiones de parqueo | 400 |
| Facturas | 400 |
| Multas | 40 |
| Notificaciones | 300 |

---

## Tecnologías

- **[Flet](https://flet.dev/)** `0.85` — interfaz gráfica (Material Design 3)
- **MariaDB** — base de datos relacional
- **mariadb** `1.1` — conector Python nativo
- **python-dotenv** — gestión de variables de entorno
- **openpyxl** — lectura del Excel de datos de prueba
