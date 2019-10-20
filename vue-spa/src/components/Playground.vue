<template>
    <div id="drawing" class="text-left m-5"></div>
</template>

<script>
    import * as SVG from 'svg.js/dist/svg';
    import * as Honeycomb from 'honeycomb-grid';

    export default {
        mounted() {

            const draw = SVG(document.getElementById('drawing')).size(465, 456)

            const Hex = Honeycomb.extendHex({ size: 30, orientation: 'flat' })
            const Grid = Honeycomb.defineGrid(Hex)
            const corners = Hex().corners().map(({ x, y }) => `${x},${y}`)

            // render 10,000 hexes
            Grid.rectangle({ width: 9, height: 8 }).forEach(hex => {
                const { x, y } = hex.toPoint()
                draw.polygon(corners)
                .attr('class', 'comb')
                .translate(x, y);
            })
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
</style>
