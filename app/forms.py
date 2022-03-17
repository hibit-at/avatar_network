from django import forms

class Filter(forms.Form):
    word = forms.CharField(required=False)
    free_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'style':'width:20px;height:20px;'}),
        )
    # sort_hot = forms.BooleanField(
    #     required=False,
    #     widget=forms.CheckboxInput(attrs={'style':'width:20px;height:20px;'}),
    #     )