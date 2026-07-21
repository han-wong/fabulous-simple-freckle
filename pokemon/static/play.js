window.addEventListener("load", (event) => {
    document.querySelector(".animation-start").className = "animation-grow"
});

function disableInput(key) {
    disabledKeys += key
    const input = document.getElementById('btn' + key)
    input.disabled = true
}

function gameIsOngoing() {
    return document.getElementById('masked-name')?.textContent.includes('_')
}

function gameIsOver() {
    const lives = document.getElementById('lives').textContent
    return lives === "0" || !lives
}

const BATCH_DELAY_MS = 150

async function handleInput(value) {
    disableInput(value)
    pendingLetters.push(value)
    clearTimeout(batchTimer)
    batchTimer = setTimeout(flushBatch, BATCH_DELAY_MS)
}

async function flushBatch() {
    if (waiting || pendingLetters.length === 0) return
    waiting = true
    const batch = pendingLetters.join('')
    pendingLetters = []

    const response = await fetch('/game' + window.location.search, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ "guessed_letters": batch })
    })
    const { masked_name, lives, streak } = await response.json();
    waiting = false

    if (lives) {
        document.getElementById('masked-name').textContent = masked_name;
        if (!masked_name.includes('_')) {
            location.reload();
            return
        }
        // let message = document.getElementById('message');
        // if (message && masked_name.split(" ").filter((a) => a != "_").length) {
        //     message.classList.add("is-hidden")
        // }
        renderLives(lives);
        renderStreak(streak);
        // more letters may have queued up while this request was in flight
        if (pendingLetters.length > 0) {
            flushBatch()
        }
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
    const response = await fetch('/game' + window.location.search)
    const { guessed_letters } = await response.json()
    Array(...guessed_letters).forEach((c) => disableInput(c))
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
                const form = document.querySelector('form')
                if (form) {
                    form.submit()
                } else {
                    location.reload()
                }
            }
        },
        false
    );
}

function renderLives(lives) {
    length = parseInt(lives, 10)
    document.getElementById('lives').textContent = Array.from({ length }, (x) => '♥').join('')
}

function renderStreak(streak) {
    document.getElementById('streak').textContent = parseInt(streak, 10)
}

function start() {
    if (!gameIsOngoing() && !gameIsOver()) {
        setTimeout(() => {
            location.reload()
        }, 3000);
    }
    renderLives(document.getElementById('lives').textContent)
    loadGuesses()
    document.documentElement.scroll({ top: document.body.scrollHeight })
}

const allowedCharacters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
let disabledKeys = ''
let waiting = false
let pendingLetters = []
let batchTimer = null

if (!gameIsOver()) {
    start()
}
