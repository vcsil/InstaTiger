#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 26 19:49:53 2025

@author: vcsil
"""

# main.py (script principal)
import os
import keyring
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from main_bot import run_automation_for_account # Importa a função do outro arquivo

# Carrega as variáveis do arquivo .env
load_dotenv()

def job_wrapper(username):
    """Função para obter a senha e chamar o bot"""
    print(f"APScheduler: Disparando job para a conta '{username}'...")
    password = keyring.get_password("instapy_automation", username)
    if password:
        run_automation_for_account(username, password)
    else:
        print(f"ERRO: Senha para '{username}' não encontrada no keyring.")

# Inicializa o agendador
scheduler = BlockingScheduler(timezone="America/Sao_Paulo")

# Pega a lista de contas do .env
accounts = os.getenv("INSTA_ACCOUNTS").split(',')

for account in accounts:
    # Agendamento CRON para rodar uma vez por dia, em horário aleatório
    hora = random.randint(9, 20)
    minuto = random.randint(0, 59)
    scheduler.add_job(
        job_wrapper,
        trigger='cron',
        args=[account],
        day_of_week='mon-sun',
        hour=hora,
        minute=minuto,
        jitter=1800  # Adiciona uma variação de até 30 minutos no horário
    )

print("--- Automação InstaPy Iniciada com Agendamento ---")
print(f"Contas a serem gerenciadas: {accounts}")
print("O script agora está em modo de espera. Ele executará as tarefas nos horários agendados.")
print("Pressione Ctrl+C para sair.")

try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    pass