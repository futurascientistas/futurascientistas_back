from django.core.management.base import BaseCommand
from users.models import Raca, Deficiencia, TipoEnsino, TipoDeVaga

class Command(BaseCommand):
    help = 'Popula dados iniciais fixos no banco (Tipos de Ensino, Raças e Deficiências)'

    def handle(self, *args, **options):
        #Tipo de Vaga
        tipos_de_vagas = [
            "Ampla Concorrência",
            "PPI (pretas, pardas, indígenas e quilombolas)",
            "Trans e Travestis",
            "PcD (pessoas com deficiência)"
        ]
        for nome in tipos_de_vagas:
            obj, created = TipoDeVaga.objects.get_or_create(nome=nome)
            if created:
                self.stdout.write(self.style.SUCCESS(f"✔ Tipo de Ensino '{nome}' criado"))
            else:
                self.stdout.write(self.style.WARNING(f"ℹ Tipo de Ensino '{nome}' já existe"))

        # Tipos de Ensino
        tipos_ensino = ["REGULAR", "INTEGRAL"]
        for nome in tipos_ensino:
            obj, created = TipoEnsino.objects.get_or_create(nome=nome)
            if created:
                self.stdout.write(self.style.SUCCESS(f"✔ Tipo de Ensino '{nome}' criado"))
            else:
                self.stdout.write(self.style.WARNING(f"ℹ Tipo de Ensino '{nome}' já existe"))

        # Raças
        racas = ["Branca", "Preta", "Parda", "Amarela", "Indígena"]
        for nome in racas:
            obj, created = Raca.objects.get_or_create(nome=nome)
            if created:
                self.stdout.write(self.style.SUCCESS(f"✔ Raça '{nome}' criada"))
            else:
                self.stdout.write(self.style.WARNING(f"ℹ Raça '{nome}' já existe"))

        # Deficiências
        deficiencias = [
            "Nenhuma",
            "Deficiência física",
            "Deficiência auditiva",
            "Deficiência visual",
            "Deficiência intelectual",
            "Deficiência múltipla",
            "Transtorno do espectro autista (TEA)"
        ]
        for nome in deficiencias:
            obj, created = Deficiencia.objects.get_or_create(nome=nome)
            if created:
                self.stdout.write(self.style.SUCCESS(f"✔ Deficiência '{nome}' criada"))
            else:
                self.stdout.write(self.style.WARNING(f"ℹ Deficiência '{nome}' já existe"))

        self.stdout.write(self.style.SUCCESS("🎉 Dados iniciais populados com sucesso!"))
