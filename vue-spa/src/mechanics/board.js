import PriorityQueue from './structure'

function get_corners(size) {
    let _corners = []
    for (var i = 0; i < 6; i++) {
        var angle_rad = Math.PI / 180 * 60 * i
        var _x = size + size * Math.cos(angle_rad)
        var _y = (Math.sqrt(3) * size / 2 + size * Math.sin(angle_rad))
        _corners.push(_x.toFixed(2) + ',' + _y.toFixed(2))
    }
    return _corners
}

const hex_size = 30
const corners = get_corners(hex_size)

const neighbors_directions = [
    [1, 0], [1, -1], [0, -1],
    [-1, 0], [-1, 1], [0, 1]
]

class Grid {
    constructor(radius, hexes) {
        this.radius = radius;
        this.hexes = hexes
        this.height_offset = Math.sqrt(3) * (this.radius - 1) * hex_size
        this.width_offset = Math.floor(this.radius / 2) * hex_size + 2 * Math.floor((this.radius - 1) / 2) * hex_size + hex_size / 2
    }

    hexToPoint(hex) {
        return {'x': hex_size * (3/2 * hex.x) + this.width_offset,
                'y': hex_size * (Math.sqrt(3)/2 * hex.x  +  Math.sqrt(3) * hex.y) + this.height_offset
        }
    }

    get([x, y]) {
        var hex = this.hexes.filter(function(d) {return d.x == x && d.y == y})
        if (hex.length > 0) {
            return hex[0];
        }
    }

    getById(hexId) {
        var coords = hexId.split(';');
        coords = [parseInt(coords[0]), parseInt(coords[1])];
        return this.get(coords);
    }

    getNeighbors(hex) {
        let neighbors = []
        neighbors_directions.forEach(nd => {
            let n_hex = this.get([hex.x + nd[0], hex.y + nd[1]])
            if (n_hex) {
                neighbors.push(n_hex)
            }
        })
        return neighbors
    }

    distance(hex_a, hex_b) {
        return Math.max(Math.abs(hex_a.q - hex_b.q), Math.abs(hex_a.r - hex_b.r), Math.abs(hex_a.s - hex_b.s))
    }

    findPath(source_hex, target_hex) {
        let frontier = new PriorityQueue((a, b) => a[1] > b[1])
        let came_from = {}
        let cost_so_far = {}

        frontier.push(source_hex, 0)
        cost_so_far[source_hex.x + ';' + source_hex.y] = 0

        while (!frontier.isEmpty()) {
            let current = frontier.pop()

            if (current == target_hex) {
                break;
            }

            var neighbors = this.getNeighbors(current)
            neighbors.forEach(next => {
                if (next.tile_type !== 'empty') {
                    return;
                }
                let nextId = next.x + ';' + next.y
                let new_cost = cost_so_far[current.x + ';' + current.y] + 1
                if (!(nextId in cost_so_far) || new_cost < cost_so_far[nextId]) {
                    cost_so_far[nextId] = new_cost
                    let priority = new_cost + this.distance(target_hex, next)
                    frontier.push(next, priority)
                    came_from[next.x + ';' + next.y] = current
                }
            })
        }
        let path = []
        if (Object.keys(came_from).length == 0) {
            return path
        }
//        let current = came_from[target_hex.x + ';' + target_hex.y]
        let current = target_hex
        while (current != source_hex) {
            path.push(current)
            current = came_from[current.x + ';' + current.y]
        }
        return path
    }
}

class Board {
    constructor(svg_field, board_data) {
//        settings svg size
        var grid_width = Math.round(board_data.radius - 1) * hex_size + 2 * board_data.radius * hex_size + 1;
        var grid_height = (2 * board_data.radius - 1) * Math.sqrt(3) * hex_size + 1;
        this.svg = svg_field.size(grid_width, grid_height);

        this.grid = new Grid(board_data.radius, board_data.hexes);
        this.tiles = this.svg.group();
        this.hero_tile = null;

        this.hero_image = this.svg.image('./src/assets/board_hero_sized.png');

        this.path = [];

        this.grid.hexes.forEach(hex => {
            if (hex.tile_type === 'hero') {
                this.hero_tile = hex
                let hero_coords = this.grid.hexToPoint(hex)
                this.hero_image.move(hero_coords.x, hero_coords.y)
            }
            const {x, y} = this.grid.hexToPoint(hex)
            hex.image = this.getBackgroundImage(hex.tile_type)
            this.tiles.polygon(corners)
            .attr('id', hex.x + ';' + hex.y)
            .attr('class', hex.tile_type !== 'empty' ? 'obstacle_comb' : 'comb')
            .attr('fill', hex.image)
            .translate(x, y);

            /*this.svg.text(hex.x + ';' + hex.y)
            .attr('text-anchor', "middle")
            .attr('fill', "black")
            .attr('font-size', 9)
            .translate(x + 30, y);

            this.svg.text(hex.q + ';' + hex.r + ';' + hex.s)
            .attr('text-anchor', "middle")
            .attr('fill', "black")
            .attr('font-size', 9)
            .translate(x + 30, y + 35);*/
        })
    }

    getHexById(hexId) {
        // for some reason this.grid.get function doesn't work, so i need to calculate it myself
        // need to open an issue on github
        var coords = hexId.split(';')
        coords = [parseInt(coords[0]), parseInt(coords[1])]
        return this.getHexByCoords(coords)
    }

    getHexByCoords(coords) {
        var _hex = this.grid[coords[0] * this.grid.height + coords[1]]
        return _hex
    }

    customMethod() {
        this.tiles.on('click', this.tileClickedHandler, this);
//        this.tiles.on('mouseover', this.tileMouseoverHandler, this);
//        this.tiles.on('mouseout', this.tileMouseoutHandler, this);
    }

    getBackgroundImage(_type) {
        if (_type === 'obstacle') {
            return this.svg.image('./src/assets/rock.jpg', hex_size * 2, hex_size * 2)
        }
        return '#f0e256'
    }

    setBackgroundImage(_hex) {
        document.getElementById(_hex.x + ';' + _hex.y).setAttribute('fill', _hex.image)
    }

    moveHero(_destination) {
        if (_destination.tile_type !== 'empty') {
            return
        }
        _destination.tile_type = 'hero'
        document.getElementById(_destination.x + ';' + _destination.y).classList.remove("comb");
        document.getElementById(_destination.x + ';' + _destination.y).classList.add("obstacle_comb");
        var coords = this.grid.hexToPoint(_destination)
        this.hero_image.animate(300, '>').move(coords.x, coords.y)

        this.hero_tile.tile_type = 'empty'
        document.getElementById(this.hero_tile.x + ';' + this.hero_tile.y).classList.remove("obstacle_comb");
        document.getElementById(this.hero_tile.x + ';' + this.hero_tile.y).classList.add("comb");

//        this.setBackgroundImage(this.hero_tile)
//        this.setBackgroundImage(_destination)
        this.hero_tile = _destination
    }

// handlers
    tileClickedHandler(event) {
        var self = this
        var _hex = this.grid.getById(event.target.id);

        function resetPath() {
            self.path.forEach(hex => {
                document.getElementById(hex.x + ';' + hex.y).setAttribute('fill', hex.image);
            })
//            probably need to save calculated path and look here for another var like "path_chosen"
            self.path = [];
        }

        function buildPath() {
            self.path = self.grid.findPath(self.hero_tile, _hex);
            self.path.forEach(hex => {
                document.getElementById(hex.x + ';' + hex.y).setAttribute('fill', 'green')
            })
        }

        if (this.grid.distance(_hex, this.hero_tile) === 1) {
            this.moveHero(_hex);
            resetPath();
        } else if (this.path.length > 0) {
            if (_hex != this.path[0]) {
                resetPath();
                buildPath();
            } else {
                this.moveHero(this.path[this.path.length - 1]);
                resetPath();
            }
        } else {
            buildPath();
        }
    }

    tileMouseoverHandler(event) {
        var _hex = this.grid.getById(event.target.id)
        if (_hex.tile_type !== 'empty') {
            return
        }
        var path = this.grid.findPath(this.hero_tile, _hex)
        path.forEach(hex => {
            document.getElementById(hex.x + ';' + hex.y).setAttribute('fill', 'green')
        })
    }

    tileMouseoutHandler(event) {
        var _hex = this.grid.getById(event.target.id)
        this.grid.hexes.forEach(neighbor => {
            if (neighbor.tile_type === 'empty') {
                document.getElementById(neighbor.x + ';' + neighbor.y).setAttribute('fill', neighbor.image)
            }
        })
    }
// handlers
}

export default Board
