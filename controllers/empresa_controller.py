from config.db import get_connection
from models import empresa_model, convenio_model


def get_all():
    try:
        conn = get_connection()
        data = empresa_model.get_all(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def create(data):
    try:
        conn = get_connection()
        new_id = empresa_model.create(conn, data)
        if data.get('porcentaje_descuento') is not None:
            convenio_model.create(conn, new_id,
                                  data.get('porcentaje_descuento', 0),
                                  data.get('estado_convenio_conv', 'activo'))
        conn.close()
        return True, "Empresa registrada exitosamente."
    except Exception as e:
        return False, str(e)


def update(id_empresa, data):
    try:
        conn = get_connection()
        empresa_model.update(conn, id_empresa, data)
        convenio_model.upsert(conn, id_empresa,
                              data.get('porcentaje_descuento', 0),
                              data.get('estado_convenio_conv', 'activo'))
        conn.close()
        return True, "Empresa actualizada exitosamente."
    except Exception as e:
        return False, str(e)


def deactivate(id_empresa):
    try:
        conn = get_connection()
        empresa_model.deactivate(conn, id_empresa)
        convenio_model.update(conn, id_empresa, 0, 'inactivo')
        conn.close()
        return True, "Empresa desactivada exitosamente."
    except Exception as e:
        return False, str(e)


# Reportes
def reporte_catalogo_tarifas():
    try:
        conn = get_connection()
        data = empresa_model.reporte_catalogo_tarifas(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def reporte_vehiculos_por_empresa():
    try:
        conn = get_connection()
        data = empresa_model.reporte_vehiculos_por_empresa(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)
