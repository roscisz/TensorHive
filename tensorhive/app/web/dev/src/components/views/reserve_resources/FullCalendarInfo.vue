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
            small
            outline
            round
            @click="close()"
          >
            Close
          </v-btn>
          <v-btn
            color="error"
            small
            round
            @click="cancelCard=!cancelCard; updateCard=false"
          >
            Cancel reservation
          </v-btn>
          <v-btn
            color="info"
            small
            round
            @click="updateCard=!updateCard; cancelCard=false"
          >
            Edit reservation
          </v-btn>
        </v-card-text>
        <v-card-text>
          Title: {{reservation.title}}
        </v-card-text>
        <v-textarea v-if="updateCard"
            outline
            label="Title"
            v-model="newTitle"
          ></v-textarea>
        <v-card-text>
          Description: {{reservation.description}}
        </v-card-text>
        <v-textarea v-if="updateCard"
            outline
            label="Description"
            v-model="newDescription"
          ></v-textarea>
        <v-card-text>
          Start: {{reservation.start.toString()}} End: {{reservation.end.toString()}}
        </v-card-text>
        <div v-if="updateCard">
          <date-picker
            id="reservationTime"
            v-model="newTime"
            range type="datetime"
            lang="en"
            format="YYYY-MM-DD HH:mm"
            :time-picker-options="timePickerOptions"
          ></date-picker>
        </div>
        <v-card-text>
          GPU UUID: {{reservation.resourceId}}
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
import DatePicker from 'vue2-datepicker'
export default {
  name: 'FullCalendarInfo',

  props: {
    showModal: Boolean,
    reservation: Object,
    cancel: Function,
    update: Function
  },
  computed: {
    selectedTimeChanged () {
      if (this.reservation.start instanceof Date) return [this.reservation.start, this.reservation.end]
      else return [new Date(this.reservation.start), new Date(this.reservation.end)]
    }
  },

  watch: {
    selectedTimeChanged () {
      this.newTime = this.selectedTimeChanged
    }
  },
  data () {
    return {
      cancelCard: false,
      updateCard: false,
      newTitle: '',
      newDescription: '',
      newTime: null,
      timePickerOptions: {
        start: '00:00',
        step: '00:30',
        end: '23:30'
      }
    }
  },

  components: {
    DatePicker
  },

  methods: {
    close: function () {
      this.$emit('close')
    },

    cancelReservation: function () {
      this.cancel(this.reservation)
      this.close()
    },

    updateReservation: function () {
      this.update(this.reservation, this.newTime, this.newTitle, this.newDescription)
      this.close()
    }
  }
}
</script>
