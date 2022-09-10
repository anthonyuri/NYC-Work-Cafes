from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from forms import LoginForm, RegisterForm
from datetime import date
from functools import wraps
import random
import datetime as dt
import ast

from sqlalchemy.testing.plugin.plugin_base import logging
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker, relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
# from forms import LoginForm, RegisterForm, CreatePostForm, CommentForm
from flask_gravatar import Gravatar

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

#CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes-nyc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


##CONFIGURE TABLE

# import logging
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# saved_cafe = db.Table('saved_cafe',
#                       db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
#                       db.Column('cafe_id', db.Integer, db.ForeignKey('cafe.id'))
#                       )

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    # user_cafes = db.relationship("Cafe", secondary=saved_cafe, back_populates="saved_users")
    # # comments = relationship("Comment", back_populates="comment_author")
    cafes = db.Column(db.String(1000))

    def __repr__(self):
        return f'<User "{self.name}">'

class Cafe(db.Model):
    _tablename__ = "cafe"
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.VARCHAR(250), nullable=False)
    map_url = db.Column(db.VARCHAR(500), nullable=False)
    img_url = db.Column(db.VARCHAR(500), nullable=False)
    location = db.Column(db.VARCHAR(500), nullable=False)
    has_sockets = db.Column(db.BOOLEAN, nullable=False)
    has_toilet = db.Column(db.BOOLEAN, nullable=False)
    has_wifi = db.Column(db.BOOLEAN, nullable=False)
    can_take_calls = db.Column(db.BOOLEAN, nullable=False)
    seats = db.Column(db.VARCHAR(250), nullable=False)
    coffee_price = db.Column(db.VARCHAR(250), nullable=False)

    # saved_users = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __repr__(self):
        return f'<Cafe "{self.name}">'

# db.create_all()

@app.route('/')
def home():
    all_cafes = Cafe.query.order_by(Cafe.id).all()

    counter = 0
    cafes_to_append = []
    all_cafes_three_list = []
    # create lists of three cafes inside a big list:
    for _ in all_cafes:
        cafes_to_append.append(all_cafes[counter])
        counter += 1
        if len(cafes_to_append) % 3 != 0:
            continue
        else:
            all_cafes_three_list.append(cafes_to_append)
            cafes_to_append = []
    # if there are leftovers in cafes_to_append, add them to the list as well:
    if len(cafes_to_append) > 0:
        all_cafes_three_list.append(cafes_to_append)


    import random
    random_num = random.randint(1, len(all_cafes_three_list) - 1)

    # now = dt.datetime.now()
    # current_hour = now.hour
    #
    # three_cafes = [all_cafes_three_list[0]]
    # if current_hour == 22:
    #     random_num = random.randint(1, len(all_cafes_three_list) - 1)
    #     three_cafes = [all_cafes_three_list[random_num]]

    three_cafes = [all_cafes_three_list[random_num]]

    return render_template("index.html", three_cafes=three_cafes)


@app.route('/cafes')
def cafes():
    all_cafes = Cafe.query.order_by(Cafe.id).all()
    for i in range(len(all_cafes)):
        all_cafes[i].ranking = len(all_cafes) - i
    db.session.commit()

    counter = 0
    cafes_to_append = []
    all_cafes_three_list = []
    # create lists of three cafes inside a big list:
    for _ in all_cafes:
        cafes_to_append.append(all_cafes[counter])
        counter += 1
        if len(cafes_to_append) % 3 != 0:
            continue
        else:
            all_cafes_three_list.append(cafes_to_append)
            cafes_to_append = []
    # if there are leftovers in cafes_to_append, add them to the list as well:
    if len(cafes_to_append) > 0:
        all_cafes_three_list.append(cafes_to_append)

    return render_template("cafes.html", all_cafes=all_cafes_three_list)


@app.route('/add', methods=["GET", "POST"])
def add_cafe():
    if request.method == 'POST':
        cafe_name = request.form['name'].title()
        map_url = request.form['map_url']
        img_url = request.form['img_url']
        location = request.form['location']
        has_sockets = int(request.form['has_sockets'])
        has_toilet = int(request.form['has_toilet'])
        has_wifi = int(request.form['has_wifi'])
        can_take_calls = int(request.form['can_take_calls'])
        seats = request.form['seats']


        if "$" not in request.form['coffee_price']:
            coffee_price = "$" + request.form['coffee_price']
        else:
            coffee_price = request.form['coffee_price']

        new_cafe = Cafe(name=cafe_name,
                        map_url=map_url,
                        img_url=img_url,
                        location=location,
                        has_sockets=has_sockets,
                        has_toilet=has_toilet,
                        has_wifi=has_wifi,
                        can_take_calls=can_take_calls,
                        seats=seats,
                        coffee_price=coffee_price)
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("add-cafe.html")

@app.route("/edit-cafe/<int:cafe_id>", methods=["GET", "POST"])
def edit_cafe(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    if request.method == 'POST':
        cafe.name = request.form['name']
        cafe.map_url = request.form['map_url']
        cafe.img_url = request.form['img_url']
        cafe.location = request.form['location']
        cafe.has_sockets = int(request.form['has_sockets'])
        cafe.has_toilet = int(request.form['has_toilet'])
        cafe.has_wifi = int(request.form['has_wifi'])
        cafe.can_take_calls = int(request.form['can_take_calls'])
        cafe.seats = request.form['seats']

        if "$" not in request.form['coffee_price']:
            price = "$" + request.form['coffee_price']
        else:
            price = request.form['coffee_price']
        cafe.coffee_price = price


        db.session.commit()
        return redirect(url_for("cafes"))

    return render_template("edit-cafe.html", cafe=cafe, is_edit=True)

@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
                form.password.data,
                method='pbkdf2:sha256',
                salt_length=8
            )

        new_user = User(
                email=form.email.data,
                name=form.name.data,
                password=hash_and_salted_password,
            )

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("cafes"))

    return render_template("register.html", form=form, current_user=current_user)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_user_page', username=user.name))
    return render_template("login.html", form=form, current_user=current_user)

@app.route('/user_save/<cafe_id>')
def user_save_cafe(cafe_id):
    if current_user.cafes == None:
        user_cafes_list = list(cafe_id)
        print(user_cafes_list)
    else:
        user_cafes_list = ast.literal_eval(current_user.cafes)
        user_cafes_list.append(cafe_id)
    print(str(user_cafes_list))
    current_user.cafes = str(user_cafes_list)

    db.session.commit()
    return redirect(url_for('get_user_page', username=current_user.name))

@app.route('/user_delete/<cafe_id>')
def user_delete_cafe(cafe_id):
    user_cafes_data = ast.literal_eval(current_user.cafes)
    user_cafes_data.remove(cafe_id)
    print(user_cafes_data)
    current_user.cafes = str(user_cafes_data)

    db.session.commit()
    return redirect(url_for('get_user_page', username=current_user.name))

@app.route('/<username>')
def get_user_page(username):
    print(current_user.cafes)
    if str(current_user.cafes) == '[]':
        user_cafes_data = None
        return render_template("user_page.html", list_empty=True)
    if current_user.cafes != None:
        user_cafes_data = ast.literal_eval(current_user.cafes)

        # for cafe_id in user_cafes_data:
        #     cafe = Cafe.query.get(cafe_id)

        print(user_cafes_data)
        user_cafes = [Cafe.query.get(cafe_id) for cafe_id in user_cafes_data]
        print(user_cafes)


        counter = 0
        cafes_to_append = []
        user_cafes_three_list = []
        # create lists of three cafes inside a big list:
        for _ in user_cafes:
            cafes_to_append.append(user_cafes[counter])
            counter += 1
            if len(cafes_to_append) % 3 != 0:
                continue
            else:
                user_cafes_three_list.append(cafes_to_append)
                cafes_to_append = []
        # if there are leftovers in cafes_to_append, add them to the list as well:
        if len(cafes_to_append) > 0:
            user_cafes_three_list.append(cafes_to_append)

        print(user_cafes_data)
        return render_template("user_page.html", user_cafes=[user_cafes], list_empty=False)
    return render_template("user_page.html", list_empty=True)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
