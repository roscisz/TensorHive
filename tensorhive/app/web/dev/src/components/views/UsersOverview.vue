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
      width="875px"
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
        <span class="headline">Manage permissions</span>
        <v-tooltip right>
          <template v-slot:activator="{ on }">
            <v-icon v-on="on">info</v-icon>
          </template>
          <v-card-text>
            Users can only reserve a specific resource if they<br />
            are affected by a permission that allows it.
          </v-card-text>
        </v-tooltip>
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
            <td>
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <span class="white-space" v-bind="attrs" v-on="on">{{ printTimespan(props.item.startsAt, props.item.endsAt) }}</span>
                </template>
                <span class="white-space">{{ printTimespan(props.item.startsAt, props.item.endsAt, full=true) }}</span>
              </v-tooltip>
            </td>
            <td>
              <v-tooltip bottom :disabled="props.item.schedules.length<=1">
                <template v-slot:activator="{ on, attrs }">
                  <span class="white-space" v-bind="attrs" v-on="on">{{ printSchedules(props.item.schedules) }}</span>
                </template>
                <span class="white-space">{{ printSchedules(props.item.schedules, all=true) }}</span>
              </v-tooltip>
            </td>
            <td>
              <v-tooltip bottom :disabled="props.item.users.length===0">
                <template v-slot:activator="{ on, attrs }">
                  <span v-bind="attrs" v-on="on">{{ props.item.users.length }}</span>
                </template>
                <span class="white-space">{{ printUsernames(props.item.users) }}</span>
              </v-tooltip>
            </td>
            <td>
              <v-tooltip bottom :disabled="props.item.groups.length===0">
                <template v-slot:activator="{ on, attrs }">
                  <span v-bind="attrs" v-on="on">{{ props.item.groups.length }}</span>
                </template>
                <span class="white-space">{{ printNames(props.item.groups) }}</span>
              </v-tooltip>
            </td>
            <td v-if="props.item.isGlobal">All</td>
            <td v-else>
              <v-tooltip bottom :disabled="props.item.resources.length===0">
                <template v-slot:activator="{ on, attrs }">
                  <span v-bind="attrs" v-on="on">{{ props.item.resources.length }}</span>
                </template>
                <span class="white-space">{{ printNames(props.item.resources) }}</span>
              </v-tooltip>
            </td>
            <td>
              <v-icon
                small
                @click="editRestriction(props.item)"
              >
                edit
              </v-icon>
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
        <span v-if="editMode" class="headline">Edit permission</span>
        <span v-else class="headline">Add permission</span>
        <v-btn small v-if="editMode" @click="clearForm">Cancel editing</v-btn>
        <form @submit.prevent="createRestriction">
          <v-divider></v-divider>
          <div class="input-group">
            <span class="input-group-addon"><i class="fa fa-info"></i></span>
            <input
              class="form-control"
              name="modalRestrictionName"
              placeholder="Permission name"
              type="text"
              v-model="modalRestrictionName"
            >
          </div>
          <v-layout>
            <v-flex xs6>
              <v-autocomplete
                v-model="usersValue"
                :items="users"
                :multiple=true
                placeholder="Users"
                item-value="id"
                item-text="username"
                prepend-icon="fa-user"
                return-object
              />
            </v-flex>
            <v-flex xs6>
              <v-autocomplete
                v-model="groupsValue"
                :items="groups"
                :multiple=true
                placeholder="Groups"
                item-value="id"
                item-text="name"
                prepend-icon="fa-group"
                return-object
              />
            </v-flex>
          </v-layout>
          <v-layout>
          <v-flex xs4>
            <v-autocomplete
              v-model="hostsValue"
              :items="hosts"
              :multiple=true
              placeholder="Hostnames"
              item-text="hostname"
              prepend-icon="fa-server"
              return-object
              :disabled="globalRestriction"
            >
            </v-autocomplete>
          </v-flex>
          <v-flex xs4>
            <v-autocomplete
              v-model="resourcesValue"
              :items="resources"
              :multiple=true
              placeholder="Resources"
              item-value="id"
              item-text="name"
              prepend-icon="fa-server"
              return-object
              :disabled="globalRestriction"
            >
            </v-autocomplete>
          </v-flex>
          <v-flex>
            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <v-checkbox  v-bind="attrs" v-on="on"
                v-model="globalRestriction"
                label="Global"
              >
              </v-checkbox>
              </template>
              <span>Global permission applies to all available resources</span>
            </v-tooltip>
          </v-flex>
          </v-layout>
          <v-layout>
          <v-flex xs4>
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
          </v-flex>
          <v-flex xs4>
          <v-menu
              ref="startTimeMenu"
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
                :max="getMaxTime()"
                :allowed-minutes="m => m % 5 === 0"
                @click:minute="$refs.startTimeMenu.save(modalStartTime)"
              ></v-time-picker>
            </v-menu>
            </v-flex>
          </v-layout>
          <v-layout>
          <v-flex xs4>
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
                :disabled="infiniteRestriction"
              ></v-text-field>
            </template>
            <v-date-picker
              title="End date"
              v-model="modalEndDate"
              :min="modalStartDate"
              :allowed-dates="isTodayOrLater"
              @input="endDateMenu = false"
            >
            </v-date-picker>
          </v-menu>
          </v-flex>
          <v-flex xs4>
          <v-menu
              ref="endTimeMenu"
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
                  :disabled="infiniteRestriction"
                ></v-text-field>
              </template>
              <v-time-picker
                title="End time"
                v-if="endTimeMenu"
                v-model="modalEndTime"
                full-width
                format="24hr"
                :min="getMinTime()"
                :allowed-minutes="m => m % 5 === 0"
                @click:minute="$refs.endTimeMenu.save(modalEndTime)"
              ></v-time-picker>
              </v-menu>
              </v-flex>
              <v-flex xs3>
                <v-checkbox
                  label="No end date"
                  v-model="infiniteRestriction"
                >
                </v-checkbox>
              </v-flex>
              </v-layout>
          <p class="font-weight-medium">
              Permission schedules
              <v-btn
                icon
                color="blue-grey lighten-5"
                @click="addSchedule()"
                :disabled="tempSchedules.length===5"
                >
                <v-icon>add</v-icon>
              </v-btn>
          </p>
          <transition-group name="fade">
            <v-layout align-center justify-center
              v-for="(schedule, key, index) in tempSchedules"
              :key="key"
              :data-index="index"
            >
            <v-menu
              ref="startMenu"
              v-model="schedule.startMenu"
              :close-on-content-click="false"
              :nudge-right="40"
              :return-value.sync="schedule.hourStart"
              lazy
              transition="none"
              offset-y
              full-width
              max-width="290px"
              min-width="290px"
            >
              <template v-slot:activator="{ on }">
                <v-text-field
                  v-model="schedule.hourStart"
                  placeholder="Start time"
                  prepend-icon="access_time"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-time-picker
                title="Start time"
                v-if="schedule.startMenu"
                v-model="schedule.hourStart"
                full-width
                format="24hr"
                :max="schedule.hourEnd"
                @click:minute="$refs.startMenu[key].save(schedule.hourStart)"
              ></v-time-picker>
            </v-menu>
            <v-menu
              ref="endMenu"
              v-model="schedule.endMenu"
              :close-on-content-click="false"
              :nudge-right="40"
              :return-value.sync="schedule.hourEnd"
              lazy
              transition="none"
              offset-y
              full-width
              max-width="290px"
              min-width="290px"
            >
              <template v-slot:activator="{ on }">
                <v-text-field
                  v-model="schedule.hourEnd"
                  placeholder="End time"
                  prepend-icon="access_time"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-time-picker
                title="End time"
                v-if="schedule.endMenu"
                v-model="schedule.hourEnd"
                full-width
                format="24hr"
                :min="schedule.hourStart"
                @click:minute="$refs.endMenu[key].save(schedule.hourEnd)"
              ></v-time-picker>
              </v-menu>
              <v-select
                style="width: 50%"
                v-model="schedule.scheduleDays"
                :items="weekdays"
                placeholder="Weekdays"
                prepend-icon="event"
                :multiple=true
              >
              </v-select>
              <v-btn
                icon
                color="blue-grey lighten-5"
                @click="deleteSchedule(key)"
                >
                <v-icon>remove</v-icon>
              </v-btn>
            </v-layout>
            </transition-group>
          <v-btn
            v-if="editMode"
            color="primary"
            type="submit"
          >
            Edit permission
          </v-btn>
          <v-btn
            v-else
            color="success"
            type="submit"
          >
            Add permission
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
          Do you want to remove this permission?
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
      <v-btn color="primary" @click="showRestrictions=true">Manage permissions</v-btn>
      <v-divider></v-divider>
    </div>
    <div class="data_table">
      <UsersInfo class="data_box" @createdUser="userCreatedAlert" @usersList="updateUsers" :groupsList="this.groups"/>
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
  watch: {
    resourcesValue: function () {
      if (this.triggerResourcesWatcher) {
        this.selectedResourcesChanged()
      } else this.triggerResourcesWatcher = true
    },
    hostsValue: function (after, before) {
      if (this.triggerHostsWatcher) {
        var host
        if (before.length > after.length) {
          host = before.filter(x => !after.includes(x))
          this.unselectHostResources(host[0])
        } else if (before.length < after.length) {
          host = after.filter(x => !before.includes(x))
          this.selectHostResources(host[0])
        }
      } else this.triggerHostsWatcher = true
    }
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
        { text: 'Timespan', sortable: false, width: 145 },
        { text: 'Schedules', sortable: false },
        { text: 'Users', value: 'users', sortable: false },
        { text: 'Groups', value: 'groups', sortable: false },
        { text: 'Resources', value: 'resources', sortable: false },
        { text: 'Actions', sortable: false }
      ],
      tempSchedules: [],
      restrictions: [],
      restrictionId: -1,
      infiniteRestriction: false,
      showRestrictions: false,
      modalRestrictionName: '',
      startDateMenu: false,
      endDateMenu: false,
      startTimeMenu: false,
      endTimeMenu: false,
      modalAlert: false,
      showRemoveRestriction: false,
      modalStartDate: '',
      modalEndDate: '',
      modalStartTime: '',
      modalEndTime: '',
      weekdays: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
      globalRestriction: false,
      resources: [],
      resourcesValue: [],
      hosts: [],
      hostsValue: [],
      editMode: false,
      currentRestriction: {},
      triggerResourcesWatcher: true,
      triggerHostsWatcher: true
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
    getMaxTime () {
      if (this.modalStartDate === this.modalEndDate) {
        return this.modalEndTime
      } else return ''
    },
    getMinTime () {
      if (this.modalStartDate === this.modalEndDate) {
        return this.modalStartTime
      } else return ''
    },
    printTimespan (start, end, full = false) {
      var formattedEnd = 'no end date'
      if (full) {
        if (moment(end).isValid()) formattedEnd = moment(end).format('ll HH:mm')
        return 'start: ' + moment(start).format('ll HH:mm') + '\nend: ' + formattedEnd
      } else {
        if (moment(end).isValid()) formattedEnd = moment(end).format('DD-MM-YYYY')
        var returnString = moment(start).format('DD-MM-YYYY') + ' -\n' + formattedEnd
        if (moment(end).isSameOrBefore(moment())) returnString = returnString + '\n(expired)'
        return returnString
      }
    },
    printNames (array) {
      return array.map(a => a.name).join(' \n')
    },
    printUsernames (array) {
      return array.map(a => a.username).join(' \n')
    },
    printSchedules (schedules, all = false) {
      if (schedules.length === 0) return 'none'
      else if (schedules.length === 1 || all) {
        var returnString = ''
        for (const schedule of schedules) {
          returnString = returnString + schedule.hourStart + '-' + schedule.hourEnd + ' '
          if (schedules.length === 1) returnString = returnString + '\n'
          returnString = returnString + schedule.scheduleDays.map(a => a.substring(0, 3)).join(', ') + '\n'
        }
        return returnString
      } else return schedules.length
    },
    selectHostResources (host) {
      for (const resource of host.resources) {
        if (!this.resourcesValue.some(r => r.id === resource.id)) {
          this.triggerResourcesWatcher = false
          this.resourcesValue.push(resource)
        }
      }
    },
    unselectHostResources (host) {
      for (const resource of host.resources) {
        if (this.resourcesValue.some(r => r.id === resource.id)) {
          this.triggerResourcesWatcher = false
          this.resourcesValue = this.resourcesValue.filter(r => r.id !== resource.id)
        }
      }
    },
    selectedResourcesChanged () {
      for (const host of this.hosts) {
        if (host.resources.every(r => this.resourcesValue.some(r2 => r2.id === r.id)) &&
        !this.hostsValue.some(h => h.hostname === host.hostname)) {
          this.triggerHostsWatcher = false
          this.hostsValue.push(host)
        } else if (!host.resources.every(r => this.resourcesValue.some(r2 => r2.id === r.id)) &&
        this.hostsValue.some(h => h.hostname === host.hostname)) {
          this.triggerHostsWatcher = false
          this.hostsValue = this.hostsValue.filter(h => h.hostname !== host.hostname)
        }
      }
    },
    clearForm () {
      this.modalRestrictionName = ''
      this.globalRestriction = false
      this.resourcesValue = []
      this.usersValue = []
      this.groupsValue = []
      this.modalStartDate = ''
      this.modalEndDate = ''
      this.modalStartTime = ''
      this.modalEndTime = ''
      this.tempSchedules = []
      this.infiniteRestriction = false
      this.restrictionId = -1
      this.editMode = false
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
    scheduleBlueprint () {
      return {
        hourStart: '',
        hourEnd: '',
        scheduleDays: [],
        startMenu: false,
        endMenu: false
      }
    },
    addSchedule () {
      const schedule = this.scheduleBlueprint
      this.tempSchedules.push(schedule())
    },
    deleteSchedule (scheduleKey) {
      this.tempSchedules.splice(scheduleKey, 1)
    },
    copySchedules (schedules) {
      this.tempSchedules = []
      for (const schedule of schedules) {
        var newSchedule = this.scheduleBlueprint()
        newSchedule.hourStart = schedule.hourStart
        newSchedule.hourEnd = schedule.hourEnd
        newSchedule.scheduleDays = schedule.scheduleDays
        this.tempSchedules.push(newSchedule)
      }
    },
    equalSchedule (s1, s2) {
      if (!s1 || !s2) return false
      return s1.hourStart === s2.hourStart &&
        s1.hourEnd === s2.hourEnd &&
        s1.scheduleDays === s2.scheduleDays
    },
    equalSchedules (schedules1, schedules2) {
      if (schedules1.length !== schedules2.length) return false
      const equalSchedule = this.equalSchedule
      return schedules1.every((x, index) => equalSchedule(x, schedules2[index]))
    },
    scheduleCompare (otherArray) {
      const equalSchedule = this.equalSchedule
      return function (current) {
        return otherArray.filter(function (other) {
          return equalSchedule(current, other)
        }).length === 0
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
    createAndAddSchedule (restriction, schedule) {
      api
        .request('post', '/schedules', this.$store.state.accessToken, {
          'hourStart': schedule.hourStart,
          'hourEnd': schedule.hourEnd,
          'scheduleDays': schedule.scheduleDays
        })
        .then(response => {
          let scheduleId = response.data.schedule.id
          this.addScheduleToRestriction(restriction, scheduleId)
        })
        .catch(error => {
          this.handleError(error)
          this.modalAlert = true
        })
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
    removeScheduleFromRestriction (restriction, schedule) {
      api
        .request('delete', '/restrictions/' + restriction + '/schedules/' + schedule, this.$store.state.accessToken)
        .then(response => {
          this.checkRestrictions()
        })
        .catch(error => {
          this.handleError(error)
          this.modalAlert = true
        })
    },
    createRestriction () {
      if (this.editMode) this.updateRestriction()
      else if (this.modalStartDate && this.modalStartTime &&
          ((this.modalEndDate && this.modalEndTime) || this.infiniteRestriction)) {
        if (this.verifyTempSchedules()) {
          var formattedStart = moment(this.modalStartDate + 'T' + this.modalStartTime).toISOString()
          var restrictionToCreate = {
            name: this.modalRestrictionName,
            start: formattedStart,
            isGlobal: this.globalRestriction
          }
          if (!this.infiniteRestriction) {
            var formattedEnd = moment(this.modalEndDate + 'T' + this.modalEndTime).toISOString()
            restrictionToCreate.end = formattedEnd
          }
          const { globalRestriction, tempSchedules, resourcesValue, usersValue, groupsValue } = this
          api
            .request('post', '/restrictions', this.$store.state.accessToken,
              restrictionToCreate)
            .then(response => {
              let restrictionId = response.data.restriction.id
              if (resourcesValue.length > 0 && globalRestriction === false) {
                for (const resource of resourcesValue) {
                  this.addResourceToRestriction(restrictionId, resource.id)
                }
              }
              if (usersValue.length > 0) {
                for (const user of usersValue) {
                  this.addUserToRestriction(restrictionId, user.id)
                }
              }
              if (groupsValue.length > 0) {
                for (const group of groupsValue) {
                  this.addGroupToRestriction(restrictionId, group.id)
                }
              }
              if (tempSchedules.length > 0) {
                for (const schedule of tempSchedules) {
                  this.createAndAddSchedule(restrictionId, schedule)
                }
              }
              this.checkRestrictions()
              this.clearForm()
            })
            .catch(error => {
              this.handleError(error)
              this.modalAlert = true
            })
        } else {
          this.errorMessage = 'Specify details for all schedules you want to create'
          this.modalAlert = true
        }
      } else {
        this.errorMessage = 'Specify start and end date and time!'
        this.modalAlert = true
      }
    },
    verifyTempSchedules () {
      if (this.tempSchedules.length === 0) return true
      else return this.tempSchedules.every(s => s.hourStart && s.hourEnd && s.scheduleDays.length > 0)
    },
    removeRestriction () {
      var restrictionId = this.restrictionId
      api
        .request('delete', '/restrictions/' + restrictionId, this.$store.state.accessToken)
        .then(response => {
          this.showRemoveRestriction = false
          this.clearForm()
          this.checkRestrictions()
        })
        .catch(error => {
          this.handleError(error)
          this.modalAlert = true
        })
    },
    editRestriction (currentRestriction) {
      this.clearForm()
      this.editMode = true
      this.restrictionId = currentRestriction.id
      this.modalRestrictionName = currentRestriction.name
      this.globalRestriction = currentRestriction.isGlobal
      if (!this.globalRestriction) this.resourcesValue = currentRestriction.resources.slice()
      this.usersValue = currentRestriction.users
      this.groupsValue = currentRestriction.groups
      this.modalStartDate = moment(currentRestriction.startsAt).format(moment.HTML5_FMT.DATE)
      this.modalStartTime = moment(currentRestriction.startsAt).format(moment.HTML5_FMT.TIME)
      if (currentRestriction.endsAt) {
        this.modalEndDate = moment(currentRestriction.endsAt).format(moment.HTML5_FMT.DATE)
        this.modalEndTime = moment(currentRestriction.endsAt).format(moment.HTML5_FMT.TIME)
      } else {
        this.infiniteRestriction = true
        this.modalEndDate = ''
        this.modalEndTime = ''
      }
      this.copySchedules(currentRestriction.schedules)
      this.currentRestriction = currentRestriction
    },
    updateRestriction () {
      if (this.modalStartDate && this.modalStartTime &&
          ((this.modalEndDate && this.modalEndTime) || this.infiniteRestriction)) {
        if (this.verifyTempSchedules()) {
          var formattedStart = moment(this.modalStartDate + 'T' + this.modalStartTime).toISOString()
          var formattedEnd = null
          if (!this.infiniteRestriction) {
            formattedEnd = moment(this.modalEndDate + 'T' + this.modalEndTime).toISOString()
          }
          const { modalRestrictionName, globalRestriction, currentRestriction,
            usersValue, groupsValue, resourcesValue, tempSchedules } = this
          api
            .request('put', '/restrictions/' + this.currentRestriction.id, this.$store.state.accessToken,
              {
                'name': modalRestrictionName,
                'start': formattedStart,
                'end': formattedEnd,
                'isGlobal': globalRestriction
              }).then(response => {
              this.checkRestrictions()
            })
            .catch(error => {
              this.handleError(error)
              this.modalAlert = true
            })

          if (currentRestriction.users !== usersValue) {
            var addUsers = usersValue.filter(
              function (x) { return currentRestriction.users.indexOf(x) < 0 })
            var deleteUsers = currentRestriction.users.filter(
              function (x) { return usersValue.indexOf(x) < 0 })

            for (const user of addUsers) {
              this.addUserToRestriction(this.restrictionId, user.id)
            }
            for (const user of deleteUsers) {
              this.removeUserFromRestriction(this.restrictionId, user.id)
            }
          }

          if (currentRestriction.groups !== groupsValue) {
            var addGroups = groupsValue.filter(
              function (x) { return currentRestriction.groups.indexOf(x) < 0 })
            var deleteGroups = currentRestriction.groups.filter(
              function (x) { return groupsValue.indexOf(x) < 0 })

            for (const group of addGroups) {
              this.addGroupToRestriction(this.restrictionId, group.id)
            }
            for (const group of deleteGroups) {
              this.removeGroupFromRestriction(this.restrictionId, group.id)
            }
          }

          if (this.globalRestriction && currentRestriction.resources.length > 0) {
            for (const resource of currentRestriction.resources) {
              this.removeResourceFromRestriction(this.restrictionId, resource.id)
            }
          } else if (currentRestriction.resources !== resourcesValue) {
            var addResources = resourcesValue.filter(
              function (x) { return currentRestriction.resources.indexOf(x) < 0 })
            var deleteResources = currentRestriction.resources.filter(
              function (x) { return resourcesValue.indexOf(x) < 0 })

            for (const resource of addResources) {
              this.addResourceToRestriction(this.restrictionId, resource.id)
            }
            for (const resource of deleteResources) {
              this.removeResourceFromRestriction(this.restrictionId, resource.id)
            }
          }

          if (!this.equalSchedules(currentRestriction.schedules, tempSchedules)) {
            var addSchedules = tempSchedules.filter(this.scheduleCompare(currentRestriction.schedules))
            var deleteSchedules = currentRestriction.schedules.filter(this.scheduleCompare(tempSchedules))

            for (const schedule of addSchedules) {
              this.createAndAddSchedule(this.restrictionId, schedule)
            }
            for (const schedule of deleteSchedules) {
              this.removeScheduleFromRestriction(this.restrictionId, schedule.id)
            }
          }
          this.clearForm()
        } else {
          this.errorMessage = 'Specify details for every schedule'
          this.modalAlert = true
        }
      } else {
        this.errorMessage = 'Specify start and end date and time!'
        this.modalAlert = true
      }
    },
    checkResources () {
      api
        .request('get', '/resources', this.$store.state.accessToken)
        .then(response => {
          this.resources = response.data
          this.populateHosts()
        })
        .catch(error => {
          this.handleError(error)
          this.modalAlert = true
        })
    },
    populateHosts () {
      for (const resource of this.resources) {
        var host = this.hosts.find(h => h.hostname === resource.hostname)
        if (host) {
          host.resources.push(resource)
        } else {
          var newHost = {
            hostname: '',
            resources: []
          }
          newHost.hostname = resource.hostname
          newHost.resources.push(resource)
          this.hosts.push(newHost)
        }
      }
    },
    showRemoveConfirmationDialog (id) {
      this.restrictionId = id
      this.showRemoveRestriction = true
    }
  }
}
</script>

<style>
.white-space {
  white-space: pre-line;

}

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
}

.data_box{
  width: 50vw;
}

.fade-enter-active, .fade-leave-active {
  transition: all .5s;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>
