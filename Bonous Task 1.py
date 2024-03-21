from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://username:password@localhost/codesnippets'
app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'

db = SQLAlchemy(app)
cache = Cache(app)

class CodeSnippet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    stdin = db.Column(db.String(100), nullable=False)
    code = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        username = request.form['username']
        language = request.form['language']
        stdin = request.form['stdin']
        code = request.form['code']

        new_snippet = CodeSnippet(username=username, language=language, stdin=stdin, code=code)
        db.session.add(new_snippet)
        db.session.commit()

        cache.delete('submissions')  # Clear cache after new submission
        return redirect(url_for('submissions'))

@app.route('/submissions')
def submissions():
    snippets = cache.get('submissions')
    if snippets is None:
        snippets = CodeSnippet.query.all()
        cache.set('submissions', snippets, timeout=60)  # Cache for 60 seconds
    return render_template('submissions.html', snippets=snippets)

if __name__ == '__main__':
    app.run(debug=True)
