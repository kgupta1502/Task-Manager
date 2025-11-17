from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:passw0rd@localhost:3308/app_db?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tasks = db.relationship("Task", backref="user", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at
        }

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "user_id": self.user_id
        }

@app.route('/')
def home():
    return jsonify({"message": "API is running successfully!"})

# CREATE USER
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()

    user = User(
        username=data['username'],
        email=data['email']
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created", "user": user.to_dict()}), 201


# GET ALL USERS
@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])


# GET SINGLE USER
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user.to_dict())


# UPDATE USER
@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)

    db.session.commit()
    return jsonify({"message": "User updated", "user": user.to_dict()})


# DELETE USER
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted"})

# CREATE TASK
@app.route('/task', methods=['POST'])
def add_task():
    data = request.get_json()

    task = Task(
        title=data['title'],
        description=data.get('description'),
        user_id=data['user_id']
    )

    db.session.add(task)
    db.session.commit()

    return jsonify({"message": "Task created", "task": task.to_dict()}), 201


# GET ALL TASKS
@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([t.to_dict() for t in tasks])


# UPDATE TASK
@app.route('/task/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.user_id = data.get('user_id', task.user_id)

    db.session.commit()
    return jsonify({"message": "Task updated", "task": task.to_dict()})


# DELETE TASK
@app.route('/task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"})

@app.route('/api/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([t.to_dict() for t in tasks])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
