from celery import shared_task
from django.utils import timezone
from django.db import transaction
import logging
from projects.models import Project
from applications.models import Application, AcompanhamentoProjeto

logger = logging.getLogger(__name__)

@shared_task
def processar_homologacao_projeto():
    hoje = timezone.now().date()
    logger.info(f"Iniciando processamento de homologação. Data de hoje: {hoje}")

    projetos = Project.objects.filter(
        status='avaliacao_inscricoes',
        fim_inscricoes=hoje
    )

    logger.info(f"Projetos encontrados para homologação: {projetos.count()}")

    logger.info(f"Projetos encontrados para homologação: {projetos.count()}")

    for projeto in projetos:
        logger.info(f"Processando projeto: {projeto.nome} (ID: {projeto.id})")

        with transaction.atomic():
            projeto.status = 'inscricoes_aprovadas'
            projeto.save()
            logger.info(f"Projeto {projeto.nome} atualizado para 'inscricoes_aprovadas'")

            inscricoes = Application.objects.filter(projeto=projeto)
            logger.info(f"{inscricoes.count()} inscrições encontradas para o projeto {projeto.nome}")

            for inscricao in inscricoes:
                novo_status = 'deferida' if inscricao.aprovado else 'indeferida'
                inscricao.status = novo_status
                inscricao.save()
                logger.info(f"Inscrição de {inscricao.usuario.email} atualizada para '{novo_status}'")

                if inscricao.aprovado and not AcompanhamentoProjeto.objects.filter(participante=inscricao.usuario, projeto=projeto).exists():
                    AcompanhamentoProjeto.objects.create(
                        participante=inscricao.usuario,
                        projeto=projeto,
                        frequencia=0.0,
                        status_projeto='em_andamento'
                    )
                    logger.info(f"Acompanhamento criado para usuário {inscricao.usuario.email} no projeto {projeto.nome}")

    logger.info("Processamento finalizado.")
