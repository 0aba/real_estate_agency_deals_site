from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.edit import FormMixin
from django.core.paginator import Paginator
from real_estate_agency import models
from django.shortcuts import redirect
from real_estate_agency import forms
from django.contrib import messages
from django.shortcuts import render
from django.views import View


class Home(FormMixin,View):
    template_name = 'common/home.html'
    form_class = forms.ReviewAgencyCreationForm
    paginate_by = 5
    have_review = None

    def get_context_data(self, **kwargs):
        page = self.request.GET.get('page')
        paginator = Paginator(
            models.ReviewAgency.non_deleted.filter(), self.paginate_by
        ).get_page(page if page else 1)

        context: dict = {
            'title': 'Домашняя страница',
            'page_obj': paginator,
            'have_review': self.have_review,
            'form': forms.ReviewAgencyCreationForm(),
        }

        return context

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            try:
                self.have_review = models.ReviewAgency.non_deleted.get(
                    wrote_review=self.request.user,
                )
            except ObjectDoesNotExist:
                self.have_review = None

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, context=Home.get_context_data(self))

    def post(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.error(request, 'Отзыв может оставить только авторизованный пользователь')
            return redirect('home', permanent=False)

        if self.request.user.banned:
            messages.error(request, 'Вы не можете использовать функцию отзывов, когда вы заблокированы')
            return redirect('home', permanent=False)
        form = self.get_form()

        if self.have_review:
            messages.error(request, 'Вы можете оставить только один отзыв у агентстве')
            return redirect('home', permanent=False)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        review_agency = form.save(commit=False)
        review_agency.wrote_review = self.request.user
        review_agency.save()

        messages.success(self.request, 'Вы успешно оставили отзыв')

        return redirect('home', permanent=False)
