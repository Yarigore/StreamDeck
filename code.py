import re
import time
import digitalio
import board
import usb_hid
import busio

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from lcd.lcd import LCD
from lcd.i2c_pcf8574_interface import I2CPCF8574Interface

sda, scl = board.GP14, board.GP15
i2c = busio.I2C(scl, sda)
lcd = LCD(I2CPCF8574Interface(i2c, 0x3F), num_rows=2, num_cols=16)

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
            
            
def aplicaciones():
    for i in range(0, len(resultado), 4):  # Aumentamos el paso a 4 para mostrar de 4 en 4 aplicaciones
        fila_1 = ['    ', '    ', '    ', '    ']  # Espacios iniciales para cada aplicación en fila 1
        fila_2 = ['    ', '    ', '    ', '    ']  # Espacios iniciales para cada aplicación en fila 2

        # Asignamos las aplicaciones a cada "cuadrante" de la pantalla
        for j in range(4):
            if i + j < len(resultado):  # Comprobar si hay más aplicaciones
                app = resultado[i + j]
                nombre_app = app['nombre']
                
                # Convertimos a cadena de texto, por si no lo es
                if isinstance(nombre_app, str):  # Verificamos que sea una cadena
                    nombre_app = str(nombre_app)  # En caso de que no lo sea, forzamos la conversión
                else:
                    nombre_app = str(nombre_app)  # Aseguramos que sea una cadena, incluso si es otro tipo
                
                # Asignamos las aplicaciones a las posiciones correctas en las filas
                if j == 0:
                    fila_1[0] = nombre_app[:7]  # Coloca en la esquina izquierda de la fila 1 (recorta a 7 caracteres)
                elif j == 1:
                    fila_1[1] = nombre_app[:7]  # Coloca en la segunda columna de la fila 1 (recorta a 7 caracteres)
                elif j == 2:
                    fila_2[0] = nombre_app[:7]  # Coloca en la esquina izquierda de la fila 2 (recorta a 7 caracteres)
                elif j == 3:
                    fila_2[1] = nombre_app[:7]  # Coloca en la segunda columna de la fila 2 (recorta a 7 caracteres)

        # Convertir las listas a cadenas y unir los elementos
        fila_1_str = ' '.join(fila_1)  # Unimos los elementos de la fila 1
        fila_2_str = ' '.join(fila_2)  # Unimos los elementos de la fila 2

        # Muestra las filas en el LCD
        lcd.set_cursor_pos(0, 0)
        lcd.print(fila_1_str[:16])  # Solo mostramos los primeros 16 caracteres
        lcd.set_cursor_pos(1, 0)
        lcd.print(fila_2_str[:16])  # Solo mostramos los primeros 16 caracteres
        print(fila_1_str[:16])  # También imprimimos en la consola
        print(fila_2_str[:16])  # También imprimimos en la consola
        time.sleep(0.5)  # Pausa para no actualizar demasiado rápido

        print(fila_1_str)
        print(fila_2_str)


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

        # Inicializamos las filas para las acciones
        fila_1 = ['        ', '        ']  # Espacios para 2 acciones en la primera fila
        fila_2 = ['        ', '        ']  # Espacios para 2 acciones en la segunda fila

        # Asignamos las acciones a las filas
        for j, accion in enumerate(app['accion']):
            nombre_accion = accion['nombre']
            if isinstance(nombre_accion, str):  # Verificamos que sea una cadena
                nombre_accion = str(nombre_accion)

            # Recortamos la acción a un máximo de 8 caracteres
            nombre_accion_cortado = nombre_accion[:8]

            # Colocamos las acciones en las filas
            if j == 0:
                fila_1[0] = nombre_accion_cortado  # Coloca la primera acción en la primera fila
            elif j == 1:
                fila_1[1] = nombre_accion_cortado  # Coloca la segunda acción en la primera fila
            elif j == 2:
                fila_2[0] = nombre_accion_cortado  # Coloca la tercera acción en la segunda fila
            elif j == 3:
                fila_2[1] = nombre_accion_cortado  # Coloca la cuarta acción en la segunda fila

        # Convertimos las filas a cadenas
        fila_1_str = ' '.join(fila_1)
        fila_2_str = ' '.join(fila_2)

        # Mostramos las filas en la pantalla (simulando el LCD aquí)
        lcd.set_cursor_pos(0, 0)
        lcd.print(fila_1_str[:16])  # Solo mostramos los primeros 16 caracteres
        lcd.set_cursor_pos(1, 0)
        lcd.print(fila_2_str[:16])  # Solo mostramos los primeros 16 caracteres
        print(fila_1_str[:16])  # También imprimimos en la consola
        print(fila_2_str[:16])  # También imprimimos en la consola

        time.sleep(0.5)  # Pausa para la siguiente actualización

        return app  # Devolvemos la aplicación seleccionada
    else:
        print("\nAplicación no encontrada.")
        return None

def animacion_volver():
    mensaje1 = "  Volviendo al "
    mensaje2 = "  menu de apps "
    
    # Limpiar el display antes de empezar la animación
    lcd.clear()

    parpadeos = 3  # Número de parpadeos que queremos
    contador_parpadeos = 0  # Contador de parpadeos realizados

    while contador_parpadeos < parpadeos:
        # Primero mostramos el mensaje
        lcd.set_cursor_pos(0, 0)
        lcd.print(mensaje1)  # Mostramos "Volviendo al menú"
        lcd.set_cursor_pos(1, 0)
        lcd.print(mensaje2)  # Mostramos "de aplicaciones..."
        print(mensaje1)  # También lo imprimimos en consola
        print(mensaje2)
        
        time.sleep(0.5)  # Esperamos medio segundo

        # Limpiamos la pantalla para el parpadeo
        lcd.clear()
        time.sleep(0.5)  # Esperamos medio segundo
        
        # Aumentamos el contador de parpadeos
        contador_parpadeos += 1

    print("Volviendo al menú de aplicaciones...")
    
    # Limpiamos la pantalla antes de mostrar el menú
    lcd.clear()


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
                animacion_volver()
                time.sleep(0.5)
                break  # Salimos del bucle y volvemos a mostrar las aplicaciones
            
            for i, accion in enumerate(app_seleccionada['accion']):
                if globals()[f'boton{i+1}'].value:
                    ejecutar_comando(accion['comando'])
                    break
            
            time.sleep(0.4)