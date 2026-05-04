"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_NAME = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH  = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v1.yml"


def pull_prompts_from_langsmith():
    """Faz pull do prompt base e salva localmente como YAML."""

    print_section_header("PULL DE PROMPTS - LangSmith")

    if not check_env_vars(["LANGCHAIN_API_KEY"]):
        return False

    print(f"📥 Fazendo pull: {PROMPT_NAME}")
    prompt = hub.pull(PROMPT_NAME)

    # Extrai mensagens do ChatPromptTemplate
    messages = []
    for msg in prompt.messages:
        role = type(msg).__name__.lower()
        if "system" in role:
            role = "system"
        elif "human" in role or "user" in role:
            role = "human"
        else:
            role = "assistant"

        content = (
            msg.prompt.template
            if hasattr(msg, "prompt")
            else str(msg)
        )
        messages.append({"role": role, "content": content})

    prompt_data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "messages": messages,
            "input_variables": list(prompt.input_variables),
            "version": "v1",
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }

    # save_yaml recebe o caminho completo como string
    success = save_yaml(prompt_data, str(OUTPUT_PATH))
    if success:
        print(f"✅ Salvo em: {OUTPUT_PATH}")
    return success


def main():
    """Função principal"""
    try:
        success = pull_prompts_from_langsmith()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Erro: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())