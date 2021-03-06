# This Makefile generates documents from source files. Its pretty neat, but
# could be a bit hard to understand at first.
#
# Check out the full pipeline at:
# 	https://synhak.org/wiki/Documents
#
# To use it, simply define DOCUMENTS as a list of documents that we want
# generated, and include it:
#
# DOCUMENTS = foo.pdf
# include ../Makefile
#
# The Makefile will find the listed source files and process them.

# Default ignore list
IGNORE=*.aux *.log *.out *.nav *.snm *.toc .gitignore

# Find all subdirectories with Makefile in them
SUBDIRS:=$(dir ${shell find -mindepth 2 -name Makefile -print})

# Generate a list of targets named some-subdir/.clean
SUBCLEAN=$(addsuffix .clean,$(SUBDIRS))

# Generate a list of targets named some-subdir/some-doc.pdf.clean
DOCCLEAN=$(addsuffix .clean,$(DOCUMENTS))

# Extra files to clean up that aren't in the DOCUMENTS variable
EXTRACLEAN=*.version.latex.clean $(addsuffix .clean,$(CLEANUP))

# Set the current directory for sub-makes
export ROOT := $(dir $(lastword $(MAKEFILE_LIST)))

# Influence where latex finds synhak.sty
TEXINPUTS:=.:$(PWD):$(TEXINPUTS):$(ROOT)/common/

# Makefile hacks for use later on
noop=
space = $(noop) $(noop)

# Always make these targets and don't complain if they're already made
.PHONY: all $(SUBDIRS) clean $(SUBCLEAN) $(CLEANUP) $(DOCCLEAN)

# The default list of things to make
all: $(DOCUMENTS) $(SUBDIRS) .gitignore

# Default list of things to clean up
clean: $(SUBCLEAN) $(DOCCLEAN) $(EXTRACLEAN)

# For each subdir, run a sub-make
$(SUBDIRS):
	$(MAKE) $(MFLAGS) -C $@

# Clean up documents: Files in EXTRACLEA, DOCCLEAN, and any generated *.clean
# targets
$(EXTRACLEAN) $(DOCCLEAN): %.clean:
	rm -vf $*

# Clean up subdirectories by running make clean in each directory
$(SUBCLEAN): %.clean:
	$(MAKE) $(MFLAGS) -C $* -f $(ROOT)/Makefile clean

# Rule to generate PDFs from SVGs
%.pdf: %.svg
		inkscape -z -T -A $@ $<

# If we want a foo.pdf and there is a foo.latex, it probably means foo.pdf
# comes from foo.latex. We'll depend on a foo.version.latex, the synhak.cls, our
# logo, and of course foo.latex. Then we'll run pdflatex to generate the pdf.
%.pdf: %.latex %.version.latex $(ROOT)/common/synhak.cls $(ROOT)/impress/logo/logo.pdf
		cd $(dir $<) && TEXINPUTS=${TEXINPUTS} pdflatex -output-format=pdf $(notdir $<) </dev/null

# A rule to generate foo.version.latex with git information
%.version.latex: ../.git/logs/HEAD
	echo "%%% This file is generated by Makefile.\n" >> $@
	echo "%%% Do not edit!\n" >> $@
	git log -1 --format="format:\
			\\gdef\\GITAbrHash{%h}\
			\\gdef\\GITAuthorDate{%ad}\
			\\gdef\\GITAuthorName{%an}" $*.latex >> $@
	git status -s $*.latex | grep ?? && echo "\\gdef\\GITAbrHash{UNCOMMITTED}\\gdef\\GITAuthorDate{??/??/??}\\gdef\\GITAuthorName{${USER}@${HOSTNAME}}" >> $@ || exit 0
	git status -s $*.latex | grep ^A && echo "\\gdef\\GITAbrHash{UNCOMMITTED}\\gdef\\GITAuthorDate{??/??/??}\\gdef\\GITAuthorName{${USER}@${HOSTNAME}}" >> $@ || exit 0

# If we want a foo.png and there exists a foo.svg, generate a png from it.
%.png: .svg
	inkscape -e $@ $<

# Generates .gitignore for any files we make since some directories have a mix
# of generated .pdfs and scanned .pdfs
.gitignore: Makefile
	echo -e "$(subst ${space},\n,${DOCUMENTS})" > .gitignore
	echo -e "$(subst ${space},\n,${IGNORE})" >> .gitignore
