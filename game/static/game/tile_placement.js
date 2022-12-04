let has_placed = false
let placed = []

function allowDrop(e) {
    e.preventDefault();
}

function drag(e, tile_id) {
    e.dataTransfer.setData("tile_id", tile_id)
    placed = placed.filter(p => p.id !== tile_id)
}

function drop(e, x, y) {
    e.preventDefault();
    const tile_id = e.dataTransfer.getData("tile_id");
    const tile = document.getElementById(tile_id);
    placed = placed.filter(p => p.id !== tile_id)
    if (x != null) {
        const existing_tile = placed.find(p => p.placed_x === x && p.placed_y === y)
        if (!existing_tile) {
            e.target.appendChild(tile);
            placed.push({
                id: tile_id,
                placed_x: x,
                placed_y: y,
            })
        }
    } else {
        const user_tiles = document.getElementById('game_user_tiles');
        user_tiles.appendChild(tile);
    }
    has_placed = placed.length > 0
    refreshButton()
}

function refreshButton() {
    const button = document.getElementById('game_submit_button');
    if (has_placed) {
        button.removeAttribute("disabled")
    } else {
        button.setAttribute("disabled", '')
    }
}

function submitTiles() {
    const error_box = document.getElementById('error-box')
    error_box.childNodes.forEach(c => error_box.removeChild(c))
    fetch("", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.CSRF_TOKEN
        },
        body: JSON.stringify({
            placed,
        })
    }).then(res => {
        if (res.ok) {
            console.log("Request complete! response:", res);
            window.location.reload();
        } else {
            res.json().then(json => {
                const error = document.createElement('p')
                error.textContent = json
                error_box.appendChild(error)
                console.log('Error submitting tiles')
            })
        }
    })
}