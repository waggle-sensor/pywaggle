all:

.PHONY: test
test:
	PYTHONPATH=src python3 -m unittest discover tests

.PHONY: svc-up
svc-up:
	docker-compose up -d

.PHONY: svc-down
svc-down:
	docker-compose down --volumes
