<template>
  <div :class="['wrapper', classes]">
    <v-alert
      v-model="alert"
      dismissible
      type="error"
    >
      {{ errorMessage }}
    </v-alert>
    <header class="main-header">
      <nav
        class="navbar navbar-static-top"
        role="navigation"
      >
        <a
          href="javascript:;"
          class="sidebar-toggle"
          data-toggle="offcanvas"
          role="button"
        >
          <span class="sr-only">Toggle navigation</span>
        </a>
        <v-menu
          class="user_chip"
          :close-on-content-click="false"
          offset-y
        >
          <v-chip
            slot="activator"
            color="green"
            text-color="white"
          >
            <v-avatar>
              <v-icon>account_circle</v-icon>
            </v-avatar>
            {{displayName}}
          </v-chip>

          <v-card>
            <v-avatar>
              <v-icon>account_circle</v-icon>
            </v-avatar>
            {{displayName}}
            <v-divider></v-divider>
            <v-card-actions>
              <v-btn flat @click="logout()">Logout</v-btn>
            </v-card-actions>
          </v-card>
        </v-menu>
      </nav>
    </header>
    <BaseSidebar/>
    <div class="content-wrapper">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
import config from '../config'
import BaseSidebar from './dash/BaseSidebar.vue'
import 'hideseek'
import api from '../api'

export default {
  name: 'TheDash',

  components: {
    BaseSidebar
  },

  data: function () {
    return {
      year: new Date().getFullYear(),
      classes: {
        fixed_layout: config.fixedLayout,
        hide_logo: config.hideLogoOnMobile
      },
      alert: false,
      errorMessage: ''
    }
  },

  computed: {
    displayName () {
      return this.$store.state.user
    }
  },

  methods: {
    changeloading () {
      this.$store.commit('TOGGLE_SEARCHING')
    },

    logout: function () {
      if (this.$store.state.accessToken !== null) {
        api
          .request('delete', '/user/logout', this.$store.state.accessToken)
          .then(response => {
            this.$store.commit('SET_ACCESS_TOKEN', null)

            if (window.localStorage) {
              window.localStorage.setItem('accessToken', null)
            }
            if (this.$store.state.refreshToken !== null) {
              api
                .request('delete', '/user/logout/refresh_token', this.$store.state.refreshToken)
                .then(response => {
                  this.$store.commit('SET_REFRESH_TOKEN', null)
                  if (window.localStorage) {
                    window.localStorage.setItem('refreshToken', null)
                  }
                })
                .catch(error => {
                  if (!error.hasOwnProperty('response')) {
                    this.errorMessage = error.message
                  } else {
                    this.errorMessage = error.response.data.msg
                  }
                  this.alert = true
                })
            }
          })
          .catch(error => {
            if (!error.hasOwnProperty('response')) {
              this.errorMessage = error.message
            } else {
              this.errorMessage = error.response.data.msg
            }
            this.alert = true
          })
      }
      this.$store.commit('SET_USER', null)
      this.$store.commit('SET_ROLE', null)

      if (window.localStorage) {
        window.localStorage.setItem('user', null)
        window.localStorage.setItem('role', null)
        window.localStorage.setItem('visibleResources', null)
        window.localStorage.setItem('watches', null)
        window.localStorage.setItem('watchIds', null)
      }
      this.$router.push('/login')
    }
  }
}
</script>

<style lang="scss">
.user_chip {
  position: absolute;
  right: 0;
  margin-top: 50px;
}
.content-wrapper {
  min-height: 100vh;
}
.wrapper.fixed_layout {
  .main-header {
    position: fixed;
    width: 100%;
    z-index: -1;
  }

  .content-wrapper {
    padding-top: 50px;
  }

  .main-sidebar {
    position: fixed;
    height: 100vh;
  }
}
</style>
