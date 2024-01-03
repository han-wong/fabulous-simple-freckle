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
    if (value && !gameIsOver()) {
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
    const { current_word, life, streak } = await response.json()
    if (life) {
        document.getElementById('current-word').textContent = current_word
        if (!current_word.includes('_')) {
            location.reload()
        }
        renderLife(life)
        renderStreak(streak)
        waiting = false
    } else {
        location.reload()
    }
}

function start() {
    if (!gameIsOngoing() && !gameIsOver()) {
        setTimeout(() => {
            location.reload()
        }, 2000);
    }
    renderLife(document.getElementById('life').textContent)
    loadGuesses()
}

function gameIsOngoing() {
    return document.getElementById('current-word')?.textContent.includes('_')
}

function gameIsOver() {
    const life = document.getElementById('life').textContent
    return life === "0" || !life
}

async function loadGuesses() {
    const response = await fetch('/guess', { method: 'GET' })
    const { guess } = await response.json()
    Array(...guess).forEach((c) => disableInput(c))
    if (gameIsOngoing()) {
        loadKeyboard()
    }
    if (gameIsOver()) {
        location.reload()
    }
}

function loadKeyboard() {
    // document.querySelectorAll('.keyboard-button').forEach((el) => (el.style.display = 'flex'));
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
}

function renderLife(life) {
    length = parseInt(life, 10)
    document.getElementById('life').textContent = Array.from({ length }, (x) => '♥').join('')
}

function renderStreak(streak) {
    document.getElementById('streak').textContent = streak, 10
}

if (!gameIsOver()) {
    start()
}