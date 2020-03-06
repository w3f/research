all: main.pdf

%.pdf: %.tex $(wildcard *.tex)
	latexmk -pdf "$<"
