from flask import Flask, render_template, url_for, request

app = Flask(__name__)


@app.route('/sign_in')
def sign_in():
    return render_template('sign_in.html')


@app.route('/testor_form', methods=['POST'])
def testor_form():
    return render_template('testor_form.html', requests=request.form)


@app.route('/registration')
def registration():
    return render_template('registration.html')


if __name__ == '__main__':
    app.run(debug=True)
