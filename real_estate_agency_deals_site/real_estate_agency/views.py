from django.views.generic import CreateView, DetailView, UpdateView
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.edit import FormMixin
from django.http import HttpResponseRedirect
from real_estate_agency import models, forms
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.db import IntegrityError
from django.contrib import messages
from django.db.models import Avg


class SignupRealEstateAgencyView(CreateView):
    form_class = forms.RealEstateAgencyCreationForm
    template_name = 'real_estate_agency/signup_real_estate_agency.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context: dict = {
            'title': 'Регистрация агентства недвижимости',
        }

        return {**base_context, **context}

    def form_valid(self, form):
        try:
            new_real_estate_agency = form.save(commit=False)
            new_real_estate_agency.representative = self.request.user
            new_real_estate_agency.save()
        except IntegrityError:
            messages.error(self.request, 'Вы можете представлять только одно агенство')
            return redirect('home', permanent=False)

        return redirect('agency_profile', slug_name=new_real_estate_agency.slug_name, permanent=False)


class ProfileRealEstateAgencyView(FormMixin, DetailView):
    model = models.RealEstateAgency
    paginate_by = 5
    form_class = forms.ReviewAgencyCreationForm
    template_name = 'real_estate_agency/profile_agency.html'
    context_object_name = 'profile_agency'
    slug_url_kwarg = 'slug_name'
    have_review = None
    profile_agency = None

    def get_context_data(self, *, object_list=None, **kwargs):
        base_context = super().get_context_data(**kwargs)
        page = self.request.GET.get('page')
        paginator = Paginator(
            models.ReviewAgency.non_deleted.filter(
                review_agency=models.RealEstateAgency.objects.get(slug_name=self.kwargs.get('slug_name')),
            ), self.paginate_by
        ).get_page(page if page else 1)

        context = {
            'reviews_agency': paginator,
            'title': f'Профиль @{self.profile_agency.name}',
            'have_review': self.have_review,
            'grade_real_estate_agency': models.ReviewAgency.non_deleted.filter(
                review_agency=self.get_object()
            ).aggregate(Avg('grade'))['grade__avg'],
            'form': forms.ReviewAgencyCreationForm(),
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            self.have_review = models.ReviewAgency.non_deleted.filter(
                wrote_review=self.request.user,
            ).exists()

        self.profile_agency = self.get_object()

        if isinstance(self.profile_agency, HttpResponseRedirect):
            messages.error(request, 'Агенство не найдено')
            return redirect('home', permanent=False)

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        try:
            object_real_estate_agency = models.RealEstateAgency.objects.get(slug_name=self.kwargs.get(self.slug_url_kwarg))
        except ObjectDoesNotExist:
            messages.error(self.request, 'Агенство не найден')
            return redirect('home', permanent=False)

        return object_real_estate_agency

    def post(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.error(request, 'Отзыв может оставить только авторизованный пользователь')
            return redirect('home', permanent=False)

        if self.request.user.banned:
            messages.error(request, 'Вы не можете использовать функцию отзывов, когда вы заблокированы')
            return redirect('agency_profile', slug_name=self.kwargs.get(self.slug_url_kwarg), permanent=False)
        form = self.get_form()

        if self.have_review:
            messages.error(request, 'Вы можете оставить только один отзыв у агентстве')
            return redirect('agency_profile', slug_name=self.kwargs.get(self.slug_url_kwarg), permanent=False)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        review_agency = form.save(commit=False)
        review_agency.review_agency = models.RealEstateAgency.objects.get(slug_name=self.kwargs.get(self.slug_url_kwarg))
        review_agency.wrote_review = self.request.user
        review_agency.save()

        messages.success(self.request, 'Вы успешно оставили отзыв')

        return redirect('agency_profile', slug_name=self.kwargs.get(self.slug_url_kwarg), permanent=False)


class ChangeProfileRealEstateAgencyView(UpdateView):
    model = models.RealEstateAgency
    form_class = forms.RealEstateAgencyUpdateForm
    template_name = 'real_estate_agency/profile_agency_change.html'
    slug_url_kwarg = 'slug_name'

    def get_context_data(self, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': 'Изменить профиль агентства недвижимости',
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.warning(self.request, 'Чтобы изменить профиль агентства необходимо авторизоваться')
            return redirect('login', permanent=False)

        agency = self.get_object()

        if isinstance(agency, HttpResponseRedirect):
            return agency

        if agency.representative != self.request.user:
            messages.error(self.request, 'У вас нет доступа к этому профилю агентства')
            return redirect('home', permanent=False)

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        try:
            agency = self.model.objects.get(slug_name=self.kwargs.get(self.slug_url_kwarg))
        except ObjectDoesNotExist:
            messages.error(self.request, 'Агенство не найден')
            return redirect('home', permanent=False)

        return agency

    def form_valid(self, form):
        update_agency_profile = form.save()
        return redirect('agency_profile', slug_name=update_agency_profile.slug_name, permanent=False)


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
        return redirect('agency_profile', slug_name=self.current_review.review_agency.slug_name, permanent=False)

