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
          :key="resource.uuid"
        >
          <input
            type="checkbox"
            v-model="resource.checked"
            @change="loadCalendar"
          >{{ resource.name }} {{ resource.uuid }}
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
      var node, resourceType, resources, obj
      var resourceTypes = []
      for (var nodeName in this.nodes) {
        resourceTypes = []
        node = this.nodes[nodeName]
        for (var resourceTypeName in node) {
          resources = node[resourceTypeName]
          for (var resource in resources) {
            resources[resource]['checked'] = false
          }
          resourceType = {
            name: resourceTypeName,
            resources: resources
          }
          resourceTypes.push(resourceType)
        }
        obj = {
          nodeName: nodeName,
          resourceTypes: resourceTypes
        }
        this.parsedNodes.push(obj)
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
            if (resource.checked) {
              obj = {
                name: resource.name,
                uuid: resource.uuid
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
