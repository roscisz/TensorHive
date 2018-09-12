<template>
  <section class="content">
    <section id="calendar_section">
      <a href="#filter_section">Adjust filters</a>
      <FullCalendar :selected-resources="selectedResources"/>
    </section>
    <section id="filter_section">
      <a href="#calendar_section">Jump up</a>
      <div style="text-align: center">Select visible resources</div>
      <div class="infrastructure_table">
        <div
          class="infrastructure_box"
          v-for="node in parsedNodes"
          :key="node.nodeName"
        >
          <div
            class="paragraph"
          >
            <input
              type="checkbox"
              v-model="node.checked"
              @change="changeNode(node)"
            >
            {{ node.nodeName }}
            <button @click="toggle(node)">[{{ node.open ? '-' : '+' }}]</button>
            <div
              class="paragraph"
              v-show="node.open"
              v-for="resourceType in node.resourceTypes"
              :key="resourceType.name"
            >
              <input
                type="checkbox"
                v-model="resourceType.checked"
                @change="changeResourceType(resourceType, node)"
              >
              {{ resourceType.name }}
              <button @click="toggle(resourceType)">[{{ resourceType.open ? '-' : '+' }}]</button>
              <div
                class="paragraph"
                v-show="resourceType.open"
                v-for="resource in resourceType.resources"
                :key="resource.resourceIndex"
              >
                <input
                  type="checkbox"
                  v-model="resource.metrics.checked"
                  @change="changeResource(resource, resourceType, node)"
                >
                GPU{{ resource.resourceIndex }} {{ resource.resourceName }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </section>
</template>

<script>
import api from '../../api'
import _ from 'lodash'
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
      selectedResources: [],
      nodeCheckbox: false,
      resourceTypeCheckbox: false,
      resourceCheckbox: false
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
              resourceUUID: resourceUUID,
              resourceName: resourceType[resourceUUID].name,
              resourceIndex: resourceType[resourceUUID].index,
              metrics: resourceType[resourceUUID].metrics
            }
            tempResource.metrics['checked'] = false
            resources.push(tempResource)
          }
          orderedResources = _.orderBy(resources, 'resourceIndex')
          tempResourceType = {
            name: resourceTypeName,
            checked: false,
            open: false,
            resources: orderedResources
          }
          resourceTypes.push(tempResourceType)
        }
        tempNode = {
          nodeName: nodeName,
          checked: false,
          open: false,
          resourceTypes: resourceTypes
        }
        this.parsedNodes.push(tempNode)
      }
    },

    changeNode (node) {
      this.nodeCheckbox = true
      for (var resourceTypeName in node.resourceTypes) {
        node.resourceTypes[resourceTypeName].checked = node.checked
        this.changeResourceType(node.resourceTypes[resourceTypeName])
      }
      this.loadCalendar()
      this.nodeCheckbox = false
    },

    changeResourceType (resourceType, node) {
      this.resourceTypeCheckbox = true
      if (!this.resourceCheckbox) {
        for (var resourceName in resourceType.resources) {
          resourceType.resources[resourceName].metrics.checked = resourceType.checked
          this.changeResource(resourceType.resources[resourceName])
        }
      }
      if (!this.nodeCheckbox) {
        var checked = true
        for (var resourceTypeName in node.resourceTypes) {
          if (!node.resourceTypes[resourceTypeName].checked) {
            checked = false
            break
          }
        }
        node.checked = checked
        this.loadCalendar()
      }
      this.resourceTypeCheckbox = false
    },

    changeResource (resource, resourceType, node) {
      this.resourceCheckbox = true
      if (!this.resourceTypeCheckbox && !this.nodeCheckbox) {
        this.loadCalendar()
      }
      if (!this.resourceTypeCheckbox) {
        var checked = true
        for (var resourceName in resourceType.resources) {
          if (!resourceType.resources[resourceName].metrics.checked) {
            checked = false
            break
          }
        }
        resourceType.checked = checked
        this.changeResourceType(resourceType, node)
      }
      this.resourceCheckbox = false
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
                uuid: resource.resourceUUID,
                index: resource.resourceIndex
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
.infrastructure_table{
  display: flex;
  flex-wrap: wrap;
}
.infrastructure_box{
  width: 20vw;
  margin-left: 1vw;
}
</style>
