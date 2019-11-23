<template>
    <div class="row">
        <svg id="drawing" class="text-left m-4 col-6"></svg>
        <!--<b-button variant="info" v-on:click="makeAction()">Select comb</b-button>-->
        <div class="col-2 height=100%">
            <b-card v-if="!!board" v-show="board.mouse_over_unit">
                <b-card-title>{{ board.current_unit.name }}</b-card-title>
                <b-list-group>
                    <b-list-group-item class="border-0 p-0 d-flex justify-content-between align-items-center">
                        Health
                        <b-badge variant="primary" pill>{{ board.current_unit.health }}</b-badge>
                    </b-list-group-item>
                    <b-list-group-item class="border-0 p-0 d-flex justify-content-between align-items-center">
                        Damage
                        <b-badge variant="primary" pill>{{ board.current_unit.damage }}</b-badge>
                    </b-list-group-item>
                    <b-list-group-item class="border-0 p-0 d-flex justify-content-between align-items-center">
                        Armor
                        <b-badge variant="primary" pill>{{ board.current_unit.armor }}</b-badge>
                    </b-list-group-item>
                </b-list-group>
            </b-card>
        </div>
    </div>
</template>

<script>
    import * as SVG from 'svg.js/dist/svg';
    import Board from '../mechanics/board'

    export default {
        props: {
            board_data: null,
            units: null,
            hero: null
        },
        data() {
            return {
                board: null,
                current_hex: null
            }
        },
        mounted() {
            const svg_container = SVG(document.getElementById('drawing'));
            this.board = new Board(this, svg_container, this.board_data, this.units, this.hero);
        },
        beforeDestroy() {
            this.$emit('close_game')
        },
        methods: {
            makeAction(action, destination) {
                this.$emit('game_action', action, destination);
            },
            handleAction(actionData) {
                console.log('actionData', actionData);
                this.board.handleAction(actionData);
            }
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
