import sqlite3
from sqlite3 import Error

from flask import Flask, render_template, request, session, redirect

app = Flask(__name__)
# GitHub Token: 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

DATABASE = "C:/Users/18044/PycharmProjects/Smile/smile.db"


def create_connection(db_file):
    """
    Create a connection with the database
    parameter: name of the database file
    returns: a connection to the file
    """
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
        return None


@app.route('/')
def render_homepage():
    return render_template('home.html')


@app.route('/menu')
def render_menu_page():
    con = create_connection(DATABASE)
    query = "SELECT name, description, volume, price, image FROM product"
    cur = con.cursor()  # Create cursor to run the query
    cur.execute(query)  # Runs the query
    product_list = cur.fetchall()
    con.close()
    return render_template('menu.html', products=product_list)


@app.route('/contact')
def render_contact_page():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def render_login_page():
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def render_signup_page():
    if request.method == 'POST':
        print(request.form)
        fname = request.form.get('fname').title().strip()
        lname = request.form.get('lname').title().strip()
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')
        password2 = request.form.get('password2')
        if password != password2:
            return redirect('/signup?error=Passwords+do+not+match')
        if len(password) < 8:
            return redirect('/signup?error=Password+must+be+eight+or+more+characters')

        try:
            con = create_connection(DATABASE)
            query = "INSERT INTO customer (id, fname, lname, email, password) VALUES (NULL, ?, ?, ?, ?)"
            cur = con.cursor()  # Create cursor to run the query
            cur.execute(query, (fname, lname, email, password))  # Runs the query
            con.commit()
            con.close()
            return redirect('/login')
        except:
            return redirect('/signup?error=Email+is+already+taken')
    error = request.args.get('error')
    if error == None:
        error = ""
    return render_template('signup.html', error=error)

app.run(host='0.0.0.0', debug=True)
