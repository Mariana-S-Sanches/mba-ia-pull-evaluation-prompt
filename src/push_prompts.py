"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.
Lê os prompts locais em YAML e os publica versionados.
"""

import os
import yaml
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

load_dotenv()

LANGSMITH_USERNAME = os.getenv("LANGCHAIN_HUB_API_KEY_USERNAME") or os.getenv("LANGSMITH_USERNAME")


def load_prompt_from_yaml(filepath: str) -> dict:
    """
    Carrega um prompt de um arquivo YAML local.

    Args:
        filepath: Caminho do arquivo YAML

    Returns:
        Dicionário com os dados do prompt
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    print(f"  ✓ YAML carregado: {filepath}")
    return data


def build_chat_prompt_template(data: dict) -> ChatPromptTemplate:
    """
    Constrói um ChatPromptTemplate a partir dos dados do YAML.

    Args:
        data: Dicionário com 'messages' e opcionalmente 'input_variables'

    Returns:
        ChatPromptTemplate pronto para push
    """
    messages = []

    for msg in data.get("messages", []):
        role = msg.get("role", "human")
        content = msg.get("content", "")

        if role == "system":
            messages.append(SystemMessagePromptTemplate.from_template(content))
        elif role == "human":
            messages.append(HumanMessagePromptTemplate.from_template(content))
        else:
            messages.append(HumanMessagePromptTemplate.from_template(content))

    prompt = ChatPromptTemplate.from_messages(messages)
    return prompt


def push_prompt(prompt, prompt_name: str, description: str = "", tags: list = None):
    """
    Faz push de um ChatPromptTemplate ao LangSmith Prompt Hub.

    Args:
        prompt: ChatPromptTemplate a ser publicado
        prompt_name: Nome completo do prompt (ex: 'username/prompt-name')
        description: Descrição do prompt
        tags: Lista de tags para o prompt
    """
    print(f"  Fazendo push para: {prompt_name}")

    hub.push(
        prompt_name,
        prompt,
        new_repo_description=description,
        new_repo_is_public=True,
        tags=tags or [],
    )

    print(f"  ✓ Push realizado com sucesso!")


def get_username() -> str:
    """Retorna o username configurado nas variáveis de ambiente."""
    username = os.getenv("LANGSMITH_USERNAME") or os.getenv("LANGCHAIN_HUB_API_KEY_USERNAME")
    if not username:
        raise ValueError(
            "Username não encontrado. Configure LANGSMITH_USERNAME no arquivo .env"
        )
    return username


def main():
    """Função principal: lê prompts otimizados e faz push ao LangSmith."""

    username = get_username()

    prompts_to_push = [
        {
            "filepath": "prompts/bug_to_user_story_v2.yml",
            "hub_name": f"{username}/bug_to_user_story_v2",
            "description": (
                "Prompt otimizado para converter relatórios de bugs em User Stories "
                "no formato ágil. Aplica Role Prompting, Few-shot Learning e Chain of Thought "
                "para garantir user stories claras, acionáveis e completas."
            ),
            "tags": ["few-shot", "chain-of-thought", "role-prompting", "agile", "user-story", "bug-to-story", "v2"],
        }
    ]

    print("\n" + "=" * 50)
    print("PUSH DE PROMPTS OTIMIZADOS AO LANGSMITH")
    print("=" * 50)

    for item in prompts_to_push:
        print(f"\nProcessando: {item['hub_name']}")
        try:
            # Carrega o YAML
            data = load_prompt_from_yaml(item["filepath"])

            # Valida metadados mínimos
            metadata = data.get("metadata", {})
            techniques = metadata.get("techniques", [])
            if len(techniques) < 2:
                print(f"  ⚠ Atenção: menos de 2 técnicas listadas nos metadados ({len(techniques)} encontradas)")

            # Constrói o ChatPromptTemplate
            prompt = build_chat_prompt_template(data)
            print(f"  ✓ Template construído com {len(data.get('messages', []))} mensagens")

            # Faz push
            push_prompt(
                prompt=prompt,
                prompt_name=item["hub_name"],
                description=item["description"],
                tags=item["tags"],
            )

        except FileNotFoundError:
            print(f"  ✗ Arquivo não encontrado: {item['filepath']}")
            print("     Execute primeiro a fase de otimização do prompt.")
            raise
        except Exception as e:
            print(f"  ✗ Erro ao processar {item['hub_name']}: {e}")
            raise

    print("\n" + "=" * 50)
    print("✅ Push concluído com sucesso!")
    print(f"   Acesse: https://smith.langchain.com/hub/{username}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
