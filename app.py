from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

import CUSTOMFUNCTION as ext_func

app = Flask(__name__)

# Flask-WTF requires an encryption key - the string can be anything
app.config['SECRET_KEY'] = 'C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb'

# Flask-Bootstrap requires this line
Bootstrap(app)


# with Flask-WTF, each web form is represented by a class
# "NameForm" can change; "(FlaskForm)" cannot
# see the route for "/" and "index.html" to see how this is used
class NameForm(FlaskForm):
    version = StringField("Enter just the version number in the form X.X.X [1.71.2]: ")
    namespace = StringField("Please enter the NAMESPACE of your selected extension [ms-python]: ")
    name = StringField("Please enter the NAME of your selected extension [python]: ")
    submit = SubmitField('Submit', render_kw={"onclick": "loading();"})


# all Flask routes below

@app.route('/', methods=['GET', 'POST'])
def index():
    # you must tell the variable 'form' what you named the class, above
    # 'form' is the variable name used in this template: index.html
    form = NameForm()
    message = ''
    if form.is_submitted():
        message = ext_func.vscode_lookup(form.version.data or '1.71.2',
                                         form.namespace.data or 'ms-python',
                                         form.name.data or 'python')
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
