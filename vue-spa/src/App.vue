<template>
      <div id="app">
            <Navbar></Navbar>
            <main class="row">
                  <aside class="col-2 px-0 sidebar">
                      <CharacterInfo></CharacterInfo>
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

    export default {
        components: {
            Navbar,
            CharacterInfo,
            Playground
        },
        data () {
            return {
                posts: ['First row', 'Second row']
            }
        },
        methods: {
            
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
