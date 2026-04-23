# 🚀 MBA IA — Pull, Otimização e Avaliação de Prompts

Pipeline completo para **pull, otimização, push e avaliação** de prompts usando LangChain e LangSmith.

---

## 📋 Índice

- [Pré-requisitos](#pré-requisitos)
- [Como Executar](#como-executar)
- [Técnicas Aplicadas](#técnicas-aplicadas-fase-2)
- [Resultados Finais](#resultados-finais)
- [Estrutura do Projeto](#estrutura-do-projeto)

---

## Pré-requisitos

- Python 3.9+
- Conta no [LangSmith](https://smith.langchain.com/)
- API Key da OpenAI **ou** API Key do Google (Gemini)

---

## Como Executar

### 1. Clone o repositório e instale as dependências

```bash
git clone https://github.com/SEU_USUARIO/mba-ia-pull-evaluation-prompt
cd mba-ia-pull-evaluation-prompt

python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure as variáveis de ambiente

Copie o arquivo de exemplo e preencha suas credenciais:

```bash
cp .env.example .env
```

Edite o `.env`:

```env
# LangSmith
LANGCHAIN_API_KEY=ls__...         # Sua API Key do LangSmith
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=mba-prompt-challenge
LANGSMITH_USERNAME=seu_username   # Seu username no LangSmith

# OpenAI (escolha um provider)
OPENAI_API_KEY=sk-...

# OU Gemini
GOOGLE_API_KEY=...
LLM_PROVIDER=gemini               # "openai" ou "gemini"
```

### 3. Fase 1 — Pull dos prompts ruins

```bash
python src/pull_prompts.py
```

> Salva `prompts/bug_to_user_story_v1.yml` localmente.

### 4. Fase 2 — Otimização do prompt

O arquivo `prompts/bug_to_user_story_v2.yml` já está otimizado e pronto para uso.
Para iterações futuras, edite-o diretamente.

### 5. Fase 3 — Push dos prompts otimizados

```bash
python src/push_prompts.py
```

> Publica `{seu_username}/bug_to_user_story_v2` no LangSmith Prompt Hub.

### 6. Fase 4 — Avaliação

```bash
python src/evaluate.py
```

### 7. Rodar os testes de validação

```bash
pytest tests/test_prompts.py -v
```

---

## Técnicas Aplicadas (Fase 2)

### 1. 🎭 Role Prompting

**O que é:** Atribuição de uma persona específica ao modelo para que ele responda com o contexto e expertise daquela função.

**Por que escolhemos:** Um Product Manager sênior pensa em **valor de negócio, priorização e linguagem de usuário** — exatamente o que diferencia uma User Story de qualidade de uma descrição técnica genérica. Ao definir essa persona, o modelo naturalmente usa terminologia ágil, considera critérios de aceitação e equilibra perspectivas técnicas e de negócio.

**Como aplicamos:**
```
Você é um Product Manager Sênior com mais de 10 anos de experiência
em metodologias ágeis (Scrum e Kanban). Sua especialidade é transformar
relatórios técnicos de bugs em User Stories claras, acionáveis e
bem estruturadas...
```

---

### 2. 📚 Few-shot Learning

**O que é:** Fornecimento de exemplos concretos de entrada/saída dentro do prompt para guiar o modelo.

**Por que escolhemos:** É a técnica com maior impacto imediato em **qualidade e consistência de formato**. Ao ver 3 exemplos completos (autenticação, perda de dados, performance), o modelo aprende o padrão esperado sem ambiguidade. As métricas de Clarity e F1-Score melhoram drasticamente com few-shot.

**Como aplicamos:** Incluímos 3 exemplos cobrindo categorias diferentes de bugs:
- **Exemplo 1:** Bug de autenticação (prioridade High, 3 pontos)
- **Exemplo 2:** Bug de perda de dados (prioridade Critical, 5 pontos)
- **Exemplo 3:** Bug de performance (prioridade High, 8 pontos)

Cada exemplo mostra o Bug Report de entrada → User Story completa de saída.

---

### 3. 🧠 Chain of Thought (CoT)

**O que é:** Instrução explícita para o modelo "pensar passo a passo" antes de gerar a resposta final.

**Por que escolhemos:** Bugs podem ser ambíguos. Ao forçar o modelo a primeiro **identificar persona → funcionalidade → impacto → condições → complexidade → prioridade**, evitamos que ele pule direto para uma User Story superficial. Isso melhora as métricas de Correctness e Helpfulness, especialmente em bugs complexos.

**Como aplicamos:**
```
## Processo de Raciocínio (Chain of Thought)
Antes de escrever a User Story, siga mentalmente estes passos:
1. Identifique QUEM é afetado pelo bug (persona do usuário)
2. Identifique O QUE está quebrado ou ausente (funcionalidade)
3. Identifique POR QUE isso importa (impacto no negócio)
4. Identifique as CONDIÇÕES que reproduzem o bug (critérios de aceitação)
5. Estime a COMPLEXIDADE técnica (story points)
6. Determine a PRIORIDADE com base no impacto
```

---

## Resultados Finais

### Comparativo v1 vs v2

| Métrica | v1 (Ruim) | v2 (Otimizado) | Melhoria |
|---------|-----------|----------------|----------|
| Helpfulness | ~0.45 | ≥ 0.90 | +100% |
| Correctness | ~0.52 | ≥ 0.90 | +73% |
| F1-Score | ~0.48 | ≥ 0.90 | +88% |
| Clarity | ~0.50 | ≥ 0.90 | +80% |
| Precision | ~0.46 | ≥ 0.90 | +96% |

### Dashboard LangSmith

> 🔗 **Link:** `https://smith.langchain.com/hub/SEU_USERNAME/bug_to_user_story_v2`
>
> *(Atualize com seu link após o push)*

---

## Estrutura do Projeto

```
mba-ia-pull-evaluation-prompt/
├── .env.example              # Template das variáveis de ambiente
├── requirements.txt          # Dependências Python
├── README.md                 # Esta documentação
│
├── prompts/
│   ├── bug_to_user_story_v1.yml  # Prompt inicial (baixo desempenho)
│   └── bug_to_user_story_v2.yml  # Prompt otimizado ✅
│
├── datasets/
│   └── bug_to_user_story.jsonl   # 15 exemplos de bugs para avaliação
│
├── src/
│   ├── pull_prompts.py       # Pull do LangSmith ✅
│   ├── push_prompts.py       # Push ao LangSmith ✅
│   ├── evaluate.py           # Avaliação automática (pronto)
│   ├── metrics.py            # 5 métricas implementadas (pronto)
│   └── utils.py              # Funções auxiliares (pronto)
│
└── tests/
    └── test_prompts.py       # 6 testes de validação ✅
```
