import sys
import traceback
from flask import Blueprint, render_template
import pdfkit


play = Blueprint('play', __name__)


@play.route('/play/math')
def play_math():
    print("-- In play_math")
    return render_template('play/play.html')

@play.route('/play/math/pdf')

def play_math_pdf():
    try:
        print("about to set path")
        path_wkthmltopdf = r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe'
        print("about to set config")
        configpdf = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
        print("about to pdfkit")
        result = render_template('play/play.html')
        pdfkit.from_string(result, 'out.pdf', configuration=configpdf)

        return "pdf should have been created"
    except Exception as e:
        print('PDF worksheet: ***Error:', e)
        traceback.print_exc(file=sys.stdout)
        tb = traceback.format_exc()
        return "<h2>Error generating pdf" + \
               '<plaintext>' + tb + '</plaintext>'
