from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(label="Your email", max_length=100)
