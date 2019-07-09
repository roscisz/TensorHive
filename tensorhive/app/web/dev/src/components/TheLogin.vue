<template>
  <div id="login">
    <v-layout row justify-center>
      <v-dialog
        persistent
        width="50vw"
        v-model="showModal"
      >
        <v-card>
          <v-card-title>
            <span class="headline">Register new account</span>
          </v-card-title>
          <v-card-text>
            <form @submit.prevent="createUser">
              <div class="input-group">
                <span class="input-group-addon"><i class="fa fa-user"></i></span>
                <input
                  class="form-control"
                  name="modalUsername"
                  placeholder="UNIX username"
                  type="text"
                  v-model="modalUsername"
                >
              </div>
              <div class="input-group">
                <span class="input-group-addon"><i class="fa fa-envelope"></i></span>
                <input
                  class="form-control"
                  name="modalEmail"
                  placeholder="Email"
                  type="text"
                  v-model="modalEmail"
                >
              </div>
              <div class="input-group">
                <span class="input-group-addon"><i class="fa fa-lock"></i></span>
                <input
                  class="form-control"
                  name="modalPassword"
                  placeholder="Password"
                  type="password"
                  v-model="modalPassword"
                >
              </div>
              <div class="input-group">
                <span class="input-group-addon"><i class="fa fa-lock"></i></span>
                <input
                  class="form-control"
                  name="modalPassword2"
                  placeholder="Repeat password"
                  type="password"
                  v-model="modalPassword2"
                >
              </div>
              Please copy the key below and paste it into <b>~/.ssh/authorized_keys</b>.<br>It will allow TensorHive to confirm you identity and access machines with provided UNIX username.
              <v-textarea
                solo
                name="entry"
                :value="entry"
                id="entry">
              </v-textarea>
              <v-btn
                color="info"
                @click="copyEntryToClipboard"
                small
              >Copy to clipboard</v-btn>
              <br>
              <v-alert
                v-model="modalAlert"
                dismissible
                type="error"
              >
                {{ errorMessage }}
              </v-alert>
              <v-btn
                color="info"
                small
                outline
                round
                @click="showModal=false"
              >
                Go back
              </v-btn>
              <v-btn
                color="success"
                type="submit"
              >
                Register
              </v-btn>
            </form>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-layout>
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
        <v-alert
          v-model="created"
          dismissible
          type="info"
        >
          Identity verification succeeded, account has been successfully created. You can now log in.
        </v-alert>
        <v-btn color="info" @click="requestEntry">Register</v-btn>
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
      modalUsername: '',
      modalEmail: '',
      modalPassword: '',
      modalPassword2: '',
      alert: false,
      modalAlert: false,
      created: false,
      errorMessage: '',
      showModal: false,
      entry: ''
    }
  },

  methods: {
    handleError: function (error) {
      if (!error.hasOwnProperty('response')) {
        this.errorMessage = error.message
      } else {
        if (!error.response.data.hasOwnProperty('msg')) {
          this.errorMessage = error.response.data
        } else {
          this.errorMessage = error.response.data.msg
        }
      }
    },

    requestEntry () {
      api
        .request('get', '/user/authorized_keys_entry', this.$store.state.accessToken)
        .then(response => {
          this.entry = response.data
          this.showModal = true
        })
        .catch(error => {
          this.handleError(error)
          this.modalAlert = true
        })
    },
    copyEntryToClipboard () {
      let entryInput = document.querySelector('#entry')
      entryInput.setAttribute('type', 'text')
      entryInput.select()
      try {
        if (document.execCommand('copy')) {
          alert('Authorized keys entry is in your clipboard')
        } else {
          alert('Something went wrong, try again')
        }
      } catch (e) {
        alert('Unable to copy')
      }
      window.getSelection().removeAllRanges()
    },
    createUser () {
      if (this.modalPassword === this.modalPassword2) {
        const { modalUsername, modalEmail, modalPassword } = this
        api
          .request('post', '/user/ssh_signup', this.$store.state.accessToken, { 'username': modalUsername, 'email': modalEmail, 'password': modalPassword })
          .then(response => {
            this.showModal = false
            this.created = true
          })
          .catch(error => {
            this.handleError(error)
            this.modalAlert = true
          })
      } else {
        this.errorMessage = 'Passwords do not match'
        this.modalAlert = true
      }
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
          this.handleError(error)
          this.alert = true
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
