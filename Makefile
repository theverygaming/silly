.PHONY: all
all: precommit


.PHONY: precommit
precommit: test

MODULES_TO_TEST := $(shell find . -name "__manifest__.py" | xargs -n1 dirname | xargs -n1 basename)

.PHONY: test
test:
	./silly-entry --connstr "sqlite:///silly_test_run.db" --loglevel DEBUG update --modules $(MODULES_TO_TEST)
	./silly-entry --connstr "sqlite:///silly_test_run.db" --loglevel DEBUG test
	./silly-entry --connstr "sqlite:///silly_test_run.db" --loglevel DEBUG uninstall --modules $(MODULES_TO_TEST)

	./silly-entry --connstr "postgresql://postgres:postgres@localhost:5432/postgres" --loglevel DEBUG update --modules $(MODULES_TO_TEST)
	coverage run --source=silly,modules ./silly-entry --connstr "postgresql://postgres:postgres@localhost:5432/postgres" --loglevel DEBUG test
	./silly-entry --connstr "postgresql://postgres:postgres@localhost:5432/postgres" --loglevel DEBUG uninstall --modules $(MODULES_TO_TEST)
	coverage html --omit="*/tests/test_*.py,__manifest__.py"
	coverage report -m --omit="*/tests/test_*.py,__manifest__.py"

.PHONY: postgrescontainer
postgrescontainer:
	docker run --rm -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres

.PHONY: psql
psql:
	PGPASSWORD="postgres" psql -d postgres -U postgres -h 127.0.0.1 $@

.PHONY: format
format: 
	black silly tests modules \
    --line-length 100 \
    --preview \
    --enable-unstable-feature string_processing \
    --exclude '/migrations/versions/.*\.py'
