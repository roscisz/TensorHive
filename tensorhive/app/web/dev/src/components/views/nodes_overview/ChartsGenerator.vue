<template>
  <!-- Main content -->
  <div>
    <button v-on:click="addChart">Add chart</button>
    <div
      v-for="line in lines"
      :key="line.name"
      class="chart_table">
      <ChartBox
        v-for="chart in line.charts"
        :key="chart.name"
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
      lines: [],
      chartDatasets: {},
      time: 5000,
      chartLength: 25,
      space: 2,
      interval: null,
      apiResponse: null,
      errors: [],
      updateChart: false,
      totalMemory: 0
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

    loadData () {
      api
        .request('get', '/nodes/metrics')
        .then(response => {
          this.apiResponse = response.data
          this.parseData()
          var obj = {
            name: 'line 1',
            charts: [
              {
                name: 'chart 1'
              }
            ]
          }
          this.lines.push(obj)
        })
        .catch(e => {
          this.errors.push(e)
        })
    },

    parseData () {
      var node, resource, metric, metricsObj, resourceTypes
      for (var nodeName in this.apiResponse) {
        resourceTypes = {}
        node = this.apiResponse[nodeName]
        for (var resourceTypeName in node) {
          resource = node[resourceTypeName][0]
          metricsObj = {}
          this.totalMemory = resource['mem_total']
          for (var metricName in resource) {
            if (!isNaN(resource[metricName]) && resource[metricName] !== null && metricName !== 'mem_total') {
              metric = this.createMetric(nodeName, resourceTypeName, metricName)
              metricsObj[metricName] = metric
            }
          }
          resourceTypes[resourceTypeName] = metricsObj
        }
        this.chartDatasets[nodeName] = resourceTypes
      }
    },

    createMetric  (nodeName, resourceType, name) {
      var labels = []
      for (var i = (this.chartLength - 1) * this.time / 1000; i >= 0; i -= this.time / 1000) {
        if (i % ((this.space + 1) * this.time / 1000) === 0) {
          labels.push(i)
        } else {
          labels.push('')
        }
      }
      var datasets = []
      for (i = 0; i < this.apiResponse[nodeName][resourceType].length; i++) {
        datasets.push(
          this.createDataset(
            this.apiResponse[nodeName][resourceType][i].name + ' ' + resourceType + i,
            this.setColor(i + 1),
            this.apiResponse[nodeName][resourceType][i][name]
          )
        )
      }
      var obj = {
        metricName: name,
        data: {
          labels: labels,
          datasets: datasets
        },
        options: this.createOptions(name)
      }
      return obj
    },

    createDataset (label, color, data) {
      var defaultData = []
      for (var i = 0; i < this.chartLength - 1; i++) {
        defaultData.push(0)
      }
      defaultData.push(data)
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

    createOptions (metricName) {
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
      switch (metricName) {
        case 'gpu_util' :
          obj['scales']['yAxes'][0]['scaleLabel']['labelString'] = '%'
          break
        case 'mem_free' :
          obj['scales']['yAxes'][0]['scaleLabel']['labelString'] = 'MiB'
          break
        case 'mem_used' :
          obj['scales']['yAxes'][0]['scaleLabel']['labelString'] = 'MiB'
          break
        case 'mem_util' :
          obj['scales']['yAxes'][0]['scaleLabel']['labelString'] = '%'
          break
        case 'power' :
          obj['scales']['yAxes'][0]['scaleLabel']['labelString'] = 'W'
          break
        case 'temp' :
          obj['scales']['yAxes'][0]['scaleLabel']['labelString'] = ''
          break
        default :
          break
      }
      if (metricName === 'mem_util' || metricName === 'gpu_util') {
        obj['scales']['yAxes'][0]['ticks'] = {
          min: 0,
          max: 100
        }
      }
      if (metricName === 'mem_used' || metricName === 'mem_free') {
        obj['scales']['yAxes'][0]['ticks'] = {
          min: 0,
          suggestedMax: this.totalMemory
        }
      }
      return obj
    },

    changeData () {
      var node, metric, resourceType
      var data = []
      for (var nodeName in this.chartDatasets) {
        node = this.chartDatasets[nodeName]
        api
          .request('get', '/nodes/' + nodeName + '/metrics/gpu')
          .then(response => {
            data = response.data
            for (var resourceTypeName in node) {
              resourceType = node[resourceTypeName]
              for (var metricName in resourceType) {
                metric = resourceType[metricName]
                for (var i = 0; i < metric.data.datasets.length; i++) {
                  metric.data.datasets[i].data.shift()
                  metric.data.datasets[i].data.push(data[i][metric.metricName])
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

    addChart () {
      var chart
      if (this.lines[this.lines.length - 1].charts.length < 3) {
        chart = {
          name: 'chart ' + (this.lines.length) + ':' + (this.lines[this.lines.length - 1].charts.length + 1)
        }
        this.lines[this.lines.length - 1].charts.push(chart)
      } else {
        chart = {
          name: 'chart ' + (this.lines.length + 1) + ':' + 1
        }
        var line = {
          name: 'line ' + (this.lines.length + 1),
          charts: [chart]
        }
        this.lines.push(line)
      }
    }
  }
}
</script>

<style>
.chart_table{
  display: flex;
  justify-content: left;
}
</style>
