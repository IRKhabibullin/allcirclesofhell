<template>
    <div id="app">
        <!-- <Navbar></Navbar> -->
        <main class="row">
            <aside class="col-2 px-0 ml-4 mt-2 sidebar">
                <div v-if="logged_in">
                    <div>
                        <label>{{ this.username }}</label>
                        <b-button type="reset" variant="danger" v-on:click="setLoginState(false)">Log out</b-button>
                    </div>
                    <CharacterInfo></CharacterInfo>
                </div>
                <LoginPanel @login_state_changed="setLoginState" v-else></LoginPanel>
            </aside>
            <div class="col px-0 playground">
                <Playground></Playground>
            </div>
        </main>
    </div>
</template>

<script>
    import Navbar from './components/Navbar'
    import CharacterInfo from './components/CharacterInfo'
    import Playground from './components/Playground'
    import LoginPanel from './components/LoginPanel'

    localStorage.setItem('endpoint', 'http://localhost:8000');

    export default {
        data() {
            return {
                logged_in: false,
                username: ''
            }
        },
        components: {
            Navbar,
            CharacterInfo,
            Playground,
            LoginPanel
        },
        methods: {
            setLoginState(state, username) {
                this.logged_in = state;
                this.username = username;
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

    sidebar {
        position: absolute;
    }

    playground {
        height: 100%;
    }
</style>
