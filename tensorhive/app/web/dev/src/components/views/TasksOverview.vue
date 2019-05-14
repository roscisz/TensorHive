<template>
  <section class="content">
    <TaskCreate
      :show-modal="showModalCreate"
      @close="showModalCreate = false"
      @getTasks="getTasks"
      :hostnames="hostnames"
      :hosts="hosts"
      :actionFlag="actionFlag"
    />
    <TaskEdit
      :show-modal="showModalEdit"
      @close="showModalEdit = false"
      @getTask="getTask(...arguments)"
      @changeActionFlag="changeActionFlag(...arguments)"
      @changeSnackbar="changeSnackbar(...arguments)"
      :taskId="taskId"
      :hostname="newHostname"
      :command="newCommand"
      :actionFlag="actionFlag"
    />

    <TaskSchedule
      :show-modal="showModalSchedule"
      @close="showModalSchedule = false"
      @updateTask="updateTask(...arguments)"
      @changeActionFlag="changeActionFlag(...arguments)"
      @changeSnackbar="changeSnackbar(...arguments)"
      :taskId="taskId"
      :spawnTime="newSpawnTime"
      :terminateTime="newTerminateTime"
      :actionFlag="actionFlag"
      :multipleFlag="multipleFlag"
      :selected="selected"
    />
    <TaskLog
      :show-modal="showModalLog"
      @close="showModalLog = false"
      :lines="logs"
      :path="path"
    />
    <v-dialog
      v-model="showModalHowItWorks"
      width="500"
    >
      <v-card>
        <v-card-title
          class="headline grey lighten-2"
          primary-title
        >
          How it works
        </v-card-title>
        <v-card-text>
          Your tasks are managed by `screen` program installed on each machine. You can attach
          to/close them as they are running. Screen sessions created by TensorHive have custom
          names so you won't be confused which is which.<br><br>
          When your task command stops executing, screen session will disappear from `screen -ls`
          but stdout produced your process will be redirected to a log file.
          Logs are automatically gathered and stored on that machine under `~/TensorHiveLogs`
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            flat
            @click="showModalHowItWorks = false"
          >
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-data-table
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
            <v-layout align-center justify-start>
              <v-checkbox
                :input-value="props.all"
                :indeterminate="props.indeterminate"
                primary
                hide-details
                @click.stop="toggleAll"
              ></v-checkbox>
              <v-tooltip
                right
              >
                <template v-slot:activator="{ on }">
                  <v-icon
                    v-on="on"
                    @click="showModalHowItWorks = true"
                  >
                    info
                  </v-icon>
                </template>
                <span>How it works</span>
              </v-tooltip>
            </v-layout>
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
          <td>{{ props.item.hostname}}</td>
          <td class="task-command">{{ props.item.command }}</td>
          <td>{{ props.item.pid }}</td>
          <td>{{ props.item.status }}</td>
          <td>{{ prettyDate(props.item.spawnAt) }}</td>
          <td>{{ prettyDate(props.item.terminateAt) }}</td>
          <td>
            <v-tooltip top>
              <template v-slot:activator="{ on }">
                <v-icon v-on="on" @click="scheduleTasks(props.item)">
                  timer
                </v-icon>
              </template>
              <span>Schedule task</span>
            </v-tooltip>
            <v-tooltip top>
              <template v-slot:activator="{ on }">
                <v-icon v-on="on" @click="spawnTasks(props.item.id)">
                  play_arrow
                </v-icon>
              </template>
              <span>Spawn task</span>
            </v-tooltip>
            <v-tooltip top>
              <template v-slot:activator="{ on }">
                <v-icon v-on="on" @click="terminateTasks(props.item.id, null)">
                  stop
                </v-icon>
              </template>
              <span>Terminate task - does not guarantee that
                    <br> task will stop (depends on command)</span>
            </v-tooltip>
            <v-tooltip top>
              <template v-slot:activator="{ on }">
                <v-icon style="font-size:20px;" v-on="on" @click="terminateTasks(props.item.id, false)">
                  💀
                </v-icon>
              </template>
              <span>Kill task - use when command is more stubborn</span>
            </v-tooltip>
            <v-tooltip top>
              <template v-slot:activator="{ on }">
                <v-icon style="font-size:20px;" v-on="on" @click="getLog(props.item.id)">
                  description
                </v-icon>
              </template>
              <span>Show log</span>
            </v-tooltip>
            <v-tooltip top>
              <template v-slot:activator="{ on }">
                <v-icon v-on="on" @click="editTask(props.item)">
                  edit
                </v-icon>
              </template>
              <span>Edit task</span>
            </v-tooltip>
            <v-tooltip top>
              <template v-slot:activator="{ on }">
                <v-icon v-on="on" @click="removeTask(props.item.id)">
                  delete
                </v-icon>
              </template>
              <span>Remove task</span>
            </v-tooltip>
          </td>
        </tr>
      </template>
    </v-data-table>
    <div class="text-xs-center pt-2">
      <v-btn color="primary" @click="showModalCreate=true">Create tasks</v-btn>
      <v-tooltip top>
        <template v-slot:activator="{ on }">
          <v-icon v-on="on" @click="scheduleTasks(null)">
            timer
          </v-icon>
        </template>
        <span>Schedule selected tasks</span>
      </v-tooltip>
      <v-tooltip top>
        <template v-slot:activator="{ on }">
          <v-icon v-on="on" @click="spawnTasks(null)">
            play_arrow
          </v-icon>
        </template>
        <span>Spawn selected tasks</span>
      </v-tooltip>
      <v-tooltip top>
        <template v-slot:activator="{ on }">
          <v-icon v-on="on" @click="terminateTasks(null, null)">
            stop
          </v-icon>
        </template>
        <span>Terminate selected tasks - does not guarantee that
          <br>task will stop (depends on command)</span>
      </v-tooltip>
      <v-tooltip top>
        <template v-slot:activator="{ on }">
          <v-icon style="font-size:20px;" v-on="on" @click="terminateTasks(null, false)">
            💀
          </v-icon>
        </template>
        <span>Kill selected tasks - use when command is more stubborn</span>
      </v-tooltip>
    </div>
    <v-snackbar
      color="amber"
      v-model="snackbar"
      bottom
      multi-line
    >
      <span style="color:black"> Synchronization in progress. Actions are not allowed now. </span>
      <v-btn
        color="black"
        flat
        @click="snackbar = false"
      >
        Close
      </v-btn>
    </v-snackbar>
  </section>
</template>

<script>
import api from '../../api'
import moment from 'moment'
import TaskCreate from './tasks_overview/TaskCreate.vue'
import TaskEdit from './tasks_overview/TaskEdit.vue'
import TaskSchedule from './tasks_overview/TaskSchedule.vue'
import TaskLog from './tasks_overview/TaskLog.vue'
export default {
  components: {
    TaskCreate,
    TaskEdit,
    TaskSchedule,
    TaskLog
  },
  data () {
    return {
      pagination: {
        sortBy: 'name'
      },
      selected: [],
      headers: [
        { text: 'ID', value: 'id' },
        { text: 'Hostname', value: 'hostname' },
        { text: 'Command', value: 'command' },
        { text: 'Pid', value: 'pid' },
        { text: 'Status', value: 'status' },
        { text: 'Spawn at', value: 'spawnAt' },
        { text: 'Terminate at', value: 'terminateAt' },
        { text: 'Actions', value: 'id', sortable: false }
      ],
      tasks: [],
      hostnames: [],
      hosts: {},
      showModalCreate: false,
      showModalEdit: false,
      showModalSchedule: false,
      showModalHowItWorks: false,
      showModalLog: false,
      taskId: -1,
      newHostname: '',
      newCommand: '',
      newSpawnTime: '',
      newTerminateTime: '',
      tableKey: 0,
      interval: null,
      time: 60000,
      initialSyncFlag: false,
      snackbar: false,
      selectedIndex: 0,
      actionFlag: false,
      multipleFlag: false,
      logs: [],
      path: '',
      actionType: '',
      gracefully: null
    }
  },

  watch: {
    initialSyncFlag () {
      this.getTasks(true)
    }
  },

  created () {
    let self = this
    this.interval = setInterval(function () {
      if (self.$route.fullPath !== '/tasks_overview') {
        clearInterval(self.interval)
      }
      self.getTasks(true)
    }, this.time)
  },

  mounted () {
    this.getHosts()
    this.getTasks(false)
  },

  methods: {
    prettyDate (date) {
      if (date !== null) {
        return moment(date).format('dddd, MMMM Do, HH:mm')
      } else {
        return null
      }
    },

    changeActionFlag (bool) {
      this.actionFlag = bool
    },
    changeSnackbar (bool) {
      this.snackbar = bool
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

    getHosts: function () {
      api
        .request('get', '/nodes/hostnames', this.$store.state.accessToken)
        .then(response => {
          this.hostnames = response.data
        })
      api
        .request('get', '/nodes/metrics', this.$store.state.accessToken)
        .then(response => {
          this.convertHostsInfo(response.data)
        })
    },

    convertHostsInfo: function (hostsInfo) {
      var hosts = {}
      for (var hostname in hostsInfo) {
        var host = hostsInfo[hostname]
        var resources = ['CPU']
        for (var gpuUUID in host.GPU) {
          resources.push('GPU' + host.GPU[gpuUUID].index)
        }
        hosts[hostname] = { resources: resources }
      }
      this.hosts = hosts
    },

    getTasks: function (sync) {
      if (!this.actionFlag) {
        this.snackbar = true
        this.actionFlag = true
        api
          .request('get', '/tasks?userId=' + this.$store.state.id + '&syncAll=' + sync, this.$store.state.accessToken)
          .then(response => {
            this.snackbar = false
            this.actionFlag = false
            this.tasks = response.data.tasks
            if (!sync) {
              this.initialSyncFlag = !this.initialSyncFlag
            }
          })
          .catch(error => {
            console.log(error)
            this.snackbar = false
            this.actionFlag = false
          })
      }
    },

    spawnTasks: function (id) {
      this.actionType = 'spawn'
      this.prepareActionLoop(id)
    },

    terminateTasks: function (id, gracefully) {
      this.gracefully = gracefully
      this.actionType = 'terminate'
      this.prepareActionLoop(id)
    },

    prepareActionLoop: function (id, actionType) {
      if (id !== null) {
        this.multipleFlag = false
        this.taskId = id
      } else {
        this.multipleFlag = true
      }
      if (!this.actionFlag) {
        this.actionFlag = true
        this.snackbar = true
        this.actionLoop()
      }
    },

    actionLoop: function () {
      var id
      if (this.multipleFlag) {
        id = this.selected[this.selectedIndex].id
      } else {
        id = this.taskId
      }
      var actionPath
      switch (this.actionType) {
        case 'spawn': actionPath = '/tasks/' + id + '/spawn'; break
        case 'terminate': actionPath = '/tasks/' + id + '/terminate?gracefully=' + this.gracefully; break
      }
      api
        .request('get', actionPath, this.$store.state.accessToken)
        .then(response => {
          this.getTaskLoop(id)
        })
        .catch(error => {
          console.log(error)
          this.getTaskLoop(id)
        })
    },

    getTaskLoop: function (id, actionType) {
      api
        .request('get', '/tasks/' + id, this.$store.state.accessToken)
        .then(response => {
          this.updateTask(id, response.data.task)
          this.resumeLoop()
        })
        .catch(error => {
          console.log(error)
          this.resumeLoop()
        })
    },

    resumeLoop: function () {
      if (this.multipleFlag) {
        this.selectedIndex++
        if (this.selectedIndex < this.selected.length) {
          switch (this.actionType) {
            case 'spawn': this.actionLoop(); break
            case 'terminate': this.actionLoop(); break
          }
        } else {
          this.selectedIndex = 0
          this.snackbar = false
          this.actionFlag = false
        }
      } else {
        this.snackbar = false
        this.actionFlag = false
      }
    },

    scheduleTasks: function (task) {
      if (task != null) {
        this.multipleFlag = false
        this.taskId = task.id
        this.newSpawnTime = task.spawn_at
        this.newTerminateTime = task.terminate_at
      } else {
        this.multipleFlag = true
      }
      this.showModalSchedule = true
    },

    editTask: function (task) {
      this.taskId = task.id
      this.newHostname = task.hostname
      this.newCommand = task.command
      this.showModalEdit = true
    },

    getTask: function (id) {
      api
        .request('get', '/tasks/' + id, this.$store.state.accessToken)
        .then(response => {
          this.updateTask(id, response.data.task)
          this.snackbar = false
          this.actionFlag = false
        })
        .catch(error => {
          console.log(error)
          this.snackbar = false
          this.actionFlag = false
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

    removeTask: function (id) {
      if (!this.actionFlag) {
        this.snackbar = true
        this.actionFlag = true
        api
          .request('delete', '/tasks/' + id, this.$store.state.accessToken)
          .then(response => {
            this.snackbar = false
            this.actionFlag = false
            this.updateTask(id, null)
          })
          .catch(error => {
            console.log(error)
            this.snackbar = false
            this.actionFlag = false
          })
      }
    },

    getLog: function (id) {
      if (!this.actionFlag) {
        this.snackbar = true
        this.actionFlag = true
        api
          .request('get', '/tasks/' + id + '/log', this.$store.state.accessToken)
          .then(response => {
            this.logs = response.data.stdout_lines
            this.path = response.data.path
            this.showModalLog = true
            this.snackbar = false
            this.actionFlag = false
          })
          .catch(error => {
            console.log(error)
            this.snackbar = false
            this.actionFlag = false
          })
      }
    }
  }
}
</script>
<style>
.parameter-name-input{
  max-width: 150px;
}
.task-command{
  background-color: #f8f9fa;
  border: 1px solid #eaecf0;
}
.space{
  width: 5px;
}
.task-select{
  max-width:100px;
}
</style>
