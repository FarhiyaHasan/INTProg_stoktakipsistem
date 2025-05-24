from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gelistirme_anahtari' #sessıon bılgılerını tarayıcıda tutmak ıcın
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' #database ne adında olucak
db = SQLAlchemy(app)

login_manager = LoginManager(app)  #kullanıcı gereklı bır sayfa mevcut ıse: kısının gunluklerı gıbı
login_manager.login_view = 'login'  # gereklı gıurıs ıcın hangı rota kullanılsın? logın rotasına gıt

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # essiz id tanimi
    name = db.Column(db.String(100), nullable=False) #name=form ıcındekı degerı al ve gonder
    email = db.Column(db.String(100), unique=True, nullable=False) #email verısı
    password = db.Column(db.String(100), nullable=False) #password verısı


    urunler = db.relationship("Urun", back_populates="kullanici")  

class Urun(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # essiz id tanimi 
    ad = db.Column(db.String(100), nullable=False)
    kategori = db.Column(db.String(50), nullable=False)
    fiyat = db.Column(db.Float, nullable=False)
    stok = db.Column(db.Integer, nullable=False)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



    kullanici = db.relationship("User", back_populates="urunler")  


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/login', methods=['GET', 'POST'])  #logın form ıcınden 
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)    #kullanıcıyı gırıs yapmıs olarak ısaretle.
            return redirect(url_for('dashboard'))  #dashboard a dondur. dashboard ıcınde ılgılı yerde user gırırsı gosterır.
        flash('E-posta veya şifre hatalı!', 'danger')
    return render_template('login.html')

 
@app.route('/register', methods=['GET', 'POST']) #regıster form ıcınden 
def register():
    if request.method == 'POST': 
        email = request.form.get('email') #regıster formundan gelen emaıl
        password = request.form.get('password') #regıster formundan gelen password
        
        if User.query.filter_by(email=email).first():
            flash('Bu e-posta zaten kayıtlı!', 'danger') #sayfa mesajları dondurme
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        name = request.form.get('name') 
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success') #sayfa mesajları dondurme
        return redirect(url_for('login'))
    return render_template('register.html')



@app.route('/dashboard')
@login_required
def dashboard():
     urunler = Urun.query.filter_by(kullanici_id=current_user.id).order_by(Urun.id.desc()).all()

     return render_template('dashboard.html', urunler=urunler)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard/urun_ekle', methods=['GET', 'POST'])
@login_required
def urun_ekle():
    if request.method == 'POST':
        ad = request.form.get('ad')
        kategori = request.form.get('kategori')
        fiyat = request.form.get('fiyat')
        stok = request.form.get('stok')

        # Kullanıcı girişi kontrolü
        if current_user.is_authenticated:
            try:
                yeni_urun = Urun(
                    ad=ad,
                    kategori=kategori,
                    fiyat=float(fiyat),
                    stok=int(stok),
                    kullanici_id=current_user.id  # Ürünü ekleyen kullanıcı ID'si
                )
                db.session.add(yeni_urun)
                db.session.commit()
                flash('Ürün başarıyla eklendi!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                db.session.rollback()
                flash(f'Hata oluştu: {str(e)}', 'danger')
                return redirect(url_for('urun_ekle'))
        else:
            flash('Kullanıcı girişi yapılmamış!', 'danger')
            return redirect(url_for('login'))

    return render_template("urun_ekle.html")


#@app.route('/stok_duzenle')
#def stok_duzenle():
 #   return render_template('stok_duzenle.html')

      #duzletme islemler

@app.route('/urun_duzenle/<int:urun_id>', methods=['GET', 'POST'])
@login_required
def urun_duzenle(urun_id):
    # mevcut stok_duzenle içeriğini buraya taşı
    urun_kaydi = Urun.query.get_or_404(urun_id)

    if urun_kaydi.kullanici_id != current_user.id:
        flash("Bu ürünü düzenleme yetkiniz yok!", "danger")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        urun_kaydi.ad = request.form['ad']
        urun_kaydi.kategori = request.form['kategori']
        urun_kaydi.fiyat = float(request.form['fiyat'])
        urun_kaydi.stok = int(request.form['stok'])

        db.session.commit()
        flash("Ürün başarıyla güncellendi.", "success")
        return redirect(url_for('dashboard'))

    return render_template("urun_duzenle.html", urun=urun_kaydi)



    # silme islemler --------------

@app.route('/urun_sil/<int:urun_id>', methods=['POST'])
@login_required
def urun_sil(urun_id):
    urun_kaydi = Urun.query.get_or_404(urun_id)

    # Sadece ürünü ekleyen kullanıcı silebilir
    if urun_kaydi.kullanici_id != current_user.id:
        flash("Bu ürünü silme yetkiniz yok!", "danger")
        return redirect(url_for('dashboard'))

    db.session.delete(urun_kaydi)
    db.session.commit()
    flash("Ürün başarıyla silindi.", "success")
    return redirect(url_for('dashboard'))



@app.route('/urun')
def urun():
    return render_template('urun.html')

@app.route('/hakkimizda')
def hakkimizda():
    return render_template('hakkimizda.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)