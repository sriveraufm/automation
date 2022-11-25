# flask imports
from flask import Flask, request, jsonify, make_response, current_app
from flask_sqlalchemy import SQLAlchemy
import uuid # for public id
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
from flask_cors import CORS

# db = SQLAlchemy(app)
# creates Flask object
app = Flask(__name__)
# configuration
# NEVER HARDCODE YOUR CONFIGURATION IN YOUR CODE
# INSTEAD CREATE A .env FILE AND STORE IN IT
app.config['SECRET_KEY'] = 'your secret key'
# database name
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# creates SQLALCHEMY object
db = SQLAlchemy(app)

# Database ORMs
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(50), unique = True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(70), unique = True)
    password = db.Column(db.String(80))

class Tareas(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	email = db.Column(db.String(70))
	title = db.Column(db.String(100))
	description = db.Column(db.String(100))
	status = db.Column(db.Boolean, default=False, nullable=False)

db.create_all()
# this route sends back list of users
@app.route('/user', methods =['GET'])
def get_all_users(current_user):
	# querying the database
	# for all the entries in it
	users = User.query.all()
	# converting the query objects
	# to list of jsons
	output = []
	for user in users:
		# appending the user data json
		# to the response list
		output.append({
			'public_id': user.public_id,
			'name' : user.name,
			'email' : user.email
		})

	return  make_response(jsonify({'users': output}),200)

# route for logging user in
@app.route('/login', methods =['POST'])
def login():
	# creates dictionary of form data
	# auth = request.form
	auth =  request.get_json(force=True)
	print(auth)
	if not auth or not auth.get('email') or not auth.get('password'):
		# returns 401 if any email or / and password is missing
		return make_response(
			'Could not verify',
			401,
			{'WWW-Authenticate' : 'Basic realm ="Login required !!"'}
		)

	user = User.query\
		.filter_by(email = auth.get('email'))\
		.first()

	if not user:
		# returns 401 if user does not exist
		return make_response(
			'Could not verify',
			401,
			{'WWW-Authenticate' : 'Basic realm ="User does not exist !!"'}
		)

	if check_password_hash(user.password, auth.get('password')):
		return make_response('login', 201)#token.decode('UTF-8')
	# returns 403 if password is wrong
	return make_response(
		'Could not verify',
		403,
		{'WWW-Authenticate' : 'Basic realm ="Wrong Password !!"'}
	)


# route for logging user in
@app.route('/change_password', methods =['POST'])
def change_password():
	# creates dictionary of form data
	# auth = request.form
	auth =  request.get_json(force=True)
	print(auth)
	if not auth or not auth.get('email') or not auth.get('password'):
		# returns 401 if any email or / and password is missing
		return make_response(
			'Could not verify',
			401,
			{'WWW-Authenticate' : 'Basic realm ="Login required !!"'}
		)

	user = User.query\
		.filter_by(email = auth.get('email'))\
		.first()

	if not user:
		# returns 401 if user does not exist
		return make_response(
			'Could not verify',
			401,
			{'WWW-Authenticate' : 'Basic realm ="User does not exist !!"'}
		)

	if check_password_hash(user.password, auth.get('password')):
		# generates the JWT Token
		# token = jwt.encode({
		# 	'public_id': user.public_id,
		# 	'exp' : datetime.utcnow() + timedelta(minutes = 30)
		# }, app.config['SECRET_KEY'])
		# print(token)
		user.password = generate_password_hash(auth.get('new_password'))
		db.session.commit()
		return make_response(jsonify({'state' : 'Password succesfully changed' }), 201)#token.decode('UTF-8')
	# returns 403 if password is wrong
	return make_response(
		'Could not verify',
		403,
		{'WWW-Authenticate' : 'Basic realm ="Wrong Password !!"'}
	)


# route for logging user in
@app.route('/delete_user', methods =['DELETE'])
def delete_user():
	# creates dictionary of form data
	# auth = request.form
	auth =  request.get_json(force=True)
	print(auth)
	if not auth or not auth.get('email') or not auth.get('password'):
		# returns 401 if any email or / and password is missing
		return make_response(
			'Could not verify',
			401,
			{'WWW-Authenticate' : 'Basic realm ="Login required !!"'}
		)

	user = User.query\
		.filter_by(email = auth.get('email'))\
		.first()

	if not user:
		# returns 401 if user does not exist
		return make_response(
			'Could not verify',
			401,
			{'WWW-Authenticate' : 'Basic realm ="User does not exist !!"'}
		)

	if check_password_hash(user.password, auth.get('password')):
		# generates the JWT Token
		# token = jwt.encode({
		# 	'public_id': user.public_id,
		# 	'exp' : datetime.utcnow() + timedelta(minutes = 30)
		# }, app.config['SECRET_KEY'])
		# print(token)
		user = User.query.filter_by(email = auth.get('email')).delete()
		tareas = Tareas.query.filter_by(email = auth.get('email')).delete()
		db.session.commit()
		return make_response(jsonify({'state' : 'User succesfully deleted' }), 200)#token.decode('UTF-8')
	# returns 403 if password is wrong
	return make_response(
		'Could not verify',
		403,
		{'WWW-Authenticate' : 'Basic realm ="Wrong Password !!"'}
	)

# signup route
@app.route('/signup', methods =['POST'])
def signup():
	# creates a dictionary of the form data
	# data = request.form
	data = request.get_json(force=True)
	# gets name, email and password
	name, email = data.get('name'), data.get('email')
	password = data.get('password')

	# checking for existing user
	user = User.query\
		.filter_by(email = email)\
		.first()
	if not user:
		# database ORM object
		user = User(
			public_id = str(uuid.uuid4()),
			name = name,
			email = email,
			password = generate_password_hash(password)
		)
		# insert user
		db.session.add(user)
		db.session.commit()

		return make_response('Successfully registered.', 201)
	else:
		# returns 202 if user already exists
		return make_response('User already exists. Please Log in.', 202)


# signup route
@app.route('/add_tarea', methods =['POST'])
def add_tarea():
	# creates a dictionary of the form data
	# data = request.form
	data = request.get_json(force=True)
	# gets name, email and password
	# name, email = data.get('name'), data.get('email')
	# password = data.get('password')
	user = User.query\
		.filter_by(email = data.get('email'))\
		.first()
	if user:
	# checking for existing user
		tarea = Tareas(
			email = data.get('email'),
			title = data.get('title'),
			description = data.get('description'),
			status = False

		)
		db.session.add(tarea)
		db.session.commit()
		return make_response('Successfully added', 201)
	else:
		return make_response('User not found',428)


# signup route	
@app.route('/get_tareas', methods =['GET'])
def get_tareas():
	# creates a dictionary of the form data
	# data = request.form
	data = request.get_json(force=True)
	# gets name, email and password
	# name, email = data.get('name'), data.get('email')
	# password = data.get('password')
	user_tareas = Tareas.query.filter_by(email = data.get('email')).all()
	if user_tareas:
		output = []
		for tarea in user_tareas:
			# appending the user data json
			# to the response list
			output.append({
				'id' : tarea.id,
				'title': tarea.title,
				'description' : tarea.description,
				'status' : tarea.status
			})

		return make_response(jsonify({'tareas': output}), 200)
	else:
		return make_response('No content found with given parameters',428)

# signup route
@app.route('/get_uncompleted', methods =['GET'])
def get_uncompleted():
	# creates a dictionary of the form data
	# data = request.form
	data = request.get_json(force=True)
	# gets name, email and password
	# name, email = data.get('name'), data.get('email')
	# password = data.get('password')
	user_tareas = Tareas.query.filter_by(email = data.get('email'), status = False).all()
	if user_tareas:
		output = []
		for tarea in user_tareas:
			# appending the user data json
			# to the response list
			output.append({
				'id' : tarea.id,
				'title': tarea.title,
				'description' : tarea.description,
				'status' : tarea.status
			})
		return make_response(jsonify({'tareas': output}),200)
	else:
		return make_response('No content found with given parameters',428)

# signup route
@app.route('/get_completed', methods =['GET'])
def get_completed():
	# creates a dictionary of the form data
	# data = request.form
	data = request.get_json(force=False)
	# gets name, email and password
	# name, email = data.get('name'), data.get('email')
	# password = data.get('password')
	user_tareas = Tareas.query.filter_by(email = data.get('email'), status = True).all()
	if user_tareas:
		output = []
		for tarea in user_tareas:
			# appending the user data json
			# to the response list
			output.append({
				'id' : tarea.id,
				'title': tarea.title,
				'description' : tarea.description,
				'status' : tarea.status
			})
		return make_response(jsonify({'tareas': output}),200)
	else:
		return make_response('No content found with given parameters',428)

@app.route('/mark_completed', methods =['POST'])
def mark_completed():
	# creates a dictionary of the form data
	# data = request.form
	data = request.get_json(force=False)
	# gets name, email and password
	# name, email = data.get('name'), data.get('email')
	# password = data.get('password')
	user_tareas = Tareas.query.filter_by(id = data.get('id')).first()
	if user_tareas:
		user_tareas.status = True
		db.session.commit()
		return make_response(jsonify({'State': 'Completed!'}),200)
	else:
		return make_response('No content found with given parameters',428)

@app.route('/mark_uncompleted', methods =['POST'])
def mark_uncompleted():
	# creates a dictionary of the form data
	# data = request.form
	data = request.get_json(force=False)
	# gets name, email and password
	# name, email = data.get('name'), data.get('email')
	# password = data.get('password')
	user_tareas = Tareas.query.filter_by(id = data.get('id')).first()
	if user_tareas:
		user_tareas.status = False
		db.session.commit()
		return make_response(jsonify({'State': 'Uncompleted.'}), 200)
	else:
		return make_response('No content found with given parameters',428)



@app.route('/delete_tarea', methods =['DELETE'])
def delete_tarea():
	# creates a dictionary of the form data
	# data = request.form
	data = request.get_json(force=False)
	# gets name, email and password
	# name, email = data.get('name'), data.get('email')
	# password = data.get('password')
	user_tareas = Tareas.query.filter_by(id = data.get('id')).first()
	if user_tareas:
		Tareas.query.filter_by(id = data.get('id')).delete()
		db.session.commit()
		return make_response(jsonify({'State': 'Deleted.'}),200)
	else:
		return make_response('No content found with given parameters',428)


@app.route('/modify_description', methods =['POST'])
def modify_description():
	# creates a dictionary of the form data
	# data = request.form
	data = request.get_json(force=False)
	# gets name, email and password
	# name, email = data.get('name'), data.get('email')
	# password = data.get('password')
	user_tareas = Tareas.query.filter_by(id = data.get('id')).first()
	if user_tareas:
		user_tareas.description = data.get('new_description')
		db.session.commit()
		return make_response(jsonify({'State': 'Description changed.'}),200)
	else:
		return make_response('No content found with given parameters',428)

	
@app.route('/modify_title', methods =['POST'])
def modify_tit():
	# creates a dictionary of the form data
	# data = request.form
	data = request.get_json(force=False)
	# gets name, email and password
	# name, email = data.get('name'), data.get('email')
	# password = data.get('password')
	user_tareas = Tareas.query.filter_by(id = data.get('id')).first()
	if user_tareas:
		user_tareas.title = data.get('new_title')
		db.session.commit()
		return make_response(jsonify({'State': 'Title changed.'}),200)
	else:
		return make_response('No content found with given parameters',428)

if __name__ == "__main__":
	# setting debug to True enables hot reload
	# and also provides a debugger shell
	# if you hit an error while running the server
	app.run(debug = True)
