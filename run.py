from flask import Flask, render_template, url_for, request, g, session, redirect
from registration import Registartor
from db import DateBase

base = DateBase()
rg = Registartor()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'MK-PIG'
base.create_users_table()


@app.route('/sign_in')
def sign_in():
    return render_template('sign_in.html')


@app.route('/testor_form', methods=['POST', 'GET'])
def testor_form():
    return render_template('testor_form.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        try:
            if rg.check_correction_email(request.form['email']) and rg.find_user(request.form['email'], request.form['password']) == False:
                if rg.reg(request.form['email'], request.form['password']):
                    return redirect(url_for('testor_form'))
        except ValueError as erorr:
            # добавить вывод ошибки в форму регистрации
            return render_template('registration.html', erorr=erorr)

    return render_template('registration.html')


@app.route('/')
def main():
    return render_template('main.html')


if __name__ == '__main__':
    app.run(debug=True)
