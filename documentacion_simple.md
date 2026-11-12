## Cómo iniciar la aplicación
1.	Verificar que todos los módulos y paquetes estén descargados(flask,pyodbc)
2.	Asegurar que la conexión con SQL server funcione y tener el servidor activo.
3.	Ejecutar app.py para que el servidor web encienda.
4.	Copiar y pegar la ruta en el navegador y entrar.



## Cómo funciona el programa

El sistema conecta los formularios web con la base de datos de forma sencilla: lo que el usuario escribe en pantalla termina guardado en SQL Server, y se mantiene ahí cada vez que se cierra y se vuelve a abrir el programa.

### El recorrido de un dato

1. **El formulario HTML** (`templates/`) recibe la información. Al presionar "Guardar", la envía al servidor.
2. **`app.py`** recibe esos datos, comprueba que estén completos y correctos, y decide qué acción ejecutar.
3. **`consultas.py`** contiene todo el SQL del proyecto. Cada función se encarga de una tarea concreta, como registrar un estudiante o guardar la asistencia.
4. **`db.py`** abre la conexión con SQL Server y confirma los cambios. Si algo falla en el camino, los deshace para que no queden datos a medias.
5. Al terminar, `app.py` vuelve al panel con un mensaje de éxito o de error, y la página muestra la información ya guardada.

### Qué hace cada archivo

| Archivo | Responsabilidad |
|---|---|
| `templates/` | Las pantallas que ve el usuario (inicio de sesión y panel principal). |
| `app.py` | Recibe los formularios, valida y dirige cada petición. |
| `consultas.py` | Las consultas SQL, una función por cada acción. |
| `db.py` | La conexión con la base de datos. |
| `config.py` | Ajustes del proyecto: servidor, lista de cursos y año escolar. |
| `schema.sql` | Crea la base de datos, las tablas y los datos iniciales. |

### Agregar un formulario nuevo

1. En el HTML, crea el formulario con `method="post"` y ponle un `name` a cada campo.
2. En `app.py`, agrega la ruta que reciba esos campos y los valide.
3. En `consultas.py`, escribe la función con el `INSERT` o `UPDATE`, usando parámetros `?` en lugar de pegar los valores en el texto SQL.

> **Una regla útil:** el SQL vive solo en `consultas.py`. Así, quien necesite modificar una consulta sabe exactamente dónde buscarla, sin tocar las pantallas ni las rutas.