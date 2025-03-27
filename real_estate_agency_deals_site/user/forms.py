from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator, MinLengthValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _
from django.utils import timezone
from datetime import timedelta
from user.models import User
from django import forms


class MyUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = User
        fields = ('username', 'email', 'password1', 'password2',)

    username = forms.CharField(
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]+$',
                message='Допускаются только латиница, цифры и нижнее подчеркивание'
            ),
        ],
        min_length=3,
        max_length=150,
        required=True,
        label='Логин'
    )


class CreateResetTokenForm(forms.Form):
    username = forms.CharField(
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]+$',
                message='Допускаются только латиница, цифры и нижнее подчеркивание'
            ),
        ],
        min_length=3,
        max_length=150,
        required=True,
        label='Логин'
    )
    email = forms.EmailField(label='Почта учетной записи')


class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        label='Новый пароль'
    )
    new_password_confirmation = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        label='Старый пароль'
    )

    def clean_new_password(self):
        password = self.cleaned_data.get('new_password')
        try:
            validate_password(password)
        except forms.ValidationError as err:
            raise forms.ValidationError(err)

        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password")
        password2 = cleaned_data.get("new_password_confirmation")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_('Пароль не совпадает с подтверждением'))

        return cleaned_data


class ChangeUserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'patronymic', 'photo', 'view_email', 'phone', 'about',)
