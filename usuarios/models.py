from django.db import models

class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    rut = models.CharField(max_length=20, unique=True)
    carrera = models.CharField(max_length=100, blank=True, null=True)
    imagen = models.BinaryField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Evento(models.Model):
    id = models.AutoField(primary_key=True)
    nom_evento = models.CharField(max_length=100)
    fecha = models.DateField()
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    relator = models.CharField(max_length=60, blank=True, null=True)
    estado = models.BooleanField()

    def __str__(self):
        return self.nom_evento

class Asistencia(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    evento_asist = models.ForeignKey(Evento, on_delete=models.CASCADE)
