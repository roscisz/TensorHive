<template>
  <section class="content">
    <v-snackbar
      color="error"
      v-model="snackbar"
      bottom
      multi-line
    >
      {{ errorMessage}}
      <v-btn
        color="white"
        flat
        @click="snackbar = false"
      >
        Close
      </v-btn>
    </v-snackbar>
    <section id="schedule_section">
      <MySchedule @showSnackbar="showSnackbar(...arguments)" @loadResources="loadResources(...arguments)" :parsed-nodes="parsedNodes"/>
    </section>
    <section id="calendar_section">
      <FullCalendar @showSnackbar="showSnackbar(...arguments)" :update-calendar="updateCalendar" :selected-resources="selectedResources"/>
    </section>
  </section>
</template>

<script>
import api from '../../api'
import _ from 'lodash'
import FullCalendar from './reserve_resources/FullCalendar.vue'
import MySchedule from './reserve_resources/MySchedule.vue'
export default {
  components: {
    FullCalendar,
    MySchedule
  },

  data () {
    return {
      nodes: [],
      parsedNodes: [],
      alert: false,
      snackbar: false,
      errorMessage: '',
      updateCalendar: false,
      selectedResources: [],
      nodeCheckbox: false,
      resourceTypeCheckbox: false,
      resourceCheckbox: false
    }
  },

  mounted () {
    if (JSON.parse(window.localStorage.getItem('visibleResources')) === null) {
      api
        .request('get', '/nodes/metrics', this.$store.state.accessToken)
        .then(response => {
          this.nodes = response.data
          this.parseData()
        })
        .catch(error => {
          if (!error.hasOwnProperty('response')) {
            this.showSnackbar(error.message)
          } else {
            this.showSnackbar(error.response.data.msg)
          }
        })
    } else {
      this.parsedNodes = JSON.parse(window.localStorage.getItem('visibleResources'))
      this.loadCalendar()
    }
  },

  methods: {
    loadResources: function (resources) {
      this.selectedResources = []
      for (var id in resources) {
        if (resources[id].selected) {
          var obj = {
            nodeName: resources[id].nodeName,
            name: resources[id].resourceName,
            uuid: id,
            index: resources[id].resourceIndex
          }
          this.selectedResources.push(obj)
        }
      }
      this.updateCalendar = !this.updateCalendar
    },

    toggle: function (node) {
      node.open = !node.open
    },

    parseData () {
      var node, resourceType, resources, resourceTypes, tempResource, tempResourceType, tempNode, orderedResources
      for (var nodeName in this.nodes) {
        resourceTypes = []
        node = this.nodes[nodeName]
        for (var resourceTypeName in node) {
          resources = []
          resourceType = node[resourceTypeName]
          for (var resourceUUID in resourceType) {
            tempResource = {
              nodeName: nodeName,
              resourceUUID: resourceUUID,
              resourceName: resourceType[resourceUUID].name,
              resourceIndex: resourceType[resourceUUID].index,
              metrics: resourceType[resourceUUID].metrics
            }
            tempResource.metrics['checked'] = true
            resources.push(tempResource)
          }
          orderedResources = _.orderBy(resources, 'resourceIndex')
          tempResourceType = {
            name: resourceTypeName,
            checked: true,
            open: false,
            resources: orderedResources
          }
          resourceTypes.push(tempResourceType)
        }
        tempNode = {
          nodeName: nodeName,
          checked: true,
          open: false,
          resourceTypes: resourceTypes
        }
        this.parsedNodes.push(tempNode)
      }
      this.loadCalendar()
    },

    loadCalendar () {
      var node, resourceType, resource, obj
      this.selectedResources = []
      for (var i = 0; i < this.parsedNodes.length; i++) {
        node = this.parsedNodes[i]
        for (var j = 0; j < node.resourceTypes.length; j++) {
          resourceType = node.resourceTypes[j]
          for (var k = 0; k < resourceType.resources.length; k++) {
            resource = resourceType.resources[k]
            if (resource.metrics.checked) {
              obj = {
                nodeName: resource.nodeName,
                name: resource.resourceName,
                uuid: resource.resourceUUID,
                index: resource.resourceIndex
              }
              this.selectedResources.push(obj)
            }
          }
        }
      }
      this.updateCalendar = !this.updateCalendar
      window.localStorage.setItem('visibleResources', JSON.stringify(this.parsedNodes))
    },

    showSnackbar (message) {
      this.errorMessage = message
      this.snackbar = true
    }
  }
}
</script>
