from flask import Flask, jsonify, render_template, url_for, request, session, redirect, abort
from werkzeug.utils import secure_filename
from registration import Registartor
from db import DateBase
from autotentification import Autotentificator
from validation import Validator
import os

valid = Validator()
aut = Autotentificator()
base = DateBase()
rg = Registartor()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'MK-PIG'
app.config['UPLOAD_FOLDER'] = 'uploads'
base.create_users_table()
base.create_table_users_items()
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    """Позволяет пользователю войти в личный кабинет
        Если операция успешна, то пользователь перенаправляется на страницу profile, в случае неудачи - остается на странице авторизации 
    Returns:
        _type_: либо шаблон страницы авторизации либо передаресация в лк
    """
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
    """позволяет зарегистрировать пользователя на сайте


    Returns:
        _type_: шаблон страницы регистрации в случае неудачи либо переадресация в личный кабинет пользователя
    """
    if request.method == 'POST':
        try:
            if valid.check_correction_email(request.form['email']) and rg.find_user(request.form['email'], request.form['password']) == False:
                if rg.reg(request.form['email'], request.form['password']):
                    session['userLogged'] = request.form['email']
                    email = request.form['email']
                    return redirect(url_for('profile', email=email))
        except ValueError as erorr:
            return render_template('registration.html', erorr=erorr)

    return render_template('registration.html')


@app.route('/')
def main():
    """отрисовывает главную страницу

    Returns:
        _type_: возвращает шаблон главной страницы
    """
    return render_template('main.html')


@app.route('/profile/<email>')
def profile(email):
    """отрисовывает личный кабинет пользователя

    Args:
        email (_type_): электроная почта (логин) пользователя
        если пользователь через адресную строку пытается попать в чужой лк, то abort-им ошибку доступа 401
    Returns:
        _type_: _description_
    """
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
    """служит для обновления/ добаления данных пользователя в личном кабинете

    Returns:
        _type_: ничего
    """
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
    """позволяет выйти из личного кабинета пользователю. Юзер удаляется из текущей сессии

    Returns:
        _type_: отрисовывает шаблон главной страницы
    """
    session.pop('userLogged', None)
    session.pop('phone_number', None)
    return render_template('main.html')


@app.route('/upload_clothes_form/<email>')
def upload_clothes_form(email):
    """отрисовывает страницу для добавления вещей на обмен

    Args:
        email (_type_): эл почта пользователя

    Returns:
        _type_: шаблон формы для зааполнения
    """
    return render_template('upload_form.html', email=email)


@app.route('/add_clothes', methods=['GET', 'POST'])
def add_clothes():
    """обрабатывает данные из формы и записывает их в БД

    Returns:
        _type_: переадресовывает пользователя в лк
    """
    if request.method == "POST":
        file = request.files['clothes_photo']
        if file:
            filename = secure_filename(file.filename)  # type: ignore
            path_to_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        user_id = base.select('user_id', 'users',
                              f'email="{session['userLogged']}"')[0][0]
        keys = 'user_id, clothes_link_to_photo, '
        values = f'"{user_id}", "{path_to_file}", '
        for key, value in request.form.items():
            keys += f'{key}, '
            values += f'"{value}", '

        # удаляем пробел и запятую в конце
        keys = keys[:-2]
        values = values[:-2]
        if base.insert('users_items', keys, values):
            file.save(path_to_file)

    return redirect(url_for('profile', email=session['userLogged']))


if __name__ == '__main__':
    app.run(debug=True)
