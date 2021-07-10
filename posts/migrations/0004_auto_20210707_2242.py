# Generated by Django 3.2.5 on 2021-07-07 16:57

import core.utils
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0003_auto_20210706_1505'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='comment_approved_by',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='comment_modified_at',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='email',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='name',
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='users.user', verbose_name='User'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='comment',
            name='comment_parent',
            field=models.BigIntegerField(blank=True, verbose_name='Comment Parent'),
        ),
        migrations.AlterField(
            model_name='post',
            name='categories',
            field=models.ManyToManyField(blank=True, to='posts.Category', verbose_name='Categories'),
        ),
        migrations.AlterField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(blank=True, to='posts.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='post',
            name='thumbnail',
            field=models.ImageField(blank=True, default='test.png', upload_to=core.utils.upload_image_path, verbose_name='Post Thumbnail'),
        ),
    ]