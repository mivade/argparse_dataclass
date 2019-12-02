.PHONY: all
all:
	@echo "Please choose a target"

.PHONY: readme
readme:
	python -c "import argparse_dataclass; print(argparse_dataclass.__doc__.strip())" > README.rst

.PHONY: test
test:
	python -m doctest argparse_dataclass.py

.PHONY: build
build:
	flit build
