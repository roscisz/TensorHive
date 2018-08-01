<template>
  <div>
    <vue-tabs
      active-tab-color="#e74c3c"
      active-text-color="white"
      type="pills"
      :start-index="1"
    >
      <v-tab
        v-for="node in nodes"
        :key="node.nodeName"
        :title="node.nodeName"
        icon="ti-user"
      >
        <div style="width: 500px">
          <MetricsTable :metrics="node.metrics"/>
        </div>
      </v-tab>
    </vue-tabs>
  </div>
</template>

<script>
import { VueTabs, VTab } from 'vue-nav-tabs'
import MetricsTable from './MetricsTable.vue'
export default {
  components: {
    VueTabs,
    VTab,
    MetricsTable
  },
  props: {
    nodes: Array
  }
}
</script>

<style>
 @import 'vue-nav-tabs/themes/vue-tabs.css';
</style>
