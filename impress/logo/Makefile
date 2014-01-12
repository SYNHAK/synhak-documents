DOCUMENTS= \
	logo-32.png \
	logo-64.png \
	logo-128.png \
	logo-256.png \
	logo-1024.png \
	logo.pdf \
	made-at-synhak.pdf

include ../../Makefile

logo-%.png: logo.svg
	inkscape -e $@ $< -w $*
