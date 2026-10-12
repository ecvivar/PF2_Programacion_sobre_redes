import requests


# Dirección base de la API desarrollada con Flask.
URL_BASE = "http://127.0.0.1:5000"


def registrar_usuario():
    """Solicita los datos y envía una petición para registrar un usuario."""
    print("\n--- REGISTRO DE USUARIO ---")

    # Solicita el nombre de usuario y la contraseña.
    usuario = input("Usuario: ")
    contraseña = input("Contraseña: ")

    # Organiza los datos en un diccionario para enviarlos como JSON.
    datos = {
        "usuario": usuario,
        "contraseña": contraseña
    }

    try:
        # Envía los datos al endpoint de registro de la API.
        respuesta = requests.post(
            f"{URL_BASE}/registro",
            json=datos,
            timeout=5
        )

        # Muestra el código HTTP y el mensaje devuelto por el servidor.
        print(f"\nCódigo: {respuesta.status_code}")
        print(respuesta.json())

    except requests.exceptions.ConnectionError:
        # Se ejecuta si no es posible establecer conexión con el servidor.
        print("\nError: no se pudo conectar con el servidor.")

    except requests.exceptions.Timeout:
        # Se ejecuta si el servidor tarda demasiado en responder.
        print("\nError: el servidor tardó demasiado en responder.")

    except requests.exceptions.RequestException as error:
        # Captura otros errores relacionados con la petición HTTP.
        print(f"\nError al realizar el registro: {error}")

    except ValueError:
        # Se ejecuta si la respuesta no contiene un JSON válido.
        print("\nError: el servidor devolvió una respuesta no válida.")


def iniciar_sesion():
    """Envía las credenciales y devuelve si el inicio de sesión fue exitoso."""
    print("\n--- INICIO DE SESIÓN ---")

    # Solicita las credenciales del usuario.
    usuario = input("Usuario: ")
    contraseña = input("Contraseña: ")

    # Prepara los datos que se enviarán a la API.
    datos = {
        "usuario": usuario,
        "contraseña": contraseña
    }

    try:
        # Envía las credenciales al endpoint de inicio de sesión.
        respuesta = requests.post(
            f"{URL_BASE}/login",
            json=datos,
            timeout=5
        )

        # Muestra el código HTTP y el mensaje recibido.
        print(f"\nCódigo: {respuesta.status_code}")
        print(respuesta.json())

        # Devuelve True únicamente si el servidor confirma el acceso.
        return respuesta.status_code == 200

    except requests.exceptions.ConnectionError:
        print("\nError: no se pudo conectar con el servidor.")

    except requests.exceptions.Timeout:
        print("\nError: el servidor tardó demasiado en responder.")

    except requests.exceptions.RequestException as error:
        print(f"\nError al realizar el inicio de sesión: {error}")

    except ValueError:
        print("\nError: el servidor devolvió una respuesta no válida.")

    # Si ocurre un error, el inicio de sesión no se considera exitoso.
    return False


def ver_tareas():
    """Realiza una petición GET para acceder a la página de tareas."""
    print("\n--- TAREAS ---")

    try:
        # Solicita al servidor la página HTML del endpoint /tareas.
        respuesta = requests.get(
            f"{URL_BASE}/tareas",
            timeout=5
        )

        # Muestra el código HTTP de la respuesta.
        print(f"\nCódigo: {respuesta.status_code}")

        # Comprueba si la petición fue atendida correctamente.
        if respuesta.status_code == 200:
            # Muestra el contenido HTML que devuelve el servidor.
            print(respuesta.text)
        else:
            # Informa si el servidor devuelve un código de error.
            print(f"Error al acceder a las tareas: {respuesta.text}")

    except requests.exceptions.ConnectionError:
        print("\nError: no se pudo conectar con el servidor.")

    except requests.exceptions.Timeout:
        print("\nError: el servidor tardó demasiado en responder.")

    except requests.exceptions.RequestException as error:
        print(f"\nError al consultar las tareas: {error}")


def menu():
    """Muestra el menú principal y controla las opciones seleccionadas."""
    # Indica si el último intento de inicio de sesión fue exitoso.
    sesion_iniciada = False

    while True:
        print("\n========================================")
        print("       SISTEMA DE GESTIÓN DE TAREAS")
        print("========================================")
        print("1. Registrarse")
        print("2. Iniciar sesión")
        print("3. Ver tareas")
        print("4. Salir")
        print("========================================")

        # Lee la opción elegida por el usuario.
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            # Permite crear una cuenta nueva.
            registrar_usuario()

        elif opcion == "2":
            # Actualiza el estado según el resultado del inicio de sesión.
            sesion_iniciada = iniciar_sesion()

        elif opcion == "3":
            # Solo permite consultar las tareas si el login fue exitoso.
            if sesion_iniciada:
                ver_tareas()
            else:
                print("\nDebe iniciar sesión antes de acceder a las tareas.")

        elif opcion == "4":
            # Finaliza la ejecución del programa.
            print("\nPrograma finalizado.")
            break

        else:
            # Informa si se ingresó una opción que no existe.
            print("\nOpción inválida.")


# Ejecuta el menú únicamente cuando se inicia este archivo directamente.
if __name__ == "__main__":
    menu()