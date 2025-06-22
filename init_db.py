from models import db, Cataclysm, Player

def initialize_database():
    # Создаем новую игровую сессию
    session = GameSession()
    db.session.add(session)
    db.session.commit()

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
            is_revealed=False
        ),
        # Добавьте больше игроков по аналогии
    ]

    db.session.add_all(players)
    db.session.commit()