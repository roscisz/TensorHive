<template>
  <v-dialog
    width="80vw"
    v-model="show"
  >
    <v-card>
      <v-card-text>
        <v-btn
          class="float-right-button"
          flat
          icon
          color="black"
          @click="close()"
        >
          <v-icon>close</v-icon>
        </v-btn>
        <span class="headline">Edit task</span>
      </v-card-text>
      <v-card-text>
        <v-layout align-center justify-start>
          <v-text-field
            class="host-input"
            label="Hostname"
            small
            v-model="newHost"
          ></v-text-field>
          <span class="space"/>
          <v-text-field
            class="command-input"
            label="Command"
            small
            v-model="newCommand"
          ></v-text-field>
        </v-layout>
      </v-card-text>
      <v-card-text>
        <v-layout align-center justify-end>
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
      newCommand: '',
      show: false
    }
  },

  watch: {
    showModal () {
      this.show = this.showModal
    },
    show () {
      if (this.show === false) this.close()
    },
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
.float-right-button {
  float: right;
}
.host-input{
  min-width: 10vw !important;
  max-width: 10vw !important;
}
.command-input{
  min-width: 65vw !important;
  max-width: 65vw !important;
}
</style>
