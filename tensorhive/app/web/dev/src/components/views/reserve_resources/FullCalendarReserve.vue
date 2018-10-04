<template>
  <v-layout row justify-center>
    <v-dialog
      persistent
      width="50vw"
      v-model="showModal"
    >
      <v-card>
        <v-card-title>
          <span class="headline">Which resources do you want to reserve?</span>
        </v-card-title>
        <v-card-text>
          <div
            class="row"
            v-for="checkbox in resourcesCheckboxes"
            :key="checkbox.uuid"
          >
            <v-checkbox
              :label="`${checkbox.nodeName} GPU${ checkbox.index } ${ checkbox.name }`"
              v-model="checkbox.checked"
              :disabled="checkbox.disabled"
            >
            </v-checkbox>
          </div>
          <label class="form-label">
            Start and end time
            <date-picker
              id="reservationTime"
              v-model="reservationTime"
              range type="datetime"
              lang="en"
              format="YYYY-MM-DD HH:mm"
              :not-before="minReservationTime"
              :not-after="maxReservationTime"
              :time-picker-options="timePickerOptions"
            ></date-picker>
          </label>
          <div v-show="showInfo===true" class="text-red"><p class="vertical-5p lead">You need to choose at least one resource to reserve</p></div>
          <div class="modal-footer text-right">
            <v-btn
              color="error"
              small
              outline
              round
              @click="close()"
            >
              Cancel
            </v-btn>
            <v-btn
              color="success"
              round
              @click="reservation()"
            >
              Reserve
            </v-btn>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-layout>
</template>

<script>
import DatePicker from 'vue2-datepicker'
export default {
  name: 'FullCalendarReserve',

  props: {
    showModal: Boolean,
    startDate: Date,
    endDate: Date,
    minReservationTime: String,
    maxReservationTime: String,
    resourcesCheckboxes: Array,
    numberOfResources: Number,
    addReservation: Function

  },

  computed: {
    selectedTimeChanged () {
      return [this.startDate, this.endDate]
    }
  },

  watch: {
    selectedTimeChanged () {
      this.reservationTime = this.selectedTimeChanged
    }
  },

  components: {
    DatePicker
  },

  data () {
    return {
      reservationTime: '',
      timePickerOptions: {
        start: '00:00',
        step: '00:30',
        end: '23:30'
      },
      showInfo: false
    }
  },

  methods: {
    close: function () {
      this.showInfo = false
      this.$emit('close')
    },

    anyChecked: function () {
      var anyChecked = false
      for (var checkbox in this.resourcesCheckboxes) {
        if (this.resourcesCheckboxes[checkbox].checked) {
          anyChecked = true
          break
        }
      }
      return anyChecked
    },

    reservation: function () {
      var tempReservation
      if (this.anyChecked()) {
        for (var i = 0; i < this.numberOfResources; i++) {
          if (this.resourcesCheckboxes[i].checked) {
            tempReservation = {
              title: 'Reserved',
              description: 'Resource ' + (i + 1).toString(),
              start: this.reservationTime[0].toISOString(),
              end: this.reservationTime[1].toISOString(),
              resourceId: this.resourcesCheckboxes[i].uuid,
              userId: this.$store.state.id
            }
            this.addReservation(tempReservation)
          }
        }
        this.close()
      } else {
        this.showInfo = true
      }
    }
  }
}
</script>
