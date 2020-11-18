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
      parsedNodeNames: [],
      restrictionEvents: []
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
      var previousCheckboxes = []
      var previousLength = this.resourcesCheckboxes.length
      for (i = 0; i < previousLength; i++) {
        obj = {
          uuid: this.resourcesCheckboxes[i].uuid,
          checked: this.resourcesCheckboxes[i].checked
        }
        previousCheckboxes[i] = obj
      }
      this.resourcesCheckboxes = []
      for (i = 0; i < this.selectedResources.length; i++) {
        var previousChecked = false
        for (var j = 0; j < previousLength; j++) {
          if (this.selectedResources[i].uuid === previousCheckboxes[j].uuid) {
            previousChecked = previousCheckboxes[j].checked
          }
        }
        obj = {
          nodeName: this.selectedResources[i].nodeName,
          name: this.selectedResources[i].name,
          uuid: this.selectedResources[i].uuid,
          index: this.selectedResources[i].index,
          checked: previousChecked,
          disabled: false
        }
        this.resourcesCheckboxes[i] = obj
      }
      this.addResourcesHeader()
      this.addUserRestrictions()
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
            userId: -1
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
    },

    addUserRestrictions () {
      api
        .request('get', '/restrictions?user_id=' + this.$store.state.id + '&include_user_groups=true', this.$store.state.accessToken)
        .then(response => {
          this.createRestrictionEvents(response.data)
        })
        .catch(error => {
          this.$emit('handleError', error)
        })
    },

    createRestrictionEvents (restrictions) {
      var start = _.cloneDeep(this.calendar.fullCalendar('getView').start)
      var end = _.cloneDeep(this.calendar.fullCalendar('getView').end)
      this.restrictionEvents = []
      for (const restriction of restrictions) {
        if (!restriction.endsAt) restriction.endsAt = end
        if (restriction.schedules.length === 0) {
          this.showRestrictionResourcesEvents(restriction, start, end, restriction.startsAt, restriction.endsAt)
        } else {
          for (const schedule of restriction.schedules) {
            for (const day of schedule.scheduleDays) {
              var date = this.findDateForWeekday(start, day)
              var eventStart = date + ' ' + schedule.hourStart
              var eventEnd = date + ' ' + schedule.hourEnd

              if (moment(date).isSameOrAfter(moment(restriction.startsAt).startOf('day')) &&
              moment(date).isSameOrBefore(moment(restriction.endsAt).endOf('day')) &&
              moment(eventStart).isSameOrBefore(moment(restriction.endsAt)) &&
              moment(eventEnd).isSameOrAfter(restriction.startsAt)) {
                if (moment(eventStart).isBefore(restriction.startsAt)) eventStart = restriction.startsAt
                if (moment(eventEnd).isAfter(restriction.endsAt)) eventEnd = restriction.endsAt
                this.showRestrictionResourcesEvents(restriction, start, end, eventStart, eventEnd)
              }
            }
          }
        }
      }
    },

    showRestrictionResourcesEvents (restriction, calendarStart, calendarEnd, eventStart, eventEnd) {
      var restrictionEvent = {
        start: '',
        end: '',
        isGlobal: false,
        resourceId: '',
        groupId: 'restriction',
        rendering: 'background',
        backgroundColor: '#bdf2ae'
      }
      var resourceCount = 0
      if (restriction.isGlobal) resourceCount = 1
      else resourceCount = restriction.resources.length
      for (var j = 0; j < resourceCount; j++) {
        if (moment(calendarStart).isSameOrBefore(restriction.endsAt) &&
        moment(calendarEnd).isSameOrAfter(restriction.startsAt)) {
          restrictionEvent.start = eventStart
          restrictionEvent.end = eventEnd
          restrictionEvent.isGlobal = restriction.isGlobal
          if (!restriction.isGlobal) restrictionEvent.resourceId = restriction.resources[j].id
          this.restrictionEvents.push(restrictionEvent)
          this.calendar.fullCalendar('renderEvent', restrictionEvent)
        }
      }
    },

    findDateForWeekday (startDate, weekday) {
      var date = moment(startDate)
      while (date.format('dddd') !== weekday) {
        date = date.add(1, 'days')
      }
      return date.format('YYYY-MM-DD')
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
        if (self.selectedResources.length > 6) {
          $(element).css('color', 'rgba(0, 0, 0, 0)')
        }
        if (!event.allDay && event.groupId !== 'restriction') {
          api
            .request('get', '/users/' + event.userId, self.$store.state.accessToken)
            .then(response => {
              element.find('.fc-title').prepend((response.data.user.username).bold().big().italics() + '<br/>')
            })
            .catch(error => {
              self.$emit('handleError', error)
            })
        }
      },
      eventAfterRender: function (event, element, view) {
        if (event.groupId !== 'restriction' || (event.groupId === 'restriction' && !event.isGlobal)) {
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
          var eventWidth
          if (event.groupId !== 'restriction') eventWidth = (Math.round(eventSlotWidth - 1)).toString() + 'px'
          else eventWidth = (Math.round(eventSlotWidth) + 1).toString() + 'px'
          $(element).css('width', eventWidth)
          if (columnIndex !== 0) {
            var margin
            if (event.groupId !== 'restriction') margin = (Math.round(columnIndex * (eventSlotWidth)) - 2).toString() + 'px'
            else margin = (Math.round(columnIndex * (eventSlotWidth)) + 1).toString() + 'px'
            $(element).css('margin-left', margin)
          } else {
            if (event.allDay) {
              $(element).css('margin-left', '1px')
            } else if (event.groupId !== 'restriction') {
              $(element).css('margin-left', '-2px')
            }
          }
          if (event.allDay) {
            if (columnIndex) {
              $(element).css('margin-top', '-36px')
            }
            $(element).css('height', 17 * 2)
          }
          if (event.groupId !== 'restriction') {
            var c = self.setColor(resourceIndex, resourceNodeName)
            if (event.userId === self.$store.state.id) {
              c = '#15C02C' // user specified color: green
            }
            if (event.color !== c) {
              event.color = c
              self.calendar.fullCalendar('updateEvent', event)
            }
          }
        }
      },

      select: function (startDate, endDate) {
        if (!startDate._ambigTime) {
          for (var i = 0; i < self.selectedResources.length; i++) {
            self.resourcesCheckboxes[i].disabled = false
          }
          var events = self.calendar.fullCalendar('clientEvents')
          var id
          for (i = 0; i < events.length; i++) {
            if (!events[i].allDay && events[i].groupId !== 'restriction') {
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
