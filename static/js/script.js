// Проверяем, зарегистрирован ли игрок
if (window.location.pathname.includes('/player/')) {
    const playerId = window.location.pathname.split('/').pop();
    fetch('/api/check_access', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ player_id: playerId })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.has_access) {
            window.location.href = '/register';
        }
    });
}

function loadPlayers() {
    fetch('/api/players')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(players => {
            console.log('Players loaded:', players);  // Отладочный вывод
            const playersList = document.getElementById('players-list');
            if (players.length === 0) {
                playersList.innerHTML = '<div class="alert alert-warning">Нет доступных игроков</div>';
            } else {
                playersList.innerHTML = players.map(player => `
                    <a href="/player/${player.id}" class="list-group-item list-group-item-action">
                        Игрок #${player.id}: ${player.name}
                    </a>
                `).join('');
            }
        })
        .catch(error => {
            console.error('Error loading players:', error);
            const playersList = document.getElementById('players-list');
            playersList.innerHTML = '<div class="alert alert-danger">Ошибка загрузки списка игроков</div>';
        });
}

document.addEventListener('DOMContentLoaded', function() {
    // Показываем IP сервера
    fetch('/api/server_info')
        .then(response => response.json())
        .then(data => {
            const serverIpElement = document.getElementById('server-ip');
            if (serverIpElement) {
                serverIpElement.textContent = data.ip;
            }
        });
    
    // Загрузка информации о катаклизме
    fetch('/api/cataclysm')
        .then(response => response.json())
        .then(data => {
            const cataclysmInfo = document.getElementById('cataclysm-info');
            cataclysmInfo.innerHTML = `
                <h5>${data.description}</h5>
                <p>👥 Остаток выжившего населения: ${data.population}%</p>
                <p>💥 Разрушения на поверхности: ${data.destruction}%</p>
                <h5 class="mt-3">Убежище</h5>
                <p>🏡 Площадь убежища: ${data.shelter_area}м²</p>
                <p>⌛ Время нахождения в убежище: ${data.time_in_shelter}</p>
                <p>🔓 ${data.conditions}</p>
                <p class="mt-2"><strong>Оборудование:</strong></p>
                <ul>
                    ${data.equipment.map(item => `<li>🔧 ${item}</li>`).join('')}
                </ul>
                <p class="mt-2"><strong>Припасы:</strong></p>
                <ul>
                    ${data.supplies.map(item => `<li>📦 ${item}</li>`).join('')}
                </ul>
                <p class="mt-2"><strong>Обитатели:</strong></p>
                <ul>
                    ${data.inhabitants.map(item => `<li>♻ ${item}</li>`).join('')}
                </ul>
            `;
        });

    // Загрузка списка игроков
    loadPlayers();

    // Обработка кнопки "Раскрыть" на странице игрока
    const revealBtn = document.getElementById('reveal-btn');
    if (revealBtn) {
        revealBtn.addEventListener('click', function() {
            const playerId = window.location.pathname.split('/').pop();
            fetch(`/api/reveal/${playerId}`, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    }
                });
        });
    }

    // Загрузка информации об игроке
    const playerInfo = document.getElementById('player-info');
    if (playerInfo) {
        const playerId = window.location.pathname.split('/').pop();
        fetch(`/api/player/${playerId}`)
            .then(response => response.json())
            .then(data => {
                playerInfo.innerHTML = `
                    <p>🪪 <strong>Имя Фамилия:</strong> ${data.name}</p>
                    <p>💼 <strong>Профессия:</strong> ${data.profession}</p>
                    <p>👥 <strong>Пол:</strong> ${data.gender}</p>
                    <p>🧸 <strong>Возраст:</strong> ${data.age}</p>
                    <p>👶 <strong>Деторождение:</strong> ${data.childfree}</p>
                    <p>🧘 <strong>Телосложение:</strong> ${data.physique}</p>
                    <p class="mt-3"><strong>Здоровье:</strong></p>
                    <ul>
                        ${data.health.map(item => `<li>❤ ${item}</li>`).join('')}
                    </ul>
                    <p class="mt-3"><strong>Черты характера:</strong></p>
                    <ul>
                        ${data.traits.map(item => `<li>👺 ${item}</li>`).join('')}
                    </ul>
                    <p class="mt-3"><strong>Фобии:</strong></p>
                    <ul>
                        ${data.phobias.map(item => `<li>👻 ${item}</li>`).join('')}
                    </ul>
                    <p class="mt-3"><strong>Хобби:</strong></p>
                    <ul>
                        ${data.hobbies.map(item => `<li>🎣 ${item}</li>`).join('')}
                    </ul>
                    <p class="mt-3"><strong>Доп. информация:</strong></p>
                    <ul>
                        ${data.additional_info.map(item => `<li>📝 ${item}</li>`).join('')}
                    </ul>
                    <p class="mt-3"><strong>Багаж:</strong></p>
                    <ul>
                        ${data.baggage.map(item => `<li>📦 ${item}</li>`).join('')}
                    </ul>
                    <p class="mt-3"><strong>Карты:</strong></p>
                    <ul>
                        ${data.cards.map((item, index) => `<li>🃏 Карта ${index + 1}: ${item}</li>`).join('')}
                    </ul>
                `;
            });
    }
});