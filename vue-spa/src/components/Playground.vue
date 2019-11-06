<template>
    <div>
        <svg id="drawing" class="text-left m-4"></svg>
        <!--<b-button variant="info" v-on:click="customThing()">Select comb</b-button>-->
    </div>
</template>

<script>
    import * as SVG from 'svg.js/dist/svg';
    import PriorityQueue from '../mechanics/structure'

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
    console.log(corners)

    const neighbours_directions = [
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

        getNeighbours(hex) {
            let neighbors = []
            neighbours_directions.forEach(nd => {
                let n_hex = this.get([hex.x + nd[0], hex.y + nd[1]])
                if (n_hex) {
                    neighbors.push(n_hex)
                }
            })
            return neighbors
        }
    }

    class Board {
        constructor(svg_field, board_data) {
            var grid_width = Math.round(board_data.radius - 1) * hex_size + 2 * board_data.radius * hex_size + 1
            var grid_height = (2 * board_data.radius - 1) * Math.sqrt(3) * hex_size + 1

            this.grid = new Grid(board_data.radius, board_data.hexes)
            console.log('grid')
            console.log(this.grid)
            this.svg = svg_field.size(grid_width, grid_height);
            this.tiles = this.svg.group();
            this.hero_tile = null

            board_data.hexes.forEach(board_hex => {
                var hex = this.grid.get([board_hex.x, board_hex.y])
                //hex.tile_type = board_hex.type
                if (hex.tile_type === 'hero_tile') {
                    this.hero_tile = hex
                }
                const {x, y} = this.grid.hexToPoint(hex)
                this.tiles.polygon(corners)
                .attr('id', hex.x + ';' + hex.y)
                .attr('class', hex.tile_type !== 'empty' ? 'obstacle_comb' : 'comb')
                .attr('fill', this.getBackgroundImage(hex.tile_type))
                .translate(x, y);

                this.svg.text(hex.x + ';' + hex.y)
                .attr('text-anchor', "middle")
                .attr('fill', "black")
                .attr('font-size', 9)
                .translate(x + 30, y);

                this.svg.text(hex.q + ';' + hex.r + ';' + hex.s)
                .attr('text-anchor', "middle")
                .attr('fill', "black")
                .attr('font-size', 9)
                .translate(x + 30, y + 35);
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
        tileClickedHandler(event) {
            var _hex = this.grid.getById(event.target.id)
            console.log(_hex)
            console.log(this.grid.getNeighbours(_hex))
            //console.log(this.grid.findPath(this.hero_tile, _hex))
        }
        tileMouseoverHandler(event) {
            var _hex = this.grid.getById(event.target.id)
            this.grid.getNeighbours(_hex).forEach(neighbour => {
                let _polygon = document.getElementById(neighbour.x + ';' + neighbour.y)
                _polygon.setAttribute('fill', 'green')
            })
        }
        tileMouseoutHandler(event) {
            var _hex = this.grid.getById(event.target.id)
            this.grid.getNeighbours(_hex).forEach(neighbour => {
                let _polygon = document.getElementById(neighbour.x + ';' + neighbour.y)
                _polygon.setAttribute('fill', '#f0e256')
            })
        }
        customMethod() {
            this.tiles.on('click', this.tileClickedHandler, this);
            this.tiles.on('mouseover', this.tileMouseoverHandler, this);
            this.tiles.on('mouseout', this.tileMouseoutHandler, this);
        }
        getBackgroundImage(_type) {
            if (_type === 'obstacle') {
                return this.svg.image('./src/assets/rock.jpg', hex_size, hex_size)
            } else if (_type === 'hero_tile') {
                return this.svg.image('./src/assets/board_hero_sized.jpg')
            }
            return '#f0e256'
        }
    }

    export default {
        props: {
            board_data: null
        },
        data() {
            return {
                board: null
            }
        },
        mounted() {
            const svg_container = SVG(document.getElementById('drawing'));
            this.board = new Board(svg_container, this.board_data);
            this.board.customMethod()
        },
        methods: {
            customThing() {
                console.log(this.board.grid.get([4, 6]))
            }
        }
    }
</script>

<style lang="scss">
    .comb {
        stroke-width: 2;
        stroke: red;
        pointer-events: visible;
    }

    .obstacle_comb {
        stroke-width: 2;
        stroke: red;
        pointer-events: visible;
    }

    .comb:hover {
        fill: #DA4567;
    }

    .clickedComb {
        stroke-width: 3;
        stroke: blue;
        pointer-events: visible;
    }
</style>
