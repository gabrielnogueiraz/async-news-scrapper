.PHONY: install run test test-cov clean docker-build docker-run help

help:
	@echo "Comandos disponíveis:"
	@echo "  make install      - Instala as dependências"
	@echo "  make run          - Executa a aplicação"
	@echo "  make test         - Executa os testes"
	@echo "  make test-cov     - Executa testes com cobertura"
	@echo "  make clean        - Remove arquivos temporários"
	@echo "  make docker-build - Build da imagem Docker"
	@echo "  make docker-run   - Executa container Docker"

install:
	pip install -r requirements.txt

run:
	python -m src.main

test:
	pytest -v

test-cov:
	pytest -v --cov=src --cov-report=term-missing --cov-report=html

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -f .coverage
	rm -f *.db

docker-build:
	docker build -t async-news-scraper .

docker-run:
	docker run -d -p 8000:8000 --name news-scraper async-news-scraper
