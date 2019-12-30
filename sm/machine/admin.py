from django.contrib import admin
from . import models

# Register your models here.
@admin.register(
    models.Routine,
    models.Flow,
    models.Task,
    models.Weight,
    models.TaskResult,
    models.TaskConnection,
    )
class DefaultAdmin(admin.ModelAdmin):
    pass
