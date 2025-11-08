from django.db import models

# Define el modelo para la tabla 'Usuario' en la base de datos.
# Cada instancia de esta clase representa un registro de un usuario.
class Usuario(models.Model):
    # Campo de clave primaria autoincremental para identificar de forma única a cada usuario.
    id = models.AutoField(primary_key=True)
    # Campo para almacenar el nombre del usuario, con una longitud máxima de 255 caracteres.
    nombre = models.CharField(max_length=255)
    # Campo para almacenar el RUT del usuario, debe ser único para cada uno.
    rut = models.CharField(max_length=20, unique=True)
    # Campo para la carrera del usuario, puede estar en blanco o ser nulo.
    carrera = models.CharField(max_length=100, blank=True, null=True)
    # Campo para almacenar datos binarios de una imagen, puede estar en blanco o ser nulo.
    imagen = models.BinaryField(blank=True, null=True)

    # Método que devuelve una representación en cadena del objeto, en este caso, el nombre del usuario.
    def __str__(self):
        return self.nombre

# Define el modelo para la tabla 'Evento' en la base de datos.
# Cada instancia de esta clase representa un evento.
class Evento(models.Model):
    # Campo de clave primaria autoincremental para el evento.
    id = models.AutoField(primary_key=True)
    # Campo para el nombre del evento.
    nom_evento = models.CharField(max_length=100)
    # Campo para la fecha del evento.
    fecha = models.DateField()
    # Campo para una descripción del evento, puede estar en blanco o ser nulo.
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    # Campo para el nombre del relator del evento, puede estar en blanco o ser nulo.
    relator = models.CharField(max_length=60, blank=True, null=True)
    # Campo booleano para indicar el estado del evento (por ejemplo, activo o inactivo).
    estado = models.BooleanField()

    # Método que devuelve el nombre del evento como su representación en cadena.
    def __str__(self):
        return self.nom_evento

# Define el modelo para la tabla 'Asistencia' en la base de datos.
# Registra la asistencia de un usuario a un evento.
class Asistencia(models.Model):
    # Campo de clave primaria autoincremental para el registro de asistencia.
    id = models.AutoField(primary_key=True)
    # Clave foránea que relaciona la asistencia con un usuario. Si el usuario se elimina, sus registros de asistencia también se eliminarán.
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    # Campo de fecha y hora que se establece automáticamente al crear el registro de asistencia.
    fecha = models.DateTimeField(auto_now_add=True)
    # Clave foránea que relaciona la asistencia con un evento. Si el evento se elimina, los registros de asistencia asociados también se eliminarán.
    evento_asist = models.ForeignKey(Evento, on_delete=models.CASCADE)