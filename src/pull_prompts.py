"""
Script para fazer pull de prompts do LangSmith Prompt Hub.
Salva os prompts localmente em formato YAML.
"""

import os
import yaml
from dotenv import load_dotenv
from langchain import hub

load_dotenv()


def pull_prompt(prompt_name: str):
    """
    Faz pull de um prompt do LangSmith Prompt Hub.

    Args:
        prompt_name: Nome do prompt no formato 'username/prompt-name'

    Returns:
        ChatPromptTemplate com o prompt carregado
    """
    print(f"  Conectando ao LangSmith...")
    print(f"  Fazendo pull do prompt: {prompt_name}")
    prompt = hub.pull(prompt_name)
    print(f"  ✓ Prompt carregado com sucesso!")
    return prompt


def save_prompt_to_yaml(prompt, filepath: str):
    """
    Salva um ChatPromptTemplate em arquivo YAML local.

    Args:
        prompt: ChatPromptTemplate retornado pelo hub.pull
        filepath: Caminho do arquivo YAML de destino
    """
    messages = []

    for message in prompt.messages:
        class_name = message.__class__.__name__

        if "System" in class_name:
            role = "system"
        elif "Human" in class_name:
            role = "human"
        elif "AI" in class_name or "Assistant" in class_name:
            role = "ai"
        else:
            role = "human"

        # Extrai o template da mensagem
        if hasattr(message, "prompt") and hasattr(message.prompt, "template"):
            content = message.prompt.template
        elif hasattr(message, "content"):
            content = message.content
        else:
            content = str(message)

        messages.append({"role": role, "content": content})

    # Extrai variáveis de input
    input_variables = list(prompt.input_variables) if hasattr(prompt, "input_variables") else []

    data = {
        "input_variables": input_variables,
        "messages": messages,
    }

    # Cria diretório se não existir
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"  ✓ Prompt salvo em: {filepath}")


def main():
    """Função principal: faz pull dos prompts e salva localmente."""

    prompts_to_pull = [
        {
            "name": "leonanluppi/bug_to_user_story_v1",
            "filepath": "prompts/bug_to_user_story_v1.yml",
        }
    ]

    print("\n" + "=" * 50)
    print("PULL DE PROMPTS DO LANGSMITH")
    print("=" * 50)

    for item in prompts_to_pull:
        print(f"\nProcessando: {item['name']}")
        try:
            prompt = pull_prompt(item["name"])
            save_prompt_to_yaml(prompt, item["filepath"])
        except Exception as e:
            print(f"  ✗ Erro ao processar {item['name']}: {e}")
            raise

    print("\n" + "=" * 50)
    print("✅ Pull concluído com sucesso!")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
