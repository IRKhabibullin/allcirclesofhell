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
        return {'x': hex_size * (3/2 * hex.q) + this.width_offset,
                'y': hex_size * (Math.sqrt(3)/2 * hex.q  +  Math.sqrt(3) * hex.r) + this.height_offset
        }
    }

    get([q, r]) {
        var hex = this.hexes.filter(function(d) {return d.q == q && d.r == r})
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
            let n_hex = this.get([hex.q + nd[0], hex.r + nd[1]])
            if (n_hex) {
                neighbors.push(n_hex)
            }
        })
        return neighbors
    }

    getHexesInRange(hex, _range, occupied_by = 'any') {
        var hexes_in_range = []
        for (var q = -_range; q < _range + 1; q++) {
            for (var r = Math.max(-_range, -q - _range); r < Math.min(_range, -q + _range) + 1; r++) {
                let _hex = this.get([q + hex.q, r + hex.r])
                if (!!_hex) {
                    if (occupied_by == 'any' || _hex.occupied_by == occupied_by) {
                        hexes_in_range.push(_hex)
                    }
                }
            }
        }
        return hexes_in_range
    }

    distance(hex_a, hex_b) {
        return Math.max(Math.abs(hex_a.x - hex_b.x), Math.abs(hex_a.y - hex_b.y), Math.abs(hex_a.z - hex_b.z))
    }

    findPath(source_hex, target_hex) {
        let frontier = new PriorityQueue((a, b) => a[1] > b[1])
        let came_from = {}
        let cost_so_far = {}

        frontier.push(source_hex, 0)
        cost_so_far[source_hex.q + ';' + source_hex.r] = 0

        while (!frontier.isEmpty()) {
            let current = frontier.pop()

            if (current == target_hex) {
                break;
            }

            var neighbors = this.getNeighbors(current)
            neighbors.forEach(next => {
                if (next.occupied_by !== 'empty') {
                    return;
                }
                let nextId = next.q + ';' + next.r
                let new_cost = cost_so_far[current.q + ';' + current.r] + 1
                if (!(nextId in cost_so_far) || new_cost < cost_so_far[nextId]) {
                    cost_so_far[nextId] = new_cost
                    let priority = new_cost + this.distance(target_hex, next)
                    frontier.push(next, priority)
                    came_from[next.q + ';' + next.r] = current
                }
            })
        }
        let path = []
        if (Object.keys(came_from).length == 0) {
            return path
        }
//        let current = came_from[target_hex.q + ';' + target_hex.r]
        let current = target_hex
        while (current != source_hex) {
            path.push(current)
            current = came_from[current.q + ';' + current.r]
        }
        return path
    }
}

class Board {
    constructor(svg_field, board_data, units) {
//        settings svg size
        var grid_width = Math.round(board_data.radius - 1) * hex_size + 2 * board_data.radius * hex_size + 1;
        var grid_height = (2 * board_data.radius - 1) * Math.sqrt(3) * hex_size + 1;
        this.svg = svg_field.size(grid_width, grid_height);

        this.grid = new Grid(board_data.radius, board_data.hexes);
        this.tiles = this.svg.group();
        this.units = units;
        this.hero = {
            'image': this.svg.image('./src/assets/board_hero_sized.png')
                .on('mouseover', this.heroMouseoverHandler, this)
                .on('mouseout', this.heroMouseoutHandler, this),
            'path': []};

        this.grid.hexes.forEach(hex => {
            if (hex.occupied_by === 'hero') {
                this.hero.hex = hex
                this.hero.moves = this.grid.getHexesInRange(hex, 1, 'empty')
                let hero_coords = this.grid.hexToPoint(hex)
                this.hero.image.move(hero_coords.x, hero_coords.y)
            }
            const {x, y} = this.grid.hexToPoint(hex)
            hex.image = this.getBackgroundImage(hex.occupied_by)
            this.tiles.polygon(corners)
            .attr('id', hex.q + ';' + hex.r)
            .attr('class', hex.occupied_by !== 'empty' ? 'obstacle_comb' : 'comb')
            .attr('fill', hex.image)
            .translate(x, y);

            /*this.svg.text(hex.q + ';' + hex.r)
            .attr('text-anchor', "middle")
            .attr('fill', "black")
            .attr('font-size', 9)
            .translate(x + 30, y);

            this.svg.text(hex.x + ';' + hex.y + ';' + hex.z)
            .attr('text-anchor', "middle")
            .attr('fill', "black")
            .attr('font-size', 9)
            .translate(x + 30, y + 35);*/
        })
        this.tiles.on('click', this.tileClickedHandler, this);

        this.units.forEach(unit => {
            unit.image = this.svg.image(unit.img_path)
                .attr('id', 'u_' + unit.pk)
                .on('mouseover', this.unitMouseoverHandler, this)
                .on('mouseout', this.unitMouseoutHandler, this);
            let _hex = this.grid.get(unit.position)
            unit.move_hexes = this.grid.getHexesInRange(_hex, unit.move_range, 'empty')
            unit.attack_hexes = this.grid.getHexesInRange(_hex, unit.attack_range, 'empty')
            _hex.occupied_by = unit.pk
            let unit_coords = this.grid.hexToPoint(_hex)
            unit.image.move(unit_coords.x, unit_coords.y)
        })
        this.current_unit = this.units[0];
        this.mouse_over_unit = false;
    }

    getHexById(hexId) {
        var coords = hexId.split(';')
        coords = [parseInt(coords[0]), parseInt(coords[1])]
        return this.getHexByCoords(coords)
    }

    getHexByCoords(coords) {
        var _hex = this.grid[coords[0] * this.grid.height + coords[1]]
        return _hex
    }

    getBackgroundImage(_type) {
        switch (_type) {
            case 'obstacle':
                return this.svg.image('./src/assets/rock.jpg', hex_size * 2, hex_size * 2)
            case 'path':
                return 'green'
            default:
                return '#f0e256'
        }
    }

    setBackgroundImage(_hex) {
        document.getElementById(_hex.q + ';' + _hex.r).setAttribute('fill', _hex.image)
    }

    moveHero(_destination) {
        if (_destination.occupied_by !== 'empty') {
            return
        }
        _destination.occupied_by = 'hero'
        document.getElementById(_destination.q + ';' + _destination.r).classList.remove("comb");
        document.getElementById(_destination.q + ';' + _destination.r).classList.add("obstacle_comb");
        var coords = this.grid.hexToPoint(_destination)
        this.hero.image.animate(300, '>').move(coords.x, coords.y)

        this.hero.hex.occupied_by = 'empty'
        document.getElementById(this.hero.hex.q + ';' + this.hero.hex.r).classList.remove("obstacle_comb");
        document.getElementById(this.hero.hex.q + ';' + this.hero.hex.r).classList.add("comb");

        this.hero.hex = _destination
        this.hero.moves = this.grid.getHexesInRange(_destination, 1, 'empty')
    }

// handlers
    tileClickedHandler(event) {
        var self = this
        var _hex = this.grid.getById(event.target.id);

        function resetPath() {
            self.hero.path.forEach(hex => {
                hex.image = self.getBackgroundImage('empty')
                document.getElementById(hex.q + ';' + hex.r).setAttribute('fill', hex.image);
            })
//            probably need to save calculated path and look here for another var like "path_chosen"
            self.hero.path = [];
        }

        function buildPath() {
            self.hero.path = self.grid.findPath(self.hero.hex, _hex);
            self.hero.path.forEach(hex => {
                hex.image = self.getBackgroundImage('path')
                document.getElementById(hex.q + ';' + hex.r).setAttribute('fill', hex.image)
            })
        }

        if (this.grid.distance(_hex, this.hero.hex) === 1) {
            this.moveHero(_hex);
            resetPath();
        } else if (this.hero.path.length > 0) {
            if (_hex != this.hero.path[0]) {
                resetPath();
                buildPath();
            } else {
                this.moveHero(this.hero.path[this.hero.path.length - 1]);
                resetPath();
            }
        } else {
            buildPath();
        }
    }

    tileMouseoverHandler(event) {
//        var _hex = this.grid.getById(event.target.id);
        var _units = this.units.filter(function(d) { return d.pk == event.target.id.slice(-1) })
        if (_units.length > 0) {
            this.current_unit = _units[0];
            console.log(this.current_unit);
            this.mouse_over_unit = true;
        }
//        if (_hex.occupied_by !== 'empty') {
//            return
//        }
//        var path = this.grid.findPath(this.hero_tile, _hex)
//        path.forEach(hex => {
//            document.getElementById(hex.x + ';' + hex.y).setAttribute('fill', 'green')
//        })
    }

    tileMouseoutHandler(event) {
//        var _hex = this.grid.getById(event.target.id);
        this.mouse_over_unit = false;
//        this.grid.hexes.forEach(neighbor => {
//            if (neighbor.occupied_by === 'empty') {
//                document.getElementById(neighbor.x + ';' + neighbor.y).setAttribute('fill', neighbor.image)
//            }
//        })
    }

    unitMouseoverHandler(event) {
        var _units = this.units.filter(function(d) { return d.pk == event.target.id.slice(-1) })
        if (_units.length > 0) {
            this.current_unit = _units[0];
            this.mouse_over_unit = true;
            this.current_unit.attack_hexes.forEach(attack_hex => {
                document.getElementById(attack_hex.q + ';' + attack_hex.r).setAttribute('fill', '#CE3030')
            })
        }
    }

    unitMouseoutHandler(event) {
        this.mouse_over_unit = false;
        var _units = this.units.filter(function(d) { return d.pk == event.target.id.slice(-1) })
        if (_units.length > 0) {

            this.current_unit.attack_hexes.forEach(attack_hex => {
                document.getElementById(attack_hex.q + ';' + attack_hex.r).setAttribute('fill', attack_hex.image);
            })
        }
    }

    heroMouseoverHandler(event) {
        this.hero.moves.forEach(_hex => {
            document.getElementById(_hex.q + ';' + _hex.r).setAttribute('fill', '#5D8AAD')
        })
    }

    heroMouseoutHandler(event) {
        this.hero.moves.forEach(_hex => {
            document.getElementById(_hex.q + ';' + _hex.r).setAttribute('fill', _hex.image);
        })
    }
// handlers
}

export default Board
