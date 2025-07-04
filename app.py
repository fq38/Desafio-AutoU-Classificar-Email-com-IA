import os
import re
import json
from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
from werkzeug.utils import secure_filename
from openai import AzureOpenAI, RateLimitError, APIError, APIConnectionError
from dotenv import load_dotenv

# Importações do NLTK e PDF
import nltk
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
from nltk.tokenize import word_tokenize
import fitz  # PyMuPDF

# --- CONFIGURAÇÕES INICIAIS ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

load_dotenv()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'super-secret-key' # Necessário para mensagens flash

# Garante que a pasta de uploads exista
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- CONFIGURAÇÃO DO CLIENTE AZURE OPENAI ---
# (Mesma configuração robusta de antes)
try:
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    if not all([api_key, azure_endpoint, deployment_name]):
        raise ValueError("ERRO: Verifique as variáveis de ambiente no arquivo .env.")
    client = AzureOpenAI(api_key=api_key, azure_endpoint=azure_endpoint, api_version="2024-05-01-preview")
    is_client_configured = True
    print("Cliente Azure OpenAI configurado com sucesso.")
except ValueError as e:
    print(e)
    client = None
    deployment_name = None
    is_client_configured = False

# --- FUNÇÕES AUXILIARES ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(filepath):
    try:
        with fitz.open(filepath) as doc:
            text = "".join(page.get_text() for page in doc)
        return text
    except Exception as e:
        print(f"Erro ao extrair texto do PDF: {e}")
        return None

# --- FUNÇÕES DE PROCESSAMENTO E IA (sem alterações) ---
def preprocess_text(text: str):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text, re.I|re.A)
    tokens = word_tokenize(text, language='portuguese')
    stop_words = set(stopwords.words('portuguese'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    stemmer = RSLPStemmer()
    stemmed_tokens = [stemmer.stem(word) for word in filtered_tokens]
    return ' '.join(stemmed_tokens)

# Em app.py

# ... (todo o resto do código permanece igual) ...

def analyze_email_with_ai(email_content: str, processed_text: str):
    """
    Chama a API do Azure OpenAI, enviando tanto o texto original quanto o processado.
    """
    if not is_client_configured or not deployment_name or not client:
        return None

    # --- CORREÇÃO APLICADA AQUI ---
    # Adicionamos a frase "no formato JSON" para cumprir o requisito da API.
    system_prompt = """
    Você é um assistente de IA especialista em produtividade. Analise o email fornecido.
    O "Email Original" te dá o contexto completo. O "Texto Pré-processado" contém as palavras-chave principais.
    Baseado em ambos, retorne um objeto JSON com as chaves "categoria" ('Produtivo' ou 'Improdutivo') e "sugestao_resposta".
    
    Retorne sua resposta estritamente no formato JSON.
    """

    user_prompt = f"""
    **Email Original:**
    ---
    {email_content}
    ---

    **Texto Pré-processado (Palavras-chave):**
    ---
    {processed_text}
    ---
    """
    
    try:
        print(f"--- Enviando para análise no Azure OpenAI (Modelo: {deployment_name}) ---")
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=400
        )
        response_content = response.choices[0].message.content
        print("--- Resposta recebida da IA ---")
        return json.loads(response_content)
    except Exception as e:
        # Imprime o erro completo no console para depuração
        print(f"ERRO NA API DO AZURE OPENAI: {e}")
        return None

# ... (o resto do código, como as rotas do Flask, permanece o mesmo) ...

# --- ENDPOINTS DA APLICAÇÃO ---
@app.route('/', methods=['GET'])
def index():
    """Renderiza a página inicial."""
    return render_template('index.html')

@app.route('/analisar', methods=['POST'])
def handle_analise():
    """Lida com a submissão do formulário (texto ou arquivo)."""
    if not is_client_configured:
        return render_template('index.html', error="Configuração do servidor incompleta. Verifique as credenciais da IA.")

    email_content = None
    file = request.files.get('email_file')
    
    # Prioridade 1: Arquivo enviado
    if file and file.filename != '' and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        if filename.lower().endswith('.txt'):
            with open(filepath, 'r', encoding='utf-8') as f:
                email_content = f.read()
        elif filename.lower().endswith('.pdf'):
            email_content = extract_text_from_pdf(filepath)
        
        os.remove(filepath) # Limpa o arquivo temporário

    # Prioridade 2: Texto colado
    elif request.form.get('email_content'):
        email_content = request.form['email_content']

    # Se nenhum conteúdo foi obtido
    if not email_content:
        return render_template('index.html', error="Nenhum texto ou arquivo válido foi fornecido. Por favor, cole um texto ou envie um arquivo .txt ou .pdf.")

    # Processamento e Análise
    processed_text = preprocess_text(email_content)
    dados_resposta = analyze_email_with_ai(email_content, processed_text)

    if dados_resposta:
        dados_resposta['texto_processado_nltk'] = processed_text
        return render_template('index.html', results=dados_resposta)
    else:
        return render_template('index.html', error="Falha ao analisar o email. Ocorreu um erro interno no servidor.")

if __name__ == '__main__':
    app.run()