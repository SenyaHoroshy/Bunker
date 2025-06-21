from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Cataclysm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(500), nullable=False)
    population = db.Column(db.Integer, nullable=False)
    destruction = db.Column(db.Integer, nullable=False)
    shelter_area = db.Column(db.Integer, nullable=False)
    time_in_shelter = db.Column(db.String(100), nullable=False)
    conditions = db.Column(db.String(200), nullable=False)
    equipment = db.Column(db.Text, nullable=False)
    supplies = db.Column(db.Text, nullable=False)
    inhabitants = db.Column(db.Text, nullable=False)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    profession = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    childfree = db.Column(db.String(100), nullable=False)
    physique = db.Column(db.String(100), nullable=False)
    health = db.Column(db.Text, nullable=False)
    traits = db.Column(db.Text, nullable=False)
    phobias = db.Column(db.Text, nullable=False)
    hobbies = db.Column(db.Text, nullable=False)
    additional_info = db.Column(db.Text, nullable=False)
    baggage = db.Column(db.Text, nullable=False)
    cards = db.Column(db.Text, nullable=False)
    is_revealed = db.Column(db.Boolean, default=False)