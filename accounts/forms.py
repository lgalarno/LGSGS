from django import forms
from django.core.exceptions import ValidationError

from .models import User  #, TraderCredentials


class CustomUserCreationForm(forms.Form):
    username = forms.CharField(label='Enter Username', min_length=3, max_length=150)
    email = forms.EmailField(label='Enter email')
    password1 = forms.CharField(label='Enter password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = User.objects.filter(username=username)
        if r.count():
            raise ValidationError("Username already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        r = User.objects.filter(email=email)
        if r.count():
            raise ValidationError("Email already exists")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Password don't match")

        return password2

    def save(self, commit=True):
        user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['password1']
        )
        return user

#
# class TraderCredentialsForm(forms.Form):
#     class Meta:
#         model = TraderCredentials
#         fields = ['unername', 'password', 'twofa', 'api_key', 'secret']
#         labels = {
#             "api_key": "API key (encrypté)",
#             "secret": "Secret key (encrypté)",
#             "unername": "Nom / email utilisé pour se connecter",
#             "password": "Mot de passe (encrypté)",
#             "twofa": "QR Code of Google 2FA secret (encrypté)",
#         }
#         widgets = {
#             'password': forms.PasswordInput,
#         }
