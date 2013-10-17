all: latex svg

.PHONY: latex svg

latex:
	make -C latex

svg:
	make -C svg
