from real_estate_agency import models as real_estate_agency_models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django import forms
from staff import models


NONE = -1

class NewComplaintForm(forms.ModelForm):
    class Meta:
        model = models.Complaint
        fields = ('feedback_email', 'message',)

class NewComplaintAuthUserForm(forms.ModelForm):
    class Meta:
        model = models.Complaint
        fields = ('message',)


class ConsiderComplaintForm(forms.ModelForm):
    class Meta:
        model = models.Complaint
        fields = ('verdict',)


class NewAppealForm(forms.ModelForm):
    class Meta:
        model = models.Appeal
        fields = ('message',)
        exclude = ('write_appeal',)


class ConsiderAppealForm(forms.ModelForm):
    class Meta:
        model = models.Appeal
        fields = ('rejected', 'verdict',)
        exclude = ('reviewed_appeal',)


class DealStatisticsFilterForm(forms.Form):
    class CompletedDealStatus(models.models.IntegerChoices):
        COMPLETED_ANY = 1, 'Любые'
        COMPLETED_ONLY = 2, 'Только завершенные'
        COMPLETED_NONE = 3, 'Только не завершенные'

    class RentalStatus(models.models.IntegerChoices):
        RENTAL_ANY = 1, 'Любые'
        RENTAL_ONLY = 2, 'Только арендованные'
        RENTAL_NONE = 3, 'Только не арендованные'

    type_deal = forms.ChoiceField(required=False,
                                  choices=(real_estate_agency_models.Deal.DealType.choices + [(NONE, 'Любой тип',)]),
                                  initial=NONE,
                                  label='Тип сделки')
    # DataConstruction
    construction_company = forms.CharField(required=False, max_length=256, label='Строительная компания')
    # end DataConstruction
    # DataRental
    rented = forms.ChoiceField(required=False, choices=RentalStatus.choices, initial=RentalStatus.RENTAL_ANY, label='Наличие аренды')
    # end DataRental

    date_create_start = forms.DateTimeField(required=False, label='Минимальная дата создание')
    date_create_end = forms.DateTimeField(required=False, label='Максимальная дата создания')
    price_min = forms.DecimalField(required=False, max_digits=10, decimal_places=2, label='Минимальная цена')
    price_max = forms.DecimalField(required=False, max_digits=10, decimal_places=2, label='Максимальная цена')
    completed_deal_status = forms.ChoiceField(required=False,
                                              choices=CompletedDealStatus.choices,
                                              initial=CompletedDealStatus.COMPLETED_ANY,
                                              label='Тип сделки')
    deleted_deal = forms.BooleanField(required=False, label='Учитывать удаленные')
    agent_username = forms.CharField(required=False, max_length=150, label='Кто ответственный')
    real_estate_deal_id = forms.IntegerField(required=False, label='С какой недвижимостью связано')

    type_real_estate = forms.ChoiceField(required=False,
                                         choices=(real_estate_agency_models.RealEstate.RealEstateType.choices + [(NONE, 'Любой тип',)]),
                                         initial=NONE,
                                         label='Тип недвижимости')
    square_min = forms.IntegerField(required=False, validators=[MinValueValidator(1)], label='Минимальная площадь')
    square_max = forms.IntegerField(required=False, validators=[MinValueValidator(1)], label='Максимальная площадь')


class ImportRealEstateDataFilterForm(forms.Form):
    class BoolFieldChoice(models.models.IntegerChoices):
        NONE = -1, 'Без разницы'
        YES = 0, 'С'
        NO = 1, 'Без'

    type_real_estate = forms.ChoiceField(required=False,
                                         choices=(real_estate_agency_models.RealEstate.RealEstateType.choices + [(NONE, 'Любой тип',)]),
                                         initial=NONE,
                                         label='Тип сделки')
    # DataPlot
    plot_buildings = forms.ChoiceField(required=False,
                                       choices=BoolFieldChoice.choices,
                                       initial=BoolFieldChoice.NONE,
                                       label='Есть постройки')
    plot_communications = forms.ChoiceField(required=False,
                                            choices=BoolFieldChoice.choices,
                                            initial=BoolFieldChoice.NONE,
                                            label='Есть коммуникации')
    # end DataPlot
    # DataApartment
    apartment_number_storeys_min = forms.IntegerField(required=False, validators=[MinValueValidator(1)], label='Количество этажей у дома минимум')
    apartment_number_storeys_max = forms.IntegerField(required=False, validators=[MinValueValidator(1)], label='Количество этажей у дома максимум')
    apartment_floor_min = forms.IntegerField(required=False, validators=[MinValueValidator(1)], label='Этаж минимум')
    apartment_floor_max = forms.IntegerField(required=False, validators=[MinValueValidator(1)], label='Этаж максимум')
    apartment_balcony = forms.ChoiceField(required=False,
                                          choices=BoolFieldChoice.choices,
                                          initial=BoolFieldChoice.NONE,
                                          label='Есть балкон')
    apartment_furniture = forms.ChoiceField(required=False,
                                           choices=BoolFieldChoice.choices,
                                           initial=BoolFieldChoice.NONE,
                                           label='Есть мебель')
    apartment_year_construction_min = forms.IntegerField(required=False, validators=[MinValueValidator(1900), MaxValueValidator(2**15)], label='Год постройки минимум')
    apartment_year_construction_max = forms.IntegerField(required=False, validators=[MinValueValidator(1900), MaxValueValidator(2**15)], label='Год постройки максимум')
    apartment_accident_rate = forms.ChoiceField(required=False,
                                                choices=BoolFieldChoice.choices,
                                                initial=BoolFieldChoice.NONE,
                                                label='Есть аварийность')
    apartment_room_type = forms.ChoiceField(required=False,
                                            choices=(real_estate_agency_models.DataApartment.RoomType   .choices + [(NONE, 'Любой тип',)]),
                                            initial=NONE,
                                            label='Тип комнаты')
    # end DataApartment
    # DataHouse
    house_number_storeys_min = forms.IntegerField(required=False, validators=[MinValueValidator(1)], label='Количество этажей минимум')
    house_number_storeys_max = forms.IntegerField(required=False, validators=[MinValueValidator(1)], label='Количество этажей максимум')
    house_area_min = forms.IntegerField(required=False, validators=[MinValueValidator(1)], label='Площадь дома минимум')
    house_area_max = forms.IntegerField(required=False, validators=[MinValueValidator(1)], label='Площадь дома максимум')
    house_year_construction_min = forms.IntegerField(required=False,
                                                     validators=[MinValueValidator(1900), MaxValueValidator(2 ** 15)],
                                                     label='Год постройки дома минимум')
    house_year_construction_max = forms.IntegerField(required=False,
                                                    validators=[MinValueValidator(1900), MaxValueValidator(2 ** 15)],
                                                    label='Год постройки дома максимум')
    house_garage = forms.ChoiceField(required=False,
                                     choices=BoolFieldChoice.choices,
                                     initial=BoolFieldChoice.NONE,
                                     label='Есть гараж')
    house_communications = forms.ChoiceField(required=False,
                                            choices=BoolFieldChoice.choices,
                                            initial=BoolFieldChoice.NONE,
                                            label='Есть коммуникации')
    # end DataHouse
    square_min = forms.DateTimeField(required=False, label='Минимальная площадь')
    square_max = forms.DateTimeField(required=False, label='Максимальная площадь')
    when_added_min = forms.DateTimeField(required=False, label='Была добавлена с')
    when_added_max = forms.DateTimeField(required=False, label='Была добавлена до')


class ImportRealtorDataFilterForm(forms.Form):
    experience_min = forms.IntegerField(required=False,
                                        validators=[MinValueValidator(0)],
                                        label='Опыт минимум месяцев')
    experience_max = forms.IntegerField(required=False,
                                        validators=[MinValueValidator(0)],
                                        label='Опыт максимум месяцев')
    price_min = forms.DecimalField(required=False, max_digits=10, decimal_places=2, label='Минимальная цена')
    price_max = forms.DecimalField(required=False, max_digits=10, decimal_places=2, label='Максимальная цена')
