from flask import Flask, render_template, url_for, request, session, redirect
from registration import Registartor
from db import DateBase
from autotentification import Autotentificator

aut = Autotentificator()
base = DateBase()
rg = Registartor()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'MK-PIG'
base.create_users_table()


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():

    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))

    if request.method == 'POST':
        try:
            if aut.find_user(request.form['email'], request.form['password']):
                session['userLogged'] = request.form['email']
                username = request.form['email'].split('@')[0]
                email = request.form['email']
                return redirect(url_for('profile', username=username, email=email))
            else:
                return render_template('sign_in.html', e="Неверный email или пароль")
        except ValueError as e:
            return render_template('sign_in.html', e=e)

    return render_template('sign_in.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        try:
            if rg.check_correction_email(request.form['email']) and rg.find_user(request.form['email'], request.form['password']) == False:
                if rg.reg(request.form['email'], request.form['password']):
                    usename = request.form['email'].split('@')[0]
                    email = request.form['email']
                    return redirect(url_for(f'profile/{usename}', username=usename, email=email))
        except ValueError as erorr:
            # добавить вывод ошибки в форму регистрации
            return render_template('registration.html', erorr=erorr)

    return render_template('registration.html')


@app.route('/')
def main():
    print('main')
    return render_template('main.html')


@app.route('/profile/<username>')
def profile(username):
    return render_template('user_account.html', username=username)


@app.route('/logout')
def logout():
    print('logout')
    session.pop('userLogged', None)
    return render_template('main.html')


if __name__ == '__main__':
    app.run(debug=True)
