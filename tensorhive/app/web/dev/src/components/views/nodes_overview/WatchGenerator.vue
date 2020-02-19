<template>
  <div>
    <v-alert
      v-model="alert"
      dismissible
      type="error"
    >
      {{ errorMessage }}
    </v-alert>
    <div class="watch_table" >
      <WatchBox
        class="watch_box"
        v-for="watch in watches"
        :key="watch.id"
        :default-node="watch.defaultNode"
        :default-resource-type="watch.defaultResourceType"
        :default-metric="watch.defaultMetric"
        :resources-indexes="resourcesIndexes"
        :chart-datasets="chartDatasets"
        :update-chart="updateChart"
        :time="time"
        @changeDefaultNode="changeDefaultNode(watch.id, ...arguments)"
        @changeDefaultResourceType="changeDefaultResourceType(watch.id, ...arguments)"
        @changeDefaultMetric="changeDefaultMetric(watch.id, ...arguments)"
        @deleteWatch="deleteWatch(watch.id)"
      />
      <div class="button_box">
        <v-btn
          class="big_button"
          fab
          dark
          color="#b8bcc2"
          v-on:click="addWatch"
        >
          <v-icon size="100px" dark>add</v-icon>
        </v-btn>
      </div>
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
      alert: false,
      errorMessage: '',
      updateChart: false,
      resourcesIndexes: {},
      watchIds: 3
    }
  },

  created () {
    this.loadData()
    let self = this
    this.interval = setInterval(function () {
      if (self.$route.fullPath !== '/nodes_overview') {
        clearInterval(self.interval)
      }
      self.changeData()
    }, this.time)
  },

  methods: {
    handleError: function (error) {
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
    },

    saveWatches: function () {
      window.localStorage.setItem('watches', JSON.stringify(this.watches))
      window.localStorage.setItem('watchIds', JSON.stringify(this.watchIds))
    },
    changeDefaultNode: function (id, name) {
      for (var index in this.watches) {
        if (this.watches[index].id === id) {
          this.watches[index].defaultNode = name
        }
      }
      this.saveWatches()
    },
    changeDefaultResourceType: function (id, name) {
      for (var index in this.watches) {
        if (this.watches[index].id === id) {
          this.watches[index].defaultResourceType = name
        }
      }
      this.saveWatches()
    },
    changeDefaultMetric: function (id, name) {
      for (var index in this.watches) {
        if (this.watches[index].id === id) {
          this.watches[index].defaultMetric = name
        }
      }
      this.saveWatches()
    },
    deleteWatch: function (id) {
      for (var index in this.watches) {
        if (this.watches[index].id === id) {
          this.watches.splice(index, 1)
        }
      }
      this.saveWatches()
    },

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
        .request('get', '/nodes/metrics', this.$store.state.accessToken)
        .then(response => {
          if (JSON.parse(window.localStorage.getItem('watches')) === null) {
            var id = 0
            this.watches = []
            for (var host in response.data) {
              var hostData = response.data[host]
              if ('GPU' in hostData) {
                this.watches.push({
                  id: id++,
                  defaultNode: host,
                  defaultResourceType: 'GPU',
                  defaultMetric: 'utilization'
                })
                this.watches.push({
                  id: id++,
                  defaultNode: host,
                  defaultResourceType: 'GPU',
                  defaultMetric: 'mem_used'
                })
                this.watches.push({
                  id: id,
                  defaultNode: host,
                  defaultResourceType: 'GPU',
                  defaultMetric: 'processes'
                })
              } else {
                this.watches.push({
                  id: id++,
                  defaultNode: host,
                  defaultResourceType: 'CPU',
                  defaultMetric: 'utilization'
                })
              }
            }
          } else {
            this.watches = JSON.parse(window.localStorage.getItem('watches'))
            this.watchIds = JSON.parse(window.localStorage.getItem('watchIds'))
          }
          this.parseData(response.data)
        })
        .catch(error => {
          this.handleError(error)
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
              metrics = this.findMetrics(resourceType, resourceTypeName)
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

    findMetrics: function (resourceType, resourceTypeName) {
      var resource, metric, tempMetrics, uniqueMetrics
      tempMetrics = {}
      uniqueMetrics = {}
      for (var resourceUUID in resourceType) {
        if (resourceType[resourceUUID] !== null) {
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
      }
      for (var uniqueMetricName in uniqueMetrics) {
        if (uniqueMetrics[uniqueMetricName].visible === true) {
          tempMetrics[uniqueMetricName] = this.createMetric(resourceType, resourceTypeName, uniqueMetricName)
        }
      }
      return tempMetrics
    },

    createMetric: function (resourceType, resourceTypeName, metricName) {
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
              resourceTypeName + resourceType[resourceUUID].index,
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
      if (metricName === 'mem_util' || metricName === 'utilization' || metricName === 'fan_speed') {
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
      for (var resourceTypeName in node) {
        resourceType = node[resourceTypeName]
        api
          .request('get', '/nodes/' + nodeName + '/' + resourceTypeName.toLowerCase() + '/metrics', this.$store.state.accessToken)
          .then(response => {
            data = response.data
            for (var resourceTypeName in node) {
              resourceType = node[resourceTypeName]
              for (var metricName in resourceType.metrics) {
                metric = resourceType.metrics[metricName]
                for (var i = 0; i < metric.data.datasets.length; i++) {
                  if (_.has(data, metric.data.datasets[i].uuid)) {
                    value = isNaN(data[metric.data.datasets[i].uuid][metric.metricName])
                      ? data[metric.data.datasets[i].uuid][metric.metricName].value
                      : data[metric.data.datasets[i].uuid][metric.metricName]
                    metric.data.datasets[i].data.shift()
                    metric.data.datasets[i].data.push(value)
                  }
                }
              }
            }
            if (!counter) {
              this.updateChart = !this.updateChart
            }
          })
          .catch(error => {
            this.handleError(error)
          })
      }
    },

    addWatch: function () {
      this.watches.push({
        id: this.watchIds,
        defaultNode: '',
        defaultResourceType: 'GPU',
        defaultMetric: ''
      })
      this.watchIds++
      this.saveWatches()
    }
  }
}
</script>

<style>
.button_box{
  margin-top: 10vh;
  margin-left: 10vw;
}
.big_button{
  height: 150px !important;
  width: 150px !important;
}
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
