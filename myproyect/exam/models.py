from django.db import models
from django.utils import timezone
from pydantic import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

class PasswordReset(models.Model):
    reset_id = models.CharField(unique=True, max_length=32)
    created_when = models.DateTimeField()
    user = models.ForeignKey(User, models.DO_NOTHING)

    def __str__(self):
        return f"Password reset for {self.user} - ID: {self.reset_id}"

class Role(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    nomRol = models.CharField(max_length=20, verbose_name='Nombre del Rol')
    
    def __str__(self):
        return self.nomRol 
    
class CustomUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    aspira = models.TextField(blank=True, null=True)
    acceso = models.BooleanField(default=False)  # Usar BooleanField para acceso

    def __str__(self):
        return f"{self.user.username} - Aspira: {self.aspira}"



class Asignature(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    nameAs = models.CharField(max_length=50, verbose_name='Nombre de la Asignatura')
    def __str__(self):
        return self.nameAs

class Course(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    nomCourse = models.CharField(max_length=25, verbose_name='Nombre del Curso', unique=True)
    profesor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        limit_choices_to={'groups__name': 'Profesor'},
        verbose_name='Profesor',
        null=True  # Permite valores nulos temporalmente
    )

    def save(self, *args, **kwargs):
        # Convertir el nombre del curso a mayúsculas antes de guardarlo
        self.nomCourse = self.nomCourse.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nomCourse


class Career(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    nameCareer = models.CharField(max_length=50, verbose_name='Nombre de la Carrera')
    def __str__(self):
        return self.nameCareer

class Student(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='Curso')
    career = models.ForeignKey(Career, on_delete=models.CASCADE, verbose_name='Carrera')

class Material(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    TYPE_CHOICES = [
        ('image', 'Imagen'),
        ('reading', 'Lectura'),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='Tipo de Material')
    content = models.TextField(verbose_name='Contenido')

class Question(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    asignature = models.ForeignKey(Asignature, on_delete=models.CASCADE, verbose_name='Asignatura')
    question = models.TextField(verbose_name='Pregunta')
    options = models.TextField(verbose_name='Opciones')  # Se pueden separar por comas: opción1, opción2, opción3
    correctOption = models.TextField(verbose_name='Opción Correcta')

class QuestionMaterial(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Pregunta')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name='Material')

class Test(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    userProfesor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Profesor encargado')
    
    # Cambié el nombre del campo a 'typeExa' para hacerlo más descriptivo
    TYPE_EXAM_CHOICES = [
        ('PT', 'Práctica'),
        ('EM', 'Módulo'),
        ('ED', 'Diagnóstico'),
    ]
    typeExa = models.CharField(
        max_length=2,
        choices=TYPE_EXAM_CHOICES,
        default='PT',  # Valor predeterminado
        verbose_name='Tipo de Prueba'
    )
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='Curso')
    testDate = models.DateField(verbose_name='Fecha de la Prueba')
    tesTimI = models.TimeField(null=True, verbose_name='Hora de la Prueba Inicio')
    tesTimF = models.TimeField(null=True, verbose_name='Hora de la Prueba Fin') 
    numQuestions = models.IntegerField(verbose_name='Número de Preguntas')
    timeDuration = models.IntegerField(default=0, verbose_name='Duración de la Prueba')
    moduEx = models.TextField(null=True, verbose_name='Modulo Examen')
    Attempts = models.IntegerField(verbose_name='Intentos')

    def __str__(self):
        return f"Test {self.id} - {self.get_typeExa_display()}"
    

class TestQuestion(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, verbose_name='Test')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Pregunta')

class ExamResult(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario', null=True)
    test = models.ForeignKey(Test, on_delete=models.CASCADE, verbose_name='Test')
    score = models.FloatField(verbose_name='Puntaje')
    answers = models.TextField(verbose_name='Respuestas')  # Respuestas seleccionadas, separadas por comas
    passed = models.BooleanField(verbose_name='Aprobado')
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')
    Attempts = models.IntegerField(default=0, verbose_name='Intentos')

class ProfessorSubject(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    professor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Profesor')
    asignature = models.ForeignKey(Asignature, on_delete=models.CASCADE, verbose_name='Asignatura')
