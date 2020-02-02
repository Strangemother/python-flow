from datetime import datetime, timedelta
from django.shortcuts import render
from django.views.generic import TemplateView, ListView, CreateView
from . import models

from django.views.generic import DetailView

class MachineIndexView(TemplateView):
    template_name = 'machine/index.html'


class FlowListView(ListView):
    model = models.Flow


class FlowDetailView(DetailView):
    model = models.Flow


class RoutineListView(ListView):
    model = models.Routine


class RoutineDetailView(DetailView):
    model = models.Routine


class TaskCreateView(CreateView):
    model = models.Task
    fields = '__all__'
    success_url = '/machine/tasks/'

class TaskListView(ListView):
    model = models.Task


class TaskDetailView(DetailView):
    model = models.Task
