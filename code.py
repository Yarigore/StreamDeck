import re
import time
import digitalio
import board
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

boton1_pin= board.GP16
boton2_pin= board.GP17
boton3_pin= board.GP18
boton4_pin= board.GP19
boton_atras= board.GP20


teclado = Keyboard(usb_hid.devices)

boton1 = digitalio.DigitalInOut(boton1_pin)
boton1.direction = digitalio.Direction.INPUT
boton1.pull = digitalio.Pull.DOWN

boton2 = digitalio.DigitalInOut(boton2_pin)
boton2.direction = digitalio.Direction.INPUT
boton2.pull = digitalio.Pull.DOWN

boton3 = digitalio.DigitalInOut(boton3_pin)
boton3.direction = digitalio.Direction.INPUT
boton3.pull = digitalio.Pull.DOWN

boton4 = digitalio.DigitalInOut(boton4_pin)
boton4.direction = digitalio.Direction.INPUT
boton4.pull = digitalio.Pull.DOWN

botonAtras = digitalio.DigitalInOut(boton_atras)
botonAtras.direction = digitalio.Direction.INPUT
botonAtras.pull = digitalio.Pull.DOWN

# Mapeo de códigos clave
keycode_mapping = {
    'A': Keycode.A, 'B': Keycode.B, 'C': Keycode.C, 'D': Keycode.D, 'E': Keycode.E,
    'F': Keycode.F, 'G': Keycode.G, 'H': Keycode.H, 'I': Keycode.I, 'J': Keycode.J,
    'K': Keycode.K, 'L': Keycode.L, 'M': Keycode.M, 'N': Keycode.N, 'O': Keycode.O,
    'P': Keycode.P, 'Q': Keycode.Q, 'R': Keycode.R, 'S': Keycode.S, 'T': Keycode.T,
    'U': Keycode.U, 'V': Keycode.V, 'W': Keycode.W, 'X': Keycode.X, 'Y': Keycode.Y,
    'Z': Keycode.Z, 'ONE': Keycode.ONE, 'TWO': Keycode.TWO, 'THREE': Keycode.THREE,
    'FOUR': Keycode.FOUR, 'FIVE': Keycode.FIVE, 'SIX': Keycode.SIX, 'SEVEN': Keycode.SEVEN,
    'EIGHT': Keycode.EIGHT, 'NINE': Keycode.NINE, 'ZERO': Keycode.ZERO, 'ENTER': Keycode.ENTER,
    'RETURN': Keycode.RETURN, 'ESCAPE': Keycode.ESCAPE, 'BACKSPACE': Keycode.BACKSPACE,
    'TAB': Keycode.TAB, 'SPACEBAR': Keycode.SPACEBAR, 'SPACE': Keycode.SPACE,
    'CONTROL': Keycode.CONTROL, 'SHIFT': Keycode.SHIFT, 'ALT': Keycode.ALT,
    'OPTION': Keycode.OPTION, 'GUI': Keycode.GUI, 'WINDOWS': Keycode.WINDOWS,
    'COMMAND': Keycode.COMMAND, 'LEFT_CONTROL': Keycode.LEFT_CONTROL, 'RIGHT_CONTROL': Keycode.RIGHT_CONTROL,
    'LEFT_SHIFT': Keycode.LEFT_SHIFT, 'RIGHT_SHIFT': Keycode.RIGHT_SHIFT,
    'LEFT_ALT': Keycode.LEFT_ALT, 'RIGHT_ALT': Keycode.RIGHT_ALT,
    'LEFT_GUI': Keycode.LEFT_GUI, 'RIGHT_GUI': Keycode.RIGHT_GUI
}


def obtener_keycodes(comando):
    keycodes = []
    partes = comando.split(' + ')

    for parte in partes:
        keycode = keycode_mapping.get(parte.upper())
        if keycode:
            keycodes.append(keycode)

    return keycodes


def convertir_texto(texto):
    aplicaciones = []
    aplicacion_actual = None

    for linea in texto.strip().split('\n'):
        linea = linea.rstrip()  # Eliminar espacios en blanco a la derecha

        if not linea:
            continue

        # Detectar un nuevo nombre de aplicación (No está tabulado)
        if not linea.startswith('\t') and not linea.startswith(' '):
            if aplicacion_actual is not None:
                aplicaciones.append(aplicacion_actual)

            aplicacion_actual = {
                'nombre': linea,
                'accion': []
            }

        # Detectar acción y comando (Líneas tabuladas o con espacios al inicio)
        elif linea.startswith('\t') or linea.startswith(' '):
            if '}' in linea:
                accion, comando = linea.split('} ')
                accion = accion.strip().replace('\t', '')
                comando = [com.strip() for com in comando.split(' + ')]  # Separar comandos por '+'

                aplicacion_actual['accion'].append({
                    'nombre': accion,
                    'comando': comando
                })

    # Añadir la última aplicación si existe
    if aplicacion_actual is not None:
        aplicaciones.append(aplicacion_actual)

    return aplicaciones


# Leer el archivo de texto
with open('shortcuts.txt', 'r', encoding='utf-8') as archivo:
    texto = archivo.read()

# Conversión del texto
resultado = convertir_texto(texto)

# Mostrar resultado
#for i, app in enumerate(resultado):
#    print(f"aplicacion[{i}].nombre = {app['nombre']}")
#    for j, accion in enumerate(app['accion']):
#        print(f"aplicacion[{i}].accion[{j}].nombre = {accion['nombre']}")
#        for k, comando in enumerate(accion['comando']):
#            keycodes = obtener_keycodes(comando)
#            print(f"aplicacion[{i}].accion[{j}].comando[{k}] = {comando} -> Keycodes: {keycodes}")
            
            
def aplicaciones():
    for i in range(0, len(resultado), 2):
        fila = ''
        for j in range(2):
            if i + j < len(resultado):  # Comprobar si hay más aplicaciones disponibles
                fila += resultado[i + j]['nombre'] + "  "
        print(fila)

def ejecutar_comando(comando):
    """Ejecuta un comando con el teclado."""
    if isinstance(comando, list):  # Si es una lista, la convertimos a cadena uniendo con '+'
        comando = "+".join(comando)
    
    if isinstance(comando, str):  # Comprobar que ahora es una cadena
        teclas = comando.split('+')
        keycodes = [keycode_mapping[tecla.strip()] for tecla in teclas if tecla.strip() in keycode_mapping]

        if keycodes:
            teclado.press(*keycodes)
            teclado.release_all()  # Suelta todas las teclas presionadas
            print(f"Comando ejecutado: {comando}")
        else:
            print(f"Comando no válido: {comando}")
    else:
        print("El comando no es válido o no se encuentra en el formato esperado.")


def mostrar_acciones(app_index):
    if app_index < len(resultado):
        app = resultado[app_index]
        print(f"\nAcciones para {app['nombre']}:")
        for j, accion in enumerate(app['accion']):
            print(f"{j + 1}. {accion['nombre']}")
            
        return app  # Devolvemos la aplicación seleccionada
    else:
        print("\nAplicación no encontrada.")
        return None

while True:
    aplicaciones()
    app_seleccionada = None
    time.sleep(0.2)
    
    if boton1.value:
        app_seleccionada = mostrar_acciones(0)
    elif boton2.value:
        app_seleccionada = mostrar_acciones(1)
    elif boton3.value:
        app_seleccionada = mostrar_acciones(2)
    elif boton4.value:
        app_seleccionada = mostrar_acciones(3)
        
    if app_seleccionada:
        time.sleep(0.5)
        while True:
            if botonAtras.value:  # Si se presiona el botón de volver atrás
                print("\nVolviendo al menú de aplicaciones...")
                time.sleep(0.5)
                break  # Salimos del bucle y volvemos a mostrar las aplicaciones
            
            for i, accion in enumerate(app_seleccionada['accion']):
                if globals()[f'boton{i+1}'].value:
                    ejecutar_comando(accion['comando'])
                    break
            
            time.sleep(0.4)