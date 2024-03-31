from flask import Flask, render_template, request, redirect
from models import db, Manufacturer, Category, Item

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def index():
    manufacturers = Manufacturer.query.all()
    return render_template('index.html', manufacturers=manufacturers)


@app.route('/aboutme')
def aboutme():
    return render_template('about.html')

@app.route('/buynow/<int:item_id>', methods=['GET', 'POST'])
def buynow(item_id):
    item = Item.query.get(item_id)
    return render_template('buynow.html', item=item)


@app.route('/shopping-cart')
def shoppingcart():
    return render_template('shoppingcart.html')


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
        item = Item(id=id, name=name, description=description, price=price, quantity=quantity, category_id=category_id)
        try:
            db.session.add(item)
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