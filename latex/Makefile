IMAGES = logo.svg
DOCUMENTS = guest-sign-sheet.pdf

all: images documents

images: $(IMAGES)

documents: $(DOCUMENTS)

%.pdf: %.svg
		inkscape -z -A $@ $<

%.pdf: %.latex
		pdflatex $<
