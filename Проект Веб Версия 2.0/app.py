from flask import Flask, render_template, request, redirect, flash, session, url_for
from models import db, Manufacturer, Category, Item, Manufacturer_items
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/'
app.secret_key = 'supersecretkey'
db.init_app(app)

@app.route('/')
def index():
    manufacturers = Manufacturer.query.all()
    return render_template('index.html', manufacturers=manufacturers)


@app.route('/aboutme')
def aboutme():
    return render_template('about.html')


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect('/')


@app.route('/buynow/<int:item_id>', methods=['GET', 'POST'])
def buynow(item_id):
    item = Item.query.get(item_id)
    if request.method == "POST":
        kolvo = int(request.form['kolvo'])

    # Проверка наличия товара перед покупкой
        if item.quantity > 0:
            item.quantity -= kolvo
            db.session.commit()
        else:
            flash('Извините, товар закончился.')
        return redirect('/')
    else:
        return render_template('buynow.html', item=item)

@app.route('/shopping-cart/')
def cart():
    item = Item.query.all()
    return render_template('shoppingcart.html', item=item, cart=session['cart'])


def cart_session():
    if 'cart' not in session:
        session['cart'] = []


@app.route('/add_to_cart', methods=['GET', 'POST'])
def add_to_cart():
    if request.method == "POST":
        id = int(request.form.get('id'))
        qty = int(request.form.get('qty'))
        cart_session()
        matching = [d for d in session['cart'] if d['id'] == id]
        if matching:
            matching[0]['qty'] += qty
        else:
            session["cart"].append({'id': id, 'qty': qty})

    return redirect('/shopping-cart')


@app.route('/<manufacturer>/')
def show_categories(manufacturer):
    manufacturer = Manufacturer.query.filter_by(name=manufacturer).first()
    if manufacturer is None:
        return render_template('bug.html')
    items = manufacturer.items
    categories = set(item.category for item in items)
    return render_template('categories.html', manufacturer=manufacturer, categories=categories)


@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == "POST":
        id = request.form['id']
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        quantity = request.form['quantity']
        category_id = request.form['category_id']
        image = request.form['image']
        item = Item(id=id, name=name, description=description, price=price, quantity=quantity, category_id=category_id, image=image)
        manufacturer_id = request.form['manufacturer_id']
        item_id = request.form['item_id']
        manufacturer_item = Manufacturer_items(manufacturer_id=manufacturer_id, item_id=item_id)
        try:
            db.session.add(item)
            db.session.add(manufacturer_item)
            db.session.commit()
            return redirect('/')
        except:
            return "Ошибочка"
    else:
        return render_template('create.html')


@app.route('/<manufacturer>/<category>')
def show_items(manufacturer, category):
    items = Item.query.join(Item.manufacturers).join(Item.category).\
                filter(Manufacturer.name == manufacturer).\
                filter(Category.name == category).all()
    return render_template('items.html', manufacturer=manufacturer, category=category, items=items)

if __name__ == '__main__':
    app.run(debug=True)