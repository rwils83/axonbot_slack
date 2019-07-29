PACKAGE := "axonbot"
VERSION := $(shell grep __version__ $(PACKAGE)/version.py | cut -d\" -f2)

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
	docker build -t axonius/axonbot:latest .

docker_shell:
	docker run --rm --name axonbot --interactive --tty -e SLACK_API_TOKEN -e AX_URL -e AX_KEY -e AX_SECRET -e HTTPS_PROXY -e AX_HTTPS_PROXY --volume axonbot_config:/home/axonbot/axonbot_config axonius/axonbot bash

docker_config:
	docker run --rm --name axonbot --interactive --tty -e SLACK_API_TOKEN -e AX_URL -e AX_KEY -e AX_SECRET -e HTTPS_PROXY -e AX_HTTPS_PROXY --volume axonbot_config:/home/axonbot/axonbot_config axonius/axonbot axonbot config

docker_run:
	docker run --rm --name axonbot --interactive --tty -e SLACK_API_TOKEN -e AX_URL -e AX_KEY -e AX_SECRET -e HTTPS_PROXY -e AX_HTTPS_PROXY --volume axonbot_config:/home/axonbot/axonbot_config axonius/axonbot

docker_run_prod:
	docker run -d --name axonbot --restart always -e SLACK_API_TOKEN -e AX_URL -e AX_KEY -e AX_SECRET -e HTTPS_PROXY -e AX_HTTPS_PROXY --volume axonbot_config:/home/axonbot/axonbot_config axonius/axonbot

docker_stop:
	docker stop axonbot || true

docker_clean:
	$(MAKE) docker_stop
	docker container rm axonbot || true
	docker volume rm axonbot_config || true

docker_prune:
	docker system prune -a -f

# Docker publish

clean:
	$(MAKE) clean_files
	$(MAKE) pkg_clean
	$(MAKE) pipenv_clean
	$(MAKE) docker_clean || true
