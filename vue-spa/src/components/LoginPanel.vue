<template>
    <div>
        <b-form @submit="logIn" @reset="logOut" v-if="show">
          <b-form-group id="input-group-1" label="Username:" label-for="input-1">
            <b-form-input
              id="input-1"
              v-model="form.username"
              required
              placeholder="Enter username"
            ></b-form-input>
          </b-form-group>

          <b-form-group id="input-group-2" label="Password:" label-for="input-2">
            <b-form-input
              id="input-2"
              type="password"
              v-model="form.password"
              required
              placeholder="Enter password"
            ></b-form-input>
          </b-form-group>

          <b-button type="submit" variant="primary">Log in</b-button>
          <b-button type="reset" variant="danger">Log out</b-button>
        </b-form>
    </div>
</template>

<script>
    import axios from 'axios'

    export default {
        data() {
            return {
                form: {
                    username: '',
                    password: ''
                },
                show: true
            }
        },
        methods: {
            logIn(evt) {
                evt.preventDefault();
                axios.post(localStorage.getItem('endpoint') + '/api-token-auth/', {
                    username: this.form.username,
                    password: this.form.password
                })
                .then(response => {
                    localStorage.setItem('token', response.data.token);
                    this.$emit('login_state_changed', true, this.form.username);
                })
                .catch(error => {
                    console.log('Failed to log in');
                    console.log(error);
                    alert(JSON.stringify('Wrong creds for user ' + this.form.username));
                    this.form.password = '';
                });
            },
            logOut(evt) {
                evt.preventDefault()
                this.form.username = '';
                this.form.password = '';
                // Trick to reset/clear native browser form validation state
                this.show = false;
                this.$nextTick(() => {
                  this.show = true;
                });
            },
            loginState(state) {
                this.$emit('login_state_changed', state, this.form.username);
            }
        }
    }
</script>

<style lang="scss">

</style>
