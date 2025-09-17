from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from users.models.user_model import User

def enviar_email_nova_versao():
    subject = '🚀 Nova versão do Futuras Cientistas disponível!'
    from_email = 'no-reply@futurascientistas.com'

    usuarias = User.objects.all()  

    for user in usuarias:

        html_content = render_to_string('components/email/nova_versao_email.html', {
            'nome': user.nome,
            'protocol': 'https',
            'domain': 'www.futurascientistas.com.br',
        })

        text_content = (
            f"Olá {user.nome},\n\n"
            "Temos novidades! A versão 2 do Futuras Cientistas já está disponível. "
            "Agora você pode inserir notas por conceitos diretamente na plataforma.\n\n"
            "Acesse sua conta e aproveite!"
        )

        msg = EmailMultiAlternatives(subject, text_content, from_email, [user.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
