## Embedding PDF files

If you need to include a research document in the wiki it is possible to embed
a PDF viewer in the generated HTML pages. You need to:

* Add the PDF file to `docs/pdf`.

* Include this tag in the markdown page where you want the embedded viewer to
show up:

```html
<iframe src="/web/viewer.html?file=/pdf/<name_of_your_pdf_file>" width="100%" height="550em"></iframe>
```
