import PriorityQueue from './structure';

const hex_size = 30;
var height_offset;
var width_offset;

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

const corners = get_corners(hex_size);
const neighbors_directions = [
    [1, 0], [1, -1], [0, -1],
    [-1, 0], [-1, 1], [0, 1]
]
// todo need to move colors const to one place
const colors = {
    'tileBackground': '#f0e256',
    'heroMoves': '#5D8AAD',
    'unitMoves': '#EE5A3A',
    'crossMoves': '#E1330D',  // unit's and hero's moves intersection
    'target': '#0f7cdb'
}

class Hex {
    /**
    * Class for hex and operations with it
    */
    constructor(hex_data, game_instance) {
        this.q = hex_data.q;
        this.r = hex_data.r;
        this.x = hex_data.q;
        this.z = hex_data.r;
        this.y = -this.q - this.r;
        this.slot = hex_data.slot;
        this.polygon = null;
        this.image = this.getBackground(this.slot, game_instance);
        let coords = this.toPoint();
        this.damage_indicator = game_instance.svg.text('0')
            .font({'fill': 'red', 'size': 18, 'opacity': 0})
            .attr('x', coords['x'] + hex_size * 4 / 3).attr('y', coords['y']);

        this.overTargetHandler = null;
        this.outTargetHandler = null;
        this.clickHandler = null;
    }

    mouseoverHandler() {
        if (!!this.overTargetHandler) {
            this.overTargetHandler(this);
        }
    }

    mouseoutHandler() {
        if (!!this.outTargetHandler) {
            this.outTargetHandler(this);
        }
    }

    mouseClickHandler() {
        if (!!this.clickHandler) {
            this.clickHandler(this);
        }
    }

    getBackground(type, game_instance) {
        /**
        * Gives hex background according to its type
        */
        switch (type) {
            case 'obstacle':
                return game_instance.svg.image('./src/assets/rock.jpg', hex_size * 2, hex_size * 2);
            default:
                return colors.tileBackground;
        }
    }

    setCurrentBackground() {
        /**
        * Sets hex background to its image
        */
        document.getElementById(this.q + ';' + this.r).setAttribute('fill', this.image);
    }

    toPoint() {
        /**
        * Converts hex to x,y pixel coordinates. Used to place svg elements
        * Not equivalent to hex's x,y values.
        */
        return {
            'x': (hex_size + 1) * (3/2 * this.q) + width_offset,
            'y': (hex_size + 1) * (Math.sqrt(3)/2 * this.q  +  Math.sqrt(3) * this.r) + height_offset
        }
    }
}

class HexGrid {
    /**
    * Class for hexagonal grid
    */
    constructor(game_instance, board_data) {
        // debug variable
        this.show_coordinates = true;

        this.game_instance = game_instance;
        this.radius = board_data.radius;
        height_offset = Math.sqrt(3) * (this.radius - 1) * (hex_size + 1);
        width_offset = Math.floor(this.radius / 2) * (hex_size + 1) +
            2 * Math.floor((this.radius - 1) / 2) * (hex_size + 1) + (hex_size + 1) / 2;
        this.hexes = {};
        var grid_width = Math.round(this.radius - 1) * (hex_size + 1) + 2 * this.radius * (hex_size + 1) + 1;
        var grid_height = (2 * this.radius - 1) * Math.sqrt(3) * (hex_size + 1) + 1;
        this.game_instance.svg.size(grid_width, grid_height);

        this.tiles = this.game_instance.svg.group();
        this.coordinates = this.game_instance.svg.group();

        for (var hex_id in board_data.hexes) {
            let hex = new Hex(board_data.hexes[hex_id], this.game_instance);
            let {x, y} = hex.toPoint();
            let _polygon = this.tiles.polygon(corners)
                .attr('id', hex_id)
                .attr('class', hex.slot != 'empty' ? 'obstacle_hex' : 'hex')
                .attr('fill', hex.image)
                .on('mouseover', hex.mouseoverHandler, hex)
                .on('mouseout', hex.mouseoutHandler, hex)
                .on('click', hex.mouseClickHandler, hex)
                .translate(x, y);
            hex.polygon = _polygon.node;

            if (this.show_coordinates) {
                this.coordinates.text(hex.q + ';' + hex.r)
                    .attr('text-anchor', "middle")
                    .attr('fill', "black")
                    .attr('font-size', 9)
                    .translate(x + 30, y);

                this.coordinates.text(hex.x + ';' + hex.y + ';' + hex.z)
                    .attr('text-anchor', "middle")
                    .attr('fill', "black")
                    .attr('font-size', 9)
                    .translate(x + 30, y + 35);
            }
            this.coordinates.attr('display', 'none');
            this.hexes[hex_id] = hex;
        };
    }

    getHexByCoords(q, r) {
        /**
        * Get hex by given q,r coordinates
        */
        return this.hexes[q + ';' + r];
    }

    getNeighbors(hex) {
        /**
        * Get neighboring hexes.
        * Up to 6 neighbors for given hex (Could be on the edge of board and will have less neighbors)
        */
        let neighbors = [];
        neighbors_directions.forEach(nd => {
            let n_hex = this.getHexByCoords(hex.q + nd[0], hex.r + nd[1]);
            if (!!n_hex) {
                neighbors.push(n_hex);
            }
        })
        return neighbors;
    }

    getHexesInRange(hex, _range, allowed_slots) {
        /**
        * Get list of hex ids in <_range> away from <center_hex>. Center hex itself doesn't count in range
        * Can specify allowed hex occupation
        * todo probably need to return object instead of list. It this function is needed at all
        */
        var hexes_in_range = [];
        for (var q = -_range; q < _range + 1; q++) {
            for (var r = Math.max(-_range, -q - _range); r < Math.min(_range, -q + _range) + 1; r++) {
                let hex_id = (q + hex.q) + ';' + (r + hex.r);
                if (!!this.hexes[hex_id]) {
                    if (!allowed_slots || allowed_slots.includes(this.hexes[hex_id].slot)) {
                        hexes_in_range.push(hex_id);
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
        let cost = {};

        frontier.push(source_hex, 0);
        cost[source_hex.q + ';' + source_hex.r] = 0;

        while (!frontier.isEmpty()) {
            let current = frontier.pop();
            if (current == target_hex) {
                break;
            }
            var neighbors = this.getNeighbors(current);
            neighbors.forEach(next => {
                if (next.slot != 'empty') {
                    // fixme for now only units have ids in hexes as numbers. But need to fix it later maybe
                    if (!(['unit', 'structure'].includes(next.slot) && next == target_hex)) {
                        return;
                    }
                }
                let nextId = next.q + ';' + next.r;
                let new_cost = cost[current.q + ';' + current.r] + 1;
                if (!(nextId in cost) || new_cost < cost[nextId]) {
                    cost[nextId] = new_cost;
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

    update_hexes(hexes) {
        for (var hex_id in hexes) {
            let _hex = hexes[hex_id];
            let current_hex = this.hexes[hex_id];
            if (current_hex.slot != _hex.slot) {
                let class_to_remove = current_hex.slot == 'empty' ? 'hex' : 'obstacle_hex';
                let class_to_add = _hex.slot == 'empty' ? 'hex' : 'obstacle_hex';
                if (class_to_add != class_to_remove) {
                    current_hex.polygon.classList.remove(class_to_remove);
                    current_hex.polygon.classList.add(class_to_add);
                }
                current_hex.slot = _hex.slot;
            }
        }
    }
}

export default HexGrid
