# Generated by Django 4.2.9 on 2024-02-28 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_comment_dislikes_comment_likes_comment_parent_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='color',
            field=models.CharField(default='black', max_length=50),
        ),
    ]
