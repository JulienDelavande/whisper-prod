DOCKER_REPO=juliendelavande
IMAGE_NAME=cpu_whisper
TAG=0.2
NAMESPACE=whisper-prod

.PHONY: build push deploy

build:
	docker buildx create --use --name mybuilder || true
	docker buildx build --platform linux/amd64 -t $(DOCKER_REPO)/$(IMAGE_NAME):$(TAG) ./backend/cpu_whisper --load

push:
	docker push $(DOCKER_REPO)/$(IMAGE_NAME):$(TAG)

deploy:
	kubectl create namespace $(NAMESPACE) || true
	helm upgrade --install cpu-whisper ./kubernetes --namespace $(NAMESPACE) --set image.repository=$(DOCKER_REPO)/$(IMAGE_NAME) --set image.tag=$(TAG)
