###############################################################################
# HELP / DEFAULT COMMAND
###############################################################################
.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: build
build: ## build a local docker container
	docker build -t ogaas .

.PHONY: build-remote
build-remote: ## build on the remote container
	docker -H 90daydx build -t ogaas .

.PHONY: run
run: ## run the container in local development mode
	docker run \
		-it \
		--rm \
		-v $(PWD)/src:/app \
		-p 8000:8000 \
		ogaas uvicorn --reload --port 8000 --host 0.0.0.0 main:app
