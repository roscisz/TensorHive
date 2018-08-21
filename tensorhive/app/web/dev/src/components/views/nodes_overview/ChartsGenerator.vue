<template>
  <!-- Main content -->
  <div>
    <button v-on:click="addChart">Add chart</button>
    <div class="chart_table" >
      <ChartBox
        class="chart_box"
        v-for="chart in charts"
        :key="chart.index"
        :api-response="apiResponse"
        :chart-datasets="chartDatasets"
        :update-chart="updateChart"
      />
    </div>
  </div>
</template>

<script>
import ChartBox from './ChartBox.vue'
import api from '../../../api'
export default {
  components: {
    ChartBox
  },

  data () {
    return {
      charts: [],
      chartDatasets: {},
      time: 5000,
      chartLength: 25,
      space: 2,
      interval: null,
      apiResponse: null,
      errors: [],
      updateChart: false,
      uniqueMetrics: {}
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
        .request('get', '/nodes/metrics')
        .then(response => {
          this.apiResponse = response.data
          this.charts = [
            {
              index: 0
            }
          ]
          this.parseData()
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

    parseData: function () {
      var node, resourceType, metrics, resourceTypes
      for (var nodeName in this.apiResponse) {
        resourceTypes = {}
        node = this.apiResponse[nodeName]
        if (node !== null) {
          for (var resourceTypeName in node) {
            resourceType = node[resourceTypeName]
            if (resourceType !== null) {
              metrics = this.findMetrics(resourceType)
              resourceTypes[resourceTypeName] = {
                metrics: metrics,
                uniqueMetricNames: this.uniqueMetrics
              }
            }
          }
        }
        this.chartDatasets[nodeName] = resourceTypes
      }
    },

    findMetrics: function (resourceType) {
      var resource, metric, metrics, tempResource, resources, tempMetrics
      resources = []
      this.uniqueMetrics = {}
      tempMetrics = {}
      for (var resourceUUID in resourceType) {
        metrics = []
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
          if (this.uniqueMetrics.hasOwnProperty(metricName)) {
            if (this.uniqueMetrics[metricName].visible === false) {
              this.uniqueMetrics[metricName] = metric
            }
          } else {
            this.uniqueMetrics[metricName] = metric
          }
          metrics.push(metric)
        }
        tempResource = {
          resourceUUID: resourceUUID,
          resourceName: resourceType[resourceUUID].name,
          resourceIndex: resourceType[resourceUUID].index,
          metrics: metrics
        }
        resources.push(tempResource)
      }
      for (var uniqueMetricName in this.uniqueMetrics) {
        if (this.uniqueMetrics[uniqueMetricName].visible === true) {
          tempMetrics[uniqueMetricName] = this.createMetric(resourceType, uniqueMetricName)
        }
      }
      return tempMetrics
    },

    createMetric: function (resourceType, metricName) {
      var labels = []
      for (var i = (this.chartLength - 1) * this.time / 1000; i >= 0; i -= this.time / 1000) {
        if (i % ((this.space + 1) * this.time / 1000) === 0) {
          labels.push(i)
        } else {
          labels.push('')
        }
      }
      var datasets = []
      var totalMemory
      var value
      for (var resourceUUID in resourceType) {
        if (resourceType[resourceUUID].metrics[metricName] !== null) {
          value = isNaN(resourceType[resourceUUID].metrics[metricName]) ? resourceType[resourceUUID].metrics[metricName].value : resourceType[resourceUUID].metrics[metricName]
          totalMemory = resourceType[resourceUUID].metrics['mem_total'].value
          datasets.push(
            this.createDataset(
              resourceUUID,
              this.setColor(resourceType[resourceUUID].index + 1),
              value
            )
          )
        }
      }
      var obj = {
        metricName: metricName,
        data: {
          labels: labels,
          datasets: datasets
        },
        options: this.createOptions(totalMemory, metricName)
      }
      return obj
    },

    createDataset: function (label, color, data) {
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
        label: label,
        fill: true,
        borderColor: color,
        pointBackgroundColor: color,
        backgroundColor: 'rgba(0, 0, 0, 0)',
        data: defaultData
      }
      return obj
    },

    createOptions: function (totalMemory, metricName) {
      var obj = {
        responsive: true,
        maintainAspectRatio: true,
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
      obj['scales']['yAxes'][0]['scaleLabel']['labelString'] = this.uniqueMetrics[metricName].unit
      if (metricName === 'mem_util' || metricName === 'gpu_util') {
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
      var node, metric, resourceType, value
      var data = []
      for (var nodeName in this.chartDatasets) {
        node = this.chartDatasets[nodeName]
        api
          .request('get', '/nodes/' + nodeName + '/gpu/metrics')
          .then(response => {
            data = response.data
            for (var resourceTypeName in node) {
              resourceType = node[resourceTypeName]
              for (var metricName in resourceType.metrics) {
                metric = resourceType.metrics[metricName]
                for (var i = 0; i < metric.data.datasets.length; i++) {
                  value = isNaN(data[metric.data.datasets[i].label][metric.metricName])
                    ? data[metric.data.datasets[i].label][metric.metricName].value
                    : data[metric.data.datasets[i].label][metric.metricName]
                  metric.data.datasets[i].data.shift()
                  metric.data.datasets[i].data.push(value)
                }
              }
            }
            this.updateChart = !(this.updateChart)
          })
          .catch(e => {
            this.errors.push(e)
          })
      }
    },

    addChart: function () {
      this.charts.push({ index: this.charts.length })
    }
  }
}
</script>

<style>
.chart_table{
  display: flex;
  flex-wrap: wrap;
}
.chart_box{
  height: 40vh;
  width: 25vw;
  margin-left: 3vh;
}
</style>
