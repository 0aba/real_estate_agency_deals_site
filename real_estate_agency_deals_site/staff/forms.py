from real_estate_agency import models as real_estate_agency_models
from django.core.exceptions import ValidationError
from django import forms
from staff import models


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
                                  choices=real_estate_agency_models.Deal.DealType.choices,
                                  initial=real_estate_agency_models.Deal.DealType.SALE,
                                  label='Тип сделки')
    # DataConstruction
    construction_company = forms.CharField(required=False, max_length=256, label='Строительная компания')
    # end DataConstruction
    # DataRental
    rented = forms.ChoiceField(required=False, choices=RentalStatus.choices, initial=RentalStatus.RENTAL_ANY, label='Наличие аренды')
    # end DataRental

    date_create_start = forms.DateTimeField(required=False, label='Минимальная дата создание')
    date_create_end = forms.DateTimeField(required=False, label='Максимальная дата создания')
    price_min = forms.DateTimeField(required=False, label='Минимальная цена')
    price_max = forms.DateTimeField(required=False, label='Максимальная цена')
    completed_deal_status = forms.ChoiceField(required=False,
                                              choices=CompletedDealStatus.choices,
                                              initial=CompletedDealStatus.COMPLETED_ANY,
                                              label='Тип сделки')
    deleted_deal = forms.BooleanField(required=False, label='Учитывать удаленные')
    agent_username = forms.CharField(required=False, max_length=150, label='Кто ответственный')
    real_estate_deal_id = forms.IntegerField(required=False, label='С какой недвижимостью связано')

    type_real_estate = forms.ChoiceField(required=False,
                                         choices=real_estate_agency_models.RealEstate.RealEstateType.choices,
                                         initial=real_estate_agency_models.RealEstate.RealEstateType.APARTMENT,
                                         label='Тип недвижимости')
    square_min = forms.DateTimeField(required=False, label='Минимальная площадь')
    square_max = forms.DateTimeField(required=False, label='Максимальная площадь')
