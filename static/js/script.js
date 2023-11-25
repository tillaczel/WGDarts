var selectedPlayers = {};

function toggleSelection(playerId) {
    var card = document.getElementById('player-card-' + playerId);
    if (selectedPlayers[playerId]) {
        delete selectedPlayers[playerId];
        card.classList.remove('selected');
    } else {
        selectedPlayers[playerId] = true;
        card.classList.add('selected');
    }
    // Call the function to update the form inputs
    updateFormInputs();
}

function updateFormInputs() {
    var form = document.getElementById('start-game-form');
    // Clear any previous inputs
    form.innerHTML = '';

    Object.keys(selectedPlayers).forEach(function (id) {
        var input = document.createElement('input');
        input.type = 'hidden';
        input.value = id;
        form.appendChild(input);
    });
}

function startGame() {
    var selectedPlayerIds = Object.keys(selectedPlayers);
    if (selectedPlayerIds.length < 2) {
        alert('Please select at least two players to start the game.');
        return false;
    }

    var form = document.getElementById('start-game-form');
    // Clear any previous inputs
    form.innerHTML = '';

    selectedPlayerIds.forEach(function(id) {
        var input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'selected_players';
        input.value = id;
        form.appendChild(input);
    });

    form.submit();
}

function toggleGuestPlayers() {
    var checkbox = document.getElementById('show-guest-players');

    {% for player in players %}
        var player_id = '{{ player.id }}';
        var isGuest = '{{ player.guest }}';
        var elementToToggle = document.getElementById('player-card-' + player_id);

        console.log('Player ID:', player_id);
        console.log('Is Guest:', isGuest);

        // Check the state of the checkbox and if the player is not a guest
        if (!checkbox.checked && isGuest.toLowerCase() === 'true') {
            elementToToggle.style.display = 'none'; // Hide the element
        } else {
            elementToToggle.style.display = 'block'; // Show the element
        }
    {% endfor %}
}

window.onload = toggleGuestPlayers;
