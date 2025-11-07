from django import forms
from .models import Usuario, Evento

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'rut', 'carrera']  # Solo los campos que quieres que se muestren

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['nom_evento', 'fecha', 'relator', 'descripcion', 'estado']  # Ajusta según tus campos

        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'estado': forms.Select(choices=[(True, 'Activo'), (False, 'Inactivo')])
        }
