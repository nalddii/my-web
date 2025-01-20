from flask import Flask, render_template, request, send_file, jsonify
from io import BytesIO
from PyPDF2 import PdfWriter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import pandas as pd
from datetime import datetime

app = Flask(__name__)

def calculate_row_height(num_rows):
    """Calculate appropriate row height based on number of rows"""
    # A4 page height is about 842 points
    # Subtract margins and title space
    available_space = 842 - (72 * 2)  # 72 points = 1 inch margins
    min_row_height = 12  # Minimum row height in points
    max_row_height = 25  # Maximum row height in points
    
    # Calculate ideal row height
    ideal_height = available_space / (num_rows + 2)  # +2 for header and some padding
    
    # Clamp between min and max heights
    return max(min_row_height, min(ideal_height, max_row_height))

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
        if '.' in line:  # Only process lines that contain a dot
            parts = line.split(".", 1)
            if len(parts) == 2:  # Ensure we have both number and name
                index = parts[0].strip()
                name = parts[1].strip()
                rows.append([index, name])

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

    # Calculate dynamic row height based on number of rows
    row_height = calculate_row_height(len(rows))

    # Create PDF using ReportLab with A4 size
    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=20,
        bottomMargin=20,
        leftMargin=30,
        rightMargin=30
    )

    # Create a title with smaller font size
    styles = getSampleStyleSheet()
    title_style = styles['Title'].clone('CustomTitle')
    title_style.fontSize = 14
    title_style.fontName = 'Helvetica'
    title_style.spaceAfter = 10
    title = Paragraph(f"Daftar Pemain Mabar RBG {date}", title_style)

    # Calculate column widths based on content
    total_width = A4[0] - 60  # Subtract margins
    col_widths = [
        total_width * 0.08,  # Nomor (8%)
        total_width * 0.22,  # Nama (22%)
        total_width * 0.10,  # Game 1 (10%)
        total_width * 0.10,  # Game 2 (10%)
        total_width * 0.10,  # Game 3 (10%)
        total_width * 0.10,  # Game 4 (10%)
        total_width * 0.15,  # Total Bayar (15%)
        total_width * 0.15   # Keterangan (15%)
    ]

    # Create table with calculated dimensions
    table = Table(table_data, colWidths=col_widths, rowHeights=[row_height] * (len(table_data)))
    
    # Add style to the table
    style = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # Smaller font size
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, "black"),  # Thinner grid lines
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold header
        ('BACKGROUND', (0, 0), (-1, 0), '#f0f0f0'),  # Light gray header
    ])
    table.setStyle(style)

    # Build PDF
    pdf.build([title, table])
    buffer.seek(0)
    return buffer

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    text = request.form['text']
    try:
        pdf_buffer = convert_to_pdf(text)
        return jsonify({
            'status': 'success',
            'message': 'PDF generated successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/download', methods=['POST'])
def download():
    text = request.form['text']
    try:
        pdf_buffer = convert_to_pdf(text)
        current_date = datetime.now().strftime("%d-%m-%Y")
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Daftar Pemain Mabar {current_date}.pdf'
        )
    except Exception as e:
        return str(e), 400

if __name__ == '__main__':
    app.run(debug=False)
