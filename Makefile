build:
	docker compose build bot


clean:
	docker compose down


dev:
	docker compose -f docker-compose.yaml -f docker-compose.expose.yaml run bot


run:
	docker compose -f docker-compose.yaml run bot
