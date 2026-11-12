"""Rutas de la aplicación.

Flujo de cada formulario:  HTML (templates/) -> ruta de este archivo -> función de consultas.py -> SQL Server.
Este archivo solo lee y valida lo que llega del formulario; el SQL no va aquí.
"""
from datetime import date
from pathlib import Path

from flask import Flask, abort, flash, redirect, render_template, request, url_for

import config
import consultas
from db import ErrorBD

# Las plantillas van en templates/. Si esa carpeta no existe se buscan junto a app.py,
# para que el proyecto funcione aunque los archivos se hayan copiado sin subcarpetas.
RAIZ = Path(__file__).parent
CARPETA_PLANTILLAS = RAIZ / "templates" if (RAIZ / "templates").is_dir() else RAIZ

app = Flask(__name__, template_folder=str(CARPETA_PLANTILLAS))
app.secret_key = config.CLAVE_SECRETA

# Secciones del panel. Deben coincidir con los id de <section> en templates/panel.html.
PESTANAS = {"inicio", "estudiantes", "asistencia", "calificaciones",
            "expedientes", "reportes", "alertas", "usuarios", "configuracion"}


def _fecha_o_hoy(texto):
    """Convierte 'AAAA-MM-DD' en date; si falta o es inválida usa la fecha de hoy."""
    try:
        return date.fromisoformat(texto)
    except (TypeError, ValueError):
        return date.today()


# --- Inicio de sesión (provisional) ---------------------------------------------

@app.get("/")
@app.get("/login")
def login():
    # Por ahora no valida nada: el botón del formulario solo redirige a /panel.
    # Para activarlo: agregar una ruta POST que compare contra dbo.usuarios
    # (guardando la contraseña con hash) y proteger /panel con una sesión.
    return render_template("login.html")


# --- Panel principal --------------------------------------------------------------

@app.get("/panel")
def panel():
    tab = request.args.get("tab", "inicio")
    if tab not in PESTANAS:
        tab = "inicio"
    curso = request.args.get("curso", "")
    fecha = _fecha_o_hoy(request.args.get("fecha"))
    ano = config.ano_escolar_actual()

    contexto = {
        "tab": tab, "curso": curso, "fecha": fecha.isoformat(), "ano_escolar": ano,
        "cursos": config.CURSOS, "nota_aprobacion": config.NOTA_APROBACION,
        "stats": {"estudiantes": 0, "asistencia": 0, "promedio": 0, "alertas": 0},
        "materias": [], "periodos": [], "materia_id": None, "periodo_id": None,
        "lista_asistencia": [], "lista_notas": [],
    }

    try:
        # Las cifras se cargan siempre porque el menú lateral muestra el contador de alertas.
        fila = consultas.estadisticas(ano)
        contexto["stats"] = {
            "estudiantes": fila["estudiantes"],
            "asistencia": round(float(fila["asistencia"] or 0), 1),
            "promedio": round(float(fila["promedio"] or 0), 1),
            "alertas": fila["alertas"],
        }

        # Cada lista se consulta solo cuando su pestaña está activa y ya hay un curso elegido.
        if tab == "asistencia" and curso:
            contexto["lista_asistencia"] = consultas.listar_asistencia(curso, fecha, ano)

        if tab == "calificaciones":
            materias = consultas.listar_materias()
            periodos = consultas.listar_periodos()
            # Si el usuario aún no eligió, se usa la primera opción de cada lista.
            materia_id = request.args.get("materia_id", type=int) or (materias[0]["id"] if materias else None)
            periodo_id = request.args.get("periodo_id", type=int) or (periodos[0]["id"] if periodos else None)
            contexto.update(materias=materias, periodos=periodos,
                            materia_id=materia_id, periodo_id=periodo_id)
            if curso and materia_id and periodo_id:
                contexto["lista_notas"] = consultas.listar_notas(curso, materia_id, periodo_id, ano)
    except ErrorBD:
        app.logger.exception("Error al leer la base de datos")
        flash("No se pudo leer la base de datos. Verifique la conexión con SQL Server.", "error")

    return render_template("panel.html", **contexto)


# --- Formulario: Registro de estudiantes ----------------------------------------

@app.post("/estudiantes")
def guardar_estudiante():
    campos = ("nombres", "apellidos", "fecha_nacimiento", "curso", "telefono", "tutor", "direccion")
    datos = {campo: request.form.get(campo, "").strip() for campo in campos}

    # El teléfono es el único campo opcional del formulario.
    faltantes = [c for c in campos if c != "telefono" and not datos[c]]
    if faltantes or datos["curso"] not in config.CURSOS:
        flash("Complete todos los campos obligatorios del estudiante.", "error")
        return redirect(url_for("panel", tab="estudiantes"))

    try:
        consultas.insertar_estudiante(
            datos["nombres"], datos["apellidos"],
            date.fromisoformat(datos["fecha_nacimiento"]),
            datos["curso"], datos["telefono"] or None,
            datos["tutor"], datos["direccion"],
            config.ano_escolar_actual(),
        )
        flash("Estudiante registrado correctamente en el sistema.", "exito")
    except ValueError:
        flash("La fecha de nacimiento no es válida.", "error")
    except ErrorBD:
        app.logger.exception("Error al guardar el estudiante")
        flash("No se pudo guardar el estudiante. Intente de nuevo.", "error")
    return redirect(url_for("panel", tab="estudiantes"))


# --- Formulario: Control de asistencia ------------------------------------------

@app.post("/asistencia")
def guardar_asistencia():
    curso = request.form.get("curso", "")
    fecha = _fecha_o_hoy(request.form.get("fecha"))

    # Cada fila de la tabla envía un campo "estado_<matricula_id>" con el valor elegido.
    registros = []
    for campo, estado in request.form.items():
        if campo.startswith("estado_"):
            if estado not in config.ESTADOS_ASISTENCIA:
                abort(400)
            registros.append((int(campo.removeprefix("estado_")), estado))

    if registros:
        try:
            consultas.guardar_asistencia(fecha, registros)
            flash(f"Asistencia del {fecha:%d/%m/%Y} guardada exitosamente.", "exito")
        except ErrorBD:
            app.logger.exception("Error al guardar la asistencia")
            flash("No se pudo guardar la asistencia. Intente de nuevo.", "error")
    return redirect(url_for("panel", tab="asistencia", curso=curso, fecha=fecha.isoformat()))


# --- Formulario: Gestión de calificaciones ------------------------------------------

@app.post("/calificaciones")
def guardar_calificaciones():
    curso = request.form.get("curso", "")
    materia_id = request.form.get("materia_id", type=int)
    periodo_id = request.form.get("periodo_id", type=int)
    if not materia_id or not periodo_id:
        abort(400)

    # Cada fila envía "nota_<matricula_id>". Las notas en blanco se ignoran (no borran la guardada).
    notas = []
    for campo, valor in request.form.items():
        if campo.startswith("nota_") and valor.strip():
            nota = float(valor)
            if not 0 <= nota <= 100:
                abort(400)
            notas.append((int(campo.removeprefix("nota_")), nota))

    if notas:
        try:
            consultas.guardar_notas(materia_id, periodo_id, notas)
            flash("Calificaciones guardadas en el sistema.", "exito")
        except ErrorBD:
            app.logger.exception("Error al guardar las calificaciones")
            flash("No se pudieron guardar las calificaciones. Intente de nuevo.", "error")
    return redirect(url_for("panel", tab="calificaciones", curso=curso,
                            materia_id=materia_id, periodo_id=periodo_id))


if __name__ == "__main__":
    # debug=True recarga el servidor al editar el código; no usar en un servidor real.
    app.run(debug=True)
