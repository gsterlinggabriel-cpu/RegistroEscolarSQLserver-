"""Conexión a SQL Server. Aquí no hay SQL de negocio: ese vive en consultas.py."""
from contextlib import contextmanager

import pyodbc

import config

# Se reexporta para que app.py pueda capturar errores de base de datos sin importar pyodbc.
ErrorBD = pyodbc.Error


@contextmanager
def transaccion():
    """Entrega un cursor dentro de una transacción.

    Si el bloque termina bien se confirma (commit); si lanza un error se deshace
    todo (rollback). Úselo cuando varias instrucciones deben guardarse juntas.
    pyodbc reutiliza conexiones (pooling), por eso abrir una por operación es barato.
    """
    conexion = pyodbc.connect(config.cadena_conexion())
    try:
        yield conexion.cursor()
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def consultar(sql, parametros=()):
    """Ejecuta un SELECT y devuelve una lista de diccionarios {columna: valor}."""
    with transaccion() as cursor:
        cursor.execute(sql, parametros)
        columnas = [columna[0] for columna in cursor.description]
        return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
