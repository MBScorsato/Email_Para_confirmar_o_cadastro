from django.urls import path
from autenticacao import views

urlpatterns = [
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_, name='login_'),
    path('sair/', views.sair, name='sair'),
    path('ativar_conta/<str:token>/', views.ativar_conta, name="ativar_conta")

]