from django.contrib.auth.models import User
from django.http import HttpResponse
import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from .utils import password_is_valid, email_html
from django.contrib import messages
from django.contrib.messages import constants
from .models import Ativacao
from hashlib import sha256
from django.contrib import auth


def cadastro(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'cadastro.html')
    elif request.method == 'POST':
        usuario = request.POST.get('usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if not password_is_valid(request, senha, confirmar_senha):
            return redirect('/auth/cadastro')
        try:
            user = User.objects.create_user(username=usuario,
                                            email=email,
                                            password=senha,
                                            is_active=False)
            user.save()

            # criando token para o novo usuario que nunca se repete
            token = sha256(f'{usuario}{email}'.encode()).hexdigest()
            ativacao = Ativacao(token=token, user=user)
            ativacao.save()

            # enviando email para a ativação da conta
            path_template = os.path.join(settings.BASE_DIR, 'autenticacao/templates/emails/cadastro_confirmado.html')
            email_html(path_template, 'Cadastro confirmado', [email, ], username=user,
                       link_ativacao=f"127.0.0.1:8000/auth/ativar_conta/{token}")

            return redirect('/auth/login')
            messages.add_message(request, constants, SUCCESS, 'Usuário cadastrado com sucesso')

        except:
            messages.add_message(request, constants.ERROR, '!Erro interno do sistema!')
            return redirect('/auth/cadastro')

        return render(request, 'cadastro.html')


def login_(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        username = request.POST.get('usuario')
        senha = request.POST.get('senha')

    usuario = auth.authenticate(username=username, password=senha)

    if not usuario:
        messages.add_message(request, constants.ERROR, 'Credenciais inválidas!')
        return redirect('/auth/login')
    else:
        auth.login(request, usuario)
        return redirect('/')


def sair(request):
    auth.logout(request)
    return redirect('/auth/login/')


def ativar_conta(request, token):
    token = get_object_or_404(Ativacao, token=token)
    if token.ativo:
        messages.add_message(request, constants.WARNING, 'Essa token já foi usado')
        return redirect('/auth/logar')
    user = User.objects.get(username=token.user.username)
    user.is_active = True
    user.save()
    token.ativo = True
    token.save()
    messages.add_message(request, constants.SUCCESS, 'Conta ativa com sucesso')
    return redirect('/auth/logar')
