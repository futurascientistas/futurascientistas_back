import uuid
from django.db import models
from futuras_cientistas import settings


class HistoricoEscolar(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # historico_escolar = models.FileField("Upload do histórico escolar", null=True, blank=True)
    historico_escolar = models.CharField("ID do Histórico Escolar no Drive", max_length=255, null=True, blank=True)
    def __str__(self):
        return f"Histórico de {self.usuario.username}"

class Disciplina(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.nome

class Nota(models.Model):
    TIPOS_CONCEITO = [
        ("LETRAS", "Conceito em letras (MB, B, R, I)"),
        ("0-10", "Nota de 0 a 10"),
        ("0-25", "Nota de 0 a 25"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    historico = models.ForeignKey(HistoricoEscolar, related_name='notas', on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    valor = models.DecimalField("Nota normalizada (0-10)", max_digits=4, decimal_places=2, null=True, blank=True)
    bimestre = models.PositiveSmallIntegerField("Bimestre", choices=[(1, '1º'), (2, '2º')])

    tipo_conceito = models.CharField("Tipo de Conceito", max_length=10, choices=TIPOS_CONCEITO, default="LETRAS")
    nota_original = models.CharField("Nota informada", max_length=5, null=True, blank=True)

    class Meta:
        unique_together = ('historico', 'disciplina', 'bimestre')
        
    @property
    def nota_final_percentual(self):
        """
        Retorna a nota final desta disciplina em percentual (0 a 100).
        Baseia-se no campo 'valor', que é sempre normalizado para 0-10.
        """
        if self.valor is not None:
            return round(float(self.valor) * 10, 2)  # 10 equivale a 100%
        return None

    def save(self, *args, **kwargs):
        if not self.nota_original:
            # se não tem nota informada, só salva sem processar
            super().save(*args, **kwargs)
            return

        n = self.nota_original.strip().upper()

        if self.tipo_conceito == "LETRAS":
            mapping = {"MB": 9, "B": 7, "R": 6, "I": 5}
            if n not in mapping:
                raise ValueError("Informe MB, B, R ou I para notas do tipo LETRAS")
            self.valor = mapping[n]

        elif self.tipo_conceito == "0-10":
            try:
                num = float(n)
            except ValueError:
                raise ValueError("Informe um número válido para notas do tipo 0-10")
            if not 0 <= num <= 10:
                raise ValueError("Nota fora da escala 0-10")
            self.valor = num

        elif self.tipo_conceito == "0-25":
            try:
                num = float(n)
            except ValueError:
                raise ValueError("Informe um número válido para notas do tipo 0-25")
            if not 0 <= num <= 25:
                raise ValueError("Nota fora da escala 0-25")
            # normaliza para 0–10
            self.valor = round(num / 25 * 10, 2)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.disciplina.nome} - {self.bimestre}º Bimestre ({self.historico.usuario.username})"
