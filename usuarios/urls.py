from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagina_inicio, name='pagina_inicio'),
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('crear_usuario/', views.crear_usuario, name='crear_usuario'),
    path('usuario/<int:usuario_id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('eventos/', views.listar_eventos, name='listar_eventos'),
    path('crear_evento/', views.crear_evento, name='crear_evento'),
    path('evento/editar/<int:evento_id>/', views.editar_evento, name='editar_evento'),  # URL para editar evento
    path('asistencias/', views.listar_asistencias, name='listar_asistencias'),
    path('capturar_imagenes/<int:usuario_id>/', views.capturar_imagenes, name='capturar_imagenes'),
    path('entrenar_modelo/', views.entrenar_modelo, name='entrenar_modelo'),
    path('reconocer_usuario/<int:evento_id>/', views.reconocer_usuario, name='reconocer_usuario'),
    path('evento/cambiar_estado/<int:evento_id>/', views.cambiar_estado_evento, name='cambiar_estado_evento'),
]
