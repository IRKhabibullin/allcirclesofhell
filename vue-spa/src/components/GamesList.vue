<template>
    <b-list-group class="align-items-start justify-content-start">
        <!-- another b-list-group-item for new game creating -->
        <b-list-group-item href="#" class="flex-column" v-for="game in games" v-on:click="gameSelected(game.game_id)">
            <div>
                <h5 class="mb-1 ">Hero: {{ game.hero_name }}</h5>
                <p class="mb-1">Round: {{ game.round }}</p>
                <small>Hp: {{ game.hero_hp }}</small>
            </div>
            <b-badge variant="primary" pill>Round: {{ game.round }}</b-badge>
            <small>Created: {{ game.created }}</small>
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
            gameSelected(game_id) {
                this.$emit('game_selected', game_id);
            }
        }
    }
</script>
