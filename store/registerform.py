from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):

    username = forms.CharField(
        label="帳號",
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'margin-top: 10px; margin-bottom: 10px;'})
    )
    first_name = forms.CharField(
        label="姓名",
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'margin-top: 10px; margin-bottom: 10px;'})
    )
    email = forms.EmailField(
        label="電子郵件",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'style': 'margin-top: 10px; margin-bottom: 10px;'})
    )
    password1 = forms.CharField(
        label="密碼",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'style': 'margin-top: 10px; margin-bottom: 10px;'})
    )
    password2 = forms.CharField(
        label="密碼確認",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'style': 'margin-top: 10px; margin-bottom: 10px;'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'password1', 'password2')