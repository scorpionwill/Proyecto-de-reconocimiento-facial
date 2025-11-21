from django import forms
from .models import Usuario, Evento

# Define un formulario de Django basado en el modelo 'Usuario'.
# Este formulario se puede usar para crear o actualizar instancias de Usuario.
class UsuarioForm(forms.ModelForm):
    class Meta:
        # Especifica que este formulario está vinculado al modelo 'Usuario'.
        model = Usuario
        # Lista los campos del modelo que se incluirán en el formulario.
        fields = ['nombre', 'rut', 'carrera']

# Define un formulario de Django basado en el modelo 'Evento'.
# Este formulario se utiliza para la creación y edición de eventos.
class EventoForm(forms.ModelForm):
    class Meta:
        # Vincula el formulario al modelo 'Evento'.
        model = Evento
        # Define los campos del modelo que se mostrarán en el formulario.
        fields = ['nom_evento', 'fecha', 'relator', 'descripcion']
        
        labels = {
            'nom_evento': 'Nombre del Evento',
        }

        # 'widgets' permite personalizar cómo se renderizan los campos del formulario en HTML.
        widgets = {
            'nom_evento': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'relator': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
        }