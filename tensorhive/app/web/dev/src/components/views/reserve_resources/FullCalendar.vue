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
    :number-of-resources="numberOfResources"
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
import $ from 'jquery'
require('../../../../static/fullcalendar/fullcalendar.js')

export default {
  components: {
    FullCalendarReserve,
    FullCalendarCancel
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
      numberOfResources: 6,
      errors: []
    }
  },

  methods: {
    setColor: function (resource) {
      var color = '#123456'
      var step = resource * 123456
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
    var obj
    for (var i = 0; i < this.numberOfResources; i++) {
      obj = {
        name: 'resource ' + (i + 1).toString(),
        checked: false,
        disabled: false
      }
      this.resourcesCheckboxes[i] = obj
    }
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

      events: api.request('get', '/reservations'),

      eventAfterRender: function (event, element, view) {
        var resource = event.resourceId
        if (view.type !== 'month') {
          var hoursWidth = 42
          var scrollWidth = 16
          var width = view.el[0].clientWidth
          var dayWidth = (width - scrollWidth - hoursWidth) / 7
          var eventSlotWidth = dayWidth / self.numberOfResources - 1
          var margin = (Math.floor((resource - 1) * eventSlotWidth)).toString() + 'px'
          var eventWidth = (Math.floor(eventSlotWidth)).toString() + 'px'
          $(element).css('width', eventWidth)
          $(element).css('margin-left', margin)
        }
        var c = self.setColor(resource)
        if (event.color !== c) {
          event.color = c
          self.calendar.fullCalendar('updateEvent', event)
        }
      },

      select: function (startDate, endDate) {
        for (var i = 0; i < self.numberOfResources; i++) {
          self.resourcesCheckboxes[i].checked = false
          self.resourcesCheckboxes[i].disabled = false
        }
        var events = self.calendar.fullCalendar('clientEvents')
        var id
        for (i = 0; i < events.length; i++) {
          if (events[i].end > startDate && events[i].start < endDate) {
            id = events[i].resourceId
            self.resourcesCheckboxes[id - 1].disabled = true
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
