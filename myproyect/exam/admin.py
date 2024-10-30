from django.contrib import admin
from .models import *

admin.site.register(Role)
admin.site.register(Asignature)
admin.site.register(Course)
admin.site.register(Student)
admin.site.register(Career)
admin.site.register(Material)
admin.site.register(Question)
admin.site.register(QuestionMaterial)
admin.site.register(Test)
admin.site.register(TestQuestion)
admin.site.register(ExamResult)
admin.site.register(ProfessorSubject)
admin.site.register(CustomUser)

