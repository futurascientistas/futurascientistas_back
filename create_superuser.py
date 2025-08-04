import os
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

cpf = '96144084053'
email = 'admin11@example.com'
password = 'S3nh@Forte123'

if User.objects.filter(cpf=cpf).exists():
    print(f'Superuser with CPF {cpf} already exists.')
elif User.objects.filter(email=email).exists():
    print(f'Superuser with email {email} already exists.')
else:
    print(f'Creating superuser with CPF {cpf}')
    user = User.objects.create_superuser(
        cpf=cpf,
        email=email,
        password=password
    )
    grupo, _ = Group.objects.get_or_create(name='admin')
    user.groups.add(grupo)
    print(f'User added to group "admin"')
