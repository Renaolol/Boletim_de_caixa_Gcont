import fpdf
pdf = fpdf.FPDF(format='letter')
pdf.add_page()
pdf.set_font("Arial",size=12)
texto = ["texto1","texto2"]
for x in texto:
    pdf.write(5,x)
pdf.output("PDF_teste.pdf")