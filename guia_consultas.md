# Guía de Consultas SQL — Sistema de Gestión de Parqueadero

Esta guía explica, de forma sencilla, las consultas SQL que usa la aplicación.
Está pensada para alguien que está aprendiendo SQL y quiere entender no solo
*qué* hace cada consulta, sino *por qué* está escrita de esa manera.

---

## Conceptos básicos antes de empezar

Antes de leer las consultas, ten claros estos tres conceptos:

- **SELECT**: le dice a la base de datos *qué columnas* quiero ver.
- **FROM**: le dice *de qué tabla* vienen los datos.
- **JOIN**: sirve para *unir dos tablas* usando una columna que tienen en común.
  - `JOIN` (o `INNER JOIN`): solo trae filas que tienen coincidencia en *ambas* tablas.
  - `LEFT JOIN`: trae *todas* las filas de la tabla de la izquierda, aunque no tengan pareja en la derecha (en ese caso pone `NULL`).
- **WHERE**: filtra filas. Es como decir "pero solo las que cumplan esta condición".
- **GROUP BY**: agrupa filas con el mismo valor en una columna, para luego poder contar o sumar.
- **ORDER BY**: ordena el resultado. `ASC` = de menor a mayor, `DESC` = de mayor a menor.

---

## 🟢 Consultas Simples

Son consultas que acceden a **una sola tabla** (o como máximo hacen un JOIN muy
directo) y aplican filtros básicos. No hay agrupaciones ni cálculos elaborados.
Son el punto de partida para aprender SQL.

---

### Consulta 1 — Buscar un usuario por su cédula
**Archivo:** `models/usuario_model.py` → función `get_by_cedula`

```sql
SELECT *
FROM Usuario
WHERE cedula = %s
```

**¿Qué hace?**
Busca y devuelve todos los datos de UN solo usuario cuya cédula coincida
exactamente con el valor que se le pasa.

**Explicación línea por línea:**

| Línea | Significado |
|---|---|
| `SELECT *` | Trae *todas* las columnas de la tabla (cedula, nombre, correo, etc.) |
| `FROM Usuario` | Los datos vienen de la tabla `Usuario` |
| `WHERE cedula = %s` | Filtra: solo el usuario cuya cédula sea igual al valor buscado |

El `%s` es un **parámetro** que Python rellena con el valor real en tiempo
de ejecución (por ejemplo, `'1023456789'`). Esto evita inyecciones SQL.

**¿Por qué es SIMPLE?**
- Una sola tabla.
- Un solo filtro con `=` (comparación directa).
- Sin JOINs, sin cálculos, sin agrupaciones.

---

### Consulta 2 — Listar todas las empresas para un selector
**Archivo:** `models/empresa_model.py` → función `get_all_for_dropdown_all`

```sql
SELECT id_empresa, nombre
FROM Empresa
ORDER BY nombre
```

**¿Qué hace?**
Trae el ID y el nombre de todas las empresas registradas, ordenadas
alfabéticamente. Se usa para llenar listas desplegables en el formulario.

**Explicación línea por línea:**

| Línea | Significado |
|---|---|
| `SELECT id_empresa, nombre` | Solo me interesan el ID y el nombre (no todos los campos) |
| `FROM Empresa` | Los datos vienen de la tabla `Empresa` |
| `ORDER BY nombre` | Ordena el resultado de la A a la Z por nombre |

**¿Por qué es SIMPLE?**
- Una sola tabla.
- Sin filtros `WHERE`.
- Sin JOINs ni cálculos.
- Solo selecciona y ordena.

---

### Consulta 3 — Buscar la suscripción activa de un vehículo
**Archivo:** `models/suscripcion_model.py` → función `get_active_by_vehiculo`

```sql
SELECT *
FROM Suscripcion
WHERE id_vehiculo = %s
  AND estado = 'Activa'
  AND fecha_final >= %s
ORDER BY fecha_final DESC
LIMIT 1
```

**¿Qué hace?**
Busca si un vehículo específico tiene alguna suscripción que esté activa
Y que además no haya vencido todavía. Si hay varias, trae solo la que
vence más tarde.

**Explicación línea por línea:**

| Línea | Significado |
|---|---|
| `WHERE id_vehiculo = %s` | Solo las suscripciones de ese vehículo |
| `AND estado = 'Activa'` | Que además estén marcadas como activas |
| `AND fecha_final >= %s` | Que su fecha de vencimiento sea hoy o en el futuro |
| `ORDER BY fecha_final DESC` | Ordena de la más lejana a la más próxima |
| `LIMIT 1` | De todo ese resultado, solo trae la primera fila |

**¿Por qué es SIMPLE?**
- Una sola tabla.
- Tiene varios filtros, pero todos son comparaciones directas (`=`, `>=`).
- No hay JOINs ni cálculos matemáticos.
- El `LIMIT 1` es una cláusula muy básica.

---

## 🟡 Consultas Intermedias

Estas consultas usan **JOINs entre varias tablas**, funciones de texto como
`CONCAT`, operadores `LIKE` para búsquedas parciales, o funciones de
agrupación (`COUNT`, `SUM`, `AVG`). Requieren entender cómo se relacionan
las tablas entre sí.

---

### Consulta 4 — Buscar usuarios por nombre o cédula (búsqueda parcial)
**Archivo:** `models/usuario_model.py` → función `get_by_cedula_or_name`

```sql
SELECT cedula,
       CONCAT(primer_nombre, ' ', primer_apellido) AS nombre_completo
FROM Usuario
WHERE cedula       LIKE %s
   OR primer_nombre  LIKE %s
   OR primer_apellido LIKE %s
   OR CONCAT(primer_nombre, ' ', primer_apellido) LIKE %s
ORDER BY primer_apellido, primer_nombre
LIMIT 50
```

Python prepara el término como `%termino%` antes de enviarlo.

**¿Qué hace?**
Busca usuarios cuya cédula, nombre o apellido *contenga* el texto que
el usuario escribió en el buscador. Devuelve máximo 50 resultados.

**Conceptos clave:**

- **`CONCAT(a, ' ', b)`**: une varias cadenas de texto en una sola.
  `CONCAT('Juan', ' ', 'Pérez')` → `'Juan Pérez'`.
- **`LIKE %valor%`**: busca filas donde la columna *contenga* ese texto en
  cualquier posición. El `%` es un comodín que significa "cualquier cosa".
  Por ejemplo, `LIKE '%arc%'` encuentra 'Marco', 'Marcela', 'García'.
- **`OR`**: si *cualquiera* de las condiciones se cumple, la fila se incluye.
- **`AS nombre_completo`**: le da un nombre amigable a esa columna en el resultado.
- **`LIMIT 50`**: evita traer miles de filas si hay muchos usuarios.

**¿Por qué es INTERMEDIA?**
- Sigue siendo una sola tabla, pero usa `CONCAT` y `LIKE`.
- Cuatro condiciones unidas con `OR` sobre la misma columna virtual.
- Introduce el concepto de búsqueda por texto parcial, que no es inmediato
  para un principiante.

---

### Consulta 5 — Vehículos sin suscripción activa (patrón anti-join)
**Archivo:** `models/vehiculo_model.py` → función `get_without_subscription`

```sql
SELECT v.id_vehiculo, v.placa
FROM Vehiculo v
LEFT JOIN Suscripcion s ON v.id_vehiculo = s.id_vehiculo
                        AND s.estado = 'Activa'
                        AND s.fecha_final >= CURDATE()
WHERE s.id_vehiculo IS NULL
ORDER BY v.placa
```

**¿Qué hace?**
Devuelve todos los vehículos que **no** tienen una suscripción activa vigente.

**Concepto clave — el patrón anti-join:**

Normalmente un `LEFT JOIN` trae todas las filas de la tabla izquierda
(`Vehiculo`) y llena con `NULL` donde no hay coincidencia en `Suscripcion`.

```
Vehiculo           Suscripcion (activa)
ABC123    ───────►  sub #5  ← tiene pareja
XYZ789    ───────►  NULL    ← no tiene pareja (no hay suscripción activa)
```

Al agregar `WHERE s.id_vehiculo IS NULL` filtramos **solo los que no tienen
pareja**, es decir, los vehículos sin suscripción. Ese truco se llama
**anti-join** y es muy común en SQL.

**¿Por qué es INTERMEDIA?**
- Usa `LEFT JOIN`, que es más difícil de entender que `JOIN`.
- La condición del JOIN está en varias líneas (`AND`).
- El filtro `IS NULL` sobre la tabla unida es un patrón no intuitivo para
  principiantes.
- `CURDATE()` es una función que devuelve la fecha de hoy.

---

### Consulta 6 — Catálogo de tarifas por tipo de vehículo
**Archivo:** `models/empresa_model.py` → función `reporte_catalogo_tarifas`

```sql
SELECT tv.nombre AS tipo_vehiculo,
       t.valor_hora,
       t.descripcion
FROM Tarifa t
JOIN TipoVehiculo tv ON t.id_tipo_vehiculo = tv.id_tipo_vehiculo
ORDER BY t.valor_hora ASC
```

**¿Qué hace?**
Muestra el precio por hora para cada tipo de vehículo (carro, moto, etc.),
ordenado del más barato al más caro.

**Explicación del JOIN:**

La tabla `Tarifa` guarda el precio por hora pero solo tiene el ID del tipo
de vehículo. La tabla `TipoVehiculo` tiene el nombre legible. El `JOIN` une
ambas para mostrar `nombre` en lugar de un número.

```
Tarifa               TipoVehiculo
id_tarifa=1          id_tipo=1 → nombre='Carro'
id_tipo_vehiculo=1 ──►
valor_hora=3000
```

**¿Por qué es INTERMEDIA?**
- Involucra dos tablas unidas con `JOIN`.
- Requiere entender la relación entre llaves foráneas (`id_tipo_vehiculo`).
- Usa alias (`t`, `tv`, `AS tipo_vehiculo`) para hacer el código más legible.

---

### Consulta 7 — Resumen de facturación por tipo de cobro
**Archivo:** `models/factura_model.py` → función `reporte_por_tipo_cobro`

```sql
SELECT tipo_cobro,
       COUNT(*)         AS total_facturas,
       SUM(valor_total) AS total_recaudado,
       AVG(valor_total) AS promedio_valor
FROM Factura
GROUP BY tipo_cobro
ORDER BY total_recaudado DESC
```

**¿Qué hace?**
Agrupa todas las facturas según su tipo de cobro (tarifa completa, suscripción,
convenio) y para cada grupo calcula cuántas hay, cuánto suman y cuánto es el
promedio.

**Funciones de agregación:**

| Función | Qué hace |
|---|---|
| `COUNT(*)` | Cuenta cuántas filas hay en ese grupo |
| `SUM(valor_total)` | Suma todos los valores_total de ese grupo |
| `AVG(valor_total)` | Calcula el promedio del valor_total en ese grupo |

**¿Cómo funciona `GROUP BY`?**

Imagina la tabla `Factura` con estas filas:

```
tipo_cobro          valor_total
Tarifa completa     60
Tarifa completa     120
Suscripcion activa  0
Suscripcion activa  0
```

Con `GROUP BY tipo_cobro` la base de datos "apila" las filas del mismo tipo
y aplica las funciones sobre cada pila:

```
tipo_cobro          total  suma   promedio
Tarifa completa     2      180    90
Suscripcion activa  2      0      0
```

**¿Por qué es INTERMEDIA?**
- Introduce `GROUP BY`, que cambia completamente la lógica de la consulta.
- Usa tres funciones de agregación distintas.
- El `ORDER BY` aplica sobre una columna calculada (`total_recaudado`), no
  sobre una columna real.

---

## 🔴 Consultas Complejas

Estas consultas combinan **múltiples JOINs**, lógica condicional dentro del
`SELECT` (`CASE WHEN`), cálculos entre columnas calculadas, funciones de
fecha avanzadas (`DATEDIFF`, `GREATEST`, `LEAST`), y filtros sobre grupos
(`HAVING`). Se usan para reportes analíticos.

---

### Consulta 8 — Listar usuarios con su rol determinado dinámicamente
**Archivo:** `models/usuario_model.py` → función `get_all`

```sql
SELECT u.cedula, u.primer_nombre, u.segundo_nombre,
       u.primer_apellido, u.segundo_apellido, u.correo,
       CASE
         WHEN a.cedula IS NOT NULL THEN 'Administrador'
         WHEN o.cedula IS NOT NULL THEN 'Operador'
         WHEN s.cedula IS NOT NULL THEN 'Suscriptor'
         ELSE 'Sin rol'
       END AS rol
FROM Usuario u
LEFT JOIN Administrador a ON u.cedula = a.cedula
LEFT JOIN Operador      o ON u.cedula = o.cedula
LEFT JOIN Suscriptor    s ON u.cedula = s.cedula
ORDER BY u.primer_apellido, u.primer_nombre
```

**¿Qué hace?**
Trae todos los usuarios y **deduce su rol** mirando en cuál de las tres
tablas de especialización (Administrador, Operador, Suscriptor) aparece
su cédula.

**¿Por qué se usan `LEFT JOIN` y no `JOIN`?**

En este sistema, un usuario puede no estar en ninguna tabla de especialización
(rol `Sin rol`). Con `JOIN` esos usuarios desaparecerían del resultado porque
no tienen pareja. Con `LEFT JOIN` se mantienen, y en las columnas de
Administrador/Operador/Suscriptor aparece `NULL`.

**¿Cómo funciona `CASE WHEN`?**

Es como un `if / else if / else` en programación:

```
CASE
  WHEN [condición 1] THEN [valor si se cumple]
  WHEN [condición 2] THEN [valor si se cumple]
  ELSE [valor si ninguna se cumple]
END
```

En este caso, si `a.cedula IS NOT NULL` significa que el usuario SÍ aparece
en la tabla `Administrador`, entonces su rol es `'Administrador'`. Se evalúa
en orden: primero verifica admin, luego operador, luego suscriptor.

**¿Por qué es COMPLEJA?**
- Tres `LEFT JOIN` simultáneos a tres tablas diferentes.
- `CASE WHEN` que genera una columna nueva con lógica condicional.
- Requiere entender la arquitectura de herencia de la base de datos (un
  usuario puede tener sub-roles en tablas separadas).

---

### Consulta 9 — Cuánto ahorró cada suscriptor vs pagar por hora
**Archivo:** `models/suscripcion_model.py` → función `reporte_ahorro_suscripcion`

```sql
SELECT s.id_suscripcion,
       v.placa,
       s.fecha_inicio, s.fecha_final, s.estado,
       COUNT(sp.id_sesion)                          AS sesiones_realizadas,
       t.valor_hora,
       COALESCE(SUM(f.valor_total), 0)              AS pagado_con_suscripcion,
       COALESCE(SUM(sp.tiempo), 0) * t.valor_hora   AS habria_pagado_sin_suscripcion,
       (COALESCE(SUM(sp.tiempo), 0) * t.valor_hora)
         - COALESCE(SUM(f.valor_total), 0)          AS ahorro
FROM Suscripcion s
JOIN Vehiculo     v  ON s.id_vehiculo      = v.id_vehiculo
JOIN TipoVehiculo tv ON v.id_tipo_vehiculo = tv.id_tipo_vehiculo
JOIN Tarifa       t  ON t.id_tipo_vehiculo = tv.id_tipo_vehiculo
LEFT JOIN SesionParqueo sp ON sp.id_vehiculo = v.id_vehiculo
                           AND sp.fecha_inicio >= s.fecha_inicio
                           AND (sp.fecha_fin IS NULL OR sp.fecha_fin <= s.fecha_final)
LEFT JOIN Factura f ON f.id_sesion = sp.id_sesion
GROUP BY s.id_suscripcion, v.placa, s.fecha_inicio,
         s.fecha_final, s.estado, t.valor_hora
ORDER BY ahorro DESC
```

**¿Qué hace?**
Para cada suscripción, calcula:
1. Cuántas sesiones de parqueo hizo el vehículo durante el periodo de la suscripción.
2. Cuánto pagó realmente (con el descuento de la suscripción).
3. Cuánto *habría* pagado si no tuviera suscripción.
4. La diferencia = el **ahorro**.

**Conceptos nuevos:**

- **`COALESCE(valor, 0)`**: si `valor` es `NULL`, lo reemplaza con `0`.
  Se usa porque `SUM` de una lista vacía devuelve `NULL`, no `0`.

- **`LEFT JOIN` con condición en el `ON`**: el `LEFT JOIN` a `SesionParqueo`
  tiene dos condiciones extra: que la sesión esté dentro del periodo de la
  suscripción. Esto es más avanzado que un `LEFT JOIN` simple.

- **Columna calculada como base de otra**: `ahorro` se calcula restando
  dos expresiones que son a su vez resultados de `SUM` y multiplicaciones.
  Es una expresión dentro de otra expresión.

- **`GROUP BY` con muchas columnas**: cuando usas funciones de agregación
  (`COUNT`, `SUM`), todas las columnas que **no** son de agregación deben
  aparecer en el `GROUP BY`.

**¿Por qué es COMPLEJA?**
- Encadena 6 tablas (4 `JOIN` + 2 `LEFT JOIN`).
- El `LEFT JOIN` de sesiones incluye filtro de rango de fechas en el `ON`.
- Las columnas calculadas usan `COALESCE` + `SUM` + multiplicación cruzada.
- Mezcla `COUNT` y `SUM` en el mismo `GROUP BY`.

---

### Consulta 10 — Horas trabajadas por operador en un periodo (diurnas y nocturnas)
**Archivo:** `models/usuario_model.py` → función `reporte_horas_operadores`

```sql
SELECT u.cedula,
       CONCAT(u.primer_nombre,' ',u.primer_apellido) AS nombre,
       COUNT(t.id_turno) AS cantidad_turnos,
       SUM(
         DATEDIFF(
           LEAST(t.fecha_final_turno, %s),
           GREATEST(t.fecha_inicio_turno, %s)
         ) + 1
       ) * 8 AS horas_totales_estimadas,
       SUM(CASE
         WHEN TIME(t.fecha_inicio_turno) < '18:00:00'
              OR TIME(t.fecha_final_turno) < '18:00:00'
         THEN DATEDIFF(LEAST(t.fecha_final_turno,%s), GREATEST(t.fecha_inicio_turno,%s))+1
         ELSE 0
       END) * 8 AS horas_diurnas,
       SUM(CASE
         WHEN TIME(t.fecha_inicio_turno) >= '18:00:00'
              OR TIME(t.fecha_final_turno) >= '18:00:00'
         THEN DATEDIFF(LEAST(t.fecha_final_turno,%s), GREATEST(t.fecha_inicio_turno,%s))+1
         ELSE 0
       END) * 8 AS horas_nocturnas
FROM Turno t
JOIN Operador o ON t.id_operador = o.cedula
JOIN Usuario  u ON o.cedula      = u.cedula
WHERE t.fecha_inicio_turno <= %s
  AND t.fecha_final_turno  >= %s
GROUP BY u.cedula, u.primer_nombre, u.primer_apellido
ORDER BY horas_totales_estimadas DESC
```

**¿Qué hace?**
Calcula cuántas horas trabajó cada operador en un rango de fechas dado,
separando las horas en **diurnas** (antes de las 6 PM) y **nocturnas**
(desde las 6 PM en adelante). Asume 8 horas por día de turno.

**Conceptos nuevos:**

- **`DATEDIFF(fecha1, fecha2)`**: calcula la diferencia en días entre dos fechas.
  `DATEDIFF('2025-01-05', '2025-01-01')` → `4`.

- **`GREATEST(a, b)`** y **`LEAST(a, b)`**: devuelven el mayor y el menor de
  dos valores, respectivamente. Se usan para "recortar" un turno que salga
  del rango de fechas solicitado:

  ```
  Turno real:    [01-ene ─────────────────── 31-ene]
  Rango pedido:          [10-ene ─── 20-ene]
  GREATEST(inicio_turno, inicio_rango) → 10-ene  (corta por la izquierda)
  LEAST(fin_turno,       fin_rango)    → 20-ene  (corta por la derecha)
  ```

- **`TIME(datetime)`**: extrae solo la parte de la hora de una fecha-hora.
  `TIME('2025-01-15 20:30:00')` → `'20:30:00'`.

- **`SUM(CASE WHEN ... THEN valor ELSE 0 END)`**: patrón para hacer una
  **suma condicional**. Cuenta solo los días que cumplan la condición (diurno
  o nocturno) y suma 0 para los que no. Es el equivalente SQL de un
  `sum(x if condicion else 0 for x in lista)` en Python.

**¿Por qué es COMPLEJA?**
- Usa funciones anidadas: `SUM` dentro de `CASE WHEN` dentro de `SUM`.
- `DATEDIFF` con `GREATEST`/`LEAST` para manejar turnos que se salen del
  rango solicitado.
- `TIME()` aplicado sobre un campo `DATETIME` para comparar solo la hora.
- El mismo parámetro de fecha se repite múltiples veces (8 veces en total)
  para distintos cálculos.
- Requiere entender conceptos de ventanas de tiempo y solapamiento de rangos.

---

## Resumen de clasificación

| # | Consulta | Archivo | Nivel | Razón principal |
|---|---|---|---|---|
| 1 | Buscar usuario por cédula | `usuario_model.py` | 🟢 Simple | Una tabla, un `WHERE` exacto |
| 2 | Listar empresas para selector | `empresa_model.py` | 🟢 Simple | Una tabla, sin filtros ni cálculos |
| 3 | Suscripción activa de un vehículo | `suscripcion_model.py` | 🟢 Simple | Una tabla, varios `WHERE` + `LIMIT` |
| 4 | Buscar usuario por nombre/cédula | `usuario_model.py` | 🟡 Intermedia | `LIKE`, `CONCAT`, múltiples `OR` |
| 5 | Vehículos sin suscripción activa | `vehiculo_model.py` | 🟡 Intermedia | `LEFT JOIN` + `IS NULL` (anti-join) |
| 6 | Catálogo de tarifas | `empresa_model.py` | 🟡 Intermedia | `JOIN` entre dos tablas relacionadas |
| 7 | Resumen de facturación por tipo | `factura_model.py` | 🟡 Intermedia | `GROUP BY` con `COUNT`, `SUM`, `AVG` |
| 8 | Usuarios con rol dinámico | `usuario_model.py` | 🔴 Compleja | 3 `LEFT JOIN` + `CASE WHEN` por herencia |
| 9 | Ahorro por suscripción | `suscripcion_model.py` | 🔴 Compleja | 6 JOINs, `COALESCE`, cálculos cruzados |
| 10 | Horas diurnas/nocturnas por operador | `usuario_model.py` | 🔴 Compleja | `GREATEST`/`LEAST`, `SUM(CASE WHEN)`, `TIME()` |
