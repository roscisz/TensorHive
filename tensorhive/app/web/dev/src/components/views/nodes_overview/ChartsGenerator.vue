<template>
  <!-- Main content -->
  <div>
    <button v-on:click="addChart">Add chart</button>
    <div
      v-for="line in lines"
      :key="line.name"
      class="chart_table">
      <NodesTable
        v-for="chart in line.charts"
        :key="chart.name"
        :nodes="chartsNodeLevel"
        />
    </div>
  </div>
</template>

<script>
import NodesTable from './NodesTable.vue'
import api from '../../../api'
export default {
  components: {
    NodesTable
  },

  data: function () {
    return {
      lines: [
        {
          name: 'line 1',
          charts: [
            {
              name: 'chart 1'
            }
          ]
        }
      ],
      chartsNodeLevel: [],
      interval: null,
      nodes: []
    }
  },

  created () {
    this.loadData()
    let self = this
    this.interval = setInterval(function () {
      self.changeData()
    }, 1000)
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

    getCurrentDate () {
      var currentDate = new Date()
      var datetime = currentDate.getDate() +
      '/' + (currentDate.getMonth() + 1) +
      '/' + currentDate.getFullYear() +
      ' @ ' + (currentDate.getHours() < 10 ? '0' + currentDate.getHours() : currentDate.getHours()) +
      ':' + (currentDate.getMinutes() < 10 ? '0' + currentDate.getMinutes() : currentDate.getMinutes()) +
      ':' + (currentDate.getSeconds() < 10 ? '0' + currentDate.getSeconds() : currentDate.getSeconds())
      return datetime
    },

    loadData () {
      api
        .request('get', '/nodes/metrics')
        .then(response => {
          this.nodes = response.data
          this.parseData()
        })
    },

    parseData () {
      var node, nodeName, resource, resourceType, metric, obj
      var metrics = []
      for (var i = 0; i < Object.keys(this.nodes).length; i++) {
        node = this.nodes[Object.keys(this.nodes)[i]]
        nodeName = Object.keys(this.nodes)[i]
        for (var j = 0; j < Object.keys(node).length; j++) {
          resourceType = Object.keys(node)[j]
          resource = node[resourceType][0]
          for (var k = 0; k < Object.keys(resource).length; k++) {
            if (!isNaN(resource[Object.keys(resource)[k]]) && resource[Object.keys(resource)[k]] !== null) {
              metric = this.createMetric(nodeName, resourceType, Object.keys(resource)[k])
              metrics.push(metric)
            }
          }
        }
        obj = {
          nodeName: nodeName,
          metrics: metrics
        }
        this.chartsNodeLevel.push(obj)
      }
    },

    createMetric  (nodeName, resourceType, name) {
      var labels = []
      for (var i = 0; i < 24; i++) {
        labels.push('')
      }
      labels.push(this.getCurrentDate())
      var datasets = []
      for (i = 0; i < this.nodes[nodeName][resourceType].length; i++) {
        datasets.push(
          this.createDataset(
            this.nodes[nodeName][resourceType][i].name + ' ' + resourceType + i,
            this.setColor(i + 1),
            this.nodes[nodeName][resourceType][i][name]
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
      for (var i = 0; i < 24; i++) {
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
      var obj = null
      if (metricName.substr(metricName.length - 3) === '[%]') {
        obj = {
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
            yAxes: [{
              id: 'y-axis-1',
              type: 'linear',
              position: 'left',
              ticks: {
                min: 0,
                max: 100
              }
            }]
          }
        }
      } else {
        obj = {
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
          }
        }
      }
      return obj
    },

    changeData () {
      var node, metric
      var data = []
      for (var i = 0; i < this.chartsNodeLevel.length; i++) {
        node = this.chartsNodeLevel[i]
        api
          .request('get', '/nodes/' + node.nodeName + '/metrics/gpu')
          .then(response => {
            data = response.data
            for (var j = 0; j < node.metrics.length; j++) {
              metric = node.metrics[j]
              for (var k = 0; k < metric.data.datasets.length; k++) {
                metric.data.datasets[k].data.shift()
                metric.data.datasets[k].data.push(data[k][metric.metricName])
              }
              metric.data.labels.shift()
              metric.data.labels.push(this.getCurrentDate())
            }
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
