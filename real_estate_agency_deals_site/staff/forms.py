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
        fields = ('verdict',)
        exclude = ('reviewed_appeal',)
