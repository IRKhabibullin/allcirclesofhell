import PriorityQueue from './structure'

function get_corners(size) {
    let _corners = [];
    for (var i = 0; i < 6; i++) {
        var angle_rad = Math.PI / 180 * 60 * i;
        var _x = size + size * Math.cos(angle_rad);
        var _y = (Math.sqrt(3) * size / 2 + size * Math.sin(angle_rad));
        _corners.push(_x.toFixed(2) + ',' + _y.toFixed(2));
    }
    return _corners;
}

const hex_size = 30;
const corners = get_corners(hex_size);

const neighbors_directions = [
    [1, 0], [1, -1], [0, -1],
    [-1, 0], [-1, 1], [0, 1]
]
const colors = {
    'tileBackground': '#f0e256',
    'path': 'green',
    'heroMoves': '#5D8AAD',
    'unitMoves': '#EE5A3A',
    'crossMoves': '#E1330D',  // unit's and hero's moves intersection
    'target': '#0f7cdb'
}

var selectedAction = 'move';

class Grid {
    /**
    * Class for hexes and operations with them
    */
    constructor(radius, hexes) {
        this.radius = radius;
        this.hexes = hexes;
        this.height_offset = Math.sqrt(3) * (this.radius - 1) * hex_size;
        this.width_offset = Math.floor(this.radius / 2) * hex_size +
            2 * Math.floor((this.radius - 1) / 2) * hex_size + hex_size / 2;
    }

    hexToPoint(hex) {
        /**
        * Converts hex to x,y pixel coordinates. Used to place svg elements
        * Not equivalent to hex's x,y values.
        */
        return {'x': hex_size * (3/2 * hex.q) + this.width_offset,
                'y': hex_size * (Math.sqrt(3)/2 * hex.q  +  Math.sqrt(3) * hex.r) + this.height_offset
        };
    }

    get([q, r]) {
        /**
        * Get hex by given q,r coordinates
        */
        var hex = this.hexes.filter(function(d) {return d.q == q && d.r == r});
        if (hex.length > 0) {
            return hex[0];
        }
    }

    getById(hexId) {
        /**
        * Get hex by id of a polygon, bound to it
        */
        var coords = hexId.split(';');
        coords = [parseInt(coords[0]), parseInt(coords[1])];
        return this.get(coords);
    }

    getNeighbors(hex) {
        /**
        * Get neighboring hexes.
        * Up to 6 neighbors for given hex (Could be on the edge of board and will have less neighbors)
        */
        let neighbors = [];
        neighbors_directions.forEach(nd => {
            let n_hex = this.get([hex.q + nd[0], hex.r + nd[1]]);
            if (n_hex) {
                neighbors.push(n_hex);
            }
        })
        return neighbors;
    }

    getHexesInRange(hex, _range, occupied_by = 'any') {
        /**
        * Get hexes in <_range> away from <center_hex>. Center hex itself counts for range 1
        * Can specify allowed hex occupation.
        * Hexes, occupied by object of type that NOT in <occupied_by>, not included in result
        */
        var hexes_in_range = [];
        for (var q = -_range; q < _range + 1; q++) {
            for (var r = Math.max(-_range, -q - _range); r < Math.min(_range, -q + _range) + 1; r++) {
                let _hex = this.get([q + hex.q, r + hex.r]);
                if (!!_hex) {
                    if (occupied_by == 'any' || _hex.occupied_by == occupied_by) {
                        hexes_in_range.push(_hex);
                    }
                }
            }
        }
        return hexes_in_range;
    }

    distance(hex_a, hex_b) {
        /**
        * Get distance between two hexes
        */
        return Math.max(Math.abs(hex_a.x - hex_b.x), Math.abs(hex_a.y - hex_b.y), Math.abs(hex_a.z - hex_b.z));
    }

    findPath(source_hex, target_hex) {
        /**
        * Finds path from source hex to target hex. Used A* algorithm
        * Counts only hexes free of obstacles
        */
        let frontier = new PriorityQueue((a, b) => a[1] > b[1]);
        let came_from = {};
        let cost_so_far = {};

        frontier.push(source_hex, 0);
        cost_so_far[source_hex.q + ';' + source_hex.r] = 0;

        while (!frontier.isEmpty()) {
            let current = frontier.pop();
            if (current == target_hex) {
                break;
            }
            var neighbors = this.getNeighbors(current);
            neighbors.forEach(next => {
                if (next.occupied_by == 'obstacle') {
                    return;
                }
                let nextId = next.q + ';' + next.r;
                let new_cost = cost_so_far[current.q + ';' + current.r] + 1;
                if (!(nextId in cost_so_far) || new_cost < cost_so_far[nextId]) {
                    cost_so_far[nextId] = new_cost;
                    let priority = new_cost + this.distance(target_hex, next);
                    frontier.push(next, priority);
                    came_from[next.q + ';' + next.r] = current;
                }
            })
        }
        let path = [];
        if (Object.keys(came_from).length == 0) {
            return path;
        }
        let current = target_hex;
        while (current != source_hex) {
            path.push(current);
            current = came_from[current.q + ';' + current.r];
        }
        return path;
    }
}

class Board {
    /**
    * Class to work with game board
    */
    constructor(component, svg_field, board_data, units, hero) {
        var grid_width = Math.round(board_data.radius - 1) * hex_size + 2 * board_data.radius * hex_size + 1;
        var grid_height = (2 * board_data.radius - 1) * Math.sqrt(3) * hex_size + 1;
        this.svg = svg_field.size(grid_width, grid_height);

        this.grid = new Grid(board_data.radius, board_data.hexes);
        this.tiles = this.svg.group();
        this.units = {};
        this.component = component;
        this.hero = {
            'image': this.svg.image('./src/assets/board_hero_sized.png')
                .on('mouseover', this.heroMouseoverHandler, this)
                .on('mouseout', this.heroMouseoutHandler, this),
            'path': [],
            'moves': [],
            'hex': this.grid.get(hero.position),
            'attack_range': hero.attack_range
        };
        hero.moves.forEach(_pos => {
            this.hero.moves.push(this.grid.get(_pos));
        });
        let hero_coords = this.grid.hexToPoint(this.hero.hex);
        this.hero.image.move(hero_coords.x, hero_coords.y);

        this.grid.hexes.forEach(hex => {
            const {x, y} = this.grid.hexToPoint(hex);
            hex.image = this.getBackgroundImage(hex.occupied_by);
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
        });
        this.tiles.on('click', this.tileClickedHandler, this);
        this.units = units;

        for (var unit_id in this.units) {
            let unit = this.units[unit_id];
            let _hex = this.grid.get(unit.position);
            _hex.occupied_by = unit.pk;
            unit.hex = _hex;

            // create image and move it to unit's position
            unit.image = this.svg.image(unit.img_path)
                .attr('id', 'u_' + unit.pk)
                .on('mouseover', this.unitMouseoverHandler, this)
                .on('mouseout', this.unitMouseoutHandler, this)
                .on('click', this.unitClickedHandler, this);
            let unit_coords = this.grid.hexToPoint(_hex);
            unit.image.move(unit_coords.x, unit_coords.y);

            // settings moves and attack hexes according to their positions
            let moves = [];
            unit.moves.forEach(_pos => {
                moves.push(this.grid.get(_pos));
            });
            unit.moves = moves;
            let attack_hexes = [];
            unit.attack_hexes.forEach(_pos => {
                attack_hexes.push(this.grid.get(_pos));
            });
            unit.attack_hexes = attack_hexes;
        }
        this.current_unit = this.units[0];
        this.show_unit_card = false;  // variable for UnitCard element in Vue component
        this.selectedAction = 'move';
        this.altPressed = false;
    }

    getHexById(hexId) {
        var coords = hexId.split(';');
        coords = [parseInt(coords[0]), parseInt(coords[1])];
        return this.getHexByCoords(coords);
    }

    getHexByCoords(coords) {
        var _hex = this.grid[coords[0] * this.grid.height + coords[1]];
        return _hex;
    }

    getBackgroundImage(_type) {
        switch (_type) {
            case 'obstacle':
                return this.svg.image('./src/assets/rock.jpg', hex_size * 2, hex_size * 2)
            case 'path':
                return colors.path
            default:
                return colors.tileBackground
        }
    }

    setBackgroundImage(_hex) {
        document.getElementById(_hex.q + ';' + _hex.r).setAttribute('fill', _hex.image);
    }

    handleAction(actionData) {
        if (actionData.action == 'move' && actionData.allowed) {
            this.moveHero(actionData.game.hero);
            this.resetPath();

            this.update_units(actionData.units);
            actionData.board.hexes.forEach(_hex => {
                this.grid.get([_hex.q, _hex.r]).occupied_by = _hex.occupied_by;
            })
        } else if (actionData.action == 'attack' && actionData.allowed) {
            this.animate('attack', {
                'svg_elem': this.hero.image,
                'source': this.grid.hexToPoint(this.hero.hex),
                'target': this.grid.hexToPoint(this.units[actionData.target].hex)
            })
            this.update_units(actionData.units);
            actionData.board.hexes.forEach(_hex => {
                this.grid.get([_hex.q, _hex.r]).occupied_by = _hex.occupied_by;
            })
        }
    }

    animate(animation, data) {
        if (animation == 'attack') {
            let svg_elem = data['svg_elem'];
            let source_point = data['source'];
            let target_point = data['target'];
            svg_elem.animate(100, '-').move(target_point.x, target_point.y);
            svg_elem.animate(100, '-').move(source_point.x, source_point.y);
        }
    }

    update_units(new_units) {
        let units_to_update = Object.keys(this.units).filter(u => u in new_units);
        let units_to_add = Object.keys(new_units).filter(u => !(u in this.units));
        let units_to_remove = Object.keys(this.units).filter(u => !(u in new_units));

        units_to_update.forEach(unit_id => {
            let _unit = new_units[unit_id];
            this.units[unit_id].health = _unit.health;
            this.units[unit_id].moves = [];
            this.moveUnit(this.units[unit_id], _unit.position);
            _unit.moves.forEach(_pos => {
                this.units[unit_id].moves.push(this.grid.get(_pos));
            });
            this.units[_unit.pk].attack_hexes = [];
            _unit.attack_hexes.forEach(_pos => {
                this.units[unit_id].attack_hexes.push(this.grid.get(_pos));
            });
        })
        units_to_remove.forEach(unit_id => {
            this.units[unit_id].image.remove();
            delete this.units[unit_id];
        })
        units_to_add.forEach(unit_id => {
            let unit = new_units[unit_id]
            let _hex = this.grid.get(unit.position);
            _hex.occupied_by = unit.pk;
            unit.hex = _hex;

            // create image and move it to unit's position
            unit.image = this.svg.image(unit.img_path)
                .attr('id', 'u_' + unit.pk)
                .on('mouseover', this.unitMouseoverHandler, this)
                .on('mouseout', this.unitMouseoutHandler, this)
                .on('click', this.unitClickedHandler, this);
            let unit_coords = this.grid.hexToPoint(_hex);
            unit.image.move(unit_coords.x, unit_coords.y);

            // settings moves and attack hexes according to their positions
            let moves = [];
            unit.moves.forEach(_pos => {
                moves.push(this.grid.get(_pos));
            });
            unit.moves = moves;
            let attack_hexes = [];
            unit.attack_hexes.forEach(_pos => {
                attack_hexes.push(this.grid.get(_pos));
            });
            unit.attack_hexes = attack_hexes;
            this.units[unit_id] = unit;
        })
    }

    moveUnit(unit, position) {
        var destination = this.grid.get(position);
        if (destination.occupied_by != 'empty') {
            return;
        }
        unit.hex.occupied_by = 'empty';
        document.getElementById(destination.q + ';' + destination.r).classList.remove("comb");
        document.getElementById(destination.q + ';' + destination.r).classList.add("obstacle_comb");
        var coords = this.grid.hexToPoint(destination);
        unit.image.animate(200, '>').delay(200).move(coords.x, coords.y);

        document.getElementById(unit.hex.q + ';' + unit.hex.r).classList.remove("obstacle_comb");
        document.getElementById(unit.hex.q + ';' + unit.hex.r).classList.add("comb");
        unit.hex = destination;
        unit.hex.occupied_by = unit.pk;
    }

    moveHero(hero) {
        var destination_hex = this.grid.get(hero.position);
        if (destination_hex.occupied_by != 'empty') {
            return;
        }
        destination_hex.occupied_by = 'hero';
        document.getElementById(destination_hex.q + ';' + destination_hex.r).classList.remove("comb");
        document.getElementById(destination_hex.q + ';' + destination_hex.r).classList.add("obstacle_comb");
        var coords = this.grid.hexToPoint(destination_hex);
        this.hero.image.animate(200, '>').move(coords.x, coords.y);

        this.hero.hex.occupied_by = 'empty';
        document.getElementById(this.hero.hex.q + ';' + this.hero.hex.r).classList.remove("obstacle_comb");
        document.getElementById(this.hero.hex.q + ';' + this.hero.hex.r).classList.add("comb");

        this.hero.hex = destination_hex;
        this.hero.moves = [];
        hero.moves.forEach(_pos => {
            this.hero.moves.push(this.grid.get(_pos));
        });
    }

    resetPath() {
        this.hero.path.forEach(hex => {
            hex.image = this.getBackgroundImage('empty');
            document.getElementById(hex.q + ';' + hex.r).setAttribute('fill', hex.image);
        })
//            probably need to save calculated path and look here for another var like "path_chosen"
        this.hero.path = [];
    }

    buildPath(destination) {
        this.hero.path = this.grid.findPath(this.hero.hex, destination);
        this.hero.path.forEach(hex => {
            hex.image = this.getBackgroundImage('path');
            document.getElementById(hex.q + ';' + hex.r).setAttribute('fill', hex.image);
        })
    }

    showMoves() {
        this.hero.moves.forEach(_hex => {
            document.getElementById(_hex.q + ';' + _hex.r).setAttribute('fill', colors.heroMoves);
        });
        for (var unit_id in this.units) {
            let unit = this.units[unit_id];
            unit.attack_hexes.forEach(hex => {
                document.getElementById(hex.q + ';' + hex.r)
                    .setAttribute('fill', this.hero.moves.includes(hex) ? colors.crossMoves : colors.unitMoves);
            })
        };
    }

    hideMoves() {
        for (var unit_id in this.units) {
            let unit = this.units[unit_id];
            unit.attack_hexes.forEach(hex => {
                document.getElementById(hex.q + ';' + hex.r).setAttribute('fill', hex.image);
            })
        };
        this.hero.moves.forEach(_hex => {
            document.getElementById(_hex.q + ';' + _hex.r).setAttribute('fill', _hex.image);
        });
    }

    keydownHandler(event) {
        if (event.keyCode == 18) {
            this.altPressed = true;
            this.showMoves();
        }
    }

    keyupHandler(event) {
        if (event.keyCode == 18) {
            this.altPressed = false;
            this.hideMoves();
        }
    }

    actionSelected(actionName) {
        selectedAction = actionName;
    }

// handlers
    tileClickedHandler(event) {
        var self = this;
        var _hex = this.grid.getById(event.target.id);

        if (selectedAction == 'attack') {
            selectedAction = 'move'
        }

        if (this.grid.distance(_hex, this.hero.hex) === 1) {
            this.component.makeAction({'action': 'move', 'destination': [_hex.q, _hex.r]});
        } else if (this.hero.path.length > 0) {
            if (_hex != this.hero.path[0]) {
                self.resetPath();
                self.buildPath(_hex);
            } else {
                let hex_in_path = this.hero.path[this.hero.path.length - 1];
                this.component.makeAction({'action': 'move', 'destination': [hex_in_path.q, hex_in_path.r]});
            }
        } else {
            self.buildPath(_hex);
        }
    }

    unitMouseoverHandler(event) {
        this.current_unit = this.units[event.target.id.slice(-1)];
        this.show_unit_card = true;
        if (selectedAction == 'attack') {
            let unit_hex = this.current_unit.hex;
            if (this.grid.distance(unit_hex, this.hero.hex) <= this.hero.attack_range) {
                document.getElementById(unit_hex.q + ';' + unit_hex.r).setAttribute('fill', colors.target);
            }
        }
    }

    unitMouseoutHandler(event) {
        this.current_unit = this.units[event.target.id.slice(-1)];
        this.show_unit_card = false;
        if (selectedAction == 'attack') {
            let unit_hex = this.current_unit.hex;
            document.getElementById(unit_hex.q + ';' + unit_hex.r).setAttribute('fill', unit_hex.image);
        }
    }

    unitClickedHandler(event) {
        var self = this;
        var _unit = this.units[event.target.id.slice(-1)];
        document.getElementById(_unit.hex.q + ';' + _unit.hex.r).setAttribute('fill', _unit.hex.image);

        if (this.grid.distance(_unit.hex, this.hero.hex) === 1) {
            this.component.makeAction({'action': 'attack', 'target': _unit.pk});
        } else if (this.hero.path.length > 0) {
            if (_unit.hex != this.hero.path[0]) {
                self.resetPath();
                self.buildPath(_unit.hex);
            } else {
                let hex_in_path = this.hero.path[this.hero.path.length - 1];
                this.component.makeAction({'action': 'move', 'destination': [hex_in_path.q, hex_in_path.r]});
            }
        } else {
            self.buildPath(_unit.hex);
        }
    }

    heroMouseoverHandler(event) {
//        this.hero.moves.forEach(_hex => {
//            document.getElementById(_hex.q + ';' + _hex.r).setAttribute('fill', colors.heroMoves);
//        });
    }

    heroMouseoutHandler(event) {
//        this.hero.moves.forEach(_hex => {
//            document.getElementById(_hex.q + ';' + _hex.r).setAttribute('fill', _hex.image);
//        });
    }
// handlers
}

export default Board
