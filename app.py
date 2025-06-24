from flask import Flask, render_template, request, jsonify, redirect, url_for, current_app
from flask_sqlalchemy import SQLAlchemy
from models import db, Cataclysm, Player
import os
import socket
from init_db import initialize_database
import threading
from flask import session as flask_session
from models import GameSession, PlayerSession

app = Flask(__name__)
app.config['SECRET_KEY'] = 'FhLHNybSzOK4PRnr0gpd'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bunker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def get_local_ip():
    """Получаем локальный IP адрес для подключения других устройств"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # не требуется реальное подключение
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def print_network_info():
    """Выводим информацию для подключения в консоль"""
    local_ip = get_local_ip()
    print("\n" + "="*50)
    print(f"Сервер запущен. Для подключения:")
    print(f"На этом устройстве: http://localhost:5000")
    print(f"На других устройствах в локальной сети: http://{local_ip}:5000")
    print("="*50 + "\n")

# Создаем БД при первом запуске
db_file = os.path.join(app.instance_path, 'bunker.db')
if not os.path.exists(db_file):
    with app.app_context():
        db.create_all()
        initialize_database()

@app.before_request
def check_session():
    if request.remote_addr == '127.0.0.1' and not GameSession.query.filter_by(admin_ip='127.0.0.1').first():
        # Создаем новую сессию, если администратор первый раз заходит
        new_session = GameSession(admin_ip='127.0.0.1')
        db.session.add(new_session)
        db.session.commit()

@app.route('/')
def index():
    current_session = GameSession.query.first()
    if not current_session:
        return redirect(url_for('register'))
    
    # Для администратора - перенаправляем в настройки
    if request.remote_addr == '127.0.0.1':
        return redirect(url_for('setup'))
    
    # Для обычных игроков проверяем их сессию
    player_session = PlayerSession.query.filter_by(
        ip_address=request.remote_addr,
        session_id=current_session.id
    ).first()
    
    if player_session:
        return redirect(url_for('player', player_id=player_session.player_id))
    else:
        return redirect(url_for('register'))

@app.route('/setup')
def setup():
    games = [d for d in os.listdir('games') if os.path.isdir(os.path.join('games', d))]
    return render_template('setup.html', games=games)

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
        'cards': player.cards.split('|')
    })

@app.route('/api/players')
def get_players():
    players = Player.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name
    } for p in players])

@app.route('/api/reveal/<int:player_id>', methods=['POST'])
def reveal_player(player_id):
    player = Player.query.get_or_404(player_id)
    db.session.commit()
    return jsonify({'success': True})

def run_with_info():
    """Запускаем сервер с выводом информации о подключении"""
    #print_network_info()
    app.run(host='0.0.0.0', port=5000, debug=True)

@app.route('/api/server_info')
def get_server_info():
    return jsonify({
        'ip': get_local_ip()
    })

@app.route('/register', methods=['GET', 'POST'])
def register():
    current_session = GameSession.query.first()
    
    if request.method == 'POST':
        player_id = request.form.get('player_id')
        player_name = request.form.get('player_name')
        
        # Проверяем, не занят ли уже этот игрок
        existing = PlayerSession.query.filter_by(
            session_id=current_session.id,
            player_id=player_id
        ).first()
        
        if existing:
            return render_template('register.html', 
                                error='Этот игрок уже занят!',
                                players=Player.query.all())
        
        # Создаем запись о игроке в сессии
        new_player_session = PlayerSession(
            session_id=current_session.id,
            player_id=player_id,
            player_name=player_name,
            ip_address=request.remote_addr,
            is_admin=False  # Все новые игроки по умолчанию не админы
        )
        db.session.add(new_player_session)
        db.session.commit()
        
        flask_session['player_id'] = player_id
        flask_session['player_name'] = player_name
        flask_session['is_admin'] = False  # Явно указываем, что это не админ
        
        return redirect(url_for('player', player_id=player_id))  # Всегда перенаправляем на страницу игрока
    
    return render_template('register.html', 
                         players=Player.query.all(),
                         error=None)

@app.route('/reset', methods=['POST'])
def reset_game():
    if request.remote_addr != '127.0.0.1':
        return jsonify({'error': 'Только администратор может сбросить игру!'}), 403
    
    # Удаляем все записи о текущей сессии
    with app.app_context():
        PlayerSession.query.delete()
        GameSession.query.delete()
        db.session.commit()
        
        # Инициализируем заново
        initialize_database()
    
    return jsonify({'success': True})

@app.route('/api/check_access', methods=['POST'])
def check_access():
    data = request.get_json()
    player_id = data['player_id']
    
    current_session = GameSession.query.first()
    if not current_session:
        return jsonify({'has_access': False})
    
    player_session = PlayerSession.query.filter_by(
        ip_address=request.remote_addr,
        session_id=current_session.id,
        player_id=player_id
    ).first()
    
    return jsonify({'has_access': bool(player_session)})

@app.route('/load_game', methods=['POST'])
def load_game():
    if request.remote_addr != '127.0.0.1':
        return jsonify({'error': 'Только администратор может загружать игру!'}), 403
    
    data = request.get_json()
    game_folder = data['game']
    
    try:
        from parser import parse_game_data
        player_count = parse_game_data(game_folder)
        app.logger.info(f"Успешно загружена игра '{game_folder}' с {player_count} игроками")
        return jsonify({'success': True, 'players': player_count})
    except Exception as e:
        app.logger.error(f"Ошибка загрузки игры: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/all_players')
def all_players():
    players = Player.query.all()
    is_admin = request.remote_addr == '127.0.0.1'
    
    prepared_players = []
    for player in players:
        # Подготавливаем поля-массивы
        def prepare_list_field(field_value, revealed_indices):
            items = field_value.split('|') if field_value else []
            revealed = revealed_indices.split(',') if revealed_indices else []
            return [{
                'value': item,
                'revealed': str(idx) in revealed
            } for idx, item in enumerate(items)]
        
        prepared_players.append({
            'id': player.id,
            'name': player.name,
            'name_revealed': player.name_revealed,
            'profession': player.profession,
            'profession_revealed': player.profession_revealed,
            'gender': player.gender,
            'gender_revealed': player.gender_revealed,
            'age': player.age,
            'age_revealed': player.age_revealed,
            'childfree': player.childfree,
            'childfree_revealed': player.childfree_revealed,
            'physique': player.physique,
            'physique_revealed': player.physique_revealed,
            
            # Поля-массивы
            'health_items': prepare_list_field(player.health, player.health_revealed),
            'traits_items': prepare_list_field(player.traits, player.traits_revealed),
            'phobias_items': prepare_list_field(player.phobias, player.phobias_revealed),
            'hobbies_items': prepare_list_field(player.hobbies, player.hobbies_revealed),
            'additional_info_items': prepare_list_field(player.additional_info, player.additional_info_revealed),
            'baggage_items': prepare_list_field(player.baggage, player.baggage_revealed),
            'cards_items': prepare_list_field(player.cards, player.cards_revealed),
        })
    
    return render_template('all_players.html', 
                         players=prepared_players,
                         is_admin=is_admin)

@app.route('/api/reveal', methods=['POST'])
def reveal_field():
    if request.remote_addr != '127.0.0.1':
        return jsonify({'error': 'Только администратор может открывать характеристики!'}), 403
    
    data = request.get_json()
    player = Player.query.get_or_404(data['player_id'])
    
    # Обрабатываем обычные поля
    simple_fields = ['name', 'profession', 'gender', 'age', 'childfree', 'physique']
    if data['field'] in simple_fields:
        setattr(player, f"{data['field']}_revealed", True)
    else:
        # Обрабатываем поля-массивы
        revealed = getattr(player, f"{data['field']}_revealed")
        if not revealed:
            revealed = str(data['index'])
        else:
            revealed_indices = revealed.split(',')
            if str(data['index']) not in revealed_indices:
                revealed_indices.append(str(data['index']))
                revealed = ','.join(revealed_indices)
        
        setattr(player, f"{data['field']}_revealed", revealed)
    
    db.session.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    run_with_info()