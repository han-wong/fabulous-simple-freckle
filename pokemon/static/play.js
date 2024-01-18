window.addEventListener("load", (event) => {
    document.querySelector(".animation-start").className = "animation-grow"
});

function disableInput(key) {
    disabledKeys += key
    const input = document.getElementById('btn' + key)
    input.disabled = true
}

function gameIsOngoing() {
    return document.getElementById('current-word')?.textContent.includes('_')
}

function gameIsOver() {
    const life = document.getElementById('life').textContent
    return life === "0" || !life
}

async function handleInput(value) {
    if (waiting) return
    waiting = true
    disableInput(value)
    const response = await fetch('/game' + window.location.search, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ "guess": value })
    })
    const { current_word, life, streak } = await response.json();
    if (life) {
        document.getElementById('current-word').textContent = current_word;
        if (!current_word.includes('_')) {
            location.reload();
        }
        let message = document.getElementById('message');
        if (message && current_word.split(" ").filter((a) => a != "_").length) {
            message.classList.add("is-hidden")
        }
        renderLife(life);
        renderStreak(streak);
        waiting = false
    } else {
        location.reload()
    }
}

function input() {
    const [{ value }] = arguments
    if (value && !gameIsOver()) {
        handleInput(value)
    }
}

async function loadGuesses() {
    const response = await fetch('/game' + window.location.search, { method: 'GET', })
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

function start() {
    if (!gameIsOngoing() && !gameIsOver()) {
        setTimeout(() => {
            location.reload()
        }, 3000);
    }
    renderLife(document.getElementById('life').textContent)
    loadGuesses()
    document.documentElement.scroll({ top: document.body.scrollHeight })
}

const allowedCharacters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
let disabledKeys = ''
let waiting = false

if (!gameIsOver()) {
    start()
}