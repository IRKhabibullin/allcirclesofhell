<template>
  <div>
    <b-navbar toggleable="lg" type="dark" variant="info">
      <b-navbar-brand href="#">All circles of hell</b-navbar-brand>

      <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

      <b-collapse id="nav-collapse" is-nav>
        <b-navbar-nav>
          <b-nav-item href="#">Link</b-nav-item>
          <b-nav-item href="#" disabled>Disabled</b-nav-item>
        </b-navbar-nav>

        <!-- Right aligned nav items -->
        <b-navbar-nav class="ml-auto">
          <b-button right v-on:click="reverseMessage" v-if="logged_in">Log out</b-button>
          <!-- <LoginPanel v-else></LoginPanel> -->
        </b-navbar-nav>
      </b-collapse>
    </b-navbar>
  </div>
</template>

<script>
    import LoginPanel from './LoginPanel'

    export default {
        components: {
            LoginPanel
        },
        data () {
            return {
                logged_in: false
            }
        },
        methods: {
            reverseMessage() {
                this.logged_in = !this.logged_in;
            },
            getToken(user, pass) {
                axios.post(localStorage.getItem('endpoint') + '/api-token-auth/', {
                    username: user,
                    password: pass
                })
                .then(response => {
                    localStorage.setItem('token', response.data.token);
                })
                .catch(error => {
                    console.log('Failed to get token');
                    console.log(error);
                })
            }
        }
    }
</script>
