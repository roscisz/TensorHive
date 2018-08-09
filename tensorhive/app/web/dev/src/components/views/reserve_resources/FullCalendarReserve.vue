<template>
  <BaseModal
    :show="showModal"
    @close="close"
  >
    <div class="modal-header">
      <h3>Which resources do you want to reserve?</h3>
    </div>
    <div class="modal-body">
      <div
        class="row"
        v-for="checkbox in resourcesCheckboxes"
        :key="checkbox.name"
      >
        {{ checkbox.name }}
        <input
          type="checkbox"
          v-model="checkbox.checked"
          :disabled="checkbox.disabled"
        >
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
    </div>
    <div class="modal-footer text-right">
      <button
        class="modal-default-button"
        @click="reservation()"
      >
        Reserve
      </button>
    </div>
  </BaseModal>
</template>

<script>
import BaseModal from './BaseModal.vue'
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
    BaseModal,
    DatePicker
  },

  data () {
    return {
      title: '',
      reservationTime: '',
      body: '',
      timePickerOptions: {
        start: '00:00',
        step: '00:30',
        end: '23:30'
      }
    }
  },

  methods: {
    close: function () {
      this.$emit('close')
      this.title = ''
      this.body = ''
    },

    reservation: function () {
      var tempReservation
      for (var i = 0; i < this.numberOfResources; i++) {
        if (this.resourcesCheckboxes[i].checked) {
          tempReservation = {
            title: 'Reserved',
            description: 'Resource ' + (i + 1).toString(),
            start: this.reservationTime[0].toISOString(),
            end: this.reservationTime[1].toISOString(),
            resourceId: i + 1,
            userId: 1
          }
          this.addReservation(tempReservation)
        }
      }
      this.close()
    }
  }
}
</script>
