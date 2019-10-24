.PHONY: requirements.txt
requirements.txt:
	pip freeze | grep -v 0.0.0 > $@
