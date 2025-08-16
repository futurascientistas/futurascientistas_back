from django.core.management.base import BaseCommand

from users.models import Estado, Raca, Deficiencia, TipoEnsino, TipoDeVaga
from users.models.school_transcript_model import Disciplina

class Command(BaseCommand):
    help = 'Popula dados iniciais fixos no banco (Tipos de Ensino, Raças e Deficiências)'

    def handle(self, *args, **options):

        #Disciplinas
        disciplinas = [
            "Matemática", "Português", "Ciências", "História", "Geografia",
            "Física", "Química", "Biologia", "Educação Física", "Artes",
            "Inglês", "Espanhol"
        ]

        for nome in disciplinas:
            obj, created = Disciplina.objects.get_or_create(nome=nome)
            if created:
                self.stdout.write(self.style.SUCCESS(f"✔ Tipo de Disciplina '{nome}' criado"))
            else:
                self.stdout.write(self.style.WARNING(f"ℹ Tipo de Disciplina '{nome}' já existe"))

        #Estados
        estados_data = [
            ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
            ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'),
            ('ES', 'Espírito Santo'), ('GO', 'Goiás'), ('MA', 'Maranhão'),
            ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
            ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'),
            ('PR', 'Paraná'), ('PE', 'Pernambuco'), ('PI', 'Piauí'),
            ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
            ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'),
            ('SC', 'Santa Catarina'), ('SP', 'São Paulo'), ('SE', 'Sergipe'),
            ('TO', 'Tocantins')
        ]

        for uf, nome in estados_data:
            obj, created = Estado.objects.get_or_create(uf=uf, nome=nome)
            if created:
                self.stdout.write(self.style.SUCCESS(f"✔ Tipo de Estado '{nome}' criado"))
            else:
                self.stdout.write(self.style.WARNING(f"ℹ Tipo de Estado '{nome}' já existe"))

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
                self.stdout.write(self.style.SUCCESS(f"✔ Tipo de Vaga '{nome}' criado"))
            else:
                self.stdout.write(self.style.WARNING(f"ℹ Tipo de Vaga '{nome}' já existe"))

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
