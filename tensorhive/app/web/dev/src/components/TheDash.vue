<template>
  <div :class="['wrapper', classes]">
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
        <!-- Navbar Right Menu -->
        <div class="navbar-custom-menu">
          <ul class="nav navbar-nav">
          </ul>
        </div>
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
      error: ''
    }
  },

  methods: {
    changeloading () {
      this.$store.commit('TOGGLE_SEARCHING')
    }
  }
}
</script>

<style lang="scss">
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
