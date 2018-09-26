<template>
<div>
  <full-calendar-reserve
    :show-modal="showModalReserve"
    @close="showModalReserve = false"
    :startDate="startDate"
    :endDate="endDate"
    :min-reservation-time="minReservationTime"
    :max-reservation-time="maxReservationTime"
    :resources-checkboxes="resourcesCheckboxes"
    :number-of-resources="selectedResources.length"
    :add-reservation="addReservation"
  ></full-calendar-reserve>
  <full-calendar-cancel
    :show-modal="showModalCancel"
    @close="showModalCancel = false"
    :reservation="reservation"
    :cancel="cancelReservation"
  ></full-calendar-cancel>
</div>
</template>

<script>
import FullCalendarReserve from './FullCalendarReserve.vue'
import FullCalendarCancel from './FullCalendarCancel.vue'
import api from '../../../api'
import config from '../../../config'
import $ from 'jquery'
import _ from 'lodash'
require('../../../../static/fullcalendar/fullcalendar.js')

export default {
  components: {
    FullCalendarReserve,
    FullCalendarCancel
  },

  props: {
    selectedResources: Array
  },

  watch: {
    selectedResources () {
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
        headers: { Authorization: this.$store.state.token },
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
      showModalCancel: false,
      reservation: null,
      startDate: null,
      endDate: null,
      minReservationTime: '',
      maxReservationTime: '',
      resourcesCheckboxes: [],
      errors: []
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

    cancelReservation: function (reservation) {
      api
        .request('delete', '/reservations/' + reservation.id.toString(), this.$store.state.token)
        .then(response => {
          this.calendar.fullCalendar('removeEvents', reservation._id)
        })
        .catch(e => {
          this.errors.push(e)
        })
    },

    addReservation: function (reservation) {
      api
        .request('post', '/reservations', this.$store.state.token, reservation)
        .then(response => {
          this.calendar.fullCalendar('refetchEvents')
        })
        .catch(e => {
          this.errors.push(e)
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
        right: ''
      },
      views: {
        week: {
          columnHeaderFormat: 'ddd D/M'
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
        var margin = (Math.floor((resourceIndex - 1) * eventSlotWidth)).toString() + 'px'
        var eventWidth = (Math.floor(eventSlotWidth)).toString() + 'px'
        $(element).css('width', eventWidth)
        $(element).css('margin-left', margin)
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
          self.minReservationTime = startDate.format()
          self.maxReservationTime = endDate.format()
          self.showModalReserve = true
        }
      },

      eventClick: function (calEvent, jsEvent, view) {
        if (calEvent.userId === self.$store.state.id && !calEvent.allDay) {
          self.showModalCancel = true
          self.reservation = calEvent
        }
      },
      viewRender: function (view, element) {
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
