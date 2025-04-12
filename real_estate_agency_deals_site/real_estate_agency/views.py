from django.views.generic import CreateView, DetailView, UpdateView, ListView, FormView
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect
from real_estate_agency import models, forms
from django.db.models import F, Value
from django.shortcuts import redirect
from django.contrib import messages


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
            address_apartment_value = self.request.GET.get('address_apartment_value')

            if address_city_value:
                queryset = queryset.filter(address_real_estate__city=address_city_value)

            if address_district_value:
                queryset = queryset.filter(address_real_estate__district=address_district_value)

            if address_street_value:
                queryset = queryset.filter(address_real_estate__street=address_street_value)

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
            garage_house = self.request.GET.get('garage_house')  # TODO DEF {'' 'yes' 'no'}
            communications_house = self.request.GET.get('communications_house')  # TODO DEF {'' 'yes' 'no'}

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

            buildings_plot = self.request.GET.get('buildings_plot')  # TODO DEF {'' 'yes' 'no'}
            communications_plot = self.request.GET.get('communications_plot')  # TODO DEF {'' 'yes' 'no'}
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
        context: dict = {
            'title': 'Добавить недвижимость',
        }

        return {**base_context, **context}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.warning(request, 'Что бы добавить недвижимость, нужно авторизоваться')
            return redirect('real_estate_list', permanent=False)

        if not self.request.user.is_staff:
            messages.error(request, 'Что бы добавить недвижимость, нужно быть администратором')
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

        return redirect('real_estate_list', permanent=False)


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
            object_user = self.model.objects.get(pk=self.kwargs.get(self.pk_url_kwarg))
        except ObjectDoesNotExist:
            messages.error(self.request, 'Недвижимость не найден')
            return redirect('real_estate_list', permanent=False)

        return object_user


class ChangeRealEstateView(UpdateView):
    1
    # model = models.Realtor
    # form_class = forms.RealtorUpdateForm
    # template_name = 'real_estate_agency/realtor_change.html'
    # pk_url_kwarg = 'pk'
    # relater_view = None
    #
    # def get_context_data(self, **kwargs):
    #     base_context = super().get_context_data(**kwargs)
    #     context = {
    #         'title': f'Изменить данные риэлтера {self.relater_view.last_name} {self.relater_view.first_name} {self.relater_view.patronymic}',
    #     }
    #
    #     return {**base_context, **context}
    #
    #
    # def dispatch(self, request, *args, **kwargs):
    #     if self.request.user.is_anonymous:
    #         messages.warning(self.request, 'Чтобы изменить риэлтера необходимо авторизоваться')
    #         return redirect('login', permanent=False)
    #
    #     self.relater_view = self.get_object()
    #
    #     if isinstance(self.relater_view, HttpResponseRedirect):
    #         return self.relater_view
    #
    #     if not self.request.user.is_staff:
    #         messages.error(self.request, 'У вас нет прав для изменения данных этого риэлетора, вы должны быть администратором')
    #         return redirect('realtor_list', permanent=False)
    #
    #     return super().dispatch(request, *args, **kwargs)
    #
    # def get_object(self, queryset=None):
    #     try:
    #         relater = models.Realtor.objects.get(pk=self.kwargs.get(self.pk_url_kwarg))
    #     except ObjectDoesNotExist:
    #         messages.error(self.request, 'Реэлетор не найден')
    #         return redirect('realtor_list', permanent=False)
    #
    #     return relater
    #
    # def form_valid(self, form):
    #     form.save()
    #     messages.success(self.request, 'Успешный изменение реэлетера')
    #
    #     return redirect('realtor', self.kwargs.get(self.pk_url_kwarg), permanent=False)


