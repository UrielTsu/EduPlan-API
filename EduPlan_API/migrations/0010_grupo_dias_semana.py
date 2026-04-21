from django.db import migrations, models


def migrate_single_day_to_list(apps, schema_editor):
    Grupo = apps.get_model("EduPlan_API", "Grupo")

    for grupo in Grupo.objects.all():
        raw_day = (grupo.dia_semana or "").strip()
        grupo.dias_semana = [raw_day] if raw_day else []
        grupo.save(update_fields=["dias_semana"])


class Migration(migrations.Migration):

    dependencies = [
        ("EduPlan_API", "0009_grupo_dia_semana_grupo_hora_fin_grupo_hora_inicio"),
    ]

    operations = [
        migrations.AddField(
            model_name="grupo",
            name="dias_semana",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.RunPython(migrate_single_day_to_list, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="grupo",
            name="dia_semana",
        ),
    ]