import sqlite3
from sqlite3 import Error

from datetime import datetime

from flask import Flask, render_template, request, session, redirect
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "qscefbthm"
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
        connection.execute('pragma foreign_keys=ON')
        return connection
    except Error as e:
        print(e)
        return None

def is_logged_in():
    """
    A function to return whether the user is logged in or not
    """
    if session.get('email') is None:
        print("Not logged in")
        return False
    else:
        print("Logged in")
        return True


@app.route('/')
def render_homepage():
    session_data = list(session.keys())
    print(session_data)
    fname = session.get('fname')
    if fname == None:
        fname = ""
    message = request.args.get('message')
    if message == None:
        message = ""
    error = request.args.get('error')
    if error == None:
        error = ""
    return render_template('home.html', logged_in=is_logged_in(), name=fname, message=message, error=error)


@app.route('/menu')
def render_menu_page():
    con = create_connection(DATABASE)
    query = "SELECT name, description, volume, price, image, id FROM product"
    cur = con.cursor()  # Create cursor to run the query
    cur.execute(query)  # Runs the query
    product_list = cur.fetchall()
    con.close()
    return render_template('menu.html', products=product_list, logged_in=is_logged_in())


@app.route('/addtocart/<product_id>')
def render_addtocart_page(product_id):
    print("Add {} to cart".format(product_id))
    try:
        customerid = session['customer_id']
    except KeyError:
        return redirect('/login?error=You+must+login+before+ordering')
    try:
        product_id = int(product_id)
    except ValueError:
        return redirect('/?error=Invalid+product+ID')
    timestamp = datetime.now()
    query = "INSERT INTO cart (customerid, productid, timestamp) VALUES (?, ?, ?)"
    con = create_connection(DATABASE)
    cur = con.cursor()
    try:
        cur.execute(query, (customerid, product_id, timestamp))
    except sqlite3.IntegrityError as e:
        print(e)
        con.close()
        return redirect('/?error=Invalid+product+ID')
    con.commit()
    return redirect(request.referrer)


@app.route('/cart')
def render_cart():
    if not is_logged_in():
        return redirect('/login?error=You+must+login+first')
    userid = session['customer_id']
    query = "SELECT productid FROM cart WHERE customerid=?;"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query, (userid,))
    product_ids = cur.fetchall()
    print(product_ids)

    for i in range(len(product_ids)):
        product_ids[i] = product_ids[i][0]
    print(product_ids)
    unique_product_ids = list(set(product_ids))
    print(unique_product_ids)
    for i in range(len(unique_product_ids)):
        product_count = product_ids.count(unique_product_ids[i])
        unique_product_ids[i] = [unique_product_ids[i], product_count]
    print(unique_product_ids)
    query = """SELECT name, price FROM product WHERE id = ?;"""
    for item in unique_product_ids:
        cur.execute(query, (item[0],))
        item_details = cur.fetchall()
        print(item_details)
        item.append((item_details[0][0]))
        item.append((item_details[0][1]))
    con.close()
    print(unique_product_ids)
    total_price = 0
    for product in unique_product_ids:
        total_price += product[1] * product[3]
    print(total_price)
    return render_template('cart.html', cart_data=unique_product_ids, total_price=total_price, logged_in=is_logged_in())

@app.route('/contact')
def render_contact_page():
    return render_template('contact.html', logged_in=is_logged_in())


@app.route('/login', methods=['GET', 'POST'])
def render_login_page():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password').strip()
        hashed_password = bcrypt.generate_password_hash(password)
        query = """SELECT id, fname, password FROM customer WHERE email = ?"""
        con = create_connection(DATABASE)
        cur = con.cursor()
        cur.execute(query, (email,))
        user_data = cur.fetchall()
        con.close()
        if user_data:
            userid = user_data[0][0]
            firstname = user_data[0][1]
            db_password = user_data[0][2]
        else:
            return redirect('/login?error=Email+or+password+is+invalid')

        if not bcrypt.check_password_hash(db_password, password):
            return redirect('/login?error=Email+or+password+is+invalid')
        # Set up a session for this login
        session['email'] = email
        session['customer_id'] = userid
        session['fname'] = firstname
        session['cart'] = []
        return redirect('/?message=Successfully+logged+in+as+{}'.format(session.get('fname')))
    error = request.args.get('error')
    message = request.args.get('message')
    if error == None:
         error = ""
    if message == None:
        message = ""
    return render_template('login.html', logged_in=is_logged_in(), error=error, message=message)
    print(userid, firstname)


@app.route('/logout')
def render_logout_page():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    return redirect('/login?message=Logged+out+successfully')


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
        hashed_password = bcrypt.generate_password_hash(password)
        try:
            con = create_connection(DATABASE)
            query = "INSERT INTO customer (id, fname, lname, email, password) VALUES (NULL, ?, ?, ?, ?)"
            cur = con.cursor()  # Create cursor to run the query
            cur.execute(query, (fname, lname, email, hashed_password))  # Runs the query
            con.commit()
            con.close()
            return redirect('/login?message=Account+created+successfully')
        except:
            return redirect('/signup?error=Email+is+already+taken')
    error = request.args.get('error')
    if error == None:
        error = ""
    return render_template('signup.html', error=error, logged_in=is_logged_in())

app.run(host='0.0.0.0', debug=True)
