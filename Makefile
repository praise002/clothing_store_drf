ifneq (,$(wildcard ./.env))
include .env
export 
ENV_FILE_PARAM = --env-file .env

endif

create_env:
	py -m venv env

act:
	.\env\Scripts\activate

mmig: 
	python manage.py makemigrations

mig: 
	python manage.py migrate

serv:
	python manage.py runserver

serv-plus:
	python manage.py runserver_plus --cert-file cert.crt
	
suser:
	python manage.py createsuperuser

cpass:
	python manage.py changepassword

shell:
	python manage.py shell

sapp:
	python manage.py startapp

reqn:
	pip install -r requirements.txt

ureqn:
	pip freeze > requirements.txt

help:  ## makefile documentation.
	@sed -ne '/@sed/!s/## //p' $(MAKEFILE_LIST)

lint: ## lint & format
	pre-commit run --all-files

init_db: ## init db
	python manage.py initd

# DOCKER COMMANDS
build:
	docker-compose up --build -d --remove-orphans

up:
	docker-compose up -d

down:
	docker-compose down

show-logs:
	docker-compose logs