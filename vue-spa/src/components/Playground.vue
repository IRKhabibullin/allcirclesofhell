<template>
    <div class="row d-flex justify-content-between">
        <svg id="drawing" class="text-left m-4 col-6"></svg>
        <!--<b-button variant="info" v-on:click="makeAction()">Select comb</b-button>-->
        <div class="col-2 height=100%">
            <b-card v-if="!!board" v-show="board.show_unit_card && board.altPressed">
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
        <div class="col-2 height=100% m-4">
            <b-card v-if="!!board">
                <b-card-title>Actions</b-card-title>
                <b-list-group class="align-items-center">
                    <b-button variant="info" v-on:click="board.actionSelected('attack')" class="btn btn-danger btn-circle p-0 btn-xl m-1">
                        <b-img src="./src/assets/sword.png" width=40 height=40 alt="Attack"></b-img>
                    </b-button>
                </b-list-group>
            </b-card>
        </div>
    </div>
</template>

<script>
    import * as SVG from 'svg.js/dist/svg';
    import Board from '../mechanics/board';

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
        destroyed() {
            window.removeEventListener('keydown', this.keydownHandler);
            window.removeEventListener('keyup', this.keyupHandler);
        },
        mounted() {
            const svg_container = SVG(document.getElementById('drawing'));
            this.board = new Board(this, svg_container, this.board_data, this.units, this.hero);
            window.addEventListener('keydown', this.keydownHandler);
            window.addEventListener('keyup', this.keyupHandler);
        },
        beforeDestroy() {
            this.$emit('close_game')
        },
        methods: {
            makeAction(action, action_data) {
                this.$emit('game_action', action, action_data);
            },
            handleAction(actionData) {
                console.log('actionData', actionData);
                this.board.handleAction(actionData);
            },
            keydownHandler(e) {
                this.board.keydownHandler(e);
            },
            keyupHandler(e) {
                this.board.keyupHandler(e);
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
    .btn-circle.btn-xl {
        width: 60px;
        height: 60px;
        padding: 10px 16px;
        border-radius: 30px;
        font-size: 24px;
        line-height: 1.33;
    }

    .btn-circle {
        width: 30px;
        height: 30px;
        padding: 6px 0px;
        border-radius: 15px;
        text-align: center;
        font-size: 12px;
        line-height: 1.42857;
    }
</style>
