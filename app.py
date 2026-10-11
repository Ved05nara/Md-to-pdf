import io
import markdown
from flask import Flask, render_template, request, jsonify, send_file
# pyrefly: ignore [missing-import]
from xhtml2pdf import pisa

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/convert', methods=['POST'])
def convert():
    # Supports JSON payload or multipart form data
    md_content = None
    if request.is_json:
        data = request.get_json()
        md_content = data.get('markdown') if data else None
    elif 'markdown' in request.form:
        md_content = request.form.get('markdown')

    # Input validation requirement
    if not md_content or not md_content.strip():
        return jsonify({"error": "Empty or missing markdown content"}), 400

    try:
        # Convert Markdown to HTML
        html_body = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Helvetica, Arial, sans-serif; font-size: 12pt; line-height: 1.5; padding: 20px; }}
                h1, h2, h3 {{ color: #2c3e50; }}
                code {{ font-family: Courier, monospace; background-color: #f4f4f4; padding: 2px 4px; }}
                pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 4px; }}
            </style>
        </head>
        <body>
            {html_body}
        </body>
        </html>
        """

        # Generate PDF into memory stream
        pdf_stream = io.BytesIO()
        pisa_status = pisa.CreatePDF(full_html, dest=pdf_stream)

        if pisa_status.err:
            return jsonify({"error": "Failed to generate PDF"}), 500

        pdf_stream.seek(0)
        return send_file(
            pdf_stream,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='converted_document.pdf'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)