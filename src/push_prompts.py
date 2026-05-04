"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
PROMPT_FILE = PROMPTS_DIR / "bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt (conteúdo da chave raiz do YAML)

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    if not prompt_data.get("system_prompt", "").strip():
        errors.append("system_prompt está vazio ou ausente")

    if not prompt_data.get("user_prompt", "").strip():
        errors.append("user_prompt está vazio ou ausente")

    if "{bug_report}" not in prompt_data.get("user_prompt", ""):
        errors.append("user_prompt não contém {bug_report}")

    if "{bug_report}" in prompt_data.get("system_prompt", ""):
        errors.append(
            "system_prompt não deve conter {bug_report} (duplicação do v1)")

    if "TODO" in prompt_data.get("system_prompt", ""):
        errors.append("system_prompt ainda contém TODOs não resolvidos")

    # Chave correta conforme utils.py
    techniques = prompt_data.get("techniques_applied", [])
    if len(techniques) < 2:
        errors.append(
            f"Mínimo 2 técnicas em 'techniques_applied' "
            f"(encontradas: {len(techniques)})"
        )

    return len(errors) == 0, errors


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    username = os.getenv("USERNAME_LANGSMITH_HUB")
    if not username:
        print(
            "❌ USERNAME_LANGSMITH_HUB não encontrado no .env"
        )
        return False

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            prompt_data["system_prompt"]
        ),
        HumanMessagePromptTemplate.from_template(
            prompt_data["user_prompt"]
        ),
    ])

    full_name = f"{username}/{prompt_name}"
    print(f"📤 Publicando: {full_name}")

    url = hub.push(
        full_name,
        prompt,
        new_repo_is_public=True,
    )

    print(f"✅ Publicado com sucesso!")
    print(f"🔗 {url}")
    return True


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS - LangSmith")

    if not check_env_vars(["LANGCHAIN_API_KEY", "LANGCHAIN_USERNAME"]):
        return 1

    # 1. Carrega o YAML — load_yaml recebe caminho completo como string
    raw = load_yaml(str(PROMPT_FILE))
    if raw is None:
        return 1

    # Desempacota chave raiz
    prompt_data = raw.get(PROMPT_KEY, raw)

    # 2. Valida
    print("🔍 Validando prompt...")
    is_valid, errors = validate_prompt(prompt_data)

    if not is_valid:
        print("❌ Prompt inválido:")
        for err in errors:
            print(f"   • {err}")
        return 1

    techniques = prompt_data.get("techniques_applied", [])
    print(
        f"✅ Validação OK — {len(techniques)} técnicas: {', '.join(techniques)}")

    # 3. Push
    success = push_prompt_to_langsmith(PROMPT_KEY, prompt_data)
    if not success:
        return 1

    print("\n✅ Concluído! Próximo passo: python src/evaluate.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
