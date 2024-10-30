from django.urls import path
from . import views

from django.conf import settings
from django.contrib.staticfiles.urls import static

urlpatterns = [
    # Inicio
    path('', views.Home, name='home'),
    
    #Rutas de roles
    path('profesor/', views.profesor_view, name='profesor_view'),  # Ruta para la vista de Profesor
    path('asesor/', views.asesor_view, name='asesor_view'),  # Ruta para la vista de Asesor
    path('subasesor/', views.subasesor_view, name='subasesor_view'),  # Ruta para la vista de SubAsesor
    path('estudiante/', views.estudiante_view, name='estudiante_view'),  # Ruta para la vista de estudiante
    
    #login
    path('register/', views.RegisterView, name='register'),
    path('login/', views.LoginView, name='login'),
    path('logout/', views.LogoutView, name='logout'),
    path('forgot-password/', views.ForgotPassword, name='forgot-password'),
    path('password-reset-sent/<str:reset_id>/', views.PasswordResetSent, name='password-reset-sent'),
    path('reset-password/<str:reset_id>/', views.ResetPassword, name='reset-password'),
    path('verify-email/<int:user_id>/<str:tipo>/', views.VerifyEmailView, name='verify-email'),

    # Roles
    path('roles/', views.roles, name='roles'),
    path('roles/create/', views.CreateRole, name='create_role'),
    path('roles/update/', views.UpdateRole, name='update_role'),
    path('roles/update/<int:id>/', views.UpdateRole, name='update_role'),
    path('roles/delete/<int:id>/', views.DeleteRole, name='delete_role'),

    # Users
    path('users/', views.users, name='users'),
    path('activar/', views.activar, name='activar'),
    path('activar/<int:user_id>/', views.activate_user, name='activate_user'),
    path('users/create/', views.RegisterView, name='create_user'),
    path('users/update/', views.UpdateUser, name='update_user'),
    path('users/update/<int:id>/', views.UpdateUser, name='update_user'),
    path('users/delete/<int:id>/', views.DeleteUser, name='delete_user'),

    # Asignaturas
    path('asignatures/', views.asignatures, name='asignature'),
    path('asignatures/create/', views.CreateAsignatures, name='create_asignature'),
    path('asignatures/update/', views.UpdateAsignatures, name='update_asignature'),
    path('asignatures/update/<int:id>/', views.UpdateAsignatures, name='update_asignature'),
    path('asignatures/delete/<int:id>/', views.DeleteAsignatures, name='delete_asignature'),
    

    # Cursos
    path('courses/', views.courses, name='courses'),
    path('courses/<int:course_id>/students/', views.course_students, name='course_students'),  # URL para la lista de estudiantes
    path('courses/create/', views.CreateCourse, name='create_course'),
    path('courses/update/', views.UpdateCourse, name='update_course'),
    path('courses/update/<int:id>/', views.UpdateCourse, name='update_course'),
    path('courses/delete/<int:id>/', views.DeleteCourse, name='delete_course'),
    
    path('profesores/', views.listar_profesores_y_cursos, name='listar_profesores_y_cursos'),

    # Estudiantes
    path('students/', views.students, name='students'),
    path('students/create/', views.CreateStudent, name='create_student'),
    path('students/update/', views.UpdateStudent, name='update_student'),
    path('students/update/<int:id>/', views.UpdateStudent, name='update_student'),
    path('students/delete/<int:id>/', views.DeleteStudent, name='delete_student'),
    path('estudiantes-por-curso/', views.estudiantes_por_curso, name='estudiantes_por_curso'),

    # Carreras
    path('careers/', views.careers, name='careers'),
    path('careers/create/', views.CreateCareers, name='create_career'),
    path('careers/update/', views.UpdateCareers, name='update_career'),
    path('careers/update/<int:id>/', views.UpdateCareers, name='update_career'),
    path('careers/delete/<int:id>/', views.DeleteCareers, name='delete_career'),

    # Materiales
    path('materials/', views.materials, name='materials'),
    path('materials/create/', views.CreateMaterials, name='create_material'),
    path('materials/update/', views.UpdateMaterials, name='update_material'),
    path('materials/update/<int:id>/', views.UpdateMaterials, name='update_material'),
    path('materials/delete/<int:id>/', views.DeleteMaterials, name='delete_material'),

    # Preguntas
    path('questions/', views.questions_view, name='questions'),
    path('questions/create/', views.CreateQuestions, name='create_question'),
    path('questions/update/', views.UpdateQuestions, name='update_question'),
    path('questions/update/<int:id>/', views.UpdateQuestions, name='update_question'),
    path('questions/delete/<int:id>/', views.DeleteQuestions, name='delete_question'),
    
    
    path('questionMat/', views.question_materials_view, name='question_materials'),
    path('questionMat/create/', views.CreateQuestionMaterial, name='create_question_material'),
    path('questionMat/update/', views.UpdateQuestionMaterial, name='update_question_material'),
    path('questionMat/update/<int:id>/', views.UpdateQuestionMaterial, name='update_question_material'),
    path('questionMat/delete/<int:id>/', views.DeleteQuestionMaterial, name='delete_question_material'),

    # Resultados de exámenes
    path('exam_results/', views.exam_results_view, name='exam_results'),
    path('exam_results/create/', views.CreateExamResult, name='create_exam_result'),
    path('exam_results/update/', views.UpdateExamResult, name='update_exam_result'),
    path('exam_results/update/<int:id>/', views.UpdateExamResult, name='update_exam_result'),
    path('exam_results/delete/<int:id>/', views.DeleteExamResult, name='delete_exam_result'),

    # Profesores y Asignaturas
    path('professor_subjects/', views.professor_subjects_view, name='professor_subjects'),
    path('professor_subjects/create/', views.CreateProfessorSubject, name='create_professor_subject'),
    path('professor_subjects/update/', views.UpdateProfessorSubject, name='update_professor_subject'),
    path('professor_subjects/update/<int:id>/', views.UpdateProfessorSubject, name='update_professor_subject'),
    path('professor_subjects/delete/<int:id>/', views.DeleteProfessorSubject, name='delete_professor_subject'),
    
    #tests (exámenes)
    path('tes/', views.list_tests, name='list_tests'),
    #tests (vista estudiante)
    path('tes/viewTes/', views.list_testsStud, name='list_testsStud'), 
 
    path('tes/create/', views.create_test, name='create_test'), 
    path('tes/update/<int:id>/', views.update_test, name='update_test'),
    path('tes/delete/<int:id>/', views.delete_test, name='delete_test'),
    
    # Rutas para TestQuestion
    path('test_questions/', views.list_test_questions, name='test_questions'),
    path('test_questions/create/', views.create_test_question, name='create_test_question'),
    path('test_questions/update/<int:pk>/', views.update_test_question, name='update_test_question'),
    path('test_questions/delete/<int:pk>/', views.delete_test_question, name='delete_test_question'),

 # Rutas para ExamResult
    path('exam_results/', views.list_exam_results, name='exam_results'),
    # Ruta pdf
    #path('exam_results/', views.export_pdf, name='export_pdf'),
    path('exam_results/create/', views.create_exam_result, name='create_exam_result'),
    path('exam_results/resultStu/', views.exam_Student, name='resultStu'),
    path('exam_results/resultStu/', views.render_to_pdf, name='generate_pdf'),
    path('exam_results/update/<int:pk>/', views.update_exam_result, name='update_exam_result'),
    path('exam_results/delete/<int:pk>/', views.delete_exam_result, name='delete_exam_result'),

    # Rutas para ProfessorSubject
    path('professor_subjects/', views.list_professor_subjects, name='professor_subjects'),
    path('professor_subjects/create/', views.create_professor_subject, name='create_professor_subject'),
    path('professor_subjects/update/<int:pk>/', views.update_professor_subject, name='update_professor_subject'),
    path('professor_subjects/delete/<int:pk>/', views.delete_professor_subject, name='delete_professor_subject'),
    
    #examen 
    path('exams/take_exam', views.take_exam, name='take_exam'),
    path('exams/take/<int:test_id>/', views.take_exam, name='take_exam'),
    path('exams/result', views.take_exam, name='result'),
    
    path('exams/result/<int:test_id>/', views.exam_result, name='result'),


]+static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)