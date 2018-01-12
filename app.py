#
#  adapted from https://github.com/realpython/flask-boilerplate
# 
#  tfarrell@broadinstitute.org
#  20180108
# 

#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import os
import rpy2
import logging
exec(open('coil_web_utils.py').read())
from logging import Formatter, FileHandler
# from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, send_file

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
#db = SQLAlchemy(app)

# Automatically tear down SQLAlchemy.
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def home():
    return render_template('pages/home.html')

@app.route('/about')
def about():
    return render_template('pages/about.html')

@app.route('/run')
def run(): 
    return render_template('pages/run.html')

@app.route('/guide')
def guide(): 
    return render_template('pages/guide.html')

@app.route('/result', methods=("POST","GET"))
def result(): 
    # get barcodes
    barcode_file_lines = [l for l in str(request.files['barcodes'].getvalue()).split('\n') if l != '']
    # setup output filename
    output_file = (lambda s: s[:s.rfind('.')] if s.rfind('.') != -1 else s)(request.form['result_filename']) + '.csv'
    # get mafs based on maf_selected
    maf_file_lines = None      # if estimating from data
    if request.form['maf_radio'] == 'file':
        maf_file_lines = [l for l in str(request.files['mafs'].getvalue()).split('\n') if l != '']	
        #if debugging: print_for_debugging([str(maf_file_lines)])
    elif request.form['maf_radio'] == 'pf3k':
	# get maf_file_lines based on selection
	select_file_contents = str(request.files['maf_pos_select'].getvalue())    
	maf_file_lines = get_filtered_maf_file_lines(request.form['maf_geo_select'], select_file_contents)	
    else:
        #if debugging: print_for_debugging([str(barcode_file_lines)])
        pass
    # compute predictions based on whether MCCOIL enabled
    predictions = []
    try: 
        if 'mccoil_checkbox' in request.form.keys() and request.form['mccoil_checkbox'] == 'on': 
            predictions = mccoil.run_mccoil(barcode_file_lines, maf_file_lines)
        else:
            predictions = COIL.exec_from_raw_input(barcode_file_lines, maf_file_lines)
        result_file = 'static/downloads/' + output_file 
        f = open(result_file, 'wb')
        f.write(format_cois_mafs_file(predictions))
        f.flush()
        f.close()
        return send_file(result_file, as_attachment=True, attachment_filename=output_file)
    except:
        return render_template('errors/500.html'), 500


# Error handlers.

@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
