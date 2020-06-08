from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError, FileField,IntegerField,SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_wtf.file import FileRequired,FileAllowed
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta
from flask_login import LoginManager, login_user, current_user, logout_user, login_required,UserMixin
from flask_bcrypt import Bcrypt
from config import MConfig
import os
from PIL import Image
import PIL
from wtforms.fields.html5 import TelField
from flask_migrate import Migrate
from wtforms.widgets import TextArea
from werkzeug.utils import secure_filename





app = Flask(__name__)
app.config.from_object(MConfig)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
app.config['UPLOAD_FOLDER'] = ".\static\images"
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    user_img = db.Column(db.String(60), nullable=True)
    city = db.Column(db.String(60), nullable=False)
    otdel=db.Column(db.String(60), nullable=False)
    phone = db.Column(db.Integer, nullable=False)

    otzivy= db.Column(db.String(360), nullable=True)


    def __repr__(self):
        return f"User('{self.username}' - '{self.email}')"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    Authors=db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    price= db.Column(db.String(150), nullable=False)
    aromat=db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    alt_txt=db.Column(db.String(250), nullable=True)
    creationData = db.Column(db.DateTime)
    img=db.Column(db.String(248), nullable=True)
    user_id = db.Column(db.Integer, nullable=False)



    def __repr__(self):
        return f'<Article{self.content}>'



class RegistrationForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired(), Length(min=4)])
    email = StringField('Электроная почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirmPassword = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    city = StringField('Город', validators=[DataRequired()])
    otdel=StringField('Отделение', validators=[DataRequired()])
    phone = TelField('Телефон')
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Такое имя уже существует')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Такой e-mail уже существует')

  

class LoginForm(FlaskForm):
    email = StringField('Электроная почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')



class ProductsForm(FlaskForm):
    brand=StringField('Брэнд', validators=[DataRequired()])
    name = StringField('Название', validators=[DataRequired()])
    aromat= StringField('Тип аромата', validators=[DataRequired()])
    content = StringField(u'описание', widget=TextArea(),validators=[DataRequired()])
    price = IntegerField('Цена', validators=[DataRequired()])
    alt_txt=StringField('Альтернативный текст', validators=[DataRequired()])
    img=  FileField(validators=[FileRequired()])
    img_name=StringField('img name', validators=[DataRequired()])
    Btm = SubmitField('Добавить')

    
    def validate_Content(self, field) :
        if len(field.data) < 10 :
            raise ValidationError('Article must be from 10 characters')



class SearchForm(FlaskForm):
    search=StringField(validators=[DataRequired()], render_kw={"placeholder": "Поиск товаров"})
    submit = SubmitField('Найти')

class Inputs(FlaskForm):
    myField = SelectField(u'Field name', validators = [DataRequired()])

class Admin():
    name='deft'


class Revs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    otziv=db.Column(db.String(250), nullable=True)
    authorOtziv=db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, nullable=True)


class Reviews(FlaskForm):
    Rev = StringField(u'Оставь отзыв', widget=TextArea(),validators=[DataRequired()])
    Btm = SubmitField('Добавить')





@app.errorhandler(404)
def page_not_found(error):
    return "такой страницы нет"


@app.route('/', methods=['GET', 'POST'])
def index():
    name=Admin()
    input1=Inputs()
    page=request.args.get('page')
    search=SearchForm()
    order=request.args.get('sort')
    
    if request.form.get("myfilter_radio"):
        x=request.form.get("myfilter_radio")
        print(x)
        items=Products.query.filter(Products.brand.contains(x))
        print(items)
 
    elif order is None:
        items = Products.query.order_by(Products.creationData.desc())

    elif order=='1':
        items = Products.query.order_by(Products.name)
    elif order=='2':
        items = Products.query.order_by(Products.brand)
    elif order=='3':
        items =  Products.query.order_by(Products.price)
    elif order=='4':
        items = Products.query.order_by(Products.price.desc())
    else:
        items = Products.query.order_by(Products.creationData.desc())


    if page and page.isdigit():
        page=int(page)
    else:
        page=1
        

    data=request.form.get('search')
    if data:
        items=Products.query.filter(Products.brand.contains(data) | Products.name.contains(data))

  
    pages=items.paginate(page=page,per_page=15)
    colvo= items.count()


    brand=Products.query.distinct(Products.brand).group_by(Products.brand)
  
    aromat=Products.query.distinct(Products.aromat).group_by(Products.aromat)

    return render_template ('index.html',items=items,title='ParfumeLover',
     colvo=colvo,pages =pages,search=search,input=input1,brand=brand,admin=name,aromat=aromat)




@app.route('/add', methods=['GET', 'POST'])
@login_required

def add():
    name=Admin()
    name=name.name
    if current_user.username==name:
        search=SearchForm()
        time = datetime.now()
        form = ProductsForm()
        brand=request.form.get('brand')
        name=request.form.get('name')
        aromat=request.form.get('aromat')
        price=request.form.get('price')
        alt=request.form.get('alt_txt')

        f=form.img.data
        fname=request.form.get('img_name')
        if f:
            img_path = os.getcwd() + url_for('static', filename='images/' + fname)
            image = Image.open(f)
            size=480,480
            image = image.resize(size)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))


        Authors='deft'
        content= request.form.get('content')
        userId=1
        if form.validate_on_submit():
            items = Products(brand=brand, Authors=Authors, name=name, price=price,
                            content=content, creationData=time,user_id=userId,
                            alt_txt=alt,img=fname,aromat=aromat)
            db.session.add(items)
            db.session.commit()
            return redirect('/')
    else:
        return redirect('/')

    return render_template('add.html', form=form,search=search,admin=name)


@app.route("/register", methods=['GET', 'POST'])
def register():
    name=Admin()
    search=SearchForm()
    if current_user.is_authenticated:
        return redirect('/')
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        #print(hashed_password)
        city=form.city.data
        otdel=form.otdel.data
        phone=form.phone.data
        user = User(username=form.username.data, email=form.email.data,
                    password=hashed_password,city=city,otdel=otdel,phone=phone)
        db.session.add(user)
        db.session.commit()
        flash('Спасибо за регистрацию')
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form,search=search,admin=name)

@app.route('/login',methods=['GET', 'POST'])
def login():
    name=Admin()
    form=SearchForm()
    if current_user.is_authenticated:
        return redirect('/')
    form2=LoginForm()
    if form2.validate_on_submit():
        user = User.query.filter_by(email=form2.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form2.password.data):
            login_user(user, remember=form2.remember.data, duration=timedelta(days=5))
            next_page = request.args.get('next') #################################################### nex_page in NOne
            if next_page is None:
                next_page='/'
            return redirect (next_page)
        else:
            flash('Login Unsuccessful. Please check your email and password')

    return render_template('login.html', title='Вход', search=form, form2=form2,admin=name)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/remove', methods=['GET'])
def removeTask():
    productId = request.args.get('id')
    art= Products.query.filter_by(id=productId).first()
    db.session.delete(art)
    db.session.commit()
    return redirect('/')




@app.route('/show',methods=['GET', 'POST'])
def show():
    form=Reviews()
    name=Admin()
    search=SearchForm()
    revies=Reviews()
    nameId=request.args.get('id')
    content=Products.query.filter_by(id=nameId).first()
    revs1=request.form.get('Rev')
    user=current_user.username
    user_id=current_user.get_id()

    #print(revs1,user)

    if revies.validate_on_submit():

        rev= Revs(authorOtziv=user,otziv=revs1,user_id=user_id)
        db.session.add(rev)
        db.session.commit()
    x=Revs.query.filter_by(id=nameId).first()

    return render_template('show.html', search=search,title='lkscas',content=content,admin=name,form=form,x=x)


@app.route('/profile',methods=['GET', 'POST'])
def profile():
    search=SearchForm()
    name=Admin()
    return render_template ('profile.html',admin=name,search=search)

@app.route('/cart',methods=['GET' ,'POST'])
def cart():
    search=SearchForm()
    name=Admin()
    items=[]
    cartId=request.args.get('id')
    cart=Products.query.filter_by(id=cartId).first()
    items.append(cart)
    if items:
        return render_template('cart.html',admin=name,search=search,items=items)
    else:
        return render_template('cart.html',admin=name,search=search,items=items)


@app.route('/add-to-cart', methods=['GET', 'POST'])
def add_to_cart():
    if request.method == 'POST':
        id = request.args.get('id')
        qty = int(request.form['qty'])

        cart = session.setdefault('cart', {})
        cart[item_id] = cart.get(product_id, 0) + qty

        return redirect(url_for('index'))

        

if __name__ == '__main__':
    app.run(debug=True)