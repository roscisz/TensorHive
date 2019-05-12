<template>
  <section class="content">
    <v-data-table
      v-model="selected"
      :headers="headers"
      :items="tasks"
      :pagination.sync="pagination"
      :loading="actionFlag"
      select-all
      item-key="id"
      class="elevation-1"
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
          <td>{{ props.item.spawnAt }}</td>
          <td>{{ props.item.terminateAt }}</td>
          <td></td>
        </tr>
      </template>
    </v-data-table>
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
export default {
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
      interval: null,
      time: 60000,
      initialSyncFlag: false,
      snackbar: false,
      actionFlag: false
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
    changeActionFlag (bool) {
      this.actionFlag = bool
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
        this.actionFlag = true
        this.snackbar = true
        api
          .request('get', '/tasks?userId=' + this.$store.state.id + '&syncAll=' + sync, this.$store.state.accessToken)
          .then(response => {
            this.actionFlag = false
            this.tasks = response.data.tasks
            this.snackbar = false
            if (!sync) {
              this.initialSyncFlag = !this.initialSyncFlag
            }
          })
          .catch(error => {
            console.log(error)
            this.actionFlag = false
          })
      }
    }
  }
}
</script>
<style>
.task-command{
  background-color: #f8f9fa;
  border: 1px solid #eaecf0;
}
</style>
