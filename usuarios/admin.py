from django.contrib import admin
from .models import Usuario, Evento, Asistencia

# Registro básico de los modelos
admin.site.register(Usuario)
admin.site.register(Evento)
admin.site.register(Asistencia)
