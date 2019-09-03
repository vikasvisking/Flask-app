import os
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
 
# database config
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy import or_
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "mysql+pymysql://test123:test123@localhost/testapp"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

class domains_csv(db.Model):
	domain = db.Column(db.Text)
	first_seen = db.Column(db.Integer)
	id = db.Column(db.Integer, primary_key= True, nullable = False)
	last_seen = db.Column(db.Integer)
	etld = db.Column(db.Text)
	time_date_imported = db.Column(db.DateTime)

class Search (db.Model):
	id = db.Column(db.Integer, primary_key= True, nullable = False)
	keyword = db.Column(db.String(100))
	domain = db.Column(INTEGER(unsigned=True), db.ForeignKey('domains_csv.id'))
	result = db.relationship('domains_csv', backref='search')

	def __repr__(self):
		return "<Searched Keyword : {}>".format(self.keyword)

@app.route('/', methods = ['GET'])
def home():
	return render_template('test-app.html')

@app.route('/add', methods = ['GET','POST'])
def add():
	if request.form:
		keyword = (request.form.get('search')).strip()
		final = "%"+keyword+"%"
		searches = domains_csv.query.filter(domains_csv.domain.like(final)).all()
		newkeyword = keyword
		search_list = []
		for search in searches:
			searchobj = Search(keyword = keyword,domain = search.id)
			db.session.add(searchobj)
			db.session.commit()
			search_list.append(searchobj)
		return render_template('test-app.html', searches = search_list)

# @app.route('/update', methods = ['POST'])
# def update():
# 	newkey = request.form.get('newkey')
# 	searchid = request.form.get('searchid')
# 	search = Search.query.filter_by(id = searchid).first()
# 	search.keyword = newkey
# 	db.session.commit()
# 	search_list = Search.query.filter_by(keyword = search.keyword)

# 	return render_template('test-app.html', searches = search_list)

@app.route('/delete/<search_id>', methods = ['GET'])
def delete(search_id):
	searchid = search_id
	search = Search.query.filter_by(id = searchid).first()
	db.session.delete(search)
	db.session.commit()
	search_list = Search.query.filter_by(keyword = search.keyword)
	return render_template('test-app.html', searches = search_list)

if __name__ == "__main__":
	# manager.run()
	app.run(debug = True)