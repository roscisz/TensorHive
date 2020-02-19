<template>
  <div>
    <div class="select_line">
      <v-select
        class="select_item"
        v-model="selectedNode"
        :items="nodes"
      ></v-select>
      <div class="select_space"/>
      <v-select
          class="select_item"
          v-model="selectedResourceType"
          :items="resourceTypes"
      ></v-select>
      <div class="select_space"/>
      <v-select
        class="select_item"
        v-model="selectedMetric"
        :items="metrics"
      ></v-select>
      <v-btn
        color="indigo"
        fab
        dark
        small
        outline
        @click="removeMe()"
      >
        <v-icon dark>delete</v-icon>
      </v-btn>
    </div>
    <v-alert
      v-model="alert"
      dismissible
      type="error"
    >
      {{ errorMessage }}
    </v-alert>
    <div v-if="showProcesses === true" class="table_box">
      <v-data-table
        :headers="headers"
        :items="processes"
        item-key="pid"
        hide-actions
        class="elevation-1"
      >
        <template slot="items" slot-scope="props">
          <tr @click="props.expanded = !props.expanded">
            <td class="text-xs-right">{{ props.item.index }}</td>
            <td class="text-xs-right">{{ props.item.owner }}</td>
            <td class="text-xs-right">{{ props.item.pid }}</td>
            <td class="text-xs-right">{{ props.item.command }}</td>
          </tr>
        </template>
        <template slot="expand" slot-scope="props">
          <v-card flat>
            <v-card-text>GPU UUID: {{ props.item.uuid }}</v-card-text>
          </v-card>
        </template>
      </v-data-table>
    </div>
    <div v-else>
      <LineChart
         class="chart_box"
        :chart-data="metricData"
        :options="metricOptions"
        :rerender-chart="rerenderChart"
        :update-chart="updateChart"/>
    </div>
  </div>
</template>

<script>
import LineChart from './LineChart.vue'
import api from '../../../api'
export default {
  components: {
    LineChart
  },

  props: {
    defaultNode: String,
    defaultResourceType: String,
    defaultMetric: String,
    resourcesIndexes: Object,
    chartDatasets: Object,
    updateChart: Boolean,
    time: Number
  },

  data () {
    return {
      selectedNode: '',
      nodes: [],
      selectedResourceType: '',
      resourceTypes: [],
      selectedMetric: '',
      metrics: [],
      rerenderChart: false,
      metricData: null,
      metricOptions: null,
      showProcesses: false,
      interval: null,
      headers: [
        { text: 'GPU index', value: 'index' },
        { text: 'owner', value: 'owner' },
        { text: 'pid', value: 'pid' },
        { text: 'command', value: 'command' }
      ],
      processes: [],
      alert: false,
      errorMessage: ''
    }
  },

  methods: {
    sendDefaultNode: function (newDefault) {
      this.$emit('changeDefaultNode', newDefault)
    },
    sendDefaultResourceType: function (newDefault) {
      this.$emit('changeDefaultResourceType', newDefault)
    },
    sendDefaultMetric: function (newDefault) {
      this.$emit('changeDefaultMetric', newDefault)
    },
    removeMe: function () {
      this.$emit('deleteWatch')
    },

    loadData: function () {
      return this.chartDatasets[this.selectedNode][this.selectedResourceType].metrics[this.selectedMetric].data
    },

    loadOptions: function () {
      return this.chartDatasets[this.selectedNode][this.selectedResourceType].metrics[this.selectedMetric].options
    },

    fillNodes: function () {
      this.nodes = []
      var nodes = this.chartDatasets
      for (var nodeName in nodes) {
        this.nodes.push(nodeName)
      }
      if (this.defaultNode === '') {
        this.selectedNode = this.nodes[0]
      } else {
        this.selectedNode = this.defaultNode
      }
      this.fillResourceTypes()
    },

    fillResourceTypes: function () {
      this.resourceTypes = []
      var resourceTypes = this.chartDatasets[this.selectedNode]
      for (var resourceTypeName in resourceTypes) {
        this.resourceTypes.push(resourceTypeName)
      }
      if (this.defaultResourceType === '') {
        this.selectedResourceType = this.resourceTypes[0]
      } else {
        this.selectedResourceType = this.defaultResourceType
      }
      this.fillMetrics()
    },

    fillMetrics: function () {
      this.metrics = []
      var metrics = this.chartDatasets[this.selectedNode][this.selectedResourceType].uniqueMetricNames
      for (var metricIndex in metrics) {
        this.metrics.push(metrics[metricIndex])
      }
      if (this.selectedResourceType === 'GPU') {
        this.metrics.push('processes')
      }
      if (this.defaultMetric === '') {
        var metric = this.metrics[0]
        for (metricIndex in this.metrics) {
          var metricName = this.metrics[metricIndex]
          if (metricName === 'utilization') {
            metric = metricName
            break
          } else if (metricName === 'mem_used') {
            metric = metricName
          }
        }
        this.selectedMetric = metric
      } else {
        this.selectedMetric = this.defaultMetric
      }
      if (this.selectedNode !== '' && this.selectedResourceType !== '' && this.selectedMetric !== '' && this.selectedMetric !== 'processes') {
        this.metricData = this.loadData()
        this.metricOptions = this.loadOptions()
        this.rerenderChart = !(this.rerenderChart)
      }
    },

    checkProcesses: function () {
      var data, processes, tempProcess
      processes = []
      api
        .request('get', '/nodes/' + this.selectedNode + '/gpu/processes', this.$store.state.accessToken)
        .then(response => {
          data = response.data
          for (var resourceUUID in data) {
            if (data[resourceUUID] !== null) {
              for (var i = 0; i < data[resourceUUID].length; i++) {
                tempProcess = data[resourceUUID][i]
                tempProcess['index'] = this.resourcesIndexes[resourceUUID]
                tempProcess['uuid'] = resourceUUID
                processes.push(tempProcess)
              }
            }
          }
          this.processes = processes
        })
        .catch(error => {
          if (!error.hasOwnProperty('response')) {
            this.errorMessage = error.message
          } else {
            if (!error.response.data.hasOwnProperty('msg')) {
              this.errorMessage = error.response.data
            } else {
              this.errorMessage = error.response.data.msg
            }
          }
          this.alert = true
        })
    }
  },

  watch: {
    selectedNode () {
      this.sendDefaultNode(this.selectedNode)
      this.fillResourceTypes()
    },
    selectedResourceType () {
      this.sendDefaultResourceType(this.selectedResourceType)
      this.fillMetrics()
    },
    selectedMetric () {
      this.sendDefaultMetric(this.selectedMetric)
      if (this.selectedMetric === 'processes') {
        this.checkProcesses()
        let self = this
        this.interval = setInterval(function () {
          if (self.$route.fullPath !== '/nodes_overview') {
            clearInterval(self.interval)
          }
          self.checkProcesses()
        }, this.time)
        this.showProcesses = true
      } else {
        this.showProcesses = false
        this.metricData = this.loadData()
        this.metricOptions = this.loadOptions()
        this.rerenderChart = !(this.rerenderChart)
        if (this.interval !== null) {
          clearInterval(this.interval)
        }
      }
    }
  },

  created () {
    this.fillNodes()
  }
}
</script>

<style>
.select_line{
  display: flex;
  justify-content: left;
  position: sticky
}
.select_space{
  width: 5%;
}
.select_item{
  width: 30%;
  position: sticky;
}
.chart_box{
  width: 100%;
  height: 34vh;
  position: relative;
}
.table_box{
  width: 100%;
  height: 34vh;
  position: relative;
  overflow-y: scroll;
}
</style>
