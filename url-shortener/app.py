from flask import Flask, request, redirect
import string
from random import choice
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os


app = Flask(__name__)


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class ShortUrls(db.Model):
    __tablename__ = 'url'

    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_id = db.Column(db.String(20), nullable=False, unique=True)
    created_at = db.Column(db.DateTime(), default=datetime.now(), nullable=False)

db.create_all()

@app.route('/', methods=['GET', 'POST'])
def url_shortener():
    if request.method == 'POST':
        if len(request.form) != 1 or 'u' not in request.form:
            return 'wrong input parameters!'
        if ShortUrls.query.filter(ShortUrls.original_url==request.form['u']).count() == 0:
            short_id = ''.join(choice(string.ascii_letters+string.digits) for _ in range(5))
            new_url = ShortUrls(original_url=request.form['u'], short_id=short_id)
            db.session.add(new_url)
            db.session.commit()
        else:
            short_id_obj = ShortUrls.query.filter(ShortUrls.original_url==request.form['u']).first()
            timedelta = datetime.now() - short_id_obj.created_at
            if timedelta.seconds > 3600:
                short_id = ''.join(choice(string.ascii_letters+string.digits) for _ in range(5))
                short_id_obj.short_id = short_id
                short_id_obj.created_at = datetime.now()
                db.session.commit()
            else:
                short_id = short_id_obj.short_id
        return f'http://localhost:80/{short_id}'


@app.route('/<short_id>')
def redirect_url(short_id):
    try:
        shorted_url_obj = ShortUrls.query.filter(ShortUrls.short_id==short_id).first()
        timedelta = datetime.now() - shorted_url_obj.created_at
        if timedelta.seconds > 3600:
            return 'url has been expired!'
        return redirect(shorted_url_obj.original_url)
    except AttributeError:
        return 'url does not exist!'


if __name__ == '__main__':
    app.run(debug=True)