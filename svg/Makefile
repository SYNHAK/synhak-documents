IMAGES=logo-32.png logo-64.png logo-128.png logo-256.png logo-1024.png logo.pdf

all: $(IMAGES)

logo-%.png: logo.svg Makefile
	inkscape -e $@ $< -w $*

%.pdf: %.svg Makefile
	inkscape -z -T -A $@ $<
