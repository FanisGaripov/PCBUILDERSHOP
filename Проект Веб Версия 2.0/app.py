from flask import Flask, render_template, request, redirect, flash, session, url_for
from models import db, Manufacturer, Category, Item, Manufacturer_items, User
import os, flask_login
from flask_login import login_required, UserMixin, LoginManager, login_user
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/'
app.secret_key = 'supersecretkey'
login_manager = LoginManager()
login_manager.init_app(app)
db.init_app(app)

@app.route('/')
def index():
    user = flask_login.current_user
    manufacturers = Manufacturer.query.all()
    return render_template('index.html', manufacturers=manufacturers, user=user)


@app.route('/aboutme')
def aboutme():
    user = flask_login.current_user
    return render_template('about.html', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    user = flask_login.current_user
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect('/')
        else:
            return 'Invalid username or password'
    return render_template('login.html', user=user)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.request_loader
def load_user_from_request(request):
    user_id = request.args.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None


@app.route('/register', methods=['GET', 'POST'])
def register():
    user = flask_login.current_user
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        if not User.query.filter_by(username=username).first():
            user = User(username=username, name=name, surname=surname, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('registration.html', user=user)


@app.route('/profile')
def profile():
    user = flask_login.current_user
    if user.is_authenticated:
        return render_template('profile.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for('index'))


@app.route('/upload', methods=['POST'])
def upload():
    user = flask_login.current_user
    if user.is_authenticated:
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect('/')
    else:
        return redirect(url_for('login'))


@app.route('/buynow/<int:item_id>', methods=['GET', 'POST'])
def buynow(item_id):
    item = Item.query.get(item_id)
    user = flask_login.current_user
    if user.is_authenticated:
        if item.quantity > 0:
            if 'kolvo' in request.form and request.form['kolvo'].isdigit():
                kolvo = request.form['kolvo']
                item.quantity -= int(kolvo)
                if user.pokupki is None and user.summa is None:
                    user.pokupki = int(kolvo)
                    user.summa = item.price * int(kolvo)
                else:
                    user.pokupki += int(kolvo)
                    user.summa += item.price * int(kolvo)
                db.session.commit()
                db.session.commit()
            else:
                flash('Ошибка')
        return render_template('buynow.html', item=item, user=user)
    else:
        return redirect(url_for('login'))


@app.route('/add_to_item/<int:item_id>', methods=['GET', 'POST'])
def add_to_item(item_id):
    item = Item.query.get(item_id)
    user = flask_login.current_user
    if user.is_authenticated:
        if item.quantity < 1:
            if 'kolvo' in request.form:
                kolvo = request.form['kolvo']
                item.quantity += int(kolvo)
                db.session.commit()
            else:
                flash('Ошибка: Не указано количество товара')
        else:
            redirect('/')
        return render_template('add_to_item.html', item=item, user=user)
    else:
        return redirect(url_for('login'))


total_price = 0
@app.route('/shopping-cart/')
def cart():
    global total_price
    item = Item.query.all()
    user = flask_login.current_user
    if user.is_authenticated:
        if 'cart' not in session or session['cart'] == []:
            return render_template('shoppingcart2.html', user=user)
        else:
            return render_template('shoppingcart.html', item=item, cart=session['cart'], total_price=total_price, user=user)
    else:
        return redirect(url_for('login'))


def cart_session():
    if 'cart' not in session:
        session['cart'] = []


@app.route('/add_to_cart', methods=['GET', 'POST'])
def add_to_cart():
    user = flask_login.current_user
    if user.is_authenticated:
        if request.method == "POST":
            id = int(request.form.get('id'))
            qty = int(request.form.get('qty'))
            price = float(request.form.get('price'))
            name = str(request.form.get('name'))
            description = str(request.form.get('description'))
            quantity = str(request.form.get('quantity'))
            image = str(request.form.get('image'))
            cart_session()
            matching = [d for d in session['cart'] if d['id'] == id]
            if matching:
                matching[0]['qty'] += qty
            else:
                session['cart'].append({'id': id, 'qty': qty, 'price': price, 'name': name, 'description': description, 'quantity': quantity, 'image': image})
            global total_price
            total_price = sum(item['price'] * item['qty'] for item in session['cart'])
            session.modified = True

        return redirect('/shopping-cart')
    else:
        return redirect(url_for('login'))


@app.route('/buy_all', methods=['POST'])
def buy_all():
    user = flask_login.current_user
    if user.is_authenticated:
        if request.method == "POST":
            # Получаем все товары из корзины
            cart_items = session['cart']

            # Проходимся по каждому товару и уменьшаем его количество в базе данных
            for item in cart_items:
                item_id = item['id']
                quantity = item['qty']
                price = item['price']
                item_to_buy = Item.query.get(item_id)
                if item_to_buy.quantity >= quantity:
                    item_to_buy.quantity -= quantity
                    if user.pokupki is None and user.summa is None:
                        user.pokupki = quantity
                        user.summa = price
                    else:
                        user.pokupki += quantity
                        user.summa += price * quantity
                    db.session.commit()
                else:
                    flash('Ошибка: Недостаточно товара на складе')
                    return redirect('/shopping-cart')

            # Очищаем корзину
            session['cart'] = []
            session.modified = True

            # Сохраняем изменения в базе данных
            db.session.commit()

            # Возвращаемся на страницу корзины с сообщением об успешной покупке
            flash('Все товары успешно куплены!')
            return redirect('/shopping-cart')
    else:
        return redirect(url_for('login'))


@app.route('/remove_from_cart/<int:item_id>', methods=['GET', 'POST'])
def remove_from_cart(item_id):
    global total_price
    if request.method == "POST":
        session['cart'] = [item for item in session['cart'] if item['id'] != item_id]
        session.modified = True
        total_price = sum(item['price'] for item in session['cart'])

    return redirect('/shopping-cart')


@app.route('/clear_cart', methods=['GET', 'POST'])
def clear_cart():
    global total_price
    if request.method == "POST":
        session['cart'] = []
        session.modified = True
        total_price = 0

    return redirect('/shopping-cart')


@app.route('/<manufacturer>/')
def show_categories(manufacturer):
    user = flask_login.current_user
    manufacturer = Manufacturer.query.filter_by(name=manufacturer).first()
    if manufacturer is None:
        return render_template('bug.html', user=user)
    items = manufacturer.items
    categories = set(item.category for item in items)
    return render_template('categories.html', manufacturer=manufacturer, categories=categories, user=user)


@app.route('/create', methods=['POST', 'GET'])
def create():
    user = flask_login.current_user
    if user.is_authenticated:
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
            return render_template('create.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/delete_item', methods=['POST', 'GET'])
def delete_item():
    user = flask_login.current_user
    if user.is_authenticated:
        if request.method == 'POST':
            item_id = request.form['delete_id']
            item = Item.query.get(item_id)
            manufacturer_item = Manufacturer_items.query.filter_by(item_id=item_id).first()
            try:
                db.session.delete(item)
                db.session.delete(manufacturer_item)
                db.session.commit()
                redirect('/')
            except:
                return 'Товар с указанным ID не найден'
        else:
            return render_template('delete_item.html', user=flask_login.current_user)
    else:
        return redirect(url_for('login'))


@app.route('/<manufacturer>/<category>')
def show_items(manufacturer, category):
    items = Item.query.join(Item.manufacturers).join(Item.category).\
                filter(Manufacturer.name == manufacturer).\
                filter(Category.name == category).all()
    user = flask_login.current_user
    return render_template('items.html', manufacturer=manufacturer, category=category, items=items, user=user)


if __name__ == '__main__':
    app.run(debug=True)