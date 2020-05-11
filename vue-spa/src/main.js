import Vue from 'vue'
import BootstrapVue from 'bootstrap-vue'
import App from './App.vue'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import './styles/custom.css'
import Axios from 'axios'

Vue.prototype.$http = Axios;
Vue.use(BootstrapVue)

new Vue({
  el: '#app',
  render: h => h(App)
})
