<script>
import { Line } from 'vue-chartjs'

export default {
  extends: Line,
  props: {
    chartData: Object,
    options: Object,
    rerenderChart: Boolean,
    updateChart: Boolean
  },

  watch: {
    rerenderChart () {
      this.$data._chart.destroy()
      this.renderChart(this.chartData, this.options)
    },
    updateChart () {
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
