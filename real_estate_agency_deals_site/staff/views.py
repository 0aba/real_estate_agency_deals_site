from django.views.generic import CreateView, UpdateView, ListView, FormView
from real_estate_agency import models as real_estate_agency_models
from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from real_estate_agency_deals_site import settings
from django.core.mail import send_mail
from user import models as user_models
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from staff import models
from staff import forms
import csv


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

        if not self.request.user.is_superuser:
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

        if not self.request.user.is_superuser:
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

        if not self.request.user.is_superuser:
            messages.error(self.request, 'Просматривать апелляции могут только администрация')
            return redirect('home', permanent=False)

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = models.Appeal.objects.filter()

        considered_status = self.request.GET.get('considered_status')
        written_after_value = self.request.GET.get('written_after_value')
        written_before_value = self.request.GET.get('written_before_value')
        username_value = self.request.GET.get('username_value')

        if considered_status and considered_status not in ('considered_rejected', 'considered_accepted',):
            queryset = queryset.filter(reviewed_appeal__isnull=False if considered_status == 'considered' else True)

        if considered_status in ('considered_rejected', 'considered_accepted',):
            queryset = queryset.filter(Q(reviewed_appeal__isnull=False)
                                       & Q(rejected=True if considered_status == 'considered_rejected' else False))

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

        if not self.request.user.is_superuser:
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
        action_user = consider_appeal.write_appeal

        subject = 'Вердикт апелляции'
        message = (f'Рассмотрена администратором: {self.request.user.username}.\n'
                   f'Вердикт: {consider_appeal.verdict}.')

        if consider_appeal.rejected:
            user_models.Notification.objects.create(
                to_whom=action_user,
                message='Вам отказано в апелляции, вердикт был отправлен на почту',
            )
        else:
            action_user.banned = False
            action_user.save()

            user_models.Notification.objects.create(
                to_whom=action_user,
                message='Вашу апелляцию приняли, вердикт был отправлен на почту',
            )

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [action_user.email],
            fail_silently=False,
        )

        return redirect('appeal_list', permanent=False)


class LogsPrivateMessage(ListView):
    paginate_by = 10
    model = user_models.PrivateMessage
    template_name = 'staff/private_message_list_for_admin.html'
    context_object_name = 'logs_PM'

    def get_context_data(self, *, object_list=None, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': 'Логи личных сообщений',
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.warning(self.request, 'Чтобы просматривать логи личных сообщений вы должны быть авторизованы')
            return redirect('login', permanent=False)

        if not self.request.user.is_superuser:
            messages.error(self.request, 'Просматривать логи личных сообщений могут только администрация')
            return redirect('home', permanent=False)

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = user_models.PrivateMessage.objects.filter()

        wrote_PM_username_value = self.request.GET.get('wrote_PM_username_value')
        received_PM_username_value = self.request.GET.get('received_PM_username_value')
        date_write_min_value = self.request.GET.get('date_write_min_value')
        date_write_max_value = self.request.GET.get('date_write_max_value')
        only_deleted_value = self.request.GET.get('only_deleted_value')

        if wrote_PM_username_value:
            queryset = queryset.filter(wrote_PM__username__icontains=wrote_PM_username_value)

        if received_PM_username_value:
            queryset = queryset.filter(received_PM__username__icontains=received_PM_username_value)

        if date_write_min_value:
            queryset = queryset.filter(date_write__gte=date_write_min_value)

        if date_write_max_value:
            queryset = queryset.filter(date_write__lte=date_write_max_value)

        if only_deleted_value:
            queryset = queryset.filter(deleted=True)

        return queryset


class DealStatistics(FormView):
    model = real_estate_agency_models.Deal
    form_class = forms.DealStatisticsFilterForm
    template_name = 'staff/download_deal_statistics.html'

    def get_context_data(self, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': f'Скачать статистику',
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.warning(request, 'Что бы скачивать статистику сделок, нужно авторизоваться')
            return redirect('login', permanent=False)

        if not self.request.user.is_superuser:
            messages.error(request, 'Что бы скачивать статистику сделок, нужно быть администратором')
            return redirect('home', permanent=False)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        deleted_deal = form.cleaned_data.get('deleted_deal')
        if deleted_deal:
            queryset = real_estate_agency_models.Deal.objects.filter()
        else:
            queryset = real_estate_agency_models.Deal.non_deleted.filter()

        type_deal = form.cleaned_data.get('type_deal')
        if type_deal:
            type_deal = int(type_deal)
            if type_deal == real_estate_agency_models.Deal.DealType.SALE:
                queryset = queryset.filter(type=real_estate_agency_models.Deal.DealType.SALE)
            elif type_deal == real_estate_agency_models.Deal.DealType.RENT:
                queryset = queryset.filter(type=real_estate_agency_models.Deal.DealType.RENT)
                rented = form.cleaned_data.get('rented')
                if rented:
                    rented = int(rented)
                    if rented == forms.DealStatisticsFilterForm.RentalStatus.RENTAL_ONLY:
                        queryset = queryset.filter(deal_rental_fk__rented=True)
                    elif rented == forms.DealStatisticsFilterForm.RentalStatus.RENTAL_NONE:
                        queryset = queryset.filter(deal_rental_fk__rented=False)
            elif type_deal == real_estate_agency_models.Deal.DealType.CONSTRUCTION:
                queryset = queryset.filter(type=real_estate_agency_models.Deal.DealType.CONSTRUCTION)
                construction_company = form.cleaned_data.get('construction_company')
                if construction_company:
                    queryset = queryset.filter(deal_construction_fk__construction_company__icontains=construction_company)

        date_create_start = form.cleaned_data.get('date_create_start')
        date_create_end = form.cleaned_data.get('date_create_end')
        price_min = form.cleaned_data.get('price_min')
        price_max = form.cleaned_data.get('price_max')
        completed_deal_status = form.cleaned_data.get('completed_deal_status')
        agent_username = form.cleaned_data.get('agent_username')
        real_estate_deal_id = form.cleaned_data.get('real_estate_deal_id')
        type_real_estate = form.cleaned_data.get('type_real_estate')
        square_min = form.cleaned_data.get('square_min')
        square_max = form.cleaned_data.get('square_max')

        if date_create_start:
            queryset = queryset.filter(date_create__gte=date_create_start)

        if date_create_end:
            queryset = queryset.filter(date_create__lte=date_create_end)

        if price_min:
            queryset = queryset.filter(current_price__gte=price_min)

        if price_max:
            queryset = queryset.filter(current_price__lte=price_max)

        if completed_deal_status:
            completed_deal_status = int(completed_deal_status)
            if completed_deal_status == forms.DealStatisticsFilterForm.CompletedDealStatus.COMPLETED_ONLY:
                queryset = queryset.filter(completed=True)
            elif completed_deal_status == forms.DealStatisticsFilterForm.CompletedDealStatus.COMPLETED_NONE:
                queryset = queryset.filter(completed=False)

        if agent_username:
            queryset = queryset.filter(agent__username=agent_username)

        if real_estate_deal_id:
            queryset = queryset.filter(real_estate_deal__pk=int(real_estate_deal_id))

        if type_real_estate:
            type_real_estate = int(type_real_estate)
            if type_real_estate == real_estate_agency_models.RealEstate.RealEstateType.APARTMENT:
                queryset = queryset.filter(real_estate_deal__type=real_estate_agency_models.RealEstate.RealEstateType.APARTMENT)
            elif type_real_estate == real_estate_agency_models.RealEstate.RealEstateType.HOUSE:
                queryset = queryset.filter(real_estate_deal__type=real_estate_agency_models.RealEstate.RealEstateType.HOUSE)
            elif type_real_estate == real_estate_agency_models.RealEstate.RealEstateType.PLOT:
                queryset = queryset.filter(real_estate_deal__type=real_estate_agency_models.RealEstate.RealEstateType.PLOT)

        if square_min:
            queryset = queryset.filter(square__gte=square_min)

        if square_max:
            queryset = queryset.filter(square__lte=square_max)

        # csv
        response = HttpResponse(content_type='text/csv')
        current_time = timezone.now()

        response['Content-Disposition'] = f'attachment; filename="deals_export-{current_time.strftime("%Y-%m-%d_%H-%M-%S")}.csv"'

        writer = csv.writer(response)
        writer.writerow(('Номер', 'Заголовок', 'Тип сделки', 'Тип недвижимости', 'Общая площадь недвижимости', 'Текущая цена', 'Номер недвижимости', 'Отвественненый агент', 'Статус завершения', 'Дата создания',))

        deal_type = real_estate_agency_models.Deal.DealType
        real_estate_type = real_estate_agency_models.RealEstate.RealEstateType

        for id_table, deal in enumerate(queryset):
            writer.writerow((id_table, deal.title, deal_type(deal.type).label, real_estate_type(deal.real_estate_deal.type).label, deal.real_estate_deal.square,
                             deal.current_price, deal.real_estate_deal.pk, deal.agent.username,
                             'Завершена' if deal.completed else 'Не завершена', deal.date_create,))

        return response
