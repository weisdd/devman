setup:
	python3 -m venv .venv

install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

lint:
	flake8 --max-line-length=88 app

build:
	docker build . -t quay.io/weisdd/devman:$(TAG)

push:
	docker push quay.io/weisdd/devman:$(TAG)
