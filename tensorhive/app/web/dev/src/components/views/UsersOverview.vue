<template>
  <section class="content">
    <div>
      <div class="text-xs-center pt-2">
        <v-btn color="primary" @click="createUser()">Create user</v-btn>
      </div>
      <v-data-table
        :headers="headers"
        :items="users"
        :search="search"
        :pagination.sync="pagination"
        item-key="id"
        hide-actions
        class="elevation-1"
      >
        <template slot="items" slot-scope="props">
          <tr>
            <td>{{ props.item.id }}</td>
            <td>{{ props.item.username }}</td>
            <td>{{ props.item.createdAt }}</td>
            <td>
              <v-icon
                small
                @click="deleteUser(props.item.id)"
              >
                delete
              </v-icon>
            </td>
          </tr>
        </template>
      </v-data-table>
      <div class="text-xs-center pt-2">
        <v-pagination v-model="pagination.page" :length="pages"></v-pagination>
      </div>
    </div>
  </section>
</template>

<script>
import api from '../../api'
export default {
  data () {
    return {
      search: '',
      pagination: {},
      selected: [],
      headers: [
        { text: 'User id', value: 'id' },
        { text: 'Username', value: 'username' },
        { text: 'Created at', value: 'createdAt' },
        { text: 'Actions', value: 'id' }
      ],
      users: [],
      time: 1000,
      errors: []
    }
  },

  computed: {
    pages () {
      if (this.pagination.rowsPerPage == null ||
        this.pagination.totalItems == null
      ) return 0

      return Math.ceil(this.pagination.totalItems / this.pagination.rowsPerPage)
    }
  },

  mounted () {
    this.checkUsers()
  },
  methods: {
    createUser: function () {
      this.$router.push('/create')
      this.checkUsers()
    },
    checkUsers: function () {
      api
        .request('get', '/users', this.$store.state.token)
        .then(response => {
          this.users = response.data
          this.pagination['totalItems'] = this.users.length
          this.pagination['rowsPerPage'] = 30
        })
        .catch(e => {
          this.pagination = {}
          this.errors.push(e)
        })
    },
    deleteUser: function (userId) {
      api
        .request('delete', '/user/delete/' + userId, this.$store.state.token)
        .then(response => {
          this.checkUsers()
        })
        .catch(e => {
          this.errors.push(e)
        })
    }
  }
}
</script>
