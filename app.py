from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from models import db, Cataclysm, Player
import os
from init_db import initialize_database

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bunker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Создаем БД при первом запуске
if not os.path.exists('instance/bunker.db'):
    with app.app_context():
        db.create_all()
        initialize_database()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        # Здесь можно добавить обработку настроек игры
        return redirect(url_for('index'))
    return render_template('setup.html')

@app.route('/player/<int:player_id>')
def player(player_id):
    return render_template('player.html', player_id=player_id)

# API endpoints
@app.route('/api/cataclysm')
def get_cataclysm():
    cataclysm = Cataclysm.query.first()
    return jsonify({
        'description': cataclysm.description,
        'population': cataclysm.population,
        'destruction': cataclysm.destruction,
        'shelter_area': cataclysm.shelter_area,
        'time_in_shelter': cataclysm.time_in_shelter,
        'conditions': cataclysm.conditions,
        'equipment': cataclysm.equipment.split('|'),
        'supplies': cataclysm.supplies.split('|'),
        'inhabitants': cataclysm.inhabitants.split('|')
    })

@app.route('/api/player/<int:player_id>')
def get_player(player_id):
    player = Player.query.get_or_404(player_id)
    return jsonify({
        'name': player.name,
        'profession': player.profession,
        'gender': player.gender,
        'age': player.age,
        'childfree': player.childfree,
        'physique': player.physique,
        'health': player.health.split('|'),
        'traits': player.traits.split('|'),
        'phobias': player.phobias.split('|'),
        'hobbies': player.hobbies.split('|'),
        'additional_info': player.additional_info.split('|'),
        'baggage': player.baggage.split('|'),
        'cards': player.cards.split('|'),
        'is_revealed': player.is_revealed
    })

@app.route('/api/players')
def get_players():
    players = Player.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name if p.is_revealed else 'Скрыто',
        'is_revealed': p.is_revealed
    } for p in players])

@app.route('/api/reveal/<int:player_id>', methods=['POST'])
def reveal_player(player_id):
    player = Player.query.get_or_404(player_id)
    player.is_revealed = True
    db.session.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)