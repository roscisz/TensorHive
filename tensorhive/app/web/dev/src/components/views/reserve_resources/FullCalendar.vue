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
        cache: true
      })
      var obj
      this.resourcesCheckboxes = []
      for (i = 0; i < this.selectedResources.length; i++) {
        obj = {
          name: this.selectedResources[i].name,
          uuid: this.selectedResources[i].uuid,
          checked: false,
          disabled: false
        }
        this.resourcesCheckboxes[i] = obj
      }
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
        .request('delete', '/reservations/' + reservation.id.toString())
        .then(response => {
          this.calendar.fullCalendar('removeEvents', reservation._id)
        })
        .catch(e => {
          this.errors.push(e)
        })
    },

    addReservation: function (reservation) {
      api
        .request('post', '/reservations', reservation)
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
      allDaySlot: false,
      height: 800,
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
        right: 'agendaWeek,agendaDay,month'
      },

      eventAfterRender: function (event, element, view) {
        var resourceIndex
        for (var i = 0; i < self.selectedResources.length; i++) {
          if (self.selectedResources[i].uuid === event.resourceId) {
            resourceIndex = i + 1
          }
        }
        if (view.type !== 'month') {
          var hoursWidth = 42
          var scrollWidth = 16
          var width = view.el[0].clientWidth
          var dayWidth = (width - scrollWidth - hoursWidth) / 7
          var eventSlotWidth = dayWidth / self.selectedResources.length - 1
          var margin = (Math.floor((resourceIndex - 1) * eventSlotWidth)).toString() + 'px'
          var eventWidth = (Math.floor(eventSlotWidth)).toString() + 'px'
          $(element).css('width', eventWidth)
          $(element).css('margin-left', margin)
        }
        var c = self.setColor(resourceIndex)
        if (event.color !== c) {
          event.color = c
          self.calendar.fullCalendar('updateEvent', event)
        }
      },

      select: function (startDate, endDate) {
        for (var i = 0; i < self.selectedResources.length; i++) {
          self.resourcesCheckboxes[i].checked = false
          self.resourcesCheckboxes[i].disabled = false
        }
        var events = self.calendar.fullCalendar('clientEvents')
        var id
        for (i = 0; i < events.length; i++) {
          if (events[i].end > startDate && events[i].start < endDate) {
            for (var j = 0; j < self.selectedResources.length; j++) {
              if (self.selectedResources[j].uuid === events[i].resourceId) {
                id = j
              }
            }
            self.resourcesCheckboxes[id].disabled = true
          }
        }
        self.startDate = startDate.toDate()
        self.endDate = endDate.toDate()
        self.minReservationTime = startDate.format()
        self.maxReservationTime = endDate.format()
        self.showModalReserve = true
      },

      eventClick: function (calEvent, jsEvent, view) {
        self.showModalCancel = true
        self.reservation = calEvent
      }
    })
  }
}
</script>
<style>
  @import '../../../../static/fullcalendar/fullcalendar.css';
</style>
