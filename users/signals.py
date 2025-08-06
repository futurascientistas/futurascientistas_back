from django.db.models.signals import post_save, post_migrate
from django.db import IntegrityError


from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import User

GRUPOS_PADROES = ['admin', 'estudante', 'avaliadora', 'professora']

# @receiver(post_save, sender=User)
# def user_created(sender, instance, created, **kwargs):
#     if created:
#         estudante_group, _ = Group.objects.get_or_create(name='estudante')
#         instance.groups.add(estudante_group)
#         instance.save()  

@receiver(post_migrate)
def criar_grupos_padrao(sender, **kwargs):
    for nome in GRUPOS_PADROES:
        try:
            Group.objects.get_or_create(name=nome)
        except IntegrityError as e:
            print(f"Erro ao criar grupo '{nome}': {e}")