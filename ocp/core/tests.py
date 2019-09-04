from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
# Para fazer testes o Django cria um banco de dados virtual,
# Se você não estiver utilizando db.sqlite é preciso que seu usuario
# logado no banco tenha acesso a criação de banco de dados pois senão
# o django não conseguirá fazer os testes...
# A solução não pode ser mudar configurar um settings para testes
# utilizando o db.sqlite???

class HomeViewTest(TestCase):
    #mostra se a url esta encontrando a pagina
    def test_home_status_code(self):
        client = Client()
        response = client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
    #Mostra se um template foi usado
    def test_home_template_used(self):
        client = Client()
        response = client.get(reverse('core:home'))
        self.assertTemplateUsed(response, 'home.html')
        self.assertTemplateUsed(response, 'base.html')


