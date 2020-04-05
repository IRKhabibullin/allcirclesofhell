<template>
    <div id="app">
        <main class="row">
            <aside class="col-2 px-0 pl-4 pt-2">
                <div class="text-left" v-if="game_state != 'logged_out'">
                    <b-dropdown id="dropdown-1" text="Settings" class="m-md-2">
                        <b-dropdown-item disabled>{{ this.username }}</b-dropdown-item>
                        <b-dropdown-divider v-if="game_state == 'game_loaded'"></b-dropdown-divider>
                        <b-dropdown-item v-if="game_state == 'game_loaded'" v-on:click="setLoginState('logged_in')">Games list</b-dropdown-item>
                        <b-dropdown-item v-if="game_state == 'game_loaded'" v-on:click="saveState">Save state</b-dropdown-item>
                        <b-dropdown-item v-if="game_state == 'game_loaded'" v-on:click="loadState">Load state</b-dropdown-item>
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-item variant="danger" v-on:click="setLoginState('logged_out')">Log out</b-dropdown-item>
                    </b-dropdown>
                </div>
                <LoginPanel @login_state_changed="setLoginState" v-if="game_state == 'logged_out'"></LoginPanel>
                <GamesList
                    @new_game="startNew"
                    @start_round="startRound"
                    @load_state="loadState"
                    v-else-if="game_state == 'logged_in'"
                ></GamesList>
                <CharacterInfo :hero="game_data.hero" v-else-if="game_state == 'game_loaded'"></CharacterInfo>
                <b-alert
                    :show="dismissCountDown"
                    fade
                    variant="success"
                    @dismiss-count-down="countDownChanged"
                >{{ alertMessage }}</b-alert>
            </aside>
            <b-overlay :show="playgroundOverlay" class="col-10 p-0 m-0">
                <Playground
                    :initial_game_data="game_data"
                    v-if="game_state == 'game_loaded'"
                    @game_action="requestAction"
                    @close_game="closeGame"
                    ref="playground"
                >
                </Playground>

                <template v-slot:overlay>
                    <div class="text-center">
                        <p>Congratulations! Round is finished!</p>
                        <b-button variant="outline-success" size="sm" @click="playgroundOverlay = false">
                            Start next round
                        </b-button>
                    </div>
                </template>
            </b-overlay>

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
                game_data: null,
                dismissSecs: 5,
                dismissCountDown: 0,
                alertMessage: '',
                playgroundOverlay: false
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
            startRound(game_id) {
                this.$http.get(localStorage.getItem('endpoint') + '/games/' + game_id, {
                    headers: {
                       Authorization: 'Token ' + localStorage.getItem('token')
                    }
                })
                .then(response => {
                    this.game_data = response.data;
                    console.log('New game', this.game_data);
                    this.game_state = 'game_loaded';
                })
                .catch(error => {
                    console.log('Failed to get game', error);
                })
            },
            saveState() {
                let data = {
                    'game_id': this.game_data.game_id
                }
                this.$http.post(localStorage.getItem('endpoint') + '/games/save_state/', data, {
                    headers: {
                       Authorization: 'Token ' + localStorage.getItem('token')
                    }
                })
                .then(response => {
                    this.showAlert('Game is saved')
                })
                .catch(error => {
                    console.log('Failed to save state', error);
                })
            },
            loadState() {
                let data = {
                    'game_id': this.game_data.game_id
                }
                this.$http.post(localStorage.getItem('endpoint') + '/games/load_state/', data, {
                    headers: {
                       Authorization: 'Token ' + localStorage.getItem('token')
                    }
                })
                .then(response => {
                    this.game_data = response.data;
                    console.log('Loaded state', this.game_data);
                    this.$refs.playground.updateGame(response.data);
                    this.showAlert('Game is loaded');
                })
                .catch(error => {
                    console.log('Failed to load state', error);
                })
            },
            startNew(newHeroName) {
                let data = {
                    'hero': {
                        'name': newHeroName
                    }
                }
                this.$http.post(localStorage.getItem('endpoint') + '/games/', data, {
                    headers: {
                       Authorization: 'Token ' + localStorage.getItem('token')
                    }
                })
                .then(response => {
                    this.game_data = response.data;
                    console.log('New game', this.game_data);
                    this.game_state = 'game_loaded';
                })
                .catch(error => {
                    console.log('Failed to get game', error);
                })
            },
            requestAction(action_data) {
                action_data['game_id'] = this.game_data.game_id
                this.$http.post(localStorage.getItem('endpoint') + '/game/', action_data, {
                    headers: {
                       Authorization: 'Token ' + localStorage.getItem('token')
                    }
                })
                .then(response => {
                    this.game_data.hero = response.data.hero;
                    if (response.data.action_data.action == 'exit' && response.data.action_data.state == 'success') {
                        this.playgroundOverlay = true;
                        this.$refs.playground.updateGame(response.data);
                        // this.showAlert('You have passed to a new round!');
                    } else {
                        this.$refs.playground.handleAction(response.data);
                    }
                })
                .catch(error => {
                    console.log('Failed to handle action', error);
                })
            },
            closeGame() {
                let data = {
                    'game_id': this.game_data.game_id
                }
                this.$http.post(localStorage.getItem('endpoint') + '/games/close_game/', data, {
                    headers: {
                       Authorization: 'Token ' + localStorage.getItem('token')
                    }
                })
                .then(response => {})
                .catch(error => {
                    console.log('Failed to close game', error);
                })
            },
            countDownChanged(dismissCountDown) {
                this.dismissCountDown = dismissCountDown;
            },
            showAlert(message) {
                this.alertMessage = message;
                this.dismissCountDown = this.dismissSecs;
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
