from django import forms
from staff import models


class NewComplaintForm(forms.ModelForm):
    class Meta:
        model = models.Complaint
        fields = ('feedback_email', 'message',)

    message = forms.CharField(
        widget=forms.Textarea,
        max_length=256,
        label='Жалоба'
    )

class NewComplaintAuthUserForm(forms.ModelForm):
    class Meta:
        model = models.Complaint
        fields = ('message',)

    message = forms.CharField(
        widget=forms.Textarea,
        max_length=256,
        label='Жалоба'
    )


class ConsiderComplaintForm(forms.ModelForm):
    class Meta:
        model = models.Complaint
        fields = ('verdict',)

    verdict = forms.CharField(
        widget=forms.Textarea,
        max_length=256,
        label='Вердикт'
    )


class NewAppealForm(forms.ModelForm):
    class Meta:
        model = models.Appeal
        fields = ('message',)
        exclude = ('write_appeal',)

    message = forms.CharField(
        widget=forms.Textarea,
        max_length=256,
        label='Апелляция'
    )


class ConsiderAppealForm(forms.ModelForm):
    class Meta:
        model = models.Appeal
        fields = ('rejected', 'verdict',)
        exclude = ('reviewed_appeal',)

    verdict = forms.CharField(
        widget=forms.Textarea,
        max_length=256,
        label='Вердикт'
    )
