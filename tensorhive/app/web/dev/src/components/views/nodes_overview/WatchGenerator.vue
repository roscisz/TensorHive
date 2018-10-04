<template>
  <div>
    <v-btn
      color="info"
      small
      outline
      round
      v-on:click="addWatch"
    >
      Add watch
    </v-btn>
    <div class="watch_table" >
      <WatchBox
        class="watch_box"
        v-for="watch in watches"
        :key="watch.index"
        :defaultMetric="watch.default"
        :resources-indexes="resourcesIndexes"
        :chart-datasets="chartDatasets"
        :update-chart="updateChart"
        :time="time"
      />
    </div>
  </div>
</template>

<script>
import WatchBox from './WatchBox.vue'
import api from '../../../api'
import _ from 'lodash'
export default {
  components: {
    WatchBox
  },

  data () {
    return {
      watches: [],
      chartDatasets: {},
      time: 5000,
      chartLength: 25,
      space: 2,
      interval: null,
      errors: [],
      updateChart: false,
      resourcesIndexes: {}
    }
  },

  created () {
    this.loadData()
    let self = this
    this.interval = setInterval(function () {
      self.changeData()
    }, this.time)
  },

  methods: {
    setColor: function (node) {
      var color = '#123456'
      var step = node * 123456
      var colorToInt = parseInt(color.substr(1), 16)
      var nstep = parseInt(step)
      if (!isNaN(colorToInt) && !isNaN(nstep)) {
        colorToInt += nstep
        var ncolor = colorToInt.toString(16)
        ncolor = '#' + (new Array(7 - ncolor.length).join(0)) + ncolor
        if (/^#[0-9a-f]{6}$/i.test(ncolor)) {
          return ncolor
        }
      }
      return color
    },

    loadData: function () {
      api
        .request('get', '/nodes/metrics', this.$store.state.token)
        .then(response => {
          this.watches = [
            {
              index: 0,
              default: 'gpu_util'
            },
            {
              index: 1,
              default: 'mem_used'
            },
            {
              index: 2,
              default: 'processes'
            }
          ]
          this.parseData(response.data)
        })
        .catch(e => {
          this.errors.push(e)
        })
    },

    isVisible: function (metric, metricName) {
      if (metric.value === null) {
        return false
      } else {
        if (metricName === 'mem_total') return false
        return true
      }
    },

    parseData: function (apiResponse) {
      var node, resourceType, metrics, resourceTypes, uniqueMetricNames
      uniqueMetricNames = []
      for (var nodeName in apiResponse) {
        resourceTypes = {}
        node = apiResponse[nodeName]
        if (node !== null) {
          for (var resourceTypeName in node) {
            uniqueMetricNames = []
            resourceType = node[resourceTypeName]
            if (resourceType !== null) {
              metrics = this.findMetrics(resourceType)
              for (var metricName in metrics) {
                uniqueMetricNames.push(metricName)
              }
              resourceTypes[resourceTypeName] = {
                metrics: metrics,
                uniqueMetricNames: uniqueMetricNames
              }
            }
          }
        }
        this.chartDatasets[nodeName] = resourceTypes
      }
    },

    findMetrics: function (resourceType) {
      var resource, metric, tempMetrics, uniqueMetrics
      tempMetrics = {}
      uniqueMetrics = {}
      for (var resourceUUID in resourceType) {
        this.resourcesIndexes[resourceUUID] = resourceType[resourceUUID].index
        resource = resourceType[resourceUUID]
        for (var metricName in resource.metrics) {
          if (isNaN(resource.metrics[metricName])) {
            metric = resource.metrics[metricName]
            metric['visible'] = this.isVisible(resource.metrics[metricName], metricName)
          } else {
            metric = {
              value: resource.metrics[metricName],
              unit: '',
              visible: this.isVisible(resource.metrics[metricName], metricName)
            }
          }
          if (uniqueMetrics.hasOwnProperty(metricName)) {
            if (uniqueMetrics[metricName].visible === false) {
              uniqueMetrics[metricName] = metric
            }
          } else {
            uniqueMetrics[metricName] = metric
          }
        }
      }
      for (var uniqueMetricName in uniqueMetrics) {
        if (uniqueMetrics[uniqueMetricName].visible === true) {
          tempMetrics[uniqueMetricName] = this.createMetric(resourceType, uniqueMetricName)
        }
      }
      return tempMetrics
    },

    createMetric: function (resourceType, metricName) {
      var labels, totalMemory, value, unit, datasets, orderedDatasets
      labels = []
      for (var i = (this.chartLength - 1) * this.time / 1000; i >= 0; i -= this.time / 1000) {
        if (i % ((this.space + 1) * this.time / 1000) === 0) {
          labels.push(i)
        } else {
          labels.push('')
        }
      }
      datasets = []
      for (var resourceUUID in resourceType) {
        if (resourceType[resourceUUID].metrics[metricName] !== null && this.isVisible(resourceType[resourceUUID].metrics[metricName], metricName)) {
          value = isNaN(resourceType[resourceUUID].metrics[metricName]) ? resourceType[resourceUUID].metrics[metricName].value : resourceType[resourceUUID].metrics[metricName]
          unit = isNaN(resourceType[resourceUUID].metrics[metricName]) ? resourceType[resourceUUID].metrics[metricName].unit : ''
          totalMemory = resourceType[resourceUUID].metrics['mem_total'].value
          datasets.push(
            this.createDataset(
              resourceUUID,
              'GPU' + resourceType[resourceUUID].index,
              this.setColor(resourceType[resourceUUID].index + 1),
              value
            )
          )
        }
      }
      orderedDatasets = _.orderBy(datasets, 'label')
      var obj = {
        metricName: metricName,
        data: {
          labels: labels,
          datasets: orderedDatasets
        },
        options: this.createOptions(totalMemory, metricName, unit)
      }
      return obj
    },

    createDataset: function (uuid, label, color, data) {
      var defaultData = []
      for (var i = 0; i < this.chartLength - 1; i++) {
        defaultData.push(0)
      }
      if (data !== null) {
        defaultData.push(data)
      } else {
        defaultData.push(-1)
      }
      var obj = {
        uuid: uuid,
        label: label,
        fill: true,
        borderColor: color,
        pointBackgroundColor: color,
        backgroundColor: 'rgba(0, 0, 0, 0)',
        data: defaultData
      }
      return obj
    },

    createOptions: function (totalMemory, metricName, unit) {
      var obj = {
        responsive: true,
        maintainAspectRatio: false,
        legend: {
          position: 'bottom',
          display: true
        },
        tooltips: {
          mode: 'label',
          xPadding: 10,
          yPadding: 10,
          bodySpacing: 10
        },
        scales: {
          xAxes: [{
            scaleLabel: {
              display: true,
              labelString: 'seconds ago'
            }
          }],
          yAxes: [{
            id: 'y-axis-1',
            type: 'linear',
            position: 'left',
            scaleLabel: {
              display: true,
              labelString: ''
            }
          }]
        }
      }
      obj['scales']['yAxes'][0]['scaleLabel']['labelString'] = unit
      if (metricName === 'mem_util' || metricName === 'gpu_util' || metricName === 'fan_speed') {
        obj['scales']['yAxes'][0]['ticks'] = {
          suggestedMin: 0,
          max: 100
        }
      }
      if (metricName === 'mem_used' || metricName === 'mem_free') {
        obj['scales']['yAxes'][0]['ticks'] = {
          suggestedMin: 0,
          suggestedMax: totalMemory
        }
      }
      return obj
    },

    changeData: function () {
      var node, counter
      counter = Object.keys(this.chartDatasets).length
      for (var nodeName in this.chartDatasets) {
        counter--
        node = this.chartDatasets[nodeName]
        this.apiRequest(node, nodeName, counter)
      }
    },

    apiRequest: function (node, nodeName, counter) {
      var metric, resourceType, value
      var data = []
      api
        .request('get', '/nodes/' + nodeName + '/gpu/metrics', this.$store.state.token)
        .then(response => {
          data = response.data
          for (var resourceTypeName in node) {
            resourceType = node[resourceTypeName]
            for (var metricName in resourceType.metrics) {
              metric = resourceType.metrics[metricName]
              for (var i = 0; i < metric.data.datasets.length; i++) {
                value = isNaN(data[metric.data.datasets[i].uuid][metric.metricName])
                  ? data[metric.data.datasets[i].uuid][metric.metricName].value
                  : data[metric.data.datasets[i].uuid][metric.metricName]
                metric.data.datasets[i].data.shift()
                metric.data.datasets[i].data.push(value)
              }
            }
          }
          if (!counter) {
            this.updateChart = !this.updateChart
          }
        })
        .catch(e => {
          this.errors.push(e)
        })
    },

    addWatch: function () {
      this.watches.push({ index: this.watches.length, default: '' })
    }
  }
}
</script>

<style>
.watch_table{
  display: flex;
  flex-wrap: wrap;
}
.watch_box{
  height: 40vh;
  width: 25vw;
  min-width: 300px;
  margin-left: 3vh;
}
</style>
