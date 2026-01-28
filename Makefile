# Makefile para ScrapPoliticos
# Simplifica comandos Docker para desarrollo y producción

.PHONY: help build up down logs shell clean test validate export

# Colores para output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

help: ## Muestra esta ayuda
	@echo "$(BLUE)ScrapPoliticos - Comandos Docker$(NC)"
	@echo ""
	@echo "$(GREEN)Comandos disponibles:$(NC)"
	@echo "  $(YELLOW)build$(NC)          Construye la imagen Docker"
	@echo "  $(YELLOW)up$(NC)             Inicia el scraper en modo attached"
	@echo "  $(YELLOW)up-detached$(NC)    Inicia el scraper en modo detached"
	@echo "  $(YELLOW)down$(NC)           Detiene todos los contenedores"
	@echo "  $(YELLOW)logs$(NC)           Muestra logs del scraper"
	@echo "  $(YELLOW)shell$(NC)          Abre una shell interactiva en el contenedor"
	@echo "  $(YELLOW)clean$(NC)          Limpia contenedores, volúmenes e imágenes"
	@echo "  $(YELLOW)clean-data$(NC)     Limpia archivos de datos generados"
	@echo "  $(YELLOW)rebuild$(NC)        Limpia y reconstruye desde cero"
	@echo "  $(YELLOW)validate$(NC)       Ejecuta validación de datos"
	@echo "  $(YELLOW)test$(NC)           Ejecuta tests del proyecto"
	@echo "  $(YELLOW)export$(NC)         Exporta datos a Excel"
	@echo "  $(YELLOW)status$(NC)         Muestra el estado de los contenedores"
	@echo "  $(YELLOW)restart$(NC)        Reinicia el scraper"
	@echo "  $(YELLOW)filter$(NC)         Analiza y filtra resultados válidos"
	@echo "  $(YELLOW)retry-failed$(NC)   Reintenta fallidos con estrategia potente"
	@echo "  $(YELLOW)polish$(NC)         Flujo completo: filter -> retry -> filter"

filter: ## Analiza y filtra resultados válidos
	@echo "$(BLUE)Analizando resultados...$(NC)"
	docker-compose run --rm scraper python scripts/analyze_and_filter.py


retry-failed: ## Reintenta fallidos con estrategia potente
	@echo "$(BLUE)Reintentando fallidos con máxima potencia (JavaScript)...$(NC)"
	docker-compose run --rm -e SOURCE_FILE=data/retry_queue.json -e FORCE_STRATEGY=javascript scraper python main.py

retry-direct: ## Reintenta fallidos SIN PROXY (Direct IP) y máxima potencia
	@echo "$(BLUE)Reintentando fallidos con Direct IP y 300s timeout...$(NC)"
	docker-compose run --rm -e SOURCE_FILE=data/retry_queue.json -e FORCE_STRATEGY=javascript -e HTTP_PROXY= -e HTTPS_PROXY= scraper python main.py


polish: filter retry-failed ## Flujo completo: filter -> retry -> filter
	@echo "$(GREEN)Reintentos finalizados. Actualizando lista de válidos...$(NC)"
	docker-compose run --rm scraper python scripts/analyze_and_filter.py


build: ## Construye la imagen Docker
	@echo "$(BLUE)Construyendo imagen Docker...$(NC)"
	docker-compose build

up: ## Inicia el scraper en modo attached
	@echo "$(BLUE)Iniciando scraper...$(NC)"
	docker-compose up scraper

up-detached: ## Inicia el scraper en modo detached
	@echo "$(BLUE)Iniciando scraper en background...$(NC)"
	docker-compose up -d scraper

down: ## Detiene todos los contenedores
	@echo "$(BLUE)Deteniendo contenedores...$(NC)"
	docker-compose down

logs: ## Muestra logs del scraper
	@echo "$(BLUE)Mostrando logs...$(NC)"
	docker-compose logs -f scraper

shell: ## Abre una shell interactiva en el contenedor
	@echo "$(BLUE)Abriendo shell en contenedor...$(NC)"
	docker-compose run --rm scraper /bin/bash

clean: ## Limpia contenedores, volúmenes e imágenes
	@echo "$(YELLOW)Limpiando recursos Docker...$(NC)"
	docker-compose down -v
	docker system prune -f

clean-data: ## Limpia archivos de datos generados
	@echo "$(YELLOW)Limpiando datos...$(NC)"
	rm -rf data/results.json data/results_partial.jsonl logs/scraper.log

rebuild: clean build ## Limpia y reconstruye desde cero
	@echo "$(GREEN)Reconstrucción completa finalizada$(NC)"

validate: ## Ejecuta validación de datos
	@echo "$(BLUE)Validando datos extraídos...$(NC)"
	docker-compose run --rm scraper python tests/validate_improvements.py

test: ## Ejecuta tests del proyecto
	@echo "$(BLUE)Ejecutando tests...$(NC)"
	docker-compose run --rm scraper pytest tests/

export: ## Exporta datos a Excel
	@echo "$(BLUE)Exportando datos a Excel...$(NC)"
	docker-compose run --rm scraper python scripts/export_excel.py

status: ## Muestra el estado de los contenedores
	@echo "$(BLUE)Estado de contenedores:$(NC)"
	docker-compose ps

restart: down up ## Reinicia el scraper
	@echo "$(GREEN)Scraper reiniciado$(NC)"
