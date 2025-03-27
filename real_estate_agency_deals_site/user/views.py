from django.views.generic import CreateView, FormView, DetailView, UpdateView, ListView
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ObjectDoesNotExist
from real_estate_agency_deals_site import settings
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from user.models import ConfirmationCode
from django.core.mail import send_mail
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.views import View
from user import models
from user import forms


class SignupView(CreateView):
    form_class = forms.MyUserCreationForm
    template_name = 'user/signup.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context: dict = {
            'title': 'Регистрация',
        }

        return {**base_context, **context}

    def form_valid(self, form):
        new_user = form.save()
        new_user.set_password(form.cleaned_data['password1'])
        new_user.save()

        code_email_confirmation = models.ConfirmationCode(
            user=new_user,
            type=models.ConfirmationCode.ConfirmationCodeType.EMAIL_CONFIRMATION,
        )
        code_email_confirmation.save()

        subject = 'Подтверждение электронной почты'
        confirmation_link = f'{settings.MAIN_HOST}{reverse('email_confirmation')}?code={code_email_confirmation.code}'
        message = (f'Подтвердите свою почту, чтобы получить все функции сайта.\n'
                   f'Ссылка: {confirmation_link}')

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [new_user.email],
            fail_silently=False,
        )
        messages.success(self.request, 'Успешное создание учетной записи')

        return redirect('email_confirmation', permanent=False)


class EmailConfirmationView(View):
    template_name = 'user/email_confirmation.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context: dict = {
            'title': 'Подтверждение почты',
        }

        return context

    def get(self, request, *args, **kwargs):
        code = request.GET.get('code')

        if code:
            try:
                confirmation_code = ConfirmationCode.objects.get(
                    code=code,
                    type=models.ConfirmationCode.ConfirmationCodeType.EMAIL_CONFIRMATION
                )
                confirmation_code.user.verification_email = True
                confirmation_code.user.save()
                confirmation_code.delete()
                messages.success(request, 'Ваша почта подтверждена')
                return redirect('home', permanent=False)
            except ObjectDoesNotExist:
               messages.error(request, 'Ошибка кода подтверждения')

        return render(request, self.template_name, context=self.get_context_data())


class MyLoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'user/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context: dict = {
            'title': 'Вход',
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Вы уже авторизованы')
            return redirect('home', permanent=False)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user: models.User = form.get_user()

        if user.banned:
            messages.error(self.request, 'Учетная запись заблокирована часть функций не доступно.\n'
                                         'Вы можете подать на апелляцию нажмите на "..." в шапке сайта '
                                         'после, чего "подать апелляцию".')

        if not user.verification_email:
            messages.error(self.request, 'Вы не можете войти в учетную запись пока не подтвердите почту')
            return redirect('login', permanent=False)

        # info! Если пользователь отключил учетную запись в нее больше не возможно войти

        login(request=self.request, user=user)
        messages.success(self.request, 'Успешный  вход')
        return super().form_valid(form)


class CreateRestorePasswordView(FormView):
    form_class = forms.CreateResetTokenForm
    template_name = 'user/create_reset.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context: dict = {
            'title': 'Подтверждение для восстановления пароля',
        }

        return {**base_context, **context}

    def form_valid(self, form):
        who_restore_pass = form

        if who_restore_pass.is_valid():
            try:
                user_reset = models.User.objects.get(
                    username=who_restore_pass.cleaned_data['username'],
                    email=who_restore_pass.cleaned_data['email'],
                )
                reset_code = models.ConfirmationCode.objects.create(
                    user=user_reset,
                    type=models.ConfirmationCode.ConfirmationCodeType.PASSWORD_RESTORE,
                    validity_time=timezone.timedelta(hours=24),
                )
                reset_code.save()

                subject = 'Сброс пароля'
                confirmation_link = f'{settings.MAIN_HOST}{reverse('restore_confirmation', 
                                                                   args=(reset_code.code,))}'
                message = (f'Для сброса пароля перейдите по ссылке ниже.\n'
                           f'Ссылка: {confirmation_link}')

                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [user_reset.email],
                    fail_silently=False,
                )

                return redirect('restore_info', permanent=False)
            except ObjectDoesNotExist:
                messages.error(self.request, 'Ошибка переданных данных')

        return redirect('create_restore_password', permanent=False)


class RestoreInfoView(View):
    template_name = 'user/restore_info.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context: dict = {
            'title': 'Информация восстановления пароля',
        }

        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, context=self.get_context_data())


class RestorePasswordView(FormView):
    form_class = forms.ResetPasswordForm
    template_name = 'user/restore_password.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context: dict = {
            'title': 'Подтверждение для восстановления пароля',
        }

        return {**base_context, **context}

    def form_valid(self, form):
        new_pass = form

        try:
            code_reset = models.ConfirmationCode.objects.get(
                code=self.kwargs.get('code'),
                type=models.ConfirmationCode.ConfirmationCodeType.PASSWORD_RESTORE,
            )
        except ObjectDoesNotExist:
            messages.error(self.request, 'Ошибка кода подтверждения')
            return redirect('restore_info', permanent=False)

        if code_reset.date_created + code_reset.validity_time < timezone.now():
            messages.error(self.request, 'Ошибка срок действия кода истек, код будет удален')
            code_reset.delete()
            return redirect('restore_info', permanent=False)

        if new_pass.is_valid():
            user_reset: models.User = code_reset.user
            user_reset.set_password(new_pass.cleaned_data['new_password'])
            user_reset.save()

            messages.success(self.request, 'Пароль был изменен')
            return redirect('login', permanent=False)


        return redirect('create_restore_password', (self.kwargs.get('code'),), permanent=False)


class ProfileUserView(DetailView):
    model = models.User
    template_name = 'user/profile_user.html'
    context_object_name = 'user_profile'
    slug_url_kwarg = 'username'

    def get_context_data(self, *, object_list=None, **kwargs):
        base_context = super().get_context_data(**kwargs)
        profile_user = self.get_object()

        context = {
            'im_in_bl': models.BlackList.objects.filter(
                whose_BL=profile_user,
                who_on_BL=self.request.user,
            ).exists() if (self.request.user.username != self.kwargs.get('username')
                           and self.request.user.is_authenticated) else None,
            'this_user_in_bl': models.BlackList.objects.filter(
                whose_BL=self.request.user,
                who_on_BL=profile_user,
            ).exists() if (self.request.user.username != self.kwargs.get('username')
                           and self.request.user.is_authenticated) else None,
            'title': f'Профиль @{self.kwargs.get('username')}',
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        profile = self.get_object()

        if isinstance(profile, HttpResponseRedirect):
            return profile

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        try:
            object_user = models.User.objects.get(username=self.kwargs.get('username'))
        except ObjectDoesNotExist:
            messages.error(self.request, 'Пользователь не найден')
            return redirect('home', permanent=False)

        return object_user


class ChangeProfileUserView(UpdateView):
    model = models.User
    form_class = forms.ChangeUserProfileForm
    template_name = 'user/profile_user_change.html'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': 'Изменить свой профиль',
        }

        return {**base_context, **context}


    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.warning(self.request, 'Чтобы изменить профиль необходимо авторизоваться')
            return redirect('login', permanent=False)

        user_profile = self.get_object()

        if isinstance(user_profile, HttpResponseRedirect):
            return user_profile

        if user_profile != self.request.user:
            messages.error(self.request, 'У вас нет доступа к этому профилю')
            return redirect('home', permanent=False)

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        try:
            user_profile = models.User.objects.get(username=self.kwargs.get('username'))
        except ObjectDoesNotExist:
            messages.error(self.request, 'Пользователь не найден')
            return redirect('home', permanent=False)

        return user_profile

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Успешный  изменение профиля')

        return redirect('user_profile', self.kwargs.get('username'), permanent=False)


class BlackListUserView(ListView):
    paginate_by = 10
    model = models.BlackList
    template_name = 'user/my_black_list.html'
    context_object_name = 'black_list'

    def get_context_data(self, *, object_list=None, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': 'Мой черный список',
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.warning(self.request, 'Авторизуйтесь, чтобы просмотреть свой черный список')
            return redirect('login', permanent=False)

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = models.BlackList.objects.filter(whose_BL=self.request.user)
        return queryset
