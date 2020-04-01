import os
from decimal import Decimal
from collections import namedtuple

from flask import Flask
from flask import (render_template, request, redirect, flash)
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

tsv_fields = ('time symbol side price shares clr_type clr_broker '
              'acc type token note')
TSVField = namedtuple('TSVField', tsv_fields)
csv_fields = ('acc date curr type side symbol shares price time comm sec_fee '
              'taf_fee ecn_fee routing_fee nscc_fee clr_type clr_broker note')
CSVField = namedtuple('CSVField', csv_fields)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    total_commissions = Decimal('0')
    colmexcomm = True if request.form.get('colmexcomm') else False
    if 'csvfile' not in request.files:
        flash('No file part')
        return redirect(request.url)

    f = request.files['csvfile']
    if f.filename == '':
        flash('No selected file')
        return redirect(request.url)

    for line in f:
        line = map(lambda l: l.replace('"', ''),
                   line.decode('utf8').replace('\n', '').split('\t'))
        tsv_fields = TSVField(*line)._asdict()
        del tsv_fields['token']
        fields = CSVField(
            curr="USD",
            date='0/0/0',
            comm="0",
            sec_fee="0",
            taf_fee="0",
            ecn_fee="0",
            routing_fee="0",
            nscc_fee="0",
            **tsv_fields)

        commission = Decimal(fields.shares) * (Decimal('0.006') if colmexcomm is False else Decimal('0.01'))
        if commission < Decimal('1.5'):
            commission = Decimal('1.5')

        total_commissions += Decimal(fields.shares) * Decimal('0.0015')
        total_commissions += commission

    return "Your fucking commissions are: $%.3f" % total_commissions


if __name__ == '__main__':
    app.configure()
    app.run()
