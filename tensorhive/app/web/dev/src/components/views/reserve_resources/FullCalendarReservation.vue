<template>
  <BaseModal
    :show="showModal"
    @close="close"
  >
    <div class="modal-header">
      <h3>Which nodes do you want to reserve?</h3>
    </div>
    <div class="modal-body">
      <div
        class="row"
        v-for="checkbox in nodesCheckboxes"
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
          format="YYYY-MM-DD HH:mm:ss"
          :not-before="minReservationTime"
          :not-after="maxReservationTime"
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
  name: 'FullCalendarReservation',

  props: {
    showModal: Boolean,
    minReservationTime: String,
    maxReservationTime: String,
    nodesCheckboxes: Array,
    numberOfNodes: Number,
    addEvent: Function

  },

  components: {
    BaseModal,
    DatePicker
  },

  data () {
    return {
      title: '',
      reservationTime: '',
      body: ''
    }
  },

  methods: {
    close: function () {
      this.$emit('close')
      this.title = ''
      this.body = ''
    },

    reservation: function () {
      var tempEvent
      for (var i = 0; i < this.numberOfNodes; i++) {
        if (this.nodesCheckboxes[i].checked) {
          tempEvent = {
            title: 'Reserved',
            description: 'node ' + (i + 1).toString(),
            start: this.reservationTime[0].toJSON().slice(0, -5),
            end: this.reservationTime[1].toJSON().slice(0, -5),
            nodeId: i + 1,
            userId: 1
          }
          this.addEvent(tempEvent)
        }
      }
      this.close()
    }
  }
}
</script>
