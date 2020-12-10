<template>
  <div>
    <span v-if="!loading">{{ username || userId }}</span>
    <v-progress-linear
      v-if="loading"
      indeterminate
      color="primary"
      :height="4"
    ></v-progress-linear>
  </div>
</template>

<script>
import api from '../../../api'

export default {
  data () {
    return {
      username: undefined,
      loading: true
    }
  },
  props: {
    userId: {
      type: Number,
      required: true
    }
  },
  mounted () {
    api
      .request('get', `/users/${this.userId}`, this.$store.state.accessToken)
      .then(response => response.data.user)
      .then(user => {
        this.username = user.username
        this.loading = false
      })
      .catch(() => {
        this.loading = false

        this.$emit(
          'error',
          new Error(
            `Could not fetch a username of the user with id '${this.userId}'`
          )
        )
      })
  }
}
</script>
