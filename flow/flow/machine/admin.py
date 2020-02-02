from django.contrib import admin
from . import models

# Register your models here.
@admin.register(
    models.Routine,
    models.Weight,
    models.TaskResult,
    models.TaskConnection,
    )
class DefaultAdmin(admin.ModelAdmin):
    pass


@admin.register(
    models.TaskError,
    )
class TaskErrorAdmin(admin.ModelAdmin):
    list_display = (
            'task_id',
            'task_key',
            'result',
        )


@admin.register(
    models.Flow
    )
class FlowAdmin(admin.ModelAdmin):
    list_display = (
        'routine',
        'state',
        'complete',
        'position',
        'spawn_count',
        'stores_count',
        'owner',
        )

    def spawn_count(self, model):
        return model.spawn.count()

    def stores_count(self, model):
        names = ',\n'.join(model.stores.values_list('key', flat=True))
        return f'{model.stores.count()} - {names}'


@admin.register(
    models.Task
    )
class FlowAdmin(admin.ModelAdmin):
    list_display = (
        'key',
        'name',
        'script',
        )
