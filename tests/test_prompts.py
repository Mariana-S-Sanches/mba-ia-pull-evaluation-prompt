"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_KEY  = "bug_to_user_story_v2"


def load_prompt_data() -> dict:
    """Carrega e desempacota os dados do prompt v2."""
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return raw.get(PROMPT_KEY, raw)


class TestPrompts:

    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        data = load_prompt_data()
        assert "system_prompt" in data, "Campo 'system_prompt' não encontrado no YAML"
        assert data["system_prompt"].strip(), "Campo 'system_prompt' está vazio"

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: 'Você é um Product Manager')."""
        data = load_prompt_data()
        system_prompt = data.get("system_prompt", "")
        role_keywords = ["você é", "voce é", "você é um", "você é uma"]
        has_role = any(kw in system_prompt.lower() for kw in role_keywords)
        assert has_role, (
            "O system_prompt não define uma persona. "
            "Adicione uma definição de role como 'Você é um Product Manager Sênior...'"
        )

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        data = load_prompt_data()
        system_prompt = data.get("system_prompt", "")
        format_keywords = [
            "user story", "como ", "eu quero", "para que",
            "critérios de aceitação", "dado que", "quando", "então",
            "markdown", "###", "==="
        ]
        has_format = any(kw in system_prompt.lower() for kw in format_keywords)
        assert has_format, (
            "O system_prompt não menciona formato de saída. "
            "Inclua instruções de formato User Story ou Markdown."
        )

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        data = load_prompt_data()
        system_prompt = data.get("system_prompt", "")
        few_shot_indicators = ["exemplo", "relato:", "saída:", "---"]
        matches = sum(1 for kw in few_shot_indicators if kw in system_prompt.lower())
        assert matches >= 2, (
            "O system_prompt não parece conter exemplos Few-shot. "
            "Adicione ao menos 2 exemplos de entrada/saída."
        )

    def test_prompt_no_todos(self):
        """Garante que não há [TODO] esquecido no texto."""
        data = load_prompt_data()
        full_text = yaml.dump(data, allow_unicode=True)
        assert "[TODO]" not in full_text.upper().replace(" ", ""), (
            "O prompt contém marcadores [TODO] não resolvidos. "
            "Remova ou preencha todos os TODOs antes de entregar."
        )

    def test_minimum_techniques(self):
        """Verifica se pelo menos 2 técnicas foram listadas nos metadados."""
        data = load_prompt_data()
        techniques = data.get("techniques_applied", [])
        assert len(techniques) >= 2, (
            f"São necessárias pelo menos 2 técnicas em 'techniques_applied'. "
            f"Encontradas: {len(techniques)} — {techniques}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])