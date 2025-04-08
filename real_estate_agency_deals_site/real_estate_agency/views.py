from django.views.generic import CreateView, DetailView, UpdateView, ListView
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect
from real_estate_agency import models, forms
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import F


class ChangeReviewAgencyView(UpdateView):
    model = models.ReviewAgency
    form_class = forms.ReviewAgencyUpdateForm
    template_name = 'real_estate_agency/review_change.html'
    pk_url_kwarg = 'pk'
    current_review = None

    def get_context_data(self, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': 'Изменить отзыв об агентстве',
            'current_review': self.current_review,
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.warning(self.request, 'Чтобы изменить отзыв об агентстве необходимо авторизоваться')
            return redirect('login', permanent=False)

        review = self.get_object()

        if isinstance(review, HttpResponseRedirect):
            return review

        self.current_review = review

        if review.wrote_review != self.request.user:
            messages.error(self.request, 'У вас нет доступа к этому отзыву об агентстве')
            return redirect('home', permanent=False)

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        try:
            review = self.model.objects.get(pk=self.kwargs.get(self.pk_url_kwarg))
        except ObjectDoesNotExist:
            messages.error(self.request, 'Отзыв агентства не найден')
            return redirect('home', permanent=False)

        return review

    def form_valid(self, form):
        review = form.save(commit=False)
        review.change = True
        review.save()
        return redirect('home', permanent=False)


class RealtorListView(ListView):
    paginate_by = 10
    model = models.Realtor
    template_name = 'real_estate_agency/realtor_list.html'
    context_object_name = 'realtor_list'

    def get_context_data(self, *, object_list=None, **kwargs):
        base_context = super().get_context_data(**kwargs)

        context = {
            'title': 'Список риэлтеров',
        }

        return {**base_context, **context}

    def get_queryset(self):
        queryset = models.Realtor.objects.filter()

        full_name_value = self.request.GET.get('full_name_value')
        experience_min_value = self.request.GET.get('experience_min_value')
        experience_max_value = self.request.GET.get('experience_max_value')
        price_min_value = self.request.GET.get('price_min_value')
        price_max_value = self.request.GET.get('price_min_value')

        if full_name_value:
            queryset = queryset.annotate(
                full_name=Concat(F('last_name'), Value(' '), F('first_name'), Value(' '), F('patronymic'))
            ).filter(full_name__icontains=full_name_value)

        if experience_min_value:
            queryset = queryset.filter(experience__gte=experience_min_value)

        if experience_max_value:
            queryset = queryset.filter(experience__lte=experience_max_value)

        if price_min_value:
            queryset = queryset.filter(price__gte=price_min_value)

        if price_max_value:
            queryset = queryset.filter(price__lte=price_max_value)

        return queryset


class NewRealtorView(CreateView):
    form_class = forms.RealtorCreationForm
    template_name = 'real_estate_agency/new_realtor.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context: dict = {
            'title': 'Добавить риэлтера',
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.warning(request, 'Что бы добавить риэлтера, нужно авторизоваться')
            return redirect('realtor_list', permanent=False)

        if not self.request.user.is_staff:
            messages.error(request, 'Что бы добавить риэлтера, нужно быть администратором')
            return redirect('realtor_list', permanent=False)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()

        messages.success(self.request, 'Успешное создан новый риэлтер')

        return redirect('realtor_list', permanent=False)


class RealtorView(DetailView):
    model = models.Realtor
    template_name = 'real_estate_agency/realtor_view.html'
    context_object_name = 'realtor_view'
    pk_url_kwarg = 'pk'

    def get_context_data(self, *, object_list=None, **kwargs):
        base_context = super().get_context_data(**kwargs)

        context = {
            'title': f'Риэлтер {self.object.last_name} {self.object.first_name} {self.object.patronymic}',
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        realtor_view = self.get_object()

        if isinstance(realtor_view, HttpResponseRedirect):
            return realtor_view

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        try:
            object_user = models.Realtor.objects.get(pk=self.kwargs.get(self.pk_url_kwarg))
        except ObjectDoesNotExist:
            messages.error(self.request, 'Риэлтор не найден')
            return redirect('realtor_list', permanent=False)

        return object_user


class ChangeRealtorView(UpdateView):
    model = models.Realtor
    form_class = forms.RealtorUpdateForm
    template_name = 'real_estate_agency/realtor_change.html'
    pk_url_kwarg = 'pk'
    relater_view = None

    def get_context_data(self, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': f'Изменить данные риэлтера {self.relater_view.last_name} {self.relater_view.first_name} {self.relater_view.patronymic}',
        }

        return {**base_context, **context}


    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.warning(self.request, 'Чтобы изменить риэлтера необходимо авторизоваться')
            return redirect('login', permanent=False)

        self.relater_view = self.get_object()

        if isinstance(self.relater_view, HttpResponseRedirect):
            return self.relater_view

        if not self.request.user.is_staff:
            messages.error(self.request, 'У вас нет прав для изменения данных этого риэлетора, вы должны быть администратором')
            return redirect('realtor_list', permanent=False)

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        try:
            relater = models.Realtor.objects.get(pk=self.kwargs.get(self.pk_url_kwarg))
        except ObjectDoesNotExist:
            messages.error(self.request, 'Реэлетор не найден')
            return redirect('realtor_list', permanent=False)

        return relater

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Успешный изменение реэлетера')

        return redirect('realtor', self.kwargs.get(self.pk_url_kwarg), permanent=False)

