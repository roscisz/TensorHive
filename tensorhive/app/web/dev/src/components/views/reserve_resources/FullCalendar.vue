<template>
<div>
  <full-calendar-reserve
    :show-modal="showModalReserve"
    @close="showModalReserve = false"
    :startDate="startDate"
    :endDate="endDate"
    :resources-checkboxes="resourcesCheckboxes"
    :number-of-resources="selectedResources.length"
    :add-reservation="addReservation"
  ></full-calendar-reserve>
  <full-calendar-info
    :show-modal="showModalInfo"
    @close="showModalInfo = false"
    @handleError="handleError"
    :reservation="reservation"
    :cancel="cancelReservation"
    :update="updateReservation"
    :refreshTasks="refreshTasks"
    :nodes="nodes"
  ></full-calendar-info>
</div>
</template>

<script>
import FullCalendarReserve from './FullCalendarReserve.vue'
import FullCalendarInfo from './FullCalendarInfo.vue'
import api from '../../../api'
import $ from 'jquery'
import moment from 'moment'
import _ from 'lodash'
require('../../../../static/fullcalendar/fullcalendar.js')

export default {
  components: {
    FullCalendarReserve,
    FullCalendarInfo
  },

  props: {
    nodes: Object,
    selectedResources: Array,
    updateCalendar: Boolean
  },

  watch: {
    updateCalendar () {
      this.calendar.fullCalendar('refetchEvents')
    }
  },

  data () {
    return {
      calendar: null,
      showModalReserve: false,
      showModalInfo: false,
      reservation: {
        title: '',
        description: '',
        resourceId: '',
        start: new Date(),
        end: new Date()
      },
      reservationId: -1,
      startDate: null,
      endDate: null,
      resourcesCheckboxes: [],
      refreshTasks: false,
      parsedNodeNames: []
    }
  },

  methods: {
    handleError: function (error) {
      this.$emit('handleError', error)
    },

    getEvents: function (start, end, callback) {
      var resourcesString = ''
      if (this.selectedResources.length > 0) {
        resourcesString = this.selectedResources[0].uuid
        for (var i = 1; i < this.selectedResources.length; i++) {
          resourcesString += ',' + this.selectedResources[i].uuid
        }
      }
      let self = this
      api
        .request('get', '/reservations?resources_ids=' + resourcesString + '&start=' + start.toISOString() + '&end=' + end.toISOString(), this.$store.state.accessToken)
        .then(response => {
          if (self.reservationId !== -1) {
            for (var reservation in response.data) {
              if (response.data[reservation].id === self.reservationId) {
                self.reservation = response.data[reservation]
                self.reservation.start = moment(self.reservation.start)
                self.reservation.end = moment(self.reservation.end)
              }
            }
            self.reservationId = -1
          }
          callback(response.data)
        })
        .catch(error => {
          this.$emit('handleError', error)
        })
      var obj
      this.resourcesCheckboxes = []
      for (i = 0; i < this.selectedResources.length; i++) {
        obj = {
          nodeName: this.selectedResources[i].nodeName,
          name: this.selectedResources[i].name,
          uuid: this.selectedResources[i].uuid,
          index: this.selectedResources[i].index,
          checked: false,
          disabled: false
        }
        this.resourcesCheckboxes[i] = obj
      }
      this.addResourcesHeader()
    },

    addResourcesHeader: function () {
      var dayStart = _.cloneDeep(this.calendar.fullCalendar('getView').start)
      for (var i = 0; i < 7; i++) {
        for (var j = 0; j < this.selectedResources.length; j++) {
          var tempReservation = {
            title: 'GPU' + this.selectedResources[j].index,
            description: this.selectedResources[j].nodeName,
            start: dayStart,
            allDay: true,
            resourceId: this.selectedResources[j].uuid,
            userId: this.$store.state.id
          }
          this.calendar.fullCalendar('renderEvent', tempReservation)
        }
        if (dayStart) dayStart = dayStart.add(1, 'days')
      }
    },

    parseNodeNames: function () {
      for (var nodeName in this.nodes) {
        this.parsedNodeNames.push(nodeName)
      }
    },

    setColor: function (resourceIndex, resourceNodeName) {
      var colors = [
        ['#00AA00', '#00AA55', '#28A228', '#26A65B'], // green
        ['#1E90FF', '#00A4A6', '#1F3A93', '#008080'], // blue
        ['#545454', '#708090', '#696969', '#6C7A89'] // gray
      ]
      if (this.parsedNodeNames.length === 0) {
        this.parseNodeNames()
      }
      var colorIndex
      for (var index in this.parsedNodeNames) {
        if (this.parsedNodeNames[index] === resourceNodeName) {
          colorIndex = index % colors.length
        }
      }
      var color = colors[colorIndex][(resourceIndex) % colors[colorIndex].length]
      return color
    },

    updateReservation: function (reservation, newTime, newTitle, newDescription) {
      var toUpdate = {}
      if (reservation.start.toISOString() !== newTime[0].toISOString()) {
        toUpdate['start'] = newTime[0].toISOString()
      }
      if (reservation.end.toISOString() !== newTime[1].toISOString()) {
        toUpdate['end'] = newTime[1].toISOString()
      }
      if (reservation.title !== newTitle && newTitle !== '') {
        toUpdate['title'] = newTitle
      }
      if (reservation.description !== newDescription && newDescription !== '') {
        toUpdate['description'] = newDescription
      }
      var empty = true
      for (var key in toUpdate) {
        if (toUpdate.hasOwnProperty(key)) {
          empty = false
        }
      }
      if (!empty) {
        api
          .request('put', '/reservations/' + reservation.id, this.$store.state.accessToken, toUpdate)
          .then(response => {
            this.calendar.fullCalendar('refetchEvents')
            this.showModalInfo = false
          })
          .catch(error => {
            this.$emit('handleError', error)
          })
      }
    },

    cancelReservation: function (reservation) {
      api
        .request('delete', '/reservations/' + reservation.id.toString(), this.$store.state.accessToken)
        .then(response => {
          this.calendar.fullCalendar('refetchEvents')
          this.showModalInfo = false
        })
        .catch(error => {
          this.$emit('handleError', error)
        })
    },

    addReservation: function (reservation) {
      api
        .request('post', '/reservations', this.$store.state.accessToken, reservation)
        .then(response => {
          this.calendar.fullCalendar('refetchEvents')
          this.showModalReserve = false
        })
        .catch(error => {
          this.$emit('handleError', error)
        })
    }
  },

  mounted () {
    let self = this
    this.calendar = $(self.$el)
    $(window).resize(function () {
      self.calendar.fullCalendar('rerenderEvents')
    })
    this.calendar.fullCalendar({
      allDaySlot: true,
      allDayText: '',
      height: 'auto',
      selectable: true,
      selectOverlap: true,
      slotEventOverlap: false,
      editable: false,
      nowIndicator: true,
      firstDay: 1,
      timezone: 'local',
      defaultView: 'agendaWeek',
      header: {
        left: 'prev,next, today, agendaWeek, week2',
        center: 'title',
        right: ''
      },
      views: {
        week: {
          columnHeaderFormat: 'ddd D/M',
          buttonText: 'One week jump'
        },
        week2: {
          type: 'agendaWeek',
          duration: { days: 7 },
          buttonText: 'One day jump',
          dateIncrement: { days: 1 },
          columnHeaderFormat: 'ddd D/M'
        }
      },
      events: function (start, end, timezone, callback) {
        self.getEvents(start, end, callback)
      },
      eventRender: function (event, element) {
        element.find('.fc-title').append('<br/>' + event.description)
        if (!event.allDay) {
          api
            .request('get', '/users/' + event.userId, self.$store.state.accessToken)
            .then(response => {
              element.find('.fc-title').prepend((response.data.username).bold().big().italics() + '<br/>')
            })
            .catch(error => {
              this.$emit('handleError', error)
            })
        }
      },
      eventAfterRender: function (event, element, view) {
        var columnIndex
        var resourceIndex
        var resourceNodeName
        for (var i = 0; i < self.selectedResources.length; i++) {
          if (self.selectedResources[i].uuid === event.resourceId) {
            columnIndex = i
            resourceIndex = self.selectedResources[i].index
            resourceNodeName = self.selectedResources[i].nodeName
          }
        }
        var hoursWidth = 42
        var scrollWidth = 16
        var width = view.el[0].clientWidth
        var dayWidth = (width - scrollWidth - hoursWidth) / 7
        var eventSlotWidth = dayWidth / self.selectedResources.length
        var eventWidth = (Math.round(eventSlotWidth - 1)).toString() + 'px'
        $(element).css('width', eventWidth)
        if (columnIndex !== 0) {
          var margin = (Math.round(columnIndex * (eventSlotWidth)) - 2).toString() + 'px'
          $(element).css('margin-left', margin)
        } else {
          if (event.allDay) {
            $(element).css('margin-left', '1px')
          } else {
            $(element).css('margin-left', '-2px')
          }
        }
        if (event.allDay) {
          if (columnIndex) {
            $(element).css('margin-top', '-36px')
          }
          $(element).css('height', 17 * 2)
        }
        var c = self.setColor(resourceIndex, resourceNodeName)
        if (event.color !== c) {
          event.color = c
          self.calendar.fullCalendar('updateEvent', event)
        }
      },

      select: function (startDate, endDate) {
        if (!startDate._ambigTime) {
          for (var i = 0; i < self.selectedResources.length; i++) {
            self.resourcesCheckboxes[i].checked = false
            self.resourcesCheckboxes[i].disabled = false
          }
          var events = self.calendar.fullCalendar('clientEvents')
          var id
          for (i = 0; i < events.length; i++) {
            if (!events[i].allDay) {
              if (events[i].end > startDate && events[i].start < endDate) {
                for (var j = 0; j < self.selectedResources.length; j++) {
                  if (self.selectedResources[j].uuid === events[i].resourceId) {
                    id = j
                  }
                }
                self.resourcesCheckboxes[id].disabled = true
              }
            }
          }
          self.startDate = startDate.toDate()
          self.endDate = endDate.toDate()
          setTimeout(function () {
            self.showModalReserve = true
          }, 100)
        }
      },

      eventClick: function (calEvent, jsEvent, view) {
        if (!calEvent.allDay) {
          self.reservationId = calEvent.id
          self.calendar.fullCalendar('refetchEvents')
          self.refreshTasks = !self.refreshTasks
          self.showModalInfo = true
        }
      },
      viewRender: function (view, element) {
        self.calendar.fullCalendar('refetchEvents')
      }
    })
  }
}
</script>
<style>
  @import '../../../../static/fullcalendar/fullcalendar.css';
  .fc th, .fc td {
    border-color: #222d32 !important;
  }
  .fc-event{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
  }
</style>
