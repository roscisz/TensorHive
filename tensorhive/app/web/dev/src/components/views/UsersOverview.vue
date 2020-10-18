<template>
  <section class="content">
    <v-alert
      v-model="alert"
      dismissible
      type="error"
    >
      {{ errorMessage }}
    </v-alert>
    <v-alert
      v-model="created"
      dismissible
      type="info"
    >
      {{ infoMessage }}
    </v-alert>
    <v-dialog
      v-model="showRestrictions"
      width="850px"
    >
    <v-card>
      <v-card-text>
        <v-btn
          class="float-right-button"
          flat
          icon
          color="black"
          @click="showRestrictions=false"
        >
          <v-icon>close</v-icon>
        </v-btn>
        <span class="headline">Manage restrictions</span>
      </v-card-text>
      <v-data-table
        :headers="restrictionHeaders"
        :items="restrictions"
        item-key="id"
        class="elevation-1"
        rows-per-page-text=""
        :rows-per-page-items="[5]"
      >
        <template slot="items" slot-scope="props">
          <tr>
            <td>{{ props.item.id }}</td>
            <td>{{ props.item.name }}</td>
            <td>{{ printTimespan(props.item.startsAt, props.item.endsAt) }}</td>
            <td>{{ printSchedule(props.item.schedules) }}</td>
            <td>
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <span v-bind="attrs" v-on="on">{{ props.item.users.length }}</span>
                </template>
                <span>{{ printUsernames(props.item.users) }}</span>
              </v-tooltip>
            </td>
            <td>
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <span v-bind="attrs" v-on="on">{{ props.item.groups.length }}</span>
                </template>
                <span>{{ printNames(props.item.groups) }}</span>
              </v-tooltip>
            </td>
            <td v-if="props.item.isGlobal">All</td>
            <td v-else>
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <span v-bind="attrs" v-on="on">{{ props.item.resources.length }}</span>
                </template>
                <span>{{ printNames(props.item.resources) }}</span>
              </v-tooltip>
            </td>
            <td>
              <v-icon
                small
                @click="showRemoveConfirmationDialog(props.item.id)"
              >
                delete
              </v-icon>
            </td>
          </tr>
        </template>
      </v-data-table>
      <v-alert
        v-model="modalAlert"
        dismissible
        type="error"
      >
        {{ errorMessage }}
      </v-alert>
      <v-card-text>
        <span class="headline">Add restriction</span>
        <form @submit.prevent="createRestriction">
          <v-card-text></v-card-text>
          <div class="input-group">
            <span class="input-group-addon"><i class="fa fa-info"></i></span>
            <input
              class="form-control"
              name="modalRestrictionName"
              placeholder="Restriction name"
              type="text"
              v-model="modalRestrictionName"
            >
          </div>
          <v-layout>
          <v-checkbox
            v-model="globalRestriction"
            label="Global restriction"
          >
          </v-checkbox>
          <transition name="fade">
            <v-autocomplete
              style="width: 70%"
              v-show="!globalRestriction"
              v-model="resourcesValue"
              :items="resources"
              :multiple=true
              placeholder="Resources"
              item-value="id"
              item-text="name"
              prepend-icon="fa-server"
            >
            </v-autocomplete>
          </transition>
          </v-layout>
          <v-layout align-center justify-start>
            <v-autocomplete
              style="width: 50%"
              v-model="usersValue"
              :items="users"
              :multiple=true
              placeholder="Users"
              item-value="id"
              item-text="username"
              prepend-icon="fa-user"
            />
            <v-autocomplete
              style="width: 50%"
              v-model="groupsValue"
              :items="groups"
              :multiple=true
              placeholder="Groups"
              item-value="id"
              item-text="name"
              prepend-icon="fa-group"
            />
          </v-layout>
          <v-layout align-center justify-start>
          <v-menu
            v-model="startDateMenu"
            :close-on-content-click="false"
            :nudge-right="40"
            lazy
            transition="none"
            offset-y
            full-width
            min-width="290px"
          >
            <template v-slot:activator="{ on }">
                <v-text-field
                  v-model="modalStartDate"
                  placeholder="Start date"
                  prepend-icon="event"
                  v-on="on"
                ></v-text-field>
            </template>
            <v-date-picker
              title="Start date"
              v-model="modalStartDate"
              :max="modalEndDate"
              :allowed-dates="isTodayOrLater"
              @input="startDateMenu = false"
            ></v-date-picker>
          </v-menu>
          <v-menu
            v-model="endDateMenu"
            :close-on-content-click="false"
            :nudge-right="40"
            lazy
            transition="none"
            offset-y
            full-width
            min-width="290px"
          >
            <template v-slot:activator="{ on }">
              <v-text-field
                v-model="modalEndDate"
                placeholder="End date"
                prepend-icon="event"
                v-on="on"
              ></v-text-field>
            </template>
            <v-date-picker
              title="End date"
              v-model="modalEndDate"
              :min="modalStartDate"
              :allowed-dates="isTodayOrLater"
              @input="endDateMenu = false"
            ></v-date-picker>
          </v-menu>
          </v-layout>
          <v-checkbox
            label="Add restriction schedule"
            v-model="addSchedule"
          >
          </v-checkbox>
          <transition name="fade">
            <v-layout align-center justify-center v-show="addSchedule">
            <v-menu
              ref="startMenu"
              v-model="startTimeMenu"
              :close-on-content-click="false"
              :nudge-right="40"
              :return-value.sync="modalStartTime"
              lazy
              transition="none"
              offset-y
              full-width
              max-width="290px"
              min-width="290px"
            >
              <template v-slot:activator="{ on }">
                <v-text-field
                  v-model="modalStartTime"
                  placeholder="Start time"
                  prepend-icon="access_time"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-time-picker
                title="Start time"
                v-if="startTimeMenu"
                v-model="modalStartTime"
                full-width
                format="24hr"
                :max="modalEndTime"
                @click:minute="$refs.startMenu.save(modalStartTime)"
              ></v-time-picker>
            </v-menu>
            <v-menu
              ref="endMenu"
              v-model="endTimeMenu"
              :close-on-content-click="false"
              :nudge-right="40"
              :return-value.sync="modalEndTime"
              lazy
              transition="none"
              offset-y
              full-width
              max-width="290px"
              min-width="290px"
            >
              <template v-slot:activator="{ on }">
                <v-text-field
                  v-model="modalEndTime"
                  placeholder="End time"
                  prepend-icon="access_time"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-time-picker
                title="End time"
                v-if="endTimeMenu"
                v-model="modalEndTime"
                full-width
                format="24hr"
                :min="modalStartTime"
                @click:minute="$refs.endMenu.save(modalEndTime)"
              ></v-time-picker>
              </v-menu>
              <v-select
                style="width: 60%"
                v-model="daysValue"
                :items="weekdays"
                placeholder="Weekdays"
                prepend-icon="event"
                :multiple=true
              >
              </v-select>
            </v-layout>
          </transition>
          <v-btn
            color="success"
            type="submit"
          >
            Add
          </v-btn>
        </form>
      </v-card-text>
    </v-card>
    </v-dialog>
    <v-dialog
      v-model="showRemoveRestriction"
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
            @click="showRemoveRestriction=false"
          >
            <v-icon>close</v-icon>
          </v-btn>
          Do you want to remove this restriction?
        </v-card-text>
        <v-card-actions>
          <v-layout align-center justify-end>
            <v-btn
              color="success"
              round
              @click="removeRestriction()"
            >
              Yes
            </v-btn>
          </v-layout>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <div class="text-xs-center pt-2">
      <v-btn color="primary" @click="showRestrictions=true">Manage restrictions</v-btn>
      <v-divider></v-divider>
    </div>
    <div class="data_table">
      <UsersInfo class="data_box" @createdUser="userCreatedAlert" @usersList="updateUsers" />
      <GroupsInfo class="data_box" :usersList="this.users" @createdGroup="groupCreatedAlert" @groupsList="updateGroups"/>
    </div>
  </section>
</template>

<script>
import api from '../../api'
import moment from 'moment'
import GroupsInfo from './users_overview/GroupsInfo.vue'
import UsersInfo from './users_overview/UsersInfo.vue'
export default {
  components: {
    GroupsInfo,
    UsersInfo
  },
  data () {
    return {
      errorMessage: '',
      infoMessage: '',
      createdGroup: false,
      created: false,
      alert: false,
      users: [],
      usersValue: [],
      groups: [],
      groupsValue: [],
      restrictionHeaders: [
        { text: 'ID', value: 'id' },
        { text: 'Name', value: 'name' },
        { text: 'Timespan', sortable: false },
        { text: 'Schedule', sortable: false },
        { text: 'Users', value: 'users', sortable: false },
        { text: 'Groups', value: 'groups', sortable: false },
        { text: 'Resources', value: 'resources', sortable: false },
        { text: 'Actions', sortable: false }
      ],
      restrictions: [],
      restrictionId: -1,
      addSchedule: false,
      showRestrictions: false,
      modalRestrictionName: '',
      startDateMenu: false,
      endDateMenu: false,
      startTimeMenu: false,
      endTimeMenu: false,
      modalAlert: false,
      modalInfo: false,
      showRemoveRestriction: false,
      modalStartDate: '',
      modalEndDate: '',
      modalStartTime: '',
      modalEndTime: '',
      weekdays: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
      daysValue: [],
      globalRestriction: false,
      resources: [],
      resourcesValue: []
    }
  },
  mounted () {
    this.checkResources()
    this.checkRestrictions()
  },
  methods: {
    prettyDate (date) {
      if (date !== null) {
        return moment(date).format('dddd, MMMM Do, HH:mm')
      } else {
        return null
      }
    },
    printTimespan (start, end) {
      return moment(start).format('ll') + ' - ' + moment(end).format('ll')
    },
    printNames (array) {
      return array.map(a => a.name).join(', ')
    },
    printUsernames (array) {
      return array.map(a => a.username).join(', ')
    },
    printSchedule (schedules) {
      if (schedules.length > 0) {
        for (const schedule of schedules) {
          return schedule.hourStart + '-' + schedule.hourEnd + ' ' +
            schedule.scheduleDays.map(a => a.substring(0, 3)).join(', ')
        }
      } else return 'none'
    },
    clearForm () {
      this.modalRestrictionName = ''
      this.globalRestriction = false
      this.resourcesValue = false
      this.addSchedule = false
      this.usersValue = []
      this.groupsValue = []
      this.modalStartDate = ''
      this.modalEndDate = ''
      this.modalStartTime = ''
      this.modalEndTime = ''
      this.daysValue = []
    },
    handleError (error) {
      if (!error.hasOwnProperty('response')) {
        this.errorMessage = error.message
      } else {
        if (!error.response.data.hasOwnProperty('msg')) {
          this.errorMessage = error.response.data
        } else {
          this.errorMessage = error.response.data.msg
        }
      }
    },
    isTodayOrLater (date) {
      return moment(date).isSameOrAfter(moment().format(moment.HTML5_FMT.DATE))
    },
    groupCreatedAlert () {
      this.created = true
      this.infoMessage = 'Group created successfully'
    },
    userCreatedAlert () {
      this.created = true
      this.infoMessage = 'User created successfully'
    },
    updateUsers (value) {
      this.users = value
    },
    updateGroups (value) {
      this.groups = value
    },
    checkRestrictions () {
      api
        .request('get', '/restrictions', this.$store.state.accessToken)
        .then(response => {
          this.restrictions = response.data
        })
        .catch(error => {
          this.handleError(error)
          this.modalAlert = true
        })
    },
    addUserToRestriction (restriction, user) {
      api
        .request('put', '/restrictions/' + restriction + '/users/' + user, this.$store.state.accessToken)
        .then(response => {
          this.checkRestrictions()
        })
        .catch(error => {
          this.handleError(error)
          this.modalAlert = true
        })
    },
    removeUserFromRestriction (restriction, user) {
      api
        .request('delete', '/restrictions/' + restriction + '/users/' + user, this.$store.state.accessToken)
        .then(response => {
          this.checkRestrictions()
        })
        .catch(error => {
          this.handleError(error)
          this.modalAlert = true
        })
    },
    addGroupToRestriction (restriction, group) {
      api
        .request('put', '/restrictions/' + restriction + '/groups/' + group, this.$store.state.accessToken)
        .then(response => {
          this.checkRestrictions()
        })
        .catch(error => {
          this.handleError(error)
          this.modalAlert = true
        })
    },
    removeGroupFromRestriction (restriction, group) {
      api
        .request('delete', '/restrictions/' + restriction + '/groups/' + group, this.$store.state.accessToken)
        .then(response => {
          this.checkRestrictions()
        })
        .catch(error => {
          this.handleError(error)
          this.modalAlert = true
        })
    },
    addResourceToRestriction (restriction, resource) {
      api
        .request('put', '/restrictions/' + restriction + '/resources/' + resource, this.$store.state.accessToken)
        .then(response => {
          this.checkRestrictions()
        })
        .catch(error => {
          this.handleError(error)
          this.modalAlert = true
        })
    },
    removeResourceFromRestriction (restriction, resource) {
      api
        .request('delete', '/restrictions/' + restriction + '/resources/' + resource, this.$store.state.accessToken)
        .then(response => {
          this.checkRestrictions()
        })
        .catch(error => {
          this.handleError(error)
          this.modalAlert = true
        })
    },
    createAndAddSchedule (restriction) {
      const { modalStartTime, modalEndTime, daysValue } = this
      if (modalStartTime && modalEndTime && daysValue) {
        api
          .request('post', '/schedules', this.$store.state.accessToken, {
            'hourStart': modalStartTime,
            'hourEnd': modalEndTime,
            'scheduleDays': daysValue
          })
          .then(response => {
            let scheduleId = response.data.schedule.id
            this.addScheduleToRestriction(restriction, scheduleId)
          })
          .catch(error => {
            this.handleError(error)
            this.modalAlert = true
          })
      }
    },
    addScheduleToRestriction (restriction, schedule) {
      api
        .request('put', '/restrictions/' + restriction + '/schedules/' + schedule, this.$store.state.accessToken)
        .then(response => {
          this.checkRestrictions()
        })
        .catch(error => {
          this.handleError(error)
          this.modalAlert = true
        })
    },
    createRestriction () {
      if (this.modalStartDate && this.modalEndDate) {
        var formattedStart = moment(this.modalStartDate).startOf('day')
        var formatedEnd = moment(this.modalEndDate).endOf('day')
        const { modalRestrictionName, globalRestriction, addSchedule,
          resourcesValue, usersValue, groupsValue } = this
        api
          .request('post', '/restrictions', this.$store.state.accessToken,
            {
              'name': modalRestrictionName,
              'start': formattedStart,
              'end': formatedEnd,
              'isGlobal': globalRestriction
            })
          .then(response => {
            let restrictionId = response.data.restriction.id
            if (resourcesValue.length > 0 && globalRestriction === false) {
              for (const resource of resourcesValue) {
                this.addResourceToRestriction(restrictionId, resource)
              }
            }
            if (usersValue.length > 0) {
              for (const user of usersValue) {
                this.addUserToRestriction(restrictionId, user)
              }
            }
            if (groupsValue.length > 0) {
              for (const group of groupsValue) {
                this.addGroupToRestriction(restrictionId, group)
              }
            }
            if (addSchedule) this.createAndAddSchedule(restrictionId)
            this.clearForm()
          })
          .catch(error => {
            this.handleError(error)
            this.modalAlert = true
          })
      } else {
        this.errorMessage = 'Specify start and end date!'
        this.modalAlert = true
      }
    },
    removeRestriction () {
      var restrictionId = this.restrictionId
      api
        .request('delete', '/restrictions/' + restrictionId, this.$store.state.accessToken)
        .then(response => {
          this.showRemoveRestriction = false
          this.checkRestrictions()
        })
        .catch(error => {
          this.handleError(error)
          this.modalAlert = true
        })
    },
    checkResources () {
      api
        .request('get', '/resources', this.$store.state.accessToken)
        .then(response => {
          this.resources = response.data
        })
        .catch(error => {
          this.handleError(error)
          this.modalAlert = true
        })
    },
    showRemoveConfirmationDialog (id) {
      this.restrictionId = id
      this.showRemoveRestriction = true
    }
  }
}
</script>

<style>
.float-right-button {
  float: right;
}
.input-group {
  padding-bottom: 2em;
  height: 4em;
  width: 100%;
}

.input-group span.input-group-addon {
  width: 2em;
  height: 4em;
}

@media (max-width: 1241px) {
  .input-group input {
    height: 4em;
  }
}
@media (min-width: 1242px) {
  .input-group input {
    height: 6em;
  }
}

.input-group-addon i {
  height: 15px;
  width: 15px;
}

.data_table{
  display: flex;
  flex-wrap: wrap;
}

.data_box{
  width: 45vw;
}

.fade-enter-active, .fade-leave-active {
  transition: all .5s;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>
