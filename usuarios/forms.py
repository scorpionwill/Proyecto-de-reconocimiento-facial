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
        fields = ['nom_evento', 'fecha', 'relator', 'descripcion', 'estado']

        # 'widgets' permite personalizar cómo se renderizan los campos del formulario en HTML.
        widgets = {
            # Renderiza el campo 'fecha' como una entrada de tipo 'date' en HTML,
            # lo que proporciona un selector de fecha en los navegadores compatibles.
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            # Renderiza el campo 'estado' como un menú desplegable ('select')
            # con las opciones 'Activo' (valor True) e 'Inactivo' (valor False).
            'estado': forms.Select(choices=[(True, 'Activo'), (False, 'Inactivo')])
        }