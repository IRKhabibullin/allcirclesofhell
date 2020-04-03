<template>
    <div class="row d-flex justify-content-between">
        <svg id="drawing" class="text-left m-4 col-6"></svg>
        <div class="col-2 height=100%">
            <b-card v-if="!!game_instance && game_instance.current_unit" v-show="game_instance.show_unit_card && game_instance.altPressed">
                <b-card-title>{{ game_instance.current_unit.name }}</b-card-title>
                <b-list-group>
                    <b-list-group-item class="border-0 p-0 d-flex justify-content-between align-items-center">
                        Health
                        <b-badge variant="primary" pill>{{ game_instance.current_unit.health }}</b-badge>
                    </b-list-group-item>
                    <b-list-group-item class="border-0 p-0 d-flex justify-content-between align-items-center">
                        Damage
                        <b-badge variant="primary" pill>{{ game_instance.current_unit.damage }}</b-badge>
                    </b-list-group-item>
                    <b-list-group-item class="border-0 p-0 d-flex justify-content-between align-items-center">
                        Armor
                        <b-badge variant="primary" pill>{{ game_instance.current_unit.armor }}</b-badge>
                    </b-list-group-item>
                </b-list-group>
            </b-card>
        </div>
        <div class="col-2 height=100% m-4">
            <b-card v-if="!!game_instance">
                <b-card-title>Actions</b-card-title>
                <b-list-group class="align-items-center">
                    <b-button
                        variant="info"
                        v-on:click="game_instance.actionManager.changeAction('attack')"
                        v-on:mouseover="game_instance.hero.showAttackHexes(true)"
                        v-on:mouseout="game_instance.hero.showAttackHexes(false)"
                        class="btn btn-danger btn-circle p-0 btn-xl m-1"
                    >
                        <b-img src="./src/assets/sword.png" width=40 height=40 alt="Attack"></b-img>
                    </b-button>
                </b-list-group>
                <b-list-group class="align-items-center">
                    <b-button
                        variant="info"
                        v-on:click="game_instance.actionManager.changeAction('range_attack')"
                        v-on:mouseover="game_instance.hero.showRangeAttackHexes(true)"
                        v-on:mouseout="game_instance.hero.showRangeAttackHexes(false)"
                        class="btn btn-warning btn-circle p-0 btn-xl m-1"
                    >
                        <b-img src="./src/assets/bow.png" width=40 height=40 alt="Range attack"></b-img>
                    </b-button>
                </b-list-group>
                <b-list-group class="align-items-center" v-for="spell in this.game_data.hero.spells">
                    <b-button
                        variant="info"
                        v-bind:title="'Spell: ' + spell.name + '\n' + spell.description"
                        v-on:click="game_instance.actionManager.changeAction(spell.code_name)"
                        class="btn btn-warning btn-circle p-0 btn-xl m-1"
                    >
                        <b-img :src="spell.img_path" width=40 height=40 :alt="spell.name"></b-img>
                    </b-button>
                </b-list-group>
            </b-card>
        </div>
    </div>
</template>

<script>
    import * as SVG from 'svg.js/dist/svg';
    import GameInstance from '../mechanics/game_instance';

    export default {
        props: {
            initial_game_data: {
                type: Object
            }
        },
        data() {
            return {
                game_data: this.initial_game_data,
                svg: null,
                game_instance: null
            }
        },
        destroyed() {
            window.removeEventListener('keydown', this.keydownHandler);
            window.removeEventListener('keyup', this.keyupHandler);
        },
        mounted() {
            console.log('initial', this.initial_game_data);
            this.svg = SVG(document.getElementById('drawing'));
            this.game_instance = new GameInstance(this, this.svg, this.game_data);
            window.addEventListener('keydown', this.keydownHandler);
            window.addEventListener('keyup', this.keyupHandler);
        },
        beforeDestroy() {
            this.$emit('close_game')
        },
        methods: {
            requestAction(action_data) {
                console.log('Requesting action', action_data);
                this.$emit('game_action', action_data);
            },
            handleAction(actionData) {
                this.game_instance.handleAction(actionData);
            },
            updateGame(gameData) {
                this.svg.clear();
                this.game_data = gameData;
                this.game_instance = new GameInstance(this, this.svg, this.game_data);
            },
            keydownHandler(e) {
                if (e.keyCode == 18) {
                    this.game_instance.altPressed = true;
                    this.game_instance.showMoves();
                }
            },
            keyupHandler(e) {
                if (e.keyCode == 18) {
                    this.game_instance.altPressed = false;
                    this.game_instance.hideMoves();
                }
                if (e.keyCode == 65) {
                    this.game_instance.actionManager.changeAction('attack');
                }
                if (e.keyCode == 82) {
                    this.game_instance.actionManager.changeAction('range_attack');
                }
                if (e.keyCode == 77 || e.keyCode == 27) {
                    this.game_instance.actionManager.changeAction('move');
                }
            }
        }
    }
</script>

<style lang="scss">
    .hex {
        stroke-width: 1;
        stroke: grey;
    }

    .obstacle_hex {
        stroke-width: 1;
        stroke: grey;
    }

    .hex:hover {
        stroke-width: 2;
        stroke: #DA4567;
    }
    .spellTarget {
        stroke-width: 2;
        stroke: #DA4567;
    }
    .secondaryTarget, .spellTarget.secondaryTarget {
        stroke: red;
        stroke-width: 3;
    }
    .attackTarget {
        stroke-width: 2;
        stroke: red;
    }
    .availableAttackTarget {
        stroke-width: 2;
        stroke: #e8463a;
    }
    .path {
        stroke: green;
        stroke-width: 2;
    }
    .pathOfFire {
        stroke: red;
        stroke-width: 2;
        fill: orange;
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
