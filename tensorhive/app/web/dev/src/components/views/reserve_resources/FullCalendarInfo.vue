<template>
  <v-layout row justify-center>
    <v-dialog
      width="50vw"
      v-model="show"
    >
      <v-card>
        <v-card-text>
          <span class="headline">{{reservation.hostname}}: GPU{{reservation.resourceIndex}}, {{reservation.resourceName}}</span>
          <v-btn
            class="float-right-button"
            flat
            icon
            color="black"
            @click="close()"
          >
            <v-icon>close</v-icon>
          </v-btn>
        </v-card-text>
        <v-card-text>
          <b>Title:</b> {{reservation.title}}
        </v-card-text>
        <v-card-text v-if="updateCard">
          <v-textarea
            outline
            label="Title"
            v-model="newTitle"
          ></v-textarea>
        </v-card-text>
        <v-card-text>
          <b>Description:</b> {{reservation.description}}
        </v-card-text>
        <v-card-text v-if="updateCard">
          <v-textarea
            outline
            label="Description"
            v-model="newDescription"
          ></v-textarea>
        </v-card-text>
        <v-card-text>
          <b>Average GPU utilization:</b> {{gpuUtilAvg}}
        </v-card-text>
        <v-card-text>
          <b>Average GPU memory utilization:</b> {{memUtilAvg}}
        </v-card-text>
        <v-card-text>
          <b>Start:</b> {{ prettyDate(reservation.start) }}
        </v-card-text>
        <v-card-text v-if="updateCard">
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
                  v-model="newStartDate"
                  label="Start date"
                  prepend-icon="event"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="newStartDate"
                @input="startDateMenu = false"
              ></v-date-picker>
            </v-menu>
            <v-menu
              ref="startMenu"
              v-model="startTimeMenu"
              :close-on-content-click="false"
              :nudge-right="40"
              :return-value.sync="newStartTime"
              lazy
              transition="none"
              offset-y
              full-width
              max-width="290px"
              min-width="290px"
            >
              <template v-slot:activator="{ on }">
                <v-text-field
                  v-model="newStartTime"
                  label="Start time"
                  prepend-icon="access_time"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-time-picker
                v-if="startTimeMenu"
                v-model="newStartTime"
                full-width
                :allowed-minutes="m => m % 30 === 0"
                format="24hr"
                @click:minute="$refs.startMenu.save(newStartTime)"
              ></v-time-picker>
            </v-menu>
          </v-layout>
        </v-card-text>
        <v-card-text>
           <b>End:</b> {{ prettyDate(reservation.end) }}
        </v-card-text>
        <v-card-text v-if="updateCard">
          <v-layout align-center justify-start>
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
                  v-model="newEndDate"
                  label="End date"
                  prepend-icon="event"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="newEndDate"
                @input="endDateMenu = false"
              ></v-date-picker>
            </v-menu>
            <v-menu
              ref="endMenu"
              v-model="endTimeMenu"
              :close-on-content-click="false"
              :nudge-right="40"
              :return-value.sync="newEndTime"
              lazy
              transition="none"
              offset-y
              full-width
              max-width="290px"
              min-width="290px"
            >
              <template v-slot:activator="{ on }">
                <v-text-field
                  v-model="newEndTime"
                  label="End time"
                  prepend-icon="access_time"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-time-picker
                v-if="endTimeMenu"
                v-model="newEndTime"
                full-width
                :allowed-minutes="m => m % 30 === 0"
                format="24hr"
                @click:minute="$refs.endMenu.save(newEndTime)"
              ></v-time-picker>
            </v-menu>
          </v-layout>
        </v-card-text>
        <v-card-text>
          <b>GPU UUID:</b> {{reservation.resourceId}}
        </v-card-text>
        <v-card-text v-if="tasksCard">
          <v-alert
            v-model="showAlert"
            dismissible
            type="warning"
          >
            Synchronization in progress. Task assign is disabled now.
          </v-alert>
        </v-card-text>
        <v-data-table
          v-if="tasksCard"
          v-model="selected"
          :headers="headers"
          :items="tasks"
          :pagination.sync="pagination"
          :loading="actionFlag"
          select-all
          item-key="id"
          class="elevation-1"
          :key="tableKey"
        >
          <template v-slot:headers="props">
            <tr>
              <th>
                <v-checkbox
                  :input-value="props.all"
                  :indeterminate="props.indeterminate"
                  primary
                  hide-details
                  @click.stop="toggleAll"
                ></v-checkbox>
              </th>
              <th
                v-for="header in props.headers"
                :key="header.text"
                :class="['column sortable', pagination.descending ? 'desc' : 'asc', header.value === pagination.sortBy ? 'active' : '']"
                @click="changeSort(header.value)"
              >
                <v-icon small>arrow_upward</v-icon>
                {{ header.text }}
              </th>
            </tr>
          </template>
          <v-progress-linear
            v-slot:progress
            :indeterminate="true"
          ></v-progress-linear>
          <template v-slot:items="props">
            <tr :active="props.selected" @click="props.selected = !props.selected">
              <td>
                <v-checkbox
                  :input-value="props.selected"
                  primary
                  hide-details
                ></v-checkbox>
              </td>
              <td>{{ props.item.id }}</td>
              <td class="task-command">{{ props.item.command }}</td>
              <td>{{ prettyDate(props.item.spawnAt) }}</td>
              <td>{{ prettyDate(props.item.terminateAt) }}</td>
            </tr>
          </template>
        </v-data-table>
        <v-btn
          v-if="tasksCard"
          class="float-right-button"
          color="info"
          small
          round
          @click="checkActionFlag()"
        >
          Assign selected
        </v-btn>
        <v-card-text v-if="actionsAbility" class="container">
          <v-btn
            class="float-right-button"
            color="yellow"
            small
            round
            @click="tasksCard=!tasksCard; cancelCard=false; updateCard=false"
          >
            Schedule task(s) for this reservation
          </v-btn>
          <v-btn
            class="float-right-button"
            color="error"
            small
            round
            @click="cancelCard=!cancelCard; tasksCard=false; updateCard=false"
          >
            Cancel reservation
          </v-btn>
          <v-btn
            class="float-right-button"
            color="info"
            small
            round
            @click="updateCard=!updateCard; tasksCard=false, cancelCard=false"
          >
            Edit reservation
          </v-btn>
        </v-card-text>
        <v-card-text v-if="cancelCard">
          Do you want to cancel selected reservation?
          <v-btn
            color="error"
            small
            outline
            round
            @click="cancelCard=false"
          >
            No
          </v-btn>
          <v-btn
            color="success"
            round
            @click="cancelReservation()"
          >
            Yes
          </v-btn>
        </v-card-text>
        <v-card-text v-if="updateCard">
          <v-btn
            color="error"
            small
            outline
            round
            @click="updateCard=false"
          >
            Back
          </v-btn>
          <v-btn
            color="success"
            round
            @click="updateReservation()"
          >
            Update
          </v-btn>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-layout>
</template>

<script>
import api from '../../../api'
import moment from 'moment'
export default {
  name: 'FullCalendarInfo',

  props: {
    showModal: Boolean,
    reservation: Object,
    cancel: Function,
    update: Function,
    refreshTasks: Boolean,
    nodes: Object
  },

  computed: {
    actionsAbility () {
      return this.reservation.userId === this.$store.state.id || this.$store.state.role === 'admin'
    },

    gpuUtilAvg () {
      if (this.reservation.gpuUtilAvg === null) {
        return 'Reservation is not completed yet, no data'
      } else if (this.reservation.gpuUtilAvg === -1) {
        return 'This GPU does not support NVIDIA-SMI'
      } else {
        return this.reservation.gpuUtilAvg + '%'
      }
    },

    memUtilAvg () {
      if (this.reservation.memUtilAvg === null) {
        return 'Reservation is not completed yet, no data'
      } else if (this.reservation.memUtilAvg === -1) {
        return 'This GPU does not support NVIDIA-SMI'
      } else {
        return this.reservation.memUtilAvg + '%'
      }
    },
    reservationTitle () {
      return this.reservation.title
    },

    reservationDescription () {
      return this.reservation.description
    },

    reservationStart () {
      return this.reservation.start
    },

    reservationEnd () {
      return this.reservation.end
    }
  },

  watch: {
    reservation () {
      for (var nodeName in this.nodes) {
        for (var gpuUUID in this.nodes[nodeName].GPU) {
          if (gpuUUID === this.reservation.resourceId) {
            var resource = this.nodes[nodeName].GPU[gpuUUID]
            this.reservation['hostname'] = nodeName
            this.reservation['resourceIndex'] = resource.index
            this.reservation['resourceName'] = resource.name
          }
        }
      }
    },

    showModal () {
      this.show = this.showModal
    },
    show () {
      if (this.show === false) this.close()
    },

    refreshTasks () {
      this.getTasks()
    },

    reservationTitle () {
      this.newTitle = this.reservationTitle
    },

    reservationDescription () {
      this.newDescription = this.reservationDescription
    },

    reservationStart () {
      if (this.reservationStart !== null) {
        this.newStartDate = moment(this.reservationStart).format('YYYY-MM-DD')
        this.newStartTime = moment(this.reservationStart).format('HH:mm')
      } else {
        this.newStartDate = ''
        this.newStartTime = ''
      }
    },

    reservationEnd () {
      if (this.reservationEnd !== null) {
        this.newEndDate = moment(this.reservationEnd).format('YYYY-MM-DD')
        this.newEndTime = moment(this.reservationEnd).format('HH:mm')
      } else {
        this.newEndDate = ''
        this.newEndTime = ''
      }
    }
  },

  data () {
    return {
      tasksCard: false,
      cancelCard: false,
      updateCard: false,
      newTitle: '',
      newDescription: '',
      startTimeMenu: false,
      startDateMenu: false,
      endTimeMenu: false,
      endDateMenu: false,
      newStartDate: '',
      newStartTime: '',
      newEndDate: '',
      newEndTime: '',
      pagination: {
        sortBy: 'name'
      },
      tasks: [],
      selected: [],
      selectedIndex: 0,
      headers: [
        { text: 'ID', value: 'id' },
        { text: 'Command', value: 'command' },
        { text: 'Spawn at', value: 'spawnAt' },
        { text: 'Terminate at', value: 'terminateAt' }
      ],
      tableKey: 0,
      actionFlag: false,
      showAlert: false,
      show: false
    }
  },

  methods: {
    prettyDate (date) {
      if (date !== null) {
        return moment(date).format('dddd, MMMM Do, HH:mm')
      } else {
        return null
      }
    },

    getTasks: function () {
      api
        .request('get', '/tasks?userId=' + this.$store.state.id + '&syncAll=false', this.$store.state.accessToken)
        .then(response => {
          this.tasks = response.data.tasks
        })
        .catch(error => {
          this.$emit('handleError', error)
        })
    },

    checkActionFlag: function () {
      if (this.actionFlag === false) {
        this.actionFlag = true
        this.showAlert = true
        this.scheduleTasks()
      }
    },

    scheduleTasks: function () {
      var id
      id = this.selected[this.selectedIndex].id
      var newTask = this.adjustHostAndCommand()
      newTask['spawnAt'] = this.reservation.start
      newTask['terminateAt'] = this.reservation.end
      api
        .request('put', '/tasks/' + id, this.$store.state.accessToken, newTask)
        .then(response => {
          this.getTask(id)
        })
        .catch(error => {
          this.$emit('handleError', error)
          this.getTask(id)
        })
    },

    adjustHostAndCommand: function () {
      for (var nodeName in this.nodes) {
        for (var gpuUUID in this.nodes[nodeName].GPU) {
          if (gpuUUID === this.reservation.resourceId) {
            return {
              hostname: nodeName,
              command: this.setCommand(this.nodes[nodeName].GPU[gpuUUID].index)
            }
          }
        }
      }
      return {}
    },

    setCommand: function (index) {
      var command = this.selected[this.selectedIndex].command
      var splitCommand = command.split(' ')
      splitCommand[0] = 'CUDA_VISIBLE_DEVICES=' + index
      return splitCommand.join(' ')
    },

    getTask: function (id) {
      api
        .request('get', '/tasks/' + id, this.$store.state.accessToken)
        .then(response => {
          this.updateTask(id, response.data.task)
          this.selectedIndex++
          if (this.selectedIndex < this.selected.length) {
            this.scheduleTasks()
          } else {
            this.selectedIndex = 0
            this.actionFlag = false
            this.showAlert = false
          }
        })
        .catch(error => {
          this.$emit('handleError', error)
          this.selectedIndex++
          if (this.selectedIndex < this.selected.length) {
            this.scheduleTasks()
          } else {
            this.selectedIndex = 0
            this.actionFlag = false
            this.showAlert = false
          }
        })
    },

    updateTask: function (id, newData) {
      for (var index in this.tasks) {
        if (this.tasks[index].id === id) {
          if (newData !== null) {
            this.tasks[index] = newData
          } else {
            this.tasks.splice(index, 1)
          }
        }
      }
      this.tableKey++
    },

    toggleAll () {
      if (this.selected.length) this.selected = []
      else this.selected = this.tasks.slice()
    },

    changeSort (column) {
      if (this.pagination.sortBy === column) {
        this.pagination.descending = !this.pagination.descending
      } else {
        this.pagination.sortBy = column
        this.pagination.descending = false
      }
    },

    close: function () {
      this.$emit('close')
    },

    cancelReservation: function () {
      this.cancel(this.reservation)
    },

    updateReservation: function () {
      var newTime = [moment(this.newStartDate + 'T' + this.newStartTime), moment(this.newEndDate + 'T' + this.newEndTime)]
      this.update(this.reservation, newTime, this.newTitle, this.newDescription)
    }
  }
}
</script>

<style>
.float-right-button {
  float: right;
}
.container {
  overflow: hidden;
}
</style>
