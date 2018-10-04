<template>
  <div id="create">
    <div class="text-center col-sm-12">
      <form @submit.prevent="createUser">
        Create new user
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
          @click="cancel()"
        >
          Cancel
        </v-btn>
        <v-btn
          color="success"
          type="submit"
          :class="'btn btn-primary btn-lg ' + loading"
        >
          Create
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
  name: 'Create',

  data (router) {
    return {
      section: 'Create',
      loading: '',
      username: '',
      password: '',
      response: ''
    }
  },

  methods: {
    cancel () {
      this.$router.push('/users_overview')
    },

    createUser () {
      const { username, password } = this

      this.toggleLoading()
      this.resetResponse()
      this.$store.commit('TOGGLE_LOADING')

      api
        .request('post', '/user/create', this.$store.state.token, { 'username': username, 'password': password })
        .then(response => {
          this.toggleLoading()
          this.$router.push('/users_overview')
        })
        .catch(error => {
          this.$store.commit('TOGGLE_LOADING')
          console.log(error)
          var status = error.response.status
          if (status === 401) {
            this.response = 'Your access token expired. Login again'
          } else if (status === 409) {
            this.response = 'This username is used by other user'
          } else {
            this.response = 'Server appears to be offline'
          }
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

<style scoped>
#create {
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
