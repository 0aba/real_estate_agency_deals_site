from real_estate_agency import models
from django import forms


class RealEstateAgencyCreationForm(forms.ModelForm):
    class Meta:
        model = models.RealEstateAgency
        fields = ('name', 'INN',)
        exclude = ('representative',)


class RealEstateAgencyUpdateForm(forms.ModelForm):
    class Meta:
        model = models.RealEstateAgency
        fields = ('logo', 'name', 'INN', 'about',)


class ReviewAgencyCreationForm(forms.ModelForm):
    class Meta:
        model = models.ReviewAgency
        fields = ('message', 'grade',)
        exclude = ('review_agency', 'wrote_review',)

    grade = forms.DecimalField(widget=forms.NumberInput(attrs={'min': '0', 'max': '5', 'step': '0.1'}), label='Оценка')


class ReviewAgencyUpdateForm(forms.ModelForm):
    class Meta:
        model = models.ReviewAgency
        fields = ('message', 'grade',)

    grade = forms.DecimalField(widget=forms.NumberInput(attrs={'min': '0', 'max': '5', 'step': '0.1'}), label='Оценка')


class RealtorCreationForm(forms.ModelForm):
    class Meta:
        model = models.Realtor
        fields = ('last_name', 'first_name', 'patronymic', 'phone', 'email', 'price', 'license',)
        exclude = ('agency_realtor',)


class RealtorUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Realtor
        fields = ('last_name', 'first_name', 'patronymic', 'photo', 'experience', 'phone', 'email', 'price', 'license',)
