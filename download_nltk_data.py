# download_nltk_data.py
import nltk

print("Baixando pacotes de dados necessários do NLTK...")

# Pacote para tokenização (dividir texto em palavras/sentenças)
nltk.download('punkt_tab')

# Pacote com a lista de stopwords em português
nltk.download('stopwords')

# Pacote para stemming em português
nltk.download('rslp')

print("Downloads concluídos com sucesso.")