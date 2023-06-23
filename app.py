from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import widgets
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField
import os
import CUSTOMFUNCTION as ext_func
import ctypes


app = Flask(__name__)


# When running in Posit Workbench, apply ProxyFix middleware
# See: https://flask.palletsprojects.com/en/2.2.x/deploying/proxy_fix/ 
if 'RS_SERVER_URL' in os.environ and os.environ['RS_SERVER_URL']:
	from werkzeug.middleware.proxy_fix import ProxyFix
	app.wsgi_app = ProxyFix(app.wsgi_app, x_prefix=1)

# Flask-WTF requires an encryption key - the string can be anything
app.config['SECRET_KEY'] = 'C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb'


# Flask-Bootstrap requires this line
Bootstrap(app)

# This code from WTForms docs, this class changes the way SelectMultipleField
# is rendered by jinja
# https://wtforms.readthedocs.io/en/3.0.x/specific_problems/
class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

def create_language_form(osstr):
  
    class LanguagesForm(FlaskForm):

        global rchoices
        rchoices = []
        global pythonchoices
        pythonchoices = []
        global quartochoices
        quartochoices = []
        if osstr and not rchoices:
            lib = ctypes.cdll.LoadLibrary('./wbi.so')
            lib.rversions.restype = ctypes.c_char_p
            r_versions = lib.rversions()
            decode_string = r_versions.decode('utf-8')
            r_versions_list = decode_string.split()
            rchoices = [(option, option) for option in r_versions_list]
            
            r_versions = MultiCheckboxField("R versions: ", choices=rchoices)

            lib.pythonversions.restype = ctypes.c_char_p
            lib.pythonversions.argtypes = [ctypes.c_char_p]
            python_versions = lib.pythonversions(osstr.encode('utf-8'))
            decode_string = python_versions.decode('utf-8')
            python_versions_list = decode_string.split()
            pythonchoices = [(option, option) for option in python_versions_list]

            python_versions = MultiCheckboxField("Python versions: ", choices=pythonchoices)
            
            lib.quartoversions.restype = ctypes.c_char_p
            quarto_versions = lib.quartoversions()
            decode_string = quarto_versions.decode('utf-8')
            quarto_versions_list = decode_string.split()
            quartochoices = [(option, option) for option in quarto_versions_list]
            
            quarto_versions = MultiCheckboxField("Quarto versions: ", choices=quartochoices)

        os = SelectField(u'Operating System', choices=[('U20', 'Ubuntu20'), ('U22', 'Ubuntu22'), ('RH7', 'RedHat 7'), ('RH8', 'RedHat 8'), ('RH9', 'RedHat 9')])
        submit = SubmitField('Submit', render_kw={"onclick": "loading();"})
    return LanguagesForm()

# all Flask routes below

@app.route('/', methods=['GET', 'POST'])
def index():
    # you must tell the variable 'form' what you named the class, above
    # 'form' is the variable name used in this template: index.html
    message = ''

    form = create_language_form('')
    if form.validate_on_submit():
        return redirect("https://colorado.posit.co" + url_for('index')+ f'download/{form.os.data}')
    return render_template('index.html', form=form)

@app.route('/download/<osstr>', methods=['GET', 'POST'])
def download(osstr):
    # you must tell the variable 'form' what you named the class, above
    # 'form' is the variable name used in this template: index.html
    #print(osstr + " from download")
    form = create_language_form(osstr)
    if form.is_submitted():
        r_version_concat = ','.join(form.r_versions.data)
        python_version_concat = ','.join(form.python_versions.data)
        quarto_version_concat = ','.join(form.quarto_versions.data)
        r_urls, python_urls, quarto_urls, workbench_urls, driver_urls = ext_func.URLRetrievalLib(form.r_versions.data or ['4.3.1'],
                                        form.python_versions.data or ['3.11.4'],
                                        form.quarto_versions.data or ['1.3.361'],
                                        osstr)
        connect_urls, pm_urls = ext_func.ConnectPackage(osstr)
        return render_template('download.html', form=form, r_urls=r_urls, python_urls=python_urls, quarto_urls=quarto_urls, 
            workbench_urls=workbench_urls, driver_urls=driver_urls, connect_urls = connect_urls, pm_urls=pm_urls, osstr=osstr)
    return render_template('download.html', form=form, osstr=osstr)



# 2 routes to handle errors - they have templates too
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/get_selected_items', methods=['GET'])
def get_selected_items():
    r_versions = request.args.getlist('r_versions[]')
    print(r_versions)
    # Do something with the selected items (e.g., process or store them)

    return ''  # Return an empty response

# keep this as is
if __name__ == '__main__':
    app.run(debug=True)
