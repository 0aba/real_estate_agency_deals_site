from django.views.generic import CreateView, DetailView, UpdateView, ListView, FormView
from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.functions import Concat
from django.shortcuts import redirect, render
from real_estate_agency import models, forms
from django.db.models import F, Value, Q
from user import models as user_models
from django.contrib import messages
from django.utils import timezone
import csv


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

        if self.request.user.banned:
            messages.error(self.request, 'Вы не можете изменить отзыв, когда вы заблокированы, но можете его удалить')
            return redirect('home', permanent=False)

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
        messages.success(self.request, 'Отзыв был успешно изменен')

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
        new_realtor = form.save()

        messages.success(self.request, 'Успешное создан новый риэлтер')

        return redirect('realtor', pk=new_realtor.pk, permanent=False)


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


class RealEstateListView(ListView):
    paginate_by = 5
    model = models.RealEstate
    template_name = 'real_estate_agency/real_estate_list.html'
    context_object_name = 'real_estate_list'

    def get_context_data(self, *, object_list=None, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': 'Список недвижимости',
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.warning(request, 'Что бы просмотреть недвижимость, нужно авторизоваться')
            return redirect('real_estate_list', permanent=False)

        if not self.request.user.is_staff:
            messages.error(request, 'Что бы просмотреть недвижимость, нужно быть агентом недвижимости')
            return redirect('real_estate_list', permanent=False)

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = models.RealEstate.non_deleted.filter()

        id_real_estate = self.request.GET.get('id_real_estate')
        square_min_value = self.request.GET.get('square_min_value')
        square_max_value = self.request.GET.get('square_max_value')
        when_added_min_value = self.request.GET.get('when_added_min_value')
        when_added_max_value = self.request.GET.get('when_added_max_value')
        address_real_estate = self.request.GET.get('address_real_estate')
        type_real_estate = self.request.GET.get('type_real_estate')

        if id_real_estate:
            queryset = queryset.filter(pk=id_real_estate)

        if square_min_value:
            queryset = queryset.filter(square__gte=square_min_value)

        if square_max_value:
            queryset = queryset.filter(square__lte=square_max_value)

        if when_added_min_value:
            queryset = queryset.filter(when_added__gte=when_added_min_value)

        if when_added_max_value:
            queryset = queryset.filter(when_added__lte=when_added_max_value)

        if address_real_estate == 'address_real_estate_exist':
            queryset = queryset.filter(address_real_estate__isnull=False)
            address_city_value = self.request.GET.get('address_city_value')
            address_district_value = self.request.GET.get('address_district_value')
            address_street_value = self.request.GET.get('address_street_value')
            address_house_value = self.request.GET.get('address_house_value')
            address_apartment_value = self.request.GET.get('address_apartment_value')

            if address_city_value:
                queryset = queryset.filter(address_real_estate__city__icontains=address_city_value)

            if address_district_value:
                queryset = queryset.filter(address_real_estate__district__icontains=address_district_value)

            if address_street_value:
                queryset = queryset.filter(address_real_estate__street__icontains=address_street_value)

            if address_house_value:
                queryset = queryset.filter(address_real_estate__house=address_house_value)

            if address_apartment_value:
                queryset = queryset.filter(address_real_estate__apartment=address_apartment_value)

        if type_real_estate == 'apartment_only':
            queryset = queryset.filter(type=models.RealEstate.RealEstateType.APARTMENT)

            number_storeys_min_value = self.request.GET.get('number_storeys_min_value')
            number_storeys_max_value = self.request.GET.get('number_storeys_max_value')
            floor_min_value = self.request.GET.get('floor_min_value')
            floor_max_value = self.request.GET.get('floor_max_value')
            balcony_real_estate = self.request.GET.get('balcony_real_estate')
            furniture_real_estate = self.request.GET.get('furniture_real_estate')
            year_construction_min_value = self.request.GET.get('year_construction_min_value')
            year_construction_max_value = self.request.GET.get('year_construction_max_value')
            accident_rate_value = self.request.GET.get('accident_rate_value')
            room_type = self.request.GET.get('room_type')

            if number_storeys_min_value:
                queryset = queryset.filter(real_estate_DA_fk__number_storeys__gte=number_storeys_min_value)

            if number_storeys_max_value:
                queryset = queryset.filter(real_estate_DA_fk__number_storeys__lte=number_storeys_max_value)

            if floor_min_value:
                queryset = queryset.filter(real_estate_DA_fk__floor__gte=floor_min_value)

            if floor_max_value:
                queryset = queryset.filter(real_estate_DA_fk__floor__lte=floor_max_value)

            if balcony_real_estate in ('yes', 'no',):
                queryset = queryset.filter(real_estate_DA_fk__balcony=True if balcony_real_estate == 'yes' else False)

            if furniture_real_estate in ('yes', 'no',):
                queryset = queryset.filter(real_estate_DA_fk__furniture=True if furniture_real_estate == 'yes' else False)

            if year_construction_min_value:
                queryset = queryset.filter(real_estate_DA_fk__year_construction__gte=year_construction_min_value)

            if year_construction_max_value:
                queryset = queryset.filter(real_estate_DA_fk__year_construction__lte=year_construction_max_value)

            if accident_rate_value:
                queryset = queryset.filter(real_estate_DA_fk__accident_rate=True)

            if room_type and room_type != 'any':
                if room_type == 'other':
                    queryset = queryset.filter(real_estate_DA_fk__room_type=models.DataApartment.RoomType.OTHER)
                elif room_type == 'one_room':
                    queryset = queryset.filter(real_estate_DA_fk__room_type=models.DataApartment.RoomType.ONE_ROOM)
                elif room_type == 'two_room':
                    queryset = queryset.filter(real_estate_DA_fk__room_type=models.DataApartment.RoomType.TWO_ROOMS)
                elif room_type == 'three_room':
                    queryset = queryset.filter(real_estate_DA_fk__room_type=models.DataApartment.RoomType.THREE_ROOMS)
                elif room_type == 'four_room':
                    queryset = queryset.filter(real_estate_DA_fk__room_type=models.DataApartment.RoomType.FOUR_ROOMS)
                elif room_type == 'four_plus_room':
                    queryset = queryset.filter(real_estate_DA_fk__room_type=models.DataApartment.RoomType.FOUR_PLUS_ROOMS)
                elif room_type == 'maisonette':
                    queryset = queryset.filter(real_estate_DA_fk__room_type=models.DataApartment.RoomType.MAISONETTE)
                elif room_type == 'loft':
                    queryset = queryset.filter(real_estate_DA_fk__room_type=models.DataApartment.RoomType.LOFT)
                elif room_type == 'penthouse':
                    queryset = queryset.filter(real_estate_DA_fk__room_type=models.DataApartment.RoomType.PENTHOUSE)
        elif type_real_estate == 'house_only':
            queryset = queryset.filter(type=models.RealEstate.RealEstateType.HOUSE)
            house_number_storeys_min = self.request.GET.get('house_number_storeys_min')
            house_number_storeys_max = self.request.GET.get('house_number_storeys_max')
            house_area_min = self.request.GET.get('house_area_min')
            house_area_max = self.request.GET.get('house_area_max')
            house_year_construction_min = self.request.GET.get('house_year_construction_min')
            house_year_construction_max = self.request.GET.get('house_year_construction_max')
            garage_house = self.request.GET.get('garage_house')
            communications_house = self.request.GET.get('communications_house')

            if house_number_storeys_min:
                queryset = queryset.filter(real_estate_DH_fk__number_storeys__gte=house_number_storeys_min)

            if house_number_storeys_max:
                queryset = queryset.filter(real_estate_DH_fk__number_storeys__lte=house_number_storeys_max)

            if house_area_min:
                queryset = queryset.filter(real_estate_DH_fk__house_area__gte=house_area_min)

            if house_area_max:
                queryset = queryset.filter(real_estate_DH_fk__house_area__lte=house_area_max)

            if house_year_construction_min:
                queryset = queryset.filter(real_estate_DH_fk__year_construction__gte=house_year_construction_min)

            if house_year_construction_max:
                queryset = queryset.filter(real_estate_DH_fk__year_construction__lte=house_year_construction_max)

            if garage_house in ('yes', 'no',):
                queryset = queryset.filter(real_estate_DH_fk__garage=True if garage_house == 'yes' else False)

            if communications_house in ('yes', 'no',):
                queryset = queryset.filter(real_estate_DH_fk__communications=True if communications_house == 'yes' else False)
        elif type_real_estate == 'plot_only':
            queryset = queryset.filter(type=models.RealEstate.RealEstateType.PLOT)

            buildings_plot = self.request.GET.get('buildings_plot')
            communications_plot = self.request.GET.get('communications_plot')
            if buildings_plot in ('yes', 'no',):
                queryset = queryset.filter(real_estate_DH_fk__buildings=True if buildings_plot == 'yes' else False)

            if communications_plot in ('yes', 'no',):
                queryset = queryset.filter(real_estate_DH_fk__communications=True if communications_plot == 'yes' else False)

        return queryset


class NewRealEstateView(FormView):
    form_class = forms.RealEstateForm
    template_name = 'real_estate_agency/new_real_estate.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': 'Добавить недвижимость',
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.warning(request, 'Что бы добавить недвижимость, нужно авторизоваться')
            return redirect('real_estate_list', permanent=False)

        if not self.request.user.is_staff:
            messages.error(request, 'Что бы добавить недвижимость, нужно быть агентом недвижимости')
            return redirect('real_estate_list', permanent=False)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        address = None

        if form.cleaned_data.get('have_address'):
            address = models.Address.objects.create(
                city=city if len(city := form.cleaned_data.get('city')) else None,
                district=district if len(district := form.cleaned_data.get('district')) else None,
                street=street if len(street := form.cleaned_data.get('street')) else None,
                house=int(form.cleaned_data.get('house')),
                apartment=int(apartment) if (apartment := form.cleaned_data.get('apartment')) else apartment,
            )

        type_real_estate = int(form.cleaned_data.get('type'))
        new_real_estate = models.RealEstate.objects.create(
            type=type_real_estate,
            main_photo=form.cleaned_data.get('main_photo'),
            square=int(form.cleaned_data.get('square')),
            about=form.cleaned_data.get('about'),
            address_real_estate=address,
        )

        if type_real_estate == models.RealEstate.RealEstateType.APARTMENT:
            models.DataApartment.objects.create(
                real_estate_DA=new_real_estate,
                number_storeys=int(form.cleaned_data.get('data_apartment_number_storeys')),
                floor=int(form.cleaned_data.get('data_apartment_floor')),
                balcony=form.cleaned_data.get('data_apartment_balcony'),
                furniture=form.cleaned_data.get('data_apartment_furniture'),
                year_construction=int(form.cleaned_data.get('data_apartment_year_construction')),
                accident_rate=form.cleaned_data.get('data_apartment_accident_rate'),
                room_type=form.cleaned_data.get('data_apartment_room_type'),
            )
        elif type_real_estate == models.RealEstate.RealEstateType.HOUSE:
            models.DataHouse.objects.create(
                real_estate_DH=new_real_estate,
                number_storeys=int(form.cleaned_data.get('data_house_number_storeys')),
                house_area=int(form.cleaned_data.get('data_house_house_area')),
                year_construction=int(form.cleaned_data.get('data_house_year_construction')),
                garage=form.cleaned_data.get('data_house_garage'),
                communications=form.cleaned_data.get('data_house_communications'),
            )
        elif type_real_estate == models.RealEstate.RealEstateType.PLOT:
            models.DataPlot.objects.create(
                real_estate_DP=new_real_estate,
                buildings=form.cleaned_data.get('data_plot_buildings'),
                communications=form.cleaned_data.get('data_plot_communications'),
            )

        messages.success(self.request, 'Недвижимость была успешно добавлена')

        return redirect('real_estate', pk=new_real_estate.pk, permanent=False)


class RealEstateView(DetailView):
    model = models.RealEstate
    template_name = 'real_estate_agency/real_estate_view.html'
    context_object_name = 'real_estate_view'
    pk_url_kwarg = 'pk'

    def get_context_data(self, *, object_list=None, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': f'Недвижимость {self.object.pk}',
        }

        if self.object.type == models.RealEstate.RealEstateType.APARTMENT:
            context['data_apartment'] = models.DataApartment.objects.get(real_estate_DA=self.object)
        elif self.object.type == models.RealEstate.RealEstateType.HOUSE:
            context['data_house'] = models.DataHouse.objects.get(real_estate_DH=self.object)
        elif self.object.type == models.RealEstate.RealEstateType.PLOT:
            context['data_plot'] = models.DataPlot.objects.get(real_estate_DP=self.object)

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.warning(request, 'Что бы просмотреть данные о недвижимости, нужно авторизоваться')
            return redirect('real_estate_list', permanent=False)

        if not self.request.user.is_staff:
            messages.error(request, 'Что бы просмотреть данные о недвижимости, нужно быть агентом недвижимости')
            return redirect('real_estate_list', permanent=False)

        real_estate = self.get_object()

        if isinstance(real_estate, HttpResponseRedirect):
            return real_estate

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        try:
            object_real_estate = self.model.objects.get(pk=self.kwargs.get(self.pk_url_kwarg))
        except ObjectDoesNotExist:
            messages.error(self.request, 'Недвижимость не найден')
            return redirect('real_estate_list', permanent=False)

        return object_real_estate


class ChangeRealEstateView(FormView):
    model = models.RealEstate
    form_class = forms.RealEstateForm
    template_name = 'real_estate_agency/real_estate_change.html'
    pk_url_kwarg = 'pk'
    old_real_estate = None

    def get_context_data(self, **kwargs):
        base_context = super().get_context_data(**kwargs)

        initial_dict = {
            'type': self.old_real_estate.type,
            'square': self.old_real_estate.square,
            'main_photo': self.old_real_estate.main_photo,
            'about': self.old_real_estate.about,
        }
        if self.old_real_estate.address_real_estate:
            initial_dict['have_address'] = True
            initial_dict['city'] = self.old_real_estate.address_real_estate.city
            initial_dict['district'] = self.old_real_estate.address_real_estate.district
            initial_dict['street'] = self.old_real_estate.address_real_estate.street
            initial_dict['house'] = self.old_real_estate.address_real_estate.house
            initial_dict['apartment'] = self.old_real_estate.address_real_estate.apartment

        if self.old_real_estate.type == models.RealEstate.RealEstateType.APARTMENT:
            data_apartment = models.DataApartment.objects.get(real_estate_DA=self.old_real_estate)
            initial_dict['data_apartment_number_storeys'] = data_apartment.number_storeys
            initial_dict['data_apartment_floor'] = data_apartment.floor
            initial_dict['data_apartment_balcony'] = data_apartment.balcony
            initial_dict['data_apartment_furniture'] = data_apartment.furniture
            initial_dict['data_apartment_year_construction'] = data_apartment.year_construction
            initial_dict['data_apartment_accident_rate'] = data_apartment.accident_rate
            initial_dict['data_apartment_room_type'] = data_apartment.room_type
        elif self.old_real_estate.type == models.RealEstate.RealEstateType.HOUSE:
            data_house = models.DataHouse.objects.get(real_estate_DH=self.old_real_estate)
            initial_dict['data_house_number_storeys'] = data_house.number_storeys
            initial_dict['data_house_house_area'] = data_house.house_area
            initial_dict['data_house_year_construction'] = data_house.year_construction
            initial_dict['data_house_garage'] = data_house.garage
            initial_dict['data_house_communications'] = data_house.communications
        elif self.old_real_estate.type == models.RealEstate.RealEstateType.PLOT:
            data_plot = models.DataPlot.objects.get(real_estate_DP=self.old_real_estate)
            initial_dict['data_plot_buildings'] = data_plot.buildings
            initial_dict['data_plot_communications'] = data_plot.communications

        context = {
            'title': f'Недвижимость {self.old_real_estate.pk}',
            'form': self.form_class(initial=initial_dict)
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.warning(request, 'Что бы изменить данные о недвижимости, нужно авторизоваться')
            return redirect('real_estate_list', permanent=False)

        if not self.request.user.is_staff:
            messages.error(request, 'Что бы изменить данные о недвижимости, нужно быть агентом недвижимости')
            return redirect('real_estate_list', permanent=False)

        self.old_real_estate = self.get_object()

        if isinstance(self.old_real_estate, HttpResponseRedirect):
            return self.old_real_estate

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        try:
            object_real_estate = self.model.objects.get(pk=self.kwargs.get(self.pk_url_kwarg))
        except ObjectDoesNotExist:
            messages.error(self.request, 'Недвижимость не найден')
            return redirect('real_estate_list', permanent=False)

        return object_real_estate

    def get(self, request, *args, **kwargs):
        if models.Deal.non_deleted.filter(
            real_estate_deal=self.old_real_estate,
        ).exists():
            messages.warning(request, 'С данной недвижимость связаны активные сделки, изменения будут отражены на них')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        if (form.cleaned_data.get('have_address') != bool(self.old_real_estate.address_real_estate)
            and models.Deal.non_deleted.filter(
                real_estate_deal=self.old_real_estate,
            ).exists()):
            messages.error(self.request, 'При попытки изменить типа с шаблона на объект или наоборот, текущие связанные сделки имеют неправильны тип')
            return redirect('real_estate_change', pk=self.kwargs.get(self.pk_url_kwarg), permanent=False)

        address = None

        if form.cleaned_data.get('have_address') and self.old_real_estate.address_real_estate:
            object_address = self.old_real_estate.address_real_estate
            object_address.city = city if len(city := form.cleaned_data.get('city')) else None
            object_address.district = district if len(district := form.cleaned_data.get('district')) else None
            object_address.street = street if len(street := form.cleaned_data.get('street')) else None
            object_address.house = int(form.cleaned_data.get('house'))
            object_address.apartment = int(apartment) if (apartment := form.cleaned_data.get('apartment')) else apartment
            object_address.save()
            address = object_address
        elif not form.cleaned_data.get('have_address') and self.old_real_estate.address_real_estate:
            self.old_real_estate.address_real_estate.delete()
        elif form.cleaned_data.get('have_address') and not self.old_real_estate.address_real_estate:
            address = models.Address.objects.create(
                city=city if len(city := form.cleaned_data.get('city')) else None,
                district=district if len(district := form.cleaned_data.get('district')) else None,
                street=street if len(street := form.cleaned_data.get('street')) else None,
                house=int(form.cleaned_data.get('house')),
                apartment=int(apartment) if (apartment := form.cleaned_data.get('apartment')) else apartment,
            )

        type_real_estate = int(form.cleaned_data.get('type'))
        old_type = self.old_real_estate.type
        self.old_real_estate.type = type_real_estate
        self.old_real_estate.main_photo = form.cleaned_data.get('main_photo')
        self.old_real_estate.square = int(form.cleaned_data.get('square'))
        self.old_real_estate.about = form.cleaned_data.get('about')
        self.old_real_estate.address_real_estate = address
        self.old_real_estate.save()

        if type_real_estate == models.RealEstate.RealEstateType.APARTMENT:
            if type_real_estate == old_type:
                old_data_apartment = models.DataApartment.objects.get(real_estate_DA=self.old_real_estate)
                old_data_apartment.number_storeys = int(form.cleaned_data.get('data_apartment_number_storeys'))
                old_data_apartment.floor = int(form.cleaned_data.get('data_apartment_floor'))
                old_data_apartment.balcony = form.cleaned_data.get('data_apartment_balcony')
                old_data_apartment.furniture = form.cleaned_data.get('data_apartment_furniture')
                old_data_apartment.year_construction = int(form.cleaned_data.get('data_apartment_year_construction'))
                old_data_apartment.accident_rate = form.cleaned_data.get('data_apartment_accident_rate')
                old_data_apartment.room_type = form.cleaned_data.get('data_apartment_room_type')
                old_data_apartment.save()
            else:
                self.__del_extend_data(old_type)
                models.DataApartment.objects.create(
                    real_estate_DA=self.old_real_estate,
                    number_storeys=int(form.cleaned_data.get('data_apartment_number_storeys')),
                    floor=int(form.cleaned_data.get('data_apartment_floor')),
                    balcony=form.cleaned_data.get('data_apartment_balcony'),
                    furniture=form.cleaned_data.get('data_apartment_furniture'),
                    year_construction=int(form.cleaned_data.get('data_apartment_year_construction')),
                    accident_rate=form.cleaned_data.get('data_apartment_accident_rate'),
                    room_type=form.cleaned_data.get('data_apartment_room_type'),
                )
        elif type_real_estate == models.RealEstate.RealEstateType.HOUSE:
            if type_real_estate == old_type:
                old_data_house = models.DataHouse.objects.get(real_estate_DH=self.old_real_estate)
                old_data_house.number_storeys = int(form.cleaned_data.get('data_house_number_storeys'))
                old_data_house.house_area = int(form.cleaned_data.get('data_house_house_area'))
                old_data_house.year_construction = int(form.cleaned_data.get('data_house_year_construction'))
                old_data_house.garage = form.cleaned_data.get('data_house_garage')
                old_data_house.communications = form.cleaned_data.get('data_house_communications')
                old_data_house.save()
            else:
                self.__del_extend_data(old_type)
                models.DataHouse.objects.create(
                    real_estate_DH=self.old_real_estate,
                    number_storeys=int(form.cleaned_data.get('data_house_number_storeys')),
                    house_area=int(form.cleaned_data.get('data_house_house_area')),
                    year_construction=int(form.cleaned_data.get('data_house_year_construction')),
                    garage=form.cleaned_data.get('data_house_garage'),
                    communications=form.cleaned_data.get('data_house_communications'),
                )
        elif type_real_estate == models.RealEstate.RealEstateType.PLOT:
            if type_real_estate == old_type:
                old_data_plot = models.DataPlot.objects.get(real_estate_DP=self.old_real_estate)
                old_data_plot.buildings = form.cleaned_data.get('data_plot_buildings')
                old_data_plot.communications = form.cleaned_data.get('data_plot_communications')
                old_data_plot.save()
            else:
                self.__del_extend_data(old_type)
                models.DataPlot.objects.create(
                    real_estate_DP=self.old_real_estate,
                    buildings=form.cleaned_data.get('data_plot_buildings'),
                    communications=form.cleaned_data.get('data_plot_communications'),
                )

        messages.success(self.request, 'Недвижимость была успешно изменена')

        return redirect('real_estate', pk=self.kwargs.get(self.pk_url_kwarg), permanent=False)

    def __del_extend_data(self, type_data):
        if type_data == models.RealEstate.RealEstateType.APARTMENT:
            models.DataApartment.objects.get(real_estate_DA=self.old_real_estate).delete()
        elif type_data == models.RealEstate.RealEstateType.HOUSE:
            models.DataHouse.objects.get(real_estate_DH=self.old_real_estate).delete()
        elif type_data == models.RealEstate.RealEstateType.PLOT:
            models.DataPlot.objects.get(real_estate_DP=self.old_real_estate).delete()


class DealListView(ListView):
    paginate_by = 5
    model = models.Deal
    template_name = 'real_estate_agency/deal_list.html'
    context_object_name = 'deal_list'

    def get_context_data(self, *, object_list=None, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': 'Список сделок',
        }

        return {**base_context, **context}

    def get_queryset(self):
        queryset = queryset = models.Deal.non_deleted.filter()
        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                id_real_estate_deal = self.request.GET.get('id_real_estate_deal')
                agent_deals = self.request.GET.get('agent_deals')
                completed_status = self.request.GET.get('completed_status')

                if id_real_estate_deal:
                    queryset = queryset.filter(real_estate_deal__pk=id_real_estate_deal)

                if agent_deals:
                    queryset = queryset.filter(agent__username=agent_deals)

                if completed_status == 'completed_status_client_search':
                    queryset = queryset.filter(completed_type=models.Deal.DealCompletedType.CLIENT_SEARCH)
                elif completed_status == 'completed_status_in_progress':
                    queryset = queryset.filter(completed_type=models.Deal.DealCompletedType.IN_PROGRESS)
                elif completed_status == 'completed_status_success':
                    queryset = queryset.filter(completed_type=models.Deal.DealCompletedType.SUCCESS)
                elif completed_status == 'completed_status_rejected':
                    queryset = queryset.filter(completed_type=models.Deal.DealCompletedType.REJECTED)
            else:
                queryset = queryset.filter(Q(deal_with=self.request.user) | Q(completed_type=models.Deal.DealCompletedType.CLIENT_SEARCH))

            my_deals_only_value = self.request.GET.get('my_deals_only_value')
            if my_deals_only_value:
                queryset = models.Deal.non_deleted.filter(Q(deal_with=self.request.user))
        else:
            queryset = models.Deal.non_deleted.filter(completed_type=models.Deal.DealCompletedType.CLIENT_SEARCH)

        title_deal_value = self.request.GET.get('title_deal_value')
        price_deal_min_value = self.request.GET.get('price_deal_min_value')
        price_deal_max_value = self.request.GET.get('price_deal_max_value')

        if title_deal_value:
            queryset = queryset.filter(title__icontains=title_deal_value)

        if price_deal_min_value:
            queryset = queryset.filter(current_price__gte=price_deal_min_value)

        if price_deal_max_value:
            queryset = queryset.filter(current_price__lte=price_deal_max_value)

        type_deal = self.request.GET.get('type_deal')
        if type_deal == 'deal_sale_only':
            queryset = queryset.filter(type=models.Deal.DealType.SALE)
        elif type_deal == 'deal_rent_only':
            queryset = queryset.filter(type=models.Deal.DealType.RENT)

            price_housing_and_municipalities_min = self.request.GET.get('price_housing_and_municipalities_min')
            price_housing_and_municipalities_max = self.request.GET.get('price_housing_and_municipalities_max')
            prepayment_min = self.request.GET.get('prepayment_min')
            prepayment_max = self.request.GET.get('prepayment_max')
            rental_period_days_min = self.request.GET.get('rental_period_days_min')
            rental_period_days_max = self.request.GET.get('rental_period_days_max')

            if price_housing_and_municipalities_min:
                queryset = queryset.filter(deal_rental_fk__price_housing_and_municipalities__gte=price_housing_and_municipalities_min)

            if price_housing_and_municipalities_max:
                queryset = queryset.filter(deal_rental_fk__price_housing_and_municipalities__lte=price_housing_and_municipalities_max)

            if prepayment_min:
                queryset = queryset.filter(deal_rental_fk__prepayment__gte=prepayment_min)

            if prepayment_max:
                queryset = queryset.filter(deal_rental_fk__prepayment__lte=prepayment_max)

            if rental_period_days_min:
                queryset = queryset.filter(deal_rental_fk__rental_period_days__gte=rental_period_days_min)

            if rental_period_days_max:
                queryset = queryset.filter(deal_rental_fk__rental_period_days__lte=rental_period_days_max)

        elif type_deal == 'deal_construction_only':
            queryset = queryset.filter(type=models.Deal.DealType.CONSTRUCTION)

            construction_company = self.request.GET.get('construction_company')
            approximate_dates_min = self.request.GET.get('approximate_dates_min')
            approximate_dates_max = self.request.GET.get('approximate_dates_max')

            if construction_company:
                queryset = queryset.filter(deal_construction_fk__construction_company__icontains=construction_company)

            if approximate_dates_min:
                queryset = queryset.filter(deal_rental_fk__approximate_dates__gte=approximate_dates_min)

            if approximate_dates_max:
                queryset = queryset.filter(deal_rental_fk__approximate_dates__lte=approximate_dates_max)

        square_min_value = self.request.GET.get('square_min_value')
        square_max_value = self.request.GET.get('square_max_value')
        type_real_estate = self.request.GET.get('type_real_estate')

        if square_min_value:
            queryset = queryset.filter(real_estate_deal__square__gte=square_min_value)

        if square_max_value:
            queryset = queryset.filter(real_estate_deal__square__lte=square_max_value)

        address_city_value = self.request.GET.get('address_city_value')
        address_district_value = self.request.GET.get('address_district_value')
        address_street_value = self.request.GET.get('address_street_value')
        address_house_value = self.request.GET.get('address_house_value')
        address_apartment_value = self.request.GET.get('address_apartment_value')

        if address_city_value:
            queryset = queryset.filter(real_estate_deal__address_real_estate__city__icontains=address_city_value)

        if address_district_value:
            queryset = queryset.filter(real_estate_deal__address_real_estate__district__icontains=address_district_value)

        if address_street_value:
            queryset = queryset.filter(real_estate_deal__address_real_estate__street__icontains=address_street_value)

        if address_house_value:
            queryset = queryset.filter(real_estate_deal__address_real_estate__house=address_house_value)

        if address_apartment_value:
            queryset = queryset.filter(real_estate_deal__address_real_estate__apartment=address_apartment_value)

        if type_real_estate == 'apartment_only':
            queryset = queryset.filter(real_estate_deal__type=models.RealEstate.RealEstateType.APARTMENT)

            number_storeys_min_value = self.request.GET.get('number_storeys_min_value')
            number_storeys_max_value = self.request.GET.get('number_storeys_max_value')
            floor_min_value = self.request.GET.get('floor_min_value')
            floor_max_value = self.request.GET.get('floor_max_value')
            balcony_real_estate = self.request.GET.get('balcony_real_estate')
            furniture_real_estate = self.request.GET.get('furniture_real_estate')
            year_construction_min_value = self.request.GET.get('year_construction_min_value')
            year_construction_max_value = self.request.GET.get('year_construction_max_value')
            accident_rate_value = self.request.GET.get('accident_rate_value')
            room_type = self.request.GET.get('room_type')

            if number_storeys_min_value:
                queryset = queryset.filter(real_estate_deal__real_estate_DA_fk__number_storeys__gte=number_storeys_min_value)

            if number_storeys_max_value:
                queryset = queryset.filter(real_estate_deal__real_estate_DA_fk__number_storeys__lte=number_storeys_max_value)

            if floor_min_value:
                queryset = queryset.filter(real_estate_deal__real_estate_DA_fk__floor__gte=floor_min_value)

            if floor_max_value:
                queryset = queryset.filter(real_estate_deal__real_estate_DA_fk__floor__lte=floor_max_value)

            if balcony_real_estate in ('yes', 'no',):
                queryset = queryset.filter(real_estate_deal__real_estate_DA_fk__balcony=True if balcony_real_estate == 'yes' else False)

            if furniture_real_estate in ('yes', 'no',):
                queryset = queryset.filter(real_estate_deal__real_estate_DA_fk__furniture=True if furniture_real_estate == 'yes' else False)

            if year_construction_min_value:
                queryset = queryset.filter(real_estate_deal__real_estate_DA_fk__year_construction__gte=year_construction_min_value)

            if year_construction_max_value:
                queryset = queryset.filter(real_estate_deal__real_estate_DA_fk__year_construction__lte=year_construction_max_value)

            if accident_rate_value:
                queryset = queryset.filter(real_estate_deal__real_estate_DA_fk__accident_rate=True)

            if room_type and room_type != 'any':
                if room_type == 'other':
                    queryset = queryset.filter(real_estate_deal__real_estate_DA_fk__room_type=models.DataApartment.RoomType.OTHER)
                elif room_type == 'one_room':
                    queryset = queryset.filter(real_estate_deal__real_estate_DA_fk__room_type=models.DataApartment.RoomType.ONE_ROOM)
                elif room_type == 'two_room':
                    queryset = queryset.filter(real_estate_deal__real_estate_DA_fk__room_type=models.DataApartment.RoomType.TWO_ROOMS)
                elif room_type == 'three_room':
                    queryset = queryset.filter(real_estate_deal__real_estate_DA_fk__room_type=models.DataApartment.RoomType.THREE_ROOMS)
                elif room_type == 'four_room':
                    queryset = queryset.filter(real_estate_deal__real_estate_DA_fk__room_type=models.DataApartment.RoomType.FOUR_ROOMS)
                elif room_type == 'four_plus_room':
                    queryset = queryset.filter(real_estate_deal__real_estate_DA_fk__room_type=models.DataApartment.RoomType.FOUR_PLUS_ROOMS)
                elif room_type == 'maisonette':
                    queryset = queryset.filter(real_estate_deal__real_estate_DA_fk__room_type=models.DataApartment.RoomType.MAISONETTE)
                elif room_type == 'loft':
                    queryset = queryset.filter(real_estate_deal__real_estate_DA_fk__room_type=models.DataApartment.RoomType.LOFT)
                elif room_type == 'penthouse':
                    queryset = queryset.filter(real_estate_deal__real_estate_DA_fk__room_type=models.DataApartment.RoomType.PENTHOUSE)
        elif type_real_estate == 'house_only':
            queryset = queryset.filter(real_estate_deal__type=models.RealEstate.RealEstateType.HOUSE)
            house_number_storeys_min = self.request.GET.get('house_number_storeys_min')
            house_number_storeys_max = self.request.GET.get('house_number_storeys_max')
            house_area_min = self.request.GET.get('house_area_min')
            house_area_max = self.request.GET.get('house_area_max')
            house_year_construction_min = self.request.GET.get('house_year_construction_min')
            house_year_construction_max = self.request.GET.get('house_year_construction_max')
            garage_house = self.request.GET.get('garage_house')
            communications_house = self.request.GET.get('communications_house')

            if house_number_storeys_min:
                queryset = queryset.filter(real_estate_deal__real_estate_DH_fk__number_storeys__gte=house_number_storeys_min)

            if house_number_storeys_max:
                queryset = queryset.filter(real_estate_deal__real_estate_DH_fk__number_storeys__lte=house_number_storeys_max)

            if house_area_min:
                queryset = queryset.filter(real_estate_deal__real_estate_DH_fk__house_area__gte=house_area_min)

            if house_area_max:
                queryset = queryset.filter(real_estate_deal__real_estate_DH_fk__house_area__lte=house_area_max)

            if house_year_construction_min:
                queryset = queryset.filter(real_estate_deal__real_estate_DH_fk__year_construction__gte=house_year_construction_min)

            if house_year_construction_max:
                queryset = queryset.filter(real_estate_deal__real_estate_DH_fk__year_construction__lte=house_year_construction_max)

            if garage_house in ('yes', 'no',):
                queryset = queryset.filter(real_estate_deal__real_estate_DH_fk__garage=True if garage_house == 'yes' else False)

            if communications_house in ('yes', 'no',):
                queryset = queryset.filter(real_estate_deal__real_estate_DH_fk__communications=True if communications_house == 'yes' else False)
        elif type_real_estate == 'plot_only':
            queryset = queryset.filter(real_estate_deal__type=models.RealEstate.RealEstateType.PLOT)

            buildings_plot = self.request.GET.get('buildings_plot')
            communications_plot = self.request.GET.get('communications_plot')
            if buildings_plot in ('yes', 'no',):
                queryset = queryset.filter(real_estate_deal__real_estate_DH_fk__buildings=True if buildings_plot == 'yes' else False)

            if communications_plot in ('yes', 'no',):
                queryset = queryset.filter(real_estate_deal__real_estate_DH_fk__communications=True if communications_plot == 'yes' else False)

        return queryset


class NewDealView(FormView):
    form_class = forms.DealForm
    template_name = 'real_estate_agency/new_deal.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': 'Добавить сделку',
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.warning(request, 'Что бы добавить сделку, нужно авторизоваться')
            return redirect('deal_list', permanent=False)

        if not self.request.user.is_staff:
            messages.error(request, 'Что бы добавить сделку, нужно быть агентом недвижимости')
            return redirect('deal_list', permanent=False)

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            context = self.get_context_data()
            context['form'] = form
            return render(request, self.template_name, context=context)

    def form_valid(self, form):
        try:
            real_estate_deal = models.RealEstate.non_deleted.get(pk=int(form.cleaned_data.get('real_estate_deal_id')))
        except ObjectDoesNotExist:
            messages.error(self.request, 'Недвижимость по данному номеру не существует')
            return redirect('deal_list', permanent=False)

        if models.Deal.non_deleted.filter(
            Q(real_estate_deal=real_estate_deal)
            & ~Q(completed_type=models.Deal.DealCompletedType.SUCCESS)
            & ~Q(completed_type=models.Deal.DealCompletedType.REJECTED)
        ).exists():
            messages.error(self.request, 'На одну недвижимость может существовать только одна активная сделка')
            return redirect('deal_new', permanent=False)

        try:
            agent = user_models.User.objects.get(
                username=form.cleaned_data.get('agent_username').strip(),
                is_staff=True
            )
        except ObjectDoesNotExist:
            messages.error(self.request, 'Агент недвижимости с данным логином не существует')
            return redirect('deal_new', permanent=False)

        type_deal = int(form.cleaned_data.get('type'))

        if type_deal == models.Deal.DealType.CONSTRUCTION and real_estate_deal.type == models.RealEstate.RealEstateType.PLOT:
            messages.error(self.request, 'Нельзя сделать сделку строительства для участка')
            return redirect('deal_new', permanent=False)


        new_deal = models.Deal.objects.create(
            title=form.cleaned_data.get('title'),
            type=type_deal,
            current_price=form.cleaned_data.get('price'),
            real_estate_deal=real_estate_deal,
            agent=agent,
        )

        if type_deal == models.Deal.DealType.RENT:
            models.DataRental.objects.create(
                deal_rental=new_deal,
                price_housing_and_municipalities=form.cleaned_data.get('price_housing_and_municipalities'),
                prepayment=form.cleaned_data.get('prepayment'),
                rental_period_days=form.cleaned_data.get('rental_period_days'),
            )
        elif type_deal == models.Deal.DealType.CONSTRUCTION:
            models.DataConstruction.objects.create(
                deal_construction=new_deal,
                construction_company=form.cleaned_data.get('construction_company'),
                approximate_dates=form.cleaned_data.get('approximate_dates'),
                project_document=form.cleaned_data.get('project_document'),
            )

        messages.success(self.request, 'Сделка была успешно добавлена')

        return redirect('deal', title_slug=new_deal.title_slug, permanent=False)


class DealView(DetailView):
    model = models.Deal
    template_name = 'real_estate_agency/deal_view.html'
    context_object_name = 'deal_view'
    slug_url_kwarg = 'title_slug'

    def get_context_data(self, *, object_list=None, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': f'Сделка {self.object.title}',
            'price_history': models.ChangePrices.objects.filter(deal_price=self.object),
        }

        if self.request.user.is_authenticated:
            context['track_this_deal'] = models.TrackDeal.objects.filter(
                track_deal=self.object,
                who_track=self.request.user,
            ).exists()

        if self.object.type == models.Deal.DealType.RENT:
            context['data_rental'] = models.DataRental.objects.get(deal_rental=self.object)
        elif self.object.type == models.Deal.DealType.CONSTRUCTION:
            context['data_construction'] = models.DataConstruction.objects.get(deal_construction=self.object)

        if self.object.real_estate_deal.type == models.RealEstate.RealEstateType.APARTMENT:
            context['data_apartment'] = models.DataApartment.objects.get(real_estate_DA=self.object.real_estate_deal)
        elif self.object.real_estate_deal.type == models.RealEstate.RealEstateType.HOUSE:
            context['data_house'] = models.DataHouse.objects.get(real_estate_DH=self.object.real_estate_deal)
        elif self.object.real_estate_deal.type == models.RealEstate.RealEstateType.PLOT:
            context['data_plot'] = models.DataPlot.objects.get(real_estate_DP=self.object.real_estate_deal)

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        deal = self.get_object()

        if isinstance(deal, HttpResponseRedirect):
            return deal

        if (self.request.user.is_staff
            or deal.completed_type == models.Deal.DealCompletedType.CLIENT_SEARCH
            or deal.deal_with == self.request.user):
            return super().dispatch(request, *args, **kwargs)

        messages.error(self.request, 'Вы не можете просматривать чужие сделки')
        return redirect('deal_list', permanent=False)

    def get_object(self, queryset=None):
        try:
            object_deal = self.model.non_deleted.get(title_slug=self.kwargs.get(self.slug_url_kwarg))
        except ObjectDoesNotExist:
            messages.error(self.request, 'Сделка не найден')
            return redirect('deal_list', permanent=False)

        return object_deal


class ChangeDealView(FormView):
    model = models.Deal
    form_class = forms.DealForm
    template_name = 'real_estate_agency/deal_change.html'
    slug_url_kwarg = 'title_slug'
    old_deal = None

    def get_context_data(self, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': f'Изменить сделку {self.old_deal.title}',
        }

        initial_dict = {
            'title': self.old_deal.title,
            'type': self.old_deal.type,
            'price': self.old_deal.current_price,
            'real_estate_deal_id': self.old_deal.real_estate_deal.pk,
            'agent_username': self.old_deal.agent.username,
        }

        if self.old_deal.type == models.Deal.DealType.RENT:
            data_rental = models.DataRental.objects.get(deal_rental=self.old_deal)
            initial_dict['price_housing_and_municipalities'] = data_rental.price_housing_and_municipalities
            initial_dict['prepayment'] = data_rental.prepayment
            initial_dict['rental_period_days'] = data_rental.rental_period_days
        elif self.old_deal.type == models.Deal.DealType.CONSTRUCTION:
            data_construction = models.DataConstruction.objects.get(deal_construction=self.old_deal)
            initial_dict['construction_company'] = data_construction.construction_company
            initial_dict['approximate_dates'] = data_construction.approximate_dates
            initial_dict['project_document'] = data_construction.project_document

        context['form'] = self.form_class(initial=initial_dict)

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.warning(request, 'Что бы изменить данные о сделке, нужно авторизоваться')
            return redirect('login', permanent=False)

        if not self.request.user.is_staff:
            messages.error(request, 'Что бы изменить данные о сделке, нужно быть агентом недвижимости')
            return redirect('deal', title_slug=self.kwargs.get(self.slug_url_kwarg), permanent=False)

        self.old_deal = self.get_object()

        if (self.old_deal.completed_type == models.Deal.DealCompletedType.SUCCESS or
            self.old_deal.completed_type == models.Deal.DealCompletedType.REJECTED):
            messages.error(request, 'Нельзя изменять уже завершенные сделки')
            return redirect('deal', title_slug=self.kwargs.get(self.slug_url_kwarg), permanent=False)

        if isinstance(self.old_deal, HttpResponseRedirect):
            return self.old_deal

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        try:
            object_deal = self.model.objects.get(title_slug=self.kwargs.get(self.slug_url_kwarg))
        except ObjectDoesNotExist:
            messages.error(self.request, 'Сделка не найден')
            return redirect('deal_list', permanent=False)

        return object_deal

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        form = self.get_form()

        if 'project_document' not in form.files and int(form.data.get('type')) == models.Deal.DealType.CONSTRUCTION:
            form.files = form.files.copy()
            form.files['project_document'] = context['form'].initial['project_document']

        if form.is_valid():
            return self.form_valid(form)
        else:
            context['form'] = form
            return render(request, self.template_name, context=context)

    def form_valid(self, form):
        try:
            real_estate_deal = models.RealEstate.non_deleted.get(pk=int(form.cleaned_data.get('real_estate_deal_id')))
        except ObjectDoesNotExist:
            messages.error(self.request, 'Недвижимость по данному номеру не существует')
            return redirect('deal_list', permanent=False)

        if real_estate_deal != self.old_deal.real_estate_deal and models.Deal.non_deleted.filter(
            Q(real_estate_deal=real_estate_deal)
            & ~Q(completed_type=models.Deal.DealCompletedType.SUCCESS)
            & ~Q(completed_type=models.Deal.DealCompletedType.REJECTED)
        ).exists():
            messages.error(self.request, 'На одну недвижимость может существовать только одна активная сделка')
            return redirect('deal_list', permanent=False)

        try:
            agent = user_models.User.objects.get(
                username=form.cleaned_data.get('agent_username').strip(),
                is_staff=True
            )
        except ObjectDoesNotExist:
            messages.error(self.request, 'Агент недвижимости с данным логином не существует')
            return redirect('deal_list', permanent=False)

        type_deal = int(form.cleaned_data.get('type'))

        if type_deal == models.Deal.DealType.CONSTRUCTION and real_estate_deal.type == models.RealEstate.RealEstateType.PLOT:
            messages.error(self.request, 'Нельзя сделать сделку строительства для участка')
            return redirect('deal_change', title_slug=self.kwargs.get(self.slug_url_kwarg), permanent=False)

        old_type = self.old_deal.type
        self.old_deal.title = form.cleaned_data.get('title')
        self.old_deal.type = type_deal
        if self.old_deal.current_price != form.cleaned_data.get('price'):
            models.ChangePrices.objects.create(
                deal_price=self.old_deal,
                price=self.old_deal.current_price,
            )
            self.old_deal.current_price = form.cleaned_data.get('price')
        self.old_deal.real_estate_deal = real_estate_deal
        self.old_deal.agent = agent
        self.old_deal.save()

        if type_deal == models.Deal.DealType.SALE:
            if type_deal != old_type:
                self.__del_extend_data(old_type)
        elif type_deal == models.Deal.DealType.RENT:
            if type_deal == old_type:
                old_data_rental = models.DataRental.objects.get(deal_rental=self.old_deal)
                old_data_rental.price_housing_and_municipalities = form.cleaned_data.get('price_housing_and_municipalities')
                old_data_rental.prepayment = form.cleaned_data.get('prepayment')
                old_data_rental.rental_period_days = form.cleaned_data.get('rental_period_days')
                old_data_rental.save()
            else:
                self.__del_extend_data(old_type)
                models.DataHouse.objects.create(
                    deal_rental=self.old_deal,
                    price_housing_and_municipalities=form.cleaned_data.get('price_housing_and_municipalities'),
                    prepayment=form.cleaned_data.get('prepayment'),
                    rental_period_days=form.cleaned_data.get('rental_period_days'),
                )
        elif type_deal == models.Deal.DealType.CONSTRUCTION:
            if type_deal == old_type:
                old_data_construction = models.DataConstruction.objects.get(deal_construction=self.old_deal)
                old_data_construction.construction_company = form.cleaned_data.get('construction_company')
                old_data_construction.approximate_dates = form.cleaned_data.get('approximate_dates')
                if old_data_construction.project_document != form.cleaned_data.get('project_document'):
                    old_data_construction.project_document = form.cleaned_data.get('project_document')
                old_data_construction.save()
            else:
                self.__del_extend_data(old_type)
                models.DataPlot.objects.create(
                    deal_construction=self.old_deal,
                    construction_company=form.cleaned_data.get('construction_company'),
                    approximate_dates=form.cleaned_data.get('approximate_dates'),
                    project_document=form.cleaned_data.get('project_document'),
                )

        messages.success(self.request, 'Сделка была успешно изменена')

        return redirect('deal', title_slug=self.old_deal.title_slug, permanent=False)

    def __del_extend_data(self, type_data):
        if type_data == models.Deal.DealType.RENT:
            models.DataRental.objects.get(deal_rental=self.old_deal).delete()
        elif type_data == models.Deal.DealType.CONSTRUCTION :
            models.DataConstruction.objects.get(deal_construction=self.old_deal).delete()


class StartDeal(FormView):
    model = models.Deal
    form_class = forms.StartDealForm
    template_name = 'real_estate_agency/start_deal.html'
    slug_url_kwarg = 'title_slug'
    current_deal = None

    def get_context_data(self, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': 'Начать сделку',
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.warning(request, 'Что бы начать сделку, нужно авторизоваться')
            return redirect('login', permanent=False)

        if not self.request.user.is_staff:
            messages.error(request, 'Что бы начать сделку, нужно быть агентом недвижимости')
            return redirect('home', permanent=False)

        try:
            self.current_deal = models.Deal.objects.get(title_slug=self.kwargs.get(self.slug_url_kwarg))
        except ObjectDoesNotExist:
            messages.error(request, 'Сделки не существует')
            return redirect('deal_list', permanent=False)

        if self.current_deal.completed_type != models.Deal.DealCompletedType.CLIENT_SEARCH:
            messages.error(request, 'Сделка должна быть в статусе "Поиск клиента", чтобы совершить это действие')
            return redirect('deal', title_slug=self.kwargs.get(self.slug_url_kwarg), permanent=False)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            deal_with = user_models.User.objects.get(username=form.cleaned_data.get('deal_with').strip())
        except ObjectDoesNotExist:
            messages.error(self.request, 'Пользователь не найден')
            return redirect('start_deal', title_slug=self.kwargs.get(self.slug_url_kwarg), permanent=False)

        self.current_deal.completed_type = models.Deal.DealCompletedType.IN_PROGRESS
        self.current_deal.deal_with = deal_with
        self.current_deal.save()

        messages.success(self.request, 'Сделка была начата успешно')

        return redirect('deal', title_slug=self.kwargs.get(self.slug_url_kwarg), permanent=False)


class SuccessDeal(FormView):
    model = models.Deal
    form_class = forms.SuccessDealForm
    template_name = 'real_estate_agency/success_deal.html'
    slug_url_kwarg = 'title_slug'
    current_deal = None

    def get_context_data(self, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': 'Завершить сделку',
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.warning(request, 'Что бы завершить сделку, нужно авторизоваться')
            return redirect('login', permanent=False)

        if not self.request.user.is_staff:
            messages.error(request, 'Что бы завершить сделку, нужно быть агентом недвижимости')
            return redirect('home', permanent=False)

        try:
            self.current_deal = models.Deal.objects.get(title_slug=self.kwargs.get(self.slug_url_kwarg))
        except ObjectDoesNotExist:
            messages.error(request, 'Сделки не существует')
            return redirect('deal_list', permanent=False)

        if self.current_deal.completed_type != models.Deal.DealCompletedType.IN_PROGRESS:
            messages.error(request, 'Сделка должна быть в статусе "В процессе совершения", чтобы совершить это действие')
            return redirect('deal', title_slug=self.kwargs.get(self.slug_url_kwarg), permanent=False)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.current_deal.completed_type = models.Deal.DealCompletedType.SUCCESS
        self.current_deal.completion_document = form.cleaned_data.get('deal_document')
        self.current_deal.save()

        messages.success(self.request, 'Сделка была завершена успешно')

        return redirect('deal', title_slug=self.kwargs.get(self.slug_url_kwarg), permanent=False)


class TrackDealView(ListView):
    paginate_by = 10
    model = models.TrackDeal
    template_name = 'real_estate_agency/my_track_deal_list.html'
    context_object_name = 'track_deal_list'

    def get_context_data(self, *, object_list=None, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': 'Список отслеживаемых сделок',
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            messages.warning(request, 'Вам необходимо авторизоваться, чтобы просмотреть список отслеживаемых сделок')
            return redirect('login', permanent=False)

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = models.TrackDeal.objects.filter(who_track=self.request.user)
        return queryset


class DealStatistics(FormView):
    model = models.Deal
    form_class = forms.DealStatisticsFilterForm
    template_name = 'real_estate_agency/download_deal_statistics.html'

    def get_context_data(self, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': f'Скачать статистику сделок',
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.warning(request, 'Что бы скачивать статистику сделок, нужно авторизоваться')
            return redirect('login', permanent=False)

        if not self.request.user.is_superuser and not self.request.user.is_staff:
            messages.error(request, 'Что бы скачивать статистику сделок, нужно быть персоналом')
            return redirect('home', permanent=False)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        deleted_deal = form.cleaned_data.get('deleted_deal')
        if deleted_deal:
            queryset = models.Deal.objects.filter()
        else:
            queryset = models.Deal.non_deleted.filter()

        type_deal = form.cleaned_data.get('type_deal')
        if type_deal:
            type_deal = int(type_deal)
            if type_deal == models.Deal.DealType.SALE:
                queryset = queryset.filter(type=models.Deal.DealType.SALE)
            elif type_deal == models.Deal.DealType.RENT:
                queryset = queryset.filter(type=models.Deal.DealType.RENT)
            elif type_deal == models.Deal.DealType.CONSTRUCTION:
                queryset = queryset.filter(type=models.Deal.DealType.CONSTRUCTION)
                construction_company = form.cleaned_data.get('construction_company')
                if construction_company:
                    queryset = queryset.filter(deal_construction_fk__construction_company__icontains=construction_company)

        date_create_start = form.cleaned_data.get('date_create_start')
        date_create_end = form.cleaned_data.get('date_create_end')
        price_min = form.cleaned_data.get('price_min')
        price_max = form.cleaned_data.get('price_max')
        completed_type_status = form.cleaned_data.get('completed_type_status')
        agent_username = form.cleaned_data.get('agent_username')
        deal_with = form.cleaned_data.get('deal_with')
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

        if completed_type_status:
            completed_type_status = int(completed_type_status)
            if completed_type_status == models.Deal.DealCompletedType.CLIENT_SEARCH:
                queryset = queryset.filter(completed_type=models.Deal.DealCompletedType.CLIENT_SEARCH)
            elif completed_type_status == models.Deal.DealCompletedType.IN_PROGRESS:
                queryset = queryset.filter(completed_type=models.Deal.DealCompletedType.IN_PROGRESS)
            elif completed_type_status == models.Deal.DealCompletedType.SUCCESS:
                queryset = queryset.filter(completed_type=models.Deal.DealCompletedType.SUCCESS)
            elif completed_type_status == models.Deal.DealCompletedType.REJECTED:
                queryset = queryset.filter(completed_type=models.Deal.DealCompletedType.REJECTED)

        if agent_username:
            queryset = queryset.filter(agent__username=agent_username)

        if deal_with:
            queryset = queryset.filter(deal_with__username=deal_with)

        if real_estate_deal_id:
            queryset = queryset.filter(real_estate_deal__pk=int(real_estate_deal_id))

        if type_real_estate:
            type_real_estate = int(type_real_estate)
            if type_real_estate == models.RealEstate.RealEstateType.APARTMENT:
                queryset = queryset.filter(real_estate_deal__type=models.RealEstate.RealEstateType.APARTMENT)
            elif type_real_estate == models.RealEstate.RealEstateType.HOUSE:
                queryset = queryset.filter(real_estate_deal__type=models.RealEstate.RealEstateType.HOUSE)
            elif type_real_estate == models.RealEstate.RealEstateType.PLOT:
                queryset = queryset.filter(real_estate_deal__type=models.RealEstate.RealEstateType.PLOT)

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

        deal_type = models.Deal.DealType
        completed_deal_type = models.Deal.DealCompletedType
        real_estate_type = models.RealEstate.RealEstateType

        for id_table, deal in enumerate(queryset):
            writer.writerow((id_table, deal.title, deal_type(deal.type).label, real_estate_type(deal.real_estate_deal.type).label, deal.real_estate_deal.square,
                             deal.current_price, deal.real_estate_deal.pk, deal.agent.username,
                             completed_deal_type(deal.completed_type).label, deal.date_create,))

        return response


class RealEstateStatistics(FormView):
    model = models.RealEstate
    form_class = forms.RealEstateStatisticsFilterForm
    template_name = 'real_estate_agency/download_real_estate_statistics.html'

    def get_context_data(self, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': 'Скачать статистику недвижимости',
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.warning(request, 'Что бы импортировать данные недвижимость, нужно авторизоваться')
            return redirect('login', permanent=False)

        if not self.request.user.is_superuser and not self.request.user.is_staff:
            messages.error(request, 'Что бы импортировать данные недвижимость, нужно быть персоналом')
            return redirect('home', permanent=False)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        queryset = models.RealEstate.non_deleted.filter()

        type_real_estate = form.cleaned_data.get('type_real_estate')
        if type_real_estate:
            type_real_estate = int(type_real_estate)
            if type_real_estate == models.RealEstate.RealEstateType.APARTMENT:
                queryset = queryset.filter(type=models.RealEstate.RealEstateType.APARTMENT)

                apartment_number_storeys_min = form.cleaned_data.get('apartment_number_storeys_min')
                apartment_number_storeys_max = form.cleaned_data.get('apartment_number_storeys_max')
                apartment_floor_min = form.cleaned_data.get('apartment_floor_min')
                apartment_floor_max = form.cleaned_data.get('apartment_floor_max')
                apartment_balcony = form.cleaned_data.get('apartment_balcony')
                apartment_furniture = form.cleaned_data.get('apartment_furniture')

                apartment_year_construction_min = form.cleaned_data.get('apartment_year_construction_min')
                apartment_year_construction_max = form.cleaned_data.get('apartment_year_construction_max')
                apartment_accident_rate = form.cleaned_data.get('apartment_accident_rate')
                apartment_room_type = form.cleaned_data.get('apartment_room_type')

                if apartment_number_storeys_min:
                    queryset = queryset.filter(real_estate_DA_fk__number_storeys__gte=apartment_number_storeys_min)

                if apartment_number_storeys_max:
                    queryset = queryset.filter(real_estate_DA_fk__number_storeys__lte=apartment_number_storeys_max)

                if apartment_floor_min:
                    queryset = queryset.filter(real_estate_DA_fk__floor__gte=apartment_floor_min)

                if apartment_floor_max:
                    queryset = queryset.filter(real_estate_DA_fk__floor__lte=apartment_floor_max)


                if apartment_year_construction_min:
                    queryset = queryset.filter(real_estate_DA_fk__year_construction__gte=apartment_year_construction_min)

                if apartment_year_construction_max:
                    queryset = queryset.filter(real_estate_DA_fk__year_construction__lte=apartment_year_construction_max)

                if apartment_balcony:
                    apartment_balcony = int(apartment_balcony)
                    if apartment_balcony == self.form_class.BoolFieldChoice.YES:
                        queryset = queryset.filter(real_estate_DA_fk__balcony=True)
                    elif apartment_balcony == self.form_class.BoolFieldChoice.NO:
                        queryset = queryset.filter(real_estate_DA_fk__balcony=False)

                if apartment_furniture:
                    apartment_furniture = int(apartment_furniture)
                    if apartment_furniture == self.form_class.BoolFieldChoice.YES:
                        queryset = queryset.filter(real_estate_DA_fk__furniture=True)
                    elif apartment_furniture == self.form_class.BoolFieldChoice.NO:
                        queryset = queryset.filter(real_estate_DA_fk__furniture=False)

                if apartment_accident_rate:
                    apartment_accident_rate = int(apartment_accident_rate)
                    if apartment_accident_rate == self.form_class.BoolFieldChoice.YES:
                        queryset = queryset.filter(real_estate_DA_fk__accident_rate=True)
                    elif apartment_accident_rate == self.form_class.BoolFieldChoice.NO:
                        queryset = queryset.filter(real_estate_DA_fk__accident_rate=False)

                if apartment_room_type:
                    apartment_room_type = int(apartment_room_type)
                    if 0 <= apartment_furniture <= len(models.DataApartment.RoomType.choices):
                        queryset = queryset.filter(real_estate_DA_fk__room_type=apartment_room_type)
            elif type_real_estate == models.RealEstate.RealEstateType.HOUSE:
                queryset = queryset.filter(type=models.RealEstate.RealEstateType.HOUSE)

                house_number_storeys_min = form.cleaned_data.get('house_number_storeys_min')
                house_number_storeys_max = form.cleaned_data.get('house_number_storeys_max')
                house_area_min = form.cleaned_data.get('house_area_min')
                house_area_max = form.cleaned_data.get('house_area_max')
                house_year_construction_min = form.cleaned_data.get('house_year_construction_min')
                house_year_construction_max = form.cleaned_data.get('house_year_construction_max')
                house_garage = form.cleaned_data.get('house_garage')
                house_communications = form.cleaned_data.get('house_communications')

                if house_number_storeys_min:
                    queryset = queryset.filter(real_estate_DH_fk__number_storeys__gte=house_number_storeys_min)

                if house_number_storeys_max:
                    queryset = queryset.filter(real_estate_DH_fk__number_storeys__lte=house_number_storeys_max)

                if house_area_min:
                    queryset = queryset.filter(real_estate_DH_fk__house_area__gte=house_area_min)

                if house_area_max:
                    queryset = queryset.filter(real_estate_DH_fk__house_area__lte=house_area_max)

                if house_year_construction_min:
                    queryset = queryset.filter(real_estate_DH_fk__year_construction__gte=house_year_construction_min)

                if house_year_construction_max:
                    queryset = queryset.filter(real_estate_DH_fk__year_construction__lte=house_year_construction_max)

                if house_garage:
                    house_garage = int(house_garage)
                    if house_garage == self.form_class.BoolFieldChoice.YES:
                        queryset = queryset.filter(real_estate_DH_fk__garage=True)
                    elif house_garage == self.form_class.BoolFieldChoice.NO:
                        queryset = queryset.filter(real_estate_DH_fk__garage=False)

                if house_communications:
                    house_communications = int(house_communications)
                    if house_communications == self.form_class.BoolFieldChoice.YES:
                        queryset = queryset.filter(real_estate_DH_fk__communications=True)
                    elif house_communications == self.form_class.BoolFieldChoice.NO:
                        queryset = queryset.filter(real_estate_DH_fk__communications=False)
            elif type_real_estate == models.RealEstate.RealEstateType.PLOT:
                queryset = queryset.filter(type=models.RealEstate.RealEstateType.PLOT)

                plot_buildings = form.cleaned_data.get('plot_buildings')
                plot_communications = form.cleaned_data.get('plot_communications')

                if plot_buildings:
                    plot_buildings = int(plot_buildings)
                    if plot_buildings == self.form_class.BoolFieldChoice.YES:
                        queryset = queryset.filter(real_estate_DH_fk__buildings=True)
                    elif plot_buildings == self.form_class.BoolFieldChoice.NO:
                        queryset = queryset.filter(real_estate_DH_fk__buildings=False)

                if plot_communications:
                    plot_communications = int(plot_communications)
                    if plot_communications == self.form_class.BoolFieldChoice.YES:
                        queryset = queryset.filter(real_estate_DP_fk__communications=True)
                    elif plot_communications == self.form_class.BoolFieldChoice.NO:
                        queryset = queryset.filter(real_estate_DP_fk__communications=False)

        square_min = form.cleaned_data.get('square_min')
        square_max = form.cleaned_data.get('square_max')
        when_added_min = form.cleaned_data.get('when_added_min')
        when_added_max = form.cleaned_data.get('when_added_max')

        if square_min:
            queryset = queryset.filter(square__gte=square_min)

        if square_max:
            queryset = queryset.filter(square__lte=square_max)

        if when_added_min:
            queryset = queryset.filter(when_added__gte=when_added_min)

        if when_added_max:
            queryset = queryset.filter(when_added__lte=when_added_max)

        # csv
        response = HttpResponse(content_type='text/csv')
        current_time = timezone.now()

        response['Content-Disposition'] = f'attachment; filename="real-estate-data-{current_time.strftime("%Y-%m-%d_%H-%M-%S")}.csv"'

        writer = csv.writer(response)
        writer.writerow(('Номер', 'Тип недвижимости', 'Площадь', 'Адрес', 'Дата добавления',))

        real_estate_type = models.RealEstate.RealEstateType

        for id_table, real_estate in enumerate(queryset):
            writer.writerow((id_table, real_estate_type(real_estate.type).label, real_estate.square,
                             str(real_estate.address_real_estate) if real_estate.address_real_estate else 'Нет (шаблон)',
                             real_estate.when_added,))

        return response


class RealtorStatistics(FormView):
    model = models.Realtor
    form_class = forms.RealtorStatisticsFilterForm
    template_name = 'real_estate_agency/download_realtor_statistics.html'

    def get_context_data(self, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': 'Скачать статистику риэлтеров',
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.warning(request, 'Что бы импортировать данные реэлтеров, нужно авторизоваться')
            return redirect('login', permanent=False)

        if not self.request.user.is_superuser and not self.request.user.is_staff:
            messages.error(request, 'Что бы импортировать данные реэлтеров, нужно быть персоналом')
            return redirect('home', permanent=False)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        queryset = models.Realtor.objects.filter()

        experience_min = form.cleaned_data.get('experience_min')
        experience_max = form.cleaned_data.get('experience_max')
        price_min = form.cleaned_data.get('price_min')
        price_max = form.cleaned_data.get('price_max')

        if experience_min:
            queryset = queryset.filter(experience=experience_min)

        if experience_max:
            queryset = queryset.filter(experience=experience_max)

        if price_min:
            queryset = queryset.filter(price__gte=price_min)

        if price_max:
            queryset = queryset.filter(price__lte=price_max)

        # csv
        response = HttpResponse(content_type='text/csv')
        current_time = timezone.now()

        response['Content-Disposition'] = f'attachment; filename="realtor-data-{current_time.strftime("%Y-%m-%d_%H-%M-%S")}.csv"'

        writer = csv.writer(response)
        writer.writerow(('Номер', 'ФИО', 'Опыт (месяцы)', 'Телефон', 'Почта', 'Цена',))

        for id_table, realtor in enumerate(queryset):
            writer.writerow((id_table,
                             ' '.join((realtor.first_name, realtor.last_name, realtor.patronymic,)),
                             realtor.experience,
                             realtor.phone,
                             realtor.email,
                             realtor.price,))

        return response


class ReCreationDealView(NewDealView):
    slug_url_kwarg = 'title_slug'
    prototype_deal = None

    def get_context_data(self, *, object_list=None, **kwargs):
        base_context = super().get_context_data(**kwargs)
        context = {
            'title': 'Пересоздать сделку по прототипу',
        }

        initial_dict = {
            'title': self.prototype_deal.title,
            'type': self.prototype_deal.type,
            'price': self.prototype_deal.current_price,
            'real_estate_deal_id': self.prototype_deal.real_estate_deal.pk,
            'agent_username': self.prototype_deal.agent.username,
        }

        if self.prototype_deal.type == models.Deal.DealType.RENT:
            data_rental = models.DataRental.objects.get(deal_rental=self.prototype_deal)
            initial_dict['price_housing_and_municipalities'] = data_rental.price_housing_and_municipalities
            initial_dict['prepayment'] = data_rental.prepayment
            initial_dict['rental_period_days'] = data_rental.rental_period_days
        elif self.prototype_deal.type == models.Deal.DealType.CONSTRUCTION:
            data_construction = models.DataConstruction.objects.get(deal_construction=self.prototype_deal)
            initial_dict['construction_company'] = data_construction.construction_company
            initial_dict['approximate_dates'] = data_construction.approximate_dates
            initial_dict['project_document'] = data_construction.project_document

        context['form'] = self.form_class(initial=initial_dict)

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        try:
            self.prototype_deal = models.Deal.non_deleted.get(title_slug=self.kwargs.get(self.slug_url_kwarg))
        except ObjectDoesNotExist:
            messages.error(self.request, 'Сделка не найдена')
            return redirect('deal_list', permanent=False)

        return super().dispatch(request, *args, **kwargs)
