# PyInstaManager 🤖

Um bot de automação para Instagram, robusto e seguro, desenvolvido em Python para gerenciar atividades de "seguir" e "parar de seguir" de forma inteligente e humanizada, minimizando os riscos de detecção.

## 🎯 Objetivo do Projeto

O objetivo principal do **PyInstaManager** é automatizar a tarefa diária e mecânica de gerenciar o crescimento de contas no Instagram. O bot foi projetado para seguir um número pré-definido de novos perfis e deixar de seguir usuários que não seguem de volta, executando essas tarefas de forma autônoma, segura e agendada para múltiplas contas.

O projeto foi construído com foco em **boas práticas de desenvolvimento e segurança**, utilizando ferramentas profissionais para gerenciamento de banco de dados, agendamento de tarefas e armazenamento de credenciais.

## ✨ Principais Funcionalidades

  * **Automação com InstaPy:** Utiliza a popular biblioteca InstaPy para interagir com o Instagram.
  * **Comportamento Humanizado:** Implementa técnicas avançadas para evitar a detecção, como:
      * Uso de User-Agents e Viewports (tamanho da janela) aleatórios a cada execução.
      * Delays e pausas longas e aleatórias entre todas as ações.
      * Agendamento de tarefas em horários e minutos diferentes a cada dia, com variação (jitter).
  * **Gerenciamento de Banco de Dados com ORM:** Usa PostgreSQL como banco de dados, com o ORM SQLAlchemy 2 para interações seguras e Pythônicas.
  * **Versionamento de Schema com Alembic:** Todas as alterações na estrutura do banco de dados são gerenciadas e versionadas com o Alembic, garantindo consistência e manutenibilidade.
  * **Agendamento Inteligente:** Utiliza o APScheduler para rodar as tarefas de forma autônoma, de dentro da própria aplicação, sem depender de ferramentas externas como o Cron.
  * **Segurança de Credenciais:** As senhas do Instagram **não** são armazenadas em arquivos de texto. O projeto usa o **python-keyring** para salvá-las de forma segura e criptografada no cofre de credenciais nativo do sistema operacional (Chaves no macOS, Credential Manager no Windows, etc.).
  * **Configuração Centralizada:** Utiliza um arquivo `.env` para gerenciar todas as configurações do projeto, como credenciais do banco de dados e lista de contas.

## 🛠️ Stack de Tecnologias

| Tecnologia | Propósito |
| :--- | :--- |
| 🐍 **Python 3.11+** | Linguagem principal do projeto. |
| 🤖 **InstaPy** | Biblioteca de automação para o Instagram. |
| 🐘 **PostgreSQL** | Banco de dados relacional para persistir os dados. |
| 🔄 **SQLAlchemy 2** | ORM para mapear objetos Python para o banco de dados. |
| 📜 **Alembic** | Ferramenta para migração e versionamento do schema do banco. |
| ⏰ **APScheduler** | Agendador de tarefas in-process. |
| 🔑 **python-keyring** | Armazenamento seguro de senhas. |
| ⚙️ **python-dotenv** | Gerenciamento de variáveis de ambiente a partir de arquivos `.env`. |
|  **SQLAlchemy-Utils** | Ferramenta auxiliar para criação programática do banco de dados. |

## 📁 Estrutura do Projeto

```
PyInstaManager/
├── alembic/                  # Pasta de configurações e versões do Alembic
│   ├── versions/
│   └── env.py                # Script de ambiente do Alembic (modificado)
├── database/                 # Módulo para tudo relacionado ao banco de dados
│   ├── __init__.py
│   ├── database.py           # Configuração do engine e sessão do SQLAlchemy 2
│   └── models.py             # Definição dos modelos/tabelas do banco
├── .env.example              # Arquivo de exemplo para as variáveis de ambiente
├── .gitignore                # Arquivo para ignorar arquivos e pastas do Git
├── alembic.ini               # Arquivo de configuração principal do Alembic
├── main.py                   # Ponto de entrada da aplicação, inicia o agendador
├── main_bot.py               # Contém a lógica principal da automação do InstaPy
├── requirements.txt          # Lista de dependências do projeto
├── setup_credentials.py      # Script para salvar as senhas no keyring (rodar uma vez)
└── setup_database.py         # Script para criar o banco de dados (rodar uma vez)
```
