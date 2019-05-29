<template>
  <v-layout row justify-center>
    <v-dialog
      width="50vw"
      persistent
      v-model="showModal"
    >
      <v-card>
        <v-card-text>
          <v-btn
            class="float-right-button"
            flat
            icon
            color="black"
            @click="close()"
          >
            <v-icon>close</v-icon>
          </v-btn>
        </v-card-text>
        <v-card-text>
          <b>Title:</b> {{reservation.title}}
        </v-card-text>
        <v-textarea
          v-if="updateCard"
          outline
          label="Title"
          v-model="newTitle"
        ></v-textarea>
        <v-card-text>
          <b>Description:</b> {{reservation.description}}
        </v-card-text>
        <v-textarea
          v-if="updateCard"
          outline
          label="Description"
          v-model="newDescription"
        ></v-textarea>
        <v-card-text>
          <b>Average GPU utilization:</b> {{gpuUtilAvg}}
        </v-card-text>
        <v-card-text>
          <b>Average GPU memory utilization:</b> {{memUtilAvg}}
        </v-card-text>
        <v-card-text>
          <b>Start:</b> {{ prettyDate(reservation.start) }}
        </v-card-text>
        <v-card-text v-if="updateCard">
          <v-layout align-center justify-start>
            <v-menu
              v-model="startDateMenu"
              :close-on-content-click="false"
              :nudge-right="40"
              lazy
              transition="none"
              offset-y
              full-width
              min-width="290px"
            >
              <template v-slot:activator="{ on }">
                <v-text-field
                  v-model="newStartDate"
                  label="Start date"
                  prepend-icon="event"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="newStartDate"
                @input="startDateMenu = false"
              ></v-date-picker>
            </v-menu>
            <v-menu
              ref="startMenu"
              v-model="startTimeMenu"
              :close-on-content-click="false"
              :nudge-right="40"
              :return-value.sync="newStartTime"
              lazy
              transition="none"
              offset-y
              full-width
              max-width="290px"
              min-width="290px"
            >
              <template v-slot:activator="{ on }">
                <v-text-field
                  v-model="newStartTime"
                  label="Start time"
                  prepend-icon="access_time"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-time-picker
                v-if="startTimeMenu"
                v-model="newStartTime"
                full-width
                :allowed-minutes="m => m % 30 === 0"
                format="24hr"
                @click:minute="$refs.startMenu.save(newStartTime)"
              ></v-time-picker>
            </v-menu>
          </v-layout>
        </v-card-text>
        <v-card-text>
           <b>End:</b> {{ prettyDate(reservation.end) }}
        </v-card-text>
        <v-card-text v-if="updateCard">
          <v-layout align-center justify-start>
            <v-menu
              v-model="endDateMenu"
              :close-on-content-click="false"
              :nudge-right="40"
              lazy
              transition="none"
              offset-y
              full-width
              min-width="290px"
            >
              <template v-slot:activator="{ on }">
                <v-text-field
                  v-model="newEndDate"
                  label="End date"
                  prepend-icon="event"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="newEndDate"
                @input="endDateMenu = false"
              ></v-date-picker>
            </v-menu>
            <v-menu
              ref="endMenu"
              v-model="endTimeMenu"
              :close-on-content-click="false"
              :nudge-right="40"
              :return-value.sync="newEndTime"
              lazy
              transition="none"
              offset-y
              full-width
              max-width="290px"
              min-width="290px"
            >
              <template v-slot:activator="{ on }">
                <v-text-field
                  v-model="newEndTime"
                  label="End time"
                  prepend-icon="access_time"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-time-picker
                v-if="endTimeMenu"
                v-model="newEndTime"
                full-width
                :allowed-minutes="m => m % 30 === 0"
                format="24hr"
                @click:minute="$refs.endMenu.save(newEndTime)"
              ></v-time-picker>
            </v-menu>
          </v-layout>
        </v-card-text>
        <v-card-text>
          <b>GPU UUID:</b> {{reservation.resourceId}}
        </v-card-text>
        <v-card-text class="container">
          <v-btn
            class="float-right-button"
            color="error"
            small
            round
            @click="cancelCard=!cancelCard; updateCard=false"
          >
            Cancel reservation
          </v-btn>
          <v-btn
            class="float-right-button"
            color="info"
            small
            round
            @click="updateCard=!updateCard; cancelCard=false"
          >
            Edit reservation
          </v-btn>
        </v-card-text>
        <v-card-text v-if="cancelCard">
          Do you want to cancel selected reservation?
          <v-btn
            color="error"
            small
            outline
            round
            @click="cancelCard=false"
          >
            No
          </v-btn>
          <v-btn
            color="success"
            round
            @click="cancelReservation()"
          >
            Yes
          </v-btn>
        </v-card-text>
        <v-card-text v-if="updateCard">
          <v-btn
            color="error"
            small
            outline
            round
            @click="updateCard=false"
          >
            Back
          </v-btn>
          <v-btn
            color="success"
            round
            @click="updateReservation()"
          >
            Update
          </v-btn>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-layout>
</template>

<script>
import moment from 'moment'
export default {
  name: 'FullCalendarInfo',

  props: {
    showModal: Boolean,
    reservation: Object,
    cancel: Function,
    update: Function
  },
  computed: {
    gpuUtilAvg () {
      if (this.reservation.gpuUtilAvg === null) {
        return 'Reservation is not completed yet, no data'
      } else if (this.reservation.gpuUtilAvg === -1) {
        return 'This GPU does not support NVIDIA-SMI'
      } else {
        return this.reservation.gpuUtilAvg + '%'
      }
    },

    memUtilAvg () {
      if (this.reservation.memUtilAvg === null) {
        return 'Reservation is not completed yet, no data'
      } else if (this.reservation.memUtilAvg === -1) {
        return 'This GPU does not support NVIDIA-SMI'
      } else {
        return this.reservation.memUtilAvg + '%'
      }
    },
    reservationTitle () {
      return this.reservation.title
    },

    reservationDescription () {
      return this.reservation.description
    },

    reservationStart () {
      return this.reservation.start
    },

    reservationEnd () {
      return this.reservation.end
    }
  },

  watch: {
    reservationTitle () {
      this.newTitle = this.reservationTitle
    },

    reservationDescription () {
      this.newDescription = this.reservationDescription
    },

    reservationStart () {
      if (this.reservationStart !== null) {
        this.newStartDate = moment(this.reservationStart).format('YYYY-MM-DD')
        this.newStartTime = moment(this.reservationStart).format('HH:mm')
      } else {
        this.newStartDate = ''
        this.newStartTime = ''
      }
    },

    reservationEnd () {
      if (this.reservationEnd !== null) {
        this.newEndDate = moment(this.reservationEnd).format('YYYY-MM-DD')
        this.newEndTime = moment(this.reservationEnd).format('HH:mm')
      } else {
        this.newEndDate = ''
        this.newEndTime = ''
      }
    }
  },

  data () {
    return {
      cancelCard: false,
      updateCard: false,
      newTitle: '',
      newDescription: '',
      startTimeMenu: false,
      startDateMenu: false,
      endTimeMenu: false,
      endDateMenu: false,
      newStartDate: '',
      newStartTime: '',
      newEndDate: '',
      newEndTime: ''
    }
  },

  methods: {
    prettyDate (date) {
      if (date !== null) {
        return moment(date).format('dddd, MMMM Do, HH:mm')
      } else {
        return null
      }
    },

    close: function () {
      this.$emit('close')
    },

    cancelReservation: function () {
      this.cancel(this.reservation)
    },

    updateReservation: function () {
      var newTime = [moment(this.newStartDate + 'T' + this.newStartTime), moment(this.newEndDate + 'T' + this.newEndTime)]
      this.update(this.reservation, newTime, this.newTitle, this.newDescription)
    }
  }
}
</script>

<style>
.float-right-button {
  float: right;
}
.container {
  overflow: hidden;
}
</style>
