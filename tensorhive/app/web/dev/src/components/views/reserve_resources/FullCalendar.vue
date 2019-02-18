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
    :reservation="reservation"
    :cancel="cancelReservation"
    :update="updateReservation"
  ></full-calendar-info>
</div>
</template>

<script>
import FullCalendarReserve from './FullCalendarReserve.vue'
import FullCalendarInfo from './FullCalendarInfo.vue'
import api from '../../../api'
import config from '../../../config'
import $ from 'jquery'
import _ from 'lodash'
require('../../../../static/fullcalendar/fullcalendar.js')

export default {
  components: {
    FullCalendarReserve,
    FullCalendarInfo
  },

  props: {
    selectedResources: Array,
    updateCalendar: Boolean
  },

  watch: {
    updateCalendar () {
      var resourcesString = ''
      if (this.selectedResources.length > 0) {
        resourcesString = this.selectedResources[0].uuid
        for (var i = 1; i < this.selectedResources.length; i++) {
          resourcesString += ',' + this.selectedResources[i].uuid
        }
      }
      this.calendar.fullCalendar('removeEventSources')
      this.calendar.fullCalendar('addEventSource', {
        url: config.serverURI + '/reservations?resources_ids=' + resourcesString,
        headers: { Authorization: this.$store.state.accessToken },
        cache: true
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
      startDate: null,
      endDate: null,
      resourcesCheckboxes: []
    }
  },

  methods: {
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
        dayStart = dayStart.add(1, 'days')
      }
    },

    setColor: function (resourceIndex) {
      var color = '#123456'
      var step = resourceIndex * 123456
      var colorToInt = parseInt(color.substr(1), 16)
      var nstep = parseInt(step)
      if (!isNaN(colorToInt) && !isNaN(nstep)) {
        colorToInt += nstep
        var ncolor = colorToInt.toString(16)
        ncolor = '#' + (new Array(7 - ncolor.length).join(0)) + ncolor
        if (/^#[0-9a-f]{6}$/i.test(ncolor)) {
          return ncolor
        }
      }
      return color
    },

    updateReservation: function (reservation, newTime, newTitle, newDescription) {
      var toUpdate = {
        id: reservation.id
      }
      if (reservation.start.toISOString() !== newTime[0].toISOString()) {
        toUpdate['start'] = newTime[0].toISOString()
      }
      if (reservation.end.toISOString() !== newTime[1].toISOString()) {
        toUpdate['end'] = newTime[1].toISOString()
      }
      if (reservation.title !== newTitle) {
        toUpdate['title'] = newTitle
      }
      if (reservation.description !== newDescription) {
        toUpdate['description'] = newDescription
      }
      api
        .request('put', '/reservations', this.$store.state.accessToken, toUpdate)
        .then(response => {
          this.calendar.fullCalendar('refetchEvents')
          this.addResourcesHeader()
        })
        .catch(error => {
          if (!error.hasOwnProperty('response')) {
            this.$emit('showSnackbar', error.message)
          } else {
            this.$emit('showSnackbar', error.response.data.msg)
          }
        })
    },

    cancelReservation: function (reservation) {
      api
        .request('delete', '/reservations/' + reservation.id.toString(), this.$store.state.accessToken)
        .then(response => {
          this.calendar.fullCalendar('removeEvents', reservation._id)
        })
        .catch(error => {
          if (!error.hasOwnProperty('response')) {
            this.$emit('showSnackbar', error.message)
          } else {
            this.$emit('showSnackbar', error.response.data.msg)
          }
        })
    },

    addReservation: function (reservation) {
      api
        .request('post', '/reservations', this.$store.state.accessToken, reservation)
        .then(response => {
          this.calendar.fullCalendar('refetchEvents')
          this.addResourcesHeader()
        })
        .catch(error => {
          if (!error.hasOwnProperty('response')) {
            this.$emit('showSnackbar', error.message)
          } else {
            this.$emit('showSnackbar', error.response.data.msg)
          }
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
        left: 'prev,next today',
        center: 'title',
        right: 'agendaWeek, week2'
      },
      views: {
        week: {
          columnHeaderFormat: 'ddd D/M'
        },
        week2: {
          type: 'agendaWeek',
          duration: { days: 7 },
          buttonText: '+-1 day',
          dateIncrement: { days: 1 },
          columnHeaderFormat: 'ddd D/M'
        }
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
              if (!error.hasOwnProperty('response')) {
                this.$emit('showSnackbar', error.message)
              } else {
                this.$emit('showSnackbar', error.response.data.msg)
              }
            })
        }
      },
      eventAfterRender: function (event, element, view) {
        var resourceIndex
        for (var i = 0; i < self.selectedResources.length; i++) {
          if (self.selectedResources[i].uuid === event.resourceId) {
            resourceIndex = i + 1
          }
        }
        var hoursWidth = 42
        var scrollWidth = 16
        var width = view.el[0].clientWidth
        var dayWidth = (width - scrollWidth - hoursWidth) / 7
        var eventSlotWidth = dayWidth / self.selectedResources.length - 1
        var eventWidth = (Math.floor(eventSlotWidth - 1)).toString() + 'px'
        $(element).css('width', eventWidth)
        if (resourceIndex !== 1) {
          var margin = (Math.floor((resourceIndex - 1) * eventSlotWidth) + 1).toString() + 'px'
          $(element).css('margin-left', margin)
        }
        if (event.allDay) {
          if (resourceIndex - 1) {
            $(element).css('margin-top', '-36px')
          }
          $(element).css('height', 17 * 2)
        }
        var c = self.setColor(resourceIndex)
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
          self.showModalReserve = true
        }
      },

      eventClick: function (calEvent, jsEvent, view) {
        if ((calEvent.userId === self.$store.state.id || self.$store.state.role === 'admin') && !calEvent.allDay) {
          self.showModalInfo = true
          self.reservation = calEvent
        }
      },
      viewRender: function (view, element) {
        self.calendar.fullCalendar('refetchEvents')
        self.addResourcesHeader()
      }
    })
  }
}
</script>
<style>
  @import '../../../../static/fullcalendar/fullcalendar.css';
  .fc-event{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
  }
</style>
