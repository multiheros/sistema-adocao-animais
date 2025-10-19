# Simple shortcuts for common tasks
# Usage examples:
#   make setup
#   make migrate
#   make run HOST=127.0.0.1 PORT=8000
#   make seed-animals COUNT=10 IMAGES=generate
#   make seed-adoptions COUNT=12 MODE=mix

SHELL := /bin/bash
PY ?= python
HOST ?= 0.0.0.0
PORT ?= 8000
COUNT ?= 10
IMAGES ?= none        # none | generate | download
MODE ?= mix           # mix | pending | approved | rejected
ADP_COUNT ?= 15       # adoptions count for demo
CREATE_USERS ?= 5     # demo users to create in seed_adoptions
USER ?= admin         # used by backfill-created-by
ADMIN_USER ?= admin
ADMIN_EMAIL ?= admin@example.com
ADMIN_PASSWORD ?= admin123

.PHONY: help setup check migrate superuser run test cov lint clean seed-animals seed-adoptions backfill-created-by shell demo admin demo-admin reset quick-demo ci-local

help:
	@echo "Targets disponíveis:"
	@echo "  setup                 - Instala dependências (requirements.txt)"
	@echo "  check                 - Executa checks do Django"
	@echo "  migrate               - makemigrations + migrate"
	@echo "  superuser             - Cria superusuário"
	@echo "  run [HOST,PORT]       - Sobe o servidor de dev (padrão: $(HOST):$(PORT))"
	@echo "  test                  - Roda testes com verbosity 2"
	@echo "  cov                   - Roda testes com coverage e gera htmlcov/"
	@echo "  lint                  - flake8 (não falha o build local)"
	@echo "  seed-animals          - Popula animais (COUNT=$(COUNT) IMAGES=$(IMAGES))"
	@echo "  seed-adoptions        - Popula adoções (COUNT=$(COUNT) MODE=$(MODE))"
	@echo "  backfill-created-by   - Atribui created_by a animais sem dono (USER=$(USER))"
	@echo "  clean                 - Limpa artefatos de build/test"
	@echo "  shell                 - Abre manage.py shell"
	@echo "  demo                  - Setup completo + seeds + sobe o servidor"
	@echo "  admin                 - Cria/atualiza superusuário não interativo (ADMIN_USER=$(ADMIN_USER))"
	@echo "  demo-admin            - Cria admin e executa 'demo' (valores padrão personalizáveis)"
	@echo "  reset                 - APAGA db.sqlite3 e media/ e roda demo-admin do zero (cuidado!)"
	@echo "  quick-demo            - Alias sem prompt (admin + demo) usando valores padrão"
    @echo "  ci-local              - Simula pipeline CI localmente (checks, lint, tests+coverage XML/HTML)"

setup:
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements.txt

check:
	$(PY) manage.py check

migrate:
	$(PY) manage.py makemigrations
	$(PY) manage.py migrate

superuser:
	$(PY) manage.py createsuperuser

run:
	$(PY) manage.py runserver $(HOST):$(PORT)

test:
	$(PY) manage.py test --verbosity 2

cov:
	@which coverage >/dev/null 2>&1 || { echo "Instalando coverage..."; $(PY) -m pip install coverage; }
	coverage run manage.py test --verbosity 2
	coverage report -m
	coverage html
	@echo "Abra htmlcov/index.html para ver o relatório."

lint:
	@which flake8 >/dev/null 2>&1 || { echo "Instalando flake8..."; $(PY) -m pip install flake8; }
	flake8 . --max-line-length=100 --extend-exclude .venv,**/migrations/** || true

seed-animals:
	$(PY) manage.py seed_animals --count $(COUNT) --with-images $(IMAGES) --force

seed-adoptions:
	$(PY) manage.py seed_adoptions --count $(COUNT) --mode $(MODE) --force

backfill-created-by:
	$(PY) manage.py backfill_animals_created_by --username $(USER) --only-null

clean:
	find . -name "__pycache__" -type d -prune -exec rm -rf {} +
	rm -f .coverage coverage.xml
	rm -rf htmlcov

shell:
	$(PY) manage.py shell

demo:
	@echo "==> Instalando dependências"
	$(MAKE) setup
	@echo "==> Migrando banco"
	$(MAKE) migrate
	@echo "==> Populando animais (COUNT=$(COUNT), IMAGES=$(IMAGES))"
	$(PY) manage.py seed_animals --count $(COUNT) --with-images $(IMAGES) --force
	@echo "==> Populando adoções (COUNT=$(ADP_COUNT), MODE=$(MODE), CREATE_USERS=$(CREATE_USERS))"
	$(PY) manage.py seed_adoptions --count $(ADP_COUNT) --mode $(MODE) --create-users $(CREATE_USERS) --force
	@echo "==> Subindo servidor em $(HOST):$(PORT)"
	$(MAKE) run

admin:
	@echo "==> Garantindo superusuário: $(ADMIN_USER)"
	$(PY) manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); u, created = User.objects.get_or_create(username='$(ADMIN_USER)', defaults={'email':'$(ADMIN_EMAIL)'}); u.is_staff=True; u.is_superuser=True; u.email='$(ADMIN_EMAIL)'; u.set_password('$(ADMIN_PASSWORD)'); u.save(); print('Superuser ready:', u.username, 'created' if created else 'updated')"

demo-admin:
	$(MAKE) admin
	$(MAKE) demo

reset:
	@echo "[ATENÇÃO] Isso vai apagar db.sqlite3 e a pasta media/ e recriar tudo do zero."
	@read -p "Confirmar? (y/N) " ans; if [ "$$ans" != "y" ] && [ "$$ans" != "Y" ]; then echo "Cancelado."; exit 1; fi
	rm -f db.sqlite3
	rm -rf media
	$(MAKE) demo-admin

quick-demo:
	$(MAKE) demo-admin

ci-local:
	@echo "==> Django system checks"
	$(MAKE) check
	@echo "==> Lint (flake8)"
	$(MAKE) lint
	@echo "==> Tests with coverage (HTML + XML)"
	$(MAKE) cov
	coverage xml
	@echo "Relatórios gerados: .coverage, coverage.xml e htmlcov/index.html"
