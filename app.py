from flask import Flask, request, jsonify, redirect, url_for, render_template_string
from flask_sqlalchemy import SQLAlchemy



# Initializing Flask app
app = Flask(__name__)

# Configuring SQLAlchemy to use SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initializing  SQLAlchemy
db = SQLAlchemy(app)

# Defining the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Creating  tables before the first request
@app.before_first_request
def create_tables():
    db.create_all()

# Route to add a new user
@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    
    if not username or not email:
        return jsonify({'error': 'Missing username or email'}), 400

    new_user = User(username=username, email=email)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User added successfully'}), 201

# Route to get all users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return render_template_string('''
        <h1>Users</h1>
        <ul>
            {% for user in users %}
                <li>{{ user.username }} - {{ user.email }} <form method="POST" action="{{ url_for('delete_user', id=user.id) }}"><button type="submit">Delete</button></form></li>
            {% endfor %}
        </ul>
    ''', users=users)

# Route to get a specific user by ID
@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify({'id': user.id, 'username': user.username, 'email': user.email})

# Route to update a user's information
@app.route('/update_user/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    user = User.query.get_or_404(id)
    
    username = data.get('username')
    email = data.get('email')
    
    if username:
        user.username = username
    if email:
        user.email = email

    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

# Route to delete a user and redirect to the users list
@app.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('get_users'))

# Running  the Flask app
if __name__ == '__main__':
    app.run(debug=True)
