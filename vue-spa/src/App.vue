<template>
    <div id="app">
        <main class="row">
            <aside class="col-2 px-0 ml-4 mt-2">
                <div v-show="game_state !== 'logged_out'">
                    <label>{{ this.username }}</label>
                    <b-button type="reset" variant="danger" v-on:click="setLoginState('logged_out')">Log out</b-button>
                </div>
                <LoginPanel @login_state_changed="setLoginState" v-if="game_state === 'logged_out'"></LoginPanel>
                <GamesList @game_selected="getGameById" v-else-if="game_state === 'logged_in'"></GamesList>
                <CharacterInfo :hero="game_info.game.hero" v-else-if="game_state === 'game_loaded'"></CharacterInfo>
                <b-button type="reset" variant="danger" v-if="game_state === 'game_loaded'" v-on:click="setLoginState('logged_in')">Games list</b-button>
            </aside>
            <Playground
                :units="game_info.units"
                :board_data="game_info.board"
                v-if="game_state === 'game_loaded'"
                class="col-10 px-0"
                @game_action="makeAction"
                @close_game="closeGame"
                ref="playground"
            ></Playground>
        </main>
    </div>
</template>

<script>
    import Navbar from './components/Navbar'
    import CharacterInfo from './components/CharacterInfo'
    import Playground from './components/Playground'
    import LoginPanel from './components/LoginPanel'
    import GamesList from './components/GamesList'

    localStorage.setItem('endpoint', 'http://localhost:8000');

    export default {
        data() {
            return {
                // game states:
                //     logged_out
                //     logged_in
                //     game_loaded
                //
                //
                game_state: 'logged_out',
                username: '',
                game_info: null
            }
        },
        components: {
            Navbar,
            CharacterInfo,
            Playground,
            LoginPanel,
            GamesList
        },
        methods: {
            setLoginState(state, username) {
                this.game_state = state;
                this.username = username;
            },
            getGameById(game_id) {
                this.$http.get(localStorage.getItem('endpoint') + '/games/' + game_id, {
                    headers: {
                       Authorization: 'Token ' + localStorage.getItem('token')
                    }
                })
                .then(response => {
                    this.game_info = response.data;
                    console.log('got game');
                    console.log(this.game_info);
                    this.game_state = 'game_loaded';
                })
                .catch(error => {
                    console.log('Failed to get game');
                    console.log(error);
                })
            },
            makeAction(action, destination) {
                console.log('making action in app')
                let action_data = {
                    'action': action,
                    'game_id': this.game_info.game.pk,
                    'destination': destination
                }
                this.$http.post(localStorage.getItem('endpoint') + '/game/', action_data, {
                    headers: {
                       Authorization: 'Token ' + localStorage.getItem('token')
                    }
                })
                .then(response => {
                    this.$refs.playground.handleAction(response.data);
                })
                .catch(error => {
                    console.log('Failed to handle action');
                    console.log(error);
                })
            },
            closeGame() {
                let data = {
                    'game_id': this.game_info.game.pk
                }
                this.$http.post(localStorage.getItem('endpoint') + '/games/close_game/', data, {
                    headers: {
                       Authorization: 'Token ' + localStorage.getItem('token')
                    }
                })
                .then(response => {})
                .catch(error => {
                    console.log('Failed to close game');
                    console.log(error);
                })
            }
        }
    }
</script>

<style lang="scss">
    html, body {
        margin: 0;
        height: 100%;
    }

    #app {
        font-family: 'Avenir', Helvetica, Arial, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-align: center;
        color: #2c3e50;
        height: 100%;
    }
</style>
