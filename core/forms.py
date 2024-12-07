from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(label="Your email", max_length=100)


class UploadFileForm(forms.Form):
    file = forms.FileField()
