from  django import forms
from . import models


class FlowForm(forms.Form):
    """The form fields for the user to complete.
    These values are not applied automtically; views.ServerCreateFormView
    Builds a model upon form_valid.
    """
    routine = forms.ModelChoiceField(
        queryset=models.Routine.objects.all()
        )

    kwargs = forms.CharField(required=False,widget=forms.Textarea(attrs={"rows":5, "cols":20}))
    start = forms.BooleanField(required=False)


class RunFlowForm(forms.Form):
    """The form fields for the user to complete.
    These values are not applied automtically; views.ServerCreateFormView
    Builds a model upon form_valid.
    """
    flow = forms.ModelChoiceField(
        queryset=models.Flow.objects.all()
        )

