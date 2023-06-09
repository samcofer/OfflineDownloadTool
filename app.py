from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import os
import CUSTOMFUNCTION as ext_func

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


# with Flask-WTF, each web form is represented by a class
# "NameForm" can change; "(FlaskForm)" cannot
# see the route for "/" and "index.html" to see how this is used
class NameForm(FlaskForm):
    r_versions = StringField("R versions, comma separated [4.3.0,3.6.3]: ")
    python_versions = StringField("Python versions, comma separated [3.11.4,3.10.12]: ")
    quarto_versions = StringField("Quarto versions, comma separated [1.3.361,1.2.475]: ")
    os = SelectField(u'Operating System', choices=[('U18', 'Ubuntu18'), ('U18', 'Ubuntu18'), ('U18', 'Ubuntu18'), ('RH7', 'RedHat 7'), ('RH8', 'RedHat 8'), ('RH9', 'RedHat 9')])
    submit = SubmitField('Submit', render_kw={"onclick": "loading();"})


# all Flask routes below

@app.route('/', methods=['GET', 'POST'])
def index():
    # you must tell the variable 'form' what you named the class, above
    # 'form' is the variable name used in this template: index.html
    form = NameForm()
    message = ''
    if form.is_submitted():
        message = ext_func.URLRetrieval(form.r_versions.data or '4.3.0,3.6.3',
                                         form.python_versions.data or '3.11.4,3.10.12',
                                         form.quarto_versions.data or '1.3.361,1.2.475',
                                         form.os.data or 'RH9')
        return render_template('index.html', form=form, message=message)
    return render_template('index.html', form=form, message=message)


# 2 routes to handle errors - they have templates too
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# keep this as is
if __name__ == '__main__':
    app.run(debug=True)
