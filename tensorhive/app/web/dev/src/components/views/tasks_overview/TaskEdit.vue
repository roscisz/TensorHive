<template>
  <v-dialog
    persistent
    width="80vw"
    v-model="showModal"
  >
    <v-card>
      <v-card-title>
        <span class="headline">Edit task</span>
      </v-card-title>
      <v-card-text>
        <v-layout align-center justify-start>
          <v-text-field
            class="task-input"
            label="Hostname"
            small
            v-model="newHost"
          ></v-text-field>
          <span class="space"/>
          <v-text-field
            class="task-input"
            label="Command"
            small
            v-model="newCommand"
          ></v-text-field>
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
            @click="changeTask"
          >
            Edit task
          </v-btn>
        </v-layout>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import api from '../../../api'
export default {
  props: {
    showModal: Boolean,
    taskId: Number,
    hostname: String,
    command: String,
    actionFlag: Boolean
  },

  data () {
    return {
      newHost: '',
      newCommand: ''
    }
  },

  watch: {
    hostname () {
      this.newHost = this.hostname
    },
    command () {
      this.newCommand = this.command
    }
  },

  methods: {
    changeTask: function () {
      var newTask = {
        hostname: this.newHost,
        command: this.newCommand
      }
      if (!this.actionFlag) {
        this.$emit('changeActionFlag', true)
        this.$emit('changeSnackbar', true)
        api
          .request('put', '/tasks/' + this.taskId, this.$store.state.accessToken, newTask)
          .then(response => {
            this.close()
            this.$emit('getTask', this.taskId, true)
          })
      }
    },

    close: function () {
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
</style>
