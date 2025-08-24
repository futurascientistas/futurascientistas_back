# core/migrations/0002_view_cidades.py

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        # Adicione a dependência do app 'localizacao' aqui
        ('core', '0001_initial'), 
    ]

    operations = [
        migrations.RunSQL(
            """
            CREATE MATERIALIZED VIEW cidades_materialized_view AS
            SELECT
                c.id AS id,
                c.nome AS nome,
                e.nome AS estado_nome,
                e.uf AS estado_uf
            FROM
                core_cidade AS c
            JOIN
                core_estado AS e
            ON c.estado_id = e.id;
            """,
            """
            DROP MATERIALIZED VIEW cidades_materialized_view;
            """
        ),
    ]