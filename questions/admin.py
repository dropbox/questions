from django.contrib import admin
from questions import models

admin.site.register(models.Group)
admin.site.register(models.Question)
admin.site.register(models.QuestionRevision)
