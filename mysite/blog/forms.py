from django import forms

class EmailPostForm(forms.form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()