from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyectos_matheu', '0002_alter_proyecto_documento_comentario'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentoArchivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('content', models.BinaryField()),
                ('content_type', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Archivo de documento',
                'verbose_name_plural': 'Archivos de documentos',
            },
        ),
    ]
