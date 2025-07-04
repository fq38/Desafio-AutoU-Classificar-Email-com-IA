# Analisador de Emails com IA e NLTK


## Descrição

Este projeto é uma solução digital desenvolvida para otimizar a gestão de emails em ambientes corporativos de alto volume, como o setor financeiro. A aplicação web utiliza Inteligência Artificial (GPT-4o via Azure OpenAI) e Processamento de Linguagem Natural (NLTK) para automatizar a leitura, classificação e sugestão de respostas para emails recebidos.

O objetivo principal é liberar o tempo da equipe, eliminando a triagem manual e permitindo que os colaboradores se concentrem em tarefas que exigem intervenção humana qualificada.

O sistema classifica os emails em duas categorias principais:
-   **Produtivo**: Mensagens que exigem uma ação ou resposta específica (ex: solicitações, dúvidas técnicas, atualizações de casos).
-   **Improdutivo**: Mensagens que não necessitam de uma ação imediata (ex: felicitações, agradecimentos, spam).

## Tecnologias Utilizadas

-   **Backend**:
    -   **Python 3**: Linguagem principal da aplicação.
    -   **Flask**: Micro-framework web para criar a API e a interface do usuário.
    -   **Gunicorn**: Servidor WSGI de produção para deploy.
-   **Inteligência Artificial e NLP**:
    -   **Azure OpenAI (GPT-4o)**: Utilizado para a tarefa de classificação e geração de texto (sugestão de resposta).
    -   **NLTK (Natural Language Toolkit)**: Usado para o pré-processamento de texto (tokenização, remoção de stopwords e stemming).
-   **Frontend**:
    -   **HTML5 / CSS3**: Estrutura e estilização da interface web simples.
-   **Deploy e Infraestrutura**:
    -   **Render**: Plataforma como Serviço (PaaS) para o deploy da aplicação.
    -   **Git / GitHub**: Para versionamento de código e integração contínua (CI/CD) com o Render.

---

## Como Funciona?

O algoritmo segue um fluxo claro desde a entrada do usuário até a apresentação do resultado.

1.  **Entrada do Usuário**: O usuário pode fornecer o conteúdo do email de duas maneiras:
    -   Colando o texto diretamente em uma área de texto.
    -   Fazendo o upload de um arquivo `.txt` ou `.pdf`.

2.  **Extração de Texto**: Se um arquivo é enviado, o backend extrai seu conteúdo textual. Para PDFs, a biblioteca `PyMuPDF` é utilizada.

3.  **Pré-processamento com NLTK**: O texto extraído passa por um pipeline de NLP para "limpeza" e extração de palavras-chave:
    -   **Normalização**: O texto é convertido para minúsculas e pontuações são removidas.
    -   **Tokenização**: O texto é quebrado em uma lista de palavras (tokens).
    -   **Remoção de Stopwords**: Palavras comuns e sem significado semântico (como 'o', 'a', 'de', 'que') são removidas da lista.
    -   **Stemming (Radicalização)**: As palavras são reduzidas ao seu radical (ex: 'solicitação', 'solicitando' -> 'solic'). Isso ajuda a agrupar palavras com o mesmo significado.

4.  **Análise com Inteligência Artificial (GPT-4o)**:
    -   **Processo de "Treinamento" da AI**: É importante notar que **não treinamos um modelo do zero**. Utilizamos um modelo pré-treinado massivo (GPT-4o) e aplicamos a técnica de **Engenharia de Prompt**.
    -   **Engenharia de Prompt**: Criamos um "prompt" (uma instrução detalhada) que é enviado para a API do Azure. Este prompt instrui a IA a agir como um especialista em produtividade e a analisar o email. Enviamos tanto o **email original** (para contexto completo) quanto o **texto pré-processado pelo NLTK** (como palavras-chave).
    -   **Saída Estruturada**: Instruímos a IA a retornar sua análise estritamente em formato **JSON**, contendo as chaves `categoria` e `sugestao_resposta`. Isso torna a resposta da IA previsível e fácil de ser processada pelo nosso backend.

5.  **Apresentação do Resultado**: O Flask recebe o JSON da IA e renderiza o resultado na interface web, mostrando a categoria identificada e a sugestão de resposta.

### Decisões Técnicas Chave

-   **Uso de NLTK + GPT-4o**: Combinamos o pré-processamento clássico de NLP (NLTK) com o poder de um LLM moderno. O NLTK cumpre o requisito de processamento e fornece palavras-chave, enquanto o GPT-4o lida com a complexidade e nuance da linguagem para uma classificação e geração de alta qualidade.
-   **Flask em vez de Django**: Para uma aplicação com um único propósito como esta, o Flask é mais leve e rápido de desenvolver.
-   **`.env` para Credenciais**: As chaves de API e outros segredos são armazenados em um arquivo `.env` e carregados como variáveis de ambiente, uma prática de segurança que impede que segredos sejam expostos no código-fonte.
-   **Deploy no Render**: Escolhido pela facilidade de uso, integração com GitHub e um plano gratuito generoso, ideal para prototipagem e projetos de pequeno/médio porte.

---

## Como Executar Localmente

Siga os passos abaixo para executar a aplicação na sua máquina.

### Pré-requisitos

-   [Python 3.10+](https://www.python.org/downloads/)
-   [Git](https://git-scm.com/downloads)

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

### 2. Crie e Ative um Ambiente Virtual

Isso cria um ambiente isolado para as dependências do projeto.

-   **No Windows:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
-   **No macOS ou Linux:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

### 3. Configure as Variáveis de Ambiente

Crie uma cópia do arquivo de exemplo `.env.example` (se houver um) ou crie um novo arquivo chamado `.env` na raiz do projeto e adicione suas credenciais do Azure:

```dotenv
# .env
AZURE_OPENAI_ENDPOINT="https://seu-recurso.openai.azure.com/"
AZURE_OPENAI_API_KEY="sua_chave_de_api_secreta"
AZURE_OPENAI_DEPLOYMENT_NAME="seu_nome_de_implantacao_gpt4o"
```

### 4. Instale as Dependências

Com o ambiente virtual ativado, instale todas as bibliotecas necessárias:

```bash
pip install -r requirements.txt
```

### 5. Baixe os Dados do NLTK

Execute o script para baixar os pacotes de dados que o NLTK precisa para funcionar:

```bash
python download_nltk_data.py
```

### 6. Execute a Aplicação

Inicie o servidor de desenvolvimento do Flask:

```bash
python app.py
```

Abra seu navegador e acesse: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## Dados de Exemplo para Teste

Use os textos abaixo para testar a aplicação.

#### Exemplo 1: Produtivo (Solicitação de Status)

```
Olá equipe,
Gostaria de solicitar uma atualização sobre o status do ticket #2024-5891, referente ao problema de acesso à plataforma de investimentos. 
Já se passaram 3 dias desde a última resposta e preciso apresentar um relatório para a diretoria na sexta-feira.
Qual a previsão de solução?
Obrigado,
Carlos Andrade
```

#### Exemplo 2: Improdutivo (Felicitações)

```
Prezados,
Gostaria de desejar a todos um Feliz Natal e um próspero Ano Novo! 
Que 2025 venha repleto de paz, saúde e sucesso para todos nós e nossas famílias.
Abraços,
Mariana Costa
```

#### Exemplo 3: Produtivo (Dúvida Técnica)

```
Bom dia,
Estou tentando integrar a nova API de pagamentos mas estou recebendo um erro 403. 
Já verifiquei minha chave de API e ela parece correta. Podem me ajudar a entender o que pode estar acontecendo? Segue em anexo o log de erro.
Atenciosamente,
Joana Silva
```