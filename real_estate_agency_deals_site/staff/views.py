from django.views.generic import CreateView, UpdateView, ListView
from django.core.exceptions import ObjectDoesNotExist
from real_estate_agency_deals_site import settings
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from user import models as user_models
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Q
from staff import models
from staff import forms


class NewComplaint(CreateView):
    form_class = None
    template_name = 'staff/new_complaint.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context: dict = {
            'title': 'Написать жалобу',
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            self.form_class = forms.NewComplaintAuthUserForm
        else:
            self.form_class = forms.NewComplaintForm

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        new_complaint = form.save(commit=False)

        if self.request.user.is_authenticated:
            new_complaint.wrote_complaint = self.request.user

        new_complaint.save()

        messages.success(self.request, 'Ваша жалобы было успешно отправлена, ответ придет вам на почту')
        return redirect('home', permanent=False)


class ComplaintList(ListView):
    paginate_by = 10
    model = models.Complaint
    template_name = 'staff/complaint_list.html'
    context_object_name = 'complaint_list'

    def get_context_data(self, *, object_list=None, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': 'Список жалоб',
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.warning(self.request, 'Чтобы просматривать жалобы вы должны быть авторизованы')
            return redirect('login', permanent=False)

        if not self.request.user.is_staff:
            messages.error(self.request, 'Просматривать жалобы могут только администрация')
            return redirect('home', permanent=False)

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = models.Complaint.objects.filter()

        considered_status = self.request.GET.get('considered_status')
        written_after_value = self.request.GET.get('written_after_value')
        written_before_value = self.request.GET.get('written_before_value')
        email_value = self.request.GET.get('email_value')

        if considered_status:
            queryset = queryset.filter(reviewed_complaint__isnull=False if considered_status == 'considered' else True)

        if written_after_value:
            queryset = queryset.filter(date_write__gte=written_after_value)

        if written_before_value:
            queryset = queryset.filter(date_write__lte=written_before_value)

        if email_value:
            queryset = queryset.filter(
                Q(feedback_email__isnull=False, feedback_email__icontains=email_value) |
                Q(feedback_email__isnull=True, wrote_complaint__email__icontains=email_value)
            )

        return queryset


class ConsiderComplaint(UpdateView):
    model = models.Complaint
    form_class = forms.ConsiderComplaintForm
    template_name = 'staff/consider_complaint.html'
    pk_url_kwarg = 'pk'
    current_complaint = None

    def get_context_data(self, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': 'Просмотр рассмотренной жалобы' if self.current_complaint.reviewed_complaint else 'Рассмотрение жалобы',
            'current_complaint': self.current_complaint,
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.warning(self.request, 'Чтобы рассмотреть жалобу вы должны быть авторизованы')
            return redirect('login', permanent=False)

        if not self.request.user.is_staff:
            messages.error(self.request, 'Рассматривать жалобы могут только администрация')
            return redirect('home', permanent=False)

        self.current_complaint = self.get_object()

        if isinstance(self.current_complaint, HttpResponseRedirect):
            return self.current_complaint

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        try:
            user_complaint = models.Complaint.objects.get(pk=self.kwargs.get(self.pk_url_kwarg))
        except ObjectDoesNotExist:
            messages.error(self.request, 'Жалоба не найдена')
            return redirect('complaint_list', permanent=False)

        return user_complaint

    def post(self, request, *args, **kwargs):
        if self.current_complaint.reviewed_complaint:
            messages.error(request, 'Жалоба уже была рассмотрена')
            return redirect('complaint_consider', pk=self.kwargs.get(self.pk_url_kwarg), permanent=False)

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        consider_complaint = form.save(commit=False)
        consider_complaint.reviewed_complaint = self.request.user
        consider_complaint.save()
        email_user = consider_complaint.feedback_email

        if self.current_complaint.wrote_complaint:
            user_models.Notification.objects.create(
                to_whom=self.current_complaint.wrote_complaint,
                message='Ваша жалоба была рассмотрена, вердикт жалобы был отправлен вам на почту',
            )
            email_user = self.current_complaint.wrote_complaint.email

        subject = 'Вердикт жалобы'
        message = (f'Рассмотрена администратором: {self.request.user.username}.\n'
                   f'Вердикт: {consider_complaint.verdict}.')

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email_user],
            fail_silently=False,
        )

        return redirect('complaint_list', permanent=False)


class NewAppeal(CreateView):
    form_class = forms.NewAppealForm
    template_name = 'staff/new_appeal.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context: dict = {
            'title': 'Написать апелляция',
        }

        return {**base_context, **context}

    def post(self, request, *args, **kwargs):
        if not self.request.user.banned:
            messages.error(request, 'Вы не заблокированы, апелляции нужны для оспаривания блокировки')
            return redirect('home', permanent=False)
        if models.Appeal.objects.filter(
            write_appeal=self.request.user,
            reviewed_appeal__isnull=True,
        ).exists():
            messages.error(request, 'У вас уже есть поданная нерассмотренная апелляция')
            return redirect('appeal_new', permanent=False)

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        new_appeal = form.save(commit=False)
        new_appeal.write_appeal = self.request.user
        new_appeal.save()

        messages.success(self.request, 'Ваша апелляция было успешно отправлена, ответ придет вам на почту')
        return redirect('home', permanent=False)


class AppealList(ListView):
    paginate_by = 10
    model = models.Appeal
    template_name = 'staff/appeal_list.html'
    context_object_name = 'appeal_list'

    def get_context_data(self, *, object_list=None, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': 'Список апелляций',
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.warning(self.request, 'Чтобы просматривать апелляции вы должны быть авторизованы')
            return redirect('login', permanent=False)

        if not self.request.user.is_staff:
            messages.error(self.request, 'Просматривать апелляции могут только администрация')
            return redirect('home', permanent=False)

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = models.Appeal.objects.filter()

        considered_status = self.request.GET.get('considered_status')
        written_after_value = self.request.GET.get('written_after_value')
        written_before_value = self.request.GET.get('written_before_value')
        username_value = self.request.GET.get('username_value')

        if considered_status:
            queryset = queryset.filter(reviewed_appeal__isnull=False if considered_status == 'considered' else True)

        if written_after_value:
            queryset = queryset.filter(date_write__gte=written_after_value)

        if written_before_value:
            queryset = queryset.filter(date_write__lte=written_before_value)

        if username_value:
            queryset = queryset.filter(write_appeal__username__icontains=username_value)

        return queryset


class ConsiderAppeal(UpdateView):
    model = models.Appeal
    form_class = forms.ConsiderAppealForm
    template_name = 'staff/consider_appeal.html'
    pk_url_kwarg = 'pk'
    current_appeal = None

    def get_context_data(self, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': 'Рассмотрение апелляции',
            'current_appeal': self.current_appeal,
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.warning(self.request, 'Чтобы рассмотреть апелляцию вы должны быть авторизованы')
            return redirect('login', permanent=False)

        if not self.request.user.is_staff:
            messages.error(self.request, 'Рассматривать апелляции могут только администрация')
            return redirect('home', permanent=False)

        self.current_appeal = self.get_object()

        if isinstance(self.current_appeal, HttpResponseRedirect):
            return self.current_appeal

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        try:
            user_appel = models.Appeal.objects.get(pk=self.kwargs.get(self.pk_url_kwarg))
        except ObjectDoesNotExist:
            messages.error(self.request, 'Апелляция не найдена')
            return redirect('appeal_list', permanent=False)

        return user_appel

    def post(self, request, *args, **kwargs):
        if self.current_appeal.reviewed_appeal:
            messages.error(request, 'Апелляция уже была рассмотрена')
            return redirect('appeal_consider', pk=self.kwargs.get(self.pk_url_kwarg), permanent=False)

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        consider_appeal = form.save(commit=False)
        consider_appeal.reviewed_appeal = self.request.user
        consider_appeal.save()
        email_user = self.current_appeal.write_appeal.email

        subject = 'Вердикт апелляции'
        message = (f'Рассмотрена администратором: {self.request.user.username}.\n'
                   f'Вердикт: {consider_appeal.verdict}.')

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email_user],
            fail_silently=False,
        )

        return redirect('appeal_list', permanent=False)
