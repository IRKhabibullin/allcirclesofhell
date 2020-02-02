<template>
    <b-list-group class="align-items-center justify-content-start">
        <b-card-title>Games list</b-card-title>
        <!-- another b-list-group-item for new game creating -->
        <b-list-group-item href="#" class="flex-column" v-on:click="startNew">
            <small>Start new</small>
        </b-list-group-item>
        <b-list-group-item href="#"
            class="flex-column"
            v-for="game in games"
            v-on:mouseover="gameDetails(game.game_id, true)"
            v-on:mouseout="gameDetails(game.game_id, false)"
        >
            <h5 class="mb-1 ">Hero: {{ game.hero_name }}</h5>
            <div v-bind:id="'game_details_' + game.game_id" style="display: none">
                <small>Created: {{ game.created }}</small>
                <b-badge variant="secondary">Round: {{ game.round }}</b-badge>
                <b-badge href="#" variant="success" pill v-on:click="gameSelected(game.game_id)">Play</b-badge>
                <b-badge href="#" variant="danger" pill v-on:click="deleteGame(game.game_id)">Delete</b-badge>
            </div>
        </b-list-group-item>
    </b-list-group>
</template>

<script>
    import axios from 'axios'

    export default {
        data () {
            return {
                games: []
            }
        },

        created() {
            this.getCurrentUserGames();
        },

        methods: {
            getCurrentUserGames() {
                this.$http.get(localStorage.getItem('endpoint') + '/games/list_by_user/', {
                    headers: {
                       Authorization: 'Token ' + localStorage.getItem('token')
                    }
                })
                .then(response => {
                    this.games = response.data
                })
                .catch(error => {
                    console.log('Failed to get games');
                    // todo need to display it in b-list-group
                    console.log(error);
                })
            },
            deleteGame(game_id) {
                this.$http.delete(localStorage.getItem('endpoint') + '/games/' + game_id, {
                    headers: {
                       Authorization: 'Token ' + localStorage.getItem('token')
                    }
                })
                .then(response => {
                    console.log('Deleted game', response.data);
                    this.getCurrentUserGames();
                })
                .catch(error => {
                    console.log('Failed to delete game', error);
                })
            },
            gameDetails(game_id, toShow) {
                let game_details = document.getElementById('game_details_' + game_id);
                game_details.setAttribute('style', 'display: ' + (toShow ? 'inline' : 'none'))
            },
            gameSelected(game_id) {
                this.$emit('game_selected', game_id);
            },
            startNew() {
                this.$emit('start_new');
            }
        }
    }
</script>
