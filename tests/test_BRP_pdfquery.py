from pdfquery import PDFQuery

pdf = PDFQuery("../rule_book/BRP SRD 1.0 CHN.pdf")
pdf.load()

print(pdf.get_page(1))
