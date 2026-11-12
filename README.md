# Registro Escolar

Aplicación web (Flask + SQL Server) donde los formularios HTML guardan sus datos en la base `RegistroEscolar`.

## Estructura

| Archivo | Para qué sirve |
|---|---|
| `schema.sql` | Crea la base, las tablas, las columnas del formulario de estudiantes y los datos iniciales (períodos y materias). Se puede ejecutar varias veces. |
| `config.py` | Conexión, lista de cursos, estados de asistencia, nota de aprobación y año escolar. |
| `db.py` | Abre la conexión y maneja las transacciones. |
| `consultas.py` | **Todo el SQL del proyecto**, una función por acción de formulario. |
| `app.py` | Rutas: reciben el formulario, validan y llaman a `consultas.py`. |
| `templates/` | `login.html` (provisional) y `panel.html` (el sistema). |

## Puesta en marcha

1. Instalar el *ODBC Driver for SQL Server* (17 o 18) y ejecutar `schema.sql` en SSMS.
2. Crear el entorno e instalar dependencias:
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Si el servidor no es `localhost` o no se usa autenticación de Windows, definir las variables de entorno `DB_SERVIDOR`, `DB_NOMBRE`, `DB_DRIVER`, `DB_USUARIO` y `DB_CLAVE` (ver `config.py`).
4. Ejecutar `python app.py` y abrir http://127.0.0.1:5000

## Agregar un formulario nuevo

1. En `panel.html`, usar `<form method="post" action="{{ url_for('mi_ruta') }}">` y un `name` en cada campo.
2. En `app.py`, crear la ruta `@app.post("/ruta")` que lea `request.form`, valide y llame a la función de consultas.
3. En `consultas.py`, escribir la función con el `INSERT`/`UPDATE` usando parámetros `?`.
