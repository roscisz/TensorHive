<template>
  <ul class="sidebar-menu">
    <li class="header">SCHEDULE</li>
    <router-link
      tag="li"
      class="pageLink"
      to="/reservations_overview"
    >
      <a>
        <i class="fa fa-table"></i>
        <span class="page">Reservations Overview</span>
      </a>
    </router-link>
    <li class="header">RESOURCES</li>
    <router-link
      tag="li"
      class="pageLink"
      to="/nodes_overview"
    >
      <a>
        <i class="fa fa-table"></i>
        <span class="page">Nodes Overview</span>
      </a>
    </router-link>
    <li class="header">PAGES</li>
    <router-link
      tag="li"
      class="pageLink"
      to="/login"
    >
      <a>
        <i class="fa fa-circle-o text-yellow"></i>
        <span class="page"> Login</span>
      </a>
    </router-link>
    <router-link
      tag="li"
      class="pageLink"
      to="/register"
    >
      <a>
        <i class="fa fa-circle-o text-green"></i>
        <span class="page"> Register</span>
      </a>
    </router-link>
    <li
      class="pageLink"
    >
      <a>
        <i class="fa fa-circle-o text-red"></i>
        <span @click="logout()" class="page"> Logout</span>
      </a>
    </li>
  </ul>
</template>
<script>
export default {
  name: 'BaseSidebarMenu',

  methods: {
    logout: function () {
      this.$store.commit('SET_USER', null)
      this.$store.commit('SET_TOKEN', null)
      this.$store.commit('SET_ROLE', null)

      if (window.localStorage) {
        window.localStorage.setItem('user', null)
        window.localStorage.setItem('token', null)
        window.localStorage.setItem('role', null)
      }

      this.$router.push('/login')
    }
  }
}
</script>
<style>
/* override default */
.sidebar-menu > li > a {
  padding: 12px 15px 12px 15px;
}

.sidebar-menu li.active > a > .fa-angle-left,
.sidebar-menu li.active > a > .pull-right-container > .fa-angle-left {
  animation-name: rotate;
  animation-duration: 0.2s;
  animation-fill-mode: forwards;
}

.treeview-title {
  z-index: 1;
}

@keyframes rotate {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(-90deg);
  }
}
</style>
