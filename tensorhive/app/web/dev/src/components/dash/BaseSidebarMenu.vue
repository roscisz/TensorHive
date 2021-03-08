<template>
  <ul class="sidebar-menu">
    <li class="header">SCHEDULE</li>
    <router-link
      tag="li"
      class="pageLink"
      to="/reservations_overview"
    >
      <a>
        <i class="fa fa-calendar-check-o"></i>
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
        <i class="fa fa-bar-chart"></i>
        <span class="page">Nodes Overview</span>
      </a>
    </router-link>
    <li class="header">JOBS</li>
    <router-link
      tag="li"
      class="pageLink"
      to="/jobs_overview"
    >
      <a>
        <i class="fa fa-suitcase"></i>
        <span class="page">Jobs Overview</span>
      </a>
    </router-link>
    <li
      class="header"
      v-if="$store.state.role === 'admin'"
    >
      ADMIN ZONE
    </li>
    <router-link
      tag="li"
      class="pageLink"
      to="/users_overview"
      v-if="$store.state.role === 'admin'"
    >
      <a>
        <i class="fa fa-users"></i>
        <span class="page">Users Overview</span>
      </a>
    </router-link>
  </ul>
</template>
<script>
export default {
  name: 'BaseSidebarMenu'
}
</script>
<style>
.fa {
  font-size: 18px;
}
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
