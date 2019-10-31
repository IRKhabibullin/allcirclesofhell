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
        props: {
            hero: Object
        }
    }
</script>
