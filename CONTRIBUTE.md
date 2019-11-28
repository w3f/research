## Embedding PDF files

If you need to include a research document in the wiki it is possible to embed
a PDF viewer in the generated HTML pages. You need to:

* Add the PDF file to `docs/_static/pdf`.

* Include this code in the markdown page where you want the embedded viewer to
show up:

```html
<iframe src="../_static/pdfview/viewer.html?file=../pdf/<name_of_your_pdf_file>" width="100%" height="650em"></iframe>
```

## Maintaining rst indexes

We recently switched to sphinx from mkdocs mainly to support [reStructuredText
syntax](http://docutils.sourceforge.net/rst.html). This is more powerful than
markdown and can support more complex things, e.g. nested lists within tables.

One unfortunate side effect is the necessity of having to manually maintain
index files, because that is how sphinx determines site and document structure.
To make this easy for you, a `./maintain-indexes.sh` script has been written
that automates the creation of new indexes. Run this whenever you create a new
directory with new pages in it. In general, it will generate an index file
called `${directory}.rst` that points to `${directory}/index` (which sphinx
knows to treat either as .md or .rst, whichever it finds first).

If you check `git status` and `git diff` after running that script, you can see
what was done, and then you can edit `${directory}.rst` as you see fit. Do not
remove the TOC as that is needed for sphinx to know the site structure. Some
edits you could do, if appropriate, are:

- Change the redirection from `index` to some other name, if you didn't use
  `index.md` as the main page for the directory.
- Remove the autoredirect (the `<meta http-equiv="refresh">`) and instead add
  some meaningful context to the page, as a "landing page" before you go onto
  the main page.
