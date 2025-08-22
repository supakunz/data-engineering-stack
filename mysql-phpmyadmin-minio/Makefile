# Makefile for Data Engineering Stack

.DEFAULT_GOAL := help
.PHONY: help setup up down logs clean build restart status test

# Colors
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Data Engineering Stack - Available Commands:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Quick Start:$(NC)"
	@echo "  make setup    # Initial setup"
	@echo "  make up       # Start all services"
	@echo "  make status   # Check service status"
	@echo "  make logs     # View all logs"
	@echo ""

setup: ## Run initial setup script
	@echo "$(YELLOW)🔧 Running setup script...$(NC)"
	@chmod +x setup.sh
	@./setup.sh
	@echo "$(GREEN)✅ Setup completed!$(NC)"

up: ## Start all services in background
	@echo "$(YELLOW)🚀 Starting all services...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)✅ Services started!$(NC)"
	@make status
	@echo ""
	@echo "$(BLUE)🌐 Access URLs:$(NC)"
	@echo "  Airflow:     http://localhost:8080 (airflow/airflow123)"
	@echo "  Spark:       http://localhost:8081"
	@echo "  MinIO:       http://localhost:9001 (minioadmin/minioadmin)"
	@echo "  Jupyter:     http://localhost:8888"

up-build: ## Build and start all services
	@echo "$(YELLOW)🏗️ Building and starting services...$(NC)"
	@docker-compose up --build -d
	@make status

down: ## Stop all services
	@echo "$(YELLOW)⏹️ Stopping services...$(NC)"
	@docker-compose down
	@echo "$(GREEN)✅ Services stopped!$(NC)"

down-clean: ## Stop services and remove volumes
	@echo "$(YELLOW)🧹 Stopping services and cleaning volumes...$(NC)"
	@docker-compose down -v
	@echo "$(GREEN)✅ Services stopped and volumes removed!$(NC)"

restart: ## Restart all services
	@echo "$(YELLOW)🔄 Restarting services...$(NC)"
	@docker-compose restart
	@make status

status: ## Show service status
	@echo "$(BLUE)📊 Service Status:$(NC)"
	@docker-compose ps

logs: ## Show logs for all services
	@echo "$(BLUE)📋 Showing logs (Ctrl+C to exit):$(NC)"
	@docker-compose logs -f

logs-airflow: ## Show Airflow logs
	@echo "$(BLUE)📋 Airflow logs:$(NC)"
	@docker-compose logs -f airflow-webserver airflow-scheduler airflow-worker

logs-spark: ## Show Spark logs
	@echo "$(BLUE)📋 Spark logs:$(NC)"
	@docker-compose logs -f spark-master spark-worker-1 spark-worker-2

logs-minio: ## Show MinIO logs
	@echo "$(BLUE)📋 MinIO logs:$(NC)"
	@docker-compose logs -f minio

build: ## Build all services
	@echo "$(YELLOW)🏗️ Building services...$(NC)"
	@docker-compose build --no-cache
	@echo "$(GREEN)✅ Build completed!$(NC)"

shell-airflow: ## Access Airflow container shell
	@echo "$(BLUE)🐚 Accessing Airflow shell...$(NC)"
	@docker-compose exec airflow-webserver bash

shell-spark: ## Access Spark master shell
	@echo "$(BLUE)🐚 Accessing Spark master shell...$(NC)"
	@docker-compose exec spark-master bash

shell-jupyter: ## Access Jupyter container shell
	@echo "$(BLUE)🐚 Accessing Jupyter shell...$(NC)"
	@docker-compose exec jupyter bash

test-connections: ## Test all service connections
	@echo "$(YELLOW)🔍 Testing service connections...$(NC)"
	@echo "Testing MinIO..."
	@curl -s http://localhost:9000/minio/health/live > /dev/null && echo "$(GREEN)✅ MinIO: OK$(NC)" || echo "$(RED)❌ MinIO: FAILED$(NC)"
	@echo "Testing Airflow..."
	@curl -s http://localhost:8080/health > /dev/null && echo "$(GREEN)✅ Airflow: OK$(NC)" || echo "$(RED)❌ Airflow: FAILED$(NC)"
	@echo "Testing Spark Master..."
	@curl -s http://localhost:8081 > /dev/null && echo "$(GREEN)✅ Spark: OK$(NC)" || echo "$(RED)❌ Spark: FAILED$(NC)"
	@echo "Testing Jupyter..."
	@curl -s http://localhost:8888 > /dev/null && echo "$(GREEN)✅ Jupyter: OK$(NC)" || echo "$(RED)❌ Jupyter: FAILED$(NC)"

clean: ## Clean up Docker resources
	@echo "$(YELLOW)🧹 Cleaning up Docker resources...$(NC)"
	@docker-compose down -v
	@docker system prune -f
	@docker volume prune -f
	@echo "$(GREEN)✅ Cleanup completed!$(NC)"

backup-data: ## Backup MinIO data
	@echo "$(YELLOW)💾 Creating backup of MinIO data...$(NC)"
	@mkdir -p backups
	@docker-compose exec minio tar czf - /data > backups/minio-backup-$$(date +%Y%m%d_%H%M%S).tar.gz
	@echo "$(GREEN)✅ Backup created in backups/ directory$(NC)"

monitor: ## Show resource usage
	@echo "$(BLUE)📊 Container Resource Usage:$(NC)"
	@docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

check-requirements: ## Check system requirements
	@echo "$(BLUE)🔍 Checking system requirements...$(NC)"
	@echo "Docker version:"
	@docker --version || echo "$(RED)❌ Docker not installed$(NC)"
	@echo "Docker Compose version:"
	@docker-compose --version || echo "$(RED)❌ Docker Compose not installed$(NC)"
	@echo "Available memory:"
	@free -h | grep "Mem:" || echo "$(RED)❌ Cannot check memory$(NC)"
	@echo "Available disk space:"
	@df -h . | tail -1 || echo "$(RED)❌ Cannot check disk space$(NC)"

dev: ## Start in development mode with file watching
	@echo "$(YELLOW)👨‍💻 Starting in development mode...$(NC)"
	@docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@make status

urls: ## Show all service URLs
	@echo "$(BLUE)🌐 Service URLs: