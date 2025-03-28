# Generated by Django 5.1.7 on 2025-03-28 14:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('staff', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='appeal',
            name='reviewed_appeal',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='reviewed_appeal_fk', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='appeal',
            name='write_appeal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='write_appeal_fk', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='complaint',
            name='reviewed_complaint',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='reviewed_complaint_fk', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='complaint',
            name='wrote_complaint',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='wrote_complaint_fk', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='complaint',
            constraint=models.CheckConstraint(condition=models.Q(('wrote_complaint__isnull', False), ('feedback_email__isnull', False), _connector='OR'), name='complaint_related_fields_CK'),
        ),
    ]
