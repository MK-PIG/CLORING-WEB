from flask import Flask, jsonify, render_template, url_for, request, session, redirect, abort
from werkzeug.utils import secure_filename
from src.registration import Registartor
from src.db import DateBase
from src.autotentification import Autotentificator
from src.validation import Validator
import os
import secrets
from src.logger import (info_logger, er_logger)
"""1 создать папку src для pyhton файлов +
 2 создать volume для логов +
 3 создание качесвтенного ридми +
 4 обработка ошибок +
 5 логирование функций +
 6 dockstrings +
 7 сфера знания +
 8 запись файлов в бд 
"""
valid = Validator()
aut = Autotentificator()
base = DateBase()
rg = Registartor()
app = Flask(__name__)
DATABASE_PATH = os.environ.get('DATABASE_PATH', '/app/data/database.db')
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/app/static/uploads')

app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY', secrets.token_hex(16))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DATABASE_PATH'] = DATABASE_PATH

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
        info_logger.info("User is already logged. Redirected to profile page")
        return redirect(url_for('profile', email=session['userLogged']))

    if request.method == 'POST':
        try:
            if aut.find_user(request.form['email'], request.form['password']):
                session['userLogged'] = request.form['email']
                email = request.form['email']
                info_logger.info(
                    f"User sign in and redirected to profile. Email: {email}")
                return redirect(url_for('profile', email=email))
            else:
                er_logger.error(
                    f"Wrong email: {request.form['email']} or passwords")
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
    if 'userLogged' in session:
        return redirect(url_for('profile', email=session['userLogged']))
    if request.method == 'POST':
        try:
            if valid.check_correction_email(request.form['email']) and rg.find_user(request.form['email'], request.form['password']) == False:
                if rg.reg(request.form['email'], request.form['password']):
                    session['userLogged'] = request.form['email']
                    email = request.form['email']
                    info_logger.info(
                        f"User has been registrated. user redirected to profile. Email: {email}")
                    return redirect(url_for('profile', email=email))
        except ValueError as erorr:
            er_logger.error(
                f"Wrong input data for registration. Email: {request.form['email']}")
            return render_template('registration.html', erorr=erorr)

    return render_template('registration.html')


@app.route('/')
def main():
    """отрисовывает главную страницу

    Returns:
        _type_: возвращает шаблон главной страницы
    """
    info_logger.info("Render main page")
    return render_template('main.html')


@app.route('/profile/<email>')
def profile(email):
    """отрисовывает личный кабинет пользователя

    Args:
        email (_type_): электроная почта (логин) пользователя
        если пользователь через адресную строку пытается попать в чужой лк, то abort-им ошибку доступа 401
    Returns:
        _type_: шаблон страницы 
    """
    try:
        # если пользователь не в сессии - то не даем юзеру доступ к изменению url
        if 'userLogged' not in session or session['userLogged'] != email:
            er_logger.error(f"Error 401. Email: {email}")
            abort(401)
        if 'phone_number' in session:
            phone_number = session['phone_number']
        else:
            result_select_phone_number = base.select(
                'phone_number', 'users', f'email="{email}"')
            phone_number = result_select_phone_number[0][0] if result_select_phone_number else ''

        result_select_user_id = base.select(
            'user_id', 'users', f'email="{email}"')
        user_id = result_select_user_id[0][0] if result_select_user_id else ''
        LIST_ITEMS_KEYS = ['clothes_name', 'clothes_category', ' clothes_size',
                           'clothes_condition', 'clothes_brand', 'clothes_material', 'clothes_color', 'clothes_description', 'clothes_link_to_photo']
        result_select_items = base.select(
            ', '.join(LIST_ITEMS_KEYS), 'users_items', f'user_id="{user_id}"')

        list_of_items = [dict(zip(LIST_ITEMS_KEYS, clothes_values_tuple))
                         for clothes_values_tuple in result_select_items]

        username = email.split('@')[0]
        info_logger.info(
            f"User has been redirected to personal account. Email: {email}, username: {username}, phone number: {phone_number}")
        return render_template('user_account.html', email=email, username=username, phone_number=phone_number, list_of_items=list_of_items, len_list_of_items=len(list_of_items))
    except Exception as e:
        er_logger.error(f"ERROR: from profile {e}")
        return redirect(url_for('main'))


@app.route('/profile/update', methods=['POST'])
def update_profile():
    """служит для обновления/ добаления данных пользователя в личном кабинете

    Returns:
        _type_:   ничего
    """
    try:
        old_email = session.get('userLogged')
        new_email = request.form.get('email')
        phone_number = request.form.get('phone')

        # Валидация данных
        if not new_email or not phone_number:
            er_logger.error(f"All fields are required to update profile")
            return jsonify({'success': False, 'error': 'Все поля обязательны'})

        if not valid.check_correction_email(new_email):
            er_logger.error(f"Incorrect email for update profile: {new_email}")
            return jsonify({'success': False, 'error': 'Некорректный адрес эл. почты'})

        if not valid.check_phone_number_correction(phone_number):
            er_logger.error(
                f"Incorrect phone number for update profile: {phone_number}")
            return jsonify({'success': False, 'error': 'Некорректный номер телефона'})

        # Здесь сохраняем в базу данных
        result_of_operation = base.update_table('users', ['email', 'phone_number'], [
            f'"{new_email}"', f'"{phone_number}"'], f'email="{old_email}"')

        # Здесь сохраняем данные о пользователе в сесиию
        if result_of_operation:
            session['userLogged'] = new_email
            session['phone_number'] = phone_number

        info_logger.info(f"Profile has been updated. Email: {new_email}")
        return jsonify({
            'success': True,
            'message': 'Профиль обновлен',
            'email': new_email,
            'phone': phone_number
        })

    except Exception as e:
        er_logger.error("Some error with profile update")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/logout')
def logout():
    """позволяет выйти из личного кабинета пользователю. Юзер удаляется из текущей сессии

    Returns:
        _type_: отрисовывает шаблон главной страницы
    """
    if session['userLogged']:
        session.pop('userLogged', None)
    if session['phone_number']:
        session.pop('phone_number', None)
    info_logger.info(
        "User has been log out. Deleted from active session. Redirected to main page")
    return render_template('main.html')


@app.route('/upload_clothes_form/<email>')
def upload_clothes_form(email):
    """отрисовывает страницу для добавления вещей на обмен

    Args:
        email (_type_): эл почта пользователя

    Returns:
        _type_: шаблон формы для заполнения
    """
    info_logger.info(f"Clothing page has been rendered. Email: {email}")
    return render_template('upload_form.html', email=email)


@app.route('/add_clothes', methods=['GET', 'POST'])
def add_clothes():
    """обрабатывает данные из формы и записывает их в БД

    Returns:
        _type_: переадресовывает пользователя в лк
    """
    if request.method == "POST":
        try:
            file = request.files['clothes_photo']
            if file:
                filename = secure_filename(file.filename)  # type: ignore
                path_to_file = os.path.join(
                    app.config['UPLOAD_FOLDER'], filename)

            user_id = base.select('user_id', 'users',
                                  f'email="{session['userLogged']}"')[0][0]
            keys = ['user_id', 'clothes_link_to_photo']
            values = [f'"{user_id}"', f'"{filename}"']

            for key in ['clothes_name', 'clothes_category', 'clothes_size',
                        'clothes_condition', 'clothes_brand', 'clothes_material',
                        'clothes_color', 'clothes_description']:
                if key in request.form:
                    keys.append(key)
                    values.append(f'"{request.form[key]}"')

                    # Вставка в БД
            if base.insert('users_items', ', '.join(keys), ', '.join(values)):
                info_logger.info(
                    f"Donation added. Email: {session.get('userLogged')}")
                file.save(path_to_file)
            info_logger.info(
                "Clothing data has been added to DB. User redirected to profile.")
        except Exception as e:
            er_logger.error(f"Error in add_clothes: {str(e)}")
            return jsonify({'success': False, 'message': str(e)}), 500
    return redirect(url_for('profile', email=session['userLogged']))


@app.route('/catalog', methods=['GET', 'POST'])
def catalog():
    """отрисовывает страницу каталога с отображением всех вещей других пользователя, кроме вещей текущего

    Returns:
        _type_: шаблон страницы каталога
    """
    try:
        if not session.get('userLogged', False):
            return redirect(url_for('sign_in'))
        email = session['userLogged']

        result_select_user_id = base.select(
            'user_id', 'users', f'email="{email}"')
        user_id = result_select_user_id[0][0] if result_select_user_id else ''

        LIST_ITEMS_KEYS = ['clothes_name',
                           'clothes_link_to_photo', 'user_id', 'item_id']

        result_select_items = base.select(
            ', '.join(LIST_ITEMS_KEYS), 'users_items', f'user_id!="{user_id}"')

        list_of_items = [dict(zip(LIST_ITEMS_KEYS, clothes_values_tuple))
                         for clothes_values_tuple in result_select_items]
        info_logger.info(f"User {email} visited page catalog")

        return render_template('catalog.html', email=email, list_of_items=list_of_items)
    except Exception as e:
        er_logger.error(f"ERROR: from catalog {e}")
        return redirect(url_for('main'))


@app.route('/card/<user_id>/<item_id>')
def card(user_id: str, item_id: str):
    """отрисовывает карточку товара по item_id

    Args:
        user_id (str): id usera в системе
        item_id (str): id вещи для обмена в системе

    Returns:
        _type_: шаблон страницы карточка товара
    """
    try:

        LIST_ITEMS_KEYS = ['clothes_name', 'clothes_category', ' clothes_size',
                           'clothes_condition', 'clothes_brand', 'clothes_material', 'clothes_color', 'clothes_description', 'clothes_link_to_photo']

        result_select_item = base.select(
            ', '.join(LIST_ITEMS_KEYS), 'users_items', f'item_id="{item_id}"')[0]
        item_dict = dict(zip(LIST_ITEMS_KEYS, result_select_item))
        result_select_email = base.select(
            'email', 'users', f'user_id="{user_id}"')[0][0]
        email = result_select_email

        result_select_phone_number = base.select(
            'phone_number', 'users', f'user_id="{user_id}"')
        phone_number = result_select_phone_number[0][0] if result_select_phone_number else "Нет"
        info_logger.info(f"User {email} visited card page")
        return render_template("card.html", item_dict=item_dict, email=email, phone_number=phone_number)
    except Exception as e:
        er_logger.error(f"ERROR: from card {e}")
        return redirect(url_for('main'))


@app.route('/donation_form')
def show_donation_form():
    """отрисовывает страницу для загрузки товара для пожертвования

    Returns:
        _type_: шаблон страницы для пожертвования
    """
    if not session.get('userLogged', False):
        return redirect(url_for('sign_in'))

    info_logger.info(
        f"User {session.get('userLogged')} visited page donation_form")
    return render_template("donation_form.html", email=session.get('userLogged'))


@app.route('/after_donation/<email>', methods=['POST', 'GET'])
def after_donation(email):
    """пока что только говорит да или нет, но в планах разрабокти отпрравка информации по почте фонду

    Args:
        email (_type_): email пользователя

    Returns:
        _type_: шаблон страницы после донаната
    """
    if request.method == 'POST':
        if not session.get('userLogged', False):
            return redirect(url_for('sign_in'))

        try:
            info_logger.info(
                f"User {email} successfully send donation_form info")
            return jsonify({'success': True, 'message': 'Вещь добавлена'}), 200

        except Exception as e:
            er_logger.error(f"Error in after_donation: {str(e)}")
            return jsonify({'success': False, 'message': str(e)}), 500

    return render_template('after_donation.html', email=session.get('userLogged'))


@app.route('/about')
def about():
    """отрисовывает страницу о нас

    Returns:
        _type_: шаблон страницы
    """
    info_logger.info(f"User visited page about")
    return render_template('about.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
