<template>
  <section class="content">
    <div
      class="paragraph"
      v-for="node in parsedNodes"
      :key="node.nodeName"
    >
      {{ node.nodeName }}
      <div
        class="paragraph"
        v-for="resourceType in node.resourceTypes"
        :key="resourceType.name"
      >
        {{ resourceType.name }}
        <div
          class="paragraph"
          v-for="resource in resourceType.resources"
          :key="resource.resourceIndex"
        >
          <input
            type="checkbox"
            v-model="resource.metrics.checked"
            @change="loadCalendar"
          >
          GPU{{ resource.resourceIndex }} {{ resource.resourceName }} {{resource.resourceUUID}}
        </div>
      </div>
    </div>
    <FullCalendar :selected-resources="selectedResources"/>
  </section>
</template>

<script>
import api from '../../api'
import FullCalendar from './reserve_resources/FullCalendar.vue'
export default {
  components: {
    FullCalendar
  },

  data () {
    return {
      nodes: [],
      parsedNodes: [],
      errors: [],
      selectedResources: []
    }
  },

  created () {
    api
      .request('get', '/nodes/metrics')
      .then(response => {
        this.nodes = response.data
        this.parseData()
      })
      .catch(e => {
        this.errors.push(e)
      })
  },

  methods: {
    parseData () {
      var node, resourceType, resources, resourceTypes, tempResource, tempResourceType, tempNode
      for (var nodeName in this.nodes) {
        resourceTypes = []
        node = this.nodes[nodeName]
        for (var resourceTypeName in node) {
          resources = []
          resourceType = node[resourceTypeName]
          for (var resourceUUID in resourceType) {
            tempResource = {
              resourceUUID: resourceUUID,
              resourceName: resourceType[resourceUUID].name,
              resourceIndex: resourceType[resourceUUID].index,
              metrics: resourceType[resourceUUID].metrics
            }
            tempResource.metrics['checked'] = false
            resources.push(tempResource)
          }
          tempResourceType = {
            name: resourceTypeName,
            resources: resources
          }
          resourceTypes.push(tempResourceType)
        }
        tempNode = {
          nodeName: nodeName,
          resourceTypes: resourceTypes
        }
        this.parsedNodes.push(tempNode)
      }
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
                name: resource.resourceName,
                uuid: resource.resourceUUID
              }
              this.selectedResources.push(obj)
            }
          }
        }
      }
    }
  }
}
</script>

<style>
.paragraph{
  margin-left: 30px;
}
</style>
