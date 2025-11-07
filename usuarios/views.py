# views.py
import cv2
import os
import time
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from .models import Asistencia, Usuario, Evento
from .forms import EventoForm
import numpy as np
from datetime import date

def pagina_inicio(request):
    evento = Evento.objects.filter(estado=True).order_by('-fecha').first()  # Obtener el evento activo más reciente
    hoy = date.today()
    
    # Determinar si el evento está en transcurso
    if evento and evento.fecha == hoy:
        mensaje_evento = f"El evento '{evento.nom_evento}' está en curso."
    else:
        mensaje_evento = "No hay ningún evento activo en este momento."
    print(f"Mensaje generado: {mensaje_evento}")
    return render(request, 'inicio.html', {'evento': evento, 'mensaje_evento': mensaje_evento})


def listar_usuarios(request):
    usuarios = Usuario.objects.all()  # Obtener todos los usuarios
    print(f"Usuarios encontrados: {usuarios}")  # Esto imprimirá los usuarios en la consola
    return render(request, 'listar_usuarios.html', {'usuarios': usuarios})


def crear_usuario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        rut_numeros = request.POST.get('rut_numeros')
        rut_dv = request.POST.get('rut_dv')
        carrera = request.POST.get('carrera')

        # Validar que los campos requeridos estén completos
        if not (nombre and rut_numeros and rut_dv and carrera):
            return render(request, 'crear_usuario.html', {'error': 'Todos los campos son obligatorios.'})

        # Concatenar el RUT completo
        rut_completo = f"{rut_numeros}-{rut_dv}"

        # Guardar en el modelo
        usuario = Usuario(nombre=nombre, rut=rut_completo, carrera=carrera)
        usuario.save()

        # Redirigir a la captura de imágenes
        return redirect('capturar_imagenes', usuario_id=usuario.id)

    # Si es GET, renderizar el formulario vacío
    return render(request, 'crear_usuario.html')

from django.shortcuts import render, get_object_or_404, redirect

def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)  # Obtener el usuario por ID
    
    if request.method == 'POST':
        # Actualizar los campos editables
        usuario.nombre = request.POST.get('nombre')
        usuario.carrera = request.POST.get('carrera')
        usuario.save()  # Guardar los cambios en la base de datos
        
        # Redirigir a la lista de usuarios después de guardar
        return redirect('listar_usuarios')
    
    # Renderizar el template con los datos actuales del usuario
    return render(request, 'editar_usuario.html', {'usuario': usuario})


def capturar_imagenes(request, usuario_id):
    # Obtener el usuario por ID
    usuario = get_object_or_404(Usuario, id=usuario_id)

    # Crear carpeta para almacenar imágenes
    path = f"media/dataset/{usuario.id}_{usuario.nombre}"
    os.makedirs(path, exist_ok=True)

    # Configurar cámara y capturar imágenes
    cam = cv2.VideoCapture(0)
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    count = 0
    total_capturas = 100  # Número máximo de capturas

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        # Convertir a escala de grises
        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rostros = detector.detectMultiScale(gris, 1.3, 5)

        for (x, y, w, h) in rostros:
            rostro = gris[y:y+h, x:x+w]
            file_name = f"{path}/rostro_{count}.jpg"
            cv2.imwrite(file_name, rostro)

            # Encriptar la imagen después de guardarla
            encriptar_imagen(file_name)
            count += 1

            # Dibujar un rectángulo alrededor del rostro
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, "Captura realizada", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Calcular el progreso en porcentaje
        porcentaje = int((count / total_capturas) * 100)
        progreso = f"Progreso: {porcentaje}%"

        # Mostrar progreso en pantalla
        cv2.putText(frame, progreso, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        #cv2.putText(frame, "Presiona 'q' para salir", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Mostrar la cámara
        cv2.imshow("Captura de Imágenes", frame)

        # Salir si se presiona 'q' o se capturan suficientes imágenes
        if cv2.waitKey(1) & 0xFF == ord('q') or count >= total_capturas or cv2.getWindowProperty("Captura de Imágenes", cv2.WND_PROP_VISIBLE) < 1:
            if cv2.getWindowProperty("Captura de Imágenes", cv2.WND_PROP_VISIBLE) < 1:
                print("Ventana de captura cerrada.")
            break

    cam.release()
    cv2.destroyAllWindows()
    return redirect('listar_usuarios')




def entrenar_modelo(request):
    data_path = "media/dataset"
    imagenes = []
    labels = []

    # Recorremos las carpetas de las imágenes
    for carpeta in os.listdir(data_path):
        label = int(carpeta.split("_")[0])
        carpeta_path = os.path.join(data_path, carpeta)

        for file in os.listdir(carpeta_path):
            img_path = os.path.join(carpeta_path, file)
            
            # Desencriptar la imagen temporalmente para su uso
            desencriptar_imagen(img_path)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            encriptar_imagen(img_path)  # Re-encriptar la imagen después de cargarla
            
            imagenes.append(img)
            labels.append(label)

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(imagenes, np.array(labels))
    recognizer.save("media/modelo_lbph.yml")

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


def reconocer_usuario(request, evento_id=None):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("media/modelo_lbph.yml")

    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    cam = cv2.VideoCapture(0)

    usuarios_registrados = set()  # Set para almacenar los usuarios ya registrados en el evento activo

    if evento_id:
        # Verificar si el evento con ese ID está activo
        try:
            evento = Evento.objects.get(id=evento_id)
        except Evento.DoesNotExist:
            return HttpResponse("Evento no encontrado", status=404)
        
        if not evento.estado:
            return HttpResponse(f"El evento '{evento.nom_evento}' no está activo", status=400)
    else:
        # Si no se pasa un evento_id, buscar el evento activo más reciente
        evento = Evento.objects.filter(estado=True).order_by('-fecha').first()

        if not evento:
            return HttpResponse("No hay eventos activos disponibles", status=400)

    last_recognized_id = None
    recognition_start_time = None
    CONFIRMATION_TIME = 2  # seconds

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rostros = detector.detectMultiScale(gris, 1.3, 5)

        if len(rostros) == 0:
            last_recognized_id = None
            recognition_start_time = None

        for (x, y, w, h) in rostros:
            rostro = gris[y:y+h, x:x+w]
            label, confianza = recognizer.predict(rostro)

            if confianza < 40:
                usuario = Usuario.objects.get(id=label)

                # Check if user is already registered BEFORE starting confirmation
                if Asistencia.objects.filter(usuario=usuario, evento_asist_id=evento.id).exists():
                    texto = f"{usuario.nombre} ya registrado"
                    color = (255, 255, 0)  # Yellow for already registered
                    last_recognized_id = None # Reset confirmation
                    recognition_start_time = None

                # If not registered, proceed with confirmation logic
                else:
                    if last_recognized_id == label:
                        elapsed_time = time.time() - recognition_start_time
                        
                        # Draw progress bar
                        progress = int((elapsed_time / CONFIRMATION_TIME) * 100)
                        cv2.rectangle(frame, (x, y + h + 5), (x + w, y + h + 15), (200, 200, 200), -1)
                        cv2.rectangle(frame, (x, y + h + 5), (x + int(w * (progress / 100)), y + h + 15), (0, 255, 0), -1)

                        if elapsed_time >= CONFIRMATION_TIME:
                            # The check is repeated here, but it's fine.
                            # It ensures that in a race condition, we don't register twice.
                            if not Asistencia.objects.filter(usuario=usuario, evento_asist_id=evento.id).exists():
                                Asistencia.objects.create(usuario=usuario, evento_asist_id=evento.id)
                                usuarios_registrados.add(usuario.id)
                                texto = f"Usuario {usuario.nombre} registrado"
                                color = (0, 255, 0)
                            else: # Should be rare to hit this else
                                texto = f"{usuario.nombre} ya registrado"
                                color = (255, 255, 0)
                            
                            # Reset after registration
                            last_recognized_id = None
                            recognition_start_time = None

                        else:
                            texto = f"Confirmando a {usuario.nombre}..."
                            color = (0, 255, 255) # Yellowish for confirming

                    else: # New face recognized for confirmation
                        last_recognized_id = label
                        recognition_start_time = time.time()
                        texto = f"Reconociendo a {usuario.nombre}"
                        color = (0, 255, 255)

            else: # Unknown face
                last_recognized_id = None
                recognition_start_time = None
                texto = "Desconocido"
                color = (0, 0, 255)

            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, texto, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        cv2.imshow("Reconocimiento Facial - presione 'q' para salir", frame)

        # Salir si se presiona 'q' o si la ventana se cierra
        if cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty("Reconocimiento Facial - presione 'q' para salir", cv2.WND_PROP_VISIBLE) < 1:
            print("Ventana de reconocimiento cerrada.")
            break

    cam.release()
    cv2.destroyAllWindows()
    return redirect('pagina_inicio')

def listar_asistencias(request):
    asistencias = Asistencia.objects.select_related('usuario', 'evento_asist')  # Optimizar consultas
    return render(request, 'listar_asistencias.html', {'asistencias': asistencias})

def listar_eventos(request):
    eventos = Evento.objects.all().order_by('fecha')  # Ordenamos los eventos por fecha
    return render(request, 'listar_eventos.html', {'eventos': eventos})

def crear_evento(request):
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_eventos')  # Redirige al listado de eventos
    else:
        form = EventoForm()

    return render(request, 'crear_evento.html', {'form': form})

def editar_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)  # Obtener el evento por su ID

    if request.method == 'POST':
        # Obtener los datos del formulario
        nom_evento = request.POST.get('nom_evento')
        fecha = request.POST.get('fecha')
        relator = request.POST.get('relator')
        descripcion = request.POST.get('descripcion')
        estado = request.POST.get('estado') == 'True'  # Convertir el valor a booleano

        # Actualizar los datos del evento
        evento.nom_evento = nom_evento
        evento.fecha = fecha
        evento.relator = relator
        evento.descripcion = descripcion
        evento.estado = estado
        evento.save()  # Guardar los cambios en la base de datos

        return redirect('listar_eventos')  # Redirigir a la lista de eventos

    return render(request, 'editar_evento.html', {'evento': evento})  # Mostrar el formulario con los datos actuales

from cryptography.fernet import Fernet
import base64

# Generar una clave simétrica y guardarla en un archivo
def generar_clave():
    clave = Fernet.generate_key()
    with open("media/encryption_key.key", "wb") as key_file:
        key_file.write(clave)

# Cargar la clave existente
def cargar_clave():
    with open("media/encryption_key.key", "rb") as key_file:
        return key_file.read()

# Encriptar una imagen
def encriptar_imagen(path_imagen):
    clave = cargar_clave()
    fernet = Fernet(clave)
    with open(path_imagen, "rb") as file:
        datos = file.read()
    datos_encriptados = fernet.encrypt(datos)
    with open(path_imagen, "wb") as file:
        file.write(datos_encriptados)

# Desencriptar una imagen
def desencriptar_imagen(path_imagen):
    clave = cargar_clave()
    fernet = Fernet(clave)
    with open(path_imagen, "rb") as file:
        datos_encriptados = file.read()
    datos_desencriptados = fernet.decrypt(datos_encriptados)
    with open(path_imagen, "wb") as file:
        file.write(datos_desencriptados)

def cambiar_estado_evento(request, evento_id):
    if request.method == "POST":
        evento = get_object_or_404(Evento, id=evento_id)
        evento.estado = not evento.estado  # Cambiar el estado
        evento.save()
    return redirect('listar_eventos')