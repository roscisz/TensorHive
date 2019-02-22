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
    <div class="container" :key="tableKey">
      <div class="left-table">
        <table>
          <tbody>
            <th class="first-column">Resources</th>
          </tbody>
        </table>
        <table>
          <tbody>
            <tr>
              <td class="first-column">Hours</td>
            </tr>
          </tbody>
        </table>
        <table>
          <tbody>
            <tr v-for="resource in tableContent.resources" :key="resource.id">
              <td class="first-column" :class="{selected: resource.selected}">
                <v-btn
                  class="small-button"
                  v-if="!resource.selected"
                  fab
                  dark
                  small
                  color="blue"
                  @click="toggle(resource)"
                >
                  <v-icon dark>add</v-icon>
                </v-btn>
                <v-btn
                  class="small-button"
                  v-if="resource.selected"
                  fab
                  dark
                  small
                  color="blue"
                  @click="toggle(resource)"
                >
                  <v-icon dark>remove</v-icon>
                </v-btn>
                {{resource.name}}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="right-table">
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
        <table>
          <tbody>
            <tr v-for="resource in tableContent.resources" :key="resource.id">
              <td v-for="slots in resource.slots" :key="slots.id" :class="{ 'reserved': slots.reserved, 'userReservation': slots.userReservation }">{{slots.value}}</td>
            </tr>
          </tbody>
        </table>
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
        resources: {},
        header: [],
        hours: [],
        tableKey: 0
      },
      scheduleStart: '',
      scheduleEnd: '',
      resourcesIds: [],
      startMoment: {},
      tableKey: 0,
      picker: new Date().toISOString().substr(0, 10),
      menu: false,
      landscape: false,
      reactive: false,
      range: 7
    }
  },

  props: {
    parsedNodes: Array
  },

  watch: {
    parsedNodes () {
      this.fillTable()
    }
  },

  methods: {
    loadResources: function () {
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

    toggle: function (resource) {
      resource.selected = !resource.selected
      this.loadResources()
      this.forceRerenderTable()
    },

    fillTable: function () {
      this.resourceIds = []
      this.tableContent.resources = {}
      for (var nodeIndex in this.parsedNodes) {
        var node = this.parsedNodes[nodeIndex]
        for (var resourceTypeIndex in node.resourceTypes) {
          var resourceType = node.resourceTypes[resourceTypeIndex]
          for (var resourceIndex in resourceType.resources) {
            var resource = resourceType.resources[resourceIndex]
            resource.name = resource.nodeName + ' GPU' + resourceIndex
            resource['selected'] = false
            this.resourcesIds.push(resource.resourceUUID)
            var slots = []
            for (var i = 0; i < 48 * this.range; i++) {
              slots.push({ value: '', id: 'slot ' + i, reserved: false, userReservation: false })
            }
            resource['slots'] = slots
            this.tableContent.resources[resource.resourceUUID] = resource
          }
        }
      }
      this.getReservations()
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
          this.parseData(response.data)
        })
        .catch(error => {
          if (!error.hasOwnProperty('response')) {
            this.$emit('showSnackbar', error.message)
          } else {
            this.$emit('showSnackbar', error.response.data.msg)
          }
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
        this.forceRerenderTable()
      }
    },

    forceRerenderTable: function () {
      this.tableKey += 1
    },

    adjustTimezone: function () {
      var d = new Date()
      var v = d.getTimezoneOffset() // in minutes for example GMT+1 = -60
      return v / 60
    }
  },

  mounted () {
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
      resources: {},
      header: header,
      hours: hours
    }
  }
}
</script>
<style scoped>
.container {
  width: 85vw;
  margin-left: 0;
  white-space: nowrap;
  display: inline-block;
  position:relative;
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
.selected {
  background-color: #42b983;
}
.small-button {
  height: 25px;
}
.left-table {
  min-width: 205px;
  overflow-x: scroll;
  display: inline-block;
}
.right-table {
  width: 70vw;
  overflow-x: scroll;
  display: inline-block;
}
.first-column {
  min-width: 200px;
  white-space: nowrap;
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
  border: 0px solid grey;
  border-radius: 3px;
  border-collapse: collapse;
  border-spacing: 0;
}
th {
  background: #fafafa;
  border: 1px solid grey;
  min-width: 960px;
  height: 40px;
  max-height: 40px;
  text-align: center;
  display: table-cell;
}
td {
  background: transparent;
  border: 1px solid grey;
  min-width: 20px;
  height: 40px;
  max-height: 40px;
  text-align: center;
  display: table-cell;
}
</style>
