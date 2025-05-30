DC = docker-compose
EXEC = docker exec -it
LOGS = docker logs
ENV = --env-file .env
APP = barter_django
GROUP = -p barter_django

APP_FILE = ./docker_compose/app_dev.yaml
POSTGRES_FILE = ./docker_compose/postgres.yaml
MIGRATIONS_FILE = ./docker_compose/migrations.yaml
POSTGRES_TEST_FILE= ./docker_compose/postgres_test.yaml
PGADMIN_FILE = ./docker_compose/pg_admin.yaml

.PHONY: app
app:
	$(DC) $(GROUP) -f $(APP_FILE) -f $(POSTGRES_FILE) -f $(POSTGRES_TEST_FILE) -f $(PGADMIN_FILE) $(ENV) up --build -d

.PHONY: down
down:
	$(DC) $(GROUP) -f $(APP_FILE) -f $(POSTGRES_FILE) -f $(POSTGRES_TEST_FILE) -f $(PGADMIN_FILE) $(ENV) down

.PHONY: migrations
migrations:
	$(DC) $(GROUP) -f $(MIGRATIONS_FILE) $(ENV) up --build -d

# Optional: Add a command to make migrations when needed
.PHONY: makemigrations
makemigrations:
	$(EXEC) $(APP) python src/manage.py makemigrations

.PHONY: logs
logs:
	$(LOGS) $(APP) -f

.PHONY: app-exec
app-exec:
	$(EXEC) $(APP) bash
