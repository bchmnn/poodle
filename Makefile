venv:
	python -m venv .venv

build:
	python -m pip install '.[dev]'

dist: build
	python -m build

check:
	python -m twine check dist/*

publish:
	python -m twine upload dist/*

bumpver:
	@python -m bumpver update $(ARGS)
	@python -m git_changelog > CHANGELOG.md
	@git add --all
	@git commit -m "feat: update changelog"
	@echo -------------------------------- release notes --------------------------------
	@python -m git_changelog --release-notes
	@echo
	@echo -------------------------------------------------------------------------------
	@echo

shell:
	python -m asyncio

clean:
	rm -rf dist build
