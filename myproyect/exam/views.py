from datetime import date, datetime, timezone
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from pydantic import ValidationError
from .models import *  # Asegúrate de importar el modelo Course
from .form import *
import coreapi #esto es para la api
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import timedelta
import logging
import random
from django.contrib.auth import logout
from django.urls import reverse
from .models import User
from django.template.loader import get_template
from xhtml2pdf import pisa
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

logger = logging.getLogger(__name__)


def is_in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

def group_required(group_name):
    return user_passes_test(lambda user: is_in_group(user, group_name), login_url='login')


@login_required
def Home(request):
    user = request.user
    if user.is_superuser:
        return redirect('admin:index')  # Redirige a la vista de administración si es superusuario

   
# Determina el grupo del usuario
    if user.groups.filter(name='Estudiante').exists():
        return redirect('estudiante_view')

    elif user.groups.filter(name='Administrador').exists():
        return redirect('administrador_view')  # Redirige a la vista de 'Administrador'

    elif user.groups.filter(name='Asesor').exists():
        return redirect('asesor_view')  # Redirige a la vista de 'Asesor'

    elif user.groups.filter(name='SubAsesor').exists():
        return redirect('subasesor_view')  # Redirige a la vista de 'SubAsesor'
    
    elif user.groups.filter(name='Profesor').exists():
        return redirect('profesor_view')  # Redirige a la vista de 'SubAsesor'

    else:
        messages.error(request, 'No role assigned. Please contact the administrator.')
        return redirect('login')  # Redirige si no tiene rol asignado
    

@group_required('Profesor')
def profesor_view(request):
    user = request.user
    profesor = User.objects.get(id=user.id)  # Asumiendo que User es tu modelo de usuario
    cursos = Course.objects.filter(profesor=profesor)
    
    context = {
            'username': user.username,
            'rol': 'Profesor',
            'cantidad_cursos': cursos.count(),
            'profesor': profesor,
        }
    return render(request, 'paginas/profesor.html', context)  # Renderiza la página para profesores


@login_required(login_url='login')
@group_required('Asesor')
def asesor_view(request):
    user = request.user
    context = {
            'username': user.username,
            'rol': 'Aseros Saber Pro',
        }
    return render(request, 'paginas/asesor.html', context)  # Renderiza la página para asesores


@login_required(login_url='login')
@group_required('SubAsesor')
def subasesor_view(request):
    user = request.user
    context = {
            'username': user.username,
            'rol': 'Sub Asesor',
        }
    return render(request, 'paginas/subasesor.html', context)  # Renderiza la página para subasesores

@login_required(login_url='login')
@group_required('Estudiante')
def estudiante_view(request):
    user = request.user  # Obtén el usuario que ha iniciado sesión
    # Obtén el objeto Student asociado al usuario
    student = get_object_or_404(Student, user=user)  # Obtiene el Student relacionado con el usuario
    
    context = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'carrera': student.career.nameCareer,  # Obtiene la carrera del modelo Career
        'curso': student.course.nomCourse,      # Obtiene el curso del modelo Course
        'rol': 'Estudiante',
        'username': user.username,
    }
    return render(request, 'paginas/estudiante.html', context)  # Renderiza la página para subasesores

# Roles
def roles(request):
    roles = Role.objects.all()
    return render(request, 'roles/index.html', {'roles': roles})


@login_required
def estudiantes_por_curso(request):
    # Obtén el profesor logueado
    profesor = request.user

    # Obtén los cursos del profesor
    cursos = Course.objects.filter(profesor=profesor)

    # Si se ha seleccionado un curso, obtén los estudiantes de ese curso
    estudiantes = []
    curso_seleccionado = None

    if request.method == "POST":
        curso_id = request.POST.get('curso')
        curso_seleccionado = get_object_or_404(Course, id=curso_id)
        estudiantes = Student.objects.filter(course=curso_seleccionado)

    context = {
        'cursos': cursos,
        'estudiantes': estudiantes,
        'curso_seleccionado': curso_seleccionado,
    }
    
    return render(request, 'students/estudiantes_por_curso.html', context) 

def CreateRole(request):
    user = request.user
    formulario = RoleForm(request.POST or None)  
    if formulario.is_valid():
        nomRol = formulario.cleaned_data['nomRol'].upper()
        new_role = Role(nomRol=nomRol)
        new_role.save()
        return redirect('roles')    
    return render(request, 'roles/create.html', {'formulario': formulario, 'username': user.username,
            'rol': 'Asesor',})

def UpdateRole(request, id):
    rol = get_object_or_404(Role, id=id)
    formulario = RoleForm(request.POST or None, instance=rol)  
    if formulario.is_valid():
        rol.nomRol = formulario.cleaned_data['nomRol'].upper()
        rol.save()
        return redirect('roles') 
    return render(request, 'roles/update.html', {'formulario': formulario})

def DeleteRole(request, id):
    rol = get_object_or_404(Role, id=id)
    rol.delete()
    return redirect('roles')


@login_required
def users(request):
    user = request.user
    users = User.objects.all()
    context = {
        'username': user.username,
        'users': users
    }
    return render(request, 'users/index.html', context)

"""
@login_required(login_url='login')  # Verifica que el usuario esté logueado
@group_required('SubAsesor')  """ # Verifica que el usuario esté en el grupo """
def activar(request):
    userj = request.user
    user = request.user
    # Obtener todos los usuarios que no están asociados a ningún grupo
    users = User.objects.filter(groups=None)

    # Crear una lista de usuarios con sus detalles, incluyendo la aspiración si están en CustomUser
    users_with_aspiration = []
    for user in users:
        try:
            # Intentar obtener el registro de CustomUser
            custom_user = CustomUser.objects.get(user=user)
            aspiration = custom_user.aspira  # Obtener la aspiración si existe
        except CustomUser.DoesNotExist:
            aspiration = None  # Si no está en CustomUser, aspiración es None

        # Agregar el usuario y su aspiración a la lista
        users_with_aspiration.append({
            'user': user,
            'aspiration': aspiration
        })

    # Pasar los usuarios al contexto para la plantilla
    context = {
        'users_with_aspiration': users_with_aspiration,
        'username': userj.username
    }
    return render(request, 'users/activar.html', context)

"""
@login_required(login_url='login')  # Verifica que el usuario esté logueado
@group_required('SubAsesor')  """ # Verifica que el usuario esté en el grupo """
def activate_user(request, user_id):
    if request.method == "POST":
        aspiracion = request.POST.get("aspiracion")
        user = get_object_or_404(User, id=user_id)
        print(f"{aspiracion}")

        # Activar el usuario
        user.is_active = True
        user.save()
        print(f"{user.is_active}")

        # Asignar el grupo según la aspiración
        if aspiracion == "Estudiante":
            group = Group.objects.get(name='Estudiante')  # Cambia 'Grupo 1' según tu lógica
            # Enviar correo de confirmación
            email_subject = 'Cuenta activada en SisPro'
            email_body = f'''
            Estimado {user.first_name},

            Tu cuenta en SisPro ya está activada y se te ha asignado al grupo "{group.name}".

            Puedes iniciar sesión con tus credenciales para acceder al sistema.

            Saludos cordiales,
            El equipo de SisPro.
            '''
            email_message = EmailMessage(
                email_subject,
                email_body,
                settings.EMAIL_HOST_USER,
                [user.email],  # Enviar al correo del usuario
            )
            email_message.send()
        elif aspiracion == "Grupo 2":
            group = Group.objects.get(name='Grupo 2')  # Cambia 'Grupo 2' según tu lógica
        else:
            messages.error(request, "Grupo no válido para la aspiración seleccionada.")
            return redirect('activar')  # Cambia a la vista de activar usuarios

        user.groups.add(group)  # Agrega el usuario al grupo
        messages.success(request, "Usuario activado y asignado al grupo correctamente.")
        return redirect('activar')  # Cambia a la vista de activar usuarios

    return redirect('activar')  # Redirige en caso de solicitud GET

def CreateUser(request):
    formulario = UserForm(request.POST or None)
    if formulario.is_valid():       
        namUsu = formulario.cleaned_data['namUsu'].upper()
        lasUsu = formulario.cleaned_data['lasUsu'].upper()
        new_user = User(
            namUsu=namUsu,
            lasUsu=lasUsu,
            rol=formulario.cleaned_data['rol'],
            typeDoc=formulario.cleaned_data['typeDoc'],
            numDoc=formulario.cleaned_data['numDoc'],
            email=formulario.cleaned_data['email'],
            password=formulario.cleaned_data['password']
        )
        new_user.save()
        return redirect('users')  
    return render(request, 'users/create.html', {'formulario': formulario})

def UpdateUser(request, id):
    user = get_object_or_404(User, id=id)
    formulario = UserForm(request.POST or None, instance=user)
    
    if formulario.is_valid():
        user.namUsu = formulario.cleaned_data['namUsu'].upper()
        user.lasUsu = formulario.cleaned_data['lasUsu'].upper()
        user.rol = formulario.cleaned_data['rol']
        user.typeDoc = formulario.cleaned_data['typeDoc']
        user.numDoc = formulario.cleaned_data['numDoc']
        user.email = formulario.cleaned_data['email']
        user.password = formulario.cleaned_data['password']  # Considera encriptar la contraseña antes de guardar
        user.save()
        return redirect('users')
    
    return render(request, 'users/update.html', {'formulario': formulario})

def DeleteUser(request, id):
    user = get_object_or_404(User, id=id)
    user.delete()
    return redirect('users')

# Asignatures------------------------------------------------------------------API
def asignatures(request):
    client = coreapi.Client()
    schema = client.get("http://localhost:8000/docs/")

    try:
        asignatures_data = client.action(schema, ["asignatures", "list"])
    except coreapi.exceptions.ErrorMessage as e:
        print(f"Error al consumir la API: {e}")
        asignatures_data = []

    return render(request, 'asignature/index.html', {'asignatures': asignatures_data})

def CreateAsignatures(request):
    formulario = AsignatureForm(request.POST or None)
    
    if formulario.is_valid():
        nameAs = formulario.cleaned_data['nameAs'].upper()
        client = coreapi.Client()
        schema = client.get("http://localhost:8000/docs/")
        try:
            params = {"nameAs": nameAs}
            client.action(schema, ["asignatures", "create"], params=params)
            return redirect('asignature')
        except coreapi.exceptions.ErrorMessage as e:
          
            print(f"Error al crear la asignatura en la API: {e}")
            formulario.add_error(None, "No se pudo crear la asignatura en la API.")
    return render(request, 'asignature/create.html', {'formulario': formulario})

def UpdateAsignatures(request, id):
    client = coreapi.Client()
    schema = client.get("http://localhost:8000/docs/")

    # Cargar la asignatura desde la API
    try:
        # Usar 'list' para obtener todas las asignaturas y buscar la correspondiente al ID
        asignature_list = client.action(schema, ["asignatures", "list"])
        
        # Filtrar la asignatura que deseas actualizar
        asignature_data = next((item for item in asignature_list if item['id'] == id), None)
        
        if not asignature_data:
            messages.error(request, "Asignatura no encontrada.")
            return redirect('asignature')  # Redirigir si no se encuentra la asignatura

        # Crear el formulario con los datos iniciales de la asignatura
        formulario = AsignatureForm(initial={"nameAs": asignature_data['nameAs']})
    except coreapi.exceptions.ErrorMessage as e:
        print(f"Error al recuperar la asignatura desde la API: {e}")
        messages.error(request, "No se pudo recuperar la asignatura.")
        return redirect('asignature')  # Redirigir si hay un error

    if request.method == 'POST':
        # Obtener los datos del formulario enviado
        formulario = AsignatureForm(request.POST)
        if formulario.is_valid():
            nameAs = formulario.cleaned_data['nameAs'].upper()  # Convertir el nombre a mayúsculas
            try:
                # Actualizar la asignatura en la API
                params = {"id": id, "nameAs": nameAs}
                client.action(schema, ["asignatures", "update"], params=params)
                messages.success(request, "Asignatura actualizada correctamente.")
                return redirect('asignature')  # Redirigir a la lista de asignaturas después de la actualización
            except coreapi.exceptions.ErrorMessage as e:
                print(f"Error al actualizar la asignatura en la API: {e}")
                formulario.add_error(None, "No se pudo actualizar la asignatura en la API.")

    # Renderizar el formulario con posibles errores
    return render(request, 'asignature/update.html', {'formulario': formulario})

def DeleteAsignatures(request, id):
    client = coreapi.Client()
    schema = client.get("http://localhost:8000/docs/")

    try:
        # Ejecuta la acción 'delete' en el endpoint 'asignatures' pasando el ID
        client.action(schema, ["asignatures", "delete"], params={"id": id})
        messages.success(request, "Asignatura eliminada correctamente.")
    except coreapi.exceptions.ErrorMessage as e:
        # Manejo de errores de la API
        print(f"Error al eliminar la asignatura en la API: {e}")
        messages.error(request, "No se pudo eliminar la asignatura en la API.")
    
    return redirect('asignature')

# Careers
def careers(request):
    careers = Career.objects.all()
    return render(request, 'careers/index.html', {'careers': careers})

def CreateCareers(request):
    formulario = CareerForm(request.POST or None)
    if formulario.is_valid():
        nameCareer = formulario.cleaned_data['nameCareer'].upper()
        new_career = Career(nameCareer=nameCareer)
        new_career.save()
        return redirect('careers')
    return render(request, 'careers/create.html', {'formulario': formulario})

def UpdateCareers(request, id):
    career = get_object_or_404(Career, id=id)
    formulario = CareerForm(request.POST or None, instance=career)
    if formulario.is_valid():
        career.nameCareer = formulario.cleaned_data['nameCareer'].upper()
        career.save()
        return redirect('careers')
    return render(request, 'careers/update.html', {'formulario': formulario})

def DeleteCareers(request, id):
    career = get_object_or_404(Career, id=id)
    career.delete()
    return redirect('careers')

# Materials----------------------------------------------------------------Pendiente aun no muestra la img 
def materials(request):
    client = coreapi.Client()
    schema = client.get("http://localhost:8090/docs/")
    
    try:
        materials_data = client.action(schema, ["materials", "list"])
        
        # Base URL para las imágenes
        base_url = "https://zn4zz9nw-8090.use2.devtunnels.ms/media/materials/"
        
        # Construir la URL completa para cada material
        for material in materials_data:
           
            material['image_url'] = base_url + material['content']  # Usa un nuevo campo para almacenar la URL de la imagen

    except coreapi.exceptions.ErrorMessage as e:
        print(f"Error al consumir la API: {e}")
        materials_data = []

    return render(request, 'materials/index.html', {'materials': materials_data})

def CreateMaterials(request):
    formulario = MaterialForm(request.POST or None, request.FILES or None)
    
    if formulario.is_valid():
        content = formulario.cleaned_data.get('content')  # Puede ser None
        text_content = formulario.cleaned_data.get('text_content')  # Puede ser None
        
        client = coreapi.Client()
        schema = client.get("http://127.0.0.1:8090/docs/")
        
        try:
            params = {
                "content": content,
                "text_content": text_content
            }
            client.action(schema, ["materials", "create"], params=params)
            return redirect('material_list')  # Redirige a la lista de materiales
        except coreapi.exceptions.ErrorMessage as e:
            print(f"Error al crear el material en la API: {e}")
            formulario.add_error(None, "No se pudo crear el material en la API.")
    
    return render(request, 'materials/create.html', {'formulario': formulario})

def UpdateMaterials(request, id):
    client = coreapi.Client()
    schema = client.get("http://127.0.0.1:8090/docs/")
    try:
        material_list = client.action(schema, ["materials", "list"])
        material_data = next((item for item in material_list if item['id'] == id), None)
        
        if not material_data:
            messages.error(request, "Material no encontrado.")
            return redirect('material_list')  
        formulario = MaterialForm(initial={
            "content": material_data['content'],
            "text_content": material_data['text_content']
        })
    except coreapi.exceptions.ErrorMessage as e:
        print(f"Error al recuperar el material desde la API: {e}")
        messages.error(request, "No se pudo recuperar el material.")
        return redirect('material_list') 

    if request.method == 'POST':
       
        formulario = MaterialForm(request.POST)
        if formulario.is_valid():
            content = formulario.cleaned_data['content']
            text_content = formulario.cleaned_data['text_content']
            try:
                params = {
                    "id": id,
                    "content": content,
                    "text_content": text_content
                }
                client.action(schema, ["materials", "update"], params=params)
                messages.success(request, "Material actualizado correctamente.")
                return redirect('material_list') 
            except coreapi.exceptions.ErrorMessage as e:
                print(f"Error al actualizar el material en la API: {e}")
                formulario.add_error(None, "No se pudo actualizar el material en la API.")
    return render(request, 'materials/update.html', {'formulario': formulario})

def DeleteMaterials(request, id):
    client = coreapi.Client()
    schema = client.get("http://127.0.0.1:8090/docs/")
    try:
        client.action(schema, ["materials", "delete"], params={"id": id})
        messages.success(request, "Material eliminado correctamente.")
    except coreapi.exceptions.ErrorMessage as e:
        print(f"Error al eliminar el material en la API: {e}")
        messages.error(request, "No se pudo eliminar el material en la API.")
    return redirect('material_list')

# Questions-----------------------------------------------
def questions_view(request):
    client = coreapi.Client()
    schema = client.get("http://localhost:8090/docs/")

    try:
        questions_data = client.action(schema, ["questions", "list"])
        print("Datos obtenidos de la API:", questions_data)  # Imprime los datos obtenidos
    except coreapi.exceptions.ErrorMessage as e:
        print(f"Error al consumir la API: {e}")
        questions_data = []

    return render(request, 'questions/index.html', {'questions': questions_data})

def CreateQuestions(request):
    # Cargar asignaturas para el formulario
    asignaturas = Asignature.objects.all()
    formulario = QuestionForm(request.POST or None)

    if formulario.is_valid():
        # Extrae los datos del formulario
        question = formulario.cleaned_data['question'].upper()
        options = formulario.cleaned_data['options']
        correct_option = formulario.cleaned_data['correctOption']
        id_asignature = formulario.cleaned_data['asignature'].id  # Obtén el ID de la asignatura seleccionada

        # Configura la conexión con la API usando coreapi
        client = coreapi.Client()
        schema = client.get("http://localhost:8090/docs/")

        # Prepara los parámetros para enviar a la API
        params = {
            "question": question,
            "options": options,
            "correctOption": correct_option,
            "idAsignature": id_asignature
        }

        try:
            # Llama a la acción de la API para crear la pregunta
            client.action(schema, ["questions", "create"], params=params)
            return redirect('questions')  # Redirige a la lista de preguntas después de guardar
        except coreapi.exceptions.ErrorMessage as e:
            print(f"Error al crear la pregunta en la API: {e}")
            formulario.add_error(None, "No se pudo crear la pregunta en la API.")
    
    # Renderiza el formulario y envía las asignaturas como contexto
    return render(request, 'questions/create.html', {'formulario': formulario, 'asignaturas': asignaturas,'user': request.user,})

def UpdateQuestions(request, id):
    question = get_object_or_404(Question, id=id)
    # Cargar asignaturas para el formulario
    asignaturas = Asignature.objects.all()  
    formulario = QuestionForm(request.POST or None, instance=question)

    if formulario.is_valid():
        question.asignature = formulario.cleaned_data['asignature']  # Asegúrate de que el campo se llama 'asignature'
        question.question = formulario.cleaned_data['question'].upper()  # Asegúrate de que el campo se llama 'question'
        question.options = formulario.cleaned_data['options']  # Campo para las opciones
        question.correctOption = formulario.cleaned_data['correctOption']  # Campo para la opción correcta
        question.save()
        return redirect('questions')  # Redirige a la lista de preguntas después de guardar

    return render(request, 'questions/update.html', {'formulario': formulario, 'asignaturas': asignaturas})

def DeleteQuestions(request, id):
    question = get_object_or_404(Question, id=id)
    question.delete()
    return redirect('questions')

# Test
def test_view_a(request):
    asignatures = Asignature.objects.all()  # Obtiene todas las asignaturas
    return render(request, 'tes/form.html', {
        'asignatures': asignatures
    })
    
@login_required
def CreateTest(request):
    # Filtrar cursos donde el profesor es el usuario logueado
    cursos_profesor = Course.objects.filter(profesor=request.user)

    # Crear el formulario y asignar los cursos disponibles
    formulario = TestForm(request.POST or None, user=request.user)  # Pasar el usuario logueado al formulario

    if formulario.is_valid():
        # Usar el usuario logueado como el profesor
        new_test = Test(
            idUserProfesor=request.user,  # Usar el usuario logueado
            idCourse=formulario.cleaned_data['course'],
            idQuestion=formulario.cleaned_data['idQuestion'],
            testDate=formulario.cleaned_data['testDate'],
            testTime=formulario.cleaned_data['testTime'],
            numQuestions=formulario.cleaned_data['numQuestions']
        )
        new_test.save()
        return redirect('test')

    # Pasar los cursos filtrados al contexto
    return render(request, 'test/create.html', {'formulario': formulario, 'cursos_profesor': cursos_profesor})

def UpdateTest(request, id):
    test = get_object_or_404(Test, id=id)
    formulario = TestForm(request.POST or None, instance=test)
    if formulario.is_valid():
        test.idUserProfesor = formulario.cleaned_data['idUserProfesor']
        test.idCourse = formulario.cleaned_data['idCourse']
        test.idQuestion = formulario.cleaned_data['idQuestion']
        test.testDate = formulario.cleaned_data['testDate']
        test.testTime = formulario.cleaned_data['testTime']
        test.numQuestions = formulario.cleaned_data['numQuestions']
        test.save()
        return redirect('test')
    return render(request, 'test/update.html', {'formulario': formulario})

def DeleteTest(request, id):
    test = get_object_or_404(Test, id=id)
    test.delete()
    return redirect('test')

# Exam Results
def exam_results_view(request):
    # Obtener todos los resultados de los exámenes
    exam_results = ExamResult.objects.all()

    # Calcular la media y la mediana de los puntajes
    scores = [result.score for result in exam_results]
    print(f"Scores: {scores}")

    if scores:
        average_score = sum(scores) / len(scores)
        sorted_scores = sorted(scores)
        if len(scores) % 2 != 0:
            median_score = sorted_scores[len(scores) // 2]
        else:
            median_score = (sorted_scores[len(scores) // 2 - 1] + sorted_scores[len(scores) // 2]) / 2
    else:
        average_score = 0
        median_score = 0

    # Calcular el total de aprobados y no aprobados
    total_passed = sum(1 for result in exam_results if result.passed)
    total_failed = len(exam_results) - total_passed

    # Calcular el puntaje más alto y el más bajo
    max_score = max(scores) if scores else 0
    min_score = min(scores) if scores else 0
    
    total_exams = ExamResult.objects.count()
    total_students = Student.objects.count()
    total_courses = Course.objects.count()
    total_results = ExamResult.objects.values('id').count()

    context = {
        'exam_results': exam_results,
        'average_score': average_score,
        'median_score': median_score,
        'total_passed': total_passed,
        'total_failed': total_failed,
        'max_score': max_score,
        'min_score': min_score,
        'total_exams': total_exams,
        'total_students': total_students,
        'total_courses': total_courses,
        'total_results': total_results,
        'user': request.user,
    }

    return render(request, 'exam_results/index.html', context)

def CreateExamResult(request):
    formulario = ExamResultForm(request.POST or None)
    if formulario.is_valid():
        new_result = ExamResult(
            user=formulario.cleaned_data['user'],
            test=formulario.cleaned_data['test'],
            score=formulario.cleaned_data['score']
        )
        new_result.save()
        return redirect('exam_results')
    return render(request, 'exam_results/create.html', {'formulario': formulario})
# views.py
def listar_profesores_y_cursos(request):
    # Obtener usuarios del grupo 'Profesor'
    profesores = User.objects.filter(groups__name='Profesor').prefetch_related('course_set')
    return render(request, 'profesor/listar_profe.html', {'profesores': profesores})

def UpdateExamResult(request, id):
    # Obtén el resultado del examen o retorna 404 si no existe
    result = get_object_or_404(ExamResult, id=id)
    formulario = ExamResultForm(request.POST or None, instance=result)
    if formulario.is_valid():
        # Actualiza los campos del resultado con los datos del formulario
        result.score = formulario.cleaned_data['score']
        result.answers = formulario.cleaned_data['answers']
        result.passed = formulario.cleaned_data['passed']
        result.save()
        return redirect('exam_results')

    return render(request, 'exam_results/update.html', {'formulario': formulario})

def DeleteExamResult(request, id):
    result = get_object_or_404(ExamResult, id=id)
    result.delete()
    return redirect('exam_results')

# Professor Subjects
def professor_subjects_view(request):
    professor_subjects = ProfessorSubject.objects.all()
    return render(request, 'professor_subjects/index.html', {'professor_subjects': professor_subjects})

def CreateProfessorSubject(request):
    formulario = ProfessorSubjectForm(request.POST or None)
    if formulario.is_valid():
        new_professor_subject = ProfessorSubject(
            professor=formulario.cleaned_data['professor'],
            subject=formulario.cleaned_data['subject']
        )
        new_professor_subject.save()
        return redirect('professor_subjects')
    return render(request, 'professor_subjects/create.html', {'formulario': formulario})

def UpdateProfessorSubject(request, id):
    professor_subject = get_object_or_404(ProfessorSubject, id=id)
    formulario = ProfessorSubjectForm(request.POST or None, instance=professor_subject)
    if formulario.is_valid():
        # Cambia 'subject' a 'subject' (o el nombre correcto del campo que estás usando)
        professor_subject.professor = formulario.cleaned_data['professor']
        professor_subject.subject = formulario.cleaned_data['asignature']  # Aquí es donde ocurre el error
        professor_subject.save()
        return redirect('professor_subjects')
    return render(request, 'professor_subjects/update.html', {'formulario': formulario})


def DeleteProfessorSubject(request, id):
    professor_subject = get_object_or_404(ProfessorSubject, id=id)
    professor_subject.delete()
    return redirect('professor_subjects')

# Courses View
def courses(request):
    courses = Course.objects.all()
    course_names = []
    student_counts = []

    for course in courses:
        student_count = Student.objects.filter(course=course).count()  # Contar estudiantes por curso
        course_names.append(course.nomCourse)
        student_counts.append(student_count)
    # Agrega la cantidad de estudiantes a cada curso
    for course in courses:
        course.num_students = Student.objects.filter(course=course).count()
        
    # Retorna la respuesta renderizada
    return render(request, 'courses/index.html', {'courses': courses,
                                                  'course_names': course_names,
        'student_counts': student_counts,'user': request.user,})
 
def course_students(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    students = course.student_set.all()  # Obtiene todos los estudiantes del curso
    return render(request, 'courses/students_list.html', {'course': course, 'students': students,'user': request.user,})       

def CreateCourse(request):
    formulario = CourseForm(request.POST or None)
    if formulario.is_valid():
        formulario.instance.nomCourse = formulario.cleaned_data['nomCourse'].upper()
        formulario.save()  # Guarda todos los campos, incluyendo 'profesor'
        return redirect('courses')
    return render(request, 'courses/create.html', {'formulario': formulario,'user': request.user,})


def UpdateCourse(request, id):
    course = get_object_or_404(Course, id=id)
    formulario = CourseForm(request.POST or None, instance=course)
    
    if formulario.is_valid():
        formulario.save()
        return redirect('list_tests')  # Cambia 'list_courses' por la vista a la que quieras redirigir
    
    return render(request, 'courses/update.html', {'formulario': formulario})

def DeleteCourse(request, id):
    course = get_object_or_404(Course, id=id)
    course.delete()
    return redirect('courses')

# Vista para la lista de estudiantes
def students(request):
    students = Student.objects.all()
    return render(request, 'students/index.html', {'students': students})

# Crear un nuevo estudiante
def CreateStudent(request):
    formulario = StudentForm(request.POST or None)
    if formulario.is_valid():
        formulario.save()
        return redirect('students')
    return render(request, 'students/create.html', {'formulario': formulario})

# Actualizar un estudiante existente
def UpdateStudent(request, id):
    student = get_object_or_404(Student, id=id)
    formulario = StudentForm(request.POST or None, instance=student)
    if formulario.is_valid():
        formulario.save()
        return redirect('students')
    return render(request, 'students/update.html', {'formulario': formulario})

# Eliminar un estudiante
def DeleteStudent(request, id):
    student = get_object_or_404(Student, id=id)
    student.delete()
    return redirect('students')

def question_materials_view(request):
    question_materials = QuestionMaterial.objects.all()
    return render(request, 'questionMat/index.html', {'question_materials': question_materials})

def CreateQuestionMaterial(request):
    if request.method == 'POST':
        form = QuestionMaterialForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('question_materials')  # Redirect to list view after successful creation
    else:
        form = QuestionMaterialForm()
    return render(request, 'questionMat/create.html', {'form': form})  # Use a separate template for creation

def UpdateQuestionMaterial(request, id):
    question_material = QuestionMaterial.objects.get(pk=id)  # Use primary key for safer retrieval
    if request.method == 'POST':
        form = QuestionMaterialForm(request.POST, instance=question_material)
        if form.is_valid():
            form.save()
            return redirect('question_materials')  # Redirect to list view after successful update
    else:
        form = QuestionMaterialForm(instance=question_material)
    return render(request, 'questionMat/update.html', {'form': form})  # Use a separate template for update

def DeleteQuestionMaterial(request, id):
    question_material = QuestionMaterial.objects.get(pk=id)
    if request.method == 'POST':
        question_material.delete()
        return redirect('question_materials')  # Redirect to list view after successful deletion
    return render(request, 'questionMat/delete.html', {'question_material': question_material}) 

# Listar todos los tests
def list_tests(request):
    user = request.user
    tests = Test.objects.all()  # Obtener todos los tests
    asignatures = Asignature.objects.all()
    return render(request, 'tes/index.html', {
        'tests': tests, 
        'asignatures': asignatures,
        'username': user.username,
        'rol': 'Profesor',
        'user': request.user,
    })
   
@login_required(login_url='login')     
def list_testsStud(request):
    today = timezone.now().date()  # Obtener la fecha actual
    current_time = timezone.now().time()  # Obtener la hora actual
    user = request.user

    # Obtener todos los tests que son para hoy
    tests = Test.objects.filter(testDate=today)  

    #for test in tests:
    # Filtrar los tests habilitados según la hora de inicio y fin
    #enabled_tests = tests.filter(tesTimI=current_time, tesTimF=current_time)
   
    for test in tests:
        print(f'Examen: {test.id}, Hora de inicio: {test.tesTimI}, Hora de fin: {test.tesTimF}')
    # Obtener todas las asignaturas
    asignatures = Asignature.objects.all()

    return render(request, 'tes/viewTes.html', {
        'tests': tests,  # Solo pasar los tests habilitados
        'asignatures': asignatures,
        'username': user.username,
        'rol': 'Estudiante',
        'user': request.user,
    })

# Crear un nuevo test
def create_test(request):
    if request.method == 'POST':
        form = TestForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('list_tests')  
            except ValidationError as e:
                form.add_error(None, e)  # Agregar el error al formulario
    else:
        form = TestForm()
    
    current_date = timezone.now().date()
    return render(request, 'tes/create.html', {
        'formulario': form,
        'current_date': current_date,
    })
# Actualizar un test existente

def update_test(request, id):
    # Obtener el test que se va a actualizar
    test = get_object_or_404(Test, id=id)
    
    # Cargar el formulario con los datos POST o con la instancia del test
    formulario = TestForm(request.POST or None, instance=test)
    
    if formulario.is_valid():
        # Actualizamos los campos individuales del modelo Test según los datos del formulario
        test.userProfesor = formulario.cleaned_data['userProfesor']
        test.typeExa = formulario.cleaned_data['typeExa']
        test.course = formulario.cleaned_data['course']
        test.testDate = formulario.cleaned_data['testDate']
        test.tesTimI = formulario.cleaned_data['tesTimI']
        test.tesTimF = formulario.cleaned_data['tesTimF']
        test.numQuestions = formulario.cleaned_data['numQuestions']
        test.timeDuration = formulario.cleaned_data['timeDuration']
        test.Attempts = formulario.cleaned_data['Attempts']
        
        # Guardar los cambios en la base de datos
        test.save()

        # Redirigir a una vista de lista de tests o a donde sea necesario
        return redirect('list_tests')  # Ajusta el nombre de la vista según tu proyecto
    
    # Renderizar el formulario de nuevo si no es válido o si la petición no es POST
    return render(request, 'tes/update.html', {'formulario': formulario})

# Eliminar un test
def delete_test(request, id):
    test = get_object_or_404(Test, id=id)
    if request.method == 'POST':
        test.delete()
        return redirect('list_tests')
    return render(request, 'tes/delete.html', {'test': test})

def create_test_question(request):
    if request.method == 'POST':
        form = TestQuestionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('test_questions/list_test_questions')
    else:
        form = TestQuestionForm()
    return render(request, 'test_questions/create.html', {'form': form})

def list_test_questions(request):
    test_questions = TestQuestion.objects.all()
    return render(request, 'test_questions/index.html', {'test_questions': test_questions})

def update_test_question(request, pk):
    test_question = TestQuestion.objects.get(pk=pk)
    if request.method == 'POST':
        form = TestQuestionForm(request.POST, instance=test_question)
        if form.is_valid():
            form.save()
            return redirect('list_test_questions')
    else:
        form = TestQuestionForm(instance=test_question)
    return render(request, 'test_questions/update.html', {'form': form})

def delete_test_question(request, pk):
    test_question = TestQuestion.objects.get(pk=pk)
    if request.method == 'POST':
        test_question.delete()
        return redirect('list_test_questions')
    return render(request, 'test_questions/delete.html', {'test_question': test_question})

def create_exam_result(request):
    if request.method == 'POST':
        form = ExamResultForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_exam_results')
    else:
        form = ExamResultForm()
    return render(request, 'exam_results/index.html', {'form': form})

def list_exam_results(request):
    exam_results = ExamResult.objects.all()
    return render(request, 'exam_results/index.html', {'exam_results': exam_results})

def update_exam_result(request, pk):
    exam_result = ExamResult.objects.get(pk=pk)
    if request.method == 'POST':
        form = ExamResultForm(request.POST, instance=exam_result)
        if form.is_valid():
            form.save()
            return redirect('list_exam_results')
    else:
        form = ExamResultForm(instance=exam_result)
    return render(request, 'exam_results/update.html', {'form': form})

def delete_exam_result(request, pk):
    exam_result = ExamResult.objects.get(pk=pk)
    if request.method == 'POST':
        exam_result.delete()
        return redirect('list_exam_results')
    return render(request, 'exam_results/delete.html', {'exam_result': exam_result})

def create_professor_subject(request):
    if request.method == 'POST':
        form = ProfessorSubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_professor_subjects')
    else:
        form = ProfessorSubjectForm()
    return render(request, 'professor_subjects/create.html', {'form': form})

def list_professor_subjects(request):
    professor_subjects = ProfessorSubject.objects.all()
    return render(request, 'professor_subjects/index.html', {'professor_subjects': professor_subjects})

def update_professor_subject(request, pk):
    professor_subject = ProfessorSubject.objects.get(pk=pk)
    if request.method == 'POST':
        form = ProfessorSubjectForm(request.POST, instance=professor_subject)
        if form.is_valid():
            form.save()
            return redirect('list_professor_subjects')
    else:
        form = ProfessorSubjectForm(instance=professor_subject)
    return render(request, 'professor_subjects/update.html', {'form': form})

def delete_professor_subject(request, pk):
    professor_subject = ProfessorSubject.objects.get(pk=pk)
    if request.method == 'POST':
        professor_subject.delete()
        return redirect('list_professor_subjects')
    return render(request, 'professor_subjects/delete.html', {'professor_subject': professor_subject})


def take_exam(request, test_id):
    test = get_object_or_404(Test, id=test_id)

    # Verificar si es el momento de iniciar el examen
    current_time = timezone.now()
    exam_start_time = timezone.make_aware(datetime.combine(test.testDate, test.tesTimI))
    
    if current_time < exam_start_time:
        return render(request, 'exams/exam_not_started.html', {'test': test})

    # Verificar si quedan intentos
    
    if test.Attempts <= 0:
        return render(request, 'tes/viewTes.html', {'test': test})

    # Inicializar variables
    num_questions = test.numQuestions
    time_per_question = 95  # Tiempo por pregunta en segundos
    total_time = num_questions * time_per_question  # Total en segundos

    if  'exam_started' in request.session and request.session['exam_started'] == test_id:
        # Recuperar el tiempo restante
        remaining_time = request.session.get('remaining_time', total_time)
        
        # Comprobar si el tiempo ya se ha agotado
        if remaining_time > 0:
            # Convertir last_check de string a datetime
            last_check_str = request.session.get('last_check')
            if last_check_str:
                last_check = timezone.datetime.fromisoformat(last_check_str)
                elapsed_time = (current_time - last_check).total_seconds()
                remaining_time -= elapsed_time
                remaining_time = max(remaining_time, 0)  # No permitir que el tiempo sea negativo

                # Guardar el tiempo restante y la última comprobación
                request.session['remaining_time'] = remaining_time
                request.session['last_check'] = current_time.isoformat()
            else:
                request.session['last_check'] = current_time.isoformat()  # Inicializar last_check si no está en la sesión
        else:
            # El tiempo se ha agotado
            return render(request, 'exams/result.html', {'test': test})
    
    else:
        # Si no hay un examen en curso, inicializar el tiempo y guardar en la sesión
        request.session['exam_started'] = test_id
        request.session['remaining_time'] = total_time
        request.session['last_check'] = current_time.isoformat()  # Guardar como string ISO

    if request.method == 'POST':
        results = {}
        correct_answers = 0
        total_questions = 0

        for key, value in request.POST.items():
            if key.startswith('question_'):
                question_id = key.split('_')[1]
                question = get_object_or_404(Question, id=question_id)

                results[question_id] = value if value else 'No respondida'
                total_questions += 1

                # Obtener las opciones y la respuesta correcta
                options = question.options.split(',')
                correct_index = int(question.correctOption)  # Suponiendo que es el índice de la respuesta correcta
                correct_answer = options[correct_index].strip()
                print("Respuesta correcta -----------", correct_answer)
                #value = "b,c"
                print("Respuesta del usuario -----------", value)

                # Comparar la respuesta seleccionada con la correcta
                if value and value.strip() == correct_answer:
                    correct_answers += 1

        # Calcular el puntaje y verificar si se aprobó
        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        passed = score >= 60
        print("Score -----------", score)

        # Guardar el resultado del examen
        ExamResult.objects.create(
            test=test,
            score=score,
            answers=','.join([str(v) for v in results.values()]),
            passed=passed,
            fecha=timezone.now()
        )

        # Decrementar el número de intentos
        test.Attempts -= 1
        test.save()  # Asegúrate de guardar los cambios en el modelo

        # Limpiar la sesión
        del request.session['exam_started']
        del request.session['remaining_time']
        del request.session['last_check']
        del request.session['questions']  # Limpiar preguntas de la sesión

        return redirect('result', test_id=test.id)

    # Si es una solicitud GET, verificar si ya tenemos preguntas en la sesión
    if 'questions' in request.session:
        questions = request.session['questions']
    else:
        # Obtener las preguntas del test
        test_questions = TestQuestion.objects.filter(test=test)[:num_questions]
        questions = []
        for test_question in test_questions:
            question = test_question.question
            options = question.options.split(',')
            questions.append({
                'id': question.id,
                'question': question.question,
                'options': options,
                'user_answer': request.session.get('answers', {}).get(str(question.id), '')  # Cargar respuesta del usuario
            })

        additional_questions_needed = num_questions - len(questions)
        if additional_questions_needed > 0:
            extra_questions = Question.objects.exclude(id__in=[q['id'] for q in questions]).order_by('?')[:additional_questions_needed]
            for question in extra_questions:
                options = question.options.split(',')
                questions.append({
                    'id': question.id,
                    'question': question.question,
                    'options': options,
                    'user_answer': request.session.get('answers', {}).get(str(question.id), '')  # Cargar respuesta del usuario
                })

        # Guardar las preguntas en la sesión
        request.session['questions'] = questions

    # Guardar las respuestas del usuario en la sesión
    request.session['answers'] = {q['id']: q['user_answer'] for q in questions}

    context = {
        'test': test,
        'questions': questions,
        'total_time': request.session.get('remaining_time', total_time),  # Pasar tiempo restante a la plantilla
        'num_questions': num_questions,
        'remaining_time': request.session.get('remaining_time', total_time) , # Pasar tiempo restante a la plantilla
        'user': request.user,
    }
    return render(request, 'exams/take_exam.html', context)
#colocar el filtro
#pdf
# Función para convertir el HTML en PDF
def render_to_pdf(request, context):
    # Obtener el usuario logueado
    user = request.user
    
    # Obtener el estudiante correspondiente al usuario logueado
    student = get_object_or_404(Student, user=user)
    
    # Obtener las pruebas realizadas por el usuario
    exam_results = ExamResult.objects.filter(user=user)
    
    # Crear el response para el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_{user.username}.pdf"'
    
    # Crear el PDF
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    
    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 100, "Reporte de Exámenes")
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 120, f"Usuario: {user.username}")
    p.drawString(100, height - 140, f"Carrera: {student.career}")
    p.drawString(100, height - 160, f"Curso: {student.course}")

    # Columnas de la tabla
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, height - 200, "ID")
    p.drawString(150, height - 200, "Fecha")
    p.drawString(250, height - 200, "Prueba")
    p.drawString(350, height - 200, "Puntaje")
    p.drawString(450, height - 200, "Aprobado")

    # Listado de resultados de exámenes
    p.setFont("Helvetica", 10)
    y_position = height - 220
    
    for exam in exam_results:
        p.drawString(100, y_position, str(exam.id))
        p.drawString(150, y_position, exam.fecha.strftime('%Y-%m-%d'))
        p.drawString(250, y_position, str(exam.test))  # Supone que test tiene un método __str__
        p.drawString(350, y_position, f"{exam.score}")
        p.drawString(450, y_position, "Sí" if exam.passed else "No")
        y_position -= 20
        
        # Salto de página si el espacio es insuficiente
        if y_position < 100:
            p.showPage()
            y_position = height - 100

    # Guardar el PDF
    p.save()
    

    return response

# Vista para los resultados de exámenes de los estudiantes
def exam_Student(request):
    # Obtener todos los resultados de los exámenes
    exam_results = ExamResult.objects.all()
    user = request.user
    for result in exam_results:
        print(result)  # Verifica los datos del objeto
        print(result.score) 
    # Calcular la media y la mediana de los puntajes
    scores = [result.score for result in exam_results]
    print(f"Scores: {scores}")

    if scores:
        average_score = sum(scores) / len(scores)
        sorted_scores = sorted(scores)
        if len(scores) % 2 != 0:
            median_score = sorted_scores[len(scores) // 2]
        else:
            median_score = (sorted_scores[len(scores) // 2 - 1] + sorted_scores[len(scores) // 2]) / 2
    else:
        average_score = 0
        median_score = 0

    # Calcular el total de aprobados y no aprobados
    total_passed = sum(1 for result in exam_results if result.score >= 80)  # Cambiar a score >= 80
    total_failed = len(exam_results) - total_passed

    # Calcular el puntaje más alto y el más bajo
    max_score = max(scores) if scores else 0
    min_score = min(scores) if scores else 0

    total_exams = ExamResult.objects.count()
    total_students = Student.objects.count()
    total_courses = Course.objects.count()
    total_results = ExamResult.objects.values('id').count()

    # Contexto que se enviará a la plantilla
    context = {
        'exam_results': exam_results,
        'average_score': average_score,
        'median_score': median_score,
        'total_passed': total_passed,  # Cambiar a total_passed
        'total_failed': total_failed,
        'max_score': max_score,
        'min_score': min_score,
        'total_exams': total_exams,
        'total_students': total_students,
        'total_courses': total_courses,
        'total_results': total_results,
        'username': user.username,
        'rol': 'Estudiante',
        'user': request.user,
    }

    # Verificar si se ha solicitado la generación de PDF
    if request.GET.get("generate_pdf"):
        return render_to_pdf(request, context)


    # Si no, simplemente renderizamos el HTML
    return render(request, 'exam_results/resultStu.html', context)

def exam_result(request, test_id):
    # Obtén el test correspondiente
    test = get_object_or_404(Test, id=test_id)
    
    # Filtra todos los resultados del examen para el test seleccionado
    results = ExamResult.objects.filter(test=test)
    
    if results.exists():
        # Si hay resultados, los mostramos en la plantilla
        context = {'results': results, 'test': test}
        return render(request, 'exams/result.html', context)
    else:
        # Si no hay resultados, puedes mostrar un mensaje o manejarlo de otra forma
        return render(request, 'exams/no_results.html', {'test': test,'user': request.user,})
       
class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    def is_expired(self):
        expiration_time = self.created_at + timedelta(minutes=10)  # 10 minutos de validez
        return timezone.now() > expiration_time


from django.contrib.auth.models import Group

def RegisterView(request):
    user = request.user
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        group_id = request.POST.get('group')  # Obtén el grupo seleccionado
        career_id = request.POST['career']
        semester = request.POST['semester']
        course_id = request.POST['course']
        
        

        user_data_has_error = False
        career = Career.objects.get(id=career_id)
        course = Course.objects.get(id=course_id)

        

        if User.objects.filter(username=username).exists():
            user_data_has_error = True
            messages.error(request, 'El nombre de usuario ya existe')

        if User.objects.filter(email=email).exists():
            user_data_has_error = True
            messages.error(request, 'El correo electrónico ya existe')
            
        if not email.endswith('@ucundinamarca.edu.co'):
            user_data_has_error = True
            messages.error(request, 'El correo electrónico debe tener el dominio @ucundinamarca.edu.co.')

        if len(password) < 8:
            user_data_has_error = True
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')

        if not user_data_has_error:
            # Crear el usuario inactivo
            new_user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
                is_active=False  # Usuario inactivo hasta que verifique su correo
            )
            # Crear el registro en el modelo Student
            student = Student.objects.create(
                user=new_user,
                career=career,
                course=course
            )
        
            
            # Asignar el grupo al usuario
            try:
                group = Group.objects.get(id=group_id)
                new_user.groups.add(group)
            except Group.DoesNotExist:
                messages.error(request, 'Grupo no válido seleccionado.')
                return render(request, 'login/register.html', {'groups': Group.objects.all()})
                
        

            # Crear y guardar el código de verificación
            verification_code = str(random.randint(100000, 999999))
            EmailVerification.objects.create(user=new_user, verification_code=verification_code)

            # Enviar el correo con el código de verificación
            email_subject = 'Verificacion de Correo electronico'
            email_body = f'Tu codigo de verificacion es: {verification_code}'
            email_message = EmailMessage(email_subject, email_body, settings.EMAIL_HOST_USER, [email])
            email_message.send()

            messages.success(request, 'Código de verificación enviado. Revisa tu correo electrónico.')
            return redirect('verify-email', user_id=new_user.id, tipo='register')
        
    if user.groups.filter(name='Asesor').exists():
        persona='Profesor'  # Redirige a la vista de 'Asesor'

    # En caso de que no sea POST o haya un error, renderizar de nuevo la página de registro
    groups = Group.objects.all()
    careers = Career.objects.all() 
    courses = Course.objects.all() 
    context = {
            'groups': groups,
            'careers': careers,
            'courses': courses,
            'username': user.username,
            'rol': 'Asesor',
            'persona': persona,
        }
    
    if user.groups.filter(name='Asesor').exists():
        persona='Profesor'  # Redirige a la vista de 'Asesor'
        return render(request, 'login/register.html', context)
    else:
        return render(request, 'login/register.html', context)


def VerifyEmailView(request, user_id, tipo):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == "POST":
        verification_code = request.POST.get('verification_code')
        try:
            # Busca el registro de verificación correspondiente
            verification_record = EmailVerification.objects.get(user=user, verification_code=verification_code)
            
            # Verifica si el código ha expirado
            if verification_record.is_expired():
                messages.error(request, 'El código de verificación ha expirado.')
                return redirect('register')

            # Activa el usuario y elimina el registro de verificación
            user.is_active = True
            user.save()
            verification_record.delete()

            messages.success(request, 'Correo electrónico verificado exitosamente.')

            # Dependiendo del tipo, redirigir al lugar correcto
            if tipo == 'acceso':
                # Autenticar y redirigir a la página principal
                auth_login(request, user)
                return redirect('home')
            else:
                # Redirigir al login en caso de que no sea acceso
                return redirect('login')

        except EmailVerification.DoesNotExist:
            messages.error(request, 'Código inválido.')

    return render(request, 'login/verify_email.html', {'user_id': user_id})


def LoginView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        userE = User.objects.filter(username=username, password=password)

        # Autenticar al usuario
        user = authenticate(request, username=username, password=password)

        if userE is not None:
            if user is not None:
                if user.groups.exists():  # Verifica si el usuario pertenece a algún grupo
            # Verificar si el usuario tiene un correo asociado
                    if user.groups.filter(name='Administrador'):
                        auth_login(request, user)
                        return redirect('home')
                    else:
                        email = user.email
                        if email:
                            # Generar código de verificación
                            verification_code = str(random.randint(100000, 999999))
                            
                            # Crear registro de verificación
                            EmailVerification.objects.create(user=user, verification_code=verification_code)

                            # Enviar el correo con el código de verificación
                            email_subject = 'Código de acceso'
                            email_body = f'Tu código de Acceso es: {verification_code}'
                            email_message = EmailMessage(email_subject, email_body, settings.EMAIL_HOST_USER, [email])
                            email_message.send()

                            messages.success(request, 'Código de Acceso enviado. Revisa tu correo electrónico.')
                            return redirect('verify-email', user_id=user.id, tipo='acceso')
                        else:
                            messages.error(request, 'El usuario no tiene un correo electrónico asociado.')
                            return redirect('login')
                else:
                    messages.error(request, 'El usuario no está asociado a un grupo.')
                    messages.error(request, 'Comunicate con tu docente.')
                    return redirect('login')   
            else: 
                messages.error(request, 'El usuario no esta activado ni asociado a grupo.')
                return redirect('login')   
            
        else:
            messages.error(request, 'Usuario no existe')
            return redirect('register')

    return render(request, 'login/login.html')


def LogoutView(request):
    
    # Cierra la sesión
    logout(request)

    # Redirige a la página de inicio de sesión
    return redirect('login')

def ForgotPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)

            new_password_reset = PasswordReset(user=user)
            new_password_reset.save()

            password_reset_url = reverse('reset-password', kwargs={'reset_id': new_password_reset.reset_id})

            full_password_reset_url = f'{request.scheme}://{request.get_host()}{password_reset_url}'
            
            email_body = f'Reset your password using the link below:\n\n\n{full_password_reset_url}'

            email_message = EmailMessage(
                'Reset your password',  # Email subject
                email_body,
                settings.EMAIL_HOST_USER,  # Email sender
                [email]  # Email receiver
            )

            email_message.fail_silently = True
            email_message.send()

            # Redirige pasando el reset_id como argumento
            return redirect('password-reset-sent', reset_id=new_password_reset.reset_id)

        except User.DoesNotExist:
            messages.error(request, f"No user with email '{email}' found")
            return redirect('forgot-password')
        
    return render(request, 'login/forgot_password.html')


def PasswordResetSent(request, reset_id):

    if PasswordReset.objects.filter(reset_id=reset_id).exists():
        return render(request, 'password_reset_sent.html')
    else:
        # redirect to forgot password page if code does not exist
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')

def ResetPassword(request, reset_id):
    try:
        # Buscar la instancia de PasswordReset utilizando reset_id
        password_reset_instance = PasswordReset.objects.get(reset_id=reset_id)
        
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            passwords_have_error = False

            if password != confirm_password:
                passwords_have_error = True
                messages.error(request, 'Passwords do not match')

            if len(password) < 5:
                passwords_have_error = True
                messages.error(request, 'Password must be at least 5 characters long')

            expiration_time = password_reset_instance.created_when + timezone.timedelta(minutes=10)

            if timezone.now() > expiration_time:
                # Eliminar el reset_id si ha expirado
                password_reset_instance.delete()
                passwords_have_error = True
                messages.error(request, 'Reset link has expired')
            
            # Reiniciar la contraseña
            if not passwords_have_error:
                user = password_reset_instance.user
                user.set_password(password)
                user.save()
                
                # Eliminar el reset_id después de usarlo
                password_reset_instance.delete()

                # Redirigir a la página de inicio de sesión
                messages.success(request, 'Password reset. Proceed to login')
                return redirect('login')

            else:
                # Redirigir de nuevo a la página de restablecimiento de contraseña y mostrar errores
                return redirect('reset-password', reset_id=reset_id)
            
    except PasswordReset.DoesNotExist:
        # Redirigir a la página de "Forgot Password" si el código no existe
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')

    return render(request, 'login/reset_password.html')