IMAGES = images/logo.pdf
DOCUMENTS = guest-sign-sheet.pdf waiver.pdf

all: $(DOCUMENTS)

clean:
	rm -f {,images/}*.pdf {,images/}*.log {,images/}*.out {,images/}*.aux

$(DOCUMENTS): $(IMAGES)

%.pdf: %.svg
		inkscape -z -A $@ $<

%.pdf: %.latex
		pdflatex $<

.PHONY: all clean
