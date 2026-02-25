# =============================================================================
# Cline + Azure DevOps MCP — Makefile
# =============================================================================

IMAGE         ?= your-org/cline-ado
TAG           ?= latest
CLINE_VERSION ?= 2.5.0
ADO_VERSION   ?= 2.4.0

# Include .env if it exists
-include .env
export

.PHONY: build push test run shell version help

## build     : Build the Docker image
build:
	docker build \
		--build-arg CLINE_VERSION=$(CLINE_VERSION) \
		--build-arg ADO_MCP_VERSION=$(ADO_VERSION) \
		-t $(IMAGE):$(TAG) \
		-t $(IMAGE):$(CLINE_VERSION) \
		.

## push      : Build and push image to Docker Hub
push: build
	docker push $(IMAGE):$(TAG)
	docker push $(IMAGE):$(CLINE_VERSION)

## run       : Start an interactive Cline session (mounts current dir)
run:
	docker run -it --rm \
		--env-file .env \
		-v "$(PWD):/workspace" \
		$(IMAGE):$(TAG)

## test      : Run cline --version to verify the image works
test:
	docker run --rm \
		--env-file .env \
		-v "$(PWD):/workspace" \
		$(IMAGE):$(TAG) \
		--version

## shell     : Open a bash shell inside the container (for debugging)
shell:
	docker run -it --rm \
		--env-file .env \
		-v "$(PWD):/workspace" \
		--entrypoint /bin/bash \
		$(IMAGE):$(TAG)

## version   : Show package versions in the image
version:
	@echo "=== Cline ==="
	@docker run --rm $(IMAGE):$(TAG) --version 2>/dev/null || true
	@echo "=== ADO MCP ==="
	@docker run --rm --entrypoint mcp-server-azuredevops $(IMAGE):$(TAG) --version 2>/dev/null || true

## help      : Show this help
help:
	@grep -E '^## ' Makefile | sed 's/^## /  /'
