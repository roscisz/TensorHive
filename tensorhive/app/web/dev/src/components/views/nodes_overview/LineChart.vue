<script>
import { Line } from 'vue-chartjs'

export default {
  extends: Line,
  props: {
    chartData: Object,
    options: Object
  },

  computed: {
    dataChanged () {
      debugger
      return this.chartData.labels[this.chartData.labels.length - 1]
    }
  },

  watch: {
    dataChanged () {
      this.$data._chart.update()
    }
  },

  mounted () {
    // this.chartData is created in the mixin.
    // If you want to pass options please create a local options object
    this.renderChart(this.chartData, this.options)
  }
}
</script>
