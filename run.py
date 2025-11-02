from flask import Flask, jsonify, render_template, url_for, request, session, redirect, abort
from registration import Registartor
from db import DateBase
from autotentification import Autotentificator
from validation import Validator

valid = Validator()
aut = Autotentificator()
base = DateBase()
rg = Registartor()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'MK-PIG'
base.create_users_table()


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():

    if 'userLogged' in session:
        return redirect(url_for('profile', email=session['userLogged']))

    if request.method == 'POST':
        try:
            if aut.find_user(request.form['email'], request.form['password']):
                session['userLogged'] = request.form['email']
                email = request.form['email']
                return redirect(url_for('profile', email=email))
            else:
                return render_template('sign_in.html', e="Неверный email или пароль")
        except ValueError as e:
            return render_template('sign_in.html', e=e)

    return render_template('sign_in.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        try:
            if valid.check_correction_email(request.form['email']) and rg.find_user(request.form['email'], request.form['password']) == False:
                if rg.reg(request.form['email'], request.form['password']):
                    session['userLogged'] = request.form['email']
                    email = request.form['email']
                    return redirect(url_for(f'profile', email=email))
        except ValueError as erorr:
            return render_template('registration.html', erorr=erorr)

    return render_template('registration.html')


@app.route('/')
def main():
    print('main')
    return render_template('main.html')


@app.route('/profile/<email>')
def profile(email):
    # если пользователь не в сессии - то не даем юзеру доступ к изменению url
    if 'userLogged' not in session or session['userLogged'] != email:
        abort(401)
    if 'phone_number' in session:
        phone_number = session['phone_number']
    else:
        result_select = base.select(
            'phone_number', 'users', f'email="{email}"')
        phone_number = result_select[0][0] if result_select else ''

    username = email.split('@')[0]
    return render_template('user_account.html', email=email, username=username, phone_number=phone_number)


@app.route('/profile/update', methods=['POST'])
def update_profile():
    try:
        old_email = session.get('userLogged')
        new_email = request.form.get('email')
        phone_number = request.form.get('phone')

        # Валидация данных
        if not new_email or not phone_number:
            return jsonify({'success': False, 'error': 'Все поля обязательны'})

        if not valid.check_correction_email(new_email):
            return jsonify({'success': False, 'error': 'Некорректный адрес эл. почты'})

        if not valid.check_phone_number_correction(phone_number):
            return jsonify({'success': False, 'error': 'Некорректный номер телефона'})

        # Здесь сохраняем в базу данных
        result_of_operation = base.update_table('users', ['email', 'phone_number'], [
            f'"{new_email}"', f'"{phone_number}"'], f'email="{old_email}"')

        # Здесь сохраняем данные о пользователе в сесиию
        if result_of_operation:
            session['userLogged'] = new_email
            session['phone_number'] = phone_number

        return jsonify({
            'success': True,
            'message': 'Профиль обновлен',
            'email': new_email,
            'phone': phone_number
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/logout')
def logout():
    print('logout')
    session.pop('userLogged', None)
    session.pop('phone_number', None)
    return render_template('main.html')


if __name__ == '__main__':
    app.run(debug=True)
