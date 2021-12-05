from django import forms

class Filter(forms.Form):
    word = forms.CharField(required=False)
    free_only = forms.BooleanField(required=False)