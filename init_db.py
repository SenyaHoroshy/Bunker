from models import db, Cataclysm, Player, GameSession

def initialize_database():
    # Очищаем базу
    db.session.query(GameSession).delete()
    db.session.query(Player).delete()
    db.session.query(Cataclysm).delete()
    
    # Создаем новую игровую сессию
    session = GameSession(admin_ip='127.0.0.1')
    db.session.add(session)
    
    # Пример данных о катаклизме
    cataclysm = Cataclysm(
        description="Ядерная война",
        population=15,
        destruction=85,
        shelter_area=120,
        time_in_shelter="10 лет",
        conditions="Автоматически открываются через 1 год",
        equipment="Генератор|Система фильтрации|Медпункт|Оружейная",
        supplies="Консервы (500 банок)|Вода (1000 литров)|Семена растений|Аптечки (50 шт)",
        inhabitants="4 человека|2 собаки"
    )
    db.session.add(cataclysm)

    # Пример данных игроков
    players = [
        Player(
            name="Иван Петров",
            profession="Врач",
            gender="Мужской",
            age=35,
            childfree="Не может иметь детей",
            physique="Спортивное",
            health="Здоров|Аллергия на пенициллин",
            traits="Лидер|Агрессивный",
            phobias="Клаустрофобия",
            hobbies="Чтение|Шахматы",
            additional_info="Бывший военный медик",
            baggage="Аптечка|Фонарик",
            cards="Может вылечить одного человека|Может потребовать любой предмет",
            
            # Все характеристики изначально скрыты
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
        ),
    ]

    db.session.add_all(players)
    db.session.commit()