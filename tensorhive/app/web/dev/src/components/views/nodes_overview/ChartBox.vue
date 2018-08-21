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
    </div>
    <div v-if="showProcesses === true" class="content_box">
      <v-data-table
        :headers="headers"
        :items="processes"
        item-key="pid"
        hide-actions
        class="elevation-1"
      >
        <template slot="items" slot-scope="props">
          <tr @click="props.expanded = !props.expanded">
            <td class="text-xs-right">{{ props.item.owner }}</td>
            <td class="text-xs-right">{{ props.item.pid }}</td>
            <td class="text-xs-right">{{ props.item.command }}</td>
            <td class="text-xs-right">{{ props.item.GPU }}</td>
          </tr>
        </template>
        <template slot="expand" slot-scope="props">
          <v-card flat>
            <v-card-text>GPU: {{ props.item.GPU }}</v-card-text>
          </v-card>
        </template>
      </v-data-table>
    </div>
    <div v-else class="content_box">
      <LineChart :chart-data="metricData" :options="metricOptions" :rerender-chart="rerenderChart" :update-chart="updateChart"/>
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
    chartDatasets: Object,
    apiResponse: Object,
    updateChart: Boolean
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
        { text: 'owner', value: 'owner' },
        { text: 'pid', value: 'pid' },
        { text: 'command', value: 'command' },
        { text: 'GPU', value: 'GPU' }
      ],
      processes: []
    }
  },

  methods: {
    loadData () {
      return this.chartDatasets[this.selectedNode][this.selectedResourceType].metrics[this.selectedMetric].data
    },

    loadOptions () {
      return this.chartDatasets[this.selectedNode][this.selectedResourceType].metrics[this.selectedMetric].options
    },

    fillNodes () {
      var nodes = this.chartDatasets
      for (var nodeName in nodes) {
        this.nodes.push(nodeName)
      }
      this.selectedNode = this.nodes[0]
    },

    fillResourceTypes () {
      var resourceTypes = this.chartDatasets[this.selectedNode]
      for (var resourceTypeName in resourceTypes) {
        this.resourceTypes.push(resourceTypeName)
      }
      this.selectedResourceType = this.resourceTypes[0]
    },

    fillMetrics () {
      var metrics = this.chartDatasets[this.selectedNode][this.selectedResourceType].uniqueMetricNames
      for (var metricName in metrics) {
        if (metrics[metricName].visible) {
          this.metrics.push(metricName)
        }
      }
      this.selectedMetric = this.metrics[0]
    },

    checkProcesses: function () {
      var data, processes, tempProcess
      processes = []
      api
        .request('get', '/nodes/' + this.selectedNode + '/gpu/processes')
        .then(response => {
          data = response.data
          for (var resourceUUID in data) {
            for (var i = 0; i < data[resourceUUID].length; i++) {
              tempProcess = data[resourceUUID][i]
              tempProcess['GPU'] = resourceUUID
              processes.push(tempProcess)
            }
          }
          this.processes = processes
        })
        .catch(e => {
          this.errors.push(e)
        })
    }
  },

  watch: {
    selectedNode () {
      this.fillResourceTypes()
      this.metricData = this.loadData()
      this.metricOptions = this.loadOptions()
      this.rerenderChart = !(this.rerenderChart)
    },
    selectedResourceType () {
      this.fillMetrics()
      this.metricData = this.loadData()
      this.metricOptions = this.loadOptions()
      this.metrics.push('processes')
      this.rerenderChart = !(this.rerenderChart)
    },
    selectedMetric () {
      if (this.selectedMetric === 'processes') {
        this.checkProcesses()
        this.showProcesses = true
      } else {
        this.showProcesses = false
        this.metricData = this.loadData()
        this.metricOptions = this.loadOptions()
        this.rerenderChart = !(this.rerenderChart)
      }
    }
  },

  created () {
    this.fillNodes()
    this.fillResourceTypes()
    this.fillMetrics()
    this.metrics.push('processes')
    this.metricData = this.loadData()
    this.metricOptions = this.loadOptions()
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
.content_box{
  height: 34vh;
  position: relative;
  overflow-y: scroll;
}
</style>
