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
const colors = {
    'tileBackground': '#f0e256',
    'path': 'green',
    'heroMoves': '#5D8AAD',
    'unitMoves': '#EE5A3A',
    'crossMoves': '#E1330D',  // unit's and hero's moves intersection
    'target': '#0f7cdb'
}

class Hex {
    /**
    * Class for hex and operations with it
    */
    constructor(hex_data, board) {
        this.q = hex_data.q;
        this.r = hex_data.r;
        this.x = hex_data.x;
        this.y = hex_data.y;
        this.z = hex_data.z;
        this.occupied_by = hex_data.occupied_by;
        this.image = this.getBackground(this.occupied_by, board);
    }

    getBackground(type, board) {
        /**
        * Gives hex background according to its type
        */
        switch (type) {
            case 'obstacle':
                return board.svg.image('./src/assets/rock.jpg', hex_size * 2, hex_size * 2);
            case 'path':
                return colors.path;
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
            'x': hex_size * (3/2 * this.q) + width_offset,
            'y': hex_size * (Math.sqrt(3)/2 * this.q  +  Math.sqrt(3) * this.r) + height_offset
        }
    }
}

class HexGrid {
    /**
    * Class for hexagonal grid
    */
    constructor(board, radius, hexes) {
        // debug variable
        this.show_coordinates = true;

        this.board = board;
        this.radius = radius;
        height_offset = Math.sqrt(3) * (this.radius - 1) * hex_size;
        width_offset = Math.floor(this.radius / 2) * hex_size +
            2 * Math.floor((this.radius - 1) / 2) * hex_size + hex_size / 2;
        this.hexes = {};
        var grid_width = Math.round(radius - 1) * hex_size + 2 * radius * hex_size + 1;
        var grid_height = (2 * radius - 1) * Math.sqrt(3) * hex_size + 1;
        this.board.svg.size(grid_width, grid_height);

        this.tiles = this.board.svg.group();
        this.tiles.on('click', this.hexClickHandler, this);

        for (var hex_id in hexes) {
            let hex = new Hex(hexes[hex_id], this.board);
            let {x, y} = hex.toPoint();
            this.tiles.polygon(corners)
                .attr('id', hex_id)
                .attr('class', hex.occupied_by !== 'empty' ? 'obstacle_comb' : 'comb')
                .attr('fill', hex.image)
                .translate(x, y);

            if (this.show_coordinates) {
                this.board.svg.text(hex.q + ';' + hex.r)
                    .attr('text-anchor', "middle")
                    .attr('fill', "black")
                    .attr('font-size', 9)
                    .translate(x + 30, y);

                this.board.svg.text(hex.x + ';' + hex.y + ';' + hex.z)
                    .attr('text-anchor', "middle")
                    .attr('fill', "black")
                    .attr('font-size', 9)
                    .translate(x + 30, y + 35);
            }
            this.hexes[hex_id] = hex;
        };
    }

    hexClickHandler(event) {
        var _hex = this.hexes[event.target.id];

        if (this.board.selectedAction == 'attack') {
            this.board.selectedAction = 'move'
        }
        if (this.distance(_hex, this.board.hero.hex) <= this.board.hero.move_range) {
            this.board.hero.resetPath();
            this.board.component.makeAction({'action': 'move', 'destination': event.target.id});
        } else if (this.board.hero.path.length > 0) {
            if (_hex != this.board.hero.path[0]) {
                this.board.hero.resetPath();
                this.board.hero.buildPath(_hex);
            } else {
                let hex_in_path = this.board.hero.path[this.board.hero.path.length - 1];
                this.board.component.makeAction({'action': 'move', 'destination': hex_in_path.q + ';' + hex_in_path.r});
            }
        } else {
            this.board.hero.buildPath(_hex);
        }
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

    getHexesInRange(hex, _range, occupied_by = 'any') {
        /**
        * Get list of hexes in <_range> away from <center_hex>. Center hex itself counts for range 1
        * Can specify allowed hex occupation.
        * Hexes, occupied by object of type that NOT in <occupied_by>, not included in result
        * todo probably need to return object instead of list. It this function is needed at all
        */
        var hexes_in_range = [];
        for (var q = -_range; q < _range + 1; q++) {
            for (var r = Math.max(-_range, -q - _range); r < Math.min(_range, -q + _range) + 1; r++) {
                let _hex = this.getHexByCoords(q + hex.q, r + hex.r);
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
                if (next.occupied_by != 'empty') {
                    // fixme for now only units have ids in hexes as numbers. But need to fix it later maybe
                    if (!(typeof next.occupied_by == 'number' && next == target_hex)) {
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
}

export default HexGrid
