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
        <span class="headline">
          Task log
          <v-btn
            flat
            icon
            color="green"
            @click="refresh()">
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
        <div v-for="(line, index) in lines" :key="index">
          {{line}}
        </div>
      </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    showModal: Boolean,
    lines: Array,
    path: String,
    taskId: Number
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
    close: function () {
      if (this.autoRefreshIntervalId !== -1) {
        window.clearInterval(this.autoRefreshIntervalId)
        this.autoRefreshIntervalId = -1
      }
      this.$emit('close')
    },
    refresh: function () {
      this.$emit('getLog', this.taskId, this.tailMode)
      if (this.autoRefresh && !this.tailMode) {
        this.autoRefresh = false
        this.toggleAutoRefresh()
      }
    },
    toggleAutoRefresh: function () {
      if (this.autoRefresh) {
        this.autoRefreshIntervalId = window.setInterval(this.refresh, 5000)
      } else {
        window.clearInterval(this.autoRefreshIntervalId)
        this.autoRefreshIntervalId = -1
      }
    }
  }
}
</script>

<style scoped>
.float-right-button {
  float: right;
}
.log_box{
  resize: both;
  background-color: #f8f9fa;
  border: 1px solid #eaecf0;
}
</style>
