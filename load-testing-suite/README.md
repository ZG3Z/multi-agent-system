# Load Testing Suite dla Multi-Agent System

Minimalna aplikacja do testowania wydajności agentów AI na Cloud Run. Zaprojektowana specjalnie dla bezpłatnych planów z ograniczonymi requestami API.

## Funkcje

- **Minimalne obciążenie**: ~21 requestów na pełny test
- **A2A Communication Testing**: Test komunikacji między agentami
- **Web Dashboard**: Wizualizacja wyników testów
- **Docker Compose**: Kompletny stack w kontenerach
- **Redis Storage**: Przechowywanie wyników testów
- **REST API**: Programowe sterowanie testami

## Szybki Start

### 1. Konfiguracja

```bash
# Klonuj/pobierz kod
git clone <repository-url>
cd load-testing-suite

# Pierwsza konfiguracja
make setup

# Edytuj .env z URL-ami Cloud Run
nano .env
```

### 2. Uruchomienie

```bash
# Zbuduj i uruchom
make build
make start

# Sprawdź status
make status
```

### 3. Testowanie

```bash
# Pełny test (21 requestów)
make test

# Tylko health check (3 requesty)
make test-health

# Dashboard
make dashboard
```

## Struktura Projektu

```
load-testing-suite/
├── minimal_load_testing.py     # Główna logika testów
├── load_test_runner.py         # API serwer
├── dashboard/
│   ├── dashboard_app.py        # Web dashboard
│   └── templates/              # HTML templates
├── docker-compose.yml          # Orchestracja kontenerów
├── Dockerfile.tester           # Load tester image
├── Dockerfile.dashboard        # Dashboard image
├── Makefile                    # Komendy zarządzania
└── .env                        # Konfiguracja URL-i
```

## Konfiguracja Cloud Run URLs

W pliku `.env` ustaw prawdziwe URL-e z Cloud Run:

```bash
CREWAI_URL=https://crewai-agent-abc123.a.run.app
LANGRAPH_URL=https://langraph-agent-abc123.a.run.app
ADK_URL=https://adk-agent-abc123.a.run.app
```

URL-e znajdziesz w Google Cloud Console > Cloud Run.

## Typy Testów

### 1. Health Check Test (3 requests)
```bash
make test-health
```
Sprawdza podstawową dostępność wszystkich agentów.

### 2. Capabilities Test (3 requests)
```bash
make test-capabilities
```
Pobiera listę możliwości każdego agenta.

### 3. A2A Communication Test (3 requests)
```bash
make test-a2a
```
Testuje komunikację Agent-to-Agent przez `/a2a/message` endpoint.

### 4. Latency Test (9 requests)
3 requesty na agenta dla sprawdzenia konsystencji czasów odpowiedzi.

### 5. Task Execution Test (3 requests) - WYŁĄCZONY
Testuje wykonanie zadań (może failować z fake API keys).

## API Endpoints

### Load Tester API (port 8080)

```bash
# Status konfiguracji
GET /config

# Start testu
POST /test/start
{
  "test_name": "my_test",
  "run_health_check": true,
  "run_capabilities": true,
  "run_a2a_test": true,
  "run_latency_test": true,
  "run_task_test": false
}

# Status testu
GET /test/status

# Wyniki testu
GET /test/results/{test_id}
```

### Dashboard (port 8081)

- `/` - Główna strona z listą testów
- `/test/{test_id}` - Szczegóły testu z wykresami
- `/api/tests` - Lista testów (JSON)

## Przykład Użycia

```bash
# Uruchom stack
make start

# Sprawdź konfigurację
curl http://localhost:8080/config

# Uruchom test
curl -X POST http://localhost:8080/test/start \
  -H "Content-Type: application/json" \
  -d '{"test_name": "test_production"}'

# Sprawdź status
curl http://localhost:8080/test/status

# Zobacz wyniki w dashboard
open http://localhost:8081
```

## Analiza Wyników

Dashboard pokazuje:

- **Response Time**: Czasy odpowiedzi per agent
- **Success Rate**: Procent udanych requestów
- **Timeline**: Czasy odpowiedzi w czasie
- **Error Analysis**: Lista błędów

Metryki kluczowe:
- Średni czas odpowiedzi
- 95th percentile czasu odpowiedzi
- Success rate per test type
- Inter-agent communication latency

## Ograniczenia i Uwagi

### Bezpłatny Plan Gemini API
- ~1,500 requests/day dla Flash
- ~50 requests/day dla Pro
- Rate limit: 5-15 RPM

### Cloud Run Free Tier
- 2M requests/month
- Minimal CPU/Memory (jak w config)
- Cold starts możliwe

### Rekomendacje
- Uruchamiaj testy max 2-3 razy dziennie
- Wyłącz `run_task_test` dla oszczędności API calls
- Monitoruj usage w Google Cloud Console

## Troubleshooting

### Agents nie odpowiadają
```bash
# Sprawdź URL-e
make config

# Sprawdź logi
make logs

# Test URL-i ręcznie
curl https://crewai-agent-abc123.a.run.app/health
```

### Redis connection failed
```bash
# Restart services
make restart

# Sprawdź kontener Redis
docker logs test-redis
```

### Dashboard nie pokazuje wykresów
- Sprawdź czy są wyniki testów
- Sprawdź logi dashboard: `make logs-dashboard`

## Komendy Makefile

```bash
make setup     # Pierwsza konfiguracja
make build     # Zbuduj obrazy
make start     # Uruchom stack
make test      # Pełny test
make dashboard # Otwórz dashboard
make status    # Status systemu
make logs      # Pokaż logi
make clean     # Wyczyść
make reset     # Pełny reset
```

## Customizacja

### Dodaj nowy test
1. Dodaj metodę w `MinimalLoadTester`
2. Dodaj endpoint w `load_test_runner.py`
3. Dodaj przycisk w dashboard

### Zmień konfigurację testów
Edytuj `TestConfig` w `load_test_runner.py`:
```python
run_new_test: bool = True
new_test_param: int = 5
```

## Deployment

System jest gotowy do uruchomienia lokalnie. Dla produkcji:

1. **Docker Hub**: Push images i deploy na serwer
2. **Cloud Run**: Deploy każdy serwis osobno
3. **Kubernetes**: Użyj manifestów z docker-compose

## Bezpieczeństwo

- Nie zawiera real API keys w repo
- Redis bez autentykacji (tylko local)
- CORS włączony dla local development
