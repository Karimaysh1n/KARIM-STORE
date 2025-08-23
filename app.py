from datetime import datetime, date


from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///KARIM_STORE_DATA.db'
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'
app.config['SECRET_KEY'] = 'your_very_secret_key_here'
jwt = JWTManager(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
UPLOAD_FOLDER = "static/uploads/products"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    views = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    condition = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(80), nullable=False)
    number = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    wilaya = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller = db.relationship('User', backref='products')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(80), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='comments')
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', backref='comments')

class Replaye(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    replay = db.Column(db.String(80), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='replayes')
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    comment = db.relationship('Comment', backref='replayed_comments')




with app.app_context():
    db.create_all()

WILAYAS = [
    "أدرار","الشلف","الأغواط","أم البواقي","باتنة","بجاية","بسكرة","بشار","البليدة","البويرة",
    "تمنراست","تبسة","تلمسان","تيارت","تيزي وزو","الجزائر","الجلفة","جيجل","سطيف","سعيدة",
    "سكيكدة","سيدي بلعباس","عنابة","قالمة","قسنطينة","المدية","مستغانم","المسيلة","معسكر","ورقلة",
    "وهران","البيض","إليزي","برج بوعريريج","بومرداس","الطارف","تندوف","تيسمسيلت","الوادي","خنشلة",
    "سوق أهراس","تيبازة","ميلة","عين الدفلى","النعامة","عين تموشنت","غرداية","غليزان","تيميمون",
    "برج باجي مختار","أولاد جلال","بني عباس","عين صالح","عين قزام","تقرت","جانت","المغير","المنيعة"
]

CATEGORIES = [
    ("electronics", "إلكترونيات"),
    ("cars", "سيارات"),
    ("houses", "عقارات")
]

@app.route('/', methods=['GET'])
def home():
    # جلب 12 منتج فقط لكل فئة
    electronics_products = Product.query.filter_by(category='electronics').limit(12).all()
    services_products   = Product.query.filter_by(category='services').limit(12).all()
    cars_products       = Product.query.filter_by(category='cars').limit(12).all()
    clothes_products    = Product.query.filter_by(category='clothes').limit(12).all()
    residences_products = Product.query.filter_by(category='residences').limit(12).all()
    houses_products     = Product.query.filter_by(category='houses').limit(12).all()
    phones_products     = Product.query.filter_by(category='phones').limit(12).all()
    furniture_products  = Product.query.filter_by(category='furniture').limit(12).all()
    gaming_products     = Product.query.filter_by(category='gaming').limit(12).all()
    decoration_products = Product.query.filter_by(category='decoration').limit(12).all()
    others_products     = Product.query.filter_by(category='others').limit(12).all()

    return render_template(
        'home_page.html',
        electronics_products=electronics_products,
        services_products=services_products,
        cars_products=cars_products,
        clothes_products=clothes_products,
        residences_products=residences_products,
        houses_products=houses_products,
        phones_products=phones_products,
        furniture_products=furniture_products,
        gaming_products=gaming_products,
        decoration_products=decoration_products,
        others_products=others_products,
        wilayas=WILAYAS,
        categories=CATEGORIES
    )


@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if "username" not in session:
        flash("Login first" , "warning")
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            name = request.form['name']
            price = request.form['price']
            quantity = request.form['quantity']
            category = request.form['category']
            condition = request.form['condition']
            description = request.form['description']
            file = request.files['image']
            number = request.form['number']
            email = request.form['email']
            wilaya = request.form['wilaya']
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                filename = "default.png"
            today = date.today()
            new_product = Product(name=name, price=price, quantity=quantity, category=category, condition=condition,
                                description=description, image=filename, views=0 , number=number , user_id=session['user_id'] , date=today , email=email , wilaya=wilaya)
            db.session.add(new_product)
            db.session.commit()
            flash('Product successfully added' , category="success")
            return redirect(url_for('home'))
        return render_template('sell_page.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
        if "username" in session:
            flash("You already logged in" , category="error")
            return redirect(url_for('home'))
        if request.method == 'POST':
            session.clear()
            username = request.form['username'].strip()
            password = request.form['password'].strip()

            target_user = User.query.filter_by(username=username).first()

            if target_user and check_password_hash(target_user.password, password):
                session['username'] = target_user.username
                session['user_id'] = target_user.id
                flash('Login successfully', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password', 'error')
                return redirect(url_for('login'))
        return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session.clear()
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        target_user = User.query.filter_by(username=username).first()
        if target_user:
            flash('Username already taken' , category="error")
            return redirect(url_for('register'))
        new_user = User(username=username , password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        session['user_id'] = new_user.id
        flash('Registration successfully' , category="success")
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/product_info/<product_id>', methods=['GET' , 'POST'])
def product_info(product_id):
    if request.method == 'POST':
      if "user_id" not in session:
          flash("Login first" , "warning")
          return redirect(url_for('login'))
      elif "user_id" in session:
        product_id = int(product_id)
        today = date.today()
        target_product = Product.query.filter_by(id=product_id).first()
        target_product.views += 1
        if "comment" in request.form:
            comment = request.form['comment']
            new_comment = Comment(comment=comment, date=today , user_id=session['user_id'] , product_id=product_id)
            db.session.add(new_comment)
            db.session.commit()
            comments = Comment.query.filter_by(product_id=product_id).all()
            replayes = Replaye.query.all()
            flash('Comment successfully added', category="success")
            return render_template('product_info.html', product=target_product, comments=comments , replayes=replayes)
    product_id = int(product_id)
    target_product = Product.query.filter_by(id=product_id).first()
    comments = Comment.query.filter_by(product_id=product_id).all()
    replayes = Replaye.query.all()
    return render_template('product_info.html' , product=target_product , comments=comments , replayes=replayes)

@app.route('/product/<comment_id>/<product_id>', methods=['GET' , 'POST'])
def product_info2(comment_id , product_id):
    if request.method == 'POST':
      if "user_id" not in session:
        flash("Login first", "warning")
        return redirect(url_for('login'))
      elif "user_id" in session:
        comment_id = int(comment_id)
        product_id = int(product_id)
        today = date.today()
        target_comment = Comment.query.filter_by(id=comment_id).first()
        target_product = Product.query.filter_by(id=product_id).first()
        replayes = Replaye.query.filter_by(comment_id=comment_id).all()
        if "replay" in request.form:
            replay = request.form["replay"]
            new_replay = Replaye(replay=replay , date=today , user_id=session['user_id'] , comment_id=comment_id)
            db.session.add(new_replay)
            db.session.commit()
            flash('Replay successfully added', category="success")
            comments = Comment.query.all()
            return render_template('product_info.html', product=target_product, comments=comments , replayes=replayes)
    comments = Comment.query.filter_by(product_id=product_id).all()
    replayes = Replaye.query.filter_by(comment_id=comment_id).all()
    target_product = Product.query.filter_by(id=product_id).first()
    return render_template('product_info.html' , product=target_product , comments=comments , replayes=replayes)



@app.route('/search')
def search():
    query = request.args.get("q", "").strip()
    if not query:
        flash("Please enter a search term", category="error")
        return redirect(url_for('home'))

    # تقسيم الجملة إلى كلمات
    words = query.split()

    # البحث: أي منتج يحتوي على query
    products = Product.query.filter(Product.name.ilike(f"%{query}%")).all()

    # فلترة إضافية لو تحب
    results = []
    for product in products:
        if any(word.lower() in product.name.lower() for word in words):
            results.append(product)

    return render_template('search_suggestions.html', results=results, product=query)

@app.route('/see_more_electronics')
def see_more_electronics():
    electronics_products = Product.query.filter_by(category="electronics").all()
    return render_template('see_more.html' , electronics=electronics_products)

@app.route('/see_more_services')
def see_more_services():
    services_products = Product.query.filter_by(category="services").all()
    return render_template('see_more.html' , services=services_products)

@app.route('/see_more_cars')
def see_more_cars():
    cars_products = Product.query.filter_by(category="cars").all()
    return render_template('see_more.html' , cars=cars_products)

@app.route('/see_more_clothes')
def see_more_clothes():
    clothes_products = Product.query.filter_by(category="clothes").all()
    return render_template('see_more.html' , clothes=clothes_products)

@app.route('/see_more_residences')
def see_more_residences():
    residences_products = Product.query.filter_by(category="residences").all()
    return render_template('see_more.html' , residences=residences_products)

@app.route('/see_more_houses')
def see_more_houses():
    houses_products = Product.query.filter_by(category="houses").all()
    return render_template('see_more.html' , houses=houses_products)

@app.route('/see_more_phones')
def see_more_phones():
    phones_products = Product.query.filter_by(category="phones").all()
    return render_template('see_more.html' , phones=phones_products)

@app.route('/see_more_furniture')
def see_more_furniture():
    furnitures_products = Product.query.filter_by(category="furnitures").all()
    return render_template('see_more.html' , furnitures=furnitures_products)

@app.route('/see_more_gaming')
def see_more_gaming():
    gaming_products = Product.query.filter_by(category="gaming").all()
    return render_template('see_more.html' , gaming=gaming_products)

@app.route('/see_more_decorations')
def see_more_decorations():
    decorations_products = Product.query.filter_by(category="decorations").all()
    return render_template('see_more.html' , decorations=decorations_products)


@app.route('/products_of_wilaya/<wilaya>')
def products_of_wilaya(wilaya):
    wilaya_products = Product.query.filter_by(wilaya=wilaya).all()
    is_electronics = Product.query.filter_by(category="electronics" , wilaya=wilaya).all()
    is_services = Product.query.filter_by(category="services" , wilaya=wilaya).all()
    is_cars = Product.query.filter_by(category="cars" , wilaya=wilaya).all()
    is_clothes = Product.query.filter_by(category="clothes" , wilaya=wilaya).all()
    is_residences = Product.query.filter_by(category="residences" , wilaya=wilaya).all()
    is_houses = Product.query.filter_by(category="houses" , wilaya=wilaya).all()
    is_phones = Product.query.filter_by(category="phones" , wilaya=wilaya).all()
    is_furniture = Product.query.filter_by(category="furniture" , wilaya=wilaya).all()
    is_gaming = Product.query.filter_by(category="gaming" , wilaya=wilaya).all()
    is_decorations = Product.query.filter_by(category="decorations" , wilaya=wilaya).all()
    return render_template('products_of_wilaya.html' , wilaya_products=wilaya_products , wilaya=wilaya,
                           is_electronics=is_electronics,
                           is_services=is_services,
                           is_cars=is_cars,
                           is_clothes=is_clothes,
                           is_residences=is_residences,
                           is_houses=is_houses,
                           is_phones=is_phones,
                           is_furniture=is_furniture,
                           is_gaming=is_gaming,
                           is_decorations=is_decorations)




@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/google5c6f4766bb48684f.html')
def google_verification():
    return "google-site-verification: google5c6f4766bb48684f.html"




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)