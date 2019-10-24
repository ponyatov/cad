.PHONY: go
go: bin/python CAD.py
	./$^

.PHONY: requirements.txt
requirements.txt:
	pip freeze | grep -v 0.0.0 > $@

.PHONY: merge release

MERGE  = Makefile .gitignore README.md .vscode requirements.txt
MERGE += CAD.py CAD.ini
merge:
	git checkout master
	git checkout ponyatov -- $(MERGE)

NOW = $(shell date +%d%m%y)
REL = $(shell git rev-parse --short=4 HEAD)
release:
	- git tag $(NOW)-$(REL)
	git push && git push --tags
	git checkout ponyatov
