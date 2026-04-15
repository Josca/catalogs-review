VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
OUTPUT := output

.PHONY: html pdf odt docx clean install

install:
	$(PIP) install -r requirements.txt

html:
	$(PYTHON) generate.py

pdf: html
	pandoc $(OUTPUT)/report.html -o $(OUTPUT)/report.pdf --pdf-engine=wkhtmltopdf

odt: html
	pandoc $(OUTPUT)/report.html -o $(OUTPUT)/report.odt

docx: html
	pandoc $(OUTPUT)/report.html -o $(OUTPUT)/report.docx

clean:
	rm -rf $(OUTPUT)
