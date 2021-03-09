<template>
  <v-dialog width="80vw" v-model="show">
    <template v-slot:activator="{ on: onDialog }">
      <v-tooltip bottom>
        <template v-slot:activator="{ on: onTooltip }">
          <!-- Disabling these rules here since they are bugged. See also: -->
          <!-- https://github.com/vuejs/eslint-plugin-vue/issues/497 -->
          <!-- eslint-disable vue/valid-v-on vue/no-parsing-error -->
          <v-btn
            class="ma-0"
            v-on="{ ...onTooltip, ...onDialog }"
            flat
            icon
            small
            color="grey"
            :readonly="performingAction"
            @click="$emit('open')"
          >
            <!-- eslint-enable vue/valid-v-on vue/no-parsing-error -->
            <v-icon
              style="font-size:20px;"
              v-on="on"
              @click="getLog(taskId)"
            >description</v-icon>
          </v-btn>
        </template>
        <span>Show log</span>
      </v-tooltip>
    </template>
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
        <span class="headline">
          Task log
          <v-btn flat icon color="green" @click="refresh()">
            <v-icon>refresh</v-icon>
          </v-btn>
        </span>
        <span class="subheading">
          <v-checkbox
            flat
            style="display: inline"
            label="Tail mode"
            v-model="tailMode"
            hide-details
          />
          <v-checkbox
            flat
            style="display: inline"
            label="Auto-refresh"
            v-model="autoRefresh"
            v-on="on"
            :disabled="!tailMode"
            hide-details
          />
        </span>
      </v-card-text>
      <v-card-text>
        {{path}}
        <div class="log_box">
          <div v-for="(line, index) in lines" :key="index">{{line}}</div>
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import { getTaskLogs } from '../../../../../api/tasks'
export default {
  props: {
    showModal: Boolean,
    lines: Array,
    path: String,
    taskId: Number,
    performingAction: Boolean
  },
  data () {
    return {
      show: false,
      tailMode: false,
      autoRefresh: false,
      autoRefreshIntervalId: -1
    }
  },
  watch: {
    showModal () {
      this.show = this.showModal
    },
    show () {
      if (this.show === false) this.close()
    },
    tailMode () {
      this.refresh()
    },
    autoRefresh () {
      this.toggleAutoRefresh()
    }
  },
  methods: {
    close () {
      if (this.autoRefreshIntervalId !== -1) {
        window.clearInterval(this.autoRefreshIntervalId)
        this.autoRefreshIntervalId = -1
      }
      this.$emit('close')
    },
    refresh () {
      this.getLog(this.taskId, this.tailMode)
      if (this.autoRefresh && !this.tailMode) {
        this.autoRefresh = false
        this.toggleAutoRefresh()
      }
    },
    toggleAutoRefresh () {
      if (this.autoRefresh) {
        this.autoRefreshIntervalId = window.setInterval(this.refresh, 5000)
      } else {
        window.clearInterval(this.autoRefreshIntervalId)
        this.autoRefreshIntervalId = -1
      }
    },
    getLog (id, tailMode = false) {
      if (!this.actionFlag) {
        this.snackbar = true
        this.actionFlag = true
        getTaskLogs(this.$store.state.accessToken, id, tailMode)
          .then(response => {
            this.logs = response.data.output_lines
            this.path = response.data.path
            this.showModalLog = true
          })
          .catch(error => {
            this.handleError(error)
          }).finally(() => {
            this.snackbar = false
            this.actionFlag = false
          })
      }
    }
  }
}
</script>

<style scoped>
  .float-right-button {
    float: right;
  }
  .log_box {
    resize: both;
    background-color: #f8f9fa;
    border: 1px solid #eaecf0;
  }
</style>
