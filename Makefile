# The main service name for your Python app
APP_SERVICE := app
# The main service name for your PostgreSQL database
DB_SERVICE := db
# The name of the persistent volume
DB_VOLUME := github-trends-reporter_postgres_data

# Use .ONESHELL to avoid issues with multi-line shell commands
.ONESHELL:

.PHONY: build up down logs clean logs-app

build:
	@echo "Building application image..."
	docker compose build $(APP_SERVICE)

up: build
	@echo "Starting services..."
	# Run the full pipeline and stop services once 'app' exits
	docker compose up --abort-on-container-exit $(DB_SERVICE) $(APP_SERVICE)

down:
	@echo "Stopping and removing containers..."
	docker compose down

logs:
	@echo "Showing all logs..."
	docker compose logs -f

logs-app:
	@echo "Showing application logs only..."
	docker compose logs -f $(APP_SERVICE)

clean: down
	@echo "Removing database volume to ensure a fresh start..."
	docker volume rm $(DB_VOLUME)
	@echo "Removing generated data and logs..."
	rm -rf data/raw data/outputs logs