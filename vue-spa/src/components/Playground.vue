<template>
    <div>
        <svg id="drawing" class="text-left m-4"></svg>
        <!--<b-button variant="info" v-on:click="customThing()">Select comb</b-button>-->
    </div>
</template>

<script>
    import * as SVG from 'svg.js/dist/svg';
    import Board from '../mechanics/board'

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
        }
    }
</script>

<style lang="scss">
    .comb {
        stroke-width: 2;
        stroke: red;
    }

    .obstacle_comb {
        stroke-width: 2;
        stroke: red;
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
