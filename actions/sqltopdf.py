import pymysql
from reportlab.pdfgen import canvas
# from langchain.chains import ConversationalRetrievalChain
# from langchain.chat_models import ChatOllama
import os

def save_transaction_to_pdf(cursor, amount, recipient):
    # Retrieve the data from the 'Transactions' table
    cursor.execute("SELECT * FROM Transactions")
    rows = cursor.fetchall()

    # Create the report
    pdf = canvas.Canvas("bank_transaction_report.pdf")
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, 800, "Bank Transaction Report")
    pdf.setFont("Helvetica", 12)
    y = 750

    for row in rows:
        pdf.drawString(50, y, "Transaction Number: " + str(row[0]))
        pdf.drawString(50, y - 20, "Date: " + str(row[1]))
        pdf.drawString(50, y - 40, "Amount Change: " + str(row[2]))
        pdf.drawString(50, y - 60, "Balance After: " + str(row[3]))
        pdf.drawString(50, y - 80, "Receiver: " + row[4])
        pdf.drawString(50, y - 100, "Information: " + row[5])
        y -= 120
        if y < 50:  # Check if the y-coordinate is too low for the next row
            pdf.showPage()  # Create a new page
            pdf.setFont("Helvetica", 12)
            y = 800

    pdf.save()