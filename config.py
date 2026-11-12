"""Configuración central del proyecto: lo que cambia entre equipos o años vive aquí."""
import os
from datetime import date

# --- Conexión a SQL Server ---------------------------------------------------
# Cada valor se puede sobrescribir con una variable de entorno, así cada
# compañero usa su propio servidor sin tocar el código.
SERVIDOR = os.getenv("DB_SERVIDOR", "localhost")  # SQL Express suele ser r"localhost\SQLEXPRESS"
BASE_DATOS = os.getenv("DB_NOMBRE", "RegistroEscolar")
DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")  # usar "ODBC Driver 18 for SQL Server" si es el instalado
USUARIO = os.getenv("DB_USUARIO")  # si queda vacío se usa la autenticación de Windows
CLAVE = os.getenv("DB_CLAVE")


def cadena_conexion():
    base = f"DRIVER={{{DRIVER}}};SERVER={SERVIDOR};DATABASE={BASE_DATOS};TrustServerCertificate=yes;"
    if USUARIO:
        return base + f"UID={USUARIO};PWD={CLAVE};"
    return base + "Trusted_Connection=yes;"


# Flask firma con esta clave los mensajes temporales (flash). Cambiarla fuera de desarrollo.
CLAVE_SECRETA = os.getenv("CLAVE_SECRETA", "desarrollo-cambiar-en-produccion")

# --- Datos que usan los formularios -----------------------------------------
# Opciones del campo "Curso / Sección". Se guardan como texto en estudiantes.curso.
CURSOS = [
    "6to Técnico Informática - A",
    "6to Técnico Informática - B",
    "5to Electromecánica - A",
    "4to Gestión Administrativa",
]

# Deben coincidir con el CHECK de la tabla dbo.asistencia en schema.sql.
ESTADOS_ASISTENCIA = ("Presente", "Ausente", "Excusa", "Tardanza")

# Nota mínima para marcar una calificación como "Aprobado" en pantalla.
NOTA_APROBACION = 70


def ano_escolar_actual():
    """Devuelve el año escolar vigente con el formato de matriculas.ano_escolar, ej. '2026-2027'.

    Se asume que el año escolar empieza en agosto; ajustar el mes si la institución usa otro.
    """
    hoy = date.today()
    inicio = hoy.year if hoy.month >= 8 else hoy.year - 1
    return f"{inicio}-{inicio + 1}"
