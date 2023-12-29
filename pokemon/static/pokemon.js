let disabledKeys = ''
let waiting = false
function disableInput(key) {
    disabledKeys += key
    const input = document.getElementById('btn' + key)
    input.disabled = true
    input.value = ''
}
function input() {
    const [{ value }] = arguments
    if (value) {
        handleInput(value)
    }
}


async function handleInput(value) {
    if (waiting) return
    waiting = true
    disableInput(value)
    const response = await fetch('/play' + window.location.search, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        redirect: 'follow',
        body: JSON.stringify({ value })
    })
    const { guess, life, streak } = await response.json()
    console.log(guess)
    if (guess) {
        document.getElementById('player-guess').textContent = guess
        if (!guess.includes('_')) {
            location.reload()
        }
    }
    renderLife(life)
    renderStreak(streak)
    waiting = false
}
function start() {
    if (!gameIsOngoing()) {
        document.getElementById('player-guess').style.display = "none";
    }
    renderLife(document.getElementById('life').textContent)
    loadGuesses()
}

function gameIsOngoing() {
    return document.getElementById('player-guess').textContent.includes('_')
}

async function loadGuesses() {
    const response = await fetch('/guess', { method: 'GET' })
    const { guess_player } = await response.json()
    Array(...guess_player).forEach((c) => disableInput(c))
    loadKeyboard()
}

function loadKeyboard() {
    if (gameIsOngoing()) {
        document.querySelectorAll('.keyboard-buttons').forEach((el) => (el.style.display = 'flex'));
        document.addEventListener(
            'keyup',
            ({ key }) => {
                const allowedCharacters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                key = key?.toUpperCase()
                if (allowedCharacters.includes(key) && !disabledKeys.includes(key)) {
                    handleInput(key)
                } else if (key === 'ENTER') {
                    location.reload()
                }
            },
            false
        );
    } else {
        setTimeout(() => {
            location.reload()
        }, 2000);
    }
}

function renderLife(life) {
    life = parseInt(life, 10)
    if (life > 0) {
        document.getElementById('life').textContent = Array.from({ length: life }, (x) => '♥').join('')
    } else {
        window.location.href = '/game_over'
    }
}

function renderStreak(streak) {
    document.getElementById('streak').textContent = streak, 10
}

start()