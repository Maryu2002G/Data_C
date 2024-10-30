from django import forms
from .models import Role, User,QuestionMaterial, Asignature, TestQuestion, Course, Career, Material, Question, Test, ExamResult, ProfessorSubject, Student

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = '__all__'

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['rol'].queryset = Role.objects.all()  
        self.fields['rol'].empty_label = "Seleccionar"  

class AsignatureForm(forms.ModelForm):
    class Meta:
        model = Asignature
        fields = '__all__'




class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra el queryset de 'profesor' para incluir solo usuarios en el grupo 'Profesor'
        self.fields['profesor'].queryset = User.objects.filter(groups__name='Profesor')




class CareerForm(forms.ModelForm):
    class Meta:
        model = Career
        fields = '__all__'

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = '__all__'

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Obtener el usuario logueado
        super(TestForm, self).__init__(*args, **kwargs)

        # Filtrar cursos donde el profesor es el usuario logueado
        if user:
            self.fields['course'].queryset = Course.objects.filter(profesor=user)
        else:
            self.fields['course'].queryset = Course.objects.none()  # Ninguna opción si no hay usuario

      
class ExamResultForm(forms.ModelForm):
    class Meta:
        model = ExamResult
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super(ExamResultForm, self).__init__(*args, **kwargs)
        # Configurar queryset de Test para usar en el campo select
        self.fields['test'].queryset = Test.objects.all()
        self.fields['test'].empty_label = "Seleccionar Test"

class ProfessorSubjectForm(forms.ModelForm):
    class Meta:
        model = ProfessorSubject
        fields = '__all__'

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        
        # Campo 'user' (anteriormente llamado 'idUser')
        if 'user' in self.fields:
            self.fields['user'].queryset = User.objects.all()
            self.fields['user'].empty_label = "Seleccionar usuario"
        
        # Campo 'course' (anteriormente llamado 'idCourse')
        if 'course' in self.fields:
            self.fields['course'].queryset = Course.objects.all()
            self.fields['course'].empty_label = "Seleccionar curso"
        
        # Campo 'career' (anteriormente llamado 'idCareer')
        if 'career' in self.fields:
            self.fields['career'].queryset = Career.objects.all()
            self.fields['career'].empty_label = "Seleccionar carrera"
class QuestionMaterialForm(forms.ModelForm):
    class Meta:
        model = QuestionMaterial
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(QuestionMaterialForm, self).__init__(*args, **kwargs)
        
        # Campo 'question' (relacionado con el modelo Question)
        if 'question' in self.fields:
            self.fields['question'].queryset = Question.objects.all()
            self.fields['question'].empty_label = "Seleccionar pregunta"
        
        # Campo 'material' (relacionado con el modelo Material)
        if 'material' in self.fields:
            self.fields['material'].queryset = Material.objects.all()
            self.fields['material'].empty_label = "Seleccionar material"
            
   
        

class TestQuestionForm(forms.ModelForm):
    class Meta:
        model = TestQuestion
        fields = '__all__'
        
        
