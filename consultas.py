"""Todo el SQL del proyecto vive en este archivo.

Cada función corresponde a una acción de un formulario. Los valores se envían
siempre como parámetros (?) y nunca pegados dentro del texto SQL: así se evitan
inyecciones SQL y el driver se encarga de convertir fechas y números.
"""
from db import consultar, transaccion

# Código visible de matrícula, ej. 2026-0012 (año de inicio + id con ceros).
# Es una constante fija, no recibe datos del usuario, por eso es seguro insertarla en el SQL.
CODIGO_MATRICULA = "LEFT(m.ano_escolar, 4) + N'-' + RIGHT(N'0000' + CAST(m.id AS NVARCHAR(10)), 4)"


# --- Panel de inicio -----------------------------------------------------------

def estadisticas(ano_escolar):
    """Cifras de las tarjetas del inicio, calculadas solo con el año escolar indicado."""
    return consultar("""
        SELECT
            (SELECT COUNT(*)
             FROM dbo.matriculas
             WHERE ano_escolar = ?) AS estudiantes,

            -- Presente y Tardanza cuentan como asistencia; Ausente y Excusa no.
            (SELECT AVG(CASE WHEN a.estado IN (N'Presente', N'Tardanza') THEN 100.0 ELSE 0 END)
             FROM dbo.asistencia a
             JOIN dbo.matriculas m ON m.id = a.matricula_id
             WHERE m.ano_escolar = ?) AS asistencia,

            (SELECT AVG(c.nota)
             FROM dbo.calificaciones c
             JOIN dbo.matriculas m ON m.id = c.matricula_id
             WHERE m.ano_escolar = ?) AS promedio,

            (SELECT COUNT(*)
             FROM dbo.alertas al
             JOIN dbo.matriculas m ON m.id = al.matricula_id
             WHERE m.ano_escolar = ?) AS alertas
    """, (ano_escolar,) * 4)[0]


# --- Formulario: Registro de estudiantes ----------------------------------------

def insertar_estudiante(nombres, apellidos, fecha_nacimiento, curso, telefono, tutor, direccion, ano_escolar):
    """Guarda al estudiante y lo matricula en el año escolar indicado.

    Las dos inserciones van en una sola transacción: si la matrícula falla,
    el estudiante tampoco queda guardado.
    """
    with transaccion() as cursor:
        cursor.execute("""
            INSERT INTO dbo.estudiantes (nombres, apellidos, fecha_nacimiento, curso, telefono, tutor, direccion)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nombres, apellidos, fecha_nacimiento, curso, telefono, tutor, direccion))
        estudiante_id = cursor.fetchone()[0]

        cursor.execute(
            "INSERT INTO dbo.matriculas (estudiante_id, ano_escolar) VALUES (?, ?)",
            (estudiante_id, ano_escolar),
        )


# --- Formulario: Control de asistencia ------------------------------------------

def listar_asistencia(curso, fecha, ano_escolar):
    """Estudiantes matriculados en el curso, con el estado ya guardado para esa fecha (si existe)."""
    return consultar(f"""
        SELECT m.id AS matricula_id,
               {CODIGO_MATRICULA} AS codigo,
               e.nombres + N' ' + e.apellidos AS estudiante,
               a.estado
        FROM dbo.matriculas m
        JOIN dbo.estudiantes e ON e.id = m.estudiante_id
        LEFT JOIN dbo.asistencia a ON a.matricula_id = m.id AND a.fecha = ?
        WHERE e.curso = ? AND m.ano_escolar = ?
        ORDER BY e.apellidos, e.nombres
    """, (fecha, curso, ano_escolar))


def guardar_asistencia(fecha, registros):
    """Guarda la lista del día. `registros` es una lista de (matricula_id, estado).

    Si ya existía asistencia para esa matrícula y fecha se actualiza; si no, se inserta.
    Así se puede volver a pasar lista el mismo día sin duplicar filas.
    """
    # SET NOCOUNT ON evita resultados intermedios que impedirían ejecutar el INSERT del lote.
    sql = """
        SET NOCOUNT ON;
        UPDATE dbo.asistencia SET estado = ? WHERE matricula_id = ? AND fecha = ?;
        IF @@ROWCOUNT = 0
            INSERT INTO dbo.asistencia (matricula_id, fecha, estado) VALUES (?, ?, ?);
    """
    parametros = [(estado, mid, fecha, mid, fecha, estado) for mid, estado in registros]
    with transaccion() as cursor:
        cursor.executemany(sql, parametros)


# --- Formulario: Gestión de calificaciones ------------------------------------------

def listar_materias():
    return consultar("SELECT id, nombre FROM dbo.materias ORDER BY nombre")


def listar_periodos():
    return consultar("SELECT id, nombre FROM dbo.periodos ORDER BY id")


def listar_notas(curso, materia_id, periodo_id, ano_escolar):
    """Estudiantes del curso con la nota ya guardada para la materia y el período elegidos."""
    return consultar(f"""
        SELECT m.id AS matricula_id,
               {CODIGO_MATRICULA} AS codigo,
               e.nombres + N' ' + e.apellidos AS estudiante,
               c.nota
        FROM dbo.matriculas m
        JOIN dbo.estudiantes e ON e.id = m.estudiante_id
        LEFT JOIN dbo.calificaciones c
               ON c.matricula_id = m.id AND c.materia_id = ? AND c.periodo_id = ?
        WHERE e.curso = ? AND m.ano_escolar = ?
        ORDER BY e.apellidos, e.nombres
    """, (materia_id, periodo_id, curso, ano_escolar))


def guardar_notas(materia_id, periodo_id, notas):
    """Guarda las notas. `notas` es una lista de (matricula_id, nota).

    Misma lógica que la asistencia: actualiza si ya existe la nota de esa
    matrícula, materia y período; si no, la inserta.
    """
    sql = """
        SET NOCOUNT ON;
        UPDATE dbo.calificaciones SET nota = ?
        WHERE matricula_id = ? AND materia_id = ? AND periodo_id = ?;
        IF @@ROWCOUNT = 0
            INSERT INTO dbo.calificaciones (matricula_id, materia_id, periodo_id, nota)
            VALUES (?, ?, ?, ?);
    """
    parametros = [
        (nota, mid, materia_id, periodo_id, mid, materia_id, periodo_id, nota)
        for mid, nota in notas
    ]
    with transaccion() as cursor:
        cursor.executemany(sql, parametros)
