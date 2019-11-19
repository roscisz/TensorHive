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
    <v-btn
      v-if="!showSchedule"
      color="info"
      small
      round
      @click="showSchedule=true;"
    >
      Select visible GPUs
    </v-btn>
    <section v-show="showSchedule" id="schedule_section">
      <v-btn
        color="info"
        small
        round
        @click="showSchedule=false"
      >
        Hide schedule
      </v-btn>
      <MySchedule @handleError="handleError(...arguments)" @loadResources="loadResources(...arguments)" :parsed-nodes="parsedNodes"/>
    </section>
    <section id="calendar_section">
      <FullCalendar @handleError="handleError(...arguments)" :update-calendar="updateCalendar" :selected-resources="selectedResources" :nodes="nodes"/>
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
      nodes: {},
      parsedNodes: [],
      alert: false,
      snackbar: false,
      errorMessage: '',
      updateCalendar: false,
      selectedResources: [],
      nodeCheckbox: false,
      resourceTypeCheckbox: false,
      resourceCheckbox: false,
      showSchedule: false,
      interval: null,
      time: 30000
    }
  },

  mounted () {
    api
      .request('get', '/nodes/metrics', this.$store.state.accessToken)
      .then(response => {
        this.nodes = response.data
        this.parseData()
      })
      .catch(error => {
        this.handleError(error)
      })
    let self = this
    this.interval = setInterval(function () {
      self.updateCalendar = !self.updateCalendar
    }, this.time)
  },

  methods: {
    handleError: function (error) {
      if (!error.hasOwnProperty('response')) {
        this.showSnackbar(error.message)
      } else {
        if (!error.response.data.hasOwnProperty('msg')) {
          this.showSnackbar(error.response.data)
        } else {
          this.showSnackbar(error.response.data.msg)
        }
      }
    },

    showSnackbar (message) {
      this.errorMessage = message
      this.snackbar = true
    },

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
        resources = []
        for (var resourceTypeName in node) {
          if (resourceTypeName === 'GPU') {
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
    }
  }
}
</script>
