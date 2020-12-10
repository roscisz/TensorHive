<template>
  <v-chip small :color="color" :text-color="textColor">{{ text }}</v-chip>
</template>

<script>
const inactiveStatus = 'not_running'
const runningStatus = 'running'
const terminatedStatus = 'terminated'
const unsynchronizedStatus = 'unsynchronized'

export default {
  props: {
    status: {
      type: String,
      required: true
    }
  },
  computed: {
    color () {
      switch (this.status) {
        case inactiveStatus:
          return 'blue-grey lighten-4'
        case runningStatus:
          return 'blue lighten-4'
        case terminatedStatus:
          return 'red lighten-4'
        case unsynchronizedStatus:
          return 'orange lighten-4'
        default:
          return 'grey lighten-3'
      }
    },
    textColor () {
      switch (this.status) {
        case inactiveStatus:
          return 'blue-grey darken-2'
        case runningStatus:
          return 'blue darken-2'
        case terminatedStatus:
          return 'red darken-2'
        case unsynchronizedStatus:
          return 'orange darken-4'
        default:
          return 'grey darken-1'
      }
    },
    text () {
      switch (this.status) {
        case inactiveStatus:
          return 'Inactive'
        case runningStatus:
          return 'Running'
        case terminatedStatus:
          return 'Terminated'
        case unsynchronizedStatus:
          return 'Unsynchronized'
        default:
          return this.status
      }
    }
  }
}
</script>
