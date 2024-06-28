import PyPDF2
import pdfplumber
import fitz  # PyMuPDF

def extract_data_from_pdf(pdf_path):
    # Extract text using PyPDF2
    def extract_text(pdf_path):
        text = ""
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() or ""
        return text

    # Extract tables using pdfplumber
    def extract_tables(pdf_path):
        tables = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables.extend(page.extract_tables())
        return tables

    # Extract links using PyMuPDF
    def extract_links(pdf_path):
        doc = fitz.open(pdf_path)
        links = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            for link in page.get_links():
                uri = link.get("uri")
                if uri:
                    links.append(uri)
        return links

    text = extract_text(pdf_path)
    tables = extract_tables(pdf_path)
    links = extract_links(pdf_path)

    return text, tables, links

# Example usage:
pdf_path = 'Media_reliance.pdf'
text, tables, links = extract_data_from_pdf(pdf_path)

print("Textual Data:")
print(text)

print("\nTables:")
for table in tables:
    for row in table:
        print(row)

print("\nLinks:")
for link in links:
    print(link)
