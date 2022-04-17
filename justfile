default: lint

pdf-docs: latex-docs
	make -C doc-source/build/latex/

latex-docs:
	SPHINX_BUILDER=latex tox -e docs

unused-imports:
	tox -e lint -- --select F401

incomplete-defs:
	#!/usr/bin/env bash
	tox -e mypy -- --disallow-incomplete-defs --disallow-untyped-defs | grep "Function is missing a .* annotation" || exit 0

vdiff:
	git diff $(repo-helper show version -q)..HEAD

bare-ignore:
	greppy '# type:? *ignore(?!\[|\w)' -s

lint: unused-imports incomplete-defs bare-ignore
	tox -n qa
