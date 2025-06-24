import os
import re
from flask import current_app
from models import db, Cataclysm, Player

def parse_game_data(game_folder):
    """Парсит данные игры из указанной папки и обновляет базу данных"""
    try:
        game_path = os.path.join('games', game_folder)
        
        # Проверяем, что папка существует
        if not os.path.exists(game_path):
            raise ValueError(f"Папка игры '{game_folder}' не найдена в директории 'games'")
        
        # Очищаем текущие данные
        try:
            db.session.query(Player).delete()
            db.session.query(Cataclysm).delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise
        
        # Ищем все файлы игроков
        player_files = sorted(
            [f for f in os.listdir(game_path) 
             if re.match(r'Player \d+\.txt$', f)],
            key=lambda x: int(re.search(r'\d+', x).group())
        )
        
        if not player_files:
            raise ValueError(f"В папке '{game_folder}' не найдены файлы игроков (ожидаются файлы вида Player1.txt, Player2.txt...)")
        
        # Парсим данные из первого файла игрока (для катаклизма и убежища)
        first_player_path = os.path.join(game_path, player_files[0])
        with open(first_player_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Парсим данные о катаклизме и убежище
        cataclysm_data = parse_cataclysm(content)
        shelter_data = parse_shelter(content)
        
        # Создаем запись о катаклизме
        cataclysm = Cataclysm(
            description=cataclysm_data['description'],
            population=cataclysm_data['population'],
            destruction=cataclysm_data['destruction'],
            shelter_area=shelter_data['area'],
            time_in_shelter=shelter_data['time'],
            conditions=shelter_data['conditions'],
            equipment='|'.join(shelter_data['equipment']),
            supplies='|'.join(shelter_data['supplies']),
            inhabitants='|'.join(shelter_data['inhabitants'])
        )
        db.session.add(cataclysm)
        
        # Парсим данные всех игроков
        for player_file in player_files:
            player_path = os.path.join(game_path, player_file)
            with open(player_path, 'r', encoding='utf-8') as file:
                content = file.read()
                player_data = parse_player(content)
                
                player = Player(
                    name=player_data['name'],
                    profession=player_data['profession'],
                    gender=player_data['gender'],
                    age=player_data['age'],
                    childfree=player_data['childfree'],
                    physique=player_data['physique'],
                    health='|'.join(player_data['health']),
                    traits='|'.join(player_data['traits']),
                    phobias='|'.join(player_data['phobias']),
                    hobbies='|'.join(player_data['hobbies']),
                    additional_info='|'.join(player_data['additional_info']),
                    baggage='|'.join(player_data['baggage']),
                    cards='|'.join(player_data['cards']),
                    name_revealed=False,
                    profession_revealed=False,
                    gender_revealed=False,
                    age_revealed=False,
                    childfree_revealed=False,
                    physique_revealed=False,
                    health_revealed="",
                    traits_revealed="",
                    phobias_revealed="",
                    hobbies_revealed="",
                    additional_info_revealed="",
                    baggage_revealed="",
                    cards_revealed=""
                )
                db.session.add(player)
        
        db.session.commit()
        return len(player_files)
    
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Ошибка при парсинге игры: {str(e)}")

def parse_cataclysm(content):
    """Парсит данные о катаклизме"""
    start = content.find('Катаклизм')
    end = content.find('-----------Убежище-------------')
    
    if start == -1 or end == -1:
        raise ValueError("Неверный формат файла: отсутствует информация о катаклизме")
    
    cataclysm_section = content[start:end]
    
    # Извлекаем описание
    description_start = cataclysm_section.find('Катаклизм') + 11
    description_end = cataclysm_section.find('👥')
    description = cataclysm_section[description_start:description_end].strip()
    
    # Извлекаем население
    population_start = cataclysm_section.find('👥') + 30
    population_end = cataclysm_section.find('💥')
    population = int(cataclysm_section[population_start:population_end].strip().replace('%', ''))
    
    # Извлекаем разрушения
    destruction_start = cataclysm_section.find('💥') + 28
    destruction_end = cataclysm_section.find('🏡')
    destruction = int(cataclysm_section[destruction_start:destruction_end].strip().replace('%', ''))
    
    return {
        'description': description,
        'population': population,
        'destruction': destruction
    }

def parse_shelter(content):
    """Парсит данные об убежище"""
    start = content.find('-----------Убежище-------------')
    end = content.find('-----------Ваш персонаж--------')
    
    if start == -1 or end == -1:
        raise ValueError("Неверный формат файла: отсутствует информация об убежище")
    
    shelter_section = content[start:end]
    
    # Извлекаем площадь
    area_start = shelter_section.find('🏡') + 18
    area_end = shelter_section.find('⌛')
    area = int(shelter_section[area_start:area_end].strip().split()[0])
    
    # Извлекаем время
    time_start = shelter_section.find('⌛') + 29
    time_end = shelter_section.find('🔓')
    time = shelter_section[time_start:time_end].strip()
    
    # Извлекаем условия
    conditions_start = shelter_section.find('🔓') + 2
    conditions_end = shelter_section.find('🔧')
    conditions = shelter_section[conditions_start:conditions_end].strip()
    
    # Извлекаем оборудование
    equipment = []
    equip_start = shelter_section.find('🔧') + 24
    next_equip = shelter_section.find('🔧', equip_start)
    next_supply = shelter_section.find('📦')
    
    while next_equip != -1 and next_equip < next_supply:
        equipment.append(shelter_section[equip_start:next_equip].strip())
        equip_start = next_equip + 24
        next_equip = shelter_section.find('🔧', equip_start)
    
    equipment.append(shelter_section[equip_start:next_supply].strip())
    
    # Извлекаем припасы
    supplies = []
    supply_start = shelter_section.find('📦') + 17
    next_supply = shelter_section.find('📦', supply_start)
    next_inhab = shelter_section.find('♻')
    
    while next_supply != -1 and next_supply < next_inhab:
        supplies.append(shelter_section[supply_start:next_supply].strip())
        supply_start = next_supply + 17
        next_supply = shelter_section.find('📦', supply_start)
    
    supplies.append(shelter_section[supply_start:next_inhab].strip())
    
    # Извлекаем обитателей
    inhabitants = []
    inhab_start = shelter_section.find('♻') + 18
    next_inhab = shelter_section.find('♻', inhab_start)
    
    while next_inhab != -1 and next_inhab < end:
        inhabitants.append(shelter_section[inhab_start:next_inhab].strip())
        inhab_start = next_inhab + 18
        next_inhab = shelter_section.find('♻', inhab_start)
    
    inhabitants.append(shelter_section[inhab_start:end].strip())
    
    return {
        'area': area,
        'time': time,
        'conditions': conditions,
        'equipment': equipment,
        'supplies': supplies,
        'inhabitants': inhabitants
    }

def parse_player(content):
    """Парсит данные игрока"""
    start = content.find('-----------Ваш персонаж--------')
    if start == -1:
        raise ValueError("Неверный формат файла: отсутствует информация о персонаже")
    
    player_section = content[start:]
    
    # Извлекаем имя
    name_start = player_section.find('🪪') + 14
    name_end = player_section.find('💼')
    name = player_section[name_start:name_end].strip()
    
    # Извлекаем профессию
    profession_start = player_section.find('💼') + 12
    profession_end = player_section.find('👥')
    profession = player_section[profession_start:profession_end].strip()
    
    # Извлекаем пол
    gender_start = player_section.find('👥') + 6
    gender_end = player_section.find('🧸')
    gender = player_section[gender_start:gender_end].strip()
    
    # Извлекаем возраст
    age_start = player_section.find('🧸') + 10
    age_end = player_section.find('👶')
    age = int(player_section[age_start:age_end].strip())
    
    # Извлекаем деторождение
    childfree_start = player_section.find('👶') + 15
    childfree_end = player_section.find('🧘')
    childfree = player_section[childfree_start:childfree_end].strip()
    
    # Извлекаем телосложение
    physique_start = player_section.find('🧘') + 15
    physique_end = player_section.find('❤')
    physique = player_section[physique_start:physique_end].strip()
    
    # Извлекаем здоровье
    health_start = player_section.find('❤') + 10
    health_end = player_section.find('👺')
    health = [player_section[health_start:health_end].strip()]
    
    # Извлекаем черты характера
    traits_start = player_section.find('👺') + 18
    traits_end = player_section.find('👻')
    traits = [player_section[traits_start:traits_end].strip()]
    
    # Извлекаем фобии
    phobias_start = player_section.find('👻') + 8
    phobias_end = player_section.find('🎣')
    phobias = [player_section[phobias_start:phobias_end].strip()]
    
    # Извлекаем хобби
    hobbies_start = player_section.find('🎣') + 8
    hobbies_end = player_section.find('📝')
    hobbies = [player_section[hobbies_start:hobbies_end].strip()]
    
    # Извлекаем доп. информацию
    info_start = player_section.find('📝') + 18
    info_end = player_section.find('📦')
    additional_info = [player_section[info_start:info_end].strip()]
    
    # Извлекаем багаж
    baggage_start = player_section.find('📦') + 8
    baggage_end = player_section.find('🃏')
    baggage = [player_section[baggage_start:baggage_end].strip()]
    
    # Извлекаем карты
    card1_start = player_section.find('🃏') + 10
    card1_end = player_section.find('🃏', card1_start)
    card2_end = len(player_section)
    
    cards = [
        player_section[card1_start:card1_end].strip(),
        player_section[card1_end + 10:card2_end].strip()
    ]
    
    return {
        'name': name,
        'profession': profession,
        'gender': gender,
        'age': age,
        'childfree': childfree,
        'physique': physique,
        'health': health,
        'traits': traits,
        'phobias': phobias,
        'hobbies': hobbies,
        'additional_info': additional_info,
        'baggage': baggage,
        'cards': cards
    }

def get_available_games():
    """Возвращает список доступных игр (папок в директории games)"""
    if not os.path.exists('games'):
        os.makedirs('games')
        return []
    
    return [d for d in os.listdir('games') if os.path.isdir(os.path.join('games', d))]