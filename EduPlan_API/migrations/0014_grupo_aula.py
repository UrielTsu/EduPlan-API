from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("EduPlan_API", "0013_inscripcion"),
    ]

    operations = [
        migrations.AddField(
            model_name="grupo",
            name="aula",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="grupos", to="EduPlan_API.aula"),
        ),
    ]