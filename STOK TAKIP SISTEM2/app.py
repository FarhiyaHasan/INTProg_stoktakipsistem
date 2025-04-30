from flask import Flask, render_template

app= Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashborad.html')
def dashborad():
   return render_template('dashborad.html')

@app.route('/hakkimizda.html')
def hakkimizda():
    return render_template('hakkimizda.html')

@app.route('/register.html')
def register():
     return render_template('register.html')

@app.route('/stok_duzenle.html')
def stok_duzenle():
     return render_template('stok_duzenle.html')


@app.route('/urun.html')
def urun():
     return render_template('urun.html')

if __name__ == '__main__':
    app.run(debug=True)









