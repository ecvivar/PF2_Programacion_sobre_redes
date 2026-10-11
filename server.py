from flask import Flask, request, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Crea la aplicación Flask que atenderá las peticiones HTTP.
app = Flask(__name__)

# Nombre del archivo SQLite donde se guardan los datos.
DATABASE = "tareas.db"


def conectar_db():
    """Abre una conexión con SQLite y permite acceder a las filas por nombre de columna."""
    # Si la base está ocupada, SQLite puede esperar hasta 10 segundos.
    conexion = sqlite3.connect(DATABASE, timeout=10)

    # Permite acceder a las columnas usando nombres, por ejemplo: fila["usuario"].
    conexion.row_factory = sqlite3.Row

    return conexion


def crear_tablas():
    """Crea las tablas necesarias si todavía no existen."""
    conexion = None

    try:
        conexion = conectar_db()

        # Guarda los usuarios y sus contraseñas protegidas mediante hash.
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                contraseña TEXT NOT NULL
            )
        """)

        # Tabla prevista para almacenar las descripciones de las tareas.
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS tareas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descripcion TEXT NOT NULL
            )
        """)

        # Confirma los cambios realizados en la base de datos.
        conexion.commit()

    except sqlite3.Error:
        # Registra el detalle técnico para facilitar el diagnóstico.
        app.logger.exception("Error al crear las tablas")

        # Propaga el error para evitar iniciar la aplicación con la base sin preparar.
        raise

    finally:
        # Cierra la conexión incluso si se produce una excepción.
        if conexion is not None:
            conexion.close()


def obtener_datos():
    """Obtiene y valida que la petición contenga un objeto JSON válido."""
    # silent=True evita que Flask genere una excepción por JSON mal formado.
    datos = request.get_json(silent=True)

    # Se espera un objeto JSON, por ejemplo: {"usuario": "cristian"}.
    if not isinstance(datos, dict):
        return None, (
            jsonify({"error": "Se debe enviar un JSON válido"}),
            400
        )

    return datos, None


@app.route("/registro", methods=["POST"])
def registro():
    """Registra un usuario nuevo y guarda su contraseña como hash."""
    datos, error = obtener_datos()

    # Si el cuerpo de la petición no es válido, devuelve el error al cliente.
    if error:
        return error

    usuario = datos.get("usuario")
    contraseña = datos.get("contraseña")

    # Comprueba que ambos campos sean textos.
    if not isinstance(usuario, str) or not isinstance(contraseña, str):
        return jsonify({
            "error": "Usuario y contraseña deben ser textos"
        }), 400

    # Elimina espacios al principio y al final del nombre de usuario.
    usuario = usuario.strip()

    # No permite registrar campos vacíos.
    if not usuario or not contraseña:
        return jsonify({
            "error": "Usuario y contraseña son obligatorios"
        }), 400

    # Genera un hash seguro; nunca se almacena la contraseña original.
    contraseña_hash = generate_password_hash(contraseña)
    conexion = None

    try:
        conexion = conectar_db()

        # Los parámetros ? evitan construir la consulta concatenando datos del usuario.
        conexion.execute(
            "INSERT INTO usuarios (usuario, contraseña) VALUES (?, ?)",
            (usuario, contraseña_hash)
        )

        # Confirma el registro en SQLite.
        conexion.commit()

        # HTTP 201 indica que el usuario fue creado correctamente.
        return jsonify({
            "mensaje": "Usuario registrado correctamente"
        }), 201

    except sqlite3.IntegrityError:
        # Revierte los cambios pendientes si se incumple una restricción de la tabla.
        if conexion is not None:
            conexion.rollback()

        # La columna usuario es UNIQUE, por lo que no admite duplicados.
        return jsonify({
            "error": "El usuario ya existe"
        }), 409

    except sqlite3.Error:
        # Revierte la transacción si ocurre otro error de SQLite.
        if conexion is not None:
            conexion.rollback()

        # El detalle queda en los registros del servidor, no en la respuesta pública.
        app.logger.exception("Error al registrar usuario")

        return jsonify({
            "error": "Error interno al registrar el usuario"
        }), 500

    finally:
        # Libera el recurso aunque haya ocurrido un error o se haya devuelto una respuesta.
        if conexion is not None:
            conexion.close()


@app.route("/login", methods=["POST"])
def login():
    """Verifica las credenciales comparando la contraseña con el hash almacenado."""
    datos, error = obtener_datos()

    if error:
        return error

    usuario = datos.get("usuario")
    contraseña = datos.get("contraseña")

    # Valida el tipo de los campos recibidos.
    if not isinstance(usuario, str) or not isinstance(contraseña, str):
        return jsonify({
            "error": "Usuario y contraseña deben ser textos"
        }), 400

    usuario = usuario.strip()

    # Comprueba que los campos no estén vacíos.
    if not usuario or not contraseña:
        return jsonify({
            "error": "Usuario y contraseña son obligatorios"
        }), 400

    conexion = None

    try:
        conexion = conectar_db()

        # Busca el usuario mediante una consulta parametrizada.
        usuario_db = conexion.execute(
            "SELECT * FROM usuarios WHERE usuario = ?",
            (usuario,)
        ).fetchone()

        # Comprueba la contraseña ingresada contra el hash almacenado.
        if usuario_db and check_password_hash(
            usuario_db["contraseña"],
            contraseña
        ):
            return jsonify({
                "mensaje": "Inicio de sesión exitoso"
            }), 200

        # No revela si falló el usuario o la contraseña.
        return jsonify({
            "error": "Usuario o contraseña incorrectos"
        }), 401

    except sqlite3.Error:
        # Registra el detalle técnico si falla una operación de base de datos.
        app.logger.exception("Error al iniciar sesión")

        return jsonify({
            "error": "Error interno al iniciar sesión"
        }), 500

    finally:
        # Cierra la conexión tanto si el login funciona como si falla.
        if conexion is not None:
            conexion.close()


@app.route("/tareas", methods=["GET"])
def tareas():
    """Devuelve la página HTML de bienvenida solicitada por la consigna."""
    # El cliente recibe HTML, no JSON.
    return """
    <!DOCTYPE html>
    <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Gestión de Tareas</title>
        </head>
        <body>
            <h1>Bienvenido al sistema de gestión de tareas</h1>
            <p>Has ingresado correctamente.</p>
        </body>
    </html>
    """, 200, {"Content-Type": "text/html; charset=utf-8"}


@app.errorhandler(404)
def recurso_no_encontrado(error):
    """Devuelve una respuesta JSON cuando la ruta solicitada no existe."""
    return jsonify({
        "error": "El recurso solicitado no existe"
    }), 404


@app.errorhandler(405)
def metodo_no_permitido(error):
    """Informa cuando se utiliza un método HTTP no admitido por la ruta."""
    return jsonify({
        "error": "El método HTTP no está permitido para este recurso"
    }), 405


@app.errorhandler(500)
def error_interno(error):
    """Devuelve un mensaje general ante errores internos no controlados."""
    return jsonify({
        "error": "Se produjo un error interno en el servidor"
    }), 500


if __name__ == "__main__":
    # Prepara las tablas antes de aceptar peticiones.
    crear_tablas()

    # Inicia el servidor local en modo de depuración para el desarrollo.
    app.run(debug=True)