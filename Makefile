.PHONY: all
all: precommit


.PHONY: precommit
precommit: test

.PHONY: test
test:
	coverage run --source=silly,modules test.py no_update
	coverage html --omit="tests/*"
	coverage report -m --omit="tests/*"

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
