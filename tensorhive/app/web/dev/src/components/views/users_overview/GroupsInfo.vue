<template>
    <section class="content">
      <v-alert
      v-model="alert"
      dismissible
      type="error"
    >
      {{ errorMessage }}
    </v-alert>
    <v-dialog
        width="500px"
        v-model="showModalCreateGroup"
      >
      <v-card>
        <v-card-text>
            <v-btn
              class="float-right-button"
              flat
              icon
              color="black"
              @click="showModalCreateGroup=false"
            >
              <v-icon>close</v-icon>
            </v-btn>
            <span class="headline">Create new group</span>
          </v-card-text>
          <v-card-text>
            <form @submit.prevent="createGroup">
              <v-card-text>
                Group name
              </v-card-text>
              <div class="input-group">
                <span class="input-group-addon"><i class="fa fa-info"></i></span>
                <input
                  class="form-control"
                  name="modalGroupName"
                  placeholder="Group name"
                  type="text"
                  v-model="modalGroupName"
                >
              </div>
              <v-card-text>
              Group members
              </v-card-text>
              <v-autocomplete
                v-model="usersValue"
                :items="usersList"
                :multiple=true
                placeholder="Username"
                item-text="username"
                item-value="id"
                prepend-icon="fa-group"
              />
              <v-alert
                v-model="modalAlert"
                dismissible
                type="error"
              >
                {{ errorMessage }}
              </v-alert>
              <v-btn
                color="success"
                type="submit"
              >
                Create
              </v-btn>
            </form>
          </v-card-text>
      </v-card>
    </v-dialog>
    <v-dialog
      v-model="showModalEditGroup"
      width="500px"
    >
      <v-card>
        <v-card-text>
          <v-btn
            class="float-right-button"
            flat
            icon
            color="black"
            @click="showModalEditGroup = false"
          >
            <v-icon>close</v-icon>
          </v-btn>
          <v-card-text>
              Edit group current group: {{currentGroup.name}}
          </v-card-text>
          <v-card-text>
              New group name
          </v-card-text>
          <div class="input-group">
                <span class="input-group-addon"><i class="fa fa-info"></i></span>
                <input
                  v-model="group.name"
                  class="form-control"
                  name="modalGroupName"
                  placeholder="Group name"
                  type="text"
                >
          </div>
          <v-card-text>
              Edit group members
          </v-card-text>
          <v-autocomplete
              v-model="group.users"
              :items="usersList"
              :multiple=true
              placeholder="Username"
              item-value="id"
              item-text="username"
              prepend-icon="fa-group"
              return-object
            />
          <v-alert
            v-model="modalAlert"
            dismissible
            type="error"
          >
            {{ errorMessage }}
          </v-alert>
          <v-btn
            color="blue darken-1"
            flat @click="updateGroup"
          >
            Edit
          </v-btn>
        </v-card-text>
      </v-card>
    </v-dialog>
    <v-dialog
      v-model="showModalRemoveGroup"
      width="400"
    >
      <v-card>
        <v-card-text
          class="headline grey lighten-2"
          primary-title
        >
          <v-btn
            class="float-right-button"
            flat
            icon
            color="black"
            @click="showModalRemoveGroup=false"
          >
            <v-icon>close</v-icon>
          </v-btn>
          Do you want to remove this group?
        </v-card-text>
        <v-card-actions>
          <v-layout align-center justify-end>
            <v-btn
              color="success"
              round
              @click="removeGroup()"
            >
              Yes
            </v-btn>
          </v-layout>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <div>
      <div class="text-xs-center pt-2">
        <v-btn color="primary" @click="showModalCreateGroup=true">Create group</v-btn>
        Total: {{ numGroups }}
      </div>
      <v-data-table
        :headers="groupHeaders"
        :items="groups"
        :pagination.sync="pagination"
        item-key="id"
        hide-actions
        class="elevation-1"
      >
        <template slot="items" slot-scope="props">
          <tr>
            <td>{{ props.item.id }}</td>
            <td>{{ props.item.name }}</td>
            <td>{{ prettyDate(props.item.createdAt) }}</td>
            <td>
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <span v-bind="attrs" v-on="on">{{ props.item.users.length }}</span>
                </template>
                <span>{{ printUsernames(props.item.users) }}</span>
              </v-tooltip>
            </td>
            <td>
              <v-icon
                small
                @click="editGroup(props.item)"
              >
                edit
              </v-icon>
              <v-icon
                small
                @click="showGroupConfirmationDialog(props.item.id)"
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
import api from '../../../api'
import UsersOverview from '../UsersOverview.vue'
export default {
  name: 'GroupsInfo',
  props: {
    usersList: Array
  },
  data () {
    return {
      pagination: {},
      groupHeaders: [
        { text: 'Group id', value: 'id' },
        { text: 'Group name', value: 'name' },
        { text: 'Created at', value: 'gorupCreated' },
        { text: 'Users', sortable: false },
        { text: 'Actions', sortable: false }
      ],
      groups: [],
      group: {
        id: -1,
        name: '',
        users: []
      },
      usersValue: [],
      showModalCreateGroup: false,
      showModalRemoveGroup: false,
      showModalEditGroup: false,
      modalGroupName: '',
      modalGroupUsers: [],
      groupId: -1,
      currentGroup: {},
      errorMessage: '',
      modalAlert: false,
      alert: false
    }
  },
  created () {
    this.prettyDate = UsersOverview.methods.prettyDate
    this.handleError = UsersOverview.methods.handleError
    this.printUsernames = UsersOverview.methods.printUsernames
  },
  computed: {
    pages () {
      if (this.pagination.rowsPerPage == null ||
            this.pagination.totalItems == null
      ) return 0

      return Math.ceil(this.pagination.totalItems / this.pagination.rowsPerPage)
    },

    numGroups () {
      return this.groups.length
    }
  },

  methods: {
    clearForm () {
      this.usersValue = []
      this.modalGroupName = ''
    },
    addUserToGroup (group, user) {
      api
        .request('put', '/groups/' + group + '/users/' + user, this.$store.state.accessToken)
        .then(response => {
          this.checkGroups()
        })
        .catch(error => {
          this.handleError(error)
          this.modalAlert = true
        })
    },

    removeUserFromGroup (group, user) {
      api
        .request('delete', '/groups/' + group + '/users/' + user, this.$store.state.accessToken)
        .then(response => {
          this.checkGroups()
        })
        .catch(error => {
          this.handleError(error)
          this.modalAlert = true
        })
    },

    createGroup () {
      const { modalGroupName, usersValue } = this
      api
        .request('post', '/groups', this.$store.state.accessToken, {'name': modalGroupName})
        .then(response => {
          let groupId = response.data.group.id
          for (const user of usersValue) {
            this.addUserToGroup(groupId, user)
          }
          this.showModalCreateGroup = false
          this.sendCreated()
          this.clearForm()
        })
        .catch(error => {
          this.handleError(error)
          this.modalAlert = true
        })
    },

    editGroup: function (currentGroup) {
      this.showModalEditGroup = true
      this.group.id = currentGroup.id
      this.group.name = currentGroup.name
      this.group.users = currentGroup.users
      this.currentGroup = currentGroup
    },

    updateGroup: function () {
      var oldGroup = this.currentGroup
      var newGroup = this.group
      if (newGroup.name !== oldGroup.name && newGroup.name !== '') {
        console.log('changing name')
        api
          .request('put', '/groups/' + newGroup.id, this.$store.state.accessToken, {'name': newGroup.name})
          .then(response => {
            this.checkGroups()
          })
          .catch(error => {
            this.handleError(error)
            this.alert = true
          })
      }
      if (newGroup.users !== oldGroup.users) {
        var toAdd = newGroup.users.filter(function (x) { return oldGroup.users.indexOf(x) < 0 })
        var toDelete = oldGroup.users.filter(function (x) { return newGroup.users.indexOf(x) < 0 })

        for (const user of toDelete) {
          this.removeUserFromGroup(this.group.id, user.id)
        }

        for (const user of toAdd) {
          this.addUserToGroup(this.group.id, user.id)
        }
      }

      this.showModalEditGroup = false
      this.group = {
        id: -1,
        name: '',
        users: []
      }
      this.checkGroups()
    },

    removeGroup: function () {
      var groupId = this.groupId
      api
        .request('delete', '/groups/' + groupId, this.$store.state.accessToken)
        .then(response => {
          this.showModalRemoveGroup = false
          this.checkGroups()
        })
        .catch(error => {
          this.handleError(error)
          this.alert = true
        })
    },

    checkGroups: function () {
      api
        .request('get', '/groups', this.$store.state.accessToken)
        .then(response => {
          this.groups = response.data
          this.emitGroups()
          this.pagination['totalItems'] = this.groups.length
          this.pagination['rowsPerPage'] = 30
        })
        .catch(error => {
          this.pagination = {}
          this.handleError(error)
          this.alert = true
        })
    },

    showGroupConfirmationDialog (id) {
      this.groupId = id
      this.showModalRemoveGroup = true
    },

    sendCreated: function () {
      this.$emit('createdGroup')
    },

    emitGroups: function () {
      this.$emit('groupsList', this.groups)
    }
  },
  mounted () {
    this.checkGroups()
  }
}
</script>
