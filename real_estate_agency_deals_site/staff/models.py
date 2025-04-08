from real_estate_agency_deals_site.settings import AUTH_USER_MODEL
from django.db.models import Q
from django.db import models


class Complaint(models.Model):
    class Meta:
        verbose_name = 'Жалоба'
        verbose_name_plural = 'Жалобы'
        constraints = [
            models.CheckConstraint(
                check=Q(wrote_complaint__isnull=False) | Q(feedback_email__isnull=False),
                name='complaint_related_fields_CK',
            ),
        ]
        ordering = ('-date_write',)

    wrote_complaint = models.ForeignKey(AUTH_USER_MODEL, null=True, on_delete=models.PROTECT,
                                        related_name='wrote_complaint_fk')
    feedback_email = models.EmailField(null=True, verbose_name='Почта обратной связи')
    message = models.CharField(max_length=256, verbose_name='Жалоба')
    reviewed_complaint = models.ForeignKey(AUTH_USER_MODEL, null=True, on_delete=models.PROTECT,
                                           related_name='reviewed_complaint_fk')
    date_write = models.DateTimeField(auto_now_add=True)
    verdict = models.CharField(null=True, max_length=256, verbose_name='Вердикт')

    objects = models.Manager()


class Appeal(models.Model):
    class Meta:
        verbose_name = 'Апелляция'
        verbose_name_plural = 'Апелляции'
        ordering = ('-date_write',)

    write_appeal = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='write_appeal_fk')
    message = models.CharField(max_length=256, verbose_name='Апелляции')
    reviewed_appeal = models.ForeignKey(AUTH_USER_MODEL, null=True, on_delete=models.PROTECT,
                                        related_name='reviewed_appeal_fk')
    rejected = models.BooleanField(default=False)
    date_write = models.DateTimeField(auto_now_add=True)
    verdict = models.CharField(null=True, max_length=256, verbose_name='Вердикт')

    objects = models.Manager()
