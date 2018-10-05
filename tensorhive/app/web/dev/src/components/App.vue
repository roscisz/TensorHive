<template>
  <div id="app">
    <v-app>
      <router-view></router-view>
    </v-app>
  </div>
</template>

<script>
export default {
  name: 'App',

  data () {
    return {
      section: 'Head'
    }
  }
}
</script>
