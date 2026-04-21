from django.db import migrations, models


def migrate_aula_estado_values(apps, schema_editor):
    Aula = apps.get_model("EduPlan_API", "Aula")
    Aula.objects.filter(estado="En uso").update(estado="Ocupado")


def revert_aula_estado_values(apps, schema_editor):
    Aula = apps.get_model("EduPlan_API", "Aula")
    Aula.objects.filter(estado="Ocupado").update(estado="En uso")


class Migration(migrations.Migration):

    dependencies = [
        ("EduPlan_API", "0006_estudiante_contacto_emergencia_nombre_and_more"),
    ]

    operations = [
        migrations.RunPython(migrate_aula_estado_values, revert_aula_estado_values),
        migrations.AlterField(
            model_name="aula",
            name="estado",
            field=models.CharField(
                choices=[
                    ("Disponible", "Disponible"),
                    ("Ocupado", "Ocupado"),
                    ("Fuera de servicio", "Fuera de servicio"),
                ],
                default="Disponible",
                max_length=20,
            ),
        ),
    ]