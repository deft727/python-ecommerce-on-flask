from flask import Flask, render_template, request, redirect, flash, url_for, session 
from flask_mail import Message,Mail
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
from time import time
import jwt
from flask import make_response


app = Flask(__name__)
app.config.from_object(MConfig)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
mail = Mail(app)
app.config['UPLOAD_FOLDER'] = "static/images"
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
    otzivy= db.relationship('Revs',backref='User',lazy='dynamic')

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def __repr__(self):
        return f"User('{self.username}' - '{self.email}')"
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    Authors=db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    price=  db.Column(db.Integer, nullable=False)
    aromat=db.Column(db.String(150), nullable=True)
    content = db.Column(db.Text, nullable=False)
    characteristics=db.Column(db.Text, nullable=False)
    alt_txt=db.Column(db.String(250), nullable=True)
    creationData = db.Column(db.DateTime)
    img1=db.Column(db.String(248), nullable=True)
    img2=db.Column(db.String(248), nullable=True)
    img3=db.Column(db.String(248), nullable=True)
    user_id = db.Column(db.Integer, nullable=False)
    otzivy2= db.relationship('Revs',backref='Products',lazy=True)

    def __repr__(self):
        return f'<Products{self.content}>'

class  ResetPasswordRequestForm(FlaskForm):
    email = StringField('Электроная почта', validators=[DataRequired(), Email()])
    submit = SubmitField('сбросить пароль')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Изменить пароль')

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

    def validate_phone(self, phone):
        user = User.query.filter_by(phone=phone.data).first()
        if user:
            raise ValidationError('Такой номер телефона уже существует')


class EditProfileForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired(), Length(min=4)])
    email = StringField('Электроная почта', validators=[DataRequired(), Email()])
    city = StringField('Город', validators=[DataRequired()])
    otdel=StringField('Отделение', validators=[DataRequired()])
    phone = TelField('Телефон')
    submit = SubmitField('Изменить')
    
    # def validate_username(self, username):
    #     user = User.query.filter_by(username=username.data).first()
    #     print(user.username,',///',username.data)
    #     if user:
    #         raise ValidationError('Такое имя уже существует')


class LoginForm(FlaskForm):
    email = StringField('Электроная почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class ProductsForm(FlaskForm):
    brand=StringField('Бренд', validators=[DataRequired()])
    name = StringField('Название', validators=[DataRequired()])
    aromat= StringField('Тип аромата', validators=[DataRequired()])
    content = StringField(u'описание', widget=TextArea(),validators=[DataRequired()])
    characteristics = StringField(u'характеристики', widget=TextArea(),validators=[DataRequired()])
    price = IntegerField('Цена', validators=[DataRequired()])
    alt_txt=StringField('Альтернативный текст', validators=[DataRequired()])
    img1=  FileField()
    img2=  FileField()
    img3=  FileField()
    img_name1=StringField('img name 1')
    img_name2=StringField('img name 2')
    img_name3=StringField('img name 3')
    Btm = SubmitField('Добавить')

    def validate_Content(self, field) :
        if len(field.data) < 10 :
            raise ValidationError('Описание должно быть не менее 10 символов')


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
    author=db.Column(db.String(250), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id=db.Column(db.Integer, db.ForeignKey('products.id'))
    img=db.Column(db.String(250), nullable=True)
    creationData = db.Column(db.DateTime)


class Reviews(FlaskForm):
    Rev = StringField(u'Оставить отзыв', widget=TextArea(),validators=[DataRequired()])
    Btm = SubmitField('Добавить')


class Cart(db.Model):
    userid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True)
    productid = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    prods = db.relationship('Products',backref='Products',lazy=True)

    def __repr__(self):
        return f"Cart('{self.userid}', '{self.productid}, '{self.quantity}')"


class Oders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    productid = db.Column(db.Integer, nullable=False)
    rebate = db.Column(db.Integer, nullable=False)    
    price=db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creationData = db.Column(db.DateTime)
    quantity=db.Column(db.Integer, nullable=False)
    oder=db.relationship('User',backref='User',lazy=True)
    #prod = db.relationship('Products',backref='Prod',lazy=True)
class quickorderForm(FlaskForm):
    Name=StringField('Имя', validators=[DataRequired()])
    Phone = IntegerField('Телефон', validators=[DataRequired()])
    submit = SubmitField('Заказать')

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
    x=request.form.get("myfilter_brand")
    x2=request.form.get("myfilter_aromat")

    if x or x2 is not None:
        if x:
            items=Products.query.filter(Products.brand.contains(x))
        if x2:
            items=Products.query.filter(Products.aromat.contains(x2))
        elif x and x2:
            items=Products.query.filter(Products.brand.contains(x)  | Products.aromat.contains(x2))

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
    if data is not None:
        items=Products.query.filter(Products.brand.contains(data) | Products.name.contains(data))

    cartId=request.form.get('item_to_cart')


    user_id=current_user.get_id()

    if   current_user.get_id() is None:
        u=User.query.filter(User.id>999999).order_by(User.id.desc()).first()
        if u:
            user_id=u.id+1
        else:
            user_id=1000000

  
    userID = request.cookies.get('userID')
    if userID is None:
        resp = make_response(redirect('/'))
        resp.set_cookie('userID', str(user_id))
        return resp
        
    if cartId is not None :
        item = db.session.query(Cart).filter(
            db.and_(Cart.userid == user_id, Cart.productid==cartId)).first()
        if item is None:
            product=Cart(userid=user_id,productid=cartId,quantity=1)
            db.session.add(product)
            db.session.commit()
            return redirect ('/')
        else:
            number=int(item.quantity+1)
            if number>4:
                return redirect('/')
            item.quantity=number
            db.session.commit()
            return redirect ('/')

    pages=items.paginate(page=page,per_page=24)

    colvo= items.count()
    cartProduct= Cart.query.filter_by(userid=user_id).count()
    brand=Products.query.distinct(Products.brand).group_by(Products.brand)
    aromat=Products.query.distinct(Products.aromat).group_by(Products.aromat)

    return render_template ('index.html',items=items,title='ParfumeLover',
    colvo=colvo,pages =pages,search=search,input=input1,brand=brand,admin=name,aromat=aromat,cartProduct=cartProduct)


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
        f1=form.img1.data
        f2=form.img2.data
        f3=form.img3.data
        fname1=request.form.get('img_name1')
        fname2=request.form.get('img_name2')
        fname3=request.form.get('img_name3')

        if f1:
            image = Image.open(f1)
            size=480,480
            image = image.resize(size)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], fname1))
        if f2:
            image = Image.open(f2)
            size=480,480
            image = image.resize(size)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], fname2))
        if f3:
            image = Image.open(f3)
            size=480,480
            image = image.resize(size)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], fname3))
        Authors='deft'
        content= request.form.get('content')
        characteristics= request.form.get('characteristics')
        userId=1
        if form.validate_on_submit():
            items = Products(brand=brand, Authors=Authors, name=name, price=price,
                            content=content,characteristics=characteristics, creationData=time,user_id=userId,
                            alt_txt=alt,img1=fname1,img2=fname2,img3=fname3,aromat=aromat)
            try:
                db.session.add(items)
                db.session.commit()
                return redirect('/')
            except:
                return redirect ('/')
    else:
        return redirect('/')

    return render_template('add.html', form=form,search=search,admin=name)


@app.route("/register", methods=['GET', 'POST'])
def register():
    name=Admin()
    search=SearchForm()
    if current_user.is_authenticated:
        redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        city=form.city.data
        otdel=form.otdel.data
        phone=form.phone.data
        user = User(username=form.username.data, email=form.email.data,
                    password=hashed_password,city=city,otdel=otdel,phone=phone)
        
        db.session.add(user)
        db.session.commit()
        flash('Спасибо за регистрацию','success')
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
            next_page = request.args.get('next')
            if next_page is None:
                next_page='/'
            return redirect (next_page)
        else:
            flash('Логин или пароль неверны','warning')
    return render_template('login.html', title='Вход', search=form, form2=form2,admin=name)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/remove', methods=['GET'])
@login_required
def remove():
    productId = request.args.get('id')
    amd= Cart.query.filter_by(productid=productId).first()
    art= Products.query.filter_by(id=productId).first()
    revs=Revs.query.filter_by(product_id=productId).first()
    if amd:
        db.session.delete(amd)
        db.session.commit()
    if revs:
        db.session.delete(revs)
        db.session.commit()
    if art:
        db.session.delete(art)
        db.session.commit()
        return redirect(url_for('index'))


@app.route('/show',methods=['GET', 'POST'])
def show():
    form=Reviews()
    name=Admin()
    search=SearchForm()
    revies=Reviews()
    nameId=request.args.get('id')
    content=Products.query.filter_by(id=nameId).first()
    img1=content.img1
    revs1=request.form.get('Rev')
    otziv=Revs.query.filter_by(product_id=nameId).all()
    user_id=current_user.get_id()
    if user_id is None:
        user_id=int(request.cookies.get('userID'))
    cartProduct= Cart.query.filter_by(userid=user_id).count()

    if revies.validate_on_submit():
        time = datetime.now()
        author=current_user.username
        rev= Revs(otziv=revs1,user_id=user_id,product_id=nameId,author=author,creationData=time,img=img1)
        try:
            db.session.add(rev)
            db.session.commit()
            flash('Отзыв добавлен','success')
            return redirect(url_for('show', id=nameId))
        except:
            redirect(url_for('index'))
    
    deletePost=request.form.get('deletePost')
    if deletePost is not None:
        rev=Revs.query.filter_by(id=deletePost).first()
        try:
            db.session.delete(rev)
            db.session.commit()
            flash('Отзыв удален','success')
            return redirect(url_for('show', id=nameId))
        except:
            redirect(url_for('index'))

    value=request.form.get('10')
    valuecount=5
    count=1
    addtocart=request.form.get('add_to_cart')
    if value is not None:
        if value=='5':
            valuecount=5
            count=1
        if value=='10':
            valuecount=10
            count=2
        if value=='15':
            valuecount=15
            count=3
        if value=='20':
            valuecount=20
            count=4
    if  addtocart:
            # if  current_user.is_anonymous:
            #     return redirect('/register')
            item = db.session.query(Cart).filter(
            db.and_(Cart.userid == user_id, Cart.productid==nameId)).first()
            if item is None:
                product=Cart(userid=user_id,productid=nameId,quantity=addtocart)
                db.session.add(product)
                db.session.commit()
                flash('Товар успешно добавлен в корзину','success')
                return redirect(url_for('show', id=nameId))
            else:
                item.quantity=addtocart
                db.session.commit()
                flash('Товар успешно добавлен в корзину','success')
                return redirect(url_for('show', id=nameId))

    return render_template('show.html', search=search,title=content.name,content=content,
    admin=name,form=form,x=otziv,cartProduct=cartProduct,count=count,valuecount=valuecount)


@app.route('/profile',methods=['GET', 'POST'])
def profile():
    search=SearchForm()
    name=Admin()
    user=current_user.get_id()
    profileUser=User.query.filter_by(id=user).first()
    otzivy=Revs.query.filter_by(user_id=user).all()
    idREv=request.form.get('delete')
    if idREv is not None:
        rev=Revs.query.filter_by(id=idREv).first()
        try:
            db.session.delete(rev)
            db.session.commit()
            return redirect ('/profile')
        except:
            return redirect ('/profile')

    return render_template ('profile.html',admin=name,search=search,user=profileUser,otzivy=otzivy)


@app.route('/cart',methods=['GET' ,'POST'])
def cart():
    search=SearchForm()
    name=Admin()
    time=datetime.now()
    user_id=current_user.get_id()
    if user_id is None:
        user_id=int(request.cookies.get('userID'))
    cart=Cart.query.filter_by(userid=user_id).all()
    cartProduct= Cart.query.filter_by(userid=user_id).count()
    value=request.form.get("VALUE")
    totalPrice=0
    discount=0
    for y in cart:
        totalPrice+=y.prods.price*y.quantity
    summ=totalPrice
    if totalPrice>1500:
        discount=5
        summ=int(summ-(summ/100*discount))
    value=request.form.get("VALUE")
    if value:
        a=value.split('/')
        idtovara=int(a[0])
        quantity=int(a[1])
        tovar=db.session.query(Cart).filter(
            db.and_(Cart.userid == user_id, Cart.productid==idtovara)).first()
        tovar.quantity=quantity
        db.session.commit()
        return redirect(url_for('cart'))

    oders=request.form.get('oders')
    if oders=='True':
            for i in cart:
                oder=Oders(productid=i.productid,rebate=discount,price=summ,user_id=user_id,creationData=time,quantity=i.quantity)
                try:
                    db.session.add(oder)
                    db.session.query(Cart).filter(Cart.userid==user_id).delete()
                    db.session.commit()
                    flash('Спасибо за покупку','success')
                    send_mail()
                    return redirect(url_for('cart'))
                except:
                    return redirect(url_for('cart'))
                
    deleteFromCart=request.form.get('deleteFromCart')
    if deleteFromCart is not None:
        deletecart=db.session.query(Cart).filter(
            db.and_(Cart.userid == user_id, Cart.productid==deleteFromCart)).first()
        try:
            db.session.delete(deletecart)
            db.session.commit()
            return redirect(url_for('cart'))
        except:
            return redirect(url_for('cart'))

    return render_template('cart.html',admin=name,search=search,items=cart,totalPrice=totalPrice,
    discount=discount,summ=summ,cartProduct=cartProduct,user_id=int(user_id))


def send_mail():
    id=int(current_user.get_id())
    if id is None:
        id=int(request.cookies.get('userID'))
    user=Oders.query.filter_by(user_id=id).order_by(Oders.id.desc()).first()
    with mail.connect() as conn:
        msg = Message("Заказ на сайте ParfumeLover",
        recipients=["zarj09@gmail.com",user.oder.email])
        msg.html =render_template('mail.html',user=user)
        conn.send(msg)


@app.route('/reset_password',methods=['GET', 'POST'])
def reset_password():
    search=SearchForm()
    name=Admin()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('Проверьте свою почту и следуйте инструкции','success')
        else:
            flash ('Пользователь с таким e-mail не найден','danger')
        return redirect(url_for('login'))
    return render_template('reset_password.html',admin=name,search=search,form=form)

def send_password_reset_email(user):
    token = user.get_reset_password_token()

    with mail.connect() as conn:
        msg = Message("[ParfumeLovwe] Сброс пароля",
        recipients=[user.email])
        msg.html =render_template('reset.html',user=user,token=token)
        conn.send(msg)

@app.route('/res_pass/<token>', methods=['GET', 'POST'])
def res_pass(token):
    search=SearchForm()
    name=Admin()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Пароль был изменен','success')
        return redirect(url_for('login'))
    return render_template('res_pass.html', form=form,admin=name,search=search)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    search=SearchForm()
    nameAdmin=Admin()
    name=nameAdmin.name
    art=Products.query.filter_by(id=request.args.get('id')).first()
    time = datetime.now()

    if current_user.username==name:
        form =ProductsForm()
        form.brand.data=art.brand
        form.name.data=art.name
        form.aromat.data=art.aromat
        form.content.data=art.content
        form.price.data=art.price
        form.alt_txt.data=art.alt_txt
        form.img_name1.data=art.img1
        form.img_name2.data=art.img2
        form.img_name3.data=art.img3
        userid=current_user.get_id()
        form.characteristics.data=art.characteristics
        f1=form.img1.data
        f2=form.img2.data
        f3=form.img3.data
        fname1=request.form.get('img_name1')
        fname2=request.form.get('img_name2')
        fname3=request.form.get('img_name3')

        if f1:
            image = Image.open(f1)
            size=480,480
            image = image.resize(size)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], fname1))
        if f2:
            image = Image.open(f2)
            size=480,480
            image = image.resize(size)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], fname2))
        if f3:
            image = Image.open(f3)
            size=480,480
            image = image.resize(size)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], fname3))

        if form.validate_on_submit():
            art.brand=request.form.get('brand')
            art.name=request.form.get('name')
            art.aromat=request.form.get('aromat')
            art.price=request.form.get('price')
            art.alt=request.form.get('alt_txt')
            art.img1=request.form.get('img_name1')
            art.img2=request.form.get('img_name2')
            art.img3=request.form.get('img_name3')
            art.characteristics=request.form.get('characteristics')
            art.content= request.form.get('content')
            art.Authors=name
            art.userId=userid
            art.creationData=time
            
            db.session.commit()
            return redirect('/')

    else:
        return redirect('/')

    return render_template('edit.html', form=form,search=search,admin=name,title='edit profile')


@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    search=SearchForm()
    name=Admin()
    form=EditProfileForm()
    iduser=current_user.get_id()
    profile=User.query.filter_by(id=iduser).first()
    if profile:
        form.username.data=profile.username
        form.email.data=profile.email
        form.city.data=profile.city
        form.otdel.data=profile.otdel
        form.phone.data=profile.phone
        if form.validate_on_submit():
            profile.username=request.form.get('username')
            x=request.form.get('username')
            profile.email=request.form.get('email')
            profile.city=request.form.get('city')
            profile.otdel=request.form.get('otdel')
            profile.phone=request.form.get('phone')
            db.session.commit()
            flash('Ваши изменения были сохранены','success')
            return redirect(url_for('profile'))

    return render_template('edit-profile.html', form=form,search=search,admin=name,title='edit profile')

@app.route('/resume')
def resume():
    return render_template('resume.html')
@app.route('/aboutUs')
def about():
    search=SearchForm()
    name=Admin()
    return render_template('aboutUs.html',search=search,admin=name,title='AboutUs')

@app.route('/quickorder', methods=['POST'])
def quick():
    name=request.form.get('quickordername')
    phone=request.form.get('quickorderphone')
    ID=request.form.get('quickID')
    time=datetime.now()
    PROD=Products.query.filter_by(id=ID).first()
    price=PROD.price
    nazv=PROD.name
    brand=PROD.brand
    if phone and PROD:
        with mail.connect() as conn:
            msg = Message("[ParfumeLover] Быстрый заказ",
            recipients=['zarj09@gmail.com'])
            msg.html =render_template('quickorder_email.html',name=name,phone=phone,time=time,
                                        price=price,nazv=nazv,brand=brand)
            conn.send(msg)
    else:
        return redirect('/')
    flash('Заказ принят в ближайшее время я с Вами свяжусь :)','success')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
#