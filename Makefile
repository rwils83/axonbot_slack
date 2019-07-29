PACKAGE := "axonbot"
VERSION := $(shell grep __version__ $(PACKAGE)/version.py | cut -d\" -f2)
DATE := $(shell date -u +'%Y-%m-%dT%H:%M:%SZ')
GIT_SHA := $(shell git rev-parse --short HEAD)

# FUTURE: write Makefile doc

.PHONY: build docs

init:
	$(MAKE) pip_install_tools
	$(MAKE) clean
	$(MAKE) pyenv_init
	$(MAKE) pipenv_init

pip_install_tools:
	pip install --quiet --upgrade --requirement requirements-pkg.txt

pipenv_install_lint:
	pipenv run pip install --quiet --upgrade --requirement requirements-lint.txt

pipenv_install_build:
	pipenv run pip install --quiet --upgrade --requirement requirements-build.txt

pipenv_clean:
	pipenv --rm || true

pipenv_init:
	pipenv install --dev --skip-lock

pyenv_init:
	# FUTURE: THROW ERROR IF NO PYENV AND SHOW LINK TO PYENV INSTALL INSTRUCTIONS
	pyenv install 3.7.3 -s
	pyenv local 3.7.3

lint:
	$(MAKE) pipenv_install_lint
	pipenv run which black && black $(PACKAGE) setup.py
	pipenv run flake8 --max-line-length 89 $(PACKAGE) setup.py
	pipenv run bandit -r . --skip B101 -x playground.py,setup.py

git_check:
	@git diff-index --quiet HEAD && echo "*** REPO IS CLEAN" || (echo "!!! REPO IS DIRTY"; false)
	@git tag | grep "$(VERSION)" && echo "*** FOUND TAG: $(VERSION)" || (echo "!!! NO TAG FOUND: $(VERSION)"; false)

git_tag:
	@git tag "$(VERSION)"
	@git push --tags
	@echo "*** ADDED TAG: $(VERSION)"

pkg_publish:
	$(MAKE) lint
	$(MAKE) pkg_build
	$(MAKE) git_check
	pipenv run twine upload dist/*

pkg_build:
	$(MAKE) pkg_clean
	$(MAKE) pipenv_install_build

	@echo "*** Building Source and Wheel (universal) distribution"
	pipenv run python setup.py sdist bdist_wheel --universal

	@echo "*** Checking package with twine"
	pipenv run twine check dist/*

pkg_clean:
	rm -rf build dist *.egg-info

clean_files:
	find . -type d -name "__pycache__" | xargs rm -rf
	find . -type f -name ".DS_Store" | xargs rm -f
	find . -type f -name "*.pyc" | xargs rm -f

docker_build:
	docker build --build-arg BUILD_DATE=$(DATE) --build-arg BUILD_VERSION=$(VERSION) --build-arg BUILD_REF=$(GIT_SHA) -t axonius/axonbot:latest .

docker_dev:
	docker run --rm --name axonbot --interactive --tty --env=SLACK_API_TOKEN --env=AX_URL --env=AX_KEY --env=AX_SECRET --env=HTTPS_PROXY --env=AX_HTTPS_PROXY --volume axonbot:/axonbot axonius/axonbot bash

docker_config:
	docker run --rm --name axonbot --interactive --tty --env=SLACK_API_TOKEN --env=AX_URL --env=AX_KEY --env=AX_SECRET --env=HTTPS_PROXY --env=AX_HTTPS_PROXY --volume axonbot:/axonbot axonius/axonbot axonbot config

docker_test:
	docker run --rm --name axonbot --interactive --tty --env=SLACK_API_TOKEN --env=AX_URL --env=AX_KEY --env=AX_SECRET --env=HTTPS_PROXY --env=AX_HTTPS_PROXY --volume axonbot:/axonbot axonius/axonbot axonbot test

docker_run_dev:
	docker run --rm --name axonbot --interactive --tty --env=SLACK_API_TOKEN --env=AX_URL --env=AX_KEY --env=AX_SECRET --env=HTTPS_PROXY --env=AX_HTTPS_PROXY --volume axonbot:/axonbot axonius/axonbot

docker_run_prod:
	docker run --detach --name axonbot --restart always --env=SLACK_API_TOKEN --env=AX_URL --env=AX_KEY --env=AX_SECRET --env=HTTPS_PROXY --env=AX_HTTPS_PROXY --volume axonbot:/axonbot axonius/axonbot

docker_stop:
	docker stop axonbot || true

docker_clean:
	$(MAKE) docker_stop
	docker container rm -f -v axonbot || true
	docker volume rm axonbot || true

docker_prune:
	docker system prune -a -f

# Docker publish

clean:
	$(MAKE) clean_files
	$(MAKE) pkg_clean
	$(MAKE) pipenv_clean
	$(MAKE) docker_clean || true
