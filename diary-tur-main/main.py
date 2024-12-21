from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)

# Varsayılan tema değişkeni
DEFAULT_THEME = 'default'



@app.route('/logout')
def logout():
    session.pop('user_id', None) 
    return redirect(url_for('login')) 

#aa
@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_card(id):
    if 'user_id' not in session:
        return redirect('/')
    
    card = Card.query.get(id)
    if card and card.user_id == session['user_id']:
        db.session.delete(card)
        db.session.commit()
    
    return redirect('/index')

#aa

# Kullanıcı tablosu
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'


# Kart tablosu
class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Her kart için benzersiz bir ID
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key olarak User'a bağlanır
    def __repr__(self):
        return f'<Card {self.title}>'


# Giriş sayfası
@app.route('/', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        form_login = request.form['email']
        form_password = request.form['password']

        user = User.query.filter_by(email=form_login).first()
        if user:
            if user.password == form_password:
                session['user_id'] = user.id
                return redirect('/index')
            else:
                error = 'Incorrect password'
        else:
            error = 'Email not found'

    return render_template('login.html', error=error)


# Kayıt olma sayfası
@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('registration.html', error="Email already registered.")

        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    return render_template('registration.html')

# Ana sayfa 
@app.route('/index')
def index():
    if 'user_id' not in session:
        return redirect('/')
 
    user_id = session['user_id']
    cards = Card.query.filter_by(user_id=user_id).order_by(Card.id).all() 
    return render_template('index.html', cards=cards, card = card)



# Kart detay sayfası
@app.route('/card/<int:id>')
def card(id):
    if 'user_id' not in session:
        return redirect('/')
    
    card = Card.query.get(id)

    if card.user_id != session['user_id']:
        return redirect('/index')

    return render_template('card.html', card=card)


# Kart oluşturma sayfası
@app.route('/create')
def create():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('create_card.html')


@app.route('/form_create', methods=['GET', 'POST'])
def form_create():
    if 'user_id' not in session:
        return redirect('/')
    if request.method == 'POST':
        title = request.form['title']
        subtitle = request.form['subtitle']
        text = request.form['text']
        user_id = session['user_id']  

        card = Card(title=title, subtitle=subtitle, text=text, user_id=user_id)  
        db.session.add(card)
        db.session.commit()
        return redirect('/index')
    return render_template('create_card.html')


if __name__ == "__main__":
    app.run(debug=True)
    