from celery import shared_task
from django.utils import timezone
from django.db import transaction
import logging
from projects.models import Project
from applications.models import Application
from users.models import User
from applications.services import *
from datetime import timedelta


logger = logging.getLogger(__name__)

@shared_task
def atualizar_status_projetos():
    hoje = timezone.now()
    logger.info(f"Iniciando atualização de status de projetos em {hoje}")

    with transaction.atomic():
        # 1. Rascunho → Inscrições Abertas
        rascunhos = Project.objects.filter(status='rascunho', inicio_inscricoes__lte=hoje)
        for projeto in rascunhos:
            projeto.status = 'inscricoes_abertas'
            projeto.save(update_fields=['status'])
            logger.info(f"{projeto.nome} atualizado para 'inscricoes_abertas'")

        # 2. Inscrições Abertas → Avaliação das Inscrições
        encerrando = Project.objects.filter(status='inscricoes_abertas', fim_inscricoes__lte=hoje)
        for projeto in encerrando:
            projeto.status = 'avaliacao_inscricoes'
            projeto.save(update_fields=['status'])
            logger.info(f"{projeto.nome} atualizado para 'avaliacao_inscricoes'")

        # 3. Avaliação das Inscrições → Inscrições Aprovadas
        aprovando = Project.objects.filter(
            status='avaliacao_inscricoes',
            data_divulgacao_resultado__isnull=False,
            data_divulgacao_resultado__lte=hoje
        )
        for projeto in aprovando:
            projeto.status = 'inscricoes_aprovadas'
            projeto.save(update_fields=['status'])
            calcular_ranking_todas_professoras.delay(projeto)
            logger.info(f"{projeto.nome} atualizado para 'inscricoes_aprovadas'")

        # 4. Inscrições Aprovadas → Em Andamento
        iniciando = Project.objects.filter(
            status='inscricoes_aprovadas',
            data_inicio_projeto__isnull=False,
            data_inicio_projeto__lte=hoje
        )
        for projeto in iniciando:
            projeto.status = 'em_andamento'
            projeto.save(update_fields=['status'])
            logger.info(f"{projeto.nome} atualizado para 'em_andamento'")

        # 5. Em Andamento → Avaliação do Projeto (15 dias antes do fim)
        avaliando = Project.objects.filter(
            status='em_andamento',
            data_fim__isnull=False,
            data_fim__gte=hoje,  # ainda não terminou
            data_fim__lte=hoje + timedelta(days=15)  # faltam 15 dias ou menos
        )
        for projeto in avaliando:
            projeto.status = 'avaliacao_projeto'
            projeto.save(update_fields=['status'])
            logger.info(f"{projeto.nome} atualizado para 'avaliacao_projeto'")

        # 6. Avaliação do Projeto → Finalizado (data_fim chegou ou passou)
        finalizando = Project.objects.filter(
            status='avaliacao_projeto',
            data_fim__isnull=False,
            data_fim__lte=hoje  # já passou da data fim
        )
        for projeto in finalizando:
            projeto.status = 'finalizado'
            projeto.save(update_fields=['status'])
            logger.info(f"{projeto.nome} atualizado para 'finalizado'")

        logger.info("Atualização de status de projetos concluída.")

