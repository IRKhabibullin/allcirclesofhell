<template>
    <b-card no-body style="max-width: 20rem;" v-bind:img-src="hero.img_path" img-alt="Image" img-top>
        <h4 class="m-0" slot="header">{{ hero.name }}</h4>
        <ClassPanel :hero="hero"></ClassPanel>
    </b-card>
</template>

<script>
    import ClassPanel from './ClassPanel'

    import axios from 'axios'
    export default {
        components: {
            ClassPanel
        },

        data () {
            return {
                hero: null
            }
        },

        created() {
            this.getCurrentHero();
            this.getCurrentUserGames();
        },

        methods: {
            getCurrentHero() {
                console.log('Token ' + localStorage.getItem('token'));
                axios.get(localStorage.getItem('endpoint') + '/heroes/1/?format=json', {
                    headers: {
                       Authorization: 'Token ' + localStorage.getItem('token')
                    }
                })
                .then(response => {this.hero = response.data;})
                .catch(error => {
                    console.log('-----error-------');
                    console.log(error);
                })
            },
            getCurrentUserGames() {
                axios.get(localStorage.getItem('endpoint') + '/games/list_by_user/', {
                    headers: {
                       Authorization: 'Token ' + localStorage.getItem('token')
                    }
                })
                .then(response => {
                    console.log('games');
                    console.log(response.data);
                })
                .catch(error => {
                    console.log('Failed to get games');
                    console.log(error);
                })
            }
        }
    }
</script>
