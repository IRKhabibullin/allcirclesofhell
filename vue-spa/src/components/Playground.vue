<template>
    <div id="drawing" class="text-left m-5"></div>
</template>

<script>
    import * as SVG from 'svg.js/dist/svg';
    import * as Honeycomb from 'honeycomb-grid';

    const Hex = Honeycomb.extendHex({ size: 30, orientation: 'flat' })
    const corners = Hex().corners().map(({ x, y }) => `${x},${y}`)

    class Battlefield {
        constructor(field) {
            this.field = field;
            this.grid = Honeycomb.defineGrid(Hex)
        }

        generateField() {
            this.grid.rectangle({ width: 9, height: 8 }).forEach(hex => {
                const { x, y } = hex.toPoint()
                var coords = hex.cube()
                var title = document.createElementNS("http://www.w3.org/2000/svg", 'title');
                this.field.polygon(corners)
                .attr('class', 'comb')
                .on('click', function() {
                    console.log(hex.cube());
                    this.attr('class', 'clickedComb');
                })
                .translate(x, y);

                this.field.text(hex.x + ';' + hex.y)
                .attr('text-anchor', "middle")
                .attr('fill', "black")
                .attr('font-size', 9)
                .translate(x + 30, y);

                this.field.text(coords.q + ';' + coords.r + ';' + coords.s)
                .attr('text-anchor', "middle")
                .attr('fill', "black")
                .attr('font-size', 9)
                .translate(x + 30, y + 35);
            })
        }

    }

    export default {
        mounted() {
            const svg_container = SVG(document.getElementById('drawing')).size(465, 456);
            var battlefield = new Battlefield(svg_container);
            battlefield.generateField();
        }
    }
</script>

<style lang="scss">
    .comb {
        stroke-width: 2;
        stroke: red;
        fill: transparent;
        pointer-events: visible;
    }

    .comb:hover {
        fill: #DA4567;
    }

    .clickedComb {
        stroke-width: 3;
        stroke: blue;
        fill: transparent;
        pointer-events: visible;
    }
</style>
