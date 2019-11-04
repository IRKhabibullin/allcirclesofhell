<template>
    <div>
        <svg id="drawing" class="text-left m-5"></svg>
        <b-button variant="info" v-on:click="this.board.customMethod()">Select comb</b-button>
    </div>
</template>

<script>
    import * as SVG from 'svg.js/dist/svg';
    import * as Honeycomb from 'honeycomb-grid';

    const hex_size = 30
    const Hex = Honeycomb.extendHex({size: hex_size, orientation: 'flat', 'tile_type': 'empty'})
    const corners = Hex().corners().map(({ x, y }) => `${x},${y}`)

    class Board {
        constructor(svg_field, board_data) {
            var grid_width = (1.5 * board_data.width + 0.5) * hex_size
            var grid_height = Math.sqrt(3) * (board_data.height + 0.5) * hex_size
            this.svg = svg_field.size(grid_width, grid_height);
            this.tiles = this.svg.group();
            this.grid = Honeycomb.defineGrid(Hex).rectangle({ width: board_data.width, height: board_data.height })
            this.hero_tile = null

            board_data.hexes.forEach(board_hex => {
                var hex = this.grid.get([board_hex.c, board_hex.r])
                hex.tile_type = board_hex.type
                if (hex.tile_type === 'hero_tile') {
                    this.hero_tile = hex
                }
                const {x, y} = hex.toPoint()
                var coords = hex.cube()
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

                this.svg.text(coords.q + ';' + coords.r + ';' + coords.s)
                .attr('text-anchor', "middle")
                .attr('fill', "black")
                .attr('font-size', 9)
                .translate(x + 30, y + 35);
            })
        }
        tileClickedHandler(event) {
            var coords = event.target.id.split(';')
            coords = [parseInt(coords[0]), parseInt(coords[1])]
            _hex = this.someMethod(coords)
            console.log(coords)
            console.log('grid 2')
            console.log(_hex)
            console.log(this.grid[0])
            console.log(this.grid[16])
            console.log(this.grid[0].distance(this.grid[16]))
            console.log(this.board)
        }
        someMethod(hexId) {
            this.grid.get(hexId)
        }
        customMethod() {
            //_hex = this.grid.get([4, 3])
            this.tiles.on('click', this.tileClickedHandler, this);
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
