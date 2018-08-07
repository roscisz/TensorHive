<template>
  <div>
    <v-container fluid grid-list-xl>
        <v-select
          v-model="selectedNode"
          :items="nodes"
        ></v-select>

        <v-select
          v-model="selectedResourceType"
          :items="resourceTypes"
        ></v-select>

        <v-select
          v-model="selectedMetric"
          :items="metrics"
        ></v-select>
    </v-container>
    <LineChart :chart-data="metricData" :options="metricOptions" :rerender-chart="rerenderChart" :update-chart="updateChart"/>
  </div>
</template>

<script>
import LineChart from './LineChart.vue'
export default {
  components: {
    LineChart
  },

  props: {
    chartDatasets: Object,
    apiResponse: Object,
    updateChart: Boolean
  },

  methods: {
    loadData () {
      return this.chartDatasets[this.selectedNode][this.selectedResourceType][this.selectedMetric].data
    },

    loadOptions () {
      return this.chartDatasets[this.selectedNode][this.selectedResourceType][this.selectedMetric].options
    },

    fillNodes () {
      var nodes = this.apiResponse
      for (var nodeName in nodes) {
        this.nodes.push(nodeName)
      }
      this.selectedNode = this.nodes[0]
    },

    fillResourceTypes () {
      var resourceTypes = this.apiResponse[this.selectedNode]
      for (var resourceTypeName in resourceTypes) {
        this.resourceTypes.push(resourceTypeName)
      }
      this.selectedResourceType = this.resourceTypes[0]
    },

    fillMetrics () {
      var metrics = this.apiResponse[this.selectedNode][this.selectedResourceType][0]
      for (var metricName in metrics) {
        if (!isNaN(metrics[metricName]) && metrics[metricName] !== null && metricName !== 'mem_total') {
          this.metrics.push(metricName)
        }
      }
      this.selectedMetric = this.metrics[0]
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
      this.rerenderChart = !(this.rerenderChart)
    },
    selectedMetric () {
      this.metricData = this.loadData()
      this.metricOptions = this.loadOptions()
      this.rerenderChart = !(this.rerenderChart)
    }
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
      metricOptions: null
    }
  },

  created () {
    this.fillNodes()
    this.fillResourceTypes()
    this.fillMetrics()
    this.metricData = this.loadData()
    this.metricOptions = this.loadOptions()
  }
}
</script>
