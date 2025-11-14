# API Load Testing Suite

Sistema profissional de teste de carga para a API Async News Scraper.

## 🎯 Objetivo

Testar a performance da **API em produção** sob carga concorrente, simulando múltiplos usuários simultâneos acessando os endpoints.

## 📊 Métricas Coletadas

### Performance da API
- **Response Time**: Tempo de resposta (avg, min, max, p50, p95, p99)
- **Throughput**: Requisições por segundo
- **Success Rate**: Taxa de sucesso sob concorrência
- **Status Code Distribution**: Distribuição de códigos HTTP

### Recursos do Servidor
- **Memory Usage**: Uso de memória (target: < 77MB)
- **CPU Usage**: Uso de CPU sob carga
- **Concurrent Handling**: Capacidade de lidar com usuários simultâneos

## 🚀 Como Usar

### 1. Iniciar o Servidor

**Primeiro, inicie a API:**

```bash
# Terminal 1 - Servidor
python -m src.main
```

Ou com uvicorn:

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

### 2. Executar Load Test

**Em outro terminal:**

```bash
# Terminal 2 - Load Test

# Teste médio (padrão)
python run_load_test.py

# Teste leve (10 usuários)
python run_load_test.py light

# Teste pesado (50 usuários)
python run_load_test.py heavy

# Teste de stress (100 usuários)
python run_load_test.py stress

# Executar todos os cenários
python run_load_test.py all
```

## 📈 Cenários de Teste

### Light Load
- **Usuários**: 10 concorrentes
- **Requisições/usuário**: 5
- **Total**: 50 requisições
- **Uso**: Validação básica

### Medium Load (Padrão)
- **Usuários**: 25 concorrentes
- **Requisições/usuário**: 10
- **Total**: 250 requisições
- **Uso**: Teste de carga normal

### Heavy Load
- **Usuários**: 50 concorrentes
- **Requisições/usuário**: 10
- **Total**: 500 requisições
- **Uso**: Teste de alta carga

### Stress Test
- **Usuários**: 100 concorrentes
- **Requisições/usuário**: 10
- **Total**: 1000 requisições
- **Uso**: Teste de stress/limite

## 🎯 Endpoints Testados

Por padrão, o load test executa requisições para:

1. `GET /health` - Health check
2. `GET /news?limit=10` - Listagem de notícias
3. `GET /` - Root endpoint

**Nota**: `POST /scrape` não é incluído por padrão pois é uma operação pesada.

## 📊 Exemplo de Output

```
================================================================================
                    API LOAD TEST - PERFORMANCE REPORT
================================================================================

⚙️  TEST CONFIGURATION
--------------------------------------------------------------------------------
Concurrent Users:         25
Requests per User:        10
Total Requests:           250
Test Duration:            5.2345 seconds

📊 REQUEST SUMMARY
--------------------------------------------------------------------------------
Successful Requests:      250
Failed Requests:          0
Success Rate:             100.00%
Throughput:               47.76 req/s

⏱️  RESPONSE TIME STATISTICS
--------------------------------------------------------------------------------
Average Response Time:    45.23 ms
Min Response Time:        12.34 ms
Max Response Time:        156.78 ms
P50 (Median):             42.10 ms
P95:                      89.45 ms
P99:                      134.56 ms

💾 MEMORY METRICS
--------------------------------------------------------------------------------
Memory Start:             45.23 MB
Memory Peak:              68.45 MB
Memory End:               52.34 MB
Memory Used:              23.22 MB
Tracemalloc Peak:         18.45 MB
✅ Memory End < 77MB:     PASS (52.34 MB)

⚡ CPU METRICS
--------------------------------------------------------------------------------
Average CPU Usage:        15.67%
CPU Samples Collected:    52

📈 STATUS CODE DISTRIBUTION
--------------------------------------------------------------------------------
✅ 200:    250 (100.00%)

🎯 ENDPOINT PERFORMANCE
--------------------------------------------------------------------------------
/health                        38.45 ms  (83 requests)
/news                          51.23 ms  (84 requests)
/                              46.12 ms  (83 requests)

📊 PERFORMANCE ANALYSIS
--------------------------------------------------------------------------------
Requests/sec per User:    1.91
Memory per Request:       0.0929 MB
Latency Rating:           Excellent (< 100ms)
Concurrency Handling:     Excellent (≥99% success)
```

## 📁 Relatórios Gerados

### Console Report
Exibido no terminal durante execução.

### JSON Report
**Localização**: `load_tests/results/load_test_results.json`

```json
{
  "timestamp": "2025-01-13T17:30:45",
  "configuration": {
    "concurrent_users": 25,
    "requests_per_user": 10,
    "total_requests": 250
  },
  "summary": {
    "success_rate_percent": 100.0,
    "throughput_req_per_sec": 47.76
  },
  "response_times": {
    "avg_ms": 45.23,
    "p95_ms": 89.45,
    "p99_ms": 134.56
  },
  "memory": {
    "end_mb": 52.34,
    "memory_threshold_77mb_pass": true
  }
}
```

## 🔍 Interpretação de Resultados

### Response Time
- **< 100ms**: Excelente
- **100-300ms**: Bom
- **300-1000ms**: Aceitável
- **> 1000ms**: Ruim

### Success Rate
- **≥ 99%**: Excelente
- **≥ 95%**: Bom
- **≥ 90%**: Regular
- **< 90%**: Ruim

### Memory End
- **< 77MB**: ✅ PASS (Objetivo atingido)
- **≥ 77MB**: ⚠️ FAIL (Otimização necessária)

### Throughput
- Maior = Melhor
- Compare com baseline
- Deve escalar com usuários

## 🛠️ Customização

### Adicionar Endpoints

Edite `run_load_test.py`:

```python
endpoints = [
    {
        "method": "GET",
        "path": "/health",
    },
    {
        "method": "POST",
        "path": "/scrape",  # Adicione novos endpoints
    },
]
```

### Criar Cenário Customizado

```python
SCENARIOS["custom"] = {
    "name": "Custom Load",
    "concurrent_users": 30,
    "requests_per_user": 15,
}
```

## 📊 Métricas Importantes

### P50, P95, P99 (Percentis)
- **P50**: 50% das requisições são mais rápidas que este valor
- **P95**: 95% das requisições são mais rápidas que este valor
- **P99**: 99% das requisições são mais rápidas que este valor

Percentis altos (P95, P99) revelam outliers e worst-case scenarios.

### Throughput vs Latency
- **Throughput alto + Latência baixa**: Sistema eficiente
- **Throughput alto + Latência alta**: Gargalo de processamento
- **Throughput baixo + Latência baixa**: Subutilização
- **Throughput baixo + Latência alta**: Sistema sobrecarregado

## 🚨 Troubleshooting

### Erro: Cannot connect to server
```bash
# Inicie o servidor primeiro
python -m src.main
```

### Muitas requisições falhando
- Reduza `concurrent_users`
- Reduza `requests_per_user`
- Verifique logs do servidor

### Memory End > 77MB
- Verifique memory leaks
- Otimize queries do banco
- Reduza cache/buffers

## 🎯 Melhores Práticas

1. **Sempre inicie o servidor antes** do load test
2. **Execute múltiplos cenários** para análise completa
3. **Compare com baseline** anterior
4. **Monitore logs do servidor** durante teste
5. **Execute em ambiente isolado** para resultados precisos

## 📚 Diferença: Load Test vs Benchmark

### Benchmark (antigo)
- Testa o **código do scraper** isoladamente
- Mede performance de scraping
- Não testa concorrência da API

### Load Test (novo)
- Testa a **API em produção**
- Simula **usuários concorrentes**
- Mede performance sob carga real
- Valida escalabilidade

## 🤝 Integração CI/CD

```yaml
# GitHub Actions example
- name: Start API Server
  run: |
    python -m src.main &
    sleep 5

- name: Run Load Test
  run: python run_load_test.py medium

- name: Check Memory Threshold
  run: |
    python -c "
    import json
    with open('load_tests/results/load_test_results.json') as f:
        data = json.load(f)
        assert data['memory']['end_mb'] < 77
    "
```

## 📝 Notas

- Load test requer servidor rodando
- Use cenário `light` para testes rápidos
- Use `stress` para encontrar limites
- Resultados variam com hardware/rede
- Execute múltiplas vezes para precisão
