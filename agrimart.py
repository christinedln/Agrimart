from flask import Flask, request, redirect, url_for, session, render_template
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

def check(filename, username, password):
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            pass
    existing_usernames = set()
    with open(filename, 'a+') as file:
        file.seek(0)  
        for line in file:
            existing_usernames.add(line.split(':')[0])
        if username in existing_usernames:
            return f"Username '{username}' already exists. Please choose a different username."
        file.write(f'{username}:{password}\n')
    return "Username and password added."

def calculate_total(cart):
    total = 0
    for item in cart:
        total += item['price'] * item['quantity']
    return total

def login():
    username = request.form['username']
    password = request.form['password']

    try:
        with open('users.txt', 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        lines = []

    for line in lines:
        stored_username, stored_password = line.strip().split(':')
        if username == stored_username and password == stored_password:
            session['logged_in'] = True
            session['username'] = username  
            session['cart'] = []
            return redirect(url_for('success'))
    error_message = "Invalid username or password. Please check your username/password or sign up first."
    return render_template('index.html', error=error_message)

def save_checkout_details(filename, username, cart, user_number, user_email):
    with open(filename, 'a') as file:
        file.write(f"Username: {username}\n")
        file.write("Products:\n")
        for product in cart:
            file.write(f" - {product['name']} (Quantity: {product['quantity']})\n")
        if user_number or user_email:
            file.write(f"Number: {user_number}\n")
            file.write(f"Email: {user_email}\n")
        file.write("\n")

products = [
    {'id': 1, 'name': 'Vermicast', 'price': 200, 'image': '/images/vermicast.jpg'},
    {'id': 2, 'name': 'Complete Fertilizers with Sulfur', 'price': 100, 'image': '/images/completefertilizerwithsulfur.jpg'},
    {'id': 3, 'name': 'Osmocote 14-14-14', 'price': 350, 'image': '/images/osmocote14-14-14.jpg'},
    {'id': 4, 'name': 'Natural Coco Peat', 'price': 80, 'image': '/images/naturalcocopeat.jpg'},
    {'id': 5, 'name': 'Organic Concoctions and Extracts', 'price': 90, 'image': '/images/organicconcoctionsandextracts.jpg'},
    {'id': 6, 'name': 'Sprayers', 'price': 2199, 'image': '/images/sprayers.jpg'},
    {'id': 7, 'name': 'Rice Hull', 'price': 200, 'image': '/images/ricehull.png'},
    {'id': 8, 'name': 'Organic Brown Rice', 'price': 600, 'image': '/images/brownriceorganic.png'},
    {'id': 9, 'name': 'Whole Wheat Seeds', 'price': 70, 'image': '/images/wholewheatseeds.png'},
    {'id': 10, 'name': 'Organic Black Brown Red', 'price': 399, 'image': '/images/organicblackbrownred.png'},
    {'id': 11, 'name': 'Organic Red Rice', 'price': 375, 'image': '/images/organicredrice.png'},
    {'id': 12, 'name': 'Hand Cultivator', 'price': 155, 'image': '/images/handcultivator.jpg'},
    {'id': 13, 'name': 'Hand Fork', 'price': 50, 'image': '/images/handcultivator.jpg'},
    {'id': 14, 'name': 'Grab Hoe', 'price': 197, 'image': '/images/grab-hoe.jpg'},
    {'id': 15, 'name': 'Hand Trowel', 'price': 45, 'image': '/images/handtrowel.jpg'},
    {'id': 16, 'name': 'Rake', 'price': 400, 'image': '/images/rake.jpg'},
    {'id': 17, 'name': 'Rake', 'price': 450, 'image': '/images/rake2.jpg'},
    {'id': 18, 'name': 'Shovel', 'price': 380, 'image': '/images/shovel.jpg'},
    {'id': 19, 'name': 'Sickle', 'price': 100, 'image': '/images/sickle.jpg'},
    {'id': 20, 'name': 'Spade', 'price': 250, 'image': '/images/spade.jpg'},
    {'id': 21, 'name': 'Spading Fork', 'price': 360, 'image': '/images/spadingfork.jpg'},
    {'id': 22, 'name': 'Wheel Barrow', 'price': 1900, 'image': '/images/wheelbarrow.jpg'},
]

cart = []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'submit_button' in request.form and request.form['submit_button'] == 'Sign Up':
            username = request.form['username']
            password = request.form['password']
            status = check('users.txt', username, password)
            session['cart'] = []  
            return render_template('index.html', status=status, products=products, cart=session['cart'], calculate_total=calculate_total)
        elif 'submit_login' in request.form and request.form['submit_login'] == 'Login':
            return login()
    else:
        if session.get('logged_in'):
            return redirect(url_for('success'))
        else:
            session['cart'] = [] 
            return render_template('index.html', products=products, cart=session['cart'], calculate_total=calculate_total)

@app.route('/success')
def success():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    return render_template('shop.html', products=products, cart=session.get('cart', []), calculate_total=calculate_total)

@app.route('/logout')
def logout():
    session['logged_in'] = False
    session.pop('username', None) 
    session['cart'] = []  
    return redirect(url_for('index'))

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    product_id = int(request.form['product_id'])
    quantity = int(request.form['quantity'])
    product = next((p for p in products if p.get('id') == product_id), None)
    if product:
        product['quantity'] = quantity
        cart = session.get('cart', [])
        cart.append(product)
        session['cart'] = cart
    return redirect(url_for('success'))

@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    product_id = int(request.form['product_id'])
    product = next((p for p in session.get('cart', []) if p.get('id') == product_id), None)
    if product:
        cart = session.get('cart', [])
        cart.remove(product)
        session['cart'] = cart
    return redirect(url_for('success'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    success_message = None
    gcash_number = "09123456789"  

    if request.method == 'POST':
        username = session.get('username')
        user_number = request.form.get('number')
        user_email = request.form.get('email')
        save_checkout_details('checkoutdetails.txt', username, session['cart'], user_number, user_email)
        success_message = "Checkout details saved successfully."
        return redirect(url_for('payment'))
    if 'cart' not in session:
        session['cart'] = []
    cart = session['cart']
    total_price = calculate_total(cart)
    return render_template('checkout.html', total_price=total_price, cart=cart, success_message=success_message, gcash_number=gcash_number)

@app.route('/payment')
def payment():
    session.pop('cart', None)  
    return render_template('payment.html')

if __name__ == '__main__':
    app.run(debug=True)