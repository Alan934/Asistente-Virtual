import pyttsx3
import speech_recognition as sr
import pywhatkit
import yfinance as yf
import pyjokes
import webbrowser
import datetime
import wikipedia
import psutil
import platform
import wmi
import GPUtil
import os

# Opciones de voz / idioma
id1 = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0"
id2 = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"
id3 = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ES-ES_HELENA_11.0"

# Función para obtener el nombre de usuario del sistema
def obtener_nombre_usuario():
    return os.getlogin()

# Función para mostrar los micrófonos disponibles y seleccionar uno
def seleccionar_microfono():
    mic_list = sr.Microphone.list_microphone_names()
    micrófonos_disponibles = [mic for mic in mic_list if "mic" in mic.lower()]

    if len(micrófonos_disponibles) == 0:
        print("No se encontraron micrófonos disponibles.")
        return None

    print("Micrófonos disponibles:")
    for i, mic in enumerate(micrófonos_disponibles):
        print(f"{i}: {mic}")

    while True:
        try:
            mic_index = int(input("Selecciona el número del micrófono que deseas usar: "))
            if mic_index >= 0 and mic_index < len(micrófonos_disponibles):
                print(f"Has seleccionado el micrófono: {micrófonos_disponibles[mic_index]}")
                return mic_index
            else:
                print("El número seleccionado no es válido. Intenta de nuevo.")
        except ValueError:
            print("Por favor, ingresa un número válido.")

# Escuchar nuestro micrófono y devolver el audio como texto
def transformar_audio_texto(microfono_index):
    r = sr.Recognizer()
    with sr.Microphone(device_index=microfono_index) as origen:
        r.pause_threshold = 0.8
        print("Ya puedes hablar")
        audio = r.listen(origen)

        try:
            pedido = r.recognize_google(audio, language="es-ES")
            print(f"Dijiste: {pedido}")
            return pedido
        except sr.UnknownValueError:
            print("Ups, no entendí")
            return "Sigo esperando"
        except sr.RequestError:
            print("Ups, no hay servicio")
            return "Sigo esperando"
        except Exception as e:
            print("Ups, algo ha salido mal")
            print(e)
            return "Sigo esperando"

# Función para que el asistente pueda ser escuchado
def hablar(mensaje):
    engine = pyttsx3.init()
    engine.setProperty("voice", id3)
    engine.say(mensaje)
    engine.runAndWait()

# Informar el día de la semana
def pedir_dia():
    dia = datetime.datetime.today()
    dia_semana = dia.weekday()
    calendario = {0: "Lunes",
                  1: "Martes",
                  2: "Miércoles",
                  3: "Jueves",
                  4: "Viernes",
                  5: "Sábado",
                  6: "Domingo"}
    hablar(f"Hoy es {calendario[dia_semana]}")

# Informar qué hora es
def pedir_hora():
    hora = datetime.datetime.now()
    hora = f"En este momento son las {hora.hour} horas con {hora.minute} minutos y {hora.second} segundos"
    print(hora)
    hablar(hora)

# Función saludo inicial
def saludo_inicial():
    hora = datetime.datetime.now()
    nombre_usuario = obtener_nombre_usuario()

    if hora.hour < 6 or hora.hour > 20:
        momento = "Buenas noches"
    elif 6 <= hora.hour < 13:
        momento = "Buen día"
    else:
        momento = "Buenas tardes"

    hablar(f"{momento} {nombre_usuario}, en qué te puedo ayudar?")

# Comprobaciones de recursos del sistema
def comprobar_cpu(procesador):
    comprobamos = 60
    if comprobamos >= procesador:
        hablar("El uso de la CPU está en niveles óptimos.")

def comprobar_memoria(memory_info):
    comprobamos = 20
    if comprobamos >= memory_info.percent:
        hablar("Advertencia: La memoria disponible es baja.")

def comprobar_espacio_disco(disk_usage):
    espacio = 15
    if espacio >= disk_usage.percent:
        hablar("El disco tiene poco espacio disponible.")

# Función central del asistente
def centro_pedido():

    # Seleccionar micrófono
    microfono_index = seleccionar_microfono()
    if microfono_index is None:
        hablar("No se pudo seleccionar un micrófono. El programa se cerrará.")
        return

    # Saludo inicial
    saludo_inicial()

    # Variable de corte
    comenzar = True

    while comenzar:
        # Activar el micrófono y guardar el pedido en un String
        pedido = transformar_audio_texto(microfono_index).lower()

        print(f"Comando recibido: {pedido}")

        if "abrir youtube" in pedido:
            hablar("Estoy abriendo YouTube")
            webbrowser.open("https://www.youtube.com")
            continue
        elif "abrir navegador" in pedido or "abrir el navegador" in pedido:
            hablar("Estoy abriendo el navegador")
            webbrowser.open("https://www.google.com.ar")
            continue
        elif "que día es hoy" in pedido or "qué día es hoy" in pedido or "qué día es" in pedido:
            pedir_dia()
            continue
        elif "qué hora es" in pedido or "que hora es" in pedido or "qué hora" in pedido:
            pedir_hora()
            continue
        elif "busca en wikipedia" in pedido:
            hablar("buscando en wikipedia")
            pedido = pedido.replace("busca en wikipedia", "")
            wikipedia.set_lang("es")
            resultado = wikipedia.summary(pedido, sentences=1)
            hablar("Encontre esta informacion en wikipedia")
            hablar(resultado)
            continue
        elif "busca en internet" in pedido:
            hablar("Buscando informacion")
            pedido = pedido.replace("busca en internet", "")
            pywhatkit.search(pedido)
            hablar("Esto es lo que he encontrado")
            continue
        elif "reproducir" in pedido:
            hablar("Reproduciendo")
            pedido = pedido.replace("reproducir", "").strip()
            pywhatkit.playonyt(pedido)
            continue
        elif "chiste" in pedido:
            hablar(pyjokes.get_joke("es"))
            continue
        elif "precio de la acción" in pedido:
            accion = pedido.split("de")[-1].strip().lower()
            cartera = {
                "apple": "AAPL",
                "amazon": "AMZN",
                "google": "GOOGL",
                "tesla": "TSLA"
            }
            try:
                accion_buscada = cartera[accion]
                ticker = yf.Ticker(accion_buscada)
                precio_actual = ticker.info['regularMarketPrice']
                hablar(f"La encontré, el precio de {accion} es {precio_actual} dólares.")
            except KeyError:
                hablar(f"No tengo información sobre la acción de {accion}.")
            except Exception as e:
                hablar("Perdón, pero no pude encontrar la información de la acción.")
                print(e)
            continue
        elif "cpu" in pedido or "detalles de procesador" in pedido:
            c=wmi.WMI()
            for processor in c.Win32_Processor():
                hablar(f"Nombre del procesador: {processor.Name}")
                hablar(f"Fabricante del procesador: {processor.Manufacturer}")
                hablar(f"Número de núcleos físicos: {processor.NumberOfCores} ")
                hablar(f"Número de hilos lógicos: {processor.NumberOfLogicalProcessors}" )
                hablar(f"Frecuencia del procesador: {(processor.MaxClockSpeed / 1000.0)}  GHz")
                hablar(f"Frecuencia del procesador: {(processor.MaxClockSpeed / 1000.0)}  GHz")
        elif "cpu en uso" in pedido or "cuánto del procesador se esta usando" in pedido or "cuanto se esta usando de cpu" in pedido:
            procesador=psutil.cpu_percent(interval=1)
            print(procesador)
            hablar(f"Se esta ocupando {procesador}%")
            comprobar_cpu(procesador)
        elif "tiempo empleado por el usuario" in pedido or "cpu usado por el usuario" in pedido:
            procesador=psutil.cpu_times()
            hablar(f"tiempo usado por el usuario:{procesador.user}")
            print(procesador.user)
        elif "tiempo empleado por el sistema" in pedido or "cpu usado por el sistema" in pedido:
            procesador=psutil.cpu_times()
            hablar(f"tiempo usado por el sistema:{procesador.system}")
            print(procesador.system)
        elif "tiempo empleado por el sistema inactivo" in pedido or "cpu usado por el sistema inactivo" in pedido:
            procesador=psutil.cpu_times()
            hablar(f"tiempo usado por el sistema inactivo:{procesador.idle}")
            print(procesador.idle)
        elif "memoria en uso" in pedido or "cuanta memoria se esta usando" in pedido:
            memory_info = psutil.virtual_memory()
            hablar(f"Uso de memoria: {memory_info.percent}%")
            comprobar_memoria(memory_info)
        elif "memoria total" in pedido:
            memory_info = psutil.virtual_memory()
            print(f"Memoria total: {memory_info.total / (1024 ** 3):.2f} GB")
            hablar(f"Memoria total: {memory_info.total / (1024 ** 3):.2f} GB")
        elif "memoria disponible" in pedido:
            memory_info = psutil.virtual_memory()
            hablar(f"Memoria disponible: {memory_info.available / (1024 ** 3):.2f} GB")
        elif "disco ocupado" in pedido or "cuánto es el disco ocupado" in pedido:
            # Obtener información del uso del disco
            disk_usage = psutil.disk_usage('/')
            hablar(f"Usado: {disk_usage.used / (1024 ** 3):.2f} GB")
            hablar(f"Porcentaje usado: {disk_usage.percent}%")
            comprobar_espaciodisco(disk_usage)
        elif "cuanto es el total del disco" in pedido or "cuánto es el total del disco" in pedido :
            disk_usage = psutil.disk_usage('/')
            hablar(f"Total: {disk_usage.total / (1024 ** 3):.2f} GB")
        elif "cuánto espacio me queda" in pedido or "cuanto disco libre tengo" in pedido:
            disk_usage = psutil.disk_usage('/')
            hablar(f"Libre: {disk_usage.free / (1024 ** 3):.2f} GB")
        elif "cuánto es el tiempo de escritura" in pedido:
            disk_usage=psutil.disk_io_counters()
            hablar(f"Tiempo de escritura:{disk_usage.write_time}")
        elif "cuánto es el tiempo de lectura" in pedido:
            disk_usage=psutil.disk_io_counters()
            hablar(f"Tiempo de lectura:{disk_usage.read_time}")

        elif "detalles del sistema operativo" in pedido:
            hablar(f"Sistema Operativo: {platform.system()}")
            hablar(f"Versión: {platform.version()}")
            hablar(f"Arquitectura: {platform.architecture()}")
        elif "detalles de gpu" in pedido:
            c = wmi.WMI()
            for gpu in c.Win32_VideoController():
                hablar(f"GPU: {gpu.Name}")
                hablar(f"Memoria GPU: {gpu.AdapterRAM / (1024 ** 2):.2f} MB")
        elif "adiós" in pedido:
            hablar(f"Nos vemos, avísame si necesitas otra cosa, {obtener_nombre_usuario()}.")
            break
        else:
            hablar("Lo siento, no puedo ayudar con eso.")

centro_pedido()
