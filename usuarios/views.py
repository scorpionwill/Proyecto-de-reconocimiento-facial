# Importa las librerías necesarias
import cv2  # OpenCV para el procesamiento de imágenes y video
import os  # Para interactuar con el sistema operativo (crear carpetas, etc.)
import time  # Para manejar tiempos de espera
from django.shortcuts import get_object_or_404, render, redirect  # Atajos de Django para vistas
from django.http import HttpResponse  # Para enviar respuestas HTTP simples
from .models import Asistencia, Usuario, Evento  # Importa los modelos de la base de datos
from .forms import EventoForm  # Importa el formulario para crear eventos
import numpy as np  # Librería para operaciones numéricas, usada para el entrenamiento
from datetime import date  # Para trabajar con fechas

# --- Vistas relacionadas con la Interfaz de Usuario y Datos ---

# Vista para la página de inicio
def pagina_inicio(request):
    # Busca en la base de datos el evento más reciente que esté marcado como 'activo'
    evento = Evento.objects.filter(estado=True).order_by('-fecha').first()
    # Obtiene la fecha actual
    hoy = date.today()
    
    # Comprueba si hay un evento activo y si su fecha es la de hoy
    if evento and evento.fecha == hoy:
        mensaje_evento = f"El evento '{evento.nom_evento}' está en curso."
    else:
        mensaje_evento = "No hay ningún evento activo en este momento."
        
    # Imprime el mensaje en la consola (útil para depuración)
    print(f"Mensaje generado: {mensaje_evento}")
    
    # Renderiza (dibuja) la plantilla 'inicio.html' y le pasa el evento y el mensaje
    return render(request, 'inicio.html', {'evento': evento, 'mensaje_evento': mensaje_evento})

# Vista para mostrar una lista de todos los usuarios
def listar_usuarios(request):
    # Obtiene todos los objetos 'Usuario' de la base de datos
    usuarios = Usuario.objects.all()
    # Imprime los usuarios encontrados en la consola
    print(f"Usuarios encontrados: {usuarios}")
    # Renderiza la plantilla 'listar_usuarios.html' y le pasa la lista de usuarios
    return render(request, 'listar_usuarios.html', {'usuarios': usuarios})

# Vista para crear un nuevo usuario
def crear_usuario(request):
    # Si el formulario se ha enviado (método POST)
    if request.method == 'POST':
        # Obtiene los datos enviados en el formulario
        nombre = request.POST.get('nombre')
        rut_numeros = request.POST.get('rut_numeros')
        rut_dv = request.POST.get('rut_dv')
        carrera = request.POST.get('carrera')

        # Valida que todos los campos necesarios hayan sido rellenados
        if not (nombre and rut_numeros and rut_dv and carrera):
            # Si falta algún campo, vuelve a mostrar el formulario con un mensaje de error
            return render(request, 'crear_usuario.html', {'error': 'Todos los campos son obligatorios.'})

        # Une los números del RUT y el dígito verificador
        rut_completo = f"{rut_numeros}-{rut_dv}"

        # Crea un nuevo objeto 'Usuario' con los datos del formulario
        usuario = Usuario(nombre=nombre, rut=rut_completo, carrera=carrera)
        # Guarda el nuevo usuario en la base de datos
        usuario.save()

        # Redirige al usuario a la página de captura de imágenes, pasando el ID del nuevo usuario
        return redirect('capturar_imagenes', usuario_id=usuario.id)

    # Si la petición es GET (el usuario acaba de entrar a la página), muestra el formulario vacío
    return render(request, 'crear_usuario.html')

# Vista para editar un usuario existente
def editar_usuario(request, usuario_id):
    # Obtiene el usuario de la base de datos por su ID. Si no lo encuentra, muestra un error 404.
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    # Si el formulario de edición se ha enviado
    if request.method == 'POST':
        # Actualiza los campos del usuario con los nuevos datos
        usuario.nombre = request.POST.get('nombre')
        usuario.carrera = request.POST.get('carrera')
        # Guarda los cambios en la base de datos
        usuario.save()
        
        # Redirige al usuario a la lista de usuarios
        return redirect('listar_usuarios')
    
    # Si la petición es GET, muestra el formulario de edición con los datos actuales del usuario
    return render(request, 'editar_usuario.html', {'usuario': usuario})

# --- Vistas relacionadas con el Reconocimiento Facial ---

# Vista para capturar las imágenes del rostro de un usuario
def capturar_imagenes(request, usuario_id):
    # Obtiene el usuario por su ID
    usuario = get_object_or_404(Usuario, id=usuario_id)

    # Define la ruta donde se guardarán las imágenes del usuario
    path = f"media/dataset/{usuario.id}_{usuario.nombre}"
    # Crea la carpeta si no existe
    os.makedirs(path, exist_ok=True)

    # Inicia la captura de video desde la cámara web (el 0 indica la cámara por defecto)
    cam = cv2.VideoCapture(0)
    # Carga el clasificador de Haar para detectar rostros frontales
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    count = 0  # Contador para el número de imágenes capturadas
    total_capturas = 100  # Define cuántas imágenes se van a tomar

    # Bucle para capturar imágenes
    while True:
        # Lee un fotograma de la cámara
        ret, frame = cam.read()
        # Si no se pudo leer el fotograma, sale del bucle
        if not ret:
            break

        # Convierte el fotograma a escala de grises (mejora la detección)
        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Detecta rostros en la imagen en escala de grises
        rostros = detector.detectMultiScale(gris, 1.3, 5)

        # Itera sobre cada rostro detectado
        for (x, y, w, h) in rostros:
            # Recorta la región del rostro
            rostro = gris[y:y+h, x:x+w]
            # Define el nombre del archivo para la imagen del rostro
            file_name = f"{path}/rostro_{count}.jpg"
            # Guarda la imagen del rostro en el archivo
            cv2.imwrite(file_name, rostro)

            # Encripta la imagen que se acaba de guardar
            encriptar_imagen(file_name)
            # Incrementa el contador
            count += 1

            # Dibuja un rectángulo verde alrededor del rostro en el fotograma original
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            # Muestra un texto sobre el rostro
            cv2.putText(frame, "Captura realizada", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Calcula el porcentaje de progreso de la captura
        porcentaje = int((count / total_capturas) * 100)
        progreso = f"Progreso: {porcentaje}%"

        # Muestra el texto del progreso en la ventana de la cámara
        cv2.putText(frame, progreso, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Muestra la ventana con el fotograma de la cámara
        cv2.imshow("Captura de Imágenes", frame)

        # Comprueba si se ha presionado la tecla 'q', si se ha alcanzado el total de capturas, o si se ha cerrado la ventana
        if cv2.waitKey(1) & 0xFF == ord('q') or count >= total_capturas or cv2.getWindowProperty("Captura de Imágenes", cv2.WND_PROP_VISIBLE) < 1:
            if cv2.getWindowProperty("Captura de Imágenes", cv2.WND_PROP_VISIBLE) < 1:
                print("Ventana de captura cerrada.")
            break

    # Libera la cámara y cierra todas las ventanas de OpenCV
    cam.release()
    cv2.destroyAllWindows()
    # Redirige a la lista de usuarios
    return redirect('listar_usuarios')

# Vista para entrenar el modelo de reconocimiento facial
def entrenar_modelo(request):
    # Ruta a la carpeta que contiene las imágenes de los usuarios
    data_path = "media/dataset"
    imagenes = []  # Lista para almacenar las imágenes de los rostros
    labels = []    # Lista para almacenar las etiquetas (IDs) de los usuarios

    # Recorre cada carpeta de usuario en el dataset
    for carpeta in os.listdir(data_path):
        # Extrae el ID del usuario del nombre de la carpeta (ej: "1_Nombre")
        label = int(carpeta.split("_")[0])
        # Ruta completa a la carpeta del usuario
        carpeta_path = os.path.join(data_path, carpeta)

        # Recorre cada imagen en la carpeta del usuario
        for file in os.listdir(carpeta_path):
            img_path = os.path.join(carpeta_path, file)
            
            # Desencripta la imagen para poder leerla
            desencriptar_imagen(img_path)
            # Lee la imagen en escala de grises
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            # Vuelve a encriptar la imagen por seguridad
            encriptar_imagen(img_path)
            
            # Añade la imagen y su etiqueta a las listas
            imagenes.append(img)
            labels.append(label)

    # Crea una instancia del reconocedor de rostros LBPH
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    # Entrena el reconocedor con las imágenes y sus etiquetas
    recognizer.train(imagenes, np.array(labels))
    # Guarda el modelo entrenado en un archivo .yml
    recognizer.save("media/modelo_lbph.yml")

    # Crea una respuesta HTML para informar al usuario que el entrenamiento fue exitoso
    response = HttpResponse("""
        <html>
            <head>
                <meta http-equiv="refresh" content="3;url='/'">
            </head>
            <body>
                <h2>Modelo entrenado y guardado con éxito.</h2>
                <p>Redirigiendo a la página de inicio...</p>
            </body>
        </html>
    """)
    
    return response

# Vista para reconocer usuarios y registrar su asistencia
def reconocer_usuario(request, evento_id=None):
    # Crea una instancia del reconocedor y carga el modelo entrenado
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("media/modelo_lbph.yml")

    # Carga el clasificador para detectar rostros
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    # Inicia la captura de video
    cam = cv2.VideoCapture(0)

    # Si se proporciona un ID de evento en la URL
    if evento_id:
        # Intenta obtener el evento de la base de datos
        try:
            evento = Evento.objects.get(id=evento_id)
        except Evento.DoesNotExist:
            return HttpResponse("Evento no encontrado", status=404)
        
        # Comprueba si el evento está activo
        if not evento.estado:
            return HttpResponse(f"El evento '{evento.nom_evento}' no está activo", status=400)
    else:
        # Si no se proporciona un ID, busca el evento activo más reciente
        evento = Evento.objects.filter(estado=True).order_by('-fecha').first()

        # Si no hay ningún evento activo
        if not evento:
            return HttpResponse("No hay eventos activos disponibles", status=400)

    last_recognized_id = None  # Almacena el ID del último rostro reconocido
    recognition_start_time = None  # Almacena el tiempo en que se empezó a reconocer un rostro
    CONFIRMATION_TIME = 2  # Segundos necesarios para confirmar un rostro antes de registrar la asistencia

    # Bucle para el reconocimiento
    while True:
        # Lee un fotograma de la cámara
        ret, frame = cam.read()
        if not ret:
            break

        # Convierte a escala de grises y detecta rostros
        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rostros = detector.detectMultiScale(gris, 1.3, 5)

        # Si no se detectan rostros, reinicia las variables de confirmación
        if len(rostros) == 0:
            last_recognized_id = None
            recognition_start_time = None

        # Itera sobre los rostros detectados
        for (x, y, w, h) in rostros:
            # Recorta el rostro
            rostro = gris[y:y+h, x:x+w]
            # Intenta predecir a quién pertenece el rostro
            label, confianza = recognizer.predict(rostro)

            # Si la confianza es menor a 40 (un valor bajo indica una alta probabilidad de acierto)
            if confianza < 40:
                # Obtiene el usuario correspondiente al ID predicho
                usuario = Usuario.objects.get(id=label)

                # Comprueba si el usuario ya tiene registrada la asistencia para este evento
                if Asistencia.objects.filter(usuario=usuario, evento_asist_id=evento.id).exists():
                    texto = f"{usuario.nombre} ya registrado"
                    color = (255, 255, 0)  # Amarillo
                    # Reinicia la confirmación
                    last_recognized_id = None
                    recognition_start_time = None
                else:
                    # Si es el mismo rostro que se estaba viendo en el fotograma anterior
                    if last_recognized_id == label:
                        # Calcula cuánto tiempo ha pasado
                        elapsed_time = time.time() - recognition_start_time
                        
                        # Dibuja una barra de progreso para la confirmación visual
                        progress = int((elapsed_time / CONFIRMATION_TIME) * 100)
                        cv2.rectangle(frame, (x, y + h + 5), (x + w, y + h + 15), (200, 200, 200), -1)
                        cv2.rectangle(frame, (x, y + h + 5), (x + int(w * (progress / 100)), y + h + 15), (0, 255, 0), -1)

                        # Si ha pasado el tiempo de confirmación
                        if elapsed_time >= CONFIRMATION_TIME:
                            # Vuelve a comprobar por si acaso y registra la asistencia
                            if not Asistencia.objects.filter(usuario=usuario, evento_asist_id=evento.id).exists():
                                Asistencia.objects.create(usuario=usuario, evento_asist_id=evento.id)
                                texto = f"Usuario {usuario.nombre} registrado"
                                color = (0, 255, 0)  # Verde
                            else:
                                texto = f"{usuario.nombre} ya registrado"
                                color = (255, 255, 0)  # Amarillo
                            
                            # Reinicia la confirmación
                            last_recognized_id = None
                            recognition_start_time = None
                        else:
                            # Si aún no ha pasado el tiempo, muestra un mensaje de confirmando
                            texto = f"Confirmando a {usuario.nombre}..."
                            color = (0, 255, 255)  # Amarillo claro
                    else:
                        # Si es un nuevo rostro, inicia el proceso de confirmación
                        last_recognized_id = label
                        recognition_start_time = time.time()
                        texto = f"Reconociendo a {usuario.nombre}"
                        color = (0, 255, 255)  # Amarillo claro
            else:
                # Si la confianza es alta (desconocido)
                last_recognized_id = None
                recognition_start_time = None
                texto = "Desconocido"
                color = (0, 0, 255)  # Rojo

            # Dibuja el rectángulo y el texto sobre el fotograma
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, texto, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Muestra la ventana de reconocimiento
        cv2.imshow("Reconocimiento Facial - presione 'q' para salir", frame)

        # Sale del bucle si se presiona 'q' o se cierra la ventana
        if cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty("Reconocimiento Facial - presione 'q' para salir", cv2.WND_PROP_VISIBLE) < 1:
            print("Ventana de reconocimiento cerrada.")
            break

    # Libera la cámara y cierra las ventanas
    cam.release()
    cv2.destroyAllWindows()
    # Redirige a la página de inicio
    return redirect('pagina_inicio')

# --- Vistas para la Gestión de Eventos y Asistencias ---

# Vista para listar todos los registros de asistencia
def listar_asistencias(request):
    # Obtiene todas las asistencias y precarga los datos de usuario y evento para optimizar
    asistencias = Asistencia.objects.select_related('usuario', 'evento_asist')
    # Renderiza la plantilla y le pasa la lista de asistencias
    return render(request, 'listar_asistencias.html', {'asistencias': asistencias})

# Vista para listar todos los eventos
def listar_eventos(request):
    # Obtiene todos los eventos, ordenados por fecha
    eventos = Evento.objects.all().order_by('fecha')
    # Renderiza la plantilla y le pasa la lista de eventos
    return render(request, 'listar_eventos.html', {'eventos': eventos})

# Vista para crear un nuevo evento
def crear_evento(request):
    # Si el formulario se ha enviado
    if request.method == 'POST':
        # Crea una instancia del formulario con los datos enviados
        form = EventoForm(request.POST)
        # Si el formulario es válido
        if form.is_valid():
            # Guarda el nuevo evento en la base de datos
            form.save()
            # Redirige a la lista de eventos
            return redirect('listar_eventos')
    else:
        # Si es una petición GET, crea un formulario vacío
        form = EventoForm()

    # Renderiza la plantilla para crear evento y le pasa el formulario
    return render(request, 'crear_evento.html', {'form': form})

# Vista para editar un evento existente
def editar_evento(request, evento_id):
    # Obtiene el evento por su ID
    evento = get_object_or_404(Evento, id=evento_id)

    # Si el formulario de edición se ha enviado
    if request.method == 'POST':
        # Actualiza los campos del evento con los datos del formulario
        evento.nom_evento = request.POST.get('nom_evento')
        evento.fecha = request.POST.get('fecha')
        evento.relator = request.POST.get('relator')
        evento.descripcion = request.POST.get('descripcion')
        # Convierte el valor del checkbox ('True'/'False') a un booleano
        evento.estado = request.POST.get('estado') == 'True'
        # Guarda los cambios
        evento.save()

        # Redirige a la lista de eventos
        return redirect('listar_eventos')

    # Si es una petición GET, muestra el formulario con los datos actuales del evento
    return render(request, 'editar_evento.html', {'evento': evento})

# Vista para cambiar el estado de un evento (activo/inactivo)
def cambiar_estado_evento(request, evento_id):
    # Solo permite la operación si es una petición POST
    if request.method == "POST":
        # Obtiene el evento por su ID
        evento = get_object_or_404(Evento, id=evento_id)
        # Invierte el estado actual (si es True lo pone en False, y viceversa)
        evento.estado = not evento.estado
        # Guarda el cambio
        evento.save()
    # Redirige a la lista de eventos
    return redirect('listar_eventos')

# --- Funciones de Encriptación ---
from cryptography.fernet import Fernet  # Librería para encriptación simétrica

# Genera una clave de encriptación y la guarda en un archivo
def generar_clave():
    # Genera una nueva clave
    clave = Fernet.generate_key()
    # Abre el archivo de la clave en modo de escritura binaria
    with open("media/encryption_key.key", "wb") as key_file:
        # Escribe la clave en el archivo
        key_file.write(clave)

# Carga la clave de encriptación desde el archivo
def cargar_clave():
    # Abre el archivo de la clave en modo de lectura binaria
    with open("media/encryption_key.key", "rb") as key_file:
        # Lee y devuelve la clave
        return key_file.read()

# Encripta un archivo de imagen
def encriptar_imagen(path_imagen):
    # Carga la clave
    clave = cargar_clave()
    # Crea un objeto Fernet con la clave
    fernet = Fernet(clave)
    # Abre la imagen en modo de lectura binaria
    with open(path_imagen, "rb") as file:
        datos = file.read()
    # Encripta los datos de la imagen
    datos_encriptados = fernet.encrypt(datos)
    # Abre la misma imagen en modo de escritura binaria (sobrescribe el original)
    with open(path_imagen, "wb") as file:
        # Escribe los datos encriptados en el archivo
        file.write(datos_encriptados)

# Desencripta un archivo de imagen
def desencriptar_imagen(path_imagen):
    # Carga la clave
    clave = cargar_clave()
    # Crea un objeto Fernet con la clave
    fernet = Fernet(clave)
    # Abre el archivo encriptado en modo de lectura binaria
    with open(path_imagen, "rb") as file:
        datos_encriptados = file.read()
    # Desencripta los datos
    datos_desencriptados = fernet.decrypt(datos_encriptados)
    # Abre el archivo en modo de escritura binaria (sobrescribe el encriptado)
    with open(path_imagen, "wb") as file:
        # Escribe los datos desencriptados
        file.write(datos_desencriptados)