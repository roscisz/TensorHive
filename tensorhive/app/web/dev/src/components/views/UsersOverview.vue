<template>
  <section class="content">
    <v-alert
      v-model="alert"
      dismissible
      type="error"
    >
      {{ errorMessage }}
    </v-alert>
    <div>
      <div class="text-xs-center pt-2">
        <v-btn color="primary" @click="createUser()">Create user</v-btn>
      </div>
      <v-dialog v-model="dialog" max-width="500px">
        <v-card>
          <v-card-text>
            Edit user
          </v-card-text>
          <v-card-text>
            <v-card-text>
              New username:
            </v-card-text>
            <v-textarea
              outline
              label="Username"
              v-model="user.username"
            ></v-textarea>
            <v-card-text>
              New password:
            </v-card-text>
            <v-textarea
              outline
              label="Password"
              v-model="user.password"
            ></v-textarea>
            <v-card-text>
              Select roles:
            </v-card-text>
            <v-checkbox
              label="admin"
              v-model="adminCheckbox"
            >
            </v-checkbox>
            <v-checkbox
              label="user"
              v-model="userCheckbox"
            >
            </v-checkbox>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" flat @click="dialog = false">Cancel</v-btn>
            <v-btn color="blue darken-1" flat @click="updateUser">Edit</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
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
                @click="editUser(props.item.id)"
              >
                edit
              </v-icon>
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
      dialog: false,
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
      user: {
        id: -1,
        username: '',
        password: '',
        roles: []
      },
      time: 1000,
      alert: false,
      errorMessage: '',
      userCheckbox: false,
      adminCheckbox: false
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

    editUser: function (id) {
      this.dialog = true
      this.user.id = id
    },

    updateUser: function () {
      if (this.adminCheckbox) {
        this.user.roles.push('admin')
      }
      if (this.userCheckbox) {
        this.user.roles.push('user')
      }
      var updatedUser = {
        id: this.user.id
      }
      if (this.user.username !== '') {
        updatedUser['username'] = this.user.username
      }
      if (this.user.password !== '') {
        updatedUser['password'] = this.user.password
      }
      if (this.user.roles.length > 0) {
        updatedUser['roles'] = this.user.roles
      }
      api
        .request('put', '/user', this.$store.state.accessToken, updatedUser)
        .then(response => {
          this.user = {
            id: -1,
            username: '',
            password: '',
            roles: []
          }
          this.adminCheckbox = false
          this.userCheckbox = false
          this.dialog = false
          this.checkUsers()
        })
        .catch(error => {
          this.pagination = {}
          if (!error.hasOwnProperty('response')) {
            this.errorMessage = error.message
          } else {
            this.errorMessage = error.response.data.msg
          }
          this.alert = true
        })
    },

    checkUsers: function () {
      api
        .request('get', '/users', this.$store.state.accessToken)
        .then(response => {
          this.users = response.data
          this.pagination['totalItems'] = this.users.length
          this.pagination['rowsPerPage'] = 30
        })
        .catch(error => {
          this.pagination = {}
          if (!error.hasOwnProperty('response')) {
            this.errorMessage = error.message
          } else {
            this.errorMessage = error.response.data.msg
          }
          this.alert = true
        })
    },

    deleteUser: function (userId) {
      api
        .request('delete', '/user/delete/' + userId, this.$store.state.accessToken)
        .then(response => {
          this.checkUsers()
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
  }
}
</script>
