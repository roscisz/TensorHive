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
    <section id="calendar_section">
      <v-btn
        color= "info"
        small
        outline
        round
        href="#filter_section"
      >
        Adjust filters
      </v-btn>
      <FullCalendar @showSnackbar="showSnackbar(...arguments)" :update-calendar="updateCalendar" :selected-resources="selectedResources"/>
    </section>
    <section id="filter_section">
      <v-btn
        color= "info"
        small
        outline
        round
        href="#calendar_section"
      >
        Jump up
      </v-btn>
      <div class="infrastructure_table">
        <div
          class="infrastructure_box"
          v-for="node in parsedNodes"
          :key="node.nodeName"
        >
          <div
            class="paragraph"
          >
            <v-checkbox
              :label="node.nodeName"
              v-model="node.checked"
              @change="changeNode(node)"
            >
            </v-checkbox>
            <v-btn
              color="indigo"
              fab
              dark
              small
              outline
              @click="toggle(node)"
            >
              <v-icon dark>{{ node.open ? 'remove' : 'add' }}</v-icon>
            </v-btn>
            <div
              class="paragraph"
              v-show="node.open"
              v-for="resourceType in node.resourceTypes"
              :key="resourceType.name"
            >
              <v-checkbox
                :label="resourceType.name"
                v-model="resourceType.checked"
                @change="changeResourceType(resourceType, node)"
              ></v-checkbox>
              <v-btn
                color="indigo"
                fab
                dark
                small
                outline
                @click="toggle(resourceType)"
              >
                <v-icon dark>{{ resourceType.open ? 'remove' : 'add' }}</v-icon>
              </v-btn>
              <div
                class="paragraph"
                v-show="resourceType.open"
                v-for="resource in resourceType.resources"
                :key="resource.resourceIndex"
              >
                <v-checkbox
                  :label="`GPU${ resource.resourceIndex } ${ resource.resourceName }`"
                  v-model="resource.metrics.checked"
                  @change="changeResource(resource, resourceType, node)"
                ></v-checkbox>
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
        this.loadCalendar()
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
                nodeName: node.nodeName,
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

<style>
.paragraph{
  margin-left: 30px;
  display:flex;
  flex-wrap: wrap;
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
