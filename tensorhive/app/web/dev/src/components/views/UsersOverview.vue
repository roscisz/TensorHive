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
            <v-card-text>
              Edit user
            </v-card-text>
            <v-card-text>
              Current username: {{currentUser.username}}
            </v-card-text>
            <v-card-text>
              New username
            </v-card-text>
            <div class="input-group">
              <span class="input-group-addon"><i class="fa fa-envelope"></i></span>
              <input
                class="form-control"
                name="modalUsername"
                placeholder="Username"
                type="text"
                v-model="user.username"
              >
            </div>
            <v-card-text>
              New password
            </v-card-text>
            <div class="input-group">
              <span class="input-group-addon"><i class="fa fa-lock"></i></span>
              <input
                class="form-control"
                name="modalPassword"
                placeholder="Password"
                type="password"
                v-model="user.password"
              >
            </div>
            <v-card-text>
              Repeat password
            </v-card-text>
            <div class="input-group">
              <span class="input-group-addon"><i class="fa fa-lock"></i></span>
              <input
                class="form-control"
                name="modalPassword2"
                placeholder="Password2"
                type="password"
                v-model="user.password2"
              >
            </div>
            <v-card-text>
              Account roles:
            </v-card-text>
            <v-card-text>
              <v-checkbox
                label="admin"
                v-model="adminCheckbox"
              >
              </v-checkbox>
            </v-card-text>
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
            <td>{{ props.item.role }}</td>
            <td>
              <v-icon
                small
                @click="editUser(props.item)"
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
        { text: 'Role', value: 'role' },
        { text: 'Actions', value: 'id' }
      ],
      users: [],
      user: {
        id: -1,
        username: '',
        password: '',
        password2: '',
        roles: []
      },
      currentUser: {},
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

    editUser: function (currentUser) {
      this.dialog = true
      this.user.id = currentUser.id
      var admin = false
      for (var role in currentUser.roles) {
        if (currentUser.roles[role] === 'admin') {
          admin = true
        }
      }
      this.adminCheckbox = admin
      this.currentUser = currentUser
    },

    updateUser: function () {
      if (this.user.password === this.user.password2) {
        if (this.adminCheckbox) {
          this.user.roles.push('admin')
        }
        this.user.roles.push('user')
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
              password2: '',
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
      } else {
        this.errorMessage = 'Passwords do not match'
        this.alert = true
      }
    },
    checkUsers: function () {
      api
        .request('get', '/users', this.$store.state.accessToken)
        .then(response => {
          this.users = response.data
          for (var user in this.users) {
            var admin = false
            for (var role in this.users[user].roles) {
              if (this.users[user].roles[role] === 'admin') {
                admin = true
              }
            }
            if (admin) {
              this.users[user]['role'] = 'admin'
            } else {
              this.users[user]['role'] = 'user'
            }
          }
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
