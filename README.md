# 🚀 Async News Scraper

Sistema assíncrono de alto desempenho para coleta e exposição de notícias do portal G1, construído com arquitetura profissional e foco em escalabilidade.

## 📋 Descrição

O **Async News Scraper** é uma aplicação completa que realiza scraping de manchetes do G1 de forma assíncrona, armazena os dados em banco SQLite e expõe endpoints REST para consulta e execução de novas coletas. O projeto foi desenvolvido seguindo as melhores práticas de engenharia de software, com código limpo, tipagem estática completa e performance otimizada.

## 🛠️ Stack Tecnológica

- **Python 3.11+** - Linguagem base com recursos modernos
- **FastAPI** - Framework web assíncrono de alta performance
- **SQLAlchemy 2.0** - ORM com suporte async/await
- **aiosqlite** - Driver SQLite assíncrono
- **aiohttp** - Cliente HTTP assíncrono para scraping
- **BeautifulSoup4** - Parser HTML para extração de dados
- **Pydantic** - Validação de dados e serialização
- **Uvicorn** - Servidor ASGI de produção

## 🏗️ Arquitetura

```
┌─────────────┐
│   FastAPI   │  ← Camada de API (endpoints REST)
└──────┬──────┘
       │
┌──────▼──────┐
│  Scraper    │  ← Camada de serviço (lógica de negócio)
└──────┬──────┘
       │
┌──────▼──────┐
│ SQLAlchemy  │  ← Camada de persistência (ORM async)
└──────┬──────┘
       │
┌──────▼──────┐
│   SQLite    │  ← Banco de dados
└─────────────┘
```

### Fluxo de Dados

1. **Scraping**: `aiohttp` faz requisição assíncrona ao G1
2. **Parsing**: `BeautifulSoup` extrai manchetes e links
3. **Persistência**: `SQLAlchemy` salva dados no SQLite (async)
4. **API**: `FastAPI` expõe endpoints para consulta e trigger de scraping

## 📁 Estrutura do Projeto

```
async-news-scrapper/
├── src/
│   ├── api.py              # Endpoints FastAPI
│   ├── db.py               # Configuração do banco async
│   ├── main.py             # Entry point da aplicação
│   ├── models.py           # Modelos SQLAlchemy
│   ├── schemas.py          # Schemas Pydantic
│   └── scrapper/
│       ├── __init__.py
│       └── news_scrapper.py # Lógica de scraping
├── requirements.txt        # Dependências Python
├── Dockerfile             # Container Docker
├── .env.example           # Variáveis de ambiente
├── .gitignore
└── README.md
```

## 🚀 Como Executar

### Pré-requisitos

- Python 3.11 ou superior
- pip

### Instalação Local

1. **Clone o repositório**
```bash
git clone <repository-url>
cd async-news-scrapper
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Execute a aplicação**
```bash
python -m src.main
```

Ou diretamente com uvicorn:
```bash
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em: `http://localhost:8000`

### Execução com Docker

1. **Build da imagem**
```bash
docker build -t async-news-scraper .
```

2. **Execute o container**
```bash
docker run -d -p 8000:8000 --name news-scraper async-news-scraper
```

3. **Acesse a aplicação**
```
http://localhost:8000
```

## 📡 Endpoints da API

### `GET /`
Informações básicas do serviço

**Response:**
```json
{
  "service": "Async News Scraper",
  "status": "running",
  "endpoints": ["/news", "/scrape"]
}
```

### `GET /news`
Retorna todas as notícias armazenadas, ordenadas por data (mais recentes primeiro)

**Query Parameters:**
- `limit` (int, default: 100) - Número máximo de resultados
- `offset` (int, default: 0) - Offset para paginação

**Response:**
```json
[
  {
    "id": 1,
    "title": "Título da notícia",
    "url": "https://g1.globo.com/...",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

### `POST /scrape`
Executa uma nova coleta de notícias do G1

**Response:**
```json
{
  "success": true,
  "news_added": 15,
  "message": "Successfully scraped and added 15 new articles"
}
```

### `GET /health`
Health check do serviço

**Response:**
```json
{
  "status": "healthy",
  "service": "async-news-scraper"
}
```

## 🧪 Exemplos de Uso

### cURL

**Listar notícias:**
```bash
curl http://localhost:8000/news
```

**Executar scraping:**
```bash
curl -X POST http://localhost:8000/scrape
```

### Python

```python
import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        # Executar scraping
        response = await client.post("http://localhost:8000/scrape")
        print(response.json())
        
        # Buscar notícias
        response = await client.get("http://localhost:8000/news?limit=10")
        print(response.json())

asyncio.run(main())
```

### JavaScript/TypeScript

```typescript
// Executar scraping
const scrapeResponse = await fetch('http://localhost:8000/scrape', {
  method: 'POST'
});
const scrapeData = await scrapeResponse.json();

// Buscar notícias
const newsResponse = await fetch('http://localhost:8000/news?limit=10');
const newsData = await newsResponse.json();
```

## 🔧 Configuração

Copie `.env.example` para `.env` e ajuste as variáveis conforme necessário:

```env
DATABASE_URL=sqlite+aiosqlite:///./news.db
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info
```

## 🎯 Características Técnicas

### Performance
- **100% Assíncrono**: Toda a stack utiliza async/await
- **Scraping Concorrente**: Múltiplas requisições paralelas
- **Connection Pooling**: Gerenciamento eficiente de conexões
- **Retry Logic**: Resiliência a falhas de rede com backoff exponencial

### Qualidade de Código
- **Type Hints**: Tipagem estática completa
- **Clean Code**: Código autoexplicativo sem comentários desnecessários
- **Separation of Concerns**: Camadas bem definidas (API, Service, Data)
- **Error Handling**: Tratamento robusto de exceções

### Segurança
- **SQL Injection Protection**: ORM previne injeções
- **Input Validation**: Pydantic valida todas as entradas
- **Timeout Management**: Proteção contra requisições travadas
- **Unique Constraints**: Previne duplicação de notícias

## 📊 Modelo de Dados

```python
class News:
    id: int                 # Primary key auto-increment
    title: str              # Título da notícia (max 500 chars)
    url: str                # URL única da notícia (max 1000 chars)
    created_at: datetime    # Timestamp de criação
```

## 🔍 Documentação Interativa

Acesse a documentação automática da API:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🤝 Contribuindo

Este projeto segue padrões profissionais de desenvolvimento:

1. Código deve ser assíncrono
2. Type hints são obrigatórios
3. Siga PEP 8
4. Mantenha a separação de camadas
5. Escreva código autoexplicativo

## 📝 Licença

MIT License

## 👨‍💻 Autor

Desenvolvido com foco em qualidade, performance e boas práticas de engenharia de software.
