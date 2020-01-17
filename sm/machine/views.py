from datetime import datetime, timedelta
from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from . import models

from django.views.generic import DetailView


class FlowListView(ListView):
    model = models.Flow


class FlowDetailView(DetailView):
    model = models.Flow
