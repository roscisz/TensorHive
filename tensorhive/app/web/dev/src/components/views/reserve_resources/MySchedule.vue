<template>
  <div>
    <div class="range-select-container">
      <v-menu
        :close-on-content-click="false"
        v-model="menu"
        :nudge-right="40"
        lazy
        transition="scale-transition"
        offset-y
        full-width
        min-width="290px"
      >
        <v-text-field
          class="date-input"
          slot="activator"
          v-model="picker"
          label="Schedule start date"
          prepend-icon="event"
          readonly
        ></v-text-field>
        <v-date-picker v-model="picker" @input="menu = false; changeSchedule()"></v-date-picker>
      </v-menu>
      <v-text-field
        class="range-input"
        v-model="range"
        min="1"
        step="1"
        type="number"
        label="Schedule range in days"
        @input="changeSchedule()"
      ></v-text-field>
    </div>
    <div class="container">
      <div class="container-header">
        <div class="left-table-header">
          <table>
            <tbody>
              <th class="first-column">Resources</th>
            </tbody>
          </table>
          <table>
            <tbody>
              <tr>
                <td class="first-column">
                  <v-checkbox
                    class="small-checkbox"
                    color="success"
                    label="Select all"
                    v-model="changeAllCheckbox"
                    @change="changeAll"
                  >
                  </v-checkbox>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="right-table-header" id="right-header">
          <table>
            <tbody>
              <th v-for="header in tableContent.header" :key="header.value">{{header.value}}</th>
            </tbody>
          </table>
          <table>
            <tbody>
              <tr>
                <td class="hours" v-for="hours in tableContent.hours" :key="hours.id">{{hours.value}}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="container-content">
        <div class="left-table" id="left-table">
          <div :key="leftTableKey">
            <table v-for="node in tableContent.nodes" :key="node.nodeName">
              <tbody>
                <tr>
                  <td class="first-column">
                    <div class="node-cell">
                      <v-checkbox
                        class="small-checkbox-node"
                        color="success"
                        :label="`${ node.nodeName }`"
                        v-model="node.selected"
                        input-value
                        @change="changeWholeNode(node.nodeName)"
                      >
                      </v-checkbox>
                      <v-btn class="mx-2 small-button" fab dark color="info" @click="toggle(node)">
                        <v-icon v-if="node.hidden" dark>add</v-icon>
                        <v-icon v-if="!node.hidden" dark>remove</v-icon>
                      </v-btn>
                    </div>
                  </td>
                </tr>
              </tbody>
              <tbody v-show="!node.hidden">
                <tr v-for="resourceUUID in node.resources" :key="resourceUUID">
                  <td class="first-column">
                    <v-checkbox
                      class="small-checkbox"
                      color="success"
                      :label="`${ tableContent.resources[resourceUUID].name }`"
                      v-model="tableContent.resources[resourceUUID].selected"
                      @change="changeResource(node.nodeName, resourceUUID)"
                    >
                    </v-checkbox>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="right-table" id="right-table">
          <div :key="rightTableKey">
            <table v-for="node in tableContent.nodes" :key="node.nodeName">
              <tbody>
                <tr>
                  <td v-for="slot in node.slots" :key="slot.id">{{slot.value}}</td>
                </tr>
              </tbody>
              <tbody v-show="!node.hidden">
                <tr v-for="resourceUUID in node.resources" :key="resourceUUID">
                  <td v-for="slot in tableContent.resources[resourceUUID].slots" :key="slot.id" :class="{ 'reserved': slot.reserved, 'userReservation': slot.userReservation }">{{slot.value}}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import moment from 'moment'
import api from '../../../api'
export default {

  data () {
    return {
      tableContent: {
        nodes: {},
        resources: {},
        header: [],
        hours: []
      },
      scheduleStart: '',
      scheduleEnd: '',
      resourcesIds: [],
      startMoment: {},
      leftTableKey: 0,
      rightTableKey: 0,
      picker: new Date().toISOString().substr(0, 10),
      menu: false,
      landscape: false,
      reactive: false,
      range: 7,
      changeAllCheckbox: true,
      allFlag: false,
      nodeFlag: false
    }
  },

  props: {
    parsedNodes: Array
  },

  watch: {
    parsedNodes () {
      this.fillTable()
      for (var nodeIndex in this.parsedNodes) {
        var nodeName = this.parsedNodes[nodeIndex].nodeName
        this.checkIfAllResourcesSelected(nodeName)
      }
      this.checkIfAllNodesSelected()
      this.loadResources()
    }
  },

  methods: {
    changeAll: function () {
      this.allFlag = true
      for (var nodeName in this.tableContent.nodes) {
        this.tableContent.nodes[nodeName].selected = this.changeAllCheckbox
        this.changeWholeNode(nodeName)
      }
      this.allFlag = false
      this.loadResources()
    },

    changeWholeNode: function (nodeName) {
      this.nodeFlag = true
      for (var resourceId in this.tableContent.nodes[nodeName].resources) {
        var resourceUUID = this.tableContent.nodes[nodeName].resources[resourceId]
        var resource = this.tableContent.resources[resourceUUID]
        resource.selected = this.tableContent.nodes[nodeName].selected
        if (this.tableContent.nodes[nodeName].selected) {
          this.selectedResources[nodeName].add(resource.resourceUUID)
        } else {
          this.selectedResources[nodeName].delete(resource.resourceUUID)
        }
      }
      if (!this.allFlag) {
        if (this.tableContent.nodes[nodeName].selected) {
          this.selectedNodes.add(nodeName)
        } else {
          this.selectedNodes.delete(nodeName)
        }
        this.checkIfAllNodesSelected()
        this.loadResources()
      }
      this.nodeFlag = false
    },

    checkIfAllNodesSelected: function () {
      if (this.selectedNodes.size === Object.keys(this.tableContent.nodes).length) {
        this.changeAllCheckbox = true
      } else {
        this.changeAllCheckbox = false
      }
    },

    changeResource: function (nodeName, resourceUUID) {
      if (this.allFlag || this.nodeFlag) {
        return
      }

      if (this.tableContent.resources[resourceUUID].selected) {
        this.selectedResources[nodeName].add(resourceUUID)
      } else {
        this.selectedResources[nodeName].delete(resourceUUID)
      }

      this.checkIfAllResourcesSelected(nodeName)
      this.checkIfAllNodesSelected()
      this.forceRerenderTables()
      this.loadResources()
    },

    checkIfAllResourcesSelected: function (nodeName) {
      if (this.selectedResources[nodeName].size === Object.keys(this.tableContent.nodes[nodeName].resources).length) {
        this.tableContent.nodes[nodeName].selected = true
        this.selectedNodes.add(nodeName)
      } else {
        this.tableContent.nodes[nodeName].selected = false
        this.selectedNodes.delete(nodeName)
      }
    },

    loadOrInitSelected: function () {
      this.selectedNodes = Set.from(JSON.parse(window.localStorage.getItem('selectedNodes')))
      this.selectedResources = JSON.parse(window.localStorage.getItem('selectedResources'))

      if (this.selectedNodes === null || this.selectedResources === null) {
        this.selectedNodes = new Set()
        this.selectedResources = {}
        for (var nodeIndex in this.parsedNodes) {
          var node = this.parsedNodes[nodeIndex]
          var nodeName = node.nodeName
          this.selectedNodes.add(nodeName)

          this.selectedResources[nodeName] = new Set()
          for (var resourceTypeIndex in node.resourceTypes) {
            var resourceType = node.resourceTypes[resourceTypeIndex]
            for (var resourceIndex in resourceType.resources) {
              var resourceUUID = resourceType.resources[resourceIndex].resourceUUID
              this.selectedResources[nodeName].add(resourceUUID)
            }
          }
        }
      }
      for (var entry in this.selectedResources) {
        this.selectedResources[entry] = Set.from(this.selectedResources[entry])
      }
    },

    storeSelected: function () {
      window.localStorage.setItem('selectedNodes', JSON.stringify(this.selectedNodes))
      window.localStorage.setItem('selectedResources', JSON.stringify(this.selectedResources))
    },

    loadResources: function () {
      this.storeSelected()
      this.$emit('loadResources', this.tableContent.resources)
    },

    changeSchedule: function () {
      var start = moment(this.picker + 'T00:00:00.000Z').add(this.adjustTimezone(), 'hours')
      this.startMoment = start
      this.scheduleStart = start.toISOString()
      this.scheduleEnd = moment(start).add(this.range, 'days').toISOString()
      var header = []
      header.push({value: start.format('dddd, MMMM Do YYYY'), id: 1})
      for (var i = 1; i < this.range; i++) {
        header.push({value: moment(start).add(i, 'days').format('dddd, MMMM Do YYYY'), id: i + 1})
      }
      var hours = []
      for (var headerName in header) {
        for (i = 0; i < 24; i++) {
          hours.push({value: i + ':00', id: headerName + ' hour ' + i})
        }
      }
      this.tableContent.header = header
      this.tableContent.hours = hours
      this.fillTable()
    },

    fillTable: function () {
      this.resourceIds = []
      this.tableContent.nodes = {}
      this.tableContent.resources = {}

      for (var nodeIndex in this.parsedNodes) {
        var node = this.parsedNodes[nodeIndex]
        var nodeName = node.nodeName
        var nodeSlots = []
        for (var i = 0; i < 48 * this.range; i++) {
          nodeSlots.push({ value: '', id: 'slot ' + i, reserved: false, userReservation: false })
        }
        this.tableContent.nodes[nodeName] = {
          nodeName: nodeName,
          hidden: true,
          resources: [],
          selected: this.selectedNodes.has(nodeName),
          slots: nodeSlots
        }

        for (var resourceTypeIndex in node.resourceTypes) {
          var resourceType = node.resourceTypes[resourceTypeIndex]
          for (var resourceIndex in resourceType.resources) {
            var resource = resourceType.resources[resourceIndex]
            resource.name = resource.nodeName + ' ' + resourceType.name + resourceIndex
            if (resource.nodeName in this.selectedResources) {
              resource['selected'] = this.selectedResources[resource.nodeName].has(resource.resourceUUID)
            } else {
              resource['selected'] = 'false'
            }
            this.resourcesIds.push(resource.resourceUUID)
            var slots = []
            for (i = 0; i < 48 * this.range; i++) {
              slots.push({ value: '', id: 'slot ' + i, reserved: false, userReservation: false })
            }
            resource['slots'] = slots
            this.tableContent.nodes[nodeName].resources.push(resource.resourceUUID)
            this.tableContent.resources[resource.resourceUUID] = resource
          }
        }
        this.selectedNodes.add(nodeName)
      }
    },

    getReservations: function () {
      var resourcesString = ''
      for (var i in this.resourcesIds) {
        resourcesString += this.resourcesIds[i] + ','
      }
      resourcesString = resourcesString.slice(0, -1)
      api
        .request('get', '/reservations?resources_ids=' + resourcesString + '&start=' + this.scheduleStart + '&end=' + this.scheduleEnd, this.$store.state.accessToken)
        .then(response => {
          if (response.data.length !== 0) {
            this.parseData(response.data)
          }
        })
        .catch(error => {
          this.$emit('handleError', error)
        })
    },

    parseData: function (data) {
      for (var i in data) {
        var start = moment(data[i].start)
        var dayDifferenceStart = this.startMoment.diff(start, 'days')
        var hoursDifferenceStart = this.startMoment.diff(start, 'hours') % 24
        var minutesDifferenceStart = this.startMoment.diff(start, 'minutes') % 60
        if (minutesDifferenceStart !== 0) minutesDifferenceStart = 1
        var end = moment(data[i].end)
        var dayDifferenceEnd = this.startMoment.diff(end, 'days')
        var hoursDifferenceEnd = this.startMoment.diff(end, 'hours') % 24
        var minutesDifferenceEnd = this.startMoment.diff(end, 'minutes') % 60
        if (minutesDifferenceEnd !== 0) minutesDifferenceEnd = 1
        var startSlot = -dayDifferenceStart * 48 - hoursDifferenceStart * 2 + minutesDifferenceStart
        var endSlot = -dayDifferenceEnd * 48 - hoursDifferenceEnd * 2 + minutesDifferenceEnd
        if (startSlot < 0) startSlot = 0
        if (endSlot > 48 * this.range) endSlot = 48 * this.range
        for (var slot = startSlot; slot < endSlot; slot++) {
          if (parseInt(this.$store.state.id) === parseInt(data[i].userId)) {
            this.tableContent.resources[data[i].resourceId].slots[slot].userReservation = true
          } else {
            this.tableContent.resources[data[i].resourceId].slots[slot].reserved = true
          }
        }
        this.forceRerenderTables()
      }
    },

    forceRerenderTables: function (key) {
      this.leftTableKey = !this.leftTableKey
      this.rightTableKey = !this.rightTableKey
    },

    adjustTimezone: function () {
      var d = new Date()
      var v = d.getTimezoneOffset() // in minutes for example GMT+1 = -60
      return v / 60
    },

    toggle (node) {
      this.tableContent.nodes[node.nodeName].hidden = !this.tableContent.nodes[node.nodeName].hidden
      this.forceRerenderTables()
    }
  },

  mounted () {
    // synchronise scrolls
    var leftTable = document.getElementById('left-table')
    var rightTable = document.getElementById('right-table')
    var rightHeader = document.getElementById('right-header')
    rightTable.onscroll = function () {
      leftTable.scrollTop = this.scrollTop
      rightHeader.scrollLeft = this.scrollLeft
    }

    var start = moment(new Date().toISOString()).add(this.adjustTimezone(), 'hours')
    this.startMoment = start
    this.scheduleStart = start.toISOString()
    this.scheduleEnd = moment(start).add(7, 'days').toISOString()
    var header = [
      {value: start.format('dddd, MMMM Do YYYY'), id: 1},
      {value: moment(start).add(1, 'days').format('dddd, MMMM Do YYYY'), id: 2},
      {value: moment(start).add(2, 'days').format('dddd, MMMM Do YYYY'), id: 3},
      {value: moment(start).add(3, 'days').format('dddd, MMMM Do YYYY'), id: 4},
      {value: moment(start).add(4, 'days').format('dddd, MMMM Do YYYY'), id: 5},
      {value: moment(start).add(5, 'days').format('dddd, MMMM Do YYYY'), id: 6},
      {value: moment(start).add(6, 'days').format('dddd, MMMM Do YYYY'), id: 7}
    ]
    var hours = []
    for (var headerName in header) {
      for (var i = 0; i < 24; i++) {
        hours.push({value: i + ':00', id: headerName + ' hour ' + i})
      }
    }
    this.tableContent = {
      nodes: {},
      resources: [],
      header: header,
      hours: hours
    }
    this.loadOrInitSelected()
  }
}
</script>
<style scoped>
.container {
  width: 100%;
  max-width: 100%;
}
.container-header {
  width: 100%;
  max-width: 100%;
  margin-left: 0;
  white-space: nowrap;
  display: inline-block;
  position:relative;
}
.container-content {
  width: 100%;
  max-width: 100%;
  margin-left: 0;
  white-space: nowrap;
  display: inline-block;
  position: relative;
}
.range-select-container {
  display:flex;
  flex-wrap: wrap;
}
.date-input {
  max-width: 150px;
}
.range-input {
  max-width: 150px;
}
.small-button {
  height: 25px !important;
  width: 25px !important;
}
.small-checkbox-node {
  margin-top: 0px !important;
  margin-left: 10px !important;
  height: 15px !important;
  width: 15px !important;
}
.small-checkbox {
  margin-top: -15px !important;
  margin-left: 10px !important;
  height: 15px !important;
  width: 15px !important;
}
.left-table {
  min-width: 205px;
  overflow-x: scroll;
  overflow-y: hidden;
  display: inline-block;
  max-height: calc(50vh - 88px);
}
.left-table-header {
  min-width: 205px;
  overflow-x: hidden;
  overflow-y: hidden;
  display: inline-block;
}
.right-table {
  width: calc(100% - 205px);
  overflow-x: scroll;
  overflow-y: scroll;
  display: inline-block;
  max-height: calc(50vh - 88px);
}
.right-table-header {
  width: calc(100% - 205px);
  overflow-x: hidden;
  overflow-y: scroll;
  display: inline-block;
}
.first-column {
  min-width: 200px;
  white-space: nowrap
}
.node-cell {
  display: flex;
}
.hours {
  min-width: 40px;
}
.reserved {
  background: #c64141;
}
.userReservation {
  background: #41c641;
}
table {
  border: 0px solid #222d32;
  border-radius: 3px;
  border-collapse: collapse;
  border-spacing: 0;
}
th {
  background: #fafafa;
  border: 1px solid #222d32;
  min-width: 960px;
  height: 40px;
  max-height: 40px;
  text-align: center;
  display: table-cell;
}
td {
  background: transparent;
  border: 1px solid #222d32;
  min-width: 20px;
  height: 40px;
  max-height: 40px;
  text-align: center;
  display: table-cell;
}
</style>
