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
