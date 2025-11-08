from django.contrib import admin
from .models import Usuario, Evento, Asistencia

# Este archivo registra los modelos de la aplicación 'usuarios' en el panel de administración de Django.
# Al registrar un modelo, Django crea automáticamente una interfaz de administración
# que permite crear, leer, actualizar y eliminar registros de ese modelo.

# Registra el modelo 'Usuario' para que sea gestionable desde el panel de administración.
admin.site.register(Usuario)

# Registra el modelo 'Evento' para que sea gestionable desde el panel de administración.
admin.site.register(Evento)

# Registra el modelo 'Asistencia' para que sea gestionable desde el panel de administración.
admin.site.register(Asistencia)