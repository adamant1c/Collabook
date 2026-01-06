from xhtml2pdf import pisa
import io

def test_pdf_generation():
    html_content = """
    <html>
    <head>
        <style>
            body { font-family: sans-serif; }
            .chapter { margin-bottom: 20px; border-bottom: 1px solid #ccc; }
        </style>
    </head>
    <body>
        <h1>Test Story</h1>
        <div class="chapter">
            <h2>Chapter 1</h2>
            <p>Action: I hit the goblin.</p>
            <p>Result: The goblin dodges.</p>
        </div>
    </body>
    </html>
    """
    
    output = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=output)
    
    if pisa_status.err:
        print("Error generating PDF")
        exit(1)
        
    print("PDF generated successfully! Size:", len(output.getvalue()))

if __name__ == "__main__":
    test_pdf_generation()
