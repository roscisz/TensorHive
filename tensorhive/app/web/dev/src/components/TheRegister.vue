<template>
  <div id="login">
    <div class="text-center col-sm-12">
      <form @submit.prevent="checkCreds">
        Register new user
        <div class="input-group">
          <span class="input-group-addon"><i class="fa fa-envelope"></i></span>
          <input
            class="form-control"
            name="username"
            placeholder="Username"
            type="text"
            v-model="username"
          >
        </div>

        <div class="input-group">
          <span class="input-group-addon"><i class="fa fa-lock"></i></span>
          <input
            class="form-control"
            name="password"
            placeholder="Password"
            type="password"
            v-model="password"
          >
        </div>
        <v-btn
          color="info"
          small
          outline
          round
          @click="login()"
          :class="'btn btn-primary btn-lg ' + loading"
        >
          Login
        </v-btn>
        <v-btn
          color="success"
          type="submit"
          :class="'btn btn-primary btn-lg ' + loading"
        >
          Register
        </v-btn>
      </form>

      <!-- errors -->
      <div v-if=response class="text-red"><p class="vertical-5p lead">{{response}}</p></div>
    </div>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'Register',

  data (router) {
    return {
      section: 'Register',
      loading: '',
      username: '',
      password: '',
      response: ''
    }
  },

  methods: {
    login () {
      this.$router.push('/login')
    },

    checkCreds () {
      const { username, password } = this

      this.toggleLoading()
      this.resetResponse()
      this.$store.commit('TOGGLE_LOADING')

      /* Making API call to authenticate a user */
      api
        .request('post', '/user/register', this.$store.state.token, { 'username': username, 'password': password })
        .then(response => {
          this.toggleLoading()

          var data = response.data
          /* Checking if error object was returned from the server */
          if (data.error) {
            var errorName = data.error.name
            if (errorName) {
              this.response =
                errorName === 'InvalidCredentialsError'
                  ? 'Username/Password incorrect. Please try again.'
                  : errorName
            } else {
              this.response = data.error
            }

            return
          }

          /* Setting user in the state and caching record to the localStorage */
          if (data.username) {
            var token = 'Bearer ' + data.access_token
            this.$store.commit('SET_USER', data.username)
            this.$store.commit('SET_ID', data.id)
            this.$store.commit('SET_TOKEN', token)
            if (window.localStorage) {
              window.localStorage.setItem('user', JSON.stringify(data.username))
              window.localStorage.setItem('token', token)
            }
            this.$router.push('/')
          }
        })
        .catch(error => {
          this.$store.commit('TOGGLE_LOADING')
          console.log(error)

          this.response = 'Server appears to be offline'
          this.toggleLoading()
        })
    },

    toggleLoading () {
      this.loading = this.loading === '' ? 'loading' : ''
    },

    resetResponse () {
      this.response = ''
    }
  }
}
</script>

<style>
#login {
  padding: 10em;
}

html,
body,
.container-table {
  height: 100%;
  background-color: #282b30 !important;
}
.container-table {
  display: table;
  color: white;
}
.vertical-center-row {
  display: table-cell;
  vertical-align: middle;
}
.vertical-20p {
  padding-top: 20%;
}
.vertical-10p {
  padding-top: 10%;
}
.vertical-5p {
  padding-top: 5%;
}
.logo {
  width: 15em;
  padding: 3em;
}

.input-group {
  padding-bottom: 2em;
  height: 4em;
  width: 100%;
}

.input-group span.input-group-addon {
  width: 2em;
  height: 4em;
}

@media (max-width: 1241px) {
  .input-group input {
    height: 4em;
  }
}
@media (min-width: 1242px) {
  form {
    padding-left: 20em;
    padding-right: 20em;
  }

  .input-group input {
    height: 6em;
  }
}

.input-group-addon i {
  height: 15px;
  width: 15px;
}
</style>
