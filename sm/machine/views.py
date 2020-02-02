from datetime import datetime, timedelta
from django.shortcuts import render
from django.views.generic import TemplateView, ListView, CreateView, FormView
from django.views.generic import DetailView

from . import models
from . import forms

print('require func')
# from machine.conf import no_patch;no_patch()
# from machine import main

from machine import main

class MachineIndexView(TemplateView):
    template_name = 'machine/index.html'


class FlowListView(ListView):
    model = models.Flow


class FlowCreateView(CreateView):
    model = models.Flow
    fields = ('routine',)
    success_url = '/machine/flows/'
    initial = {
        'state': 'INIT'
    }

class ComplexFlowCreateView(FormView):
    form_class = forms.FlowForm
    template_name = 'machine/flow_form.html'
    success_url = '/machine/flows/'

    def form_valid(self, form):
        data = form.cleaned_data

        flow = models.Flow(
            routine=data['routine'],
            state='INIT',
            )
        flow.save()

        if data['start'] is True:

            kw = {}
            print('Starting flow', flow.pk)
            res = main.run_flow(flow.pk, **kw)

            print('Start res', res)
        return super().form_valid(form)


class RunFlowFormView(FormView):
    form_class = forms.RunFlowForm
    template_name = 'machine/flow_form.html'
    success_url = '/machine/flows/'

    def form_valid(self, form):
        data = form.cleaned_data
        flow = data['flow']
        print('Starting flow', flow.pk)
        res = main.submit_flow(flow.pk)
        print('Start res', res)
        return super().form_valid(form)


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
