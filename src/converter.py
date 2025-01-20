from PyPDF2 import PdfWriter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd
from datetime import datetime

def convert_to_pdf(data):
    # Get the current date
    current_date = datetime.now()
    date = current_date.strftime("%d-%m-%Y")
    
    # Create a BytesIO buffer to store the PDF
    buffer = BytesIO()
    
    # Split the string into lines
    lines = data.strip().split("\n")

    # Process each line into a list of dictionaries
    rows = []
    for line in lines:
        index, name = line.split(".", 1)  # Split by the first occurrence of '.'
        rows.append([int(index), name.strip()])

    # Create a DataFrame
    df = pd.DataFrame(rows, columns=["Nomor", "Nama"])

    # Add additional columns with empty values
    df['Game 1'] = None
    df['Game 2'] = None
    df['Game 3'] = None
    df['Game 4'] = None
    df['Total Bayar'] = None
    df['Keterangan'] = None

    # Convert DataFrame to a list of lists for the table
    table_data = [df.columns.tolist()] + df.values.tolist()

    # Create PDF using ReportLab
    pdf = SimpleDocTemplate(buffer, pagesize=letter, topMargin=30, bottomMargin=36, leftMargin=50, rightMargin=50)

    # Create a title
    styles = getSampleStyleSheet()
    styles['Title'].fontSize = 12
    styles['Title'].fontName = 'Helvetica'
    title = Paragraph(f"Daftar Pemain Mabar RBG {date}", styles['Title'])

    # Create table
    table = Table(table_data, colWidths=[70] * len(df.columns), rowHeights=25)
    
    # Add style to the table
    style = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, "black"),
    ])
    table.setStyle(style)

    # Build PDF
    pdf.build([title, Spacer(1, 12), table])
    buffer.seek(0)
    return buffer