from django.urls import path
from . import views

# Define las rutas URL para la aplicación 'usuarios'.
# Cada 'path' conecta una URL con una función de vista específica en 'views.py'.
urlpatterns = [
    # URL para la página de inicio.
    path('', views.pagina_inicio, name='pagina_inicio'),
    
    # URL para mostrar la lista de todos los usuarios.
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'),
    
    # URL para el formulario de creación de un nuevo usuario.
    path('crear_usuario/', views.crear_usuario, name='crear_usuario'),
    
    # URL para editar un usuario existente, identificado por su 'usuario_id'.
    path('usuario/<int:usuario_id>/editar/', views.editar_usuario, name='editar_usuario'),
    
    # URL para mostrar la lista de todos los eventos.
    path('eventos/', views.listar_eventos, name='listar_eventos'),
    
    # URL para el formulario de creación de un nuevo evento.
    path('crear_evento/', views.crear_evento, name='crear_evento'),
    
    # URL para editar un evento existente, identificado por su 'evento_id'.
    path('evento/editar/<int:evento_id>/', views.editar_evento, name='editar_evento'),
    
    # URL para mostrar la lista de todas las asistencias registradas.
    path('asistencias/', views.listar_asistencias, name='listar_asistencias'),
    
    # URL para iniciar el proceso de captura de imágenes para un usuario específico.
    path('capturar_imagenes/<int:usuario_id>/', views.capturar_imagenes, name='capturar_imagenes'),
    
    # URL para iniciar el entrenamiento del modelo de reconocimiento facial.
    path('entrenar_modelo/', views.entrenar_modelo, name='entrenar_modelo'),
    
    # URL para iniciar el reconocimiento facial y registrar la asistencia a un evento específico.
    path('reconocer_usuario/<int:evento_id>/', views.reconocer_usuario, name='reconocer_usuario'),
    
    # URL para cambiar el estado (activo/inactivo) de un evento.
    path('evento/cambiar_estado/<int:evento_id>/', views.cambiar_estado_evento, name='cambiar_estado_evento'),
]