<template>
  <div id="login">
    <div class="text-center col-sm-12">
      <!-- login form -->
      <form @submit.prevent="checkCreds">
        Login to your account
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
        <v-alert
          v-model="alert"
          dismissible
          type="error"
        >
          {{ errorMessage }}
        </v-alert>
        <v-btn
          color="success"
          type="submit"
        >
          Login
        </v-btn>
      </form>
    </div>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'Login',

  data (router) {
    return {
      section: 'Login',
      username: '',
      password: '',
      alert: false,
      errorMessage: ''
    }
  },

  methods: {
    create () {
      this.$router.push('/create')
    },

    checkCreds () {
      const { username, password } = this

      this.toggleLoading()
      this.resetResponse()
      this.$store.commit('TOGGLE_LOADING')
      /* Making API call to authenticate a user */
      api
        .request('post', '/user/login', this.$store.state.accessToken, { 'username': username, 'password': password })
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
          if (username) {
            var accessToken = 'Bearer ' + data.access_token
            var refreshToken = 'Bearer ' + data.refresh_token
            var object = JSON.parse(atob(data.access_token.split('.')[1]))
            var id = object.identity
            var role = object.user_claims.roles.length === 2 ? 'admin' : 'user'
            this.$store.commit('SET_USER', username)
            this.$store.commit('SET_ROLE', role)
            this.$store.commit('SET_ID', id)
            this.$store.commit('SET_ACCESS_TOKEN', accessToken)
            this.$store.commit('SET_REFRESH_TOKEN', refreshToken)

            if (window.localStorage) {
              window.localStorage.setItem('user', JSON.stringify(username))
              window.localStorage.setItem('accessToken', accessToken)
              window.localStorage.setItem('refreshToken', refreshToken)
              window.localStorage.setItem('role', role)
              window.localStorage.setItem('userId', id)
            }
            this.$router.push('/')
          }
        })
        .catch(error => {
          this.errorMessage = error.response.data.msg
          this.alert = true
        })
    },

    logout: function () {
      api
        .request('delete', '/user/logout', this.$store.state.accessToken)
        .catch(error => {
          this.errorMessage = error.response.data.msg
          this.alert = true
        })
      api
        .request('delete', '/user/logout/refresh_token', this.$store.state.refreshToken)
        .catch(error => {
          this.errorMessage = error.response.data.msg
          this.alert = true
        })
      this.$store.commit('SET_USER', null)
      this.$store.commit('SET_ACCESS_TOKEN', null)
      this.$store.commit('SET_REFRESH_TOKEN', null)
      this.$store.commit('SET_ROLE', null)

      if (window.localStorage) {
        window.localStorage.setItem('user', null)
        window.localStorage.setItem('accessToken', null)
        window.localStorage.setItem('refreshToken', null)
        window.localStorage.setItem('role', null)
        window.localStorage.setItem('visibleResources', null)
        window.localStorage.setItem('watches', null)
        window.localStorage.setItem('watchIds', null)
      }
      this.$router.push('/login')
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

<style scoped>
#login {
  padding: 10em;
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
