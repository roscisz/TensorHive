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
      <span class="logo-mini">
      </span>
      <!-- Header Navbar -->
      <nav
        class="navbar navbar-static-top"
        role="navigation"
      >
        <!-- Sidebar toggle button-->
        <a
          href="javascript:;"
          class="sidebar-toggle"
          data-toggle="offcanvas"
          role="button"
        >
          <span class="sr-only">Toggle navigation</span>
        </a>
        <v-chip
          class="user_chip"
          close
          v-model="loggedIn"
          color="green"
          text-color="white"
        >
          <v-avatar>
            <v-icon>check_circle</v-icon>
          </v-avatar>
          {{displayName}}
        </v-chip>
      </nav>
    </header>
    <!-- Left side column. contains the logo and sidebar -->
    <BaseSidebar/>
    <!-- Content Wrapper. Contains page content -->
    <div class="content-wrapper">
      <!-- Content Header (Page header) -->
      <section class="content-header">
        <h1>
          {{$route.name }}
          <small>{{ $route.meta.description }}</small>
        </h1>
        <ol class="breadcrumb">
          <li>
            <a href="javascript:;">
              <i class="fa fa-home"></i>Home</a>
          </li>
          <li class="active">{{$route.name}}</li>
        </ol>
      </section>
      <router-view></router-view>
    </div>
    <!-- /.content-wrapper -->
    <!-- Main Footer -->
    <footer class="main-footer">
    </footer>
  </div>
  <!-- ./wrapper -->
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
      // section: 'Dash',
      year: new Date().getFullYear(),
      classes: {
        fixed_layout: config.fixedLayout,
        hide_logo: config.hideLogoOnMobile
      },
      loggedIn: true,
      alert: false,
      errorMessage: ''
    }
  },

  computed: {
    displayName () {
      return this.$store.state.user
    }
  },

  watch: {
    loggedIn () {
      if (this.loggedIn === false) {
        this.logout()
      }
    }
  },

  methods: {
    changeloading () {
      this.$store.commit('TOGGLE_SEARCHING')
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
    }
  }
}
</script>

<style lang="scss">
.user_chip {
  margin-top: 8px;
}
.wrapper.fixed_layout {
  .main-header {
    position: fixed;
    width: 100%;
  }

  .content-wrapper {
    padding-top: 50px;
  }

  .main-sidebar {
    position: fixed;
    height: 100vh;
  }
}

.wrapper.hide_logo {
  @media (max-width: 767px) {
    .main-header .logo {
      display: none;
    }
  }
}

.logo-mini,
.logo-lg {
  text-align: left;

  img {
    padding: .4em !important;
  }
}

.logo-lg {
  img {
    display: -webkit-inline-box;
    width: 25%;
  }
}

.user-panel {
  height: 4em;
}

hr.visible-xs-block {
  width: 100%;
  background-color: rgba(0, 0, 0, 0.17);
  height: 1px;
  border-color: transparent;
}
</style>
