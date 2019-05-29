<template>
  <v-dialog
    persistent
    width="40vw"
    v-model="showModal"
  >
    <v-card>
      <v-card-title>
        <span class="headline">Schedule task</span>
      </v-card-title>
      <v-card-text>
        <v-layout align-center justify-start>
          <v-checkbox
            label="Set spawn time"
            v-model="spawn"
          >
          </v-checkbox>
          <v-menu
            v-model="spawnDateMenu"
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
                v-model="newSpawnDate"
                label="Spawn date"
                prepend-icon="event"
                v-on="on"
              ></v-text-field>
            </template>
            <v-date-picker
              v-model="newSpawnDate"
              @input="spawnDateMenu = false"
            ></v-date-picker>
          </v-menu>
          <v-menu
            ref="spawnMenu"
            v-model="spawnTimeMenu"
            :close-on-content-click="false"
            :nudge-right="40"
            :return-value.sync="newSpawnTime"
            lazy
            transition="none"
            offset-y
            full-width
            max-width="290px"
            min-width="290px"
          >
            <template v-slot:activator="{ on }">
              <v-text-field
                v-model="newSpawnTime"
                label="Spawn time"
                prepend-icon="access_time"
                v-on="on"
              ></v-text-field>
            </template>
            <v-time-picker
              v-if="spawnTimeMenu"
              v-model="newSpawnTime"
              full-width
              format="24hr"
              @click:minute="$refs.spawnMenu.save(newSpawnTime)"
            ></v-time-picker>
          </v-menu>
        </v-layout>
        <v-layout align-center justify-start>
          <v-checkbox
            label="Set terminate time"
            v-model="terminate"
          >
          </v-checkbox>
          <v-menu
            v-model="terminateDateMenu"
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
                v-model="newTerminateDate"
                label="Terminate date"
                prepend-icon="event"
                v-on="on"
              ></v-text-field>
            </template>
            <v-date-picker v-model="newTerminateDate" @input="terminateDateMenu = false"></v-date-picker>
          </v-menu>
          <v-menu
            ref="terminateMenu"
            v-model="terminateTimeMenu"
            :close-on-content-click="false"
            :nudge-right="40"
            :return-value.sync="newTerminateTime"
            lazy
            transition="none"
            offset-y
            full-width
            max-width="290px"
            min-width="290px"
          >
            <template v-slot:activator="{ on }">
              <v-text-field
                v-model="newTerminateTime"
                label="Terminate time"
                prepend-icon="access_time"
                v-on="on"
              ></v-text-field>
            </template>
            <v-time-picker
              v-if="terminateTimeMenu"
              v-model="newTerminateTime"
              full-width
              format="24hr"
              @click:minute="$refs.terminateMenu.save(newTerminateTime)"
            ></v-time-picker>
          </v-menu>
        </v-layout>
      </v-card-text>
      <v-card-text>
        <v-layout align-center justify-end>
          <v-btn
            color="info"
            small
            outline
            round
            @click="close"
          >
            Cancel
          </v-btn>
          <v-btn
            color="success"
            @click="checkActionFlag"
          >
            Schedule task
          </v-btn>
        </v-layout>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import api from '../../../api'
import moment from 'moment'
export default {
  props: {
    showModal: Boolean,
    taskId: Number,
    spawnTime: String,
    terminateTime: String,
    actionFlag: Boolean,
    multipleFlag: Boolean,
    selected: Array
  },

  data () {
    return {
      spawnTimeMenu: false,
      spawnDateMenu: false,
      terminateTimeMenu: false,
      terminateDateMenu: false,
      spawn: false,
      terminate: false,
      newSpawnDate: '',
      newSpawnTime: '',
      newTerminateDate: '',
      newTerminateTime: '',
      selectedIndex: 0
    }
  },

  watch: {
    spawnTime () {
      if (this.spawnTime !== null) {
        this.newSpawnDate = moment(this.spawnTime).format('YYYY-MM-DD')
        this.newSpawnTime = moment(this.spawnTime).format('HH:mm')
      } else {
        this.newSpawnDate = ''
        this.newSpawnTime = ''
      }
    },
    terminateTime () {
      if (this.terminateTime !== null) {
        this.newTerminateDate = moment(this.terminateTime).format('YYYY-MM-DD')
        this.newTerminateTime = moment(this.terminateTime).format('HH:mm')
      } else {
        this.newTerminateDate = ''
        this.newTerminateTime = ''
      }
    }
  },

  methods: {
    actionSave: function () {
      this.$refs.menu.save(this.newSpawnTime)
    },

    checkActionFlag: function () {
      if (this.actionFlag === false) {
        this.$emit('changeActionFlag', true)
        this.$emit('changeSnackbar', true)
        this.scheduleTasks()
      }
    },

    scheduleTasks: function () {
      var newTask = {}
      if (this.newSpawnTime !== '' && this.newSpawnTime !== null && this.newSpawnTime !== undefined) {
        newTask['spawnAt'] = moment(this.newSpawnDate + 'T' + this.newSpawnTime).toISOString()
      }
      if (this.newTerminateTime !== '' && this.newTerminateTime !== null && this.newTerminateTime !== undefined) {
        newTask['terminateAt'] = moment(this.newTerminateDate + 'T' + this.newTerminateTime).toISOString()
      }
      if (!this.spawn) {
        newTask['spawnAt'] = null
      }
      if (!this.terminate) {
        newTask['terminateAt'] = null
      }
      var id
      if (this.multipleFlag) {
        id = this.selected[this.selectedIndex].id
      } else {
        id = this.taskId
      }
      api
        .request('put', '/tasks/' + id, this.$store.state.accessToken, newTask)
        .then(response => {
          this.close()
          this.getTask(id)
        })
        .catch(error => {
          this.$emit('handleError', error)
          this.close()
          this.getTask(id)
        })
    },

    getTask: function (id) {
      api
        .request('get', '/tasks/' + id, this.$store.state.accessToken)
        .then(response => {
          this.$emit('updateTask', id, response.data.task)
          if (this.multipleFlag) {
            this.selectedIndex++
            if (this.selectedIndex < this.selected.length) {
              this.scheduleTasks()
            } else {
              this.selectedIndex = 0
              this.$emit('changeActionFlag', false)
              this.$emit('changeSnackbar', false)
            }
          } else {
            this.$emit('changeActionFlag', false)
            this.$emit('changeSnackbar', false)
          }
        })
        .catch(error => {
          this.$emit('handleError', error)
          if (this.multipleFlag) {
            this.selectedIndex++
            if (this.selectedIndex < this.selected.length) {
              this.scheduleTasks()
            } else {
              this.selectedIndex = 0
              this.$emit('changeActionFlag', false)
              this.$emit('changeSnackbar', false)
            }
          } else {
            this.$emit('changeActionFlag', false)
            this.$emit('changeSnackbar', false)
          }
        })
    },

    close: function () {
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
</style>
