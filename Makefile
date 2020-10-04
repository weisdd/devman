setup:
	python3 -m venv .venv

install:
	pip install --upgrade pip &&\
		pip install -r src/app/requirements.txt

lint:
	flake8 --max-line-length=88 src/app

build:
	docker build . -t quay.io/weisdd/devman:$(TAG)

push:
	docker push quay.io/weisdd/devman:$(TAG)
