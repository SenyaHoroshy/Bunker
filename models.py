from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class PlayerSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('game_session.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    player_name = db.Column(db.String(100))
    ip_address = db.Column(db.String(50))
    is_admin = db.Column(db.Boolean, default=False)

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
    
    # Поля, которые хранят положение элементов (открыто/закрыто другим игрокам)
    name_revealed = db.Column(db.Boolean, default=False)
    profession_revealed = db.Column(db.Boolean, default=False)
    gender_revealed = db.Column(db.Boolean, default=False)
    age_revealed = db.Column(db.Boolean, default=False)
    childfree_revealed = db.Column(db.Boolean, default=False)
    physique_revealed = db.Column(db.Boolean, default=False)
    
    # Для массивов
    health_revealed = db.Column(db.String(255), default="")
    traits_revealed = db.Column(db.String(255), default="")
    phobias_revealed = db.Column(db.String(255), default="")
    hobbies_revealed = db.Column(db.String(255), default="")
    additional_info_revealed = db.Column(db.String(255), default="")
    baggage_revealed = db.Column(db.String(255), default="")
    cards_revealed = db.Column(db.String(255), default="")

class GameSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(db.Boolean, default=True)
    admin_ip = db.Column(db.String(50), default='127.0.0.1')