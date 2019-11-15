## Embedding PDF files

If you need to include a research document in the wiki it is possible to embed
a PDF viewer in the generated HTML pages. You need to:

* Add the PDF file to `docs/_static/pdf`.

* Include this code in the markdown page where you want the embedded viewer to
show up:

```html
<style>
.md-grid {
    max-width: inherit;
}
.md-sidebar--secondary {
    display: none;
}
.md-content {
    margin-right: 0em;
}
</style>
<iframe src="../_static/pdfview/viewer.html?file=../pdf/<name_of_your_pdf_file>" width="100%" height="650em"></iframe>
```
