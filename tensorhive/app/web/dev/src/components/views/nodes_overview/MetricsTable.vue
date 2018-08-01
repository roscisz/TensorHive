<template>
  <div>
    <vue-tabs
      active-tab-color="#e74c3c"
      active-text-color="white"
      type="pills"
      :start-index="1"
    >
      <v-tab
        v-for="metric in metrics"
        :key="metric.metricName"
        :title="metric.metricName"
        icon="ti-user"
      >
        <LineChart :chart-data="metric.data" :options="metric.options"/>
      </v-tab>
    </vue-tabs>
  </div>
</template>

<script>
import { VueTabs, VTab } from 'vue-nav-tabs'
import LineChart from './LineChart.vue'
export default {
  components: {
    VueTabs,
    VTab,
    LineChart
  },

  props: {
    metrics: Array
  }
}
</script>

<style>
 @import 'vue-nav-tabs/themes/vue-tabs.css';
</style>
