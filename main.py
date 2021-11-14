#!/usr/bin/env python3
import os
import shlex
import string
import random
from subprocess import Popen
from time import sleep
from flask import Flask, render_template
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import StringField, MultipleFileField, SubmitField, FileField, PasswordField
from wtforms.validators import DataRequired

app = Flask(__name__, template_folder='.')
app.config['SECRET_KEY'] = '*********'
script_path = os.getcwd()


def rand_char(size=15, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


log_dir = f"{script_path}/logs_{rand_char()}"
os.mkdir(log_dir)
log_file = f"{log_dir}/log_{rand_char()}"
template_dir = f"{script_path}/template_{rand_char()}"
os.mkdir(template_dir)
inventory_dir = f"{script_path}/inventory_{rand_char()}"
os.mkdir(inventory_dir)


class DeployForm(FlaskForm):
    img_version = StringField('Docker Image Version', default="latest")
    inventory_file = FileField('Inventory File', validators=[DataRequired()])
    template_files = MultipleFileField('Template Files', validators=[DataRequired()])
    vault_password = PasswordField('Ansible Vault Password')
    submit = SubmitField('Deploy')


@app.route('/')
@app.route('/index')
def index():
    deploy_form = DeployForm()
    return render_template('index.html', form=deploy_form)


@app.route("/stream")
def stream():
    def generate():
        with open(f"{log_file}", 'r') as f:
            while True:
                yield f.read()
                sleep(1)

    return app.response_class(generate(), mimetype='text/plain')


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    form = DeployForm()
    if form.validate_on_submit():
        for file in form.template_files.data:
            file_name = secure_filename(file.filename)
            file.save(f"{template_dir}/{file_name}")
        file = form.inventory_file.data
        inventory_file_name = secure_filename(file.filename)
        file.save(f"{inventory_dir}/inventory_file_name")
    out = open(f"{log_file}", "w")
    command = f"{script_path}/deploy_cluster.sh -vault-password {form.vault_password.data} -template-dir {template_dir} -inventory-file {inventory_dir}/{inventory_file_name}"
    Popen(shlex.split(command), stdout=out, stderr=out)
    return render_template('streamer.html')


if __name__ == '__main__':
    app.run(debug=True)
