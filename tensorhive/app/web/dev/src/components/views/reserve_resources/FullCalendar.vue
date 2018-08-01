<template>
<div>
  <div></div>
  <button @click="showModalReservation = true">Reserve</button>
  <full-calendar-reservation
    :show-modal="showModal"
    @close="showModal = false"
    :min-reservation-time="minReservationTime"
    :max-reservation-time="maxReservationTime"
    :nodes-checkboxes="nodesCheckboxes"
    :number-of-nodes="numberOfNodes"
    :add-event="addEvent"
  ></full-calendar-reservation>
</div>
</template>

<script>
import FullCalendarReservation from './FullCalendarReservation.vue'
import api from '../../../api'
import $ from 'jquery'
require('../../../../static/fullcalendar/fullcalendar.js')

export default {
  components: {
    FullCalendarReservation
  },

  data () {
    return {
      calendar: null,
      showModal: false,
      minReservationTime: '',
      maxReservationTime: '',
      nodesCheckboxes: [],
      numberOfNodes: 6,
      errors: []
    }
  },

  methods: {
    setColor: function (node) {
      var color = '#123456'
      var step = node * 123456
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

    deleteEvent: function (event) {
      api
        .request('delete', '/reservations/' + event.id.toString())
        .then(response => {
          this.calendar.fullCalendar('removeEvents', event._id)
        })
    },

    addEvent: function (event) {
      api
        .request('post', '/reservations', event)
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
    for (var i = 0; i < this.numberOfNodes; i++) {
      obj = {
        name: 'Node ' + (i + 1).toString(),
        checked: false,
        disabled: false
      }
      this.nodesCheckboxes[i] = obj
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
      defaultView: 'agendaWeek',
      header: {
        left: 'prev,next today',
        center: 'title',
        right: 'agendaWeek,agendaDay,month'
      },

      events: api.request('get', '/reservations'),

      eventAfterRender: function (event, element, view) {
        var node = event.nodeId
        if (view.type !== 'month') {
          var hoursWidth = 42
          var scrollWidth = 16
          var width = view.el[0].clientWidth
          var dayWidth = (width - scrollWidth - hoursWidth) / 7
          var eventSlotWidth = dayWidth / self.numberOfNodes - 1
          var margin = (Math.floor((node - 1) * eventSlotWidth)).toString() + 'px'
          var eventWidth = (Math.floor(eventSlotWidth)).toString() + 'px'
          $(element).css('width', eventWidth)
          $(element).css('margin-left', margin)
        }
        var c = self.setColor(node)
        if (event.color !== c) {
          event.color = c
          self.calendar.fullCalendar('updateEvent', event)
        }
      },

      select: function (startDate, endDate) {
        for (var i = 0; i < self.numberOfNodes; i++) {
          self.nodesCheckboxes[i].checked = false
          self.nodesCheckboxes[i].disabled = false
        }
        var events = self.calendar.fullCalendar('clientEvents')
        var id
        for (i = 0; i < events.length; i++) {
          if (events[i].end > startDate && events[i].start < endDate) {
            id = events[i].nodeId
            self.nodesCheckboxes[id - 1].disabled = true
          }
        }
        self.minReservationTime = startDate.format()
        self.maxReservationTime = endDate.format()
        self.showModal = true
      },

      eventClick: function (calEvent, jsEvent, view) {
        self.deleteEvent(calEvent)
      }
    })
  }
}
</script>
<style>
  @import '../../../../static/fullcalendar/fullcalendar.css';
</style>
