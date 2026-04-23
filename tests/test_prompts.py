"""
Testes de validação para o prompt otimizado bug_to_user_story_v2.yml
Execute com: pytest tests/test_prompts.py -v
"""

import pytest
import yaml
import os


PROMPT_V2_PATH = "prompts/bug_to_user_story_v2.yml"


@pytest.fixture(scope="module")
def prompt_data():
    """Carrega o arquivo YAML do prompt v2 para todos os testes."""
    assert os.path.exists(PROMPT_V2_PATH), (
        f"Arquivo não encontrado: {PROMPT_V2_PATH}. "
        "Certifique-se de criar o prompt otimizado antes de rodar os testes."
    )
    with open(PROMPT_V2_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data


@pytest.fixture(scope="module")
def system_content(prompt_data):
    """Extrai o conteúdo do system message."""
    messages = prompt_data.get("messages", [])
    system_messages = [m for m in messages if m.get("role") == "system"]
    if not system_messages:
        return ""
    return system_messages[0].get("content", "")


@pytest.fixture(scope="module")
def full_text(prompt_data):
    """Retorna todo o texto do prompt (todas as mensagens concatenadas)."""
    messages = prompt_data.get("messages", [])
    return "\n".join(m.get("content", "") for m in messages)


# =============================================================================
# TESTE 1 — System Prompt existe e não está vazio
# =============================================================================
def test_prompt_has_system_prompt(prompt_data, system_content):
    """
    Verifica se o prompt possui um system message definido e com conteúdo.
    Um system prompt é essencial para definir o comportamento do modelo.
    """
    messages = prompt_data.get("messages", [])
    system_messages = [m for m in messages if m.get("role") == "system"]

    assert len(system_messages) > 0, (
        "O prompt deve conter pelo menos uma mensagem com role='system'. "
        "O system prompt é essencial para definir o comportamento do modelo."
    )

    assert system_content.strip(), (
        "O system prompt existe, mas está vazio. "
        "Adicione instruções claras no campo 'content' do system message."
    )

    assert len(system_content.strip()) >= 100, (
        f"O system prompt parece muito curto ({len(system_content.strip())} caracteres). "
        "Um bom system prompt deve ter pelo menos 100 caracteres com instruções claras."
    )


# =============================================================================
# TESTE 2 — Prompt define uma persona/role
# =============================================================================
def test_prompt_has_role_definition(system_content):
    """
    Verifica se o prompt define uma persona ou papel específico (Role Prompting).
    Ex: 'Você é um Product Manager', 'Você é um especialista em...', etc.
    """
    role_indicators = [
        "você é",
        "voce é",
        "você é um",
        "você atua como",
        "você é uma",
        "seu papel é",
        "sua função é",
        "age como",
        "atue como",
        "especialista",
        "product manager",
        "analista",
        "sênior",
        "senior",
    ]

    content_lower = system_content.lower()
    found_role = any(indicator in content_lower for indicator in role_indicators)

    assert found_role, (
        "O prompt deve definir uma persona ou papel (Role Prompting). "
        "Exemplo: 'Você é um Product Manager Sênior com experiência em metodologias ágeis.' "
        f"Indicadores buscados: {role_indicators}"
    )


# =============================================================================
# TESTE 3 — Prompt menciona formato de saída (Markdown ou User Story)
# =============================================================================
def test_prompt_mentions_format(full_text):
    """
    Verifica se o prompt especifica o formato de saída esperado.
    Deve mencionar Markdown, User Story padrão ou o formato Como/Quero/Para que.
    """
    format_indicators = [
        "markdown",
        "user story",
        "como [",
        "como um",
        "quero [",
        "para que [",
        "dado ",
        "quando ",
        "então ",
        "critérios de aceitação",
        "criterios de aceitacao",
        "formato",
        "###",
        "**como**",
        "**quero**",
    ]

    content_lower = full_text.lower()
    found_format = any(indicator in content_lower for indicator in format_indicators)

    assert found_format, (
        "O prompt deve especificar o formato de saída esperado. "
        "Inclua instruções sobre Markdown, formato de User Story (Como/Quero/Para que) "
        "ou critérios de aceitação BDD (Dado/Quando/Então). "
        f"Indicadores buscados: {format_indicators}"
    )


# =============================================================================
# TESTE 4 — Prompt contém exemplos de entrada/saída (Few-shot)
# =============================================================================
def test_prompt_has_few_shot_examples(full_text):
    """
    Verifica se o prompt contém exemplos práticos de entrada e saída (Few-shot Learning).
    Esta técnica é obrigatória conforme os requisitos do desafio.
    """
    few_shot_indicators = [
        "exemplo",
        "example",
        "bug report:",
        "input:",
        "saída:",
        "output:",
        "entrada:",
        "user story gerada",
        "### exemplo",
        "## exemplo",
    ]

    content_lower = full_text.lower()
    found_examples = any(indicator in content_lower for indicator in few_shot_indicators)

    assert found_examples, (
        "O prompt deve conter exemplos de entrada/saída (Few-shot Learning). "
        "Esta técnica é OBRIGATÓRIA. Adicione pelo menos 2 exemplos com "
        "'Bug Report' e a respectiva 'User Story' esperada. "
        f"Indicadores buscados: {few_shot_indicators}"
    )

    # Verifica se há pelo menos 2 exemplos
    example_count = sum(
        1 for indicator in ["exemplo 1", "exemplo 2", "example 1", "example 2"]
        if indicator in content_lower
    )

    assert example_count >= 2 or full_text.lower().count("bug report") >= 2, (
        "O prompt deve conter pelo menos 2 exemplos de Few-shot. "
        f"Encontrado(s): {example_count} exemplo(s) numerado(s). "
        "Adicione mais exemplos para melhorar a qualidade das respostas."
    )


# =============================================================================
# TESTE 5 — Prompt não contém TODO pendentes
# =============================================================================
def test_prompt_no_todos(full_text, prompt_data):
    """
    Garante que não há marcadores [TODO], [FIXME] ou [PLACEHOLDER] esquecidos no prompt.
    Esses marcadores indicam que o prompt está incompleto.
    """
    todo_markers = ["[todo]", "[fixme]", "[placeholder]", "[completar]", "[preencher]", "todo:"]
    content_lower = full_text.lower()

    found_todos = [marker for marker in todo_markers if marker in content_lower]

    assert not found_todos, (
        f"Foram encontrados marcadores pendentes no prompt: {found_todos}. "
        "Substitua todos os TODOs, FIXMEs e PLACEHOLDERs por conteúdo real. "
        "Um prompt de produção não deve ter itens incompletos."
    )

    # Verifica também no YAML completo (metadata, etc.)
    full_yaml = str(prompt_data).lower()
    found_in_yaml = [marker for marker in todo_markers if marker in full_yaml]

    assert not found_in_yaml, (
        f"Marcadores pendentes encontrados nos metadados do YAML: {found_in_yaml}. "
        "Verifique todos os campos do arquivo YAML."
    )


# =============================================================================
# TESTE 6 — Metadados contêm pelo menos 2 técnicas listadas
# =============================================================================
def test_minimum_techniques(prompt_data):
    """
    Verifica se os metadados do YAML listam pelo menos 2 técnicas de Prompt Engineering.
    As técnicas devem estar documentadas no campo metadata.techniques.
    """
    metadata = prompt_data.get("metadata", {})

    assert metadata, (
        "O arquivo YAML deve conter uma seção 'metadata'. "
        "Exemplo:\n"
        "metadata:\n"
        "  techniques:\n"
        "    - Few-shot Learning\n"
        "    - Chain of Thought"
    )

    techniques = metadata.get("techniques", [])

    assert isinstance(techniques, list), (
        "O campo 'metadata.techniques' deve ser uma lista. "
        f"Tipo atual: {type(techniques).__name__}"
    )

    assert len(techniques) >= 2, (
        f"O prompt deve utilizar pelo menos 2 técnicas de Prompt Engineering. "
        f"Técnicas encontradas ({len(techniques)}): {techniques}. "
        "Adicione mais técnicas como: Few-shot Learning, Chain of Thought, "
        "Role Prompting, Tree of Thought, ReAct, Skeleton of Thought."
    )

    # Verifica que as técnicas têm nomes significativos (não estão vazias)
    valid_techniques = [t for t in techniques if t and str(t).strip()]

    assert len(valid_techniques) >= 2, (
        f"Algumas técnicas estão com nomes vazios. "
        f"Técnicas válidas encontradas: {valid_techniques}"
    )

    print(f"\n  ✓ Técnicas encontradas: {valid_techniques}")
