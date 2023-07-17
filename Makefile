checksum-pyproject = $(shell sha256sum pyproject.toml | cut -d " " -f1)
checksum-sources = $(shell find poodle -type f -name "*.py" -exec sha256sum {} \; | sha256sum | cut -d " " -f1)
dist-dir = dist

.venv:
	python -m venv .venv

venv: .venv

requirements-dev.txt:
	python -m piptools compile --extra dev -o requirements-dev.txt pyproject.toml
	python -m pip install -r requirements-dev.txt

.targets/install-dev/$(checksum-pyproject):
	python -m piptools compile --extra dev -o requirements-dev.txt pyproject.toml
	python -m pip install -r requirements-dev.txt
	@mkdir -p .targets/install-dev
	@rm -f .targets/install-dev/*
	@touch .targets/install-dev/$(checksum-pyproject)

.PHONY: install-dev
install-dev: .targets/install-dev/$(checksum-pyproject) requirements-dev.txt

requirements.txt:
	python -m piptools compile -o requirements.txt pyproject.toml
	python -m pip install -r requirements.txt

.targets/install/$(checksum-pyproject):
	python -m piptools compile -o requirements.txt pyproject.toml
	python -m pip install -r requirements.txt
	@mkdir -p .targets/install
	@rm -f .targets/install/*
	@touch .targets/install/$(checksum-pyproject)

.PHONY: install
install: .targets/install/$(checksum-pyproject) requirements.txt

.targets/build/$(checksum-sources):
	python -m build
	@mkdir -p .targets/build
	@rm -f .targets/build/*
	@touch .targets/build/$(checksum-sources)

dist:
	python -m build
	@mkdir -p .targets/build
	@rm -f .targets/build/*
	@touch .targets/build/$(checksum-sources)

.PHONY: build
build: install .targets/build/$(checksum-sources) dist

.PHONY: install-pip
install-pip:
	python -m pip install '.'

.PHONY: lint
lint: install-dev
	python -m mypy poodle
	python -m pylint poodle

.PHONY: format
format: install-dev
	python -m black poodle
	python -m isort poodle

.PHONY: check
check: build
	python -m twine check dist/*

.PHONY: publish
publish: lint check
	python -m twine upload --verbose -u '__token__' dist/*

.PHONY: bumpver
bumpver: format lint build
	@python -m bumpver update $(ARGS)
	@python -m git_changelog > CHANGELOG.md
	@git add --all
	@git commit -m "feat: update changelog"
	@echo -------------------------------- release notes --------------------------------
	@python -m git_changelog --release-notes
	@echo
	@echo -------------------------------------------------------------------------------
	@echo

.PHONY: shell
shell: install
	python -m asyncio

.PHONY: play
play: install
	python examples/playground.py

.PHONY: clean
clean:
	@rm -rf .targets build dist
	@rm -rf `find poodle -name __pycache__`
	@rm -rf bchmnn.poodle.egg-info
