from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json
from flask_login import UserMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

# Modelin (aynı şekilde)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Urun(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # essiz id tanimi 
    ad = db.Column(db.String(100), nullable=False)
    kategori = db.Column(db.String(50), nullable=False)
    fiyat = db.Column(db.Float, nullable=False)
    stok = db.Column(db.Integer, nullable=False)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('urunler', lazy=True))

    # json aktarma fonksiyonu   najajahhsdasdj

def export_urunler_to_json():
    with app.app_context():
        urunler = Urun.query.all()
        data =[]
        for urun in urunler:
            data.append({
                'id': urun.id,
                'ad': urun.ad,
                'kategori': urun.kategori,
                'fiyat': urun.fiyat,
                'stok': urun.stok,
                'kullanici_id': urun.kullanici_id,
                'kullanici_adi': urun.user.name if urun.user else None
            })
            with open('urunler.json', 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

        print("urunler başarıyla urunler.json dosyasına kaydedildi!")


if __name__ == '__main__':
    export_urunler_to_json()