from datetime import datetime, timedelta
from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from . import models


class FlowListView(ListView):
    model = models.Flow
