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
          <date-picker
            id="spawnTime"
            v-model="newSpawnTime"
            type="datetime"
            lang="en"
            format="YYYY-MM-DD HH:mm"
            :time-picker-options="timePickerOptions"
            confirm
            append-to-body
          ></date-picker>
        </v-layout>
        <v-layout align-center justify-start>
          <v-checkbox
            label="Set terminate time"
            v-model="terminate"
          >
          </v-checkbox>
          <date-picker
            id="terminateTime"
            v-model="newTerminateTime"
            type="datetime"
            lang="en"
            format="YYYY-MM-DD HH:mm"
            :time-picker-options="timePickerOptions"
            confirm
            append-to-body
          ></date-picker>
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
import DatePicker from 'vue2-datepicker'
export default {
  components: {
    DatePicker
  },

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
      spawn: false,
      terminate: false,
      newSpawnTime: '',
      newTerminateTime: '',
      timePickerOptions: {
        start: '00:00',
        step: '00:30',
        end: '23:30'
      },
      selectedIndex: 0
    }
  },

  watch: {
    spawnTime () {
      this.newSpawnTime = this.spawnTime
    },
    terminateTime () {
      this.newTerminateTime = this.terminateTime
    }
  },

  methods: {
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
        newTask['spawnAt'] = this.newSpawnTime.toISOString()
      }
      if (this.newTerminateTime !== '' && this.newTerminateTime !== null && this.newTerminateTime !== undefined) {
        newTask['terminateAt'] = this.newTerminateTime.toISOString()
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
